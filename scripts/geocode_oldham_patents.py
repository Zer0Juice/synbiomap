"""
geocode_oldham_patents.py — put Oldham & Hall's synthetic-biology patents on a map.

Oldham & Hall (2018), "Synthetic Biology: Mapping the Patent Landscape"
(doi:10.1101/483826), released a curated dataset of ~7,640 synthetic-biology
patent *families* (data/core.csv in their repo). That dataset records patent
numbers, inventors' names, applicants and IPC codes — but NO inventor addresses,
so it cannot be mapped geographically as-is.

This script fills that gap. For each family we:

  1. Parse the US granted patent numbers from the family's member list.
  2. Look those numbers up in the USPTO Open Data Portal (ODP, api.uspto.gov),
     which DOES return parsed inventor addresses (city / state / country).
  3. Assign the family a location from its inventors.

Why inventor addresses (not applicant/assignee)?
  Inventor addresses reflect where the research was actually done; assignee
  addresses tend to be corporate headquarters (Breschi & Lissoni, 2001,
  doi:10.1093/icc/10.4.975).

Why fractional counting (not first-inventor)?
  The first-listed inventor is only a weak proxy for the lead — the USPTO does
  not require inventors to be ordered by contribution. Assigning the whole
  patent to the first inventor's city biases the geography of multi-city
  collaborations. We therefore capture EVERY inventor and split each patent's
  weight equally across the cities of its located inventors (e.g. 2 inventors in
  Boston + 1 in San Francisco -> Boston 2/3, San Francisco 1/3). This is the
  standard in regional patent statistics (OECD REGPAT) and keeps city totals
  additive (the weights of any patent sum to 1). We still record a single
  `primary_city` (first located inventor) for one-dot-per-patent map placement.

Coverage limits (reported at the end of the run):
  - ODP only covers US applications filed on/after 2001-01-01, so pre-2001
    families and families with no US member cannot be geocoded this way.
  - Inventor addresses are residence/correspondence addresses — a proxy for the
    place of work, not the lab itself.

Outputs (data/processed/):
  oldham_patents_geocoded.csv      one row per family (wide): primary location +
                                   distinct inventor cities + counts.
  oldham_patent_city_weights.csv   one row per (family, city): fractional weight
                                   + lat/lon — the analysis-ready table for any
                                   city-level aggregation.

Caches (so re-runs are cheap and restartable):
  data/raw/oldham/odp_lookups.json   patentNumber -> ODP metadata (or null if
                                     the number was queried but not found).
  data/geo/geocoding_cache.json      shared city -> lat/lon cache (also used by
                                     the iGEM/paper geocoding).

Usage:
    python scripts/geocode_oldham_patents.py
Requires USPTO_ODP_KEY in .env (https://data.uspto.gov/apis/getting-started).
"""

from __future__ import annotations
import sys
import re
import csv
import json
import zipfile
import logging
from pathlib import Path
from collections import Counter

import pandas as pd
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load USPTO_ODP_KEY (and other secrets) from .env into the environment.
load_dotenv(REPO_ROOT / ".env")

from src.ingest import odp
from src.geo.geocode import geocode_dataframe

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths. The Oldham repo is a sibling clone in ~/Downloads; fall back to the
# unzipped copy if present. Adjust OLDHAM_DIR if you cloned it elsewhere.
# ---------------------------------------------------------------------------
OLDHAM_DIR  = Path("/Users/zakh/Downloads/oldham-patents")
OLDHAM_ZIP  = OLDHAM_DIR / "data" / "core.csv.zip"
OLDHAM_CSV  = OLDHAM_DIR / "data" / "core.csv"  # used if already unzipped

ODP_CACHE   = REPO_ROOT / "data" / "raw" / "oldham" / "odp_lookups.json"
GEO_CACHE   = REPO_ROOT / "data" / "geo" / "geocoding_cache.json"
OUT_WIDE    = REPO_ROOT / "data" / "processed" / "oldham_patents_geocoded.csv"
OUT_LONG    = REPO_ROOT / "data" / "processed" / "oldham_patent_city_weights.csv"

# US granted utility patents: US + 7-8 digits + kind code (A, B1, B2).
# This deliberately excludes pre-grant publications (11-digit US20xx... numbers)
# and design/plant/reissue patents (D/PP/RE prefixes), which the ODP
# patentNumber lookup does not serve the same way.
RE_US_GRANT = re.compile(r"\bUS(\d{7,8})[AB][12]?\b")


# ---------------------------------------------------------------------------
# 1. Load Oldham families and parse their US grant numbers.
# ---------------------------------------------------------------------------
def _open_core_csv():
    """Yield rows from Oldham's core.csv, whether zipped or already extracted."""
    if OLDHAM_CSV.exists():
        f = open(OLDHAM_CSV, encoding="utf-8-sig", newline="")
        return f, csv.DictReader(f)
    if OLDHAM_ZIP.exists():
        zf = zipfile.ZipFile(OLDHAM_ZIP)
        raw = zf.read("core.csv").decode("utf-8-sig").splitlines()
        return zf, csv.DictReader(raw)
    raise FileNotFoundError(
        f"Could not find Oldham core.csv at {OLDHAM_CSV} or {OLDHAM_ZIP}. "
        "Clone https://github.com/poldham/synbio (or set OLDHAM_DIR)."
    )


