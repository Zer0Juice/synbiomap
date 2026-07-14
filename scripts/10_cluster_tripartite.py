"""
Step 10 — Cluster the three-type corpus in the fine-tuned space.

Runs UMAP -> HDBSCAN on the fine-tuned embeddings of papers + projects + patents,
so topic clusters are defined jointly across all three artifact types. The
per-document cluster label is the input to the decisive cluster co-membership
test in the notebook; the 2D coordinates feed the website's semantic-space map.

Why cluster jointly (not per type)?
  The whole question is whether a city's three artifact types share topics. That
  only means something if the topics are one shared partition that all three types
  are scored against. Clustering each type separately would beg the question.

Why UMAP -> HDBSCAN?
  768 dimensions are too sparse to cluster directly (curse of dimensionality); we
  reduce first. We cluster on a higher-D reduction (density structure survives
  better than in 2D) and keep a separate 2D reduction only for plotting.
  HDBSCAN needs no fixed k and labels low-density documents as noise (-1), which
  we drop from the topic measure. References: McInnes et al. (2018); Campello et
  al. (2013); Grootendorst (2022, BERTopic).

Outputs
-------
  data/processed/artifacts_tripartite_clustered.csv   (+ cluster_label, umap_x/y)
  data/embeddings/finetuned/projections.json          (id, x, y, cluster)

Usage
-----
  python scripts/10_cluster_tripartite.py
  python scripts/10_cluster_tripartite.py --min-cluster-size 60 --cluster-dims 10
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.embed.embeddings import _load_cache
from src.cluster.cluster import (
    reduce_dimensions, cluster_hdbscan, attach_results_to_df, save_projections,
)

PROCESSED = REPO_ROOT / "data" / "processed"
DEFAULT_CORPUS = PROCESSED / "artifacts_tripartite.csv"
DEFAULT_CACHE  = REPO_ROOT / "data" / "embeddings" / "finetuned" / "embeddings.json"
DEFAULT_OUT    = PROCESSED / "artifacts_tripartite_clustered.csv"
DEFAULT_PROJ   = REPO_ROOT / "data" / "embeddings" / "finetuned" / "projections.json"


def run(args):
    df = pd.read_csv(args.corpus, low_memory=False)
    cache = _load_cache(args.cache)
    valid = df[df["id"].isin(cache)].copy().reset_index(drop=True)
    print(f"Documents with embeddings: {len(valid):,} / {len(df):,}  "
          f"{valid['type'].value_counts().to_dict()}")

    ids = valid["id"].tolist()
    X = np.asarray([cache[i] for i in ids], dtype=np.float32)
    print(f"Embedding matrix: {X.shape}")

    # 2D for plotting, higher-D for clustering.
    print("UMAP -> 2D (for the map)...")
    coords_2d = reduce_dimensions(X, n_components=2,
                                  n_neighbors=args.n_neighbors, min_dist=0.1)
    print(f"UMAP -> {args.cluster_dims}D (for clustering)...")
    coords_hd = reduce_dimensions(X, n_components=args.cluster_dims,
                                  n_neighbors=args.n_neighbors, min_dist=0.0)

    labels = cluster_hdbscan(
        coords_hd,
        min_cluster_size=args.min_cluster_size,
        min_samples=args.min_samples,
        cluster_selection_method=args.method,
    )

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int((labels == -1).sum())
    print(f"\nClusters: {n_clusters}   noise: {n_noise:,} ({n_noise/len(labels):.1%})")

    # Cluster composition by artifact type, and which cluster is carbon capture.
    comp = valid[["type"]].copy()
    comp["cluster"] = labels
    comp["cc"] = valid["case_study_flag"].astype(str).str.lower().isin(["true", "1", "1.0"]).values
    per = comp[comp["cluster"] >= 0].groupby("cluster")
    print(f"\n{'clu':>4} {'n':>6} {'papers':>7} {'proj':>6} {'patent':>7} {'cc_share':>9}")
    for cl, g in per:
        vc = g["type"].value_counts()
        print(f"{cl:>4} {len(g):>6} {vc.get('paper',0):>7} {vc.get('project',0):>6} "
              f"{vc.get('patent',0):>7} {g['cc'].mean():>9.2%}")
    cc_cluster = comp[comp["cluster"] >= 0].groupby("cluster")["cc"].mean().idxmax()
    print(f"\nCarbon-capture cluster (highest cc share): cluster {cc_cluster}")

    out = attach_results_to_df(df, ids, coords_2d, labels)
    out.to_csv(args.out, index=False)
    save_projections(ids, coords_2d, labels, args.proj)
    print(f"\nSaved:\n  {args.out}\n  {args.proj}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Cluster the tripartite corpus in the fine-tuned space.")
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS,
                   help="Corpus CSV to cluster (default artifacts_tripartite.csv).")
    p.add_argument("--cache", type=Path, default=DEFAULT_CACHE,
                   help="Embedding cache file (default finetuned/embeddings.json).")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT,
                   help="Clustered-corpus output CSV.")
    p.add_argument("--proj", type=Path, default=DEFAULT_PROJ,
                   help="Projections JSON output for the website map.")
    p.add_argument("--n-neighbors", type=int, default=15, help="UMAP n_neighbors (default 15)")
    p.add_argument("--cluster-dims", type=int, default=10, help="UMAP dims for clustering (default 10)")
    p.add_argument("--min-cluster-size", type=int, default=50,
                   help="HDBSCAN min cluster size (default 50; larger = fewer, broader topics)")
    p.add_argument("--min-samples", type=int, default=10, help="HDBSCAN min_samples (default 10)")
    p.add_argument("--method", default="eom", choices=["eom", "leaf"],
                   help="HDBSCAN cluster selection (default eom)")
    run(p.parse_args())
