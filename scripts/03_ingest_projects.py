"""
Step 3 — Ingest iGEM projects and parts.

Loads iGEM data from local CSV files, normalizes them to the shared schema,
and saves data/processed/projects.csv and data/processed/parts.csv.

Usage:
    python scripts/03_ingest_projects.py

Requires:
    data/raw/projects/igem_projects.csv
    data/raw/parts/igem_parts.csv

See src/ingest/igem.py for instructions on how to obtain these files.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import igem, normalize

def run():
    cfg = load_config()

    print("=== Step 3: Ingest iGEM Projects and Parts ===\n")

    # --- 1. Load and normalize projects ---
    # Accept either the canonical name or the actual downloaded filename
    _alt = REPO_ROOT / 'data' / 'raw' / 'projects' / 'igem_teams_with_descriptions_2004_2025.csv'
    projects_path = REPO_ROOT / 'data' / 'raw' / 'projects' / 'igem_projects.csv'
    if not projects_path.exists() and _alt.exists():
        projects_path = _alt
    if not projects_path.exists():
        print(f"ERROR: {projects_path.relative_to(REPO_ROOT)} not found.")
        print("Download iGEM project data and place it there first.")
        print("See src/ingest/igem.py for instructions.")
        return None, None

    raw_projects_df = igem.load_projects(str(projects_path))
    raw_project_records = [igem.extract_project_fields(row) for _, row in raw_projects_df.iterrows()]

    projects_df = normalize.normalize_projects(
        raw_records=raw_project_records,
        carbon_keywords=cfg['corpus']['carbon_capture_keywords'],
    )

    print(f"Projects: {len(projects_df)}, carbon capture: {projects_df['case_study_flag'].sum()}")

    # --- 2. Load and normalize parts (optional — run 03b_fetch_parts.py first) ---
    parts_path = REPO_ROOT / 'data' / 'raw' / 'parts' / 'igem_parts.csv'
    if not parts_path.exists():
        print(f"WARNING: {parts_path.relative_to(REPO_ROOT)} not found.")
        print("Skipping parts — run scripts/03b_fetch_parts.py to generate it.")
        import pandas as pd
        parts_df = pd.DataFrame()
    else:
        raw_parts_df = igem.load_parts(str(parts_path))
        raw_part_records = [igem.extract_part_fields(row) for _, row in raw_parts_df.iterrows()]

        parts_df = normalize.normalize_parts(
            raw_records=raw_part_records,
            carbon_keywords=cfg['corpus']['carbon_capture_keywords'],
        )

        print(f"Parts: {len(parts_df)}, carbon capture: {parts_df['case_study_flag'].sum()}")

    # --- 3. Save ---
    processed_dir = REPO_ROOT / 'data' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)

    projects_df.to_csv(processed_dir / 'projects.csv', index=False)
    print(f"Saved projects.csv to {processed_dir.relative_to(REPO_ROOT)}/")

    # Only write parts.csv if there is actual data — an empty file causes
    # pandas errors in later steps.
    if len(parts_df) > 0:
        parts_df.to_csv(processed_dir / 'parts.csv', index=False)
        print(f"Saved parts.csv ({len(parts_df)} parts) to {processed_dir.relative_to(REPO_ROOT)}/")
    else:
        print("No parts data — parts.csv not written. Run scripts/03b_fetch_parts.py to add parts.")

    return projects_df, parts_df


if __name__ == "__main__":
    run()
