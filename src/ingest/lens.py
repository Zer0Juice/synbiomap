"""
lens.py — fetch patents from the Lens.org API.

Lens.org is a free patent and scholarly search platform.
Patent retrieval requires a free API token (set LENS_API_TOKEN in .env).

API documentation: https://docs.api.lens.org/
Schema reference: GET https://api.lens.org/schema/patent

Corpus construction strategy:
  Synthetic biology has no dedicated IPC/CPC patent classification code.
  A pure keyword search can overestimate activity because "synthetic biology"
  terminology overlaps with general biotechnology and genetic engineering
  (Oldham & Hall, 2018, bioRxiv doi:10.1101/483826).

  van Doren, Koenigstein & Reiss (2013, doi:10.1007/s11693-013-9121-7)
  combined IPC class filters with keyword groups for precision. We adopt the
  same keyword strategy but apply it to the `full_text` field (title +
  abstract + claims + description) rather than via IPC code filtering, since
  the Lens.org API does not expose IPC classification symbols as a searchable
  field in the standard API plan. The multi-keyword layered approach still
  achieves comparable precision — synthetic-biology-specific terminology is
  rare in non-synbio biotech patents.

Searchable fields confirmed via schema (GET /schema/patent):
  full_text    — combined title, abstract, claims, description (best coverage)
  abstract     — abstract text only
  description  — description text only
  date_published — top-level date field, supports range queries
  jurisdiction   — top-level string field (e.g. "US", "EP")
  lang           — top-level string field (e.g. "en")

Retrievable (include) fields:
  biblio.invention_title          — list of {text, lang}
  biblio.parties.applicants       — list of {extracted_name.value, residence, extracted_address}
  biblio.classifications_ipcr     — IPC classifications (retrievable but not searchable)
  abstract                        — list of {text, lang}
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
    Search Lens.org for patents matching keywords.

    Keywords are searched across the `full_text` field, which covers title,
    abstract, claims, and description. This is the broadest and most reliable
    search field confirmed by the Lens.org schema (GET /schema/patent).

    Note on IPC filtering: the `ipc_codes` parameter is accepted for API
    compatibility but is silently ignored. The Lens.org standard API plan does
    not expose IPC classification symbols as a searchable field — queries
    against biblio.classifications_ipcr.classifications.symbol consistently
    return 0 results even for records that contain those codes. IPC codes ARE
    retrievable (returned in the response) and are used downstream for
    analysis, but cannot be used as a query filter.

    Parameters
    ----------
    keywords        : search terms matched across full patent text
    ipc_codes       : ignored (kept for API compatibility with the config file)
    year_min        : earliest publication year (inclusive)
    year_max        : latest publication year (inclusive)
    max_results     : stop after this many patents
    per_page        : results per request (Lens.org max is 100)
    retrieval_reason: label injected into each patent dict for tracking
                      which layer of the corpus strategy found it
    """
    token = os.getenv("LENS_API_TOKEN", "")
    if not token or token == "your_lens_token_here":
        raise EnvironmentError(
            "LENS_API_TOKEN is not configured. Open .env and replace "
            "'your_lens_token_here' with your real token. "
            "Get a free token at https://www.lens.org/lens/user/subscriptions"
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # --- Build query ---
    must_clauses = []

    # Keyword clause: search full_text (title + abstract + claims + description).
    # Phrase queries ("synthetic biology") require exact match; OR combines layers.
    keyword_query = " OR ".join(f'"{kw}"' for kw in keywords)
    must_clauses.append({
        "query_string": {
            "query": keyword_query,
            "fields": ["full_text"],
        }
    })

    # Date filter: uses date_published, a top-level field that supports range queries.
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
            # Include fields confirmed against GET /schema/patent.
            # biblio.* subfields are object paths returned nested under biblio.
            "include": [
                "lens_id", "date_published", "jurisdiction",
                "biblio.invention_title",        # list of {text, lang}
                "biblio.parties.applicants",     # list of {extracted_name.value, residence, extracted_address}
                "biblio.classifications_ipcr",   # IPC codes (for downstream analysis)
                "abstract",                      # list of {text, lang}
            ],
        }

        # Retry with exponential backoff on rate-limit (429) responses.
        # Lens.org enforces a per-account rate limit; waiting and retrying
        # is the correct response rather than giving up.
        max_retries = 5
        backoff = 60  # seconds to wait on first 429; doubles each retry
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(LENS_BASE, json=payload, headers=headers, timeout=30)
                if response.status_code == 429:
                    wait = backoff * (2 ** attempt)
                    logger.warning(f"Rate limited (429). Waiting {wait}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                break
            except requests.RequestException as e:
                logger.error(f"Lens.org request failed: {e}")
                response = None
                break
        if response is None or not response.ok:
            logger.error("Lens.org: giving up after retries or request error.")
            break
        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to parse Lens.org response: {e}")
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

        time.sleep(2.0)  # polite delay between pages; reduces risk of 429

    return results


def extract_fields(patent: dict) -> dict:
    """
    Pull the fields we care about from a raw Lens patent object.

    Returns a flat dict ready to be passed to normalize.py.

    Field paths match the confirmed Lens schema (GET /schema/patent):
      biblio.invention_title      — list of {text, lang}
      biblio.parties.applicants   — list of {extracted_name.value, residence, extracted_address}
      abstract                    — list of {text, lang}
    """
    title    = _extract_title(patent)
    abstract = _extract_abstract(patent)
    country, city = _extract_location(patent)

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
    """Title lives at biblio.invention_title as a list of {text, lang}."""
    titles = patent.get("biblio", {}).get("invention_title", [])
    if not titles:
        return ""
    # Prefer English; fall back to first entry
    for t in titles:
        if isinstance(t, dict) and t.get("lang") == "en":
            return t.get("text", "")
    first = titles[0]
    return first.get("text", "") if isinstance(first, dict) else str(first)


def _extract_abstract(patent: dict) -> str:
    """Abstract lives at the top-level `abstract` field as a list of {text, lang}."""
    abstracts = patent.get("abstract", [])
    if not abstracts:
        return ""
    # Prefer English; fall back to first entry
    for a in abstracts:
        if isinstance(a, dict) and a.get("lang") == "en":
            return a.get("text", "")
    first = abstracts[0]
    return first.get("text", "") if isinstance(first, dict) else str(first)


def _extract_location(patent: dict) -> tuple[str | None, str | None]:
    """
    Extract country and city from applicants.

    Applicants live at biblio.parties.applicants as a list of:
      {extracted_name: {value}, residence: "US", extracted_address: "..."}

    `residence` is a 2-letter country code (e.g. "US", "CH").
    `extracted_address` sometimes contains a city but is unstructured.
    We return the country code directly and leave city as None unless
    a city can be parsed — geocoding is handled downstream by normalize.py.
    """
    applicants = patent.get("biblio", {}).get("parties", {}).get("applicants", [])
    for applicant in applicants:
        country = applicant.get("residence")  # 2-letter ISO code or None
        if country:
            # extracted_address is a raw string like "ETH Zurich, Zurich, Switzerland"
            # We don't attempt to parse city here; downstream geocoding handles it
            return country, None
    return None, None
