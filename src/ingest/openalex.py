"""
openalex.py — fetch academic papers from the OpenAlex API.

OpenAlex is a free, open index of scholarly works.
API documentation: https://docs.openalex.org/

Authentication (both optional, set in .env):
  OPENALEX_EMAIL   — enables the "polite pool" for faster response times
  OPENALEX_API_KEY — free account key from openalex.org; grants 10,000
                     filtered queries/day and 1,000 full-text searches/day.
                     Passed as the `api_key` query parameter.

Methodology note:
  We retrieve papers by searching for synthetic biology keywords in titles
  and abstracts. We then expand the corpus using citation links to capture
  related work that may not use the exact same keywords.
  See: Waltman & van Eck (2012) for discussion of keyword vs. citation-based
       corpus construction in bibliometrics.
"""

from __future__ import annotations
import os
import time
import logging
from typing import Iterator
import requests

logger = logging.getLogger(__name__)

OPENALEX_BASE = "https://api.openalex.org"


def _get_auth() -> tuple[dict, dict]:
    """
    Return (headers, auth_params) for OpenAlex requests.

    - Email in User-Agent enables the polite pool (faster responses).
    - api_key as a query parameter grants higher daily rate limits.
      Both are optional; either, both, or neither can be set.
    """
    email = os.getenv("OPENALEX_EMAIL", "")
    api_key = os.getenv("OPENALEX_API_KEY", "")

    headers = {"User-Agent": f"mailto:{email}"} if email else {}
    auth_params = {"api_key": api_key} if api_key else {}

    return headers, auth_params


def search_papers(
    keywords: list[str],
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 5000,
    per_page: int = 200,
    retrieval_reason: str = "keyword",
) -> Iterator[dict]:
    """
    Search OpenAlex for papers matching any of the given keywords.

    Yields raw OpenAlex work objects (dicts) one at a time, with a
    `retrieval_reason` field injected so the caller can track which layer
    of the corpus construction strategy found each paper.

    Parameters
    ----------
    keywords        : strings to search for in title/abstract (any match)
    year_min        : earliest publication year (inclusive)
    year_max        : latest publication year (inclusive)
    max_results     : stop after yielding this many results
    per_page        : results per API request (max 200 for OpenAlex)
    retrieval_reason: label injected into each result dict, e.g.
                      "core_keyword", "subfield_keyword", "citation_expansion"
    """
    # Build the filter string (OpenAlex uses a custom filter syntax)
    # We search title_and_abstract for any of the keywords
    keyword_filter = "|".join(keywords)
    filters = [f"title_and_abstract.search:{keyword_filter}"]

    if year_min:
        filters.append(f"publication_year:>{year_min - 1}")
    if year_max:
        filters.append(f"publication_year:<{year_max + 1}")

    filter_str = ",".join(filters)

    headers, auth_params = _get_auth()

    params = {
        "filter": filter_str,
        "per-page": per_page,
        "cursor": "*",  # cursor-based pagination for large result sets
        **auth_params,
    }

    yielded = 0

    logger.info(f"Starting OpenAlex search with filter: {filter_str}")

    while yielded < max_results:
        try:
            response = requests.get(
                f"{OPENALEX_BASE}/works",
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"OpenAlex request failed: {e}")
            break

        results = data.get("results", [])
        if not results:
            break

        for work in results:
            if yielded >= max_results:
                return
            work["retrieval_reason"] = retrieval_reason
            yield work
            yielded += 1

        # Move to the next page using the cursor
        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor:
            break
        params["cursor"] = next_cursor

        # Be polite: small delay between requests
        time.sleep(0.1)

    logger.info(f"OpenAlex search complete. Retrieved {yielded} works.")


def get_citing_works(
    work_id: str,
    max_results: int = 500,
) -> Iterator[dict]:
    """
    Fetch works that cite a given OpenAlex work ID.

    This is used for citation-based corpus expansion: once we have a seed
    set of relevant papers, we can retrieve their citers to find related
    work published later.

    Parameters
    ----------
    work_id : OpenAlex work ID, e.g. "W2741809807"
    max_results : maximum number of citing works to return
    """
    headers, auth_params = _get_auth()

    params = {
        "filter": f"cites:{work_id}",
        "per-page": 200,
        "cursor": "*",
        **auth_params,
    }

    yielded = 0

    while yielded < max_results:
        try:
            response = requests.get(
                f"{OPENALEX_BASE}/works",
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"OpenAlex cites request failed: {e}")
            break

        for work in data.get("results", []):
            if yielded >= max_results:
                return
            yield work
            yielded += 1

        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor:
            break
        params["cursor"] = next_cursor
        time.sleep(0.1)


