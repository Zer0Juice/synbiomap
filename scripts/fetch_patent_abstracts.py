"""
fetch_patent_abstracts.py — get abstract text for the Oldham patents so they can
be embedded on full text, not titles alone.

Why this is a separate step:
  The USPTO Open Data Portal (ODP) bibliographic API returns the patent TITLE
  but NOT the abstract. Embedding titles alone gives a weak semantic signal —
  two patents can share a vague title ("Genetic circuit") yet describe very
  different inventions. Abstracts are the standard text field for patent
  embedding (e.g. Shapira, Kwon & Youtie 2017, doi:10.1007/s11192-017-2452-5).

How we get the abstract anyway:
  Each granted patent's ODP record carries grantDocumentMetaData.fileLocationURI,
  a link to that patent's grant XML in the USPTO bulk dataset (PTGRXML-SPLT).
  That XML contains the full <abstract>. We look up the link, download the XML,
  and parse the abstract (see src/ingest/odp.py).

Scope:
  We fetch one abstract per Oldham family — the representative US grant
  (`rep_patent`) chosen during geocoding (scripts/geocode_oldham_patents.py).
  That matches the one-row-per-family structure of the embedding corpus.

Output (data/processed/):
  oldham_patent_abstracts.csv — id, rep_patent, title, abstract, text,
  has_abstract. `text` = "title. abstract" (title only if no abstract) and is
  the field to embed. Join to oldham_patents_geocoded.csv on `id`.

Cache (data/raw/oldham/patent_abstracts.json):
  bare patent number -> {"file_uri", "abstract"}. Saved incrementally, so an
  interrupted run resumes without re-downloading. Delete it to force a refetch.

Usage:
    python scripts/fetch_patent_abstracts.py
Requires USPTO_ODP_KEY in .env.
"""

from __future__ import annotations
import re
import sys
import json
import logging
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
load_dotenv(REPO_ROOT / ".env")

from src.ingest import odp

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

GEOCODED   = REPO_ROOT / "data" / "processed" / "oldham_patents_geocoded.csv"
CACHE_PATH = REPO_ROOT / "data" / "raw" / "oldham" / "patent_abstracts.json"
OUT_PATH   = REPO_ROOT / "data" / "processed" / "oldham_patent_abstracts.csv"

# Polite delay between grant-XML downloads (seconds). The ODP file endpoint is
# rate-limited per key; 0.6s keeps us well-behaved and the run cache-restartable.
DOWNLOAD_DELAY = 0.6
SAVE_EVERY = 50


def _bare(rep_patent: str) -> str:
    """'US10059961' -> '10059961' (bare grant number for ODP lookup)."""
    return re.sub(r"^US", "", str(rep_patent or "").strip())


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache))


def run():
    print("=== Fetch patent abstracts for the Oldham corpus ===\n")
    if not GEOCODED.exists():
        raise FileNotFoundError(
            f"{GEOCODED} not found. Run scripts/geocode_oldham_patents.py first."
        )

    fam = pd.read_csv(GEOCODED, dtype={"rep_patent": str})
    fam = fam[fam["rep_patent"].fillna("").str.strip() != ""].copy()
    fam["number"] = fam["rep_patent"].map(_bare)
    numbers = sorted(fam["number"].unique())
    print(f"Families with a representative US grant: {len(fam)}")
    print(f"Unique patent numbers to fetch:          {len(numbers)}\n")

    cache = load_cache()

    # ------------------------------------------------------------------
    # Phase A — get the grant-XML link (file_uri) for any new numbers.
    # ------------------------------------------------------------------
    need_uri = [n for n in numbers if n not in cache]
    if need_uri:
        print(f"--- Phase A: looking up grant-document links for {len(need_uri)} patents ---")
        docs = odp.lookup_grant_documents(need_uri, batch_size=20)
        for n in need_uri:
            d = docs.get(n) or {}
            cache[n] = {"file_uri": d.get("file_uri", "")}  # abstract added in Phase B
        save_cache(cache)
    else:
        print("--- Phase A: all grant-document links already cached ---")

    # ------------------------------------------------------------------
    # Phase B — download each grant XML and extract its abstract.
    # ------------------------------------------------------------------
    import time
    todo = [n for n in numbers if "abstract" not in cache.get(n, {})]
    print(f"\n--- Phase B: downloading abstracts for {len(todo)} patents "
          f"({len(numbers) - len(todo)} already cached) ---")

    for i, n in enumerate(todo, 1):
        entry = cache.setdefault(n, {"file_uri": ""})
        uri = entry.get("file_uri", "")
        if not uri:
            entry["abstract"] = ""          # no grant doc -> no abstract available
        else:
            xml = odp.fetch_grant_xml(uri)
            if xml is None:
                continue                     # transient failure: leave for next run
            entry["abstract"] = odp.extract_abstract_from_grant_xml(xml)
            time.sleep(DOWNLOAD_DELAY)

        if i % SAVE_EVERY == 0:
            save_cache(cache)
            got = sum(1 for n2 in numbers if cache.get(n2, {}).get("abstract"))
            logger.info(f"  {i}/{len(todo)} fetched ({got} non-empty abstracts so far)")

    save_cache(cache)

    # ------------------------------------------------------------------
    # Build the output table (one row per family).
    # ------------------------------------------------------------------
    def _abstract(n: str) -> str:
        return (cache.get(n, {}) or {}).get("abstract", "") or ""

    fam["abstract"] = fam["number"].map(_abstract)
    fam["has_abstract"] = fam["abstract"].str.len() > 0
    # Embedding text: title + abstract (title alone if abstract missing).
    title = fam["title"].fillna("").astype(str).str.strip()
    fam["text"] = [
        (f"{t}. {a}" if a else t).strip(". ").strip() or t
        for t, a in zip(title, fam["abstract"])
    ]

    out = fam[["id", "rep_patent", "title", "abstract", "text", "has_abstract"]]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    n_abs = int(fam["has_abstract"].sum())
    mean_len = int(fam.loc[fam["has_abstract"], "abstract"].str.len().mean()) if n_abs else 0
    print(f"\nSaved {len(out)} rows -> {OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Abstracts retrieved: {n_abs}/{len(fam)} ({n_abs/len(fam):.0%})")
    print(f"Mean abstract length: {mean_len} characters")
    print("\nExample:")
    ex = fam[fam["has_abstract"]].iloc[0]
    print(f"  {ex['rep_patent']}  {ex['title'][:55]}")
    print(f"  {ex['abstract'][:200]}...")

    return out


if __name__ == "__main__":
    run()
