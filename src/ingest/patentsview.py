"""
patentsview.py — fetch patents from the PatentsView API.

PatentsView (https://patentsview.org) is maintained by the USPTO and provides
free, open access to US patent data. No API key is required for basic access
(up to 45 requests/minute). Optional: set PATENTSVIEW_API_KEY in .env for a
higher rate limit.

API documentation: https://patentsview.org/apis
Query language: https://patentsview.org/apis/purpose/query-data/api-query-language

Coverage note:
  PatentsView covers USPTO-granted US patents only. This is a limitation
  compared to Lens.org (global coverage), but US patents are the most widely
  used dataset in innovation research and are fully reproducible without any
  API key. The USPTO is the largest single patent office, so US-only coverage
  captures a large share of global synthetic biology patent activity.

Corpus construction strategy:
  Synthetic biology has no dedicated CPC patent classification code.
  A pure keyword search can overestimate activity because "synthetic biology"
  terminology overlaps with general biotechnology and genetic engineering
  (Oldham & Hall, 2018, bioRxiv doi:10.1101/483826).

  We use a two-layer keyword strategy following van Doren, Koenigstein & Reiss
  (2013, doi:10.1007/s11693-013-9121-7):
    - Layer 1: core self-identifying terms (high precision)
    - Layer 2: subfield/enabling terms (broader, catches adjacent work)

  Unlike Lens.org, PatentsView fully supports CPC class filtering. Enabling
  it (via use_cpc_filter=True) applies an AND condition requiring patents to
  belong to one of the configured technical classes — this reduces false
  positives but may exclude some synthetic biology patents assigned to
  non-standard classes. The filter is off by default for maximum recall.

Query structure:
  Each keyword is searched as an exact phrase across patent_title and
  patent_abstract (combined with OR). Multiple keywords within a layer are
  combined with OR logic. An optional CPC scope filter (AND) can be added
  to restrict results to biotechnology patent classes.

Location data (an improvement over Lens.org):
  PatentsView returns city, country, latitude, and longitude for assignees
  (the companies or institutions that own the patent). This allows direct
  geocoding of patents without a separate geocoding step, unlike Lens.org
  which only returned a country code.

Searchable fields (from PatentsView schema):
  patent_title    — title text (supports _text_phrase)
  patent_abstract — abstract text (supports _text_phrase)
  patent_date     — grant date (ISO 8601 string, e.g. "2015-06-30")
  cpc_group_id    — CPC group code (e.g. "C12N", supports exact match)

Returned fields used by this module:
  patent_id       — USPTO patent number (e.g. "10234567")
  patent_title    — title string
  patent_abstract — abstract string
  patent_date     — grant date string
  assignees       — list of {assignee_city, assignee_country,
                             assignee_latitude, assignee_longitude}
  cpcs            — list of {cpc_group_id, cpc_subgroup_id}
"""

from __future__ import annotations
import os
import time
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

PATENTSVIEW_BASE = "https://search.patentsview.org/api/v1/patent/"

# Fields to retrieve for each patent.
# assignees gives us city / country / lat / lon directly — no separate
# geocoding step needed for the country level.
_RETURN_FIELDS = [
    "patent_id",
    "patent_title",
    "patent_abstract",
    "patent_date",
    "assignees",   # nested: assignee_city, assignee_country, lat, lon
    "cpcs",        # nested: cpc_group_id, cpc_subgroup_id (for analysis)
]


def search_patents(
    keywords: list[str],
    cpc_codes: list[str] | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 5000,
    per_page: int = 1000,
    retrieval_reason: str = "keyword",
    use_cpc_filter: bool = False,
) -> list[dict]:
    """
    Search PatentsView for patents matching the given keywords.

    Keywords are searched as exact phrases across patent_title and
    patent_abstract. Results from all keywords are combined with OR logic.
    CPC class filtering can optionally be enabled for higher precision.

    Parameters
    ----------
    keywords        : exact phrases to search in title and abstract
    cpc_codes       : CPC group codes to restrict results (e.g. ["C12N", "C12P"]).
                      Only used when use_cpc_filter=True.
    year_min        : earliest grant year to include (inclusive)
    year_max        : latest grant year to include (inclusive)
    max_results     : stop after collecting this many patents
    per_page        : patents per API request (PatentsView max is 1000)
    retrieval_reason: label injected into each record for downstream tracking
    use_cpc_filter  : if True, AND the keyword query with a CPC code filter.
                      Increases precision but may miss some relevant patents.

    Returns
    -------
    List of raw patent dicts, each with a 'retrieval_reason' key added.
    Pass each dict to extract_fields() to flatten to a normalizable record.
    """
    headers = {"Content-Type": "application/json"}

    # Optional API key for higher rate limits.
    api_key = os.getenv("PATENTSVIEW_API_KEY", "")
    if api_key:
        headers["X-Api-Key"] = api_key

    query = _build_query(
        keywords=keywords,
        cpc_codes=cpc_codes if use_cpc_filter else None,
        year_min=year_min,
        year_max=year_max,
    )

    results: list[dict] = []
    after_cursor: str | None = None

    while len(results) < max_results:
        batch_size = min(per_page, max_results - len(results))

        options: dict[str, Any] = {"per_page": batch_size}
        if after_cursor:
            options["after"] = after_cursor

        payload: dict[str, Any] = {
            "q": query,
            "f": _RETURN_FIELDS,
            "o": options,
        }

        # Retry with exponential backoff on rate-limit (429) responses.
        # PatentsView enforces 45 requests/minute without a key. Waiting
        # and retrying is the correct response.
        max_retries = 5
        backoff = 30   # seconds to wait on first 429; doubles each retry
        response = None

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    PATENTSVIEW_BASE,
                    json=payload,
                    headers=headers,
                    timeout=60,
                )
                if response.status_code == 429:
                    wait = backoff * (2 ** attempt)
                    logger.warning(
                        f"Rate limited (429). Waiting {wait}s before retry "
                        f"{attempt + 1}/{max_retries}..."
                    )
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                break
            except requests.RequestException as e:
                logger.error(f"PatentsView request failed: {e}")
                response = None
                break

        if response is None or not response.ok:
            logger.error("PatentsView: giving up after retries or request error.")
            break

        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to parse PatentsView response: {e}")
            break

        batch = data.get("patents") or []
        if not batch:
            break

        for patent in batch:
            patent["retrieval_reason"] = retrieval_reason

        results.extend(batch)
        total = data.get("total_patent_count", 0)
        logger.info(
            f"PatentsView: retrieved {len(results)} / {min(total, max_results)}"
        )

        # Cursor-based pagination: 'after' value comes from the last record.
        # PatentsView v1 returns a '_cursor' field in each patent for this.
        last_cursor = batch[-1].get("_cursor")
        if last_cursor and len(results) < total:
            after_cursor = last_cursor
        else:
            break

        time.sleep(1.5)  # polite delay between pages

    return results


