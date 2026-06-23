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
import re
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


# ---------------------------------------------------------------------------
# Lookup-by-number helpers (used for geocoding an external patent list, e.g.
# Oldham & Hall's synthetic-biology landscape, where we have patent numbers
# but no inventor addresses). These complement the keyword search above.
# ---------------------------------------------------------------------------

def extract_all_inventor_locations(meta: dict) -> list[dict]:
    """
    Return a location record for EVERY inventor on the patent, in listed order.

    Each record is {"name", "city", "state", "country"}. Inventors with no
    usable city are still returned (with empty city) so the caller can count
    total vs. located inventors and compute fractional weights honestly.

    Why all inventors, not just the first?
      The first-listed inventor is only a weak proxy for the "lead" — the USPTO
      does not require inventors to be ordered by contribution. For a city-level
      study, assigning the whole patent to the first inventor's city biases the
      geography of multi-city collaborations (common in academic synthetic
      biology). Capturing every inventor lets the analysis use fractional
      counting (each patent contributes a total weight of 1, split across the
      cities of its inventors), which is the standard in regional patent
      statistics (OECD REGPAT methodology) and keeps city totals additive.

    State (geographicRegionCode) is kept because many US city names repeat
    across states, so "City, ST, US" geocodes far more reliably than "City, US".
    For non-US inventors the state is usually empty and the country carries the
    disambiguating information instead.
    """
    locations: list[dict] = []
    for inv in (meta.get("inventorBag") or []):
        name = (inv.get("inventorNameText") or "").strip()
        city = state = country = ""
        for addr in (inv.get("correspondenceAddressBag") or []):
            c = (addr.get("cityName") or "").strip()
            if not c:
                continue
            city = c
            state = (addr.get("geographicRegionCode") or "").strip()
            country = (
                addr.get("countryCode")
                or addr.get("country")
                or addr.get("countryName")
                or ""
            ).strip()
            break
        locations.append({
            "name": name, "city": city, "state": state, "country": country,
        })
    return locations


def extract_patent_record(patent: dict) -> dict:
    """
    Flatten a raw ODP search result into a record ready for enrichment.

    Unlike extract_fields() (which keeps only the FIRST inventor's city and
    drops everything else), this keeps EVERY inventor's location and the link
    to the patent's grant XML, so the caller can do all-inventor (fractional)
    geocoding and fetch the abstract. The default ODP search response already
    includes inventorBag and grantDocumentMetaData, so no extra API call is
    needed at this stage — only the later abstract download.

    Returns a dict: patent_id, number, title, year, locations (list from
    extract_all_inventor_locations), file_uri (grant XML link), abstract
    (empty, filled later), retrieval_reason.
    """
    meta = patent.get("applicationMetaData", {}) or {}
    num = str(meta.get("patentNumber") or "").strip()
    title = meta.get("inventionTitle", "") or ""

    year = None
    grant_date = meta.get("grantDate", "") or ""
    if grant_date[:4].isdigit():
        year = int(grant_date[:4])

    gdoc = patent.get("grantDocumentMetaData", {}) or {}
    return {
        "patent_id":        f"US{num}" if num else "",
        "number":           num,
        "title":            title,
        "year":             year,
        "locations":        extract_all_inventor_locations(meta),
        "file_uri":         gdoc.get("fileLocationURI", ""),
        "abstract":         "",
        "retrieval_reason": patent.get("retrieval_reason", "keyword"),
    }


