"""
Step 3g — Match iGEM-citing papers to patents via Marx PPP, then fetch patent metadata.

Background
----------
Matt Marx's Patent-Paper Pairs (PPP) dataset links OpenAlex Work IDs to USPTO
patent numbers using textual similarity of citing strings in patent documents.
Reference: Marx & Fuegi (2020), "Reliance on Science in Patenting"
           Journal of Economics & Management Strategy, 29(1): 72-93.
           Data: https://doi.org/10.7910/DVN/6RFQ7F

We use PPP to find which USPTO patents are linked to papers that explicitly
mention iGEM BioBrick parts. This gives us a documented knowledge path:
  iGEM part → paper mentioning it → patent citing that paper

Pipeline
--------
  1. Load part_paper_edges_mentions.csv (papers mentioning iGEM parts) → unique DOIs
  2. Resolve DOIs → OpenAlex Work IDs via OpenAlex API (bare W... IDs)
  3. Join Work IDs against PPP dataset → matched (paper, patent) pairs
  4. Collect unique USPTO patent numbers from matched pairs
  5. Fetch patent metadata from PatentsView API (USPTO open data)
  6. Normalize to shared schema and save:
       data/processed/patents.csv
       data/processed/paper_patent_ppp_links.csv

Outputs
-------
  data/processed/patents.csv
      One row per unique patent. Shared schema (id, type, title, text, year,
      city, country, lat, lon, …). id = full USPTO number e.g. "US-10000036".

  data/processed/paper_patent_ppp_links.csv
      Edge table: openalex_id, patent_id, ppp_score, days_diff (days from
      paper publication to patent grant; negative = paper before patent).

Usage
-----
  python scripts/03g_match_ppp_fetch_patents.py
  python scripts/03g_match_ppp_fetch_patents.py --dry-run   # diagnostic only
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.utils.schema import build_text_field, REQUIRED_COLUMNS

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

MENTIONS_CSV  = REPO_ROOT / "data" / "processed" / "part_paper_edges_mentions.csv"
PPP_CSV       = REPO_ROOT / "data" / "raw" / "ppp" / "patent_paper_pairs.csv"
PATENTS_OUT   = REPO_ROOT / "data" / "processed" / "patents.csv"
LINKS_OUT     = REPO_ROOT / "data" / "processed" / "paper_patent_ppp_links.csv"

OPENALEX_BASE    = "https://api.openalex.org"
PATENTSVIEW_BASE = "https://search.patentsview.org/api/v1/patent/"

# ---------------------------------------------------------------------------
# Step 1 — resolve DOIs → OpenAlex Work IDs
# ---------------------------------------------------------------------------

def resolve_dois_to_openalex(dois: list[str], batch_size: int = 50) -> dict[str, str]:
    """
    Query OpenAlex to convert DOIs → bare OpenAlex Work IDs (e.g. "W2025049717").

    OpenAlex supports filtering by multiple DOIs in one request using pipe-
    separated values. We batch to stay within URL length limits.

    Returns dict: lowercase DOI → bare Work ID ("W...").
    DOIs not found in OpenAlex are omitted.
    """
    from dotenv import load_dotenv
    import os
    load_dotenv(REPO_ROOT / ".env")
    email = os.getenv("OPENALEX_EMAIL", "")
    params_base = {"mailto": email} if email else {}

    doi_to_id: dict[str, str] = {}
    total = len(dois)

    for i in range(0, total, batch_size):
        chunk = dois[i : i + batch_size]
        doi_filter = "|".join(f"https://doi.org/{d}" for d in chunk)
        params = {
            "filter": f"doi:{doi_filter}",
            "per-page": batch_size,
            "select": "id,doi",
            **params_base,
        }
        try:
            resp = requests.get(
                f"{OPENALEX_BASE}/works",
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            for work in resp.json().get("results", []):
                raw_doi = (work.get("doi") or "").lower()
                bare_doi = (
                    raw_doi
                    .replace("https://doi.org/", "")
                    .replace("http://doi.org/", "")
                    .strip()
                )
                # OpenAlex ID is a URL like https://openalex.org/W123; take the tail
                oa_url = work.get("id", "")
                bare_id = oa_url.split("/")[-1]  # e.g. "W2025049717"
                if bare_doi and bare_id:
                    doi_to_id[bare_doi] = bare_id
        except requests.RequestException as e:
            logger.error(f"OpenAlex batch {i}–{i+batch_size} failed: {e}")
            time.sleep(5)
            continue

        batch_num = i // batch_size + 1
        total_batches = (total - 1) // batch_size + 1
        logger.info(
            f"  OpenAlex batch {batch_num}/{total_batches}: "
            f"{len(doi_to_id)} resolved so far"
        )
        time.sleep(0.15)  # polite pool: ~6 req/s is fine

    return doi_to_id


# ---------------------------------------------------------------------------
# Step 2 — load PPP and filter to matched Work IDs
# ---------------------------------------------------------------------------

def match_ppp(
    work_ids: set[str],
    ppp_path: Path,
) -> pd.DataFrame:
    """
    Load Marx's PPP CSV and return only rows whose paperid is in work_ids.

    PPP columns: paperid, patent, ppp_score, daysdiffcont, all_patents_for_the_same_paper
    We keep: paperid, patent, ppp_score, daysdiffcont (rename to days_diff).

    PPP is ~548k rows, so we stream it in chunks to avoid loading the whole
    file into memory.
    """
    chunks = []
    for chunk in pd.read_csv(
        ppp_path,
        usecols=["paperid", "patent", "ppp_score", "daysdiffcont"],
        chunksize=50_000,
    ):
        matched = chunk[chunk["paperid"].isin(work_ids)]
        if len(matched):
            chunks.append(matched)

    if not chunks:
        return pd.DataFrame(columns=["paperid", "patent", "ppp_score", "daysdiffcont"])

    return pd.concat(chunks, ignore_index=True)


# ---------------------------------------------------------------------------
# Step 3 — fetch patent metadata from PatentsView
# ---------------------------------------------------------------------------

# Fields to request from PatentsView v1 API.
# PatentsView documentation: https://search.patentsview.org/docs/docs/Search%20API/FieldList
_PTV_FIELDS = [
    "patent_id",
    "patent_title",
    "patent_abstract_text",
    "patent_date",
    "assignees.assignee_city",
    "assignees.assignee_country",
    "assignees.assignee_latitude",
    "assignees.assignee_longitude",
]


def fetch_patents_patentsview(
    patent_numbers: list[str],
    batch_size: int = 25,
) -> list[dict]:
    """
    Fetch patent metadata from PatentsView API v1 for a list of USPTO patent
    numbers (e.g. ["10000036", "10000103"]).

    We use batched _or queries because PatentsView does not support a native
    multi-value _in operator. Batch size 25 keeps query URLs short enough.

    Returns a list of raw PatentsView patent dicts.
    """
    results = []
    total = len(patent_numbers)

    for i in range(0, total, batch_size):
        chunk = patent_numbers[i : i + batch_size]

        # Build _or query over patent_id equality checks
        or_clauses = [{"_eq": {"patent_id": pid}} for pid in chunk]
        query = {"_or": or_clauses} if len(or_clauses) > 1 else or_clauses[0]

        body = {
            "q": query,
            "f": _PTV_FIELDS,
            "o": {"size": batch_size},
        }

        try:
            resp = requests.post(
                PATENTSVIEW_BASE,
                json=body,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            batch_results = data.get("patents", [])
            results.extend(batch_results)
        except requests.RequestException as e:
            logger.error(f"PatentsView batch {i}–{i+batch_size} failed: {e}")
            time.sleep(5)
            continue

        batch_num = i // batch_size + 1
        total_batches = (total - 1) // batch_size + 1
        logger.info(
            f"  PatentsView batch {batch_num}/{total_batches}: "
            f"{len(results)} fetched so far"
        )
        time.sleep(0.2)  # be polite

    return results


# ---------------------------------------------------------------------------
# Step 4 — normalize PatentsView records to shared schema
# ---------------------------------------------------------------------------

def normalize_patents(
    raw: list[dict],
    carbon_keywords: list[str],
    retrieval_reason: str = "ppp_igem_paper_link",
) -> pd.DataFrame:
    """
    Convert raw PatentsView records to the shared artifact schema.

    Geography: PatentsView returns per-assignee city/country/lat/lon. We use
    the first assignee as the primary location (most patents have one assignee).
    All assignee cities are stored in all_cities / all_coords for the
    multi-city analysis pipeline.

    Case study tagging: keyword match on title + abstract, same approach as
    normalize_papers() in src/ingest/normalize.py.
    """
    keywords_lower = [k.lower() for k in carbon_keywords]

    rows = []
    for p in raw:
        patent_id = p.get("patent_id", "")
        if not patent_id:
            continue

        title    = (p.get("patent_title") or "").strip()
        abstract = (p.get("patent_abstract_text") or "").strip()
        text     = build_text_field(title, abstract)

        # Year from grant date "YYYY-MM-DD"
        date_str = p.get("patent_date") or ""
        year = int(date_str[:4]) if len(date_str) >= 4 else None

        # Geography — iterate over assignees
        assignees = p.get("assignees") or []
        cities, coords = [], []
        for a in assignees:
            city = (a.get("assignee_city") or "").strip() or None
            country = (a.get("assignee_country") or "").strip() or None
            try:
                lat = float(a["assignee_latitude"])
                lon = float(a["assignee_longitude"])
            except (TypeError, ValueError, KeyError):
                lat, lon = None, None

            if city and city not in cities:
                cities.append(city)
                coords.append([lat, lon])

        primary_city    = cities[0] if cities else None
        primary_country = (assignees[0].get("assignee_country") or "").strip() or None if assignees else None
        primary_lat     = coords[0][0] if coords else None
        primary_lon     = coords[0][1] if coords else None
        all_cities_str  = json.dumps(cities) if cities else None
        all_coords_str  = json.dumps(coords) if coords else None

        # Carbon-capture case-study tagging
        # Methodology: keyword match on lowercased title + abstract.
        # confidence = fraction of keywords present (0–1), same as normalize.py.
        text_lower = text.lower()
        hits = [kw for kw in keywords_lower if kw in text_lower]
        case_study_flag       = len(hits) > 0
        case_study_confidence = round(len(hits) / len(keywords_lower), 4) if keywords_lower else 0.0

        rows.append({
            "id":                   f"US-{patent_id}",
            "type":                 "patent",
            "title":                title,
            "text":                 text,
            "year":                 year,
            "city":                 primary_city,
            "country":              primary_country,
            "lat":                  primary_lat,
            "lon":                  primary_lon,
            "all_cities":           all_cities_str,
            "all_coords":           all_coords_str,
            "theme_primary":        None,
            "theme_secondary":      None,
            "case_study_flag":      case_study_flag,
            "case_study_confidence": case_study_confidence,
            "retrieval_reason":     retrieval_reason,
        })

    df = pd.DataFrame(rows)
    # Ensure all required columns are present
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[REQUIRED_COLUMNS].drop_duplicates(subset=["id"])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(dry_run: bool = False):
    print("=== Step 3g: Match PPP → Fetch Patents ===\n")

    cfg = load_config()
    carbon_keywords = cfg["corpus"]["carbon_capture_keywords"]

    # ── Step 1: load mentions, collect unique DOIs ──────────────────────────
    print("Step 1: Loading part_paper_edges_mentions.csv…")
    mentions = pd.read_csv(MENTIONS_CSV)
    dois = mentions["doi"].dropna().str.strip().str.lower().unique().tolist()
    print(f"  {len(mentions)} mention edges, {len(dois)} unique DOIs\n")

    # ── Step 2: resolve DOIs → OpenAlex Work IDs ────────────────────────────
    print(f"Step 2: Resolving {len(dois)} DOIs via OpenAlex API…")
    doi_to_id = resolve_dois_to_openalex(dois)
    resolved = len(doi_to_id)
    print(
        f"  Resolved {resolved} / {len(dois)} DOIs "
        f"({resolved / len(dois) * 100:.1f}%)\n"
    )

    if not doi_to_id:
        print("ERROR: No DOIs resolved. Check your internet connection or OpenAlex API.")
        return

    work_ids = set(doi_to_id.values())  # bare W... IDs

    # ── Step 3: match against PPP ────────────────────────────────────────────
    print(f"Step 3: Matching {len(work_ids)} Work IDs against PPP dataset…")
    print(f"  (Loading {PPP_CSV.name} in 50k-row chunks, this takes a moment…)")
    ppp_matched = match_ppp(work_ids, PPP_CSV)
    print(f"  Matched {len(ppp_matched)} PPP rows")
    print(f"  Unique papers with a patent link: {ppp_matched['paperid'].nunique()}")
    print(f"  Unique patents: {ppp_matched['patent'].nunique()}\n")

    if dry_run:
        print("── Dry-run diagnostics ──")
        print(ppp_matched.head(10).to_string(index=False))
        print(f"\nWould fetch {ppp_matched['patent'].nunique()} patents from PatentsView.")
        print("Exiting (--dry-run). Remove the flag to run the full pipeline.")
        return

    if ppp_matched.empty:
        print("No matches found in PPP. Exiting.")
        return

    # ── Step 4: build and save edge table ────────────────────────────────────
    # Enrich edges with the DOI so downstream users can trace paper → part
    id_to_doi = {v: k for k, v in doi_to_id.items()}
    ppp_matched = ppp_matched.copy()
    ppp_matched["doi"] = ppp_matched["paperid"].map(id_to_doi)
    ppp_matched = ppp_matched.rename(columns={
        "paperid":     "openalex_id",
        "patent":      "patent_id",    # keeps the full US-... form
        "daysdiffcont": "days_diff",   # negative = paper before patent
    })

    # Add the part_name column by joining back to mentions via DOI
    doi_to_parts = (
        mentions[["doi", "part_name"]]
        .assign(doi=lambda df: df["doi"].str.strip().str.lower())
        .drop_duplicates()
        .groupby("doi")["part_name"]
        .apply(list)
        .reset_index()
        .rename(columns={"part_name": "part_names"})
    )
    doi_to_parts["part_names"] = doi_to_parts["part_names"].apply(json.dumps)
    ppp_matched = ppp_matched.merge(doi_to_parts, on="doi", how="left")

    edge_cols = ["openalex_id", "doi", "part_names", "patent_id", "ppp_score", "days_diff"]
    ppp_matched[edge_cols].to_csv(LINKS_OUT, index=False)
    print(f"Saved edge table: {LINKS_OUT.relative_to(REPO_ROOT)}")
    print(f"  ({len(ppp_matched)} edges)\n")

    # ── Step 5: fetch patent metadata from PatentsView ───────────────────────
    # Strip "US-" prefix for PatentsView (it uses bare numbers like "10000036")
    raw_patent_ids = (
        ppp_matched["patent_id"]
        .str.replace("US-", "", regex=False)
        .unique()
        .tolist()
    )
    total_patents = len(raw_patent_ids)
    print(f"Step 5: Fetching {total_patents} patents from PatentsView API…")
    print(f"  ({(total_patents + 24) // 25} batches of up to 25 patents each)\n")

    raw_patents = fetch_patents_patentsview(raw_patent_ids)
    print(f"\n  Fetched {len(raw_patents)} patent records from PatentsView\n")

    if not raw_patents:
        print("WARNING: PatentsView returned no records. patents.csv will not be saved.")
        return

    # ── Step 6: normalize and save ──────────────────────────────────────────
    print("Step 6: Normalizing to shared schema…")
    patents_df = normalize_patents(raw_patents, carbon_keywords)
    print(f"  {len(patents_df)} unique patents")
    print(f"  With city data: {patents_df['city'].notna().sum()}")
    print(f"  Carbon capture tagged: {patents_df['case_study_flag'].sum()}")
    print(f"  Year range: {patents_df['year'].min()}–{patents_df['year'].max()}")

    patents_df.to_csv(PATENTS_OUT, index=False)
    print(f"\nSaved: {PATENTS_OUT.relative_to(REPO_ROOT)}  ({len(patents_df)} patents)")
    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Match iGEM-citing papers to patents via PPP, then fetch patent metadata."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve DOIs and match PPP but skip PatentsView fetch. Shows diagnostics.",
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run)