def extract_fields(patent: dict) -> dict:
    """
    Pull the fields we care about from a raw PatentsView patent object.

    Returns a flat dict ready to be passed to normalize.normalize_patents().

    PatentsView provides location at the assignee level. We use the first
    assignee with a non-empty city. If no city is available, we fall back to
    country only. Latitude and longitude are included when available — this
    means many patents can skip the geocoding step entirely.
    """
    title    = patent.get("patent_title") or ""
    abstract = patent.get("patent_abstract") or ""

    year = None
    date_str = patent.get("patent_date") or ""
    if date_str:
        try:
            year = int(date_str[:4])
        except (ValueError, TypeError):
            pass

    city, country, lat, lon = _extract_location(patent)

    return {
        "patent_id":        patent.get("patent_id", ""),
        "title":            title,
        "abstract":         abstract,
        "year":             year,
        "city":             city,
        "country":          country,
        "lat":              lat,
        "lon":              lon,
        "retrieval_reason": patent.get("retrieval_reason", "keyword"),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_query(
    keywords: list[str],
    cpc_codes: list[str] | None,
    year_min: int | None,
    year_max: int | None,
) -> dict:
    """
    Build a PatentsView API v1 query dict.

    Each keyword is searched as an exact phrase in patent_title OR
    patent_abstract. Multiple keywords are combined with OR. An optional
    CPC scope filter and date range are added with AND logic.
    """
    # One OR clause per keyword, searching both title and abstract.
    # _text_phrase requires an exact match of the full phrase anywhere in the
    # field text — appropriate for multi-word terms like "synthetic biology".
    keyword_clauses: list[dict] = []
    for kw in keywords:
        keyword_clauses.append({"_text_phrase": {"patent_title": kw}})
        keyword_clauses.append({"_text_phrase": {"patent_abstract": kw}})

    keyword_query: dict = {"_or": keyword_clauses}

    # Conditions to AND together with the keyword query.
    and_conditions: list[dict] = [keyword_query]

    # CPC class filter — only applied when use_cpc_filter=True was passed.
    # Each CPC code is matched as an exact group ID (e.g. "C12N").
    if cpc_codes:
        cpc_clauses = [{"_eq": {"cpc_group_id": code}} for code in cpc_codes]
        and_conditions.append({"_or": cpc_clauses})

    # Date range — PatentsView patent_date is the grant date (YYYY-MM-DD).
    if year_min:
        and_conditions.append({"_gte": {"patent_date": f"{year_min}-01-01"}})
    if year_max:
        and_conditions.append({"_lte": {"patent_date": f"{year_max}-12-31"}})

    if len(and_conditions) == 1:
        return and_conditions[0]
    return {"_and": and_conditions}


def _extract_location(patent: dict) -> tuple[str | None, str | None, float | None, float | None]:
    """
    Extract city, country, latitude, and longitude from the first assignee
    with a usable location.

    PatentsView returns an `assignees` list, each entry containing:
      assignee_city       — string (may be empty)
      assignee_country    — ISO alpha-2 country code (may be empty)
      assignee_latitude   — float (may be null)
      assignee_longitude  — float (may be null)

    We use the first assignee that has a non-null country. City and
    coordinates are populated when available, otherwise left as None.
    They will be filled in by the geocoding step if missing.
    """
    assignees = patent.get("assignees") or []
    for assignee in assignees:
        country = assignee.get("assignee_country") or None
        if not country:
            continue
        city = assignee.get("assignee_city") or None
        lat  = assignee.get("assignee_latitude")
        lon  = assignee.get("assignee_longitude")
        # Convert string lat/lon to float if present
        try:
            lat = float(lat) if lat is not None else None
            lon = float(lon) if lon is not None else None
        except (ValueError, TypeError):
            lat, lon = None, None
        return city, country, lat, lon
    return None, None, None, None
