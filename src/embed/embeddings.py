"""
embeddings.py — generate and cache text embeddings for all artifacts.

Model choice:
  We use SPECTER ("allenai-specter"), a transformer model trained specifically
  on scientific papers using citation-informed contrastive learning. It
  produces 768-dimensional embeddings well-suited to measuring semantic
  relatedness across patents, papers, and research projects in scientific
  domains like synthetic biology.

  SPECTER loads via the sentence-transformers library, which means no extra
  dependencies and no compatibility issues.

  Reference: Cohan et al. (2020) "SPECTER: Document-level Representation
  Learning using Citation-informed Transformers." ACL 2020.
  https://arxiv.org/abs/2004.13313

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


def load_model(model_name: str = "allenai-specter"):
    """
    Load an embedding model by name via sentence-transformers.

    The model is downloaded on first use and cached by HuggingFace in
    ~/.cache/huggingface/.

    Parameters
    ----------
    model_name : HuggingFace model name or local path
    """
    from sentence_transformers import SentenceTransformer
    logger.info(f"Loading embedding model: {model_name}")
    return SentenceTransformer(model_name)


def generate_embeddings(
    df: pd.DataFrame,
    model,
    text_col: str = "text",
    id_col: str = "id",
    cache_file: Optional[str | Path] = None,
    batch_size: int = 64,
) -> dict[str, list[float]]:
    """
    Generate embeddings for all rows in df, saving progress after every batch.

    Each batch is written to disk immediately so that a crash or kernel restart
    only loses the work from the current batch (~64 items), not the entire run.

    Parameters
    ----------
    df : DataFrame with at least `id_col` and `text_col` columns
    model : loaded SentenceTransformer model
    text_col : column containing text to embed
    id_col : column containing unique artifact IDs
    cache_file : path used as the base for the cache directory
                 (e.g. data/embeddings/embeddings.json →
                       data/embeddings/embeddings_batches/)
    batch_size : number of texts to encode at once

    Returns
    -------
    dict mapping artifact id → embedding vector (list of floats)
    """
    cache = _load_cache(cache_file)

    # Find rows not yet in the cache
    ids = df[id_col].tolist()
    texts = df[text_col].tolist()
    to_embed = [(i, t) for i, t in zip(ids, texts) if i not in cache]

    if not to_embed:
        logger.info("All embeddings found in cache. Nothing to compute.")
        return cache

    logger.info(f"Computing embeddings for {len(to_embed)} items (batch_size={batch_size})")

    batch_ids = [i for i, _ in to_embed]
    batch_texts = [t for _, t in to_embed]

    for start in tqdm(range(0, len(batch_texts), batch_size), desc="Embedding"):
        chunk_ids = batch_ids[start : start + batch_size]
        chunk_texts = batch_texts[start : start + batch_size]

        # Encode this chunk of texts into vectors
        vectors = model.encode(chunk_texts, show_progress_bar=False)  # shape: (n, 768)

        # Update the in-memory cache
        for artifact_id, vector in zip(chunk_ids, vectors):
            cache[artifact_id] = vector.tolist()

        # Save this batch to disk immediately — only a tiny binary file is
        # written, not the entire cache. Progress is safe after every batch.
        _save_batch(chunk_ids, vectors, cache_file)

    logger.info(f"Embeddings complete. Cache now has {len(cache)} entries.")
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
    valid_ids = []

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

    This means you never lose prior work when upgrading the cache format.
    """
    if cache_file is None:
        return {}

    cache_file = Path(cache_file)
    cache = {}

    # --- 1. Load legacy JSON if present ---
    if cache_file.exists():
        logger.info(f"Loading legacy JSON cache from {cache_file.name}...")
        with open(cache_file, "r") as f:
            cache.update(json.load(f))
        logger.info(f"  Loaded {len(cache)} entries from JSON.")

    # --- 2. Load binary batch files (override JSON entries if same ID) ---
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
                ids = ids_file.read_text().splitlines()
                vecs = np.load(vecs_file)  # shape: (n, 768)
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

    Writing binary .npy files (~200 KB per batch) is much faster than
    rewriting a growing JSON file. Total disk I/O per run stays roughly
    constant regardless of how large the cache gets.
    """
    if cache_file is None:
        return

    batch_dir = _batch_dir(Path(cache_file))
    batch_dir.mkdir(parents=True, exist_ok=True)

    # Number the batch file after the existing ones
    existing = sorted(batch_dir.glob("*.npy"))
    batch_n = len(existing)
    stem = f"batch_{batch_n:06d}"

    # Save IDs as plain text (one per line) and vectors as binary numpy array
    (batch_dir / f"{stem}.txt").write_text("\n".join(chunk_ids))
    np.save(batch_dir / f"{stem}.npy", np.array(chunk_vecs, dtype=np.float32))
