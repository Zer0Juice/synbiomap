"""
cluster.py — dimensionality reduction (UMAP) and clustering (HDBSCAN).

Pipeline:
  1. Take high-dimensional embeddings (e.g. 384-dim for MiniLM)
  2. Reduce to 2D with UMAP (for visualization) and optionally higher-D
     (for better clustering, since 2D can distort cluster structure)
  3. Cluster with HDBSCAN on the reduced space

Why UMAP + HDBSCAN?
  These are standard choices for embedding-based text clustering.
  UMAP preserves both local and global structure better than t-SNE.
  HDBSCAN does not require a fixed number of clusters and handles
  noise (unlabeled outliers) gracefully.

References:
  UMAP: McInnes et al. (2018) arXiv:1802.03426
  HDBSCAN: Campello et al. (2013) ECML PKDD
  Applied to text: Grootendorst (2022) "BERTopic" arXiv:2203.05794
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def reduce_dimensions(
    matrix: np.ndarray,
    n_components: int = 2,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    metric: str = "cosine",
    random_state: int = 42,
) -> np.ndarray:
    """
    Reduce embedding matrix to lower dimensions with UMAP.

    Parameters
    ----------
    matrix : shape (n_samples, embedding_dim)
    n_components : output dimensionality (2 for visualization, 5–15 for clustering)
    n_neighbors : UMAP hyperparameter — controls local vs. global structure balance.
                  Smaller = more local detail; larger = more global shape.
    min_dist : UMAP hyperparameter — minimum distance between points in low-dim space.
               Smaller = tighter clusters; larger = more uniform spread.
    metric : distance metric for UMAP; "cosine" suits text embeddings
    random_state : random seed for reproducibility

    Returns
    -------
    reduced : shape (n_samples, n_components)
    """
    import umap

    logger.info(
        f"Running UMAP: {matrix.shape} → {n_components}D "
        f"(n_neighbors={n_neighbors}, min_dist={min_dist})"
    )
    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
        low_memory=False,
    )
    reduced = reducer.fit_transform(matrix)
    logger.info("UMAP complete.")
    return reduced


def cluster_hdbscan(
    reduced: np.ndarray,
    min_cluster_size: int = 10,
    min_samples: int = 5,
    metric: str = "euclidean",
) -> np.ndarray:
    """
    Cluster a reduced embedding matrix with HDBSCAN.

    Parameters
    ----------
    reduced : shape (n_samples, n_components) — output of reduce_dimensions
    min_cluster_size : minimum number of points to form a cluster.
                       Larger = fewer, broader clusters.
    min_samples : controls how conservative clustering is.
                  Higher = more points labeled as noise (label = -1).
    metric : distance metric; "euclidean" is standard for UMAP-reduced data

    Returns
    -------
    labels : integer cluster labels, shape (n_samples,)
             -1 means the point was classified as noise / no cluster
    """
    import hdbscan

    logger.info(
        f"Running HDBSCAN: min_cluster_size={min_cluster_size}, "
        f"min_samples={min_samples}"
    )
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric=metric,
        prediction_data=True,
    )
    labels = clusterer.fit_predict(reduced)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = (labels == -1).sum()
    logger.info(f"HDBSCAN: {n_clusters} clusters, {n_noise} noise points.")
    return labels


def attach_results_to_df(
    df: pd.DataFrame,
    valid_ids: list[str],
    coords_2d: np.ndarray,
    labels: np.ndarray,
    id_col: str = "id",
) -> pd.DataFrame:
    """
    Add UMAP coordinates and cluster labels back to the main DataFrame.

    Rows without embeddings (not in valid_ids) get NaN for coords and -1
    for cluster label.

    Returns a copy of df with new columns: umap_x, umap_y, cluster_label
    """
    # Build mapping: id → (x, y, label)
    id_to_result = {
        artifact_id: (coords_2d[i, 0], coords_2d[i, 1], int(labels[i]))
        for i, artifact_id in enumerate(valid_ids)
    }

    df = df.copy()
    df["umap_x"] = df[id_col].map(lambda i: id_to_result.get(i, (None, None, -1))[0])
    df["umap_y"] = df[id_col].map(lambda i: id_to_result.get(i, (None, None, -1))[1])
    df["cluster_label"] = df[id_col].map(lambda i: id_to_result.get(i, (None, None, -1))[2])

    return df


def save_projections(
    valid_ids: list[str],
    coords_2d: np.ndarray,
    labels: np.ndarray,
    output_path: str | Path,
):
    """
    Save UMAP coordinates and cluster labels to a JSON file for the website.

    The website's JavaScript reads this file to render the semantic space
    explorer without any server-side computation.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = [
        {"id": artifact_id, "x": float(coords_2d[i, 0]), "y": float(coords_2d[i, 1]), "cluster": int(labels[i])}
        for i, artifact_id in enumerate(valid_ids)
    ]
    with open(output_path, "w") as f:
        json.dump(data, f)
    logger.info(f"Saved {len(data)} projections to {output_path}")