def lookup_patents_by_number(
    patent_numbers: list[str],
    batch_size: int = 20,
    delay: float = 1.0,
) -> dict[str, dict]:
    """
    Look up USPTO patents by their grant number and return inventor metadata.

    Used when we already have a list of US patent numbers (e.g. extracted from
    another dataset's patent families) and want the inventor addresses that the
    source dataset does not provide.

    Patent numbers must be the bare grant number with no "US" prefix and no
    kind code — e.g. "8153432", not "US8153432B2". The caller is responsible
    for normalising them (see scripts/geocode_oldham_patents.py).

    Numbers are queried in batches using an OR group on the
    `applicationMetaData.patentNumber` field:
        applicationMetaData.patentNumber:(8153432 OR 9121036 OR ...)
    This keeps the number of HTTP requests low (one request per `batch_size`
    numbers) while respecting the ODP per-request result limit.

    Note: the ODP only covers applications filed on or after 2001-01-01, so
    patents granted from older (pre-2001) filings will simply not be found and
    are silently absent from the returned mapping.

    Parameters
    ----------
    patent_numbers : list of bare grant numbers (strings of digits)
    batch_size     : how many numbers to OR together per request
    delay          : polite delay (seconds) between requests

    Returns
    -------
    dict mapping patentNumber (str) -> applicationMetaData dict for every
    number the ODP could resolve. Numbers not found are absent from the dict.
    """
    api_key = os.getenv("USPTO_ODP_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "USPTO_ODP_KEY is not set. Add it to .env. "
            "Get a free key at https://data.uspto.gov/apis/getting-started"
        )

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    fields = [
        "applicationNumberText",
        "applicationMetaData.patentNumber",
        "applicationMetaData.inventionTitle",
        "applicationMetaData.grantDate",
        "applicationMetaData.inventorBag",
    ]

    # De-duplicate while preserving order so the cache/lookup is stable.
    unique_numbers = list(dict.fromkeys(n for n in patent_numbers if n))
    resolved: dict[str, dict] = {}

    for start in range(0, len(unique_numbers), batch_size):
        batch = unique_numbers[start:start + batch_size]
        or_group = " OR ".join(batch)
        payload = {
            "q": f"applicationMetaData.patentNumber:({or_group})",
            "fields": fields,
            # Allow a little headroom in case a number maps to >1 record.
            "pagination": {"offset": 0, "limit": batch_size + 5},
        }

        max_retries = 5
        backoff = 30
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    ODP_SEARCH_URL, json=payload, headers=headers, timeout=30
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
                    response = None  # no matches in this batch
                    break
                response.raise_for_status()
                break
            except requests.RequestException as e:
                logger.error(f"ODP lookup request failed: {e}")
                response = None
                break

        if response is not None and response.ok:
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"Failed to parse ODP lookup response: {e}")
                data = {}
            for wrapper in (data.get("patentFileWrapperDataBag") or []):
                meta = wrapper.get("applicationMetaData", {}) or {}
                num = str(meta.get("patentNumber") or "").strip()
                if num:
                    resolved[num] = meta

        done = min(start + batch_size, len(unique_numbers))
        logger.info(f"ODP lookup: {done}/{len(unique_numbers)} numbers queried, "
                    f"{len(resolved)} resolved")
        time.sleep(delay)

    return resolved


# ---------------------------------------------------------------------------
# Abstract retrieval.
#
# The ODP bibliographic API does NOT return abstract text — only the title.
# But each granted patent's record carries grantDocumentMetaData.fileLocationURI,
# a link to the patent's individual grant XML in the USPTO bulk dataset
# (product PTGRXML-SPLT). That XML contains the full <abstract>. We fetch and
# parse it here so the corpus can be embedded on abstracts, not titles alone.
#
# Flow per patent:
#   1. lookup_grant_documents()  -> grantDocumentMetaData.fileLocationURI
#   2. fetch_grant_xml()         -> GET the URI; ODP 302-redirects to a signed
#                                   data.uspto.gov URL which serves the raw XML
#   3. extract_abstract_from_grant_xml() -> plain-text abstract
# ---------------------------------------------------------------------------