def load_families() -> list[dict]:
    """
    Return one record per Oldham family with its parsed US grant numbers.

    Each record: {key, title, applicant, ipc, us_grants: [bare numbers]}.
    """
    handle, reader = _open_core_csv()
    # Header fields are space-padded in the source file (", priority_...").
    reader.fieldnames = [(fn or "").strip() for fn in reader.fieldnames]

    families: list[dict] = []
    for row in reader:
        row = { (k or "").strip(): v for k, v in row.items() }
        # Combine the fields that can carry US patent numbers, then parse.
        blob = " ; ".join(filter(None, [
            row.get("inpadoc_family_members"),
            row.get("inpadoc_first_family_member"),
            row.get("application_number_long"),
            row.get("priority_number_long"),
        ]))
        grants = sorted(set(RE_US_GRANT.findall(blob)))
        families.append({
            "key":       row.get("Key", "").strip(),
            "title":     (row.get("title_original", "") or "").split(" | ")[0].strip(),
            "applicant": (row.get("applicant_cleaned", "") or "").strip(),
            "ipc":       (row.get("ipc_subclass", "") or "").strip(),
            "us_grants": grants,
        })

    if hasattr(handle, "close"):
        handle.close()
    return families


# ---------------------------------------------------------------------------
# 2. Resolve US grant numbers -> ODP metadata, with an on-disk cache.
# ---------------------------------------------------------------------------
def resolve_numbers(numbers: list[str]) -> dict[str, dict | None]:
    """
    Return {number: ODP metadata or None}. Cached so re-runs only fetch the
    numbers not seen before (None is cached too, so we don't re-query misses).
    """
    ODP_CACHE.parent.mkdir(parents=True, exist_ok=True)
    cache: dict[str, dict | None] = {}
    if ODP_CACHE.exists():
        cache = json.loads(ODP_CACHE.read_text())

    todo = [n for n in numbers if n not in cache]
    logger.info(f"{len(numbers)} unique US grant numbers; "
                f"{len(cache)} cached, {len(todo)} to fetch from ODP.")

    # Fetch in chunks and save the cache after each chunk, so an interrupted
    # run keeps its progress and can be restarted from where it stopped.
    CHUNK = 200
    for i in range(0, len(todo), CHUNK):
        chunk = todo[i:i + CHUNK]
        resolved = odp.lookup_patents_by_number(chunk, batch_size=20)
        for n in chunk:
            cache[n] = resolved.get(n)          # None if ODP had no match
        ODP_CACHE.write_text(json.dumps(cache))
        logger.info(f"ODP cache saved: {min(i + CHUNK, len(todo))}/{len(todo)} "
                    f"new numbers fetched.")

    return cache


# ---------------------------------------------------------------------------
# 3. Assign each family a location from its inventors.
# ---------------------------------------------------------------------------
def _geo_key(city: str, state: str, country: str) -> tuple[str, str]:
    """
    Build (geo_city, geo_country) for the geocoder. US cities carry the state
    so the query is "City, ST" + "US"; others use the bare city + country.
    """
    country = (country or "").upper()
    if country == "US" and state:
        return f"{city}, {state}", country
    return city, country


def build_tables(families: list[dict], cache: dict[str, dict | None]):
    """
    Return (wide_rows, long_rows).

    wide_rows: one per family — primary location, distinct cities, counts.
    long_rows: one per (family, distinct city) — fractional weight (pre-geocode).
    """
    wide_rows, long_rows = [], []

    for fam in families:
        # Among the family's resolvable US grants, use the earliest-granted one
        # as the representative record (closest to the original invention).
        resolved = [(n, cache.get(n)) for n in fam["us_grants"] if cache.get(n)]
        resolved.sort(key=lambda nm: nm[1].get("grantDate") or "9999")

        primary_city = primary_state = primary_country = ""
        rep_number = rep_grant_date = ""
        n_inv_total = n_inv_located = 0
        city_counts: Counter = Counter()         # (geo_city, geo_country) -> n inventors
        located_seen = False

        if resolved:
            rep_number, meta = resolved[0]
            rep_grant_date = meta.get("grantDate") or ""
            locs = odp.extract_all_inventor_locations(meta)
            n_inv_total = len(locs)
            for loc in locs:
                if not loc["city"]:
                    continue
                n_inv_located += 1
                gcity, gcountry = _geo_key(loc["city"], loc["state"], loc["country"])
                city_counts[(gcity, gcountry)] += 1
                if not located_seen:                 # first located inventor = primary
                    primary_city, primary_state, primary_country = (
                        loc["city"], loc["state"], loc["country"].upper())
                    located_seen = True

        # Fractional weights: each patent contributes a total weight of 1,
        # split across the distinct cities of its located inventors.
        for (gcity, gcountry), n in city_counts.items():
            long_rows.append({
                "id":       fam["key"],
                "geo_city": gcity,
                "country":  gcountry,
                "weight":   n / n_inv_located,       # sums to 1 across the family
                "rep_patent": f"US{rep_number}",
            })

        wide_rows.append({
            "id":               fam["key"],
            "type":             "patent",
            "title":            fam["title"],
            "applicant":        fam["applicant"],
            "ipc_subclass":     fam["ipc"],
            "rep_patent":       f"US{rep_number}" if rep_number else "",
            "year":             int(rep_grant_date[:4]) if rep_grant_date[:4].isdigit() else None,
            "primary_city":     primary_city,
            "primary_state":    primary_state,
            "primary_country":  primary_country,
            "n_us_grants":      len(fam["us_grants"]),
            "n_inventors":      n_inv_total,
            "n_inventors_located": n_inv_located,
            "n_distinct_cities":   len(city_counts),
            "all_cities":       " | ".join(sorted(c for c, _ in city_counts)),
        })

    return wide_rows, long_rows


