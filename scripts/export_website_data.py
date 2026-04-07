"""
export_website_data.py
----------------------
Generates the three JSON data files needed by the website's interactive
visualizations from the processed pipeline outputs.

Outputs (written to website/assets/data/):
  artifacts.json   — array of artifact metadata records
  projections.json — array of {id, x, y, cluster} for the UMAP scatter plot
  cities.json      — aggregated city-level counts for the geo map

Run from the project root:
    python scripts/export_website_data.py
"""

import json
import math
import os
import sys
from pathlib import Path

import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
EMBEDDINGS = ROOT / "data" / "embeddings"
OUT_DIR = ROOT / "website" / "assets" / "data"

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Load all_artifacts.csv ─────────────────────────────────────────────────────
artifacts_path = PROCESSED / "all_artifacts.csv"
if not artifacts_path.exists():
    print(f"ERROR: {artifacts_path} not found. Run the pipeline first.", file=sys.stderr)
    sys.exit(1)

print(f"Loading {artifacts_path} ...")
df = pd.read_csv(artifacts_path, low_memory=False)
print(f"  {len(df):,} rows loaded.")

# Normalise type values (pipeline may use 'paper' or 'papers', etc.)
type_map = {"papers": "paper", "patents": "patent", "projects": "project", "parts": "part"}
df["type"] = df["type"].str.strip().replace(type_map)


# ── 1. artifacts.json ─────────────────────────────────────────────────────────
# Keep only the fields the JS needs; drop heavy text columns.
artifact_cols = [
    "id", "type", "title", "year", "city", "country", "lat", "lon",
    "theme_primary", "theme_secondary",
    "case_study_flag", "case_study_confidence",
    "cluster_label",
]
existing_cols = [c for c in artifact_cols if c in df.columns]
artifacts_df = df[existing_cols].copy()

# Convert NaN → None so JSON serialises cleanly
artifacts_records = []
for row in artifacts_df.itertuples(index=False):
    rec = {}
    for col in existing_cols:
        val = getattr(row, col)
        if isinstance(val, float) and math.isnan(val):
            rec[col] = None
        elif hasattr(val, "item"):          # numpy scalar
            rec[col] = val.item()
        else:
            rec[col] = val
    artifacts_records.append(rec)

artifacts_out = OUT_DIR / "artifacts.json"
with open(artifacts_out, "w") as f:
    json.dump(artifacts_records, f, separators=(",", ":"))
print(f"  → {artifacts_out} ({len(artifacts_records):,} records)")


# ── 2. projections.json ───────────────────────────────────────────────────────
# Prefer data/embeddings/projections.json if it exists (already has x,y,cluster).
emb_proj = EMBEDDINGS / "projections.json"

if emb_proj.exists() and emb_proj.stat().st_size > 100:
    print(f"Loading projections from {emb_proj} ...")
    with open(emb_proj) as f:
        projections = json.load(f)
    print(f"  {len(projections):,} projection records.")
elif "umap_x" in df.columns and "umap_y" in df.columns:
    # Fall back to columns in all_artifacts.csv
    print("Building projections from umap_x / umap_y columns in all_artifacts.csv ...")
    proj_df = df[["id", "umap_x", "umap_y", "cluster_label"]].copy()
    proj_df = proj_df.dropna(subset=["umap_x", "umap_y"])
    projections = [
        {
            "id": row.id,
            "x": float(row.umap_x),
            "y": float(row.umap_y),
            "cluster": int(row.cluster_label) if not (isinstance(row.cluster_label, float) and math.isnan(row.cluster_label)) else -1,
        }
        for row in proj_df.itertuples(index=False)
    ]
    print(f"  {len(projections):,} projection records.")
else:
    print("WARNING: No projection data found. projections.json will be empty.", file=sys.stderr)
    projections = []

proj_out = OUT_DIR / "projections.json"
with open(proj_out, "w") as f:
    json.dump(projections, f, separators=(",", ":"))
print(f"  → {proj_out}")


# ── 3. cities.json ────────────────────────────────────────────────────────────
print("Building cities.json ...")

# Work from rows that have valid coordinates
geo_df = df.dropna(subset=["lat", "lon", "city"]).copy()

# case_study_flag may be stored as string 'True'/'False' or bool
geo_df["_cc"] = geo_df["case_study_flag"].astype(str).str.lower() == "true"

city_records = []
for (city, country), grp in geo_df.groupby(["city", "country"], dropna=True):
    lat = float(grp["lat"].iloc[0])
    lon = float(grp["lon"].iloc[0])
    rec = {
        "city": city,
        "country": country,
        "lat": lat,
        "lon": lon,
        "count_papers": int((grp["type"] == "paper").sum()),
        "count_patents": int((grp["type"] == "patent").sum()),
        "count_projects": int((grp["type"] == "project").sum()),
        "count_parts": int((grp["type"] == "part").sum()),
        "count_carbon_capture": int(grp["_cc"].sum()),
    }
    city_records.append(rec)

# Sort by total activity descending
city_records.sort(
    key=lambda c: c["count_papers"] + c["count_patents"] + c["count_projects"] + c["count_parts"],
    reverse=True,
)

cities_out = OUT_DIR / "cities.json"
with open(cities_out, "w") as f:
    json.dump(city_records, f, separators=(",", ":"))
print(f"  → {cities_out} ({len(city_records):,} cities)")

print("\nDone. Website data files are ready.")
