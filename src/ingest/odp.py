"""
odp.py — fetch US patents from the USPTO Open Data Portal (ODP) API.

The ODP is the official USPTO data platform (api.uspto.gov). It replaced the
old PatentsView and Lens.org workflows as the authoritative programmatic source
for US patent bibliographic data.

API spec: API-docs/odp-swagger.yaml
Getting started: https://data.uspto.gov/apis/getting-started

Authentication:
  All requests require an ODP API key in the X-API-KEY header.
  Set USPTO_ODP_KEY in .env. Get a free key at the link above.

Search strategy:
  The `q` parameter accepts boolean operators (AND, OR, NOT), wildcards (*),
  and exact phrases ("..."). We phrase-match each keyword and combine with OR.
  Results are filtered to granted utility patents via:
    - filters:      applicationMetaData.applicationTypeCode UTL
    - rangeFilters: applicationMetaData.grantDate YYYY-MM-DD:YYYY-MM-DD

  Limiting to utility patents (UTL) excludes design and plant patents, which
  are not relevant to synthetic biology research activity. Only applications
  with a grantDate are included (i.e. issued patents, not pending applications).

Coverage:
  The ODP only covers US patent applications filed on or after 2001-01-01.
  Pre-2001 patents are not available through this API.

Data limitation — no abstract text:
  The ODP Patent File Wrapper API returns bibliographic metadata only; it does
  not expose patent abstract text. The title (inventionTitle) is used as the
  text field for embedding. This is a known trade-off vs. Lens.org, which
  returned abstracts. If richer text is needed later, patent grant XMLs are
  accessible via the grantDocumentMetaData.fileLocationURI field.

Location strategy:
  Inventor addresses are preferred over applicant (assignee) addresses because
  they reflect where the research was conducted rather than where the company
  is headquartered (Breschi & Lissoni, 2001, doi:10.1093/icc/10.4.975).
  We use the first inventor entry with a non-empty city.
"""

from __future__ import annotations
import os
import time
import logging
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

ODP_SEARCH_URL = "https://api.uspto.gov/api/v1/patent/applications/search"


def search_patents(
    keywords: list[str],
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 2000,
    per_page: int = 25,
    retrieval_reason: str = "keyword",
) -> list[dict]:
    """
    Search the USPTO ODP for US granted utility patents matching keywords.

    Keywords are phrase-matched across all indexed metadata fields (including
    inventionTitle). Multiple keywords are combined with OR so that any single
    keyword phrase triggers inclusion. Results are filtered to utility patents
    that have a recorded grant date, i.e. issued patents only.

    Parameters
    ----------
    keywords        : list of search terms; each is treated as an exact phrase
    year_min        : earliest grant year (inclusive); defaults to 2001
    year_max        : latest grant year (inclusive); defaults to current year
    max_results     : stop after this many patents
    per_page        : results per request (ODP max is 25)
    retrieval_reason: label attached to each record for corpus tracking

    Returns
    -------
    List of raw patent dicts from the ODP. Each dict has an extra
    `retrieval_reason` field injected. Pass to extract_fields() before
    normalising.
    """
    api_key = os.getenv("USPTO_ODP_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "USPTO_ODP_KEY is not set. Add it to .env. "
            "Get a free key at https://data.uspto.gov/apis/getting-started"
        )

    headers = {"X-API-KEY": api_key}

    # Phrase-match each keyword; combine with OR.
    # E.g. ["synthetic biology", "genetic circuit"]
    #   → '"synthetic biology" OR "genetic circuit"'
    keyword_query = " OR ".join(f'"{kw}"' for kw in keywords)

    # Grant date range — ensures we only retrieve issued (granted) patents.
    # The ODP only covers applications from 2001, so that is the floor.
    grant_from = f"{year_min}-01-01" if year_min else "2001-01-01"
    grant_to   = f"{year_max}-12-31" if year_max else "2099-12-31"

    results: list[dict] = []
    offset = 0

    while len(results) < max_results:
        batch_size = min(per_page, max_results - len(results))

        params: dict = {
            "q":           keyword_query,
            # Utility patents only — excludes design (DES) and plant (PLT).
            "filters":     "applicationMetaData.applicationTypeCode UTL",
            # Only include applications that have been granted within the window.
            "rangeFilters": f"applicationMetaData.grantDate {grant_from}:{grant_to}",
            "offset":      offset,
            "limit":       batch_size,
        }

        max_retries = 5
        backoff = 30
        response = None

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    ODP_SEARCH_URL,
                    params=params,
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
                if response.status_code == 404:
                    # 404 means no results for this query, not a server error.
                    logger.info("ODP: no results found for query.")
                    return results
                response.raise_for_status()
                break
            except requests.RequestException as e:
                logger.error(f"ODP request failed: {e}")
                response = None
                break

        if response is None or not response.ok:
            logger.error("ODP: giving up after retries or request error.")
            break

        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to parse ODP response: {e}")
            break

        batch = data.get("patentFileWrapperDataBag") or []
        if not batch:
            break

        for patent in batch:
            patent["retrieval_reason"] = retrieval_reason

        results.extend(batch)
        total = data.get("count", 0)
        logger.info(f"ODP: retrieved {len(results)} / {min(total, max_results)}")

        if offset + len(batch) >= total or len(batch) < batch_size:
            break

        offset += len(batch)
        time.sleep(1.0)  # polite delay between pages; reduces 429 risk

    return results


def extract_fields(patent: dict) -> dict:
    """
    Pull the fields we care about from a raw ODP patent application object.

    Returns a flat dict ready for normalize.normalize_patents_odp().

    Field paths confirmed against the live API (GET /api/v1/patent/applications/{id}):
      applicationNumberText                → application number (always present)
      applicationMetaData.patentNumber     → issued patent number (present if granted)
      applicationMetaData.inventionTitle   → patent title
      applicationMetaData.grantDate        → grant date (YYYY-MM-DD)
      applicationMetaData.inventorBag      → list of inventor records with addresses
    """
    meta        = patent.get("applicationMetaData", {})
    app_number  = patent.get("applicationNumberText", "") or ""
    patent_num  = meta.get("patentNumber", "") or ""
    title       = meta.get("inventionTitle", "") or ""

    year = None
    grant_date = meta.get("grantDate", "")
    if grant_date:
        try:
            year = int(grant_date[:4])
        except (ValueError, TypeError):
            pass

    city, country = _extract_inventor_location(meta)

    return {
        "patent_id":        f"US{patent_num}" if patent_num else f"USapp{app_number}",
        "title":            title,
        "year":             year,
        "city":             city,
        "country":          country,
        "retrieval_reason": patent.get("retrieval_reason", "keyword"),
    }


def _extract_inventor_location(meta: dict) -> tuple[str, str]:
    """
    Return (city, country) from the first inventor with a non-empty city.

    Loops through all inventors and their address entries until a city is
    found. Country comes from countryCode (alpha-2) or countryName as fallback.
    """
    for inv in (meta.get("inventorBag") or []):
        for addr in (inv.get("correspondenceAddressBag") or []):
            city = (addr.get("cityName") or "").strip()
            if not city:
                continue
            # ODP may return countryCode (alpha-2), countryName, or country
            country = (
                addr.get("countryCode")
                or addr.get("country")
                or addr.get("countryName")
                or ""
            ).strip()
            return city, country

    return "", ""
