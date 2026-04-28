"""
patentsview.py — fetch USPTO patents from the PatentsView API.

PatentsView (search.patentsview.org) is the official USPTO data platform
maintained by the USPTO and the Institute for Progress. It provides
structured, parsed data for every US patent granted since 1976.

Why PatentsView instead of Lens.org?
  Lens.org returns applicant data where the city is buried in an unstructured
  address string and is often missing. PatentsView returns inventor addresses
  as clean, parsed fields (inventor_city, inventor_state, inventor_country),
  making geocoding reliable and straightforward.

  PatentsView is also US-only, which means every record in our corpus will
  have inventor location data — no records with blank city fields.

API documentation:
  https://search.patentsview.org/docs/

Registration:
  A free API key is required. Register at:
  https://patentsview.org/apis/keyrequest

  Set PATENTSVIEW_API_KEY in .env

Query strategy:
  We search the `patent_abstract` and `patent_title` fields for each keyword
  using the `_text_any` operator, which performs a full-text OR search across
  the specified fields. Multiple keyword groups are combined with `_or`.

  Year filtering uses the `patent_year` field with `_gte` / `_lte`.

Reference for corpus keyword strategy:
  Shapira, Kwon & Youtie (2017) "Tracking the emergence of synthetic biology."
  Scientometrics 112(3), pp. 1457–1478.
"""

from __future__ import annotations
import os
import time
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

PATENTSVIEW_BASE = "https://search.patentsview.org/api/v1/patent/"

# Fields to request from the API.
# Full reference: https://search.patentsview.org/docs/
_FIELDS = [
    "patent_id",
    "patent_title",
    "patent_abstract",
    "patent_date",
    "patent_year",
    "inventors.inventor_city",
    "inventors.inventor_state",
    "inventors.inventor_country",
    "assignees.assignee_city",
    "assignees.assignee_state",
    "assignees.assignee_country",
    "assignees.assignee_organization",
    "ipcr_classifications.ipcr_classification_ipc_class",
    "ipcr_classifications.ipcr_classification_subclass",
]


