"""
Step 3e — Find papers that mention iGEM BioBrick IDs in full text.

Why this matters
----------------
The DOI-based approach in step 3c finds papers *cited by* parts in the iGEM
Registry. But many papers *use* or *characterise* parts without the registry
entry ever being updated with that citation. This script finds that broader
set by searching for the literal BioBrick ID strings (e.g. "BBa_K1989010")
in publication full text via PubMed Central.

How it works
------------
We use the NCBI eutils API to search PubMed Central (PMC), which indexes the
full body text of open-access biomedical papers. The query is simply "BBa_"
which PMC's full-text index matches against the BioBrick ID prefix. This
returns ~12,000 candidate papers in a single search.

We then:
  1. Fetch the full XML for each paper in batches.
  2. Regex-scan the XML for all BBa_ part IDs (e.g. "BBa_K1989010").
  3. Keep only papers where at least one BBa_ ID appears in the text.
  4. Match found IDs against our known parts to build a part→paper edge table.

Why not search per part ID?
  We have 89,000 parts. Issuing one query per part would take hours and
  exceed NCBI's rate limits. The single-query + post-filter approach is
  orders of magnitude faster.

Batching note
-------------
NCBI eutils supports "history server" batching: one esearch stores results
server-side (you get a WebEnv token), then efetch pulls them in pages using
retstart/retmax. This means we make one search request + ~65 fetch requests
for all 12,000+ records — very efficient.

Rate limits
-----------
Without an API key: 3 requests/second.
With an NCBI API key (free, see https://www.ncbi.nlm.nih.gov/account/):
10 requests/second. Set NCBI_API_KEY in your .env file to use it.

Outputs
-------
  data/processed/biobrick_papers.csv
      One row per paper that mentions ≥1 BioBrick ID.
      Columns: pmcid, pmid, doi, title, abstract, year, journal,
               authors, matched_parts, retrieval_reason

  data/processed/part_paper_edges_mentions.csv
      Long-format edge table linking parts to papers by mention.
      Columns: part_name, pmcid, doi, year

Usage
-----
  # Full run
  python scripts/03e_fetch_biobrick_papers.py

  # Test with first 500 records only
  python scripts/03e_fetch_biobrick_papers.py --max-records 500

  # Ignore existing cache and restart
  python scripts/03e_fetch_biobrick_papers.py --no-resume
"""

import argparse
import json
import logging
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load .env if present (for NCBI_API_KEY)
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROCESSED_DIR = REPO_ROOT / "data" / "processed"
CACHE_DIR     = REPO_ROOT / "data" / "raw" / "biobrick_papers"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PARTS_CSV    = PROCESSED_DIR / "parts.csv"
PAPERS_OUT   = PROCESSED_DIR / "biobrick_papers.csv"
EDGES_OUT    = PROCESSED_DIR / "part_paper_edges_mentions.csv"

# Cache stores extracted records (NOT raw XML) so we can resume
CACHE_FILE      = CACHE_DIR / "fetched_records.jsonl"
CHECKPOINT_FILE = CACHE_DIR / "checkpoint.json"   # tracks last retstart

# ---------------------------------------------------------------------------
# NCBI eutils settings
# ---------------------------------------------------------------------------

EUTILS_BASE  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")    # optional; raises rate limit

BATCH_SIZE   = 200    # records per efetch request (NCBI max: 10,000 but large XMLs)
SLEEP_NO_KEY = 0.34   # ~3 req/sec without API key (NCBI limit)
SLEEP_W_KEY  = 0.11   # ~9 req/sec with API key
TIMEOUT_SEC  = 60

# Matches any BioBrick part ID in text:
#   Classic format: BBa_R0010, BBa_K1234567
#   Newer format:   BBa_25V0RSVX (longer alphanumeric suffix)
BIOBRICK_RE = re.compile(r"BBa_[A-Za-z0-9]+")


def sleep_politely():
    """Wait between NCBI requests to respect rate limits."""
    time.sleep(SLEEP_W_KEY if NCBI_API_KEY else SLEEP_NO_KEY)


def ncbi_params(**extra) -> dict:
    """Base params for every NCBI eutils request."""
    p = {"retmode": "json", **extra}
    if NCBI_API_KEY:
        p["api_key"] = NCBI_API_KEY
    return p


# ---------------------------------------------------------------------------
# Step 1: Collect all PMC IDs matching the search term
# ---------------------------------------------------------------------------

