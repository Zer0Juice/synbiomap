"""
patentsview.py — fetch patents from the PatentsView API.

PatentsView is a free, open-access US patent database maintained by the
USPTO (United States Patent and Trademark Office). No API key is required.
Covers all US-granted patents from 1976 to the present.

API documentation: https://patentsview.org/apis/purpose
Endpoint: POST https://api.patentsview.org/patents/query

Scope limitation:
  PatentsView covers US patents only (USPTO grants). International patents
  filed via PCT or granted by other offices (EPO, JPO, CNIPA, etc.) are
  not included. This introduces a US geographic bias in the patents data.
  The tradeoff is justified for this thesis project: the US is consistently
  the largest single jurisdiction for synthetic biology patents (Oldham &
  Hall, 2018), and the API's openness, free access, and stable schema
  support reproducibility and long-term archival access without credentials.

Corpus construction strategy:
  Synthetic biology has no dedicated IPC/CPC patent classification code.
  We adopt the keyword-layer strategy from van Doren, Koenigstein & Reiss
  (2013, doi:10.1007/s11693-013-9121-7):

    Layer 1 — core self-identifying terms (high precision):
      "synthetic biology", "synthetic genomics", "synthetic genome"

    Layer 2 — subfield/enabling terms (broader coverage):
      "genetic circuit", "gene synthesis", "DNA assembly", "BioBrick", etc.

  Keywords are searched as exact phrases across patent_title and
  patent_abstract using OR logic. IPC subclass codes from the config are
  accepted for API compatibility but are used only for downstream analysis,
  not as query filters — the PatentsView `_text_phrase` operator is more
  reliable for scoping synbio patents than IPC alone, because many synbio
  patents are filed under broad biotechnology classes.

PatentsView query DSL (key operators used here):
  _text_phrase : exact phrase match in a named text field
  _or          : logical OR over a list of clauses
  _and         : logical AND over a list of clauses
  _gte / _lte  : range comparisons (used for patent_date filtering)

Pageable fields returned per patent:
  patent_number        — USPTO patent number (unique identifier)
  patent_title         — full title text
  patent_abstract      — abstract text
  patent_date          — grant date (YYYY-MM-DD)
  assignee_organization— name of the first assignee
  assignee_country     — 2-letter ISO country code of assignee
  assignee_city        — city of assignee
  assignee_state       — US state (where applicable)
  ipc_subclass_id      — IPC subclass (e.g. "C12N") for downstream analysis
"""

from __future__ import annotations
import time
import logging

import requests

logger = logging.getLogger(__name__)

PATENTSVIEW_BASE = "https://api.patentsview.org/patents/query"

# Fields to retrieve per patent (subset of the full PatentsView schema).
# See https://patentsview.org/apis/api-query-language for the full field list.
_FIELDS = [
    "patent_number",
    "patent_title",
    "patent_abstract",
    "patent_date",
    "assignee_organization",
    "assignee_country",
    "assignee_city",
    "assignee_state",
    "ipc_subclass_id",
]


def search_patents(
    keywords: list[str],
    ipc_codes: list[str] | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 2000,
    per_page: int = 500,
    retrieval_reason: str = "keyword",
) -> list[dict]:
    """
    Search PatentsView for US patents matching the given keyword phrases.

    Each keyword is searched as an exact phrase in both patent_title and
    patent_abstract. Multiple keywords are combined with OR logic, so any
    keyword match qualifies a patent for retrieval.

    Parameters
    ----------
    keywords        : list of exact keyword phrases to search for
    ipc_codes       : accepted for API compatibility, but ignored as a filter.
                      The PatentsView API does support IPC filtering, but
                      restricting to IPC codes AND keywords would miss patents
                      assigned to broad biotechnology classes. IPC data IS
                      returned in the response for downstream analysis.
    year_min        : earliest patent grant year to include (inclusive)
    year_max        : latest patent grant year to include (inclusive)
    max_results     : stop after this many patents total
    per_page        : records per API request (PatentsView supports up to 10,000)
    retrieval_reason: label stored on each record to track which layer found it
    """
    # Build the keyword clause: any phrase in title OR abstract qualifies.
    keyword_clauses = []
    for kw in keywords:
        keyword_clauses.append({"_text_phrase": {"patent_title": kw}})
        keyword_clauses.append({"_text_phrase": {"patent_abstract": kw}})

    if len(keyword_clauses) == 1:
        keyword_query: dict = keyword_clauses[0]
    else:
        keyword_query = {"_or": keyword_clauses}

    # Date filter: patent_date is in YYYY-MM-DD format.
    date_clauses: list[dict] = []
    if year_min:
        date_clauses.append({"_gte": {"patent_date": f"{year_min}-01-01"}})
    if year_max:
        date_clauses.append({"_lte": {"patent_date": f"{year_max}-12-31"}})

    if date_clauses:
        query: dict = {"_and": date_clauses + [keyword_query]}
    else:
        query = keyword_query

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
        backoff = 10  # seconds; doubles each retry
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    PATENTSVIEW_BASE,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                )
                if response.status_code == 429:
                    wait = backoff * (2 ** attempt)
                    logger.warning(
                        f"PatentsView rate limit (429). "
                        f"Waiting {wait}s before retry {attempt + 1}/{max_retries}..."
                    )
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                break
            except requests.RequestException as exc:
                logger.error(f"PatentsView request failed: {exc}")
                response = None
                break

        if response is None or not response.ok:
            logger.error("PatentsView: giving up after retries or request error.")
            break

        try:
            data = response.json()
        except Exception as exc:
            logger.error(f"Failed to parse PatentsView response: {exc}")
            break

        batch: list[dict] = data.get("patents") or []
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
        time.sleep(1.0)  # polite delay between pages to avoid rate limits

    return results


def extract_fields(patent: dict) -> dict:
    """
    Pull the fields we care about from a raw PatentsView patent record.

    Returns a flat dict ready to be passed to normalize.py.

    The PatentsView response nests assignees as a list under each patent
    (one patent can have multiple assignees). We take the first assignee
    that has a non-null country code, which matches how the pipeline
    previously handled the Lens.org `residence` field.
    """
    title    = patent.get("patent_title", "") or ""
    abstract = patent.get("patent_abstract", "") or ""

    year = None
    date_str = patent.get("patent_date", "")
    if date_str:
        try:
            year = int(date_str[:4])
        except (ValueError, TypeError):
            pass

    country, city = _extract_location(patent)

    return {
        "patent_number":    patent.get("patent_number", ""),
        "title":            title,
        "abstract":         abstract,
        "year":             year,
        "city":             city,
        "country":          country,
        "retrieval_reason": patent.get("retrieval_reason", "keyword"),
    }


def _extract_location(patent: dict) -> tuple[str | None, str | None]:
    """
    Return (country, city) from the first assignee with location data.

    PatentsView returns assignees as a list of dicts, each containing:
      assignee_country — 2-letter ISO country code (e.g. "US", "DE")
      assignee_city    — city string (may be None for non-US assignees)
      assignee_state   — US state abbreviation (e.g. "MA", "CA")

    We iterate until we find an assignee with a country code, then
    return that country and city. Geocoding (lat/lon) is handled
    downstream by normalize.py and geocode_papers.py.
    """
    assignees = patent.get("assignees") or []
    for assignee in assignees:
        country = assignee.get("assignee_country")
        city    = assignee.get("assignee_city")
        if country:
            return country, city
    return None, None
