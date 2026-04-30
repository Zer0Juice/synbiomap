"""
geocode_papers.py — fill city, lat, lon for academic papers using OpenAlex
institution geo data.

Why a separate script?
  OpenAlex works responses include *dehydrated* institution objects that
  contain id, display_name, and country_code — but NOT the geo sub-object
  (city, latitude, longitude). Full geo data is only available by fetching
  each institution individually via the /institutions endpoint. This script
  does that in batches so we don't re-fetch all 9,000+ works.

Pipeline:
  1. Read papers.csv (produced by 01_ingest_papers.py).
     Each paper has an institution_ids column: a semicolon-separated list
     of OpenAlex institution IDs collected during ingestion.
  2. Collect all unique institution IDs across the corpus.
  3. Batch-fetch full institution objects from the OpenAlex /institutions
     endpoint (up to 50 IDs per request). Cache results so re-runs are fast.
  4. For each paper:
       - primary city/lat/lon  → first institution that has geo data
       - all_cities / all_coords → all institutions that have geo data
         (JSON arrays, for multi-city analysis and the geographic map)
  5. Overwrite papers.csv with the filled-in geo columns.

After running this script, re-run:
  python scripts/05_cluster.py
  python scripts/06_visualize.py

Reference:
  OpenAlex institution object schema (includes full geo):
  https://docs.openalex.org/api-entities/institutions/institution-object
"""

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PAPERS_PATH = REPO_ROOT / "data" / "processed" / "papers.csv"
CACHE_PATH  = REPO_ROOT / "data" / "geo" / "openalex_institution_cache.json"

OPENALEX_INSTITUTIONS = "https://api.openalex.org/institutions"
BATCH_SIZE    = 50    # max IDs per request (OpenAlex limit)
REQUEST_DELAY = 0.12  # seconds between requests (polite pool: ~10 req/s)
SAVE_EVERY    = 500   # flush cache to disk every N newly fetched institutions


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def load_cache() -> dict:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


# ---------------------------------------------------------------------------
# OpenAlex auth helpers
# ---------------------------------------------------------------------------

