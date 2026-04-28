"""
embeddings.py — generate and cache text embeddings for all artifacts.

Model choice:
  We use SPECTER2 ("allenai/specter2_base" + proximity adapter), the 2022
  successor to the original SPECTER model. Like its predecessor, SPECTER2 was
  trained on scientific papers using citation-informed contrastive learning and
  produces 768-dimensional embeddings suited to measuring semantic relatedness
  across patents, papers, and research projects in scientific domains.

  SPECTER2 improves on SPECTER in two ways:
    1. It uses adapter layers — small task-specific modules — so one base model
       can be fine-tuned for different tasks (proximity search, classification,
       etc.) without retraining from scratch.
    2. The proximity adapter is explicitly trained for document-level similarity
       retrieval, which matches our use case: finding how close two documents
       are in semantic space.

  Loading requires the `adapters` library (pip install adapters) in addition
  to HuggingFace `transformers`.

  Reference: Specter2 — https://huggingface.co/allenai/specter2
  Original SPECTER: Cohan et al. (2020) "SPECTER: Document-level Representation
  Learning using Citation-informed Transformers." ACL 2020.
  https://arxiv.org/abs/2004.13313

  ⚠️  Cache compatibility: embeddings from SPECTER and SPECTER2 are NOT
  interchangeable — they live in different vector spaces. If you switch models,
  delete data/embeddings/ so the cache is rebuilt from scratch.

Caching:
  Embeddings are expensive to compute. We cache them as small binary files so
  that re-running the pipeline skips already-embedded texts and no progress is
  lost if the process is interrupted mid-run.

  How it works:
    Each batch of ~64 items is saved immediately after it is computed, as a
    pair of files in data/embeddings/embeddings_batches/:

      batch_000042.txt  — one artifact ID per line
      batch_000042.npy  — numpy float32 matrix, shape (batch_size, 768)

    On load, all batch files are read and merged into a single id→vector dict.
    This replaces the old approach of holding everything in RAM and writing one
    large JSON file at the end — which got progressively slower and lost all
    progress on a crash.

  Backward compatibility:
    If an old embeddings.json file exists, it is loaded first so that prior
    work is not wasted. New batches are written to the batch directory only.
    You can delete embeddings.json once the run completes to save disk space.

  NOTE: If you switch embedding models, delete the data/embeddings/ directory
  so the cache is rebuilt — vectors from different models are incompatible.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SPECTER2 wrapper
# ---------------------------------------------------------------------------

class Specter2Model:
    """
    Thin wrapper around the SPECTER2 base model + proximity adapter.

    SPECTER2 is not distributed as a SentenceTransformer, so we wrap the raw
    HuggingFace model to give it the same .encode() interface that the rest of
    this module expects.

    The proximity adapter is the right choice for semantic similarity tasks
    (as opposed to the classification or adhoc_query adapters).

    Reference: https://huggingface.co/allenai/specter2
    """

    BASE_MODEL = "allenai/specter2_base"
    ADAPTER    = "allenai/specter2"
    ADAPTER_NAME = "specter2_proximity"

    def __init__(self, device: str = "cpu"):
        import torch
        from transformers import AutoTokenizer
        from adapters import AutoAdapterModel

        self.device = device
        logger.info(f"Loading SPECTER2 base model: {self.BASE_MODEL} (device={device})")
        self.tokenizer = AutoTokenizer.from_pretrained(self.BASE_MODEL)
        self.model = AutoAdapterModel.from_pretrained(self.BASE_MODEL)

        # Load the proximity adapter — trained for symmetric document-to-document
        # similarity retrieval. This is the right adapter for our task (cosine
        # similarity between two document centroids).
        #
        # SPECTER2 ships with three adapters; the others are NOT appropriate here:
        #   - specter2_classification  → assigns documents to fixed categories
        #   - specter2_adhoc_query     → asymmetric query→document search
        #
        # set_active=True activates the adapter immediately (equivalent to calling
        # model.set_active_adapters("specter2_proximity") separately).
        logger.info(f"Loading adapter: {self.ADAPTER} (proximity / document similarity)")
        self.model.load_adapter(
            self.ADAPTER,
            source="hf",
            load_as=self.ADAPTER_NAME,
            set_active=True,
        )
        self.model.to(device)
        self.model.eval()

    def encode(self, texts: list[str], batch_size: int = 32, show_progress_bar: bool = False) -> np.ndarray:
        """
        Encode a list of texts into 768-dimensional vectors.

        Extraction strategy: we take the embedding of the [CLS] token from the
        last hidden state. This is the standard approach for SPECTER-family
        models and produces one vector per document regardless of length.

        Speed notes:
          - max_length=256: abstracts and project descriptions almost never
            exceed 256 tokens (~190 words). BERT-family attention is O(n²) in
            sequence length, so halving from 512→256 gives roughly 4x speedup
            on the attention layers. Content beyond 256 tokens is truncated,
            but the most informative content in abstracts is frontloaded.
          - torch.inference_mode: faster than no_grad — also disables view
            tracking in addition to gradient computation.
          - Length-sorted batching: within each batch, texts are sorted by
            length so that padding (which wastes computation) is minimised.
            A batch with mixed-length texts pads everything to the longest one;
            sorting by length keeps padding overhead small.
          - batch_size=32: on Apple Silicon (MPS), 32 typically runs faster
            than 64 due to memory transfer overhead between CPU and GPU.
        """
        import torch

        # Sort texts by length so each mini-batch has similar-length texts,
        # minimising wasted computation from padding shorter texts to the max.
        # We record the original order so we can restore it before returning.
        order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
        sorted_texts = [texts[i] for i in order]
        inverse = [0] * len(order)
        for new_i, orig_i in enumerate(order):
            inverse[orig_i] = new_i

        all_vectors = [None] * len(texts)
        iterator = range(0, len(sorted_texts), batch_size)
        if show_progress_bar:
            iterator = tqdm(iterator, desc="Encoding", unit="batch")

        with torch.inference_mode():
            for start in iterator:
                chunk = sorted_texts[start : start + batch_size]
                inputs = self.tokenizer(
                    chunk,
                    padding=True,       # pad to the longest in THIS batch only
                    truncation=True,
                    max_length=256,     # abstracts rarely exceed ~190 words
                    return_tensors="pt",
                ).to(self.device)

                outputs = self.model(**inputs)
                # CLS token is the first token; shape: (batch, hidden_size)
                cls_vecs = outputs.last_hidden_state[:, 0, :].cpu().numpy()

                for batch_i, sorted_i in enumerate(range(start, start + len(chunk))):
                    all_vectors[order[sorted_i]] = cls_vecs[batch_i]

                # Free GPU/MPS memory after each mini-batch
                if self.device == "mps":
                    torch.mps.empty_cache()
                elif self.device == "cuda":
                    torch.cuda.empty_cache()

        return np.array(all_vectors, dtype=np.float32)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_model(model_name: str = "specter2"):
    """
    Load an embedding model by name.

    Supported values for model_name:
      "specter2"       — SPECTER2 with proximity adapter (default, recommended)
      "allenai-specter" — original SPECTER via sentence-transformers (legacy)
      any HuggingFace SentenceTransformer model name — loaded via sentence-transformers

    Device selection (in priority order):
      1. CUDA  — NVIDIA GPU
      2. MPS   — Apple Silicon GPU (M1/M2/M3/M4); typically 5–10x faster than CPU
      3. CPU   — fallback

    Parameters
    ----------
    model_name : model identifier string (see above)
    """
    import torch

    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    if model_name == "specter2":
        return Specter2Model(device=device)

    # Fallback: treat as a sentence-transformers model name
    from sentence_transformers import SentenceTransformer
    logger.info(f"Loading SentenceTransformer model: {model_name} (device={device})")
    return SentenceTransformer(model_name, device=device)


def generate_embeddings(
    df: pd.DataFrame,
    model,
    text_col: str = "text",
    id_col: str = "id",
    cache_file: Optional[str | Path] = None,
    batch_size: int = 32,
    checkpoint_every: int = 256,
) -> dict[str, list[float]]:
    """
    Generate embeddings for all rows in df, saving checkpoints to disk regularly.

    Checkpoints are written every `checkpoint_every` documents (default 256).
    This means a crash or keyboard interrupt loses at most ~256 items of work,
    regardless of how large the dataset is.

    Parameters
    ----------
    df : DataFrame with at least `id_col` and `text_col` columns
    model : loaded model (Specter2Model or SentenceTransformer)
    text_col : column containing text to embed
    id_col : column containing unique artifact IDs
    cache_file : path for the embedding cache (batch files live alongside it)
    batch_size : number of texts per encoding call; 32 is a good default for
                 Apple Silicon (MPS). Increase to 64 if you have a fast GPU.
    checkpoint_every : save a batch file to disk after this many documents.
                       Lower = safer against crashes, higher = fewer file I/O ops.

    Returns
    -------
    dict mapping artifact id → embedding vector (list of floats)
    """
    import time

    cache = _load_cache(cache_file)

    ids   = df[id_col].tolist()
    texts = df[text_col].tolist()
    to_embed = [(i, t) for i, t in zip(ids, texts) if i not in cache]

    if not to_embed:
        logger.info("All embeddings found in cache. Nothing to compute.")
        return cache

    n_todo = len(to_embed)
    logger.info(f"Computing embeddings for {n_todo:,} items "
                f"(batch_size={batch_size}, checkpoint_every={checkpoint_every})")

    # Buffers that accumulate between checkpoints
    pending_ids  = []
    pending_vecs = []

    pbar = tqdm(total=n_todo, desc="Embedding", unit="doc", dynamic_ncols=True)
    t0   = time.time()

    for start in range(0, n_todo, batch_size):
        chunk = to_embed[start : start + batch_size]
        chunk_ids   = [i for i, _ in chunk]
        chunk_texts = [t for _, t in chunk]

        # encode() handles its own internal batching, length-sorting, and
        # memory management — we just pass the chunk and get vectors back.
        vectors = model.encode(chunk_texts, show_progress_bar=False)

        for artifact_id, vector in zip(chunk_ids, vectors):
            cache[artifact_id] = vector.tolist()

        pending_ids.extend(chunk_ids)
        pending_vecs.append(vectors)

        pbar.update(len(chunk))

        # Write a checkpoint once we have accumulated enough documents.
        # Flushing regularly means we never lose more than `checkpoint_every`
        # items of work, even if the process is killed mid-run.
        if len(pending_ids) >= checkpoint_every:
            _save_batch(pending_ids, np.vstack(pending_vecs), cache_file)
            elapsed = time.time() - t0
            rate    = len(pending_ids) / elapsed if elapsed > 0 else 0
            pbar.set_postfix({"docs/s": f"{rate:.1f}", "saved": len(cache)})
            pending_ids  = []
            pending_vecs = []
            t0 = time.time()

    # Flush any remaining documents that didn't fill a full checkpoint window
    if pending_ids:
        _save_batch(pending_ids, np.vstack(pending_vecs), cache_file)

    pbar.close()
    logger.info(f"Embeddings complete. Cache now has {len(cache):,} entries.")
    return cache


def embeddings_to_matrix(
    df: pd.DataFrame,
    cache: dict[str, list[float]],
    id_col: str = "id",
) -> tuple[np.ndarray, list[str]]:
    """
    Convert the cache dict to a NumPy matrix aligned with df.

    Returns
    -------
    matrix : shape (n_artifacts, embedding_dim)
    valid_ids : list of IDs that had embeddings (rows without embeddings are skipped)
    """
    valid_rows = []
    valid_ids  = []

    for _, row in df.iterrows():
        artifact_id = row[id_col]
        if artifact_id in cache:
            valid_rows.append(cache[artifact_id])
            valid_ids.append(artifact_id)
        else:
            logger.warning(f"No embedding found for id={artifact_id}, skipping.")

    matrix = np.array(valid_rows, dtype=np.float32)
    return matrix, valid_ids


# ---------------------------------------------------------------------------
# Cache I/O
# ---------------------------------------------------------------------------

def _batch_dir(cache_file: Path) -> Path:
    """Return the batch directory path corresponding to a cache file path."""
    return cache_file.parent / (cache_file.stem + "_batches")


def _load_cache(cache_file: Optional[str | Path]) -> dict:
    """
    Load the embedding cache.

    Reads from two sources and merges them:
    1. Old-style embeddings.json (if present) — for backward compatibility
       with any work done before this caching format was introduced.
    2. Batch files in embeddings_batches/ — the fast, incremental format.
       These override the JSON if the same ID appears in both.
    """
    if cache_file is None:
        return {}

    cache_file = Path(cache_file)
    cache = {}

    if cache_file.exists():
        logger.info(f"Loading legacy JSON cache from {cache_file.name}...")
        with open(cache_file, "r") as f:
            cache.update(json.load(f))
        logger.info(f"  Loaded {len(cache)} entries from JSON.")

    batch_dir = _batch_dir(cache_file)
    if batch_dir.exists():
        batch_files = sorted(batch_dir.glob("*.txt"))
        if batch_files:
            logger.info(f"Loading {len(batch_files)} batch files from {batch_dir.name}/...")
            before = len(cache)
            for ids_file in batch_files:
                vecs_file = ids_file.with_suffix(".npy")
                if not vecs_file.exists():
                    logger.warning(f"  Missing .npy for {ids_file.name}, skipping.")
                    continue
                ids  = ids_file.read_text().splitlines()
                vecs = np.load(vecs_file)
                for artifact_id, vec in zip(ids, vecs):
                    cache[artifact_id] = vec.tolist()
            logger.info(f"  Added {len(cache) - before} entries from batch files.")

    return cache


def _save_batch(
    chunk_ids: list[str],
    chunk_vecs: np.ndarray,
    cache_file: Optional[str | Path],
) -> None:
    """
    Save one batch of embeddings as a pair of files:
      - <batch_dir>/batch_NNNNNN.txt  — one artifact ID per line
      - <batch_dir>/batch_NNNNNN.npy  — float32 matrix, shape (n, 768)
    """
    if cache_file is None:
        return

    batch_dir = _batch_dir(Path(cache_file))
    batch_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(batch_dir.glob("*.npy"))
    batch_n  = len(existing)
    stem     = f"batch_{batch_n:06d}"

    (batch_dir / f"{stem}.txt").write_text("\n".join(chunk_ids))
    np.save(batch_dir / f"{stem}.npy", np.array(chunk_vecs, dtype=np.float32))
