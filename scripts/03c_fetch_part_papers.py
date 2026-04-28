"""
Step 3c — Fetch papers cited by iGEM parts via OpenAlex.

Many iGEM parts in the Registry include a `source` field citing the paper
that describes the biological sequence or device the part encodes. This script:

  1. Reads parts_cache.jsonl (produced by step 3b Phase 1 — no team lookup needed)
  2. Extracts all DOIs from the `source` and `description` fields
  3. Resolves those DOIs to full paper records via the OpenAlex API
  4. Normalises and saves the results as papers_from_parts.csv

Why this is useful:
  Parts cite papers because they are adaptations of published sequences or
  devices. This gives us a documented knowledge link between the academic
  literature and the student parts corpus — stronger than keyword overlap.

  These papers are collected separately from the keyword-based corpus in
  papers.csv so that their origin is traceable. Downstream steps can merge
  them, analyse them independently, or use the part→paper links as edges.

Outputs
-------
  data/processed/papers_from_parts.csv
      One row per unique paper resolved from a part DOI.
      Same column schema as papers.csv (openalex_id, title, abstract, year,
      doi, country, institution_ids, cited_works, retrieval_reason, …).

  data/processed/part_paper_edges.csv
      Columns: part_name, doi, openalex_id
      Links each part to the paper(s) its source field cites.
      openalex_id is blank if OpenAlex did not find the DOI.

Usage:
    python scripts/03c_fetch_part_papers.py

    # Test with a small sample first:
    python scripts/03c_fetch_part_papers.py --max-dois 100
"""

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest.openalex import extract_fields, _get_auth
from src.ingest.normalize import normalize_papers

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

OPENALEX_BASE = "https://api.openalex.org"

RAW_DIR       = REPO_ROOT / "data" / "raw" / "parts"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

PARTS_CACHE      = RAW_DIR / "parts_cache.jsonl"
PAPERS_OUT       = PROCESSED_DIR / "papers_from_parts.csv"
PART_EDGES_OUT   = PROCESSED_DIR / "part_paper_edges.csv"

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[^\s,;\]\)\">]+")


# ---------------------------------------------------------------------------
# Step 1: extract DOIs from the parts cache
# ---------------------------------------------------------------------------

def extract_dois_from_parts(parts_cache: Path) -> dict[str, list[str]]:
    """
    Read parts_cache.jsonl and extract DOIs from each part's source and
    description fields.

    Returns a dict: part_name → list of DOIs (normalised, no URL prefix).
    Parts with no DOIs are omitted.
    """
    part_dois: dict[str, list[str]] = {}

    with open(parts_cache) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            part = json.loads(line)
            name = part.get("name", "")
            text = (part.get("source") or "") + " " + (part.get("description") or "")
            raw = DOI_PATTERN.findall(text)
            cleaned = list({re.sub(r"[.,;)\]>\"']+$", "", d) for d in raw})
            if cleaned:
                part_dois[name] = cleaned

    return part_dois


# ---------------------------------------------------------------------------
# Step 2: resolve DOIs via OpenAlex in batches
# ---------------------------------------------------------------------------

def fetch_works_by_dois(
    dois: list[str],
    retrieval_reason: str = "igem_part_citation",
    batch_size: int = 50,
) -> list[dict]:
    """
    Fetch full OpenAlex work records for a list of DOIs.

    OpenAlex supports filtering by multiple DOIs in one request using
    `filter=doi:10.xxx/yyy|10.zzz/www`. We batch up to 50 DOIs per request
    to stay within URL length limits.

    Only papers with abstracts are returned — we need text to embed.

    Parameters
    ----------
    dois          : list of bare DOI strings (e.g. "10.1021/acschembio.5b00753")
    batch_size    : DOIs per API request (keep ≤ 50)

    Returns a list of raw OpenAlex work dicts with retrieval_reason injected.
    """
    headers, auth_params = _get_auth()
    results = []
    total = len(dois)

    for i in range(0, total, batch_size):
        chunk = dois[i : i + batch_size]
        # OpenAlex DOI filter expects full URLs joined by |
        doi_filter = "|".join(f"https://doi.org/{d}" for d in chunk)

        params = {
            "filter": f"doi:{doi_filter},has_abstract:true",
            "per-page": batch_size,
            **auth_params,
        }

        try:
            resp = requests.get(
                f"{OPENALEX_BASE}/works",
                params=params,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"OpenAlex batch {i}–{i+batch_size} failed: {e}")
            time.sleep(5)
            continue

        batch_results = data.get("results", [])
        for work in batch_results:
            work["retrieval_reason"] = retrieval_reason
        results.extend(batch_results)

        logger.info(
            f"Batch {i//batch_size + 1}/{(total-1)//batch_size + 1}: "
            f"resolved {len(batch_results)}/{len(chunk)} DOIs "
            f"(total so far: {len(results)})"
        )
        time.sleep(0.15)   # OpenAlex polite pool: ~6 req/sec is fine

    return results


