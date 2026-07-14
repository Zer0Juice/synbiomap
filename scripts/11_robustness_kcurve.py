"""
Step 11 — Clustering-resolution robustness for the decisive test.

Re-clusters the fine-tuned embeddings with KMeans at a range of granularities
(k topics, coarse to fine) and re-runs the within-country co-membership
permutation at each k, for the paper-project and paper-patent links. If the
signal is real it should survive the whole sweep, not appear only at the one
HDBSCAN partition used in the notebook. Using KMeans here also shows the result
is not an artifact of HDBSCAN specifically.

Output
------
  data/processed/robustness_kcurve.csv   (k, type_a, type_b, observed, null, p, ...)

Usage
-----
  python scripts/11_robustness_kcurve.py
  python scripts/11_robustness_kcurve.py --ks 10 20 40 60 80 120 --n-perm 1000
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.embed.embeddings import _load_cache
from src.analyze.robustness import kmeans_labels, decisive_for_labels

PROCESSED = REPO_ROOT / "data" / "processed"
DEFAULT_CORPUS = PROCESSED / "artifacts_tripartite_clustered.csv"
DEFAULT_CACHE  = REPO_ROOT / "data" / "embeddings" / "finetuned" / "embeddings.json"
DEFAULT_OUT    = PROCESSED / "robustness_kcurve.csv"

PAIRS = [("paper", "project"), ("paper", "patent"), ("project", "patent")]
MIN_DOCS = 5


def run(ks, n_perm, corpus, cache_file, out):
    arts = pd.read_csv(corpus, low_memory=False)
    arts["city_key"] = arts["city"].astype(str).str.strip().str.lower()
    cache = _load_cache(cache_file)

    valid = arts[arts["id"].isin(cache)].copy().reset_index(drop=True)
    ids = valid["id"].tolist()
    X = np.asarray([cache[i] for i in ids], dtype=np.float32)
    print(f"Embeddings: {X.shape}")

    country_of = (
        arts.groupby("city_key")["country"]
        .agg(lambda s: s.dropna().iloc[0] if s.notna().any() else None).to_dict()
    )
    city_name = arts.groupby("city_key")["city"].first().to_dict()

    all_rows = []
    for k in ks:
        print(f"KMeans k={k} ...", flush=True)
        labels = kmeans_labels(X, k)
        rows = decisive_for_labels(arts, labels, ids, k, PAIRS, MIN_DOCS,
                                   country_of, city_name, n_perm=n_perm)
        for r in rows:
            print(f"  {r['type_a']:8}x{r['type_b']:8} cities={r['n_cities']:3} "
                  f"excess={r['excess']:+.4f} p={r['p_value']:.4f}")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_csv(out, index=False)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Clustering-resolution robustness sweep.")
    p.add_argument("--ks", type=int, nargs="+", default=[10, 20, 40, 60, 80, 120])
    p.add_argument("--n-perm", type=int, default=1000)
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS,
                   help="Clustered corpus CSV (default artifacts_tripartite_clustered.csv).")
    p.add_argument("--cache", type=Path, default=DEFAULT_CACHE,
                   help="Embedding cache file (default finetuned/embeddings.json).")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT,
                   help="Output CSV (default robustness_kcurve.csv).")
    a = p.parse_args()
    run(a.ks, a.n_perm, a.corpus, a.cache, a.out)
