"""
Step 6 — Export data for website visualizations.

Loads the clustered artifact data and exports lightweight JSON files that
the website's JavaScript reads to render the Semantic Space Explorer and
Geographic View.

Usage:
    python scripts/06_visualize.py

Output (written to website/assets/data/):
    artifacts.json    — one record per artifact with metadata
    projections.json  — UMAP coordinates (copied from data/embeddings/)
    cities.json       — city-level counts by artifact type
"""

import sys
import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
from src.utils.config import load_config

def run():
    cfg = load_config()

    print("=== Step 6: Export Data for Website ===\n")

    processed_dir = REPO_ROOT / 'data' / 'processed'
    embeddings_dir = REPO_ROOT / 'data' / 'embeddings'
    web_data_dir = REPO_ROOT / 'website' / 'assets' / 'data'
    web_data_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. Load combined artifact data ---
    all_artifacts_path = processed_dir / 'all_artifacts.csv'
    if not all_artifacts_path.exists():
        print("ERROR: all_artifacts.csv not found. Run step 05 first.")
        return

    df = pd.read_csv(all_artifacts_path)
    print(f"{len(df)} artifacts loaded")

    # --- 2. Export artifacts.json ---
    # Only keep the fields the website needs to keep the file small.
    web_cols = ['id', 'type', 'title', 'year', 'city', 'country',
                'case_study_flag', 'cluster_label']
    artifacts = (
        df[web_cols]
        .where(pd.notnull(df[web_cols]), None)
        .to_dict(orient='records')
    )

    with open(web_data_dir / 'artifacts.json', 'w') as f:
        json.dump(artifacts, f)
    print(f"Wrote artifacts.json ({len(artifacts)} records)")

    # --- 3. Copy projections.json to website ---
    proj_src = embeddings_dir / 'projections.json'
    if proj_src.exists():
        shutil.copy(proj_src, web_data_dir / 'projections.json')
        print("Copied projections.json")
    else:
        print("WARNING: projections.json not found. Run step 05 first.")

    # --- 4. Build and export cities.json ---
    city_df = df.dropna(subset=['city', 'lat', 'lon'])

    cities = (
        city_df.groupby(['city', 'country', 'lat', 'lon'])
        .apply(lambda g: pd.Series({
            'count_papers':         (g['type'] == 'paper').sum(),
            'count_patents':        (g['type'] == 'patent').sum(),
            'count_projects':       (g['type'] == 'project').sum(),
            'count_parts':          (g['type'] == 'part').sum(),
            'count_carbon_capture': int(g['case_study_flag'].sum()),
        }))
        .reset_index()
        .to_dict(orient='records')
    )

    with open(web_data_dir / 'cities.json', 'w') as f:
        json.dump(cities, f)
    print(f"Wrote cities.json ({len(cities)} cities)")

    print(f"\nAll files written to {web_data_dir.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    run()