# ---------------------------------------------------------------------------
# Step 3: build the part → paper edge table
# ---------------------------------------------------------------------------

def build_edges(
    part_dois: dict[str, list[str]],
    doi_to_openalex_id: dict[str, str],
) -> pd.DataFrame:
    """
    Build the part_paper_edges table.

    For every (part, doi) pair, record the resolved OpenAlex ID.
    Rows where OpenAlex didn't find the DOI still appear with a blank
    openalex_id so we can see coverage gaps.
    """
    rows = []
    for part_name, dois in part_dois.items():
        for doi in dois:
            rows.append({
                "part_name":   part_name,
                "doi":         doi,
                "openalex_id": doi_to_openalex_id.get(doi.lower(), ""),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(max_dois: int | None = None):
    print("=== Step 3c: Fetch papers cited by iGEM parts ===\n")

    if not PARTS_CACHE.exists():
        print("ERROR: parts_cache.jsonl not found.")
        print("Run 'python scripts/03b_fetch_parts.py --skip-authors' first to fetch all parts.")
        return

    cfg = load_config()
    carbon_keywords = cfg["corpus"]["carbon_capture_keywords"]

    # --- Step 1: extract DOIs ---
    print("Step 1: Extracting DOIs from parts cache…")
    part_dois = extract_dois_from_parts(PARTS_CACHE)

    all_dois = list({doi for dois in part_dois.values() for doi in dois})
    print(f"  {len(part_dois)} parts have at least one DOI")
    print(f"  {len(all_dois)} unique DOIs total")

    if max_dois:
        all_dois = all_dois[:max_dois]
        print(f"  Limiting to {max_dois} DOIs (--max-dois flag)\n")
    else:
        print()

    # --- Step 2: resolve via OpenAlex ---
    print(f"Step 2: Resolving {len(all_dois)} DOIs via OpenAlex…")
    print(f"  ({(len(all_dois) + 49) // 50} API requests at 50 DOIs each)\n")

    works = fetch_works_by_dois(all_dois)

    # Build a DOI → OpenAlex ID lookup from the resolved works.
    # OpenAlex returns the DOI as a full URL (https://doi.org/10.xxx/yyy).
    doi_to_openalex_id: dict[str, str] = {}
    for work in works:
        raw_doi = (work.get("doi") or "").lower()
        bare = raw_doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        oa_id = work.get("id", "").split("/")[-1]  # e.g. "W2741809807"
        if bare and oa_id:
            doi_to_openalex_id[bare] = oa_id

    resolved = len(doi_to_openalex_id)
    print(f"\nResolved {resolved} / {len(all_dois)} DOIs ({resolved/len(all_dois)*100:.1f}%)")

    # --- Step 3: normalise papers ---
    print("\nStep 3: Normalising paper records…")
    raw_records = [extract_fields(w) for w in works]
    for rec in raw_records:
        rec["retrieval_reason"] = "igem_part_citation"

    papers_df = normalize_papers(
        raw_records=raw_records,
        carbon_keywords=carbon_keywords,
    )
    print(f"  {len(papers_df)} papers normalised")
    print(f"  Carbon capture tagged: {papers_df['case_study_flag'].sum()}")

    # --- Step 4: build edges ---
    print("\nStep 4: Building part → paper edges…")
    edges_df = build_edges(part_dois, doi_to_openalex_id)
    matched = edges_df["openalex_id"].notna() & (edges_df["openalex_id"] != "")
    print(f"  {len(edges_df)} edges ({matched.sum()} with resolved OpenAlex ID)")

    # --- Save ---
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    papers_df.to_csv(PAPERS_OUT, index=False)
    edges_df.to_csv(PART_EDGES_OUT, index=False)

    print(f"\nSaved:")
    print(f"  {PAPERS_OUT.relative_to(REPO_ROOT)}  ({len(papers_df)} papers)")
    print(f"  {PART_EDGES_OUT.relative_to(REPO_ROOT)}  ({len(edges_df)} edges)")
    print("\nRun scripts/geocode_papers.py next to fill in city/lat/lon.")
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch papers cited by iGEM parts via OpenAlex"
    )
    parser.add_argument(
        "--max-dois",
        type=int,
        default=None,
        help="Limit number of DOIs resolved (useful for testing)",
    )
    args = parser.parse_args()
    run(max_dois=args.max_dois)