def _auth_params() -> dict:
    """Return api_key param if set in environment or .env file."""
    api_key = os.getenv("OPENALEX_API_KEY", "")
    if not api_key:
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("OPENALEX_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    return {"api_key": api_key} if api_key else {}


def _auth_headers() -> dict:
    email = os.getenv("OPENALEX_EMAIL", "")
    if not email:
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("OPENALEX_EMAIL="):
                    email = line.split("=", 1)[1].strip()
                    break
    return {"User-Agent": f"mailto:{email}"} if email else {}


# ---------------------------------------------------------------------------
# Batch-fetch institution geo data from OpenAlex
# ---------------------------------------------------------------------------

def fetch_institution_geo(inst_ids: list[str], cache: dict) -> int:
    """
    Fetch full institution objects for a list of OpenAlex institution IDs.

    Stores results in `cache` as:
      {"https://openalex.org/I123": {"city": "...", "lat": ..., "lon": ...}}
    or None if the institution has no geo data.

    Returns the number of newly fetched institutions.
    """
    # Only fetch IDs not already in cache
    missing = [i for i in inst_ids if i not in cache]
    if not missing:
        return 0

    print(f"  Fetching {len(missing)} institution records from OpenAlex "
          f"({len(missing) // BATCH_SIZE + 1} requests)…", flush=True)

    auth_params  = _auth_params()
    auth_headers = _auth_headers()
    fetched = 0

    for batch_start in range(0, len(missing), BATCH_SIZE):
        chunk = missing[batch_start : batch_start + BATCH_SIZE]

        # Strip URL prefix to bare IDs for the filter param
        bare_ids = [c.split("/")[-1] for c in chunk]
        id_filter = "|".join(bare_ids)

        try:
            time.sleep(REQUEST_DELAY)
            r = requests.get(
                OPENALEX_INSTITUTIONS,
                params={"filter": f"ids.openalex:{id_filter}",
                        "per-page": BATCH_SIZE,
                        **auth_params},
                headers=auth_headers,
                timeout=30,
            )
            r.raise_for_status()
            results = r.json().get("results", [])
        except Exception as e:
            print(f"  WARNING: batch {batch_start}–{batch_start+BATCH_SIZE} failed: {e}",
                  flush=True)
            # Mark as None so we don't retry this batch in subsequent runs
            for inst_id in chunk:
                cache[inst_id] = None
            continue

        # Index returned institutions by their full URL ID
        returned = {inst.get("id"): inst for inst in results if inst.get("id")}

        for inst_id in chunk:
            inst = returned.get(inst_id)
            if inst is None:
                cache[inst_id] = None
                continue
            geo = inst.get("geo") or {}
            city = geo.get("city") or None
            lat  = geo.get("latitude")
            lon  = geo.get("longitude")
            if city and lat is not None and lon is not None:
                cache[inst_id] = {"city": city, "lat": float(lat), "lon": float(lon)}
            else:
                cache[inst_id] = None

        fetched += len(chunk)
        if fetched % SAVE_EVERY == 0 or batch_start + BATCH_SIZE >= len(missing):
            save_cache(cache)
            print(f"  {min(batch_start + BATCH_SIZE, len(missing))}/{len(missing)} done",
                  flush=True)

    return fetched


# ---------------------------------------------------------------------------
# Apply geo data back to papers
# ---------------------------------------------------------------------------

def apply_geo_to_papers(df: pd.DataFrame, cache: dict) -> pd.DataFrame:
    """
    Fill city, lat, lon, all_cities, and all_coords in df using the cache.

    For each paper:
      - institution_ids contains a semicolon-separated list of OpenAlex
        institution IDs collected during ingestion.
      - We look up each institution in the cache and collect all that have
        city/lat/lon data.
      - The first institution with geo data becomes the primary city/lat/lon.
      - All institutions with geo data populate all_cities / all_coords.
    """
    df = df.copy()

    cities_list   = []
    lats          = []
    lons          = []
    all_cities_list = []
    all_coords_list = []

    for _, row in df.iterrows():
        raw_ids = row.get("institution_ids", "")
        inst_ids = [i.strip() for i in str(raw_ids).split(";") if i.strip()] if raw_ids else []

        geos = []
        for inst_id in inst_ids:
            geo = cache.get(inst_id)
            if geo:
                geos.append(geo)

        if geos:
            # Primary = first institution with geo data
            cities_list.append(geos[0]["city"])
            lats.append(geos[0]["lat"])
            lons.append(geos[0]["lon"])
            # all_cities / all_coords = all institutions with geo (unique cities)
            seen = set()
            ac, coords = [], []
            for g in geos:
                if g["city"] not in seen:
                    seen.add(g["city"])
                    ac.append(g["city"])
                    coords.append([g["lat"], g["lon"]])
            all_cities_list.append(json.dumps(ac))
            all_coords_list.append(json.dumps(coords))
        else:
            cities_list.append(None)
            lats.append(None)
            lons.append(None)
            all_cities_list.append(None)
            all_coords_list.append(None)

    df["city"]       = cities_list
    df["lat"]        = lats
    df["lon"]        = lons
    df["all_cities"] = all_cities_list
    df["all_coords"] = all_coords_list

    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    print("=== Geocode Papers (via OpenAlex institution geo) ===\n")

    # --- 1. Load papers ---
    if not PAPERS_PATH.exists():
        print("ERROR: papers.csv not found. Run 01_ingest_papers.py first.")
        return

    df = pd.read_csv(PAPERS_PATH, dtype={"institution_ids": str})
    print(f"Loaded {len(df)} papers from {PAPERS_PATH.name}")

    if "institution_ids" not in df.columns:
        print("ERROR: institution_ids column missing. Re-run 01_ingest_papers.py first.")
        return

    # --- 2. Collect all unique institution IDs ---
    all_inst_ids: set[str] = set()
    for raw in df["institution_ids"].dropna():
        for inst_id in str(raw).split(";"):
            inst_id = inst_id.strip()
            if inst_id:
                all_inst_ids.add(inst_id)

    print(f"Unique institution IDs across corpus: {len(all_inst_ids)}")

    # --- 3. Fetch institution geo (with cache) ---
    cache = load_cache()
    cached = sum(1 for i in all_inst_ids if i in cache)
    print(f"Cache: {cached} already cached, {len(all_inst_ids) - cached} to fetch\n")

    newly_fetched = fetch_institution_geo(list(all_inst_ids), cache)
    if newly_fetched:
        save_cache(cache)
        print(f"Saved {len(cache)} institutions to cache.\n")

    # --- 4. Apply geo to papers ---
    df = apply_geo_to_papers(df, cache)

    n_city = df["city"].notna().sum()
    n_lat  = df["lat"].notna().sum()
    print(f"\nResults:")
    print(f"  Papers with city:    {n_city} / {len(df)}")
    print(f"  Papers with lat/lon: {n_lat} / {len(df)}")

    # Show top cities as a sanity check
    print("\nTop 10 cities:")
    print(df["city"].value_counts().head(10).to_string())

    # --- 5. Save ---
    df.to_csv(PAPERS_PATH, index=False)
    print(f"\nSaved updated papers.csv to {PAPERS_PATH.relative_to(REPO_ROOT)}")
    print("Next: run scripts/05_cluster.py and scripts/06_visualize.py")


if __name__ == "__main__":
    run()
