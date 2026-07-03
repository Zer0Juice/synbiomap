"""
Step 4d — Cross-genre retrieval evaluation (recall@k).

Purpose
-------
This is the validation that justifies the shared-embedding method in the
manuscript. The whole point of fine-tuning SPECTER2 is to place papers,
patents, projects and parts in ONE comparable semantic space. This script
measures whether that actually works, by testing cross-genre retrieval:

  "Given a patent, does its linked paper rank near the top of all candidate
   papers?"  — and the same for project↔paper links.

We report the standard information-retrieval metrics:
  recall@k — fraction of queries whose correct match is in the top k results.
  MRR      — mean reciprocal rank (1/rank of the correct match, averaged);
             rewards putting the right answer higher, not just in the top k.
  Reference: Manning, Raghavan & Schütze (2008), *Introduction to Information
             Retrieval*, ch. 8 (evaluation of ranked retrieval).

We run the SAME test on two encoders and compare:
  baseline  — off-the-shelf SPECTER2 (base + proximity adapter), as used in
              src/embed/embeddings.py.
  finetuned — SPECTER2 base + our fine-tuned adapter (models/specter2_synbio).
If fine-tuning helped cross-genre comparability, the finetuned column should
show higher recall@k and MRR, especially on the patent and project edges.

Test data
---------
The held-out validation pairs (data/finetune/pairs_val.jsonl), restricted to
the cross-genre edge types — these documents were never seen in training.

For each directed edge type (e.g. patent_paper = query is a patent, target is
its paper) we build a retrieval task:
  queries    = the distinct anchor documents
  candidates = the distinct positive documents (the pool to rank)
  relevant   = for each anchor, the positive(s) it is actually linked to
A query "hits at k" if any of its relevant targets is in the top k candidates.

Usage
-----
  python scripts/eval_recall_at_k.py
  python scripts/eval_recall_at_k.py --adapter models/specter2_synbio/final
  python scripts/eval_recall_at_k.py --edges patent_paper project_paper
  python scripts/eval_recall_at_k.py --baseline-only    # before training exists
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

FINETUNE_DIR = REPO_ROOT / "data" / "finetune"
DEFAULT_ADAPTER = REPO_ROOT / "models" / "specter2_synbio" / "best"

# The cross-genre edges we care about — the ones that test whether different
# artifact types share a comparable space. (paper_paper and project_part are
# within-genre or already-easy, so they are not the interesting validation.)
DEFAULT_EDGES = [
    "patent_paper",       # given a patent, find its paper
    "paper_patent",       # given a paper, find its patent
    "project_paper",      # given a project, find a paper it cited (wiki)
    "paper_project",      # given a paper, find a project that cited it (wiki)
    "project_paper_part", # given a project, find a paper via a shared part
]


# ─────────────────────────────────────────────────────────────────────────────
# Encoders
# ─────────────────────────────────────────────────────────────────────────────

def _pick_device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_finetuned_encoder(adapter_path: Path, device: str):
    """
    Load SPECTER2 base + our fine-tuned adapter.

    Reuses Specter2Model.encode() (CLS pooling, title[SEP]abstract, max_len 256)
    so the baseline and fine-tuned models are embedded identically — only the
    adapter differs. This is important: any metric gap must come from the
    adapter, not from a difference in how we encode.
    """
    from src.embed.embeddings import Specter2Model
    from transformers import AutoTokenizer
    from adapters import AutoAdapterModel

    enc = Specter2Model.__new__(Specter2Model)  # skip __init__ (it loads proximity)
    enc.device = device
    enc.tokenizer = AutoTokenizer.from_pretrained(Specter2Model.BASE_MODEL)
    enc.model = AutoAdapterModel.from_pretrained(Specter2Model.BASE_MODEL)
    name = enc.model.load_adapter(str(adapter_path), set_active=True)
    enc.model.set_active_adapters(name)
    enc.model.to(device)
    enc.model.eval()
    return enc


# ─────────────────────────────────────────────────────────────────────────────
# Load evaluation pairs
# ─────────────────────────────────────────────────────────────────────────────

def load_edge_tasks(val_path: Path, edges: list) -> dict:
    """
    Read pairs_val.jsonl and group into per-edge retrieval tasks.

    Returns {edge_type: {
        "queries":    [(anchor_id, anchor_text), ...]        (deduped),
        "candidates": [(positive_id, positive_text), ...]    (deduped),
        "relevant":   {anchor_id: set(positive_id, ...)},
    }}
    """
    by_edge = defaultdict(list)
    with open(val_path) as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("edge_type") in edges:
                by_edge[rec["edge_type"]].append(rec)

    tasks = {}
    for edge, recs in by_edge.items():
        q_text, c_text = {}, {}
        relevant = defaultdict(set)
        for r in recs:
            q_text[r["anchor_id"]]   = r["anchor_text"]
            c_text[r["positive_id"]] = r["positive_text"]
            relevant[r["anchor_id"]].add(r["positive_id"])
        tasks[edge] = {
            "queries":    list(q_text.items()),
            "candidates": list(c_text.items()),
            "relevant":   dict(relevant),
        }
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_edge(encoder, task: dict, ks: list, batch_size: int = 32) -> dict:
    """
    Compute recall@k and MRR for one edge's retrieval task with one encoder.

    Steps:
      1. Encode all queries and all candidates.
      2. L2-normalise, so dot product = cosine similarity.
      3. For each query, rank candidates by similarity and find the best
         (smallest) rank among its relevant targets.
      4. recall@k = fraction of queries whose best rank is < k; MRR = mean 1/rank.
    """
    q_ids   = [qid for qid, _ in task["queries"]]
    q_texts = [t   for _, t   in task["queries"]]
    c_ids   = [cid for cid, _ in task["candidates"]]
    c_texts = [t   for _, t   in task["candidates"]]

    q_vecs = encoder.encode(q_texts, batch_size=batch_size)
    c_vecs = encoder.encode(c_texts, batch_size=batch_size)

    q_vecs = q_vecs / (np.linalg.norm(q_vecs, axis=1, keepdims=True) + 1e-12)
    c_vecs = c_vecs / (np.linalg.norm(c_vecs, axis=1, keepdims=True) + 1e-12)

    sims = q_vecs @ c_vecs.T                     # (n_queries, n_candidates)
    # argsort descending → ranked candidate indices per query
    ranked = np.argsort(-sims, axis=1)
    c_index = {cid: i for i, cid in enumerate(c_ids)}

    hits = {k: 0 for k in ks}
    rr_sum = 0.0
    n = 0
    for i, qid in enumerate(q_ids):
        rel_cols = {c_index[r] for r in task["relevant"][qid] if r in c_index}
        if not rel_cols:
            continue
        n += 1
        # position (0-based) of each candidate in this query's ranking
        order = ranked[i]
        best_rank = min(np.where(order == col)[0][0] for col in rel_cols)
        rr_sum += 1.0 / (best_rank + 1)
        for k in ks:
            if best_rank < k:
                hits[k] += 1

    return {
        "n_queries":  n,
        "pool_size":  len(c_ids),
        "recall":     {k: hits[k] / n if n else 0.0 for k in ks},
        "mrr":        rr_sum / n if n else 0.0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────

def print_report(results: dict, ks: list, model_names: list):
    """Print a per-edge comparison table across the evaluated models."""
    kcols = "  ".join(f"R@{k:<4}" for k in ks)
    header = f"{'edge':<20} {'model':<10} {'n':>5} {'pool':>6}  {kcols}  {'MRR':>6}"
    print("\n" + header)
    print("-" * len(header))
    for edge in results:
        for mname in model_names:
            r = results[edge].get(mname)
            if r is None:
                continue
            rec = "  ".join(f"{r['recall'][k]:.3f}" for k in ks)
            print(f"{edge:<20} {mname:<10} {r['n_queries']:>5} {r['pool_size']:>6}  "
                  f"{rec}  {r['mrr']:.3f}")
        print()


def run(args):
    device = _pick_device()
    print(f"Device: {device}")

    ks = sorted(int(k) for k in args.k)
    val_path = FINETUNE_DIR / "pairs_val.jsonl"
    tasks = load_edge_tasks(val_path, args.edges)

    print(f"Loaded {len(tasks)} edge tasks from {val_path.name}:")
    for edge, t in tasks.items():
        print(f"  {edge:<20} {len(t['queries']):>5} queries, "
              f"{len(t['candidates']):>5} candidates")

    # Which models to run
    model_names = []
    encoders = {}

    if not args.finetuned_only:
        from src.embed.embeddings import Specter2Model
        print("\nLoading baseline: SPECTER2 base + proximity adapter...")
        encoders["baseline"] = Specter2Model(device=device)
        model_names.append("baseline")

    if not args.baseline_only:
        adapter_path = Path(args.adapter)
        if not adapter_path.exists():
            print(f"\n⚠️  Fine-tuned adapter not found at {adapter_path} — "
                  f"skipping (run scripts/finetune_specter2.py first).")
        else:
            print(f"\nLoading fine-tuned: SPECTER2 base + {adapter_path}...")
            encoders["finetuned"] = load_finetuned_encoder(adapter_path, device)
            model_names.append("finetuned")

    # Evaluate
    results = {edge: {} for edge in tasks}
    for mname in model_names:
        print(f"\nEvaluating [{mname}]...")
        for edge, task in tasks.items():
            results[edge][mname] = evaluate_edge(encoders[mname], task, ks)
            r = results[edge][mname]
            print(f"  {edge:<20} R@{ks[0]}={r['recall'][ks[0]]:.3f}  MRR={r['mrr']:.3f}")

    print_report(results, ks, model_names)

    # Save machine-readable results next to the adapter (or in models/)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"ks": ks, "models": model_names, "results": results}, indent=2))
    print(f"Saved: {out}")


def parse_args():
    p = argparse.ArgumentParser(description="Cross-genre recall@k evaluation for SPECTER2 fine-tuning.")
    p.add_argument("--adapter", default=str(DEFAULT_ADAPTER),
                   help=f"Fine-tuned adapter directory (default: {DEFAULT_ADAPTER})")
    p.add_argument("--edges", nargs="+", default=DEFAULT_EDGES,
                   help="Edge types to evaluate (default: the cross-genre edges)")
    p.add_argument("--k", nargs="+", default=[1, 5, 10],
                   help="Recall cutoffs (default: 1 5 10)")
    p.add_argument("--baseline-only", action="store_true",
                   help="Only run the off-the-shelf SPECTER2 baseline")
    p.add_argument("--finetuned-only", action="store_true",
                   help="Only run the fine-tuned adapter")
    p.add_argument("--out", default=str(REPO_ROOT / "models" / "specter2_synbio" / "recall_at_k.json"),
                   help="Where to save the results JSON")
    return p.parse_args()


if __name__ == "__main__":
    run(parse_args())
