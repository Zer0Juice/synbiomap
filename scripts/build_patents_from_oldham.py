"""
Build the shared-schema patents.csv from the Oldham synthetic-biology patents.

This replaces the small USPTO-ODP keyword set (data/processed/patents.csv,
~227 rows) with the much larger, curated Oldham & Hall synthetic-biology patent
corpus that we have already geocoded and fetched abstracts for. The three
Oldham intermediate files were produced by:

  scripts/geocode_oldham_patents.py  -> data/processed/oldham_patents_geocoded.csv
  scripts/fetch_patent_abstracts.py  -> data/processed/oldham_patent_abstracts.csv
  scripts/geocode_oldham_patents.py  -> data/processed/oldham_patent_city_weights.csv

WHY OLDHAM:
  Synthetic biology has no dedicated patent classification code, so keyword-only
  searches over-count general biotechnology (Oldham & Hall, 2018,
  doi:10.1101/483826). Oldham & Hall hand-curated a synthetic-biology patent
  landscape; using their family list gives a far more precise corpus than our
  earlier two-layer keyword pull.

UNIT OF ANALYSIS:
  The Oldham data is keyed on the patent *family* (one invention, possibly many
  national filings). We keep the family id as the artifact `id` so it joins
  directly to oldham_patent_city_weights.csv. Each family carries a
  representative granted US number (`rep_patent`) for reference only.

WHAT THIS SCRIPT DOES:
  1. Keep families that are geocoded (have a primary city) AND have an abstract
     record. (Abstracts were only fetched for the geocoded-with-city subset, so
     this is exactly the ~2,900 usable families.)
  2. Build the primary location + aligned all_cities / all_coords lists from the
     per-inventor city weights (every city kept here has valid coordinates, so
     all_cities[i] always pairs with a real all_coords[i] for explode_by_city).
  3. Hand the records to normalize_patents_odp() — the SAME normaliser the ODP
     ingest uses — so the output schema, text field, and carbon-capture
     case-study tagging are identical to the rest of the pipeline.
  4. Write data/processed/patents.csv and a matching patent_city_weights.csv.

The old 227-row patents.csv is git-tracked, so it can be recovered with
`git restore data/processed/patents.csv` if ever needed.

Usage:
    python scripts/build_patents_from_oldham.py
"""

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest.normalize import normalize_patents_odp

PROCESSED = REPO_ROOT / "data" / "processed"
GEOCODED_PATH   = PROCESSED / "oldham_patents_geocoded.csv"
ABSTRACTS_PATH  = PROCESSED / "oldham_patent_abstracts.csv"
WEIGHTS_IN_PATH = PROCESSED / "oldham_patent_city_weights.csv"

PATENTS_OUT_PATH = PROCESSED / "patents.csv"
WEIGHTS_OUT_PATH = PROCESSED / "patent_city_weights.csv"

# Provenance tag recorded on every patent so its source stays traceable.
RETRIEVAL_REASON = "oldham_synbio"


def _primary_geo_name(primary_city: str, state, country: str) -> str:
    """
    Reconstruct the city name as it appears in all_cities / city weights.

    The geocoder keys US cities as "City, ST" (state disambiguates same-named
    towns); non-US cities use the bare city name. The `primary_city` column
    stores only the bare name, so we rebuild the keyed form to match.
    """
    state = "" if pd.isna(state) else str(state).strip()
    if str(country).upper() == "US" and state:
        return f"{primary_city}, {state}"
    return primary_city


