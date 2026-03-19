"""
Step 1 — Ingest papers from OpenAlex.

Downloads synthetic biology papers, normalizes them to the shared schema,
tags carbon-capture papers, and saves data/processed/papers.csv.

Usage:
    python scripts/01_ingest_papers.py

Requires:
    OPENALEX_EMAIL set in .env (optional but recommended for higher rate limits)
"""

import sys
from pathlib import Path

# Make sure imports resolve from repo root regardless of where you run this from
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import openalex, normalize

def run():
    cfg = load_config()

    print("=== Step 1: Ingest Papers from OpenAlex ===\n")
    print("Seed keywords:", cfg['corpus']['seed_keywords'])

    # --- 1. Fetch papers ---
    raw_works = []
    for work in openalex.search_papers(
        keywords=cfg['corpus']['seed_keywords'],
        year_min=cfg['corpus']['year_min'],
        year_max=cfg['corpus'].get('year_max'),
        max_results=cfg['corpus']['openalex_max_results'],
    ):
        raw_works.append(openalex.extract_fields(work))

    print(f"\nDownloaded {len(raw_works)} works from OpenAlex.")

    # --- 2. Normalize to shared schema ---
    papers_df = normalize.normalize_papers(
        raw_records=raw_works,
        carbon_keywords=cfg['corpus']['carbon_capture_keywords'],
    )

    print(f"Normalized: {len(papers_df)} papers")
    print(f"Carbon capture: {papers_df['case_study_flag'].sum()} papers tagged")

    # --- 3. Save ---
    output_path = REPO_ROOT / 'data' / 'processed' / 'papers.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    papers_df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path.relative_to(REPO_ROOT)}")

    # --- 4. Quick summary ---
    print(f"\nYear range: {papers_df['year'].min()} — {papers_df['year'].max()}")
    print("\nTop countries:")
    print(papers_df['country'].value_counts().head(10).to_string())
    print("\nTop cities:")
    print(papers_df['city'].value_counts().head(10).to_string())

    return papers_df


if __name__ == "__main__":
    run()
