"""
Step 2 — Ingest patents from Lens.org.

Downloads synthetic biology patents, normalizes them to the shared schema,
tags carbon-capture patents, and saves data/processed/patents.csv.

Usage:
    python scripts/02_ingest_patents.py

Requires:
    LENS_API_TOKEN set in .env
    Get a free token at https://www.lens.org/lens/user/subscriptions
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import lens, normalize

def run():
    cfg = load_config()

    print("=== Step 2: Ingest Patents from Lens.org ===\n")

    # --- 1. Fetch patents ---
    raw_patents = lens.search_patents(
        keywords=cfg['corpus']['seed_keywords'],
        year_min=cfg['corpus']['year_min'],
        year_max=cfg['corpus'].get('year_max'),
        max_results=cfg['corpus']['lens_max_results'],
    )

    raw_records = [lens.extract_fields(p) for p in raw_patents]
    print(f"Downloaded {len(raw_records)} patents from Lens.org.")

    # --- 2. Normalize and tag ---
    patents_df = normalize.normalize_patents(
        raw_records=raw_records,
        carbon_keywords=cfg['corpus']['carbon_capture_keywords'],
    )

    print(f"Normalized: {len(patents_df)} patents")
    print(f"Carbon capture: {patents_df['case_study_flag'].sum()} patents tagged")

    # --- 3. Save ---
    output_path = REPO_ROOT / 'data' / 'processed' / 'patents.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    patents_df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path.relative_to(REPO_ROOT)}")

    print("\nTop countries:")
    print(patents_df['country'].value_counts().head(10).to_string())

    return patents_df


if __name__ == "__main__":
    run()
