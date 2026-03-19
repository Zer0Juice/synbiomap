"""
Step 5 — UMAP projection and HDBSCAN clustering.

Loads the embedding cache, projects embeddings to 2D with UMAP, clusters
with HDBSCAN, and saves results for the website and further analysis.

Usage:
    python scripts/05_cluster.py

Output:
    data/embeddings/projections.json  — 2D coordinates and cluster labels per artifact
    data/processed/all_artifacts.csv  — combined artifact table with cluster columns added
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
from src.utils.config import load_config
from src.embed.embeddings import embeddings_to_matrix, _load_cache
from src.cluster.cluster import (
    reduce_dimensions, cluster_hdbscan,
    attach_results_to_df, save_projections,
)

def run():
    cfg = load_config()

    print("=== Step 5: UMAP Projection and HDBSCAN Clustering ===\n")

    # --- 1. Load all artifacts and embedding cache ---
    processed_dir = REPO_ROOT / 'data' / 'processed'
    dfs = []
    for name in ['papers', 'patents', 'projects', 'parts']:
        path = processed_dir / f'{name}.csv'
        if path.exists():
            dfs.append(pd.read_csv(path))

    if not dfs:
        print("ERROR: No processed CSVs found. Run steps 01–03 first.")
        return None

    combined = pd.concat(dfs, ignore_index=True)

    cache_path = REPO_ROOT / 'data' / 'embeddings' / 'embeddings.json'
    cache = _load_cache(str(cache_path))
    print(f"{len(combined)} artifacts, {len(cache)} cached embeddings")

    # --- 2. Build the embedding matrix ---
    matrix, valid_ids = embeddings_to_matrix(combined, cache)
    print(f"Embedding matrix: {matrix.shape}")

    # --- 3. UMAP dimensionality reduction ---
    # UMAP preserves both local and global structure while reducing to 2D.
    # Cosine metric suits text embeddings; random_state ensures reproducibility.
    # See: McInnes et al. (2018), https://arxiv.org/abs/1802.03426
    umap_cfg = cfg['umap']
    print(f"\nRunning UMAP (n_neighbors={umap_cfg['n_neighbors']}, min_dist={umap_cfg['min_dist']})...")
    coords_2d = reduce_dimensions(
        matrix,
        n_components=umap_cfg['n_components'],
        n_neighbors=umap_cfg['n_neighbors'],
        min_dist=umap_cfg['min_dist'],
        metric=umap_cfg['metric'],
        random_state=umap_cfg['random_state'],
    )
    print(f"UMAP output: {coords_2d.shape}")

    # --- 4. HDBSCAN clustering ---
    # HDBSCAN finds clusters of varying density and marks outliers as -1.
    # See: Campello et al. (2013), https://doi.org/10.1007/978-3-642-37456-2_14
    cl_cfg = cfg['clustering']
    print(f"\nRunning HDBSCAN (min_cluster_size={cl_cfg['min_cluster_size']})...")
    labels = cluster_hdbscan(
        coords_2d,
        min_cluster_size=cl_cfg['min_cluster_size'],
        min_samples=cl_cfg['min_samples'],
    )

    label_counts = pd.Series(labels).value_counts().sort_index()
    n_clusters = (label_counts.index >= 0).sum()
    n_noise = label_counts.get(-1, 0)
    print(f"Found {n_clusters} clusters, {n_noise} noise points")
    print(label_counts.head(20).to_string())

    # --- 5. Save results ---
    proj_path = REPO_ROOT / 'data' / 'embeddings' / 'projections.json'
    save_projections(valid_ids, coords_2d, labels, str(proj_path))

    combined_with_clusters = attach_results_to_df(combined, valid_ids, coords_2d, labels)
    all_artifacts_path = processed_dir / 'all_artifacts.csv'
    combined_with_clusters.to_csv(all_artifacts_path, index=False)

    print(f"\nSaved projections.json and all_artifacts.csv")

    return combined_with_clusters


if __name__ == "__main__":
    run()
