"""
embeddings.py — generate and cache text embeddings for all artifacts.

We use sentence-transformers, a library that wraps pre-trained transformer
models and makes it easy to encode sentences into fixed-size vectors.

Model choice:
  "all-MiniLM-L6-v2" is the default. It is small (80MB), fast, and performs
  well on scientific text. For higher quality, "allenai-specter" was trained
  specifically on scientific papers and may give better results.

  Reference: Reimers & Gurevych (2019) "Sentence-BERT: Sentence Embeddings
  using Siamese BERT-Networks." EMNLP 2019. https://arxiv.org/abs/1908.10084

Caching:
  Embeddings are expensive to compute. We cache them in a JSON file so
  that re-running the pipeline skips already-embedded texts.
  Cache key = artifact id → embedding vector (list of floats).
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


def load_model(model_name: str = "all-MiniLM-L6-v2"):
    """
    Load a sentence-transformer model.

    The model is downloaded on first use and cached by the
    sentence-transformers library in ~/.cache/huggingface/.

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
    Generate embeddings for all rows in df, using a cache to skip
    already-processed items.

    Parameters
    ----------
    df : DataFrame with at least `id_col` and `text_col` columns
    model : loaded SentenceTransformer model
    text_col : column containing text to embed
    id_col : column containing unique artifact IDs
    cache_file : path to JSON cache file (created if it doesn't exist)
    batch_size : number of texts to encode at once

    Returns
    -------
    dict mapping artifact id → embedding vector (list of floats)
    """
    cache = _load_cache(cache_file)

    # Find rows that are not yet cached
    ids = df[id_col].tolist()
    texts = df[text_col].tolist()
    to_embed = [(i, t) for i, t in zip(ids, texts) if i not in cache]

    if not to_embed:
        logger.info("All embeddings found in cache. Nothing to compute.")
        return cache

    logger.info(f"Computing embeddings for {len(to_embed)} items (batch_size={batch_size})")

    # Process in batches
    batch_ids, batch_texts = zip(*to_embed)
    batch_ids = list(batch_ids)
    batch_texts = list(batch_texts)

    all_vectors = []
    for start in tqdm(range(0, len(batch_texts), batch_size), desc="Embedding"):
        chunk = batch_texts[start : start + batch_size]
        vectors = model.encode(chunk, show_progress_bar=False)
        all_vectors.extend(vectors.tolist())

    for artifact_id, vector in zip(batch_ids, all_vectors):
        cache[artifact_id] = vector

    _save_cache(cache, cache_file)
    logger.info(f"Embeddings saved. Cache now has {len(cache)} entries.")

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

def _load_cache(cache_file: Optional[str | Path]) -> dict:
    if cache_file is None:
        return {}
    cache_file = Path(cache_file)
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict, cache_file: Optional[str | Path]):
    if cache_file is None:
        return
    cache_file = Path(cache_file)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(cache, f)
