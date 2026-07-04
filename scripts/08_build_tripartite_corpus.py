"""
Step 8 — Build the three-type artifact corpus for the tripartite city analysis.

Combines papers.csv, projects.csv and patents.csv into one table on the shared
schema, so the successor to notebook 01 can embed and cluster all three artifact
types together in the fine-tuned space. The old all_artifacts.csv held only
papers and projects; this adds patents as the third node.

Output
------
  data/processed/artifacts_tripartite.csv   (paper + project + patent rows)

Geography note
--------------
Patents are geocoded to INVENTOR cities — where the research was done — following
Breschi & Lissoni (2001), and are split fractionally across multiple inventor
cities in patent_city_weights.csv. The `city` column used here is the primary
(first located inventor) city, matching how papers and projects use their primary
institution city, so the three types are treated consistently. The fractional
weights remain available for a robustness check.

Usage
-----
  python scripts/08_build_tripartite_corpus.py
"""

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.schema import REQUIRED_COLUMNS

PROCESSED = REPO_ROOT / "data" / "processed"
OUT = PROCESSED / "artifacts_tripartite.csv"

SOURCES = {
    "paper":   PROCESSED / "papers.csv",
    "project": PROCESSED / "projects.csv",
    "patent":  PROCESSED / "patents.csv",
}


def load_typed(path: Path, expected_type: str) -> pd.DataFrame:
    """Load one source CSV, keep only the shared-schema columns, and coerce type."""
    df = pd.read_csv(path, low_memory=False)
    # Fill any missing shared columns so the three frames align exactly.
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[REQUIRED_COLUMNS].copy()
    # The type column should already say paper/project/patent, but normalise it
    # so a mislabelled source can't silently pollute the corpus.
    df["type"] = expected_type
    return df


def run():
    frames = []
    print(f"{'type':9} {'rows':>7} {'with_city':>10} {'with_text':>10}")
    for typ, path in SOURCES.items():
        df = load_typed(path, typ)
        frames.append(df)
        print(f"{typ:9} {len(df):>7} {int(df['city'].notna().sum()):>10} "
              f"{int(df['text'].notna().sum()):>10}")

    combined = pd.concat(frames, ignore_index=True)

    # A row is only usable in the analysis if it has both text (to embed) and a
    # city (to place). Keep everything here — the notebook applies its own floors —
    # but report how many clear the bar so problems surface early.
    usable = combined["text"].notna() & combined["city"].notna()
    print(f"\nCombined: {len(combined):,} rows  "
          f"({int(usable.sum()):,} with both text and city)")
    print("By type:", combined["type"].value_counts().to_dict())

    combined.to_csv(OUT, index=False)
    print(f"\nSaved: {OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    run()