def search_patents(
    keywords: list[str],
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 2000,
    per_page: int = 100,
    retrieval_reason: str = "keyword",
) -> list[dict]:
    """
    Search PatentsView for US patents matching keywords.

    Keywords are searched across patent_abstract and patent_title using
    a full-text OR match. Multiple keywords in the list are combined
    with a single _text_any query so they are treated as alternatives
    (i.e. any keyword can match).

    Parameters
    ----------
    keywords        : list of search terms (any one can match)
    year_min        : earliest patent grant year (inclusive)
    year_max        : latest patent grant year (inclusive)
    max_results     : maximum total results to retrieve
    per_page        : results per page (PatentsView max is 1000)
    retrieval_reason: label attached to each record for corpus tracking

    Returns
    -------
    List of raw patent dicts from the API, each with a `retrieval_reason`
    field injected. Pass these to extract_fields() for normalization.
    """
    api_key = os.getenv("PATENTSVIEW_API_KEY", "")
    if not api_key or api_key == "your_patentsview_api_key_here":
        raise EnvironmentError(
            "PATENTSVIEW_API_KEY is not configured. Open .env and set it. "
            "Get a free key at https://patentsview.org/apis/keyrequest"
        )

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    # Build the keyword query.
    # _text_any searches for any of the space-separated words across the
    # listed fields. We join multiple keywords with spaces so that any
    # keyword phrase triggers a match.
    #
    # Note: PatentsView full-text search does not support phrase matching
    # (quoted phrases) for multi-word terms. Each word is matched
    # independently. To keep precision high we use the same multi-layer
    # keyword strategy as the rest of the corpus (see 02_ingest_patents.py):
    # layer 1 uses narrow, self-identifying terms; layer 2 uses broader
    # enabling-technology terms.
    keyword_string = " ".join(keywords)
    keyword_clause: dict[str, Any] = {
        "_text_any": {
            "patent_abstract": keyword_string,
            "patent_title": keyword_string,
        }
    }

    # Combine keyword clause with optional year range.
    # _and requires all sub-clauses to match.
    clauses: list[dict] = [keyword_clause]

    if year_min is not None:
        clauses.append({"_gte": {"patent_year": year_min}})
    if year_max is not None:
        clauses.append({"_lte": {"patent_year": year_max}})

    if len(clauses) == 1:
        query = clauses[0]
    else:
        query = {"_and": clauses}

    results: list[dict] = []
    page = 1

    while len(results) < max_results:
        batch_size = min(per_page, max_results - len(results))

        payload = {
            "q": query,
            "f": _FIELDS,
            "o": {
                "per_page": batch_size,
                "page": page,
            },
        }

        # Retry on rate-limit (429) with exponential backoff.
        max_retries = 5
        backoff = 30
        response = None

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    PATENTSVIEW_BASE,
                    json=payload,
                    headers=headers,
                    timeout=30,
                )
                if response.status_code == 429:
                    wait = backoff * (2 ** attempt)
                    logger.warning(
                        f"Rate limited (429). Waiting {wait}s "
                        f"(retry {attempt + 1}/{max_retries})..."
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

        if len(results) >= total or len(batch) < batch_size:
            break

        page += 1
        time.sleep(1.0)  # polite delay between pages

    return results


def extract_fields(patent: dict) -> dict:
    """
    Pull the fields we care about from a raw PatentsView patent object.

    Returns a flat dict ready for normalize.normalize_patents_patentsview().

    Location strategy:
      We use the first inventor's city and state/country as the primary
      location. Inventors are the people who actually did the work, and their
      addresses are more reliably tied to where the research was conducted than
      assignee (company) addresses, which may reflect headquarters rather than
      labs.

      For US patents (inventor_country = "US"), we store city + state so the
      geocoding step can construct a precise "City, ST, US" query. For non-US
      inventors, we use city + country.

    IPC classification:
      The top-level IPC class (e.g. "C12") and subclass (e.g. "C12N") are
      stored for downstream analysis. These are not used for corpus filtering
      (PatentsView does not support IPC filtering in keyword searches), but
      they are useful for characterizing the patent's technical domain.
    """
    patent_id = patent.get("patent_id", "")
    title = patent.get("patent_title", "") or ""
    abstract = patent.get("patent_abstract", "") or ""

    year = None
    patent_year = patent.get("patent_year")
    if patent_year:
        try:
            year = int(patent_year)
        except (ValueError, TypeError):
            pass

    # Extract inventor location from the first inventor entry.
    city, state, country = _extract_inventor_location(patent)

    # Extract first assignee organization name (for reference / filtering).
    assignee_org = _extract_assignee_org(patent)

    # Extract IPC codes (top class + subclass from first entry).
    ipc_class, ipc_subclass = _extract_ipc(patent)

    return {
        "patent_id":        f"US{patent_id}" if patent_id else "",
        "title":            title,
        "abstract":         abstract,
        "year":             year,
        "city":             city,
        "state":            state,
        "country":          country,
        "assignee_org":     assignee_org,
        "ipc_class":        ipc_class,
        "ipc_subclass":     ipc_subclass,
        "retrieval_reason": patent.get("retrieval_reason", "keyword"),
    }


def _extract_inventor_location(patent: dict) -> tuple[str, str, str]:
    """
    Return (city, state, country) from the first inventor with a city.

    Loops through inventors until it finds one with a city — some inventors
    have no address data, so the first inventor is not always usable.
    """
    inventors = patent.get("inventors") or []
    for inv in inventors:
        city    = (inv.get("inventor_city")    or "").strip()
        state   = (inv.get("inventor_state")   or "").strip()
        country = (inv.get("inventor_country") or "").strip().upper()
        if city:
            return city, state, country
    return "", "", ""


def _extract_assignee_org(patent: dict) -> str:
    """Return the name of the first assignee organisation, or empty string."""
    assignees = patent.get("assignees") or []
    for asgn in assignees:
        org = (asgn.get("assignee_organization") or "").strip()
        if org:
            return org
    return ""


def _extract_ipc(patent: dict) -> tuple[str, str]:
    """Return (ipc_class, ipc_subclass) from the first IPC classification."""
    ipcr = patent.get("ipcr_classifications") or []
    for entry in ipcr:
        cls    = (entry.get("ipcr_classification_ipc_class")    or "").strip()
        subcls = (entry.get("ipcr_classification_subclass") or "").strip()
        if cls:
            return cls, subcls
    return "", ""
