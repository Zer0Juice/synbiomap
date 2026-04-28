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
    # Parts are excluded: they are short registry entries without proper abstracts
    # and are not embedded. The iGEM projects that contain them are embedded instead.
    dfs = []
    for name in ['papers', 'patents', 'projects']:
        path = processed_dir / f'{name}.csv'
        if path.exists() and path.stat().st_size > 0:
            try:
                df = pd.read_csv(path)
                if len(df) > 0:
                    dfs.append(df)
            except Exception:
                pass

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

    # --- 3. Two-stage UMAP reduction ---
    # Stage 1: reduce to n_components_cluster dimensions for clustering.
    # Clustering directly on 2D UMAP distorts cluster structure because too much
    # information is lost in the final squeeze. Reducing to 5–20D first preserves
    # local neighbourhood relationships that HDBSCAN relies on.
    # Stage 2: reduce to 2D separately for visualization only.
    # Following: Grootendorst (2022) "BERTopic" arXiv:2203.05794
    # See also: McInnes et al. (2018), https://arxiv.org/abs/1802.03426
    umap_cfg = cfg['umap']
    n_cluster_dims = umap_cfg.get('n_components_cluster', 10)
    n_viz_dims     = umap_cfg.get('n_components_viz', 2)

    print(f"\nStage 1 — UMAP to {n_cluster_dims}D for clustering "
          f"(n_neighbors={umap_cfg['n_neighbors']}, min_dist={umap_cfg['min_dist']})...")
    coords_nd = reduce_dimensions(
        matrix,
        n_components=n_cluster_dims,
        n_neighbors=umap_cfg['n_neighbors'],
        min_dist=umap_cfg['min_dist'],
        metric=umap_cfg['metric'],
        random_state=umap_cfg['random_state'],
    )
    print(f"UMAP output: {coords_nd.shape}")

    print(f"\nStage 2 — UMAP to {n_viz_dims}D for visualization...")
    coords_2d = reduce_dimensions(
        matrix,
        n_components=n_viz_dims,
        n_neighbors=umap_cfg['n_neighbors'],
        min_dist=umap_cfg['min_dist'],
        metric=umap_cfg['metric'],
        random_state=umap_cfg['random_state'],
    )
    print(f"UMAP output: {coords_2d.shape}")

    # --- 4. HDBSCAN clustering (on high-D coords, not 2D) ---
    # HDBSCAN finds clusters of varying density and marks outliers as -1.
    # Running on the high-D output gives better cluster quality than on 2D.
    # See: Campello et al. (2013), https://doi.org/10.1007/978-3-642-37456-2_14
    cl_cfg = cfg['clustering']
    print(f"\nRunning HDBSCAN on {n_cluster_dims}D coords "
          f"(min_cluster_size={cl_cfg['min_cluster_size']})...")
    labels = cluster_hdbscan(
        coords_nd,
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

    # Save high-D coords and valid_ids for step 5b (cluster labeling + sub-clustering).
    # coords_nd is the n_components_cluster-dimensional UMAP output used for HDBSCAN.
    # It is needed to compute cluster centroids for representative title selection.
    # NOTE: if you re-run step 5, delete cluster_labels.json so labels are refreshed
    # for the new clustering (HDBSCAN cluster integers can renumber on each run).
    import numpy as np, json as _json
    nd_path = REPO_ROOT / 'data' / 'embeddings' / 'coords_nd.npy'
    ids_path = REPO_ROOT / 'data' / 'embeddings' / 'valid_ids.json'
    np.save(str(nd_path), coords_nd.astype('float32'))
    with open(ids_path, 'w') as _f:
        _json.dump(valid_ids, _f)

    print(f"\nSaved projections.json and all_artifacts.csv")
    print(f"Saved coords_nd.npy {coords_nd.shape} and valid_ids.json ({len(valid_ids)} ids)")

    return combined_with_clusters


if __name__ == "__main__":
    run()
