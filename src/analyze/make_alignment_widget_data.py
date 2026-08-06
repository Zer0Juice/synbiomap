"""
make_alignment_widget_data.py — export per-project data for the local-alignment widget.

The "Calculating Relatedness" slide makes one headline claim: a student project sits
closer, in embedding space, to its OWN city's average paper than to a typical other
city's papers. Across the eligible projects, ~90% are closer to home. This is the
project-level version of the alignment result the manuscript plots as
`project_level_alignment.png`; see stage_embeddings() in
scripts/export_paper_assets.py for the exact same computation.

For each project in a city that has enough papers to form a stable centroid, we:
  1. L2-normalise the project embedding,
  2. take the cosine to every eligible city's unit paper-centroid,
  3. record `own`  = cosine to the project's own city, and
     `other` = mean cosine to all OTHER cities,
  4. δ = own − other.  δ > 0 means "closer to home".

The interactive scatter plots `other` (x) against `own` (y) with the y = x line;
90% of the dots land above it. This script writes the small JSON the widget reads.
No embeddings are recomputed at page-load time — everything heavy happens here.

    python src/analyze/make_alignment_widget_data.py

Reads : data/processed/papers.csv, data/processed/projects.csv
        data/embeddings/embeddings.json  (cached SPECTER2 vectors, via _load_cache)
Writes: website/assets/data/project_alignment.json
        [{title, city, country, year, own, other}]  (+ a `meta` summary object at [0])
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"
EMB_FILE = ROOT / "data" / "embeddings" / "embeddings.json"
BATCH_DIR = ROOT / "data" / "embeddings" / "embeddings_batches"
OUT = ROOT / "website" / "assets" / "data" / "project_alignment.json"

MIN_CITY_PAPERS = 3  # a city needs >= 3 papers before its centroid is stable enough to use


def unit_centroid(vectors: np.ndarray) -> np.ndarray:
    """Mean of a set of embedding vectors, L2-normalised."""
    c = vectors.mean(axis=0)
    n = np.linalg.norm(c)
    return c / n if n > 0 else c


def load_cache() -> dict:
    """Merge the cached SPECTER2 vectors into an id -> np.array dict.

    This mirrors embed.embeddings._load_cache but avoids importing that module
    (which pulls in torch/transformers). Reads the legacy embeddings.json if present,
    then the incremental batch_*.txt / batch_*.npy pairs, which take precedence.
    """
    import json as _json

    cache: dict = {}
    if EMB_FILE.exists():
        with open(EMB_FILE) as f:
            cache.update(_json.load(f))
    if BATCH_DIR.exists():
        for ids_file in sorted(BATCH_DIR.glob("*.txt")):
            vecs_file = ids_file.with_suffix(".npy")
            if not vecs_file.exists():
                continue
            ids = ids_file.read_text().splitlines()
            vecs = np.load(vecs_file)
            for artifact_id, vec in zip(ids, vecs):
                cache[artifact_id] = vec
    return cache


def main() -> None:
    cache = load_cache()
    print(f"loaded {len(cache):,} cached embeddings")
    if not cache:
        sys.exit("no embeddings in cache — nothing to do")

    papers = pd.read_csv(DATA / "papers.csv", usecols=["id", "city", "year"])
    projects = pd.read_csv(
        DATA / "projects.csv", usecols=["id", "title", "city", "country", "year"]
    )
    for df in (papers, projects):
        df["city_key"] = df["city"].astype(str).str.strip().str.lower()

    # Attach embeddings; drop rows whose id was never embedded.
    def attach(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["emb"] = df["id"].map(cache.get)
        df = df.dropna(subset=["emb"]).reset_index(drop=True)
        df["emb"] = df["emb"].map(lambda v: np.asarray(v, dtype=np.float32))
        return df

    pap, proj = attach(papers), attach(projects)
    print(f"papers w/ emb: {len(pap):,}   projects w/ emb: {len(proj):,}")

    # --- Eligible city paper-centroids (>= MIN_CITY_PAPERS papers each) ---
    counts = pap.groupby("city_key").size()
    eligible = [c for c, n in counts.items() if n >= MIN_CITY_PAPERS]
    cmat = np.stack(
        [unit_centroid(np.stack(pap.loc[pap.city_key == c, "emb"].to_numpy())) for c in eligible]
    ).astype(np.float32)
    idx = {c: i for i, c in enumerate(eligible)}
    print(f"{len(eligible)} eligible cities (>= {MIN_CITY_PAPERS} papers)")

    # --- Project-level own-city vs other-city similarity ---
    pv = proj[proj.city_key.isin(idx)].reset_index(drop=True)
    P = np.stack(pv["emb"].to_numpy()).astype(np.float32)
    P /= np.clip(np.linalg.norm(P, axis=1, keepdims=True), 1e-8, None)
    sims = P @ cmat.T
    own = sims[np.arange(len(pv)), pv.city_key.map(idx).to_numpy()]
    other = (sims.sum(axis=1) - own) / (len(eligible) - 1)
    delta = own - other

    frac_pos = float((delta > 0).mean())
    print(f"{len(pv):,} projects · closer-to-home {frac_pos:.1%} · mean δ {delta.mean():+.4f}")

    # --- Assemble records. A short title keeps the JSON small but hovers useful. ---
    def short(t: str, n: int = 80) -> str:
        t = str(t).strip()
        return t if len(t) <= n else t[: n - 1] + "…"

    rows = [
        {
            "title": short(r.title),
            "city": str(r.city).strip(),
            "country": ("" if pd.isna(r.country) else str(r.country).strip()),
            "year": (None if pd.isna(r.year) else int(r.year)),
            "own": round(float(o), 4),
            "other": round(float(ot), 4),
        }
        for r, o, ot in zip(pv.itertuples(), own, other)
    ]

    meta = {
        "meta": True,
        "n_projects": len(pv),
        "n_cities": len(eligible),
        "frac_pos": round(frac_pos, 4),
        "mean_delta": round(float(delta.mean()), 4),
        "min_city_papers": MIN_CITY_PAPERS,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump([meta, *rows], f, separators=(",", ":"))
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
