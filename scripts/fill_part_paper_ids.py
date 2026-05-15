"""
Fill the paper_id column in part_source_papers.csv by looking up each DOI
in the OpenAlex API.

OpenAlex returns a work record at:
    GET https://api.openalex.org/works/doi:{doi}

The `id` field of that record is the canonical OpenAlex work ID
(e.g. "https://openalex.org/W2023545713"), which we write into paper_id.

The script is restartable: rows that already have a paper_id are skipped.
Progress is saved every 50 requests so you don't lose work if it's interrupted.

Usage:
    python scripts/fill_part_paper_ids.py
"""

import os
import sys
import time
import logging
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

CSV_PATH    = REPO_ROOT / "data" / "processed" / "part_source_papers.csv"
OA_BASE     = "https://api.openalex.org"
DELAY       = 0.12   # seconds between requests (~8 req/s, well within the polite limit)
SAVE_EVERY  = 50     # save CSV after this many successful lookups
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

email = os.getenv("OPENALEX_EMAIL", "")
headers = {"User-Agent": f"mailto:{email}"} if email else {}
if email:
    log.info(f"Using polite pool (mailto:{email})")
else:
    log.warning("OPENALEX_EMAIL not set — requests will be slower (anonymous pool)")


def lookup_doi(doi: str) -> str | None:
    """Return the OpenAlex work ID for a DOI, or None if not found."""
    url = f"{OA_BASE}/works/doi:{doi}"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json().get("id")   # e.g. "https://openalex.org/W2023545713"
        if r.status_code == 404:
            return None                 # DOI not in OpenAlex
        log.warning(f"HTTP {r.status_code} for {doi}")
        return None
    except requests.RequestException as e:
        log.warning(f"Request error for {doi}: {e}")
        return None


def main():
    df = pd.read_csv(CSV_PATH, dtype={"paper_id": object})
    log.info(f"Loaded {len(df)} rows, {df['paper_id'].notna().sum()} already filled")

    unique_dois = df.loc[df["paper_id"].isna(), "doi"].unique().tolist()
    log.info(f"Unique DOIs to look up: {len(unique_dois)}")

    if not unique_dois:
        log.info("Nothing to do — all paper_ids already filled.")
        return

    # doi → openalex_id cache built from this run
    cache: dict[str, str | None] = {}
    n_found = 0
    n_missing = 0
    since_save = 0

    for i, doi in enumerate(unique_dois, 1):
        openalex_id = lookup_doi(doi)
        cache[doi] = openalex_id

        if openalex_id:
            n_found += 1
            since_save += 1
        else:
            n_missing += 1

        if i % 25 == 0 or i == len(unique_dois):
            log.info(
                f"  {i}/{len(unique_dois)}  found={n_found}  not_in_openalex={n_missing}"
            )

        # Save progress periodically
        if since_save >= SAVE_EVERY or i == len(unique_dois):
            mask = df["doi"].isin([d for d, v in cache.items() if v])
            df.loc[mask, "paper_id"] = df.loc[mask, "doi"].map(cache)
            df.to_csv(CSV_PATH, index=False)
            since_save = 0

        time.sleep(DELAY)

    log.info(f"\nDone. Found: {n_found}/{len(unique_dois)} DOIs in OpenAlex.")
    log.info(f"Saved to {CSV_PATH}")


if __name__ == "__main__":
    main()