_ABSTRACT_RE = re.compile(r"<abstract\b[^>]*>(.*?)</abstract>", re.S | re.I)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def lookup_grant_documents(
    patent_numbers: list[str],
    batch_size: int = 20,
    delay: float = 1.0,
) -> dict[str, dict]:
    """
    Return {patentNumber: {"app_number", "title", "grant_date", "file_uri"}}.

    `file_uri` is grantDocumentMetaData.fileLocationURI — the link to the
    patent's grant XML, needed by fetch_grant_xml() to retrieve the abstract.
    Patent numbers must be bare grant numbers (no "US" prefix, no kind code).
    Same batched OR-query strategy as lookup_patents_by_number().
    """
    api_key = os.getenv("USPTO_ODP_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "USPTO_ODP_KEY is not set. Add it to .env. "
            "Get a free key at https://data.uspto.gov/apis/getting-started"
        )

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    fields = [
        "applicationNumberText",
        "applicationMetaData.patentNumber",
        "applicationMetaData.inventionTitle",
        "applicationMetaData.grantDate",
        "grantDocumentMetaData",
    ]
    unique_numbers = list(dict.fromkeys(n for n in patent_numbers if n))
    out: dict[str, dict] = {}

    for start in range(0, len(unique_numbers), batch_size):
        batch = unique_numbers[start:start + batch_size]
        payload = {
            "q": f"applicationMetaData.patentNumber:({' OR '.join(batch)})",
            "fields": fields,
            "pagination": {"offset": 0, "limit": batch_size + 5},
        }

        max_retries, backoff, response = 5, 30, None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    ODP_SEARCH_URL, json=payload, headers=headers, timeout=30
                )
                if response.status_code == 429:
                    wait = backoff * (2 ** attempt)
                    logger.warning(f"Rate limited (429). Waiting {wait}s "
                                   f"(retry {attempt + 1}/{max_retries})...")
                    time.sleep(wait)
                    continue
                if response.status_code == 404:
                    response = None
                    break
                response.raise_for_status()
                break
            except requests.RequestException as e:
                logger.error(f"ODP grant-doc lookup failed: {e}")
                response = None
                break

        if response is not None and response.ok:
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"Failed to parse grant-doc response: {e}")
                data = {}
            for w in (data.get("patentFileWrapperDataBag") or []):
                meta = w.get("applicationMetaData", {}) or {}
                num = str(meta.get("patentNumber") or "").strip()
                if not num:
                    continue
                gdoc = w.get("grantDocumentMetaData", {}) or {}
                out[num] = {
                    "app_number": w.get("applicationNumberText", ""),
                    "title":      meta.get("inventionTitle", ""),
                    "grant_date": meta.get("grantDate", ""),
                    "file_uri":   gdoc.get("fileLocationURI", ""),
                }

        done = min(start + batch_size, len(unique_numbers))
        logger.info(f"Grant-doc lookup: {done}/{len(unique_numbers)} queried, "
                    f"{len(out)} with metadata")
        time.sleep(delay)

    return out


def fetch_grant_xml(file_uri: str, timeout: int = 60) -> str | None:
    """
    Download a patent's grant XML from its fileLocationURI.

    The ODP endpoint responds with a 302 redirect to a signed data.uspto.gov
    URL; requests follows it automatically. Returns the XML text, or None if
    the download failed or did not return XML.
    """
    if not file_uri:
        return None
    api_key = os.getenv("USPTO_ODP_KEY", "")
    headers = {"X-API-KEY": api_key}
    try:
        r = requests.get(file_uri, headers=headers, allow_redirects=True, timeout=timeout)
    except requests.RequestException as e:
        logger.warning(f"Grant XML download failed for {file_uri}: {e}")
        return None
    if r.ok and r.text.lstrip()[:5].lower() == "<?xml":
        return r.text
    logger.warning(f"Grant XML not returned (HTTP {r.status_code}) for {file_uri}")
    return None


def extract_abstract_from_grant_xml(xml: str | None) -> str:
    """
    Return the plain-text abstract from a us-patent-grant XML document.

    Strips inner markup (<p>, <sub>, formulas, etc.) and collapses whitespace.
    Returns "" if the document has no abstract (e.g. some older grants).
    """
    if not xml:
        return ""
    m = _ABSTRACT_RE.search(xml)
    if not m:
        return ""
    return _WS_RE.sub(" ", _TAG_RE.sub(" ", m.group(1))).strip()