def build_records(geo: pd.DataFrame, abss: pd.DataFrame,
                  weights: pd.DataFrame) -> list[dict]:
    """Turn one row per family into the dict shape normalize_patents_odp wants."""
    # Per-family map: keyed city name -> [lat, lon], keeping only valid coords
    # so every entry we emit is plottable and stays index-aligned.
    coord_by_family: dict[str, dict[str, list]] = {}
    valid = weights[weights["lat"].notna() & weights["lon"].notna()]
    for fid, grp in valid.groupby("id"):
        coord_by_family[fid] = {
            row.geo_city: [row.lat, row.lon] for row in grp.itertuples()
        }

    abs_by_id = abss.set_index("id")
    records = []
    for r in geo.itertuples():
        fid = r.id
        abs_row = abs_by_id.loc[fid] if fid in abs_by_id.index else None

        title = (r.title if pd.notna(r.title) else "") or ""
        if not title and abs_row is not None and pd.notna(abs_row["title"]):
            title = abs_row["title"]
        abstract = ""
        if abs_row is not None and pd.notna(abs_row["abstract"]):
            abstract = abs_row["abstract"]

        # Year: Oldham stores it as a float; keep a clean int or None.
        year = int(r.year) if pd.notna(r.year) else None

        # Ordered, coord-aligned city lists: primary first, then the family's
        # other inventor cities in the geocoded order, skipping any without
        # coordinates (so all_cities[i] always pairs with all_coords[i]).
        fam_coords = coord_by_family.get(fid, {})
        primary_name = _primary_geo_name(r.primary_city, r.primary_state,
                                         r.primary_country)
        ordered = [primary_name] if r.primary_city and pd.notna(r.primary_city) else []
        raw_all = str(r.all_cities).split("|") if pd.notna(r.all_cities) else []
        for name in raw_all:
            name = name.strip()
            if name and name not in ordered:
                ordered.append(name)

        all_cities, all_coords = [], []
        for name in ordered:
            if name in fam_coords:
                all_cities.append(name)
                all_coords.append(fam_coords[name])

        records.append({
            "patent_id": fid,
            "title": title,
            "abstract": abstract,
            "year": year,
            "city": r.primary_city if pd.notna(r.primary_city) else "",
            "country": r.primary_country if pd.notna(r.primary_country) else "",
            "lat": r.lat if pd.notna(r.lat) else None,
            "lon": r.lon if pd.notna(r.lon) else None,
            "all_cities": all_cities,
            "all_coords": all_coords,
            "retrieval_reason": RETRIEVAL_REASON,
        })
    return records


def run():
    cfg = load_config()
    carbon_keywords = cfg["corpus"]["carbon_capture_keywords"]

    print("=== Build patents.csv from the Oldham synthetic-biology corpus ===\n")
    geo = pd.read_csv(GEOCODED_PATH)
    abss = pd.read_csv(ABSTRACTS_PATH)
    weights = pd.read_csv(WEIGHTS_IN_PATH)
    print(f"Loaded {len(geo)} geocoded families, {len(abss)} abstract records, "
          f"{len(weights)} city-weight rows.")

    # Keep families that are BOTH geocoded (have a city) and have an abstract
    # record — i.e. the usable, plottable, embeddable subset.
    geo = geo[geo["primary_city"].notna()].copy()
    keep_ids = set(geo["id"]) & set(abss["id"])
    geo = geo[geo["id"].isin(keep_ids)]
    abss = abss[abss["id"].isin(keep_ids)]
    print(f"Keeping {len(keep_ids)} families that are geocoded AND have abstracts.\n")

    records = build_records(geo, abss, weights)
    patents_df = normalize_patents_odp(records, carbon_keywords)

    patents_df.to_csv(PATENTS_OUT_PATH, index=False)

    # Matching city weights for the geographic view: same families, generic
    # column set (drop the Oldham-only rep_patent column), keyed on family id.
    out_weights = (weights[weights["id"].isin(keep_ids)]
                   [["id", "geo_city", "country", "weight", "lat", "lon"]])
    out_weights.to_csv(WEIGHTS_OUT_PATH, index=False)

    # ------------------------------------------------------------------ summary
    n = len(patents_df)
    n_text = patents_df["text"].astype(str).str.strip().str.len().gt(0).sum()
    n_geo  = (patents_df["lat"].notna() & patents_df["lon"].notna()).sum()
    n_abs  = (patents_df["text"].astype(str).str.len() > patents_df["title"].astype(str).str.len() + 2).sum()
    print(f"Saved {n} patents -> {PATENTS_OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Saved {len(out_weights)} (patent,city) rows -> {WEIGHTS_OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"  with text:             {n_text}/{n} ({n_text/n:.0%})")
    print(f"  with real abstract:    {n_abs}/{n} ({n_abs/n:.0%})")
    print(f"  with coordinates:      {n_geo}/{n} ({n_geo/n:.0%})")
    print(f"  carbon-capture tagged: {int(patents_df['case_study_flag'].sum())}")
    print(f"  year range:            {int(patents_df['year'].min())}–{int(patents_df['year'].max())}")
    print("\nTop countries:")
    print(patents_df["country"].value_counts().head(8).to_string())
    print("\nTop cities:")
    print(patents_df["city"].value_counts().head(8).to_string())
    return patents_df


if __name__ == "__main__":
    run()