def get_referenced_work_ids(work_id: str) -> list[str]:
    """
    Return the list of OpenAlex IDs that a given paper cites (backward snowball).

    OpenAlex stores these as full URLs like "https://openalex.org/W123".
    We strip them to bare IDs like "W123" for use in batch fetching.

    Parameters
    ----------
    work_id : an OpenAlex work ID, e.g. "W2741809807"
    """
    headers, auth_params = _get_auth()
    try:
        response = requests.get(
            f"{OPENALEX_BASE}/works/{work_id}",
            params=auth_params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch work {work_id}: {e}")
        return []

    raw_ids = data.get("referenced_works", [])
    # Strip URL prefix to get bare IDs: "https://openalex.org/W123" → "W123"
    return [r.split("/")[-1] for r in raw_ids if r]


def fetch_works_by_ids(
    work_ids: list[str],
    retrieval_reason: str = "citation_expansion",
    batch_size: int = 50,
) -> Iterator[dict]:
    """
    Fetch full work objects for a list of OpenAlex IDs.

    OpenAlex supports filtering by up to ~50 IDs per request using
    `filter=ids.openalex:W1|W2|W3`. We chunk the list and page through it.

    Used for both backward snowballing (fetch the papers a seed cites) and
    as a complement to the forward snowball in get_citing_works().

    Parameters
    ----------
    work_ids        : list of bare OpenAlex IDs, e.g. ["W123", "W456"]
    retrieval_reason: label injected into each yielded work dict
    batch_size      : IDs per request (keep ≤ 50 to stay within URL limits)
    """
    headers, auth_params = _get_auth()

    for i in range(0, len(work_ids), batch_size):
        chunk = work_ids[i : i + batch_size]
        id_filter = "|".join(chunk)

        params = {
            "filter": f"ids.openalex:{id_filter}",
            "per-page": batch_size,
            **auth_params,
        }

        try:
            response = requests.get(
                f"{OPENALEX_BASE}/works",
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Batch fetch failed for chunk {i}–{i+batch_size}: {e}")
            continue

        for work in data.get("results", []):
            work["retrieval_reason"] = retrieval_reason
            yield work

        time.sleep(0.1)


def extract_fields(work: dict) -> dict:
    """
    Pull the fields we care about from a raw OpenAlex work object.

    Returns a flat dict ready to be passed to normalize.py.
    """
    # Abstract is stored as an inverted index {word: [positions]}
    # We need to reconstruct it in reading order.
    abstract = _reconstruct_abstract(work.get("abstract_inverted_index") or {})

    # Institutions are nested; we take the first affiliated institution's city
    city, country = _extract_location(work)

    return {
        "openalex_id": work.get("id", ""),
        "title": work.get("title", "") or "",
        "abstract": abstract,
        "year": work.get("publication_year"),
        "doi": work.get("doi", ""),
        "city": city,
        "country": country,
    }


def _reconstruct_abstract(inverted_index: dict) -> str:
    """
    OpenAlex stores abstracts as inverted indexes to save space.
    This function reconstructs the original word order.

    Example inverted index: {"carbon": [0, 5], "capture": [1], ...}
    """
    if not inverted_index:
        return ""
    # Build a list of (position, word) pairs, then sort by position
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(word for _, word in word_positions)


def _extract_location(work: dict) -> tuple[str | None, str | None]:
    """
    Extract city and country from the first author's institution.

    OpenAlex institution objects have a "geo" field with city/country.
    We prefer the first author's first institution.
    """
    authorships = work.get("authorships", [])
    for authorship in authorships:
        institutions = authorship.get("institutions", [])
        for inst in institutions:
            geo = inst.get("geo", {})
            city = geo.get("city")
            country = geo.get("country")
            if city or country:
                return city, country
    return None, None
