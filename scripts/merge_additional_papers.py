"""
merge_additional_papers.py — add biobrick_papers and papers_from_parts to papers.csv.

Both sources contain papers that are related to iGEM parts but were collected
separately from the main OpenAlex keyword search:

  biobrick_papers.csv   — papers that mention specific BioBrick part numbers,
                          fetched from the iGEM Registry's full-text search.
                          Format: pmcid, pmid, doi, title, abstract, year, ...
                          Needs: OpenAlex lookup (for institution IDs + geo),
                                 schema conversion, and case-study tagging.

  papers_from_parts.csv — papers cited by iGEM parts or teams, pulled via
                          the OpenAlex part-citation pipeline.
                          Format: already in the shared schema (same columns
                          as papers.csv), but city/lat/lon are all missing.
                          Needs: geocoding via existing institution_ids.

Pipeline for each source:
  1. biobrick_papers — look up each DOI in OpenAlex to get institution_ids and
                       a canonical OpenAlex ID. Use the biobrick abstract when
                       OpenAlex doesn't have one.
  2. papers_from_parts — already in the right format; geocode the geo columns.
  3. Collect all new institution IDs not yet in the cache.
  4. Batch-fetch institution geo from OpenAlex (same as geocode_papers.py).
  5. Apply geocoding to all new records.
  6. Merge with papers.csv, deduplicating by id (first occurrence wins).
  7. Save updated papers.csv.

The script is restartable: the institution geo cache on disk means re-running it
will skip institutions already fetched and only call the API for new ones.

Usage:
    python scripts/merge_additional_papers.py
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
load_dotenv(REPO_ROOT / ".env")

from src.utils.config import load_config
from src.ingest import normalize
from src.utils.schema import build_text_field

# ── Paths ─────────────────────────────────────────────────────────────────────
PAPERS_PATH         = REPO_ROOT / "data" / "processed" / "papers.csv"
BIOBRICK_PATH       = REPO_ROOT / "data" / "processed" / "biobrick_papers.csv"
PARTS_PAPERS_PATH   = REPO_ROOT / "data" / "processed" / "papers_from_parts.csv"
INST_CACHE_PATH     = REPO_ROOT / "data" / "geo" / "openalex_institution_cache.json"

# ── API constants ──────────────────────────────────────────────────────────────
OA_BASE       = "https://api.openalex.org"
BATCH_SIZE    = 50     # max institution IDs per request (OpenAlex limit)
REQUEST_DELAY = 0.12   # seconds between requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)


# ── Auth ───────────────────────────────────────────────────────────────────────

def _headers() -> dict:
    email = os.getenv("OPENALEX_EMAIL", "")
    return {"User-Agent": f"mailto:{email}"} if email else {}

def _auth_params() -> dict:
    key = os.getenv("OPENALEX_API_KEY", "")
    return {"api_key": key} if key else {}


# ── OpenAlex DOI lookup ────────────────────────────────────────────────────────

def fetch_work_by_doi(doi: str) -> dict | None:
    """
    Fetch a full OpenAlex work object by DOI.

    Returns the raw work dict (same format as the /works endpoint), or None
    if the DOI is not found or the request fails.

    We use this (rather than the keyword search) for biobrick papers because
    we already know which specific papers we want — we just need their
    institution and citation metadata from OpenAlex.
    """
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
    url = f"{OA_BASE}/works/https://doi.org/{doi}"
    try:
        r = requests.get(url, headers=_headers(), params=_auth_params(), timeout=15)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        log.warning(f"DOI fetch failed for {doi}: {e}")
        return None


# ── Institution geocoding (same logic as the deleted geocode_papers.py) ────────

def load_inst_cache() -> dict:
    INST_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if INST_CACHE_PATH.exists():
        with open(INST_CACHE_PATH) as f:
            return json.load(f)
    return {}

def save_inst_cache(cache: dict) -> None:
    with open(INST_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def fetch_institution_geo(inst_ids: list[str], cache: dict) -> int:
    """
    Fetch geo data for institution IDs not yet in the cache.

    Fetches in batches of BATCH_SIZE. Updates the cache dict in place and
    returns the count of newly fetched institutions.

    Each cache entry has the form:
        { "city": "Cambridge", "lat": 42.36, "lon": -71.10 }
    or None if the institution has no geo data.

    Reference: OpenAlex institution object geo sub-object —
      https://docs.openalex.org/api-entities/institutions/institution-object
    """
    to_fetch = [i for i in inst_ids if i not in cache]
    if not to_fetch:
        return 0

    log.info(f"  Fetching geo for {len(to_fetch)} new institutions...")
    n_fetched = 0

    for start in range(0, len(to_fetch), BATCH_SIZE):
        batch = to_fetch[start:start + BATCH_SIZE]
        id_filter = "|".join(batch)
        params = {"filter": f"ids.openalex:{id_filter}", "per-page": BATCH_SIZE,
                  **_auth_params()}
        try:
            r = requests.get(f"{OA_BASE}/institutions", headers=_headers(),
                             params=params, timeout=30)
            r.raise_for_status()
            results = r.json().get("results", [])
        except requests.RequestException as e:
            log.warning(f"Institution batch {start}–{start+BATCH_SIZE} failed: {e}")
            # Mark all IDs in this batch as None so we don't retry endlessly
            for inst_id in batch:
                cache.setdefault(inst_id, None)
            time.sleep(REQUEST_DELAY)
            continue

        found_ids = set()
        for inst in results:
            inst_id = inst.get("id", "")
            geo = inst.get("geo", {}) or {}
            city = geo.get("city") or inst.get("display_name")
            lat  = geo.get("latitude")
            lon  = geo.get("longitude")
            if city and lat is not None and lon is not None:
                cache[inst_id] = {"city": city, "lat": lat, "lon": lon}
            else:
                cache[inst_id] = None
            found_ids.add(inst_id)
            n_fetched += 1

        # Mark IDs not returned by the API as None
        for inst_id in batch:
            if inst_id not in found_ids:
                cache[inst_id] = None

        time.sleep(REQUEST_DELAY)

    return n_fetched


def apply_geo(df: pd.DataFrame, cache: dict) -> pd.DataFrame:
    """
    Fill city, lat, lon, all_cities, all_coords from the institution cache.

    For each row:
      - Reads the semicolon-separated institution_ids column.
      - Looks up each ID in the cache.
      - Primary city/lat/lon = first institution with geo data.
      - all_cities / all_coords = all institutions with geo (JSON arrays).
    """
    df = df.copy()
    cities, lats, lons, all_cities, all_coords = [], [], [], [], []

    for _, row in df.iterrows():
        raw = row.get("institution_ids", "")
        ids = [i.strip() for i in str(raw).split(";") if i.strip()] if pd.notna(raw) and raw else []

        geos = [g for i in ids if (g := cache.get(i))]

        if geos:
            cities.append(geos[0]["city"])
            lats.append(geos[0]["lat"])
            lons.append(geos[0]["lon"])
            seen, ac, coord_pairs = set(), [], []
            for g in geos:
                if g["city"] not in seen:
                    seen.add(g["city"])
                    ac.append(g["city"])
                    coord_pairs.append([g["lat"], g["lon"]])
            all_cities.append(json.dumps(ac))
            all_coords.append(json.dumps(coord_pairs))
        else:
            cities.append(None)
            lats.append(None)
            lons.append(None)
            all_cities.append(None)
            all_coords.append(None)

    df["city"]       = cities
    df["lat"]        = lats
    df["lon"]        = lons
    df["all_cities"] = all_cities
    df["all_coords"] = all_coords
    return df


# ── Process biobrick_papers ────────────────────────────────────────────────────

def process_biobrick_papers(carbon_keywords: list[str]) -> pd.DataFrame:
    """
    Convert biobrick_papers.csv to the shared schema.

    For each paper we try to fetch its full record from OpenAlex via DOI.
    This gives us a canonical OpenAlex ID and the institution_ids needed for
    geocoding. If a paper isn't in OpenAlex, we fall back to a pmcid-based
    ID and skip geocoding (city will remain NaN).

    We always prefer the biobrick abstract over the OpenAlex one when both
    are available — the biobrick version was retrieved from the full-text
    index and tends to be cleaner.
    """
    log.info(f"Loading {BIOBRICK_PATH.name}...")
    bb = pd.read_csv(BIOBRICK_PATH, dtype=str)
    log.info(f"  {len(bb)} biobrick papers to process")

    records = []
    n_openalex = 0
    n_fallback = 0

    for i, row in bb.iterrows():
        doi       = str(row.get("doi", "") or "").strip()
        pmcid     = str(row.get("pmcid", "") or "").strip()
        title     = str(row.get("title", "") or "").strip()
        abstract  = str(row.get("abstract", "") or "").strip()
        year_raw  = row.get("year")
        retrieval = str(row.get("retrieval_reason", "biobrick_fulltext_search") or "")

        try:
            year = int(float(year_raw)) if pd.notna(year_raw) else None
        except (ValueError, TypeError):
            year = None

        openalex_id    = None
        institution_ids = ""
        cited_works    = ""
        country        = None

        if doi and doi != "nan":
            work = fetch_work_by_doi(doi)
            time.sleep(REQUEST_DELAY)

            if work:
                n_openalex += 1
                openalex_id = work.get("id", "")

                # Use OpenAlex year if we don't have one
                if year is None:
                    year = work.get("publication_year")

                # Use OpenAlex abstract if biobrick one is empty
                if not abstract:
                    from src.ingest.openalex import _reconstruct_abstract
                    abstract = _reconstruct_abstract(
                        work.get("abstract_inverted_index") or {}
                    )

                # Collect institution IDs for geocoding
                seen_inst: set[str] = set()
                inst_list: list[str] = []
                for authorship in work.get("authorships", []):
                    for inst in authorship.get("institutions", []):
                        inst_id = inst.get("id", "")
                        if inst_id and inst_id not in seen_inst:
                            inst_list.append(inst_id)
                            seen_inst.add(inst_id)
                institution_ids = ";".join(inst_list)

                # Country from first institution
                for authorship in work.get("authorships", []):
                    for inst in authorship.get("institutions", []):
                        cc = inst.get("country_code")
                        if cc:
                            country = cc
                            break
                    if country:
                        break

                # Citation links
                raw_refs = work.get("referenced_works", []) or []
                cited_works = ";".join(r.split("/")[-1] for r in raw_refs if r)
            else:
                n_fallback += 1
        else:
            n_fallback += 1

        # Build the canonical ID
        if openalex_id:
            record_id = openalex_id
        elif pmcid and pmcid != "nan":
            record_id = f"pmc_{pmcid}"
        else:
            import hashlib
            record_id = "bb_" + hashlib.md5(title.encode()).hexdigest()[:8]

        text = build_text_field(title, abstract)
        case_study = normalize._tag_case_study(text, carbon_keywords)

        records.append({
            "id":                    record_id,
            "type":                  "paper",
            "title":                 title,
            "text":                  text,
            "year":                  year,
            "city":                  None,
            "country":               country,
            "lat":                   None,
            "lon":                   None,
            "all_cities":            None,
            "all_coords":            None,
            "theme_primary":         None,
            "theme_secondary":       None,
            "case_study_flag":       case_study["case_study_flag"],
            "case_study_confidence": case_study["case_study_confidence"],
            "retrieval_reason":      retrieval,
            "cited_works":           cited_works,
            "institution_ids":       institution_ids,
        })

        if (i + 1) % 50 == 0:
            log.info(f"  {i + 1}/{len(bb)} processed "
                     f"(OpenAlex: {n_openalex}, fallback: {n_fallback})")

    log.info(f"  Done. OpenAlex found: {n_openalex}, fallback IDs: {n_fallback}")
    return pd.DataFrame(records)


# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    print("=== Merge Additional Papers into papers.csv ===\n")

    cfg = load_config()
    carbon_keywords = cfg["corpus"]["carbon_capture_keywords"]

    # ── 1. Load base papers.csv ────────────────────────────────────────────────
    log.info(f"Loading {PAPERS_PATH.name}...")
    papers = pd.read_csv(PAPERS_PATH, dtype={"institution_ids": str, "cited_works": str})
    log.info(f"  {len(papers)} existing papers")
    existing_ids = set(papers["id"].dropna().astype(str))

    # ── 2. Load and geocode papers_from_parts ──────────────────────────────────
    log.info(f"\nLoading {PARTS_PAPERS_PATH.name}...")
    pfp = pd.read_csv(PARTS_PAPERS_PATH, dtype={"institution_ids": str, "cited_works": str})
    log.info(f"  {len(pfp)} papers_from_parts rows")

    # ── 3. Process biobrick_papers (API calls) ─────────────────────────────────
    log.info("\nProcessing biobrick papers via OpenAlex DOI lookup...")
    bb_df = process_biobrick_papers(carbon_keywords)
    log.info(f"  {len(bb_df)} biobrick paper records built")

    # ── 4. Collect all institution IDs that need geocoding ─────────────────────
    inst_cache = load_inst_cache()
    log.info(f"\nLoaded institution cache: {len(inst_cache)} entries")

    all_inst_ids: set[str] = set()
    for df_src in [pfp, bb_df]:
        for raw in df_src["institution_ids"].dropna():
            for inst_id in str(raw).split(";"):
                inst_id = inst_id.strip()
                if inst_id:
                    all_inst_ids.add(inst_id)

    log.info(f"Unique institution IDs needed: {len(all_inst_ids)}")
    n_new = fetch_institution_geo(list(all_inst_ids), inst_cache)
    if n_new:
        save_inst_cache(inst_cache)
        log.info(f"  Saved updated institution cache ({len(inst_cache)} total entries)")

    # ── 5. Apply geocoding to both new sources ─────────────────────────────────
    log.info("\nApplying geocoding to papers_from_parts...")
    pfp = apply_geo(pfp, inst_cache)
    n_geocoded_pfp = pfp["city"].notna().sum()
    log.info(f"  {n_geocoded_pfp}/{len(pfp)} geocoded")

    log.info("Applying geocoding to biobrick papers...")
    bb_df = apply_geo(bb_df, inst_cache)
    n_geocoded_bb = bb_df["city"].notna().sum()
    log.info(f"  {n_geocoded_bb}/{len(bb_df)} geocoded")

    # ── 6. Merge — deduplicating by id, existing papers take priority ──────────
    log.info("\nMerging all sources...")

    # Ensure column alignment
    extra_cols = ["cited_works", "institution_ids"]
    for col in extra_cols:
        if col not in papers.columns:
            papers[col] = ""

    col_order = list(papers.columns)  # preserve existing column order

    # Align new sources to match column order, adding any missing cols as NaN
    def align(df: pd.DataFrame) -> pd.DataFrame:
        for col in col_order:
            if col not in df.columns:
                df[col] = None
        return df[col_order]

    pfp_aligned = align(pfp.copy())
    bb_aligned  = align(bb_df.copy())

    new_pfp = pfp_aligned[~pfp_aligned["id"].astype(str).isin(existing_ids)]
    new_bb  = bb_aligned[~bb_aligned["id"].astype(str).isin(existing_ids)]

    log.info(f"  papers.csv:          {len(papers):>5} papers (existing)")
    log.info(f"  papers_from_parts:   {len(pfp_aligned):>5} rows → {len(new_pfp):>5} new")
    log.info(f"  biobrick_papers:     {len(bb_aligned):>5} rows → {len(new_bb):>5} new")

    merged = pd.concat([papers, new_pfp, new_bb], ignore_index=True)
    log.info(f"  Total after merge:   {len(merged):>5} papers")

    # ── 7. Carbon capture summary ──────────────────────────────────────────────
    n_cc = merged["case_study_flag"].sum()
    log.info(f"\nCarbon capture tagged: {n_cc} / {len(merged)}")

    # ── 8. Save ────────────────────────────────────────────────────────────────
    merged.to_csv(PAPERS_PATH, index=False)
    log.info(f"\nSaved updated papers.csv → {PAPERS_PATH.relative_to(REPO_ROOT)}")
    log.info("Next: re-run scripts/04_embed.py and scripts/05_cluster.py")


if __name__ == "__main__":
    run()
