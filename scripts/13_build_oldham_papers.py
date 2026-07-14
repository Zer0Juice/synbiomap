"""
Step 13 — Convert Paul Oldham's synthetic-biology literature corpus into our
shared paper schema, fetching abstracts and city geo-data from OpenAlex.

Why this script exists
----------------------
We want to re-run the tripartite city-level analysis on a *different* paper set:
instead of our own keyword+citation OpenAlex corpus (papers.csv), we use the
fixed literature list from

    Oldham, P. & Hall, S. (2018). "Synthetic Biology: Mapping the Patent
    Landscape." bioRxiv 483826 / OSF 73fmu.

Oldham's list is just DOIs, titles and years (data/literature.csv in his
repository). It has no abstracts and no geography, so it is not directly usable
in our pipeline. This script:

  1. Reads Oldham's literature.csv and collects the DOIs.
  2. Batch-resolves each DOI against OpenAlex to recover the abstract, author
     institutions, publication year, and citation links.
  3. Batch-fetches the full institution objects to get city / lat / lon
     (works responses only carry dehydrated institutions with no geo — same
     two-phase trick as scripts/archive/geocode_papers.py). The institution
     cache is shared with the main paper pipeline, so most lookups are hits.
  4. Normalises everything to our shared schema and tags the carbon-capture
     case study, exactly like normal papers.

Coverage note
-------------
OpenAlex abstract coverage is patchy for older papers. We KEEP every Oldham
paper that resolves in OpenAlex rather than dropping abstract-less ones (the
point is to reproduce *his* corpus, not re-filter it). Papers with an abstract
get retrieval_reason "oldham"; title-only papers get "oldham_title_only" so
they can be filtered later if desired. build_text_field falls back to the title
so title-only papers still carry embeddable text.

Output
------
  data/processed/papers_oldham.csv   (same schema as papers.csv)

Next
----
  python scripts/08_build_tripartite_corpus.py \
      --papers data/processed/papers_oldham.csv \
      --out    data/processed/artifacts_tripartite_oldham.csv

Usage
-----
  python scripts/13_build_oldham_papers.py
  python scripts/13_build_oldham_papers.py --limit 200   # quick test slice
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import openalex, normalize

# Oldham's repository lives in a sibling Downloads folder (an extra working dir).
OLDHAM_LIT = Path("/Users/zakh/Downloads/oldham-patents/data/literature.csv")

PROCESSED    = REPO_ROOT / "data" / "processed"
OUT_PATH     = PROCESSED / "papers_oldham.csv"
INST_CACHE   = REPO_ROOT / "data" / "geo" / "openalex_institution_cache.json"

OPENALEX_WORKS        = "https://api.openalex.org/works"
OPENALEX_INSTITUTIONS = "https://api.openalex.org/institutions"

# Fields we pull from each work. Selecting keeps the payload small and fast.
WORK_SELECT = (
    "id,doi,title,publication_year,"
    "abstract_inverted_index,authorships,referenced_works"
)

DOI_BATCH  = 50    # DOIs per /works request (OR-joined in one filter)
INST_BATCH = 50    # institution IDs per /institutions request
DELAY      = 0.12  # polite-pool pacing (~10 req/s)


# ---------------------------------------------------------------------------
# OpenAlex auth (email -> polite pool, api_key -> higher limits). Both optional.
# ---------------------------------------------------------------------------

def _auth() -> tuple[dict, dict]:
    import os
    email = os.getenv("OPENALEX_EMAIL", "")
    key   = os.getenv("OPENALEX_API_KEY", "")
    headers = {"User-Agent": f"mailto:{email}"} if email else {}
    params  = {"api_key": key} if key else {}
    return headers, params


def _norm_doi(doi: str) -> str:
    """Lowercase bare DOI, stripped of any URL / 'doi:' prefix."""
    if not doi:
        return ""
    d = str(doi).strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d.strip()


# ---------------------------------------------------------------------------
# Phase 1 — resolve DOIs to OpenAlex works
# ---------------------------------------------------------------------------

def fetch_works_by_dois(dois: list[str]) -> tuple[dict[str, dict], list[str]]:
    """
    Resolve a list of bare DOIs against OpenAlex.

    Returns
    -------
    by_doi  : {normalised_doi: raw work dict} for every DOI that resolved
    missing : DOIs that OpenAlex did not return (no such work, or no DOI match)
    """
    headers, auth = _auth()
    by_doi: dict[str, dict] = {}

    n_batches = (len(dois) + DOI_BATCH - 1) // DOI_BATCH
    for b, start in enumerate(range(0, len(dois), DOI_BATCH), 1):
        chunk = dois[start:start + DOI_BATCH]
        # OpenAlex's doi filter wants the full https://doi.org/... form.
        filt = "doi:" + "|".join("https://doi.org/" + d for d in chunk)
        params = {"filter": filt, "per-page": DOI_BATCH,
                  "select": WORK_SELECT, **auth}
        try:
            time.sleep(DELAY)
            r = requests.get(OPENALEX_WORKS, params=params, headers=headers, timeout=30)
            r.raise_for_status()
            results = r.json().get("results", [])
        except requests.RequestException as e:
            print(f"  WARNING: batch {b}/{n_batches} failed: {e}", flush=True)
            continue

        for work in results:
            d = _norm_doi(work.get("doi", ""))
            if d:
                by_doi[d] = work

        if b % 10 == 0 or b == n_batches:
            print(f"  works: batch {b}/{n_batches}  resolved {len(by_doi)}/{start + len(chunk)}",
                  flush=True)

    missing = [d for d in dois if d not in by_doi]
    return by_doi, missing


# ---------------------------------------------------------------------------
# Phase 2 — institution geo (city/lat/lon), cached and shared with main pipeline
# ---------------------------------------------------------------------------

def load_inst_cache() -> dict:
    if INST_CACHE.exists():
        with open(INST_CACHE) as f:
            return json.load(f)
    return {}


def fetch_institution_geo(inst_ids: list[str], cache: dict) -> int:
    """Fill `cache` with {inst_id: {city,lat,lon} or None}. Returns #fetched."""
    missing = [i for i in inst_ids if i not in cache]
    if not missing:
        return 0
    headers, auth = _auth()
    print(f"  fetching {len(missing)} new institution records "
          f"({len(missing) // INST_BATCH + 1} requests)…", flush=True)

    for start in range(0, len(missing), INST_BATCH):
        chunk = missing[start:start + INST_BATCH]
        bare = [c.split("/")[-1] for c in chunk]
        params = {"filter": f"ids.openalex:{'|'.join(bare)}",
                  "per-page": INST_BATCH, **auth}
        try:
            time.sleep(DELAY)
            r = requests.get(OPENALEX_INSTITUTIONS, params=params, headers=headers, timeout=30)
            r.raise_for_status()
            returned = {i.get("id"): i for i in r.json().get("results", []) if i.get("id")}
        except requests.RequestException as e:
            print(f"  WARNING: institution batch @{start} failed: {e}", flush=True)
            for cid in chunk:
                cache[cid] = None
            continue

        for cid in chunk:
            inst = returned.get(cid)
            geo = (inst or {}).get("geo") or {}
            city, lat, lon = geo.get("city"), geo.get("latitude"), geo.get("longitude")
            if inst and city and lat is not None and lon is not None:
                cache[cid] = {"city": city, "lat": float(lat), "lon": float(lon)}
            else:
                cache[cid] = None

    with open(INST_CACHE, "w") as f:
        json.dump(cache, f, indent=2)
    return len(missing)


