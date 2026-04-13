"""
patentsview.py — fetch patents from PatentsView (USPTO bulk database).

PatentsView is maintained by the USPTO and provides free, open access to
US patent data via a REST API. No API key or authentication is required.

API documentation: https://patentsview.org/apis/purpose-built-databases/api
Query language:    https://patentsview.org/apis/purpose-built-databases/api

Coverage note:
  PatentsView covers **granted US patents** (USPTO) only. It does not
  include European, PCT (international), or other national patents.
  For synthetic biology innovation studies, US patents are an important
  signal because the US is historically the largest single source of
  synthetic biology patents (van Doren et al., 2013). Any cross-country
  geographic comparison should account for this US-only scope.

Corpus construction strategy:
  Synthetic biology has no dedicated CPC patent classification code.
  A pure keyword search can overestimate activity due to overlap with
  general biotechnology (Oldham & Hall, 2018, bioRxiv doi:10.1101/483826).

  We follow the keyword-layer strategy from van Doren, Koenigstein & Reiss
  (2013, doi:10.1007/s11693-013-9121-7), searching patent title and abstract
  with two keyword groups. CPC code filtering can be added as an optional
  AND constraint to improve precision; CPC and IPC codes are equivalent for
  these biotechnology classes (C12N, C12P, C12Q).

Searchable fields:
  patent_title      — patent title text
  patent_abstract   — abstract text
  patent_date       — grant date (YYYY-MM-DD), supports range queries
  cpc_subgroup_id   — CPC classification code (supports _begins for prefix match)

Location data:
  PatentsView pre-geocodes assignee addresses, so latitude and longitude
  are available directly from the API — no separate geocoding step is needed
  for patent locations.
"""

from __future__ import annotations
import logging
import time

import requests

logger = logging.getLogger(__name__)

PATENTSVIEW_BASE = "https://api.patentsview.org/patents/query"

# Fields to request from PatentsView.
# Assignee location fields are nested under the 'assignees' sub-entity.
_FIELDS = [
    "patent_number",
    "patent_date",
    "patent_title",
    "patent_abstract",
    "assignee_organization",
    "assignee_city",
    "assignee_state",
    "assignee_country",
    "assignee_latitude",
    "assignee_longitude",
    "cpc_subgroup_id",
]


def search_patents(
    keywords: list[str],
    cpc_codes: list[str] | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 2000,
    per_page: int = 100,
    retrieval_reason: str = "keyword",
) -> list[dict]:
    """
    Search PatentsView for US patents matching keywords.

    Keywords are searched across patent title AND abstract (OR between
    keywords, OR between title/abstract) so that any keyword hit anywhere
    in the text retrieves the patent. This mirrors the full-text keyword
    strategy from van Doren et al. (2013).

    Parameters
    ----------
    keywords        : search terms matched against title and abstract
    cpc_codes       : optional CPC class prefixes (e.g. ["C12N", "C12P"])
                      applied as an AND constraint for higher precision;
                      if None, no CPC filter is applied
    year_min        : earliest grant year (inclusive)
    year_max        : latest grant year (inclusive)
    max_results     : stop after this many patents
    per_page        : results per request (PatentsView max is 100)
    retrieval_reason: label injected into each patent dict to track which
                      layer of the corpus strategy found it
    """
    # Build keyword clause.
    # _text_phrase requires an exact phrase match, which is what we want for
    # multi-word terms like "synthetic biology" (not a bag-of-words match).
    # We search both title and abstract so that patents that describe the
    # concept in the abstract but not the title are included.
    keyword_clauses = []
    for kw in keywords:
        keyword_clauses.append({"_text_phrase": {"patent_title": kw}})
        keyword_clauses.append({"_text_phrase": {"patent_abstract": kw}})

    clauses: list[dict] = [{"_or": keyword_clauses}]

    # Optional CPC filter: require at least one matching class prefix.
    # This reduces false positives from general biotech patents that use
    # synthetic biology terminology loosely (van Doren et al. 2013).
    if cpc_codes:
        cpc_clauses = [{"_begins": {"cpc_subgroup_id": code}} for code in cpc_codes]
        clauses.append({"_or": cpc_clauses})

    # Date range filters. patent_date is in "YYYY-MM-DD" format.
    if year_min:
        clauses.append({"_gte": {"patent_date": f"{year_min}-01-01"}})
    if year_max:
        clauses.append({"_lte": {"patent_date": f"{year_max}-12-31"}})

    query = {"_and": clauses} if len(clauses) > 1 else clauses[0]

    results: list[dict] = []
    page = 1

    while len(results) < max_results:
        batch_size = min(per_page, max_results - len(results))
        payload = {
            "q": query,
            "f": _FIELDS,
            "o": {"per_page": batch_size, "page": page},
        }

        # Retry with exponential backoff on rate-limit (429) responses.
        max_retries = 5
        backoff = 10  # seconds; PatentsView is generally generous with limits
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    PATENTSVIEW_BASE, json=payload, timeout=30
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

        if len(results) >= total:
            break

        page += 1
        time.sleep(1.0)  # polite delay between pages

    return results


def extract_fields(patent: dict) -> dict:
    """
    Pull the fields we care about from a raw PatentsView patent object.

    Returns a flat dict ready to be passed to normalize.py.

    PatentsView nests assignee location under an 'assignees' list. We take
    the first assignee's location (primary assignee). Patents with no
    assignee are kept but will lack location data.

    Unlike Lens.org, PatentsView pre-geocodes assignee addresses, so
    lat/lon are available directly without a separate geocoding step.
    """
    title    = (patent.get("patent_title") or "").strip()
    abstract = (patent.get("patent_abstract") or "").strip()
    country, city, lat, lon = _extract_location(patent)

    year = None
    date_str = patent.get("patent_date") or ""
    if date_str:
        try:
            year = int(date_str[:4])
        except (ValueError, TypeError):
            pass

    return {
        "patent_id":        patent.get("patent_number", ""),
        "title":            title,
        "abstract":         abstract,
        "year":             year,
        "city":             city,
        "country":          country,
        "lat":              lat,
        "lon":              lon,
        "retrieval_reason": patent.get("retrieval_reason", "keyword"),
    }


def _extract_location(
    patent: dict,
) -> tuple[str | None, str | None, float | None, float | None]:
    """
    Extract country, city, and coordinates from the first assignee.

    PatentsView pre-geocodes assignee addresses, so lat/lon are available
    directly without a separate geocoding step. This improves on Lens.org,
    which only provided a country code and left city/coordinates to
    downstream geocoding.

    The first assignee is used as the primary location. For patents with
    multiple assignees, only the first is used here; the full list is
    available in the raw cached data if needed later.
    """
    assignees = patent.get("assignees") or []
    for a in assignees:
        country = a.get("assignee_country") or None
        city    = a.get("assignee_city") or None
        lat_raw = a.get("assignee_latitude")
        lon_raw = a.get("assignee_longitude")
        try:
            lat = float(lat_raw) if lat_raw not in (None, "") else None
            lon = float(lon_raw) if lon_raw not in (None, "") else None
        except (ValueError, TypeError):
            lat, lon = None, None
        return country, city, lat, lon  # first assignee only
    return None, None, None, None
