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

    # --- 2a. Export artifacts.json (lightweight — no text) ---
    # Omit 'text' here to keep the file small (~1 MB vs 20 MB).
    # The abstract text is stored separately in abstracts.json and fetched
    # lazily only when the user clicks an artifact in the explorer.
    web_cols = ['id', 'type', 'title', 'year', 'city', 'country',
                'lat', 'lon', 'case_study_flag', 'cluster_label']

    # Convert to records, then replace float NaN with None.
    # pandas .where() doesn't work for float columns (None becomes NaN again),
    # so we do a post-pass. Browsers reject NaN — it is not valid JSON.
    import math
    def _clean(val):
        if isinstance(val, float) and math.isnan(val):
            return None
        return val

    artifacts = [
        {k: _clean(v) for k, v in row.items()}
        for row in df[web_cols].to_dict(orient='records')
    ]

    with open(web_data_dir / 'artifacts.json', 'w') as f:
        json.dump(artifacts, f)
    print(f"Wrote artifacts.json ({len(artifacts)} records)")

    # --- 2b. Export abstracts.json (id → abstract text, fetched on demand) ---
    # The 'text' field is "Title. Abstract…". We strip the title prefix to
    # store only the abstract, saving space and avoiding redundancy.
    abstracts = {}
    for _, row in df[['id', 'title', 'text']].iterrows():
        text  = row['text'] if pd.notnull(row['text']) else ""
        title = row['title'] if pd.notnull(row['title']) else ""
        abstract = text
        if title and text.startswith(title):
            abstract = text[len(title):].lstrip(". ").strip()
        if abstract:
            abstracts[row['id']] = abstract

    with open(web_data_dir / 'abstracts.json', 'w') as f:
        json.dump(abstracts, f)
    print(f"Wrote abstracts.json ({len(abstracts)} entries)")

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