# NCBI esearch caps results at 9,999 IDs per query, regardless of retmax.
# We split the search into date-range sub-queries so each slice is under
# the limit, then deduplicate and merge.
YEAR_RANGES = [
    ("2000", "2015"),
    ("2016", "2019"),
    ("2020", "2022"),
    ("2023", "2030"),   # catches future publications in case the script is rerun
]


def _fetch_ids_for_range(base_term: str, year_start: str, year_end: str) -> list[str]:
    """Fetch all PMC IDs for `base_term` within a publication-date range."""
    term = f"{base_term} AND ({year_start}:{year_end}[pdat])"
    r = requests.get(
        f"{EUTILS_BASE}/esearch.fcgi",
        params=ncbi_params(db="pmc", term=term, retmax=9999, retmode="json"),
        timeout=TIMEOUT_SEC,
    )
    r.raise_for_status()
    result = r.json().get("esearchresult", {})
    if "ERROR" in result:
        logger.warning(f"esearch error for {year_start}-{year_end}: {result['ERROR']}")
        return []
    ids = result.get("idlist", [])
    count = int(result.get("count", 0))
    logger.info(f"  {year_start}–{year_end}: {len(ids):,} / {count:,} IDs")
    return ids


def get_all_pmc_ids(term: str = "BBa_") -> list[str]:
    """
    Return all PMC IDs matching `term`, split across year-range sub-queries.

    NCBI esearch has a hard cap of 9,999 IDs per query. To retrieve more
    than that, we split on publication-date ranges (YEAR_RANGES), each of
    which is well under the limit for our corpus. Results are deduplicated.

    Why not use WebEnv + efetch offsets?
    NCBI's PMC efetch returns HTTP 400 for offsets beyond ~9,800 when
    fetching full-text XML via a history-server query. Fetching by explicit
    ID list has no such limit.
    """
    all_ids: list[str] = []
    seen: set[str] = set()

    for year_start, year_end in YEAR_RANGES:
        ids = _fetch_ids_for_range(term, year_start, year_end)
        for i in ids:
            if i not in seen:
                all_ids.append(i)
                seen.add(i)
        sleep_politely()

    return all_ids


# ---------------------------------------------------------------------------
# Step 2: Fetch a batch of PMC articles as XML and extract data
# ---------------------------------------------------------------------------

def fetch_batch_xml(pmc_ids: list[str]) -> str:
    """
    Fetch a batch of PMC articles as full-text XML by explicit PMC ID list.

    Fetching by ID (rather than by WebEnv offset) avoids the NCBI efetch
    limit of ~9,800 records for PMC XML result sets.
    """
    r = requests.get(
        f"{EUTILS_BASE}/efetch.fcgi",
        params={
            "db":      "pmc",
            "id":      ",".join(pmc_ids),
            "rettype": "xml",
            "retmode": "xml",
            **({"api_key": NCBI_API_KEY} if NCBI_API_KEY else {}),
        },
        timeout=TIMEOUT_SEC,
    )
    r.raise_for_status()
    return r.text


