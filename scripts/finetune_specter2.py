"""
Step 4c — Fine-tune SPECTER2 on the synthetic biology citation graph.

This script adds a LoRA adapter to SPECTER2 and trains it on the (anchor, positive)
pairs built by build_finetune_data.py. Only the adapter weights are updated —
the base model is frozen — so the original SPECTER2 knowledge is preserved.

What is a LoRA adapter?
-----------------------
LoRA (Low-Rank Adaptation) is a technique for fine-tuning large models cheaply.
Instead of updating all 110 million weights, it inserts small trainable matrices
into each attention layer (~1–5 million parameters total). This is much faster,
uses less memory, and is less prone to forgetting what the base model already
knows.

What is InfoNCE loss?
---------------------
The training signal is InfoNCE (the same objective SPECTER2 was pre-trained on).
Given a batch of (anchor, positive) pairs, the model is asked: "which item in
this batch is the true positive for this anchor?" All other items in the batch
serve as negatives. The loss is cross-entropy over a cosine similarity matrix.
Larger batches = harder negatives = stronger training signal.

Reference: van den Oord et al. (2018) "Representation Learning with Contrastive
Predictive Coding." https://arxiv.org/abs/1807.03748

Usage
-----
  python scripts/finetune_specter2.py [options]

Options
-------
  --batch-size    Number of pairs per training step (default: 32)
                  Larger = stronger negatives but more memory.
  --epochs        Number of passes over the training data (default: 2)
  --lr            Learning rate for the adapter weights (default: 2e-4)
                  Higher than typical full fine-tuning because only adapter
                  weights are updated.
  --max-seq-len   Token limit per document (default: 256)
  --val-steps     Evaluate on the validation set every N steps (default: 500)
  --output-dir    Where to save the fine-tuned adapter (default: models/specter2_synbio)

Output
------
  models/specter2_synbio/
    adapter_config.json     — LoRA configuration
    pytorch_adapter.bin     — trained adapter weights
    training_log.jsonl      — loss at each logged step
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

FINETUNE_DIR = REPO_ROOT / "data" / "finetune"
DEFAULT_OUT  = REPO_ROOT / "models" / "specter2_synbio"

SPECTER2_BASE    = "allenai/specter2_base"
ADAPTER_NAME     = "synbio_proximity"


# ─────────────────────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────────────────────

class PairsDataset(Dataset):
    """Loads (anchor_text, positive_text) pairs from a JSONL file."""

    def __init__(self, jsonl_path: Path):
        self.pairs = []
        with open(jsonl_path) as f:
            for line in f:
                rec = json.loads(line)
                anchor_text   = rec["anchor_text"].strip()
                positive_text = rec["positive_text"].strip()
                if anchor_text and positive_text:
                    self.pairs.append((anchor_text, positive_text))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        return self.pairs[idx]


def collate_fn(batch):
    """Return two parallel lists: anchors and positives."""
    anchors   = [a for a, _ in batch]
    positives = [p for _, p in batch]
    return anchors, positives


# ─────────────────────────────────────────────────────────────────────────────
# Model loading
# ─────────────────────────────────────────────────────────────────────────────

def load_model_with_adapter(output_dir: Path):
    """
    Load SPECTER2 base and attach a new LoRA adapter for domain fine-tuning.

    We freeze all base model weights and only train the LoRA adapter. This
    preserves SPECTER2's broad scientific knowledge while adding synbio-specific
    signal. The resulting adapter can be loaded on top of specter2_base at
    inference time alongside the original proximity adapter.
    """
    from transformers import AutoTokenizer
    from adapters import AutoAdapterModel, LoRAConfig

    print(f"Loading base model: {SPECTER2_BASE}")
    tokenizer = AutoTokenizer.from_pretrained(SPECTER2_BASE)
    model = AutoAdapterModel.from_pretrained(SPECTER2_BASE)

    # Add a LoRA adapter with rank 16.
    # rank=16 gives a good balance between capacity and parameter count.
    # For reference, rank=8 gives ~0.5 M params, rank=16 ~1 M params.
    # The adapter is inserted into all attention projection layers (q, v by default).
    lora_config = LoRAConfig(r=16, alpha=32)
    model.add_adapter(ADAPTER_NAME, config=lora_config)

    # Activate the adapter and set it to training mode.
    # freeze_model(True) freezes all base model weights; only adapter weights
    # remain trainable. This is the standard pattern for adapter fine-tuning.
    model.train_adapter(ADAPTER_NAME)
    model.set_active_adapters(ADAPTER_NAME)

    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total     = sum(p.numel() for p in model.parameters())
    print(f"Trainable params: {n_trainable:,} / {n_total:,} "
          f"({100 * n_trainable / n_total:.1f}%)")

    return model, tokenizer


# ─────────────────────────────────────────────────────────────────────────────
# Encoding helper
# ─────────────────────────────────────────────────────────────────────────────

def encode_batch(model, tokenizer, texts: list[str], max_seq_len: int, device: str) -> torch.Tensor:
    """
    Tokenise and encode a list of texts, returning CLS-token vectors.

    CLS pooling is used to match how SPECTER2 is used at inference time
    (see src/embed/embeddings.py). Consistent pooling between training and
    inference is important so the model learns to pack information into the
    CLS token.
    """
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=max_seq_len,
        return_tensors="pt",
    ).to(device)

    outputs = model(**inputs)
    # CLS token is at position 0 of last_hidden_state
    return outputs.last_hidden_state[:, 0, :]


# ─────────────────────────────────────────────────────────────────────────────
# InfoNCE loss
# ─────────────────────────────────────────────────────────────────────────────

def info_nce_loss(anchor_vecs: torch.Tensor, positive_vecs: torch.Tensor, temperature: float = 0.05) -> torch.Tensor:
    """
    Compute InfoNCE (in-batch contrastive) loss.

    For each anchor, the model must identify its paired positive among all
    positives in the batch. All non-paired positives serve as negatives.

    Steps:
      1. L2-normalise both sets of vectors.
      2. Compute a (batch_size × batch_size) cosine similarity matrix.
      3. Divide by temperature (lower = sharper distribution = harder task).
      4. Cross-entropy loss where the correct answer for row i is column i.

    Temperature 0.05 is standard for this type of contrastive objective.
    Lowering it makes training harder but can improve retrieval quality.
    Raising it makes training easier but embeddings become less discriminative.
    """
    a = F.normalize(anchor_vecs,   dim=1)
    p = F.normalize(positive_vecs, dim=1)
    logits = torch.mm(a, p.t()) / temperature
    labels = torch.arange(len(a), device=a.device)
    return F.cross_entropy(logits, labels)


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

@torch.no_grad()
def evaluate(model, tokenizer, val_loader: DataLoader, max_seq_len: int, device: str) -> float:
    """Compute mean InfoNCE loss on the validation set."""
    model.eval()
    total_loss = 0.0
    n_batches  = 0
    for anchors, positives in val_loader:
        a_vecs = encode_batch(model, tokenizer, anchors,   max_seq_len, device)
        p_vecs = encode_batch(model, tokenizer, positives, max_seq_len, device)
        total_loss += info_nce_loss(a_vecs, p_vecs).item()
        n_batches  += 1
    model.train()
    return total_loss / max(n_batches, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Training loop
# ─────────────────────────────────────────────────────────────────────────────

def train(args):
    device = (
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )
    print(f"Device: {device}")

    # Load data
    print("\nLoading training pairs...")
    train_dataset = PairsDataset(FINETUNE_DIR / "pairs_train.jsonl")
    val_dataset   = PairsDataset(FINETUNE_DIR / "pairs_val.jsonl")

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=0,  # 0 is safest on macOS/MPS
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collate_fn,
        num_workers=0,
    )

    print(f"Train pairs: {len(train_dataset):,}")
    print(f"Val pairs:   {len(val_dataset):,}")

    # Load model
    print()
    output_dir = Path(args.output_dir)
    model, tokenizer = load_model_with_adapter(output_dir)
    model = model.to(device)

    # Only pass parameters that require gradients to the optimiser.
    # This is critical — passing frozen parameters wastes memory and can
    # cause errors with some optimisers.
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr,
        weight_decay=0.01,
    )

    # Linear warmup over the first 10% of steps, then constant LR.
    # Warmup prevents the adapter weights from jumping to a bad local minimum
    # at the start when they are randomly initialised.
    total_steps  = math.ceil(len(train_dataset) / args.batch_size) * args.epochs
    warmup_steps = total_steps // 10

    def lr_lambda(step):
        if step < warmup_steps:
            return step / max(warmup_steps, 1)
        return 1.0

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    # Logging
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "training_log.jsonl"
    log_file = open(log_path, "w")

    def log(record: dict):
        log_file.write(json.dumps(record) + "\n")
        log_file.flush()

    print(f"\nStarting training: {args.epochs} epoch(s), "
          f"{total_steps} total steps, "
          f"{warmup_steps} warmup steps\n")

    global_step   = 0
    best_val_loss = float("inf")

    for epoch in range(1, args.epochs + 1):
        epoch_loss = 0.0
        n_batches  = 0
        t0 = time.time()

        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}", unit="batch")

        for anchors, positives in pbar:
            model.train()
            optimizer.zero_grad()

            a_vecs = encode_batch(model, tokenizer, anchors,   args.max_seq_len, device)
            p_vecs = encode_batch(model, tokenizer, positives, args.max_seq_len, device)
            loss   = info_nce_loss(a_vecs, p_vecs)

            loss.backward()
            # Gradient clipping prevents large gradient spikes from destabilising
            # the adapter weights early in training.
            torch.nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], max_norm=1.0
            )
            optimizer.step()
            scheduler.step()

            epoch_loss += loss.item()
            n_batches  += 1
            global_step += 1

            pbar.set_postfix({"loss": f"{loss.item():.4f}", "step": global_step})

            # Periodic validation
            if global_step % args.val_steps == 0:
                val_loss = evaluate(model, tokenizer, val_loader, args.max_seq_len, device)
                record = {
                    "step":     global_step,
                    "epoch":    epoch,
                    "val_loss": round(val_loss, 4),
                    "lr":       scheduler.get_last_lr()[0],
                }
                log(record)
                tqdm.write(f"  step {global_step:>6}  val_loss={val_loss:.4f}  lr={record['lr']:.2e}")

                # Save best adapter checkpoint
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    model.save_adapter(str(output_dir / "best"), ADAPTER_NAME)
                    tqdm.write(f"  ✓ New best val_loss={best_val_loss:.4f} — checkpoint saved")

        avg_epoch_loss = epoch_loss / max(n_batches, 1)
        elapsed = time.time() - t0
        print(f"\nEpoch {epoch} done — avg_train_loss={avg_epoch_loss:.4f}  time={elapsed:.0f}s")
        log({
            "epoch":           epoch,
            "avg_train_loss":  round(avg_epoch_loss, 4),
            "elapsed_seconds": round(elapsed, 1),
        })

    # Save final adapter
    model.save_adapter(str(output_dir / "final"), ADAPTER_NAME)
    log_file.close()

    print(f"\nDone.")
    print(f"  Best checkpoint:  {output_dir / 'best'}")
    print(f"  Final checkpoint: {output_dir / 'final'}")
    print(f"  Training log:     {log_path}")
    print(f"\nTo use the fine-tuned adapter at inference time:")
    print(f"  model.load_adapter('{output_dir / 'best'}')")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Fine-tune SPECTER2 on the synbio citation graph")
    p.add_argument("--batch-size",  type=int,   default=32,
                   help="Pairs per training step (default: 32). Larger = harder negatives.")
    p.add_argument("--epochs",      type=int,   default=2,
                   help="Number of passes over training data (default: 2)")
    p.add_argument("--lr",          type=float, default=2e-4,
                   help="Learning rate for adapter weights (default: 2e-4)")
    p.add_argument("--max-seq-len", type=int,   default=256,
                   help="Token limit per document (default: 256)")
    p.add_argument("--val-steps",   type=int,   default=500,
                   help="Validate every N steps (default: 500)")
    p.add_argument("--output-dir",  type=str,   default=str(DEFAULT_OUT),
                   help=f"Where to save the adapter (default: {DEFAULT_OUT})")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(args)
