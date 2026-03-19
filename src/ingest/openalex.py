"""
openalex.py — fetch academic papers from the OpenAlex API.

OpenAlex is a free, open index of scholarly works. No API key is needed,
but providing a "polite pool" email (set OPENALEX_EMAIL in .env) gives
faster response times.

API documentation: https://docs.openalex.org/

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


def _get_headers() -> dict:
    """
    Build request headers. Including an email enables the "polite pool"
    on OpenAlex, which has higher rate limits.
    """
    email = os.getenv("OPENALEX_EMAIL", "")
    if email:
        return {"User-Agent": f"mailto:{email}"}
    return {}


def search_papers(
    keywords: list[str],
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 5000,
    per_page: int = 200,
) -> Iterator[dict]:
    """
    Search OpenAlex for papers matching any of the given keywords.

    Yields raw OpenAlex work objects (dicts) one at a time.
    The caller is responsible for normalizing them via normalize.py.

    Parameters
    ----------
    keywords : list of strings to search for in title/abstract
    year_min : earliest publication year (inclusive)
    year_max : latest publication year (inclusive)
    max_results : stop after yielding this many results
    per_page : number of results per API request (max 200 for OpenAlex)
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

    params = {
        "filter": filter_str,
        "per-page": per_page,
        "cursor": "*",  # cursor-based pagination for large result sets
    }

    headers = _get_headers()
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
    params = {
        "filter": f"cites:{work_id}",
        "per-page": 200,
        "cursor": "*",
    }
    headers = _get_headers()
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