def parse_batch_xml(xml_text: str) -> list[dict]:
    """
    Parse a batch of PMC article XML into a list of record dicts.

    For each article we extract:
      - pmcid: PubMed Central ID (e.g. "PMC12345")
      - pmid: PubMed ID (if available)
      - doi: DOI string (bare, without https://doi.org/)
      - title: article title (plain text)
      - abstract: abstract text (plain text, concatenated paragraphs)
      - year: publication year (int)
      - journal: journal title
      - authors: comma-separated author list
      - matched_parts: semicolon-separated BioBrick IDs found anywhere in full XML

    Only records where at least one BBa_ ID is found are returned.
    Records with no matches are silently discarded (they are false positives
    from the PMC text index treating _ as a word separator).
    """
    records = []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logger.warning(f"XML parse error: {e}. Skipping batch.")
        return records

    for article in root.iter("article"):
        # --- Regex-scan the whole article XML for BioBrick IDs ---
        article_xml = ET.tostring(article, encoding="unicode")
        found_ids = sorted(set(BIOBRICK_RE.findall(article_xml)))
        if not found_ids:
            continue   # not a genuine BioBrick paper

        # --- Extract metadata ---
        # IDs
        pmcid = ""
        pmid  = ""
        doi   = ""
        for aid in article.iter("article-id"):
            pub_type = aid.get("pub-id-type", "")
            val = aid.text.strip() if aid.text else ""
            if pub_type == "pmcid":
                # PMC efetch returns the full "PMC12345" string already
                pmcid = val if val.startswith("PMC") else f"PMC{val}"
            elif pub_type == "pmid":
                pmid = val
            elif pub_type == "doi":
                doi = val

        # Title
        title_el = article.find(".//article-title")
        title = "".join(title_el.itertext()).strip() if title_el is not None else ""

        # Abstract (concatenate all paragraph texts)
        abstract_parts = []
        for ab in article.iter("abstract"):
            for p in ab.iter("p"):
                abstract_parts.append("".join(p.itertext()).strip())
        abstract = " ".join(abstract_parts)

        # Publication year
        year = None
        for pd_el in article.iter("pub-date"):
            y_el = pd_el.find("year")
            if y_el is not None and y_el.text:
                try:
                    year = int(y_el.text.strip())
                    break
                except ValueError:
                    pass

        # Journal
        journal = ""
        j_el = article.find(".//journal-title")
        if j_el is not None:
            journal = "".join(j_el.itertext()).strip()

        # Authors (last-name + first initial)
        author_names = []
        for contrib in article.iter("contrib"):
            if contrib.get("contrib-type") == "author":
                sn = contrib.findtext("name/surname") or ""
                fn = contrib.findtext("name/given-names") or ""
                if sn:
                    author_names.append(f"{sn} {fn[0]}." if fn else sn)
        authors = ", ".join(author_names[:10])  # cap at 10 for readability

        records.append({
            "pmcid":         pmcid,
            "pmid":          pmid,
            "doi":           doi,
            "title":         title,
            "abstract":      abstract,
            "year":          year,
            "journal":       journal,
            "authors":       authors,
            "matched_parts": ";".join(found_ids),
            "retrieval_reason": "biobrick_fulltext_search",
        })

    return records


# ---------------------------------------------------------------------------
# Step 3: Build part → paper edge table
# ---------------------------------------------------------------------------