# ---------------------------------------------------------------------------
# 4. Geocode distinct cities and merge coordinates back.
# ---------------------------------------------------------------------------
def add_coordinates(wide_df: pd.DataFrame, long_df: pd.DataFrame):
    """Geocode every distinct (geo_city, country) once and join lat/lon back."""
    if long_df.empty:
        wide_df["lat"] = None
        wide_df["lon"] = None
        return wide_df, long_df

    distinct = long_df[["geo_city", "country"]].drop_duplicates().reset_index(drop=True)
    logger.info(f"Geocoding {len(distinct)} distinct inventor cities "
                f"(cached in {GEO_CACHE.name})...")
    distinct = geocode_dataframe(
        distinct, cache_file=GEO_CACHE,
        city_col="geo_city", country_col="country",
        provider="nominatim",
    )

    long_df = long_df.merge(distinct, on=["geo_city", "country"], how="left")

    # Primary lat/lon for the wide table = coordinates of the primary city.
    prim = wide_df.copy()
    prim["geo_city"], prim["country"] = zip(*[
        _geo_key(c, s, k) for c, s, k in zip(
            prim["primary_city"], prim["primary_state"], prim["primary_country"])
    ])
    coords = distinct.set_index(["geo_city", "country"])[["lat", "lon"]]
    merged = prim.merge(coords, left_on=["geo_city", "country"],
                        right_index=True, how="left").drop(columns=["geo_city", "country"])
    return merged, long_df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run():
    print("=== Geocoding the Oldham synthetic-biology patent landscape ===\n")

    families = load_families()
    n_families = len(families)
    with_grants = sum(1 for f in families if f["us_grants"])
    all_numbers = sorted({n for f in families for n in f["us_grants"]})
    print(f"Families loaded:                 {n_families}")
    print(f"  with >=1 US granted patent:    {with_grants} ({with_grants/n_families:.0%})")
    print(f"  unique US grant numbers:       {len(all_numbers)}\n")

    cache = resolve_numbers(all_numbers)
    n_resolved = sum(1 for n in all_numbers if cache.get(n))
    print(f"\nUS grant numbers resolved by ODP: {n_resolved}/{len(all_numbers)} "
          f"({n_resolved/max(len(all_numbers),1):.0%}) "
          f"(unresolved are mostly pre-2001 filings, outside ODP coverage)\n")

    wide_rows, long_rows = build_tables(families, cache)
    wide_df = pd.DataFrame(wide_rows)
    long_df = pd.DataFrame(long_rows)

    located = (wide_df["n_inventors_located"] > 0).sum()
    print(f"Families with an inventor location: {located}/{n_families} "
          f"({located/n_families:.0%})")

    wide_df, long_df = add_coordinates(wide_df, long_df)

    OUT_WIDE.parent.mkdir(parents=True, exist_ok=True)
    wide_df.to_csv(OUT_WIDE, index=False)
    long_df.to_csv(OUT_LONG, index=False)
    print(f"\nSaved {len(wide_df)} families  -> {OUT_WIDE.relative_to(REPO_ROOT)}")
    print(f"Saved {len(long_df)} (family,city) rows -> {OUT_LONG.relative_to(REPO_ROOT)}")

    # --- Quick sanity readout ---------------------------------------------
    geo_ok = wide_df["lat"].notna().sum()
    print(f"\nFamilies with coordinates:        {geo_ok}/{n_families} "
          f"({geo_ok/n_families:.0%})")

    if not long_df.empty:
        us_share = (long_df["country"] == "US").mean()
        print(f"Inventor-city rows in the US:     {us_share:.0%} "
              f"(rest are foreign inventors on US patents)")
        print("\nTop 12 inventor cities (fractional patent weight):")
        top = (long_df.groupby(["geo_city", "country"])["weight"]
               .sum().sort_values(ascending=False).head(12))
        for (city, country), w in top.items():
            print(f"  {w:6.1f}  {city}, {country}")

    return wide_df, long_df


if __name__ == "__main__":
    run()
