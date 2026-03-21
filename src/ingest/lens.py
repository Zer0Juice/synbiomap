"""
lens.py — fetch patents from the Lens.org API.

Lens.org is a free patent and scholarly search platform.
Patent retrieval requires a free API token (set LENS_API_TOKEN in .env).

API documentation: https://docs.api.lens.org/

Corpus construction strategy:
  Synthetic biology has no dedicated IPC/CPC patent classification code.
  A pure keyword search radically overestimates activity because "synthetic
  biology" terminology overlaps with general biotechnology and genetic
  engineering (Oldham & Hall, 2018, bioRxiv doi:10.1101/483826).

  We follow van Doren, Koenigstein & Reiss (2013, Systems and Synthetic
  Biology, doi:10.1007/s11693-013-9121-7), who combined:
    1. An IPC class scope filter (C12N, C12P, C12Q, C12S, C40B)
    2. Synthetic biology keyword groups
  using AND logic, yielding 1,195 patents from WIPO (1990–2010).

  The IPC filter ensures we only retrieve patents in the right technical
  space (genetic engineering, fermentation, enzyme processes, gene
  libraries). The keywords then select for synthetic biology specifically
  within that space.
"""

from __future__ import annotations
import os
import time
import logging
from typing import Iterator

import requests

logger = logging.getLogger(__name__)

LENS_BASE = "https://api.lens.org/patent/search"


def search_patents(
    keywords: list[str],
    ipc_codes: list[str] | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 2000,
    per_page: int = 100,
    retrieval_reason: str = "keyword",
) -> list[dict]:
    """
    Search Lens.org for patents matching keywords within IPC code scope.

    When `ipc_codes` are provided, the query requires BOTH a keyword match
    AND an IPC classification match (AND logic). This is the van Doren et al.
    (2013) approach and substantially reduces false positives from general
    biotech patents.

    Parameters
    ----------
    keywords        : search terms matched against title, abstract, and claims
    ipc_codes       : IPC code prefixes to filter by (e.g. ["C12N", "C40B"]).
                      Each prefix is matched with a wildcard (C12N → C12N*).
                      If None or empty, no IPC filter is applied.
    year_min        : earliest publication year (inclusive)
    year_max        : latest publication year (inclusive)
    max_results     : stop after this many patents
    per_page        : results per request (Lens.org max is 100)
    retrieval_reason: label injected into each patent dict for tracking
                      which layer of the corpus strategy found it
    """
    token = os.getenv("LENS_API_TOKEN", "")
    if not token:
        raise EnvironmentError(
            "LENS_API_TOKEN is not set. Add it to your .env file. "
            "Get a free token at https://www.lens.org/lens/user/subscriptions"
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # --- Build query ---
    must_clauses = []

    # Keyword clause: any keyword match in title, abstract, or claims
    keyword_query = " OR ".join(f'"{kw}"' for kw in keywords)
    must_clauses.append({
        "query_string": {
            "query": keyword_query,
            "fields": ["title", "abstract", "claims.text"],
        }
    })

    # IPC filter: patent must belong to at least one of the target classes.
    # We use wildcard matching (C12N → C12N*) to catch all subclasses.
    # The IPC symbol field in Lens is: biblio.classifications_ipcr.classifications.symbol
    if ipc_codes:
        ipc_query = " OR ".join(f"{code}*" for code in ipc_codes)
        must_clauses.append({
            "query_string": {
                "query": ipc_query,
                "fields": ["biblio.classifications_ipcr.classifications.symbol"],
            }
        })

    # Date filter
    if year_min or year_max:
        date_range: dict = {"date_published": {}}
        if year_min:
            date_range["date_published"]["gte"] = f"{year_min}-01-01"
        if year_max:
            date_range["date_published"]["lte"] = f"{year_max}-12-31"
        must_clauses.append({"range": date_range})

    results = []
    offset = 0

    while len(results) < max_results:
        batch_size = min(per_page, max_results - len(results))

        payload = {
            "query": {"bool": {"must": must_clauses}},
            "size": batch_size,
            "from": offset,
            "include": [
                "lens_id", "title", "abstract", "date_published",
                "applicants", "inventors", "jurisdiction",
                "biblio.application_reference",
                "biblio.classifications_ipcr",  # IPC codes for the record
            ],
        }

        try:
            response = requests.post(LENS_BASE, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Lens.org request failed: {e}")
            break

        batch = data.get("data", [])
        if not batch:
            break

        for patent in batch:
            patent["retrieval_reason"] = retrieval_reason

        results.extend(batch)
        offset += len(batch)

        total = data.get("total", 0)
        logger.info(f"Lens.org: retrieved {len(results)} / {min(total, max_results)}")

        if offset >= total:
            break

        time.sleep(0.5)  # Lens.org recommends being polite

    return results


def extract_fields(patent: dict) -> dict:
    """
    Pull the fields we care about from a raw Lens patent object.

    Returns a flat dict ready to be passed to normalize.py.
    """
    title    = _extract_title(patent)
    abstract = _extract_abstract(patent)
    city, country = _extract_location(patent)

    year = None
    date_pub = patent.get("date_published", "")
    if date_pub:
        try:
            year = int(date_pub[:4])
        except (ValueError, TypeError):
            pass

    return {
        "lens_id":          patent.get("lens_id", ""),
        "title":            title,
        "abstract":         abstract,
        "year":             year,
        "city":             city,
        "country":          country,
        "retrieval_reason": patent.get("retrieval_reason", "keyword"),
    }


def _extract_title(patent: dict) -> str:
    title = patent.get("title", "")
    if isinstance(title, list):
        for t in title:
            if isinstance(t, dict) and t.get("lang") == "en":
                return t.get("text", "")
        if title:
            first = title[0]
            return first.get("text", "") if isinstance(first, dict) else str(first)
    return str(title or "")


def _extract_abstract(patent: dict) -> str:
    abstract = patent.get("abstract", "")
    if isinstance(abstract, list):
        for a in abstract:
            if isinstance(a, dict) and a.get("lang") == "en":
                return a.get("text", "")
        if abstract:
            first = abstract[0]
            return first.get("text", "") if isinstance(first, dict) else str(first)
    return str(abstract or "")


def _extract_location(patent: dict) -> tuple[str | None, str | None]:
    """
    Extract city and country from the first applicant.

    Applicants (organizations that filed the patent) often carry location.
    We prefer `residence` if present, otherwise fall back to top-level fields.
    """
    for applicant in patent.get("applicants", []):
        residence = applicant.get("residence", {})
        country   = residence.get("country_code") or applicant.get("country_code")
        city      = residence.get("city")          or applicant.get("city")
        if country:
            return city, country
    return None, None
