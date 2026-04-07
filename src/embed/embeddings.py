"""
embeddings.py — generate and cache text embeddings for all artifacts.

Model choice:
  We use SPECTER2 ("allenai/specter2_base"), a transformer model trained
  specifically on scientific papers using citation-informed contrastive
  learning. It produces 768-dimensional embeddings well-suited to measuring
  semantic relatedness across patents, papers, and research projects in
  scientific domains like synthetic biology.

  Reference: Singh et al. (2022) "SciRepEval: A Multi-Format Benchmark for
  Scientific Document Representations." arXiv:2211.13308.
  Original SPECTER: Cohan et al. (2020) "SPECTER: Document-level
  Representation Learning using Citation-informed Transformers."
  ACL 2020. https://arxiv.org/abs/2004.13313

  SPECTER2 uses the `adapters` library (not sentence-transformers) to load
  task-specific adapter weights on top of the base model. We wrap it in a
  small class so the rest of the pipeline can call .encode() as usual.

Caching:
  Embeddings are expensive to compute. We cache them in a JSON file so
  that re-running the pipeline skips already-embedded texts.
  Cache key = artifact id → embedding vector (list of floats).

  NOTE: If you switch models, delete data/embeddings/embeddings.json so the
  cache is rebuilt with the new model's vectors.
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
    Wraps the SPECTER2 base model (allenai/specter2_base) so it has the same
    .encode(texts) interface as a SentenceTransformer.

    We load the model with plain HuggingFace Transformers (AutoModel +
    AutoTokenizer), which avoids the `adapters` library and its dependency
    conflicts. The base model is already fine-tuned on scientific citation
    data and produces high-quality embeddings for scientific text.

    Requires: pip install transformers torch
    """

    def __init__(self, base: str = "allenai/specter2_base"):
        import torch
        from transformers import AutoTokenizer, AutoModel

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading SPECTER2 from {base} (device={self.device})")
        self.tokenizer = AutoTokenizer.from_pretrained(base)
        self.model = AutoModel.from_pretrained(base)
        self.model.to(self.device)
        self.model.eval()

    def encode(self, texts: list[str], batch_size: int = 16,
               show_progress_bar: bool = False) -> np.ndarray:
        """
        Encode a list of strings into a (n, 768) float32 NumPy array.

        We use the CLS token representation, which is the standard choice for
        SPECTER2 document-level embeddings.

        max_length=512 matches the model's training context window.
        """
        import torch

        all_vecs = []
        iterator = range(0, len(texts), batch_size)
        if show_progress_bar:
            iterator = tqdm(iterator, desc="SPECTER2 encode")

        for start in iterator:
            chunk = texts[start : start + batch_size]
            inputs = self.tokenizer(
                chunk,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)

            # CLS token (first token) from the last hidden state
            vecs = outputs.last_hidden_state[:, 0, :].cpu().float().numpy()
            all_vecs.append(vecs)

        return np.vstack(all_vecs)


def load_model(model_name: str = "allenai/specter2_base"):
    """
    Load an embedding model by name.

    If model_name contains "specter2", we load SPECTER2 using plain
    HuggingFace Transformers (no `adapters` library needed).
    Otherwise we fall back to loading a standard SentenceTransformer model.

    The model is downloaded on first use and cached by HuggingFace in
    ~/.cache/huggingface/.

    Parameters
    ----------
    model_name : HuggingFace model name or local path
    """
    if "specter2" in model_name.lower():
        logger.info("Detected SPECTER2 — loading with plain transformers")
        return Specter2Model(base="allenai/specter2_base")
    else:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading SentenceTransformer model: {model_name}")
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