def apply_geo(df: pd.DataFrame, cache: dict) -> pd.DataFrame:
    """Fill primary city/lat/lon and all_cities/all_coords from the cache."""
    df = df.copy()
    cities, lats, lons, all_c, all_co = [], [], [], [], []
    for raw in df["institution_ids"].fillna(""):
        ids = [i.strip() for i in str(raw).split(";") if i.strip()]
        geos = [cache[i] for i in ids if cache.get(i)]
        if geos:
            cities.append(geos[0]["city"]); lats.append(geos[0]["lat"]); lons.append(geos[0]["lon"])
            seen, names, coords = set(), [], []
            for g in geos:
                if g["city"] not in seen:
                    seen.add(g["city"]); names.append(g["city"]); coords.append([g["lat"], g["lon"]])
            all_c.append(json.dumps(names)); all_co.append(json.dumps(coords))
        else:
            cities.append(None); lats.append(None); lons.append(None)
            all_c.append(None); all_co.append(None)
    df["city"], df["lat"], df["lon"] = cities, lats, lons
    df["all_cities"], df["all_coords"] = all_c, all_co
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(limit: int | None):
    cfg = load_config()  # also loads .env into os.environ for OpenAlex auth
    carbon_keywords = cfg["corpus"]["carbon_capture_keywords"]

    print("=== Step 13: Convert Oldham literature corpus to our schema ===\n")
    if not OLDHAM_LIT.exists():
        print(f"ERROR: Oldham literature file not found at {OLDHAM_LIT}")
        return

    # utf-8-sig strips the BOM; skipinitialspace trims the leading spaces in
    # Oldham's header (" doi", " title", …).
    lit = pd.read_csv(OLDHAM_LIT, encoding="utf-8-sig", skipinitialspace=True,
                      dtype=str).fillna("")
    lit.columns = [c.strip() for c in lit.columns]
    print(f"Oldham literature rows: {len(lit)}")

    # Keep Oldham's own title/year as a fallback for the few works where
    # OpenAlex lacks them, keyed by normalised DOI.
    lit["doi_norm"] = lit["doi"].map(_norm_doi)
    lit = lit[lit["doi_norm"] != ""].copy()
    fallback = (lit.drop_duplicates("doi_norm")
                   .set_index("doi_norm")[["title", "publication_year"]]
                   .to_dict("index"))

    dois = sorted(lit["doi_norm"].unique().tolist())
    if limit:
        dois = dois[:limit]
    print(f"Unique DOIs to resolve: {len(dois)}"
          f"{f' (limited to {limit})' if limit else ''}\n")

    # --- Phase 1: DOIs -> works ---
    print("--- Resolving DOIs against OpenAlex ---")
    by_doi, missing = fetch_works_by_dois(dois)
    print(f"Resolved {len(by_doi)} / {len(dois)} DOIs "
          f"({len(missing)} not found in OpenAlex)\n")

    # --- Build raw records in the shape normalize_papers expects ---
    raw_records = []
    n_abstract = 0
    for d in dois:
        work = by_doi.get(d)
        if work is None:
            continue
        fields = openalex.extract_fields(work)
        has_abstract = bool(fields.get("abstract", "").strip())
        n_abstract += int(has_abstract)
        # Backfill title/year from Oldham's list when OpenAlex is blank.
        fb = fallback.get(d, {})
        if not fields.get("title"):
            fields["title"] = fb.get("title", "")
        if not fields.get("year"):
            yr = fb.get("publication_year", "")
            fields["year"] = int(yr) if str(yr).isdigit() else None
        fields["retrieval_reason"] = "oldham" if has_abstract else "oldham_title_only"
        raw_records.append(fields)

    print(f"Records built: {len(raw_records)}  "
          f"(with abstract: {n_abstract}, title-only: {len(raw_records) - n_abstract})\n")

    # --- Normalise to shared schema (city still empty here) ---
    papers = normalize.normalize_papers(raw_records, carbon_keywords)
    print(f"Carbon-capture tagged: {int(papers['case_study_flag'].sum())} papers")

    # --- Phase 2: institution geo ---
    print("\n--- Geocoding via OpenAlex institutions ---")
    all_ids: set[str] = set()
    for raw in papers["institution_ids"].dropna():
        for i in str(raw).split(";"):
            if i.strip():
                all_ids.add(i.strip())
    cache = load_inst_cache()
    have = sum(1 for i in all_ids if i in cache)
    print(f"Unique institutions: {len(all_ids)}  ({have} cached, {len(all_ids) - have} to fetch)")
    fetch_institution_geo(list(all_ids), cache)
    papers = apply_geo(papers, cache)

    n_city = int(papers["city"].notna().sum())
    print(f"\nPapers with a city: {n_city} / {len(papers)}")
    print("Top cities:")
    print(papers["city"].value_counts().head(10).to_string())

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    papers.to_csv(OUT_PATH, index=False)
    print(f"\nSaved {len(papers)} papers -> {OUT_PATH.relative_to(REPO_ROOT)}")
    if papers["year"].notna().any():
        print(f"Year range: {int(papers['year'].min())} — {int(papers['year'].max())}")
    print("\nNext: build the tripartite corpus with")
    print("  python scripts/08_build_tripartite_corpus.py \\")
    print("      --papers data/processed/papers_oldham.csv \\")
    print("      --out    data/processed/artifacts_tripartite_oldham.csv")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Convert Oldham's literature corpus to our paper schema.")
    p.add_argument("--limit", type=int, default=None,
                   help="Only process the first N DOIs (for a quick test).")
    run(p.parse_args().limit)