def build_edges(papers_df: pd.DataFrame, known_parts: set[str]) -> pd.DataFrame:
    """
    Expand matched_parts into one row per (part_name, paper) pair.
    Only includes BioBrick IDs that exist in our known parts set.
    Unknown IDs (typos, parts not in our corpus) are excluded from edges.
    """
    rows = []
    for _, row in papers_df.iterrows():
        ids = [x for x in (row["matched_parts"] or "").split(";") if x]
        for part_id in ids:
            if part_id in known_parts:
                rows.append({
                    "part_name": part_id,
                    "pmcid":     row["pmcid"],
                    "doi":       row["doi"],
                    "year":      row["year"],
                })
    return pd.DataFrame(rows).drop_duplicates(subset=["part_name", "pmcid"])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(max_records: int | None, resume: bool):
    print("=== Step 3e: Find papers mentioning BioBrick IDs (PMC full-text) ===\n")

    if NCBI_API_KEY:
        print(f"NCBI API key found — using higher rate limit (10 req/sec)\n")
    else:
        print("No NCBI_API_KEY found — using polite rate limit (3 req/sec)")
        print("  Tip: Get a free API key at https://www.ncbi.nlm.nih.gov/account/")
        print("  and add NCBI_API_KEY=yourkey to your .env file.\n")

    # Load known part IDs
    print(f"Loading part IDs from {PARTS_CSV.relative_to(REPO_ROOT)}…")
    parts_df    = pd.read_csv(PARTS_CSV, usecols=["part_name"])
    known_parts = set(parts_df["part_name"].dropna().unique())
    print(f"  {len(known_parts):,} unique part IDs loaded\n")

    # --- Resume or fresh start ---
    all_records: list[dict] = []
    seen_pmcids: set[str] = set()   # PMC IDs already processed
    fetched_ids: set[str] = set()   # PMC IDs already fetched (processed OR skipped)

    if resume and CACHE_FILE.exists() and CHECKPOINT_FILE.exists():
        print("Resuming from cache…")
        with open(CACHE_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                pmcid = rec.get("pmcid", "")
                if pmcid not in seen_pmcids:
                    all_records.append(rec)
                    seen_pmcids.add(pmcid)
        with open(CHECKPOINT_FILE) as f:
            checkpoint = json.load(f)
        fetched_ids = set(checkpoint.get("fetched_ids", []))
        print(f"  Loaded {len(all_records):,} cached papers. {len(fetched_ids):,} IDs already processed.\n")
    else:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()

    # --- Collect all PMC IDs ---
    print("Collecting all matching PMC IDs…")
    all_pmc_ids = get_all_pmc_ids("BBa_")
    print(f"  {len(all_pmc_ids):,} PMC IDs collected")

    if max_records:
        all_pmc_ids = all_pmc_ids[:max_records]
        print(f"  Limited to {len(all_pmc_ids):,} by --max-records")

    # Exclude IDs already processed in a previous run
    remaining_ids = [i for i in all_pmc_ids if i not in fetched_ids]
    n_batches = (len(remaining_ids) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"  {len(remaining_ids):,} IDs to fetch in {n_batches} batches of {BATCH_SIZE}\n")

    # --- Fetch loop ---
    for batch_num, batch_start in enumerate(range(0, len(remaining_ids), BATCH_SIZE), 1):
        chunk = remaining_ids[batch_start : batch_start + BATCH_SIZE]

        try:
            xml_text = fetch_batch_xml(chunk)
            sleep_politely()
        except requests.RequestException as e:
            logger.error(f"Batch {batch_num} fetch failed: {e}. Retrying in 15s…")
            time.sleep(15)
            try:
                xml_text = fetch_batch_xml(chunk)
                sleep_politely()
            except requests.RequestException as e2:
                logger.error(f"Retry failed: {e2}. Skipping batch {batch_num}.")
                fetched_ids.update(chunk)   # mark as processed so resume skips them
                continue

        new_records = parse_batch_xml(xml_text)

        # Deduplicate against already-seen PMCIDs
        unique_new = [r for r in new_records if r["pmcid"] not in seen_pmcids]
        for r in unique_new:
            seen_pmcids.add(r["pmcid"])
        all_records.extend(unique_new)
        fetched_ids.update(chunk)

        # Append to cache
        with open(CACHE_FILE, "a") as f:
            for r in unique_new:
                f.write(json.dumps(r) + "\n")

        # Save checkpoint
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump({"fetched_ids": list(fetched_ids)}, f)

        articles_in_batch = len(xml_text.split("<article ")) - 1
        logger.info(
            f"Batch {batch_num:>4}/{n_batches} | "
            f"in batch: {articles_in_batch:>4} | "
            f"with BBa_ IDs: {len(unique_new):>4} | "
            f"total kept: {len(all_records):>6}"
        )

    # --- Build DataFrames ---
    print(f"\n{'='*55}")
    print(f"Fetching complete. {len(all_records):,} papers with BioBrick IDs.")

    if not all_records:
        print("No records found. Exiting.")
        return

    papers_df = pd.DataFrame(all_records)
    # Use pmcid as primary key; fall back to doi when pmcid is missing
    papers_df["_key"] = papers_df["pmcid"].where(
        papers_df["pmcid"].notna() & (papers_df["pmcid"] != ""),
        papers_df["doi"],
    )
    papers_df = papers_df.drop_duplicates(subset=["_key"]).drop(columns=["_key"])

    print("\nBuilding part → paper edge table…")
    edges_df = build_edges(papers_df, known_parts)

    n_parts_found     = edges_df["part_name"].nunique() if len(edges_df) else 0
    all_found_ids     = (
        papers_df["matched_parts"].dropna()
        .str.split(";").explode()
        .replace("", pd.NA).dropna()
        .nunique()
        if len(papers_df) else 0
    )

    print(f"\nSummary:")
    print(f"  Papers mentioning ≥1 BioBrick ID:  {len(papers_df):>6,}")
    print(f"  Distinct BioBrick IDs mentioned:    {all_found_ids:>6,}")
    print(f"  Edges (part → paper, known parts):  {len(edges_df):>6,}")
    print(f"  Distinct known parts with a paper:  {n_parts_found:>6,} / {len(known_parts):,}")

    # --- Save ---
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    papers_df.to_csv(PAPERS_OUT, index=False)
    edges_df.to_csv(EDGES_OUT,   index=False)

    print(f"\nSaved:")
    print(f"  {PAPERS_OUT.relative_to(REPO_ROOT)}  ({len(papers_df):,} papers)")
    print(f"  {EDGES_OUT.relative_to(REPO_ROOT)}  ({len(edges_df):,} edges)")
    print("\nDone. You can join biobrick_papers.csv with parts.csv via part_name.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find PMC papers mentioning BioBrick IDs via NCBI eutils full-text search"
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Stop after processing N PMC records (useful for testing). Omit for full run.",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore existing cache and start fresh.",
    )
    args = parser.parse_args()

    run(max_records=args.max_records, resume=not args.no_resume)
