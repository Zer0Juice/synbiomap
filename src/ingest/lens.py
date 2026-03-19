"""
lens.py — fetch patents from the Lens.org API.

Lens.org is a free patent and scholarly search platform.
Patent retrieval requires a free API token (set LENS_API_TOKEN in .env).

API documentation: https://docs.api.lens.org/

Methodology note:
  Patents are searched by keyword in title, abstract, and claims.
  We focus on granted patents and published applications.
  The Cooperative Patent Classification (CPC) code C12N is often used for
  synthetic biology-related patents, but keyword search gives broader coverage.
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
    year_min: int | None = None,
    year_max: int | None = None,
    max_results: int = 2000,
    per_page: int = 100,
) -> list[dict]:
    """
    Search Lens.org for patents matching any of the given keywords.

    Returns a list of raw Lens patent objects.
    The caller should normalize them via normalize.py.

    Parameters
    ----------
    keywords : list of strings to search for in title/abstract/claims
    year_min : earliest application year (inclusive)
    year_max : latest application year (inclusive)
    max_results : stop after retrieving this many patents
    per_page : number of results per request (max 100 for Lens)
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

    # Build the query: keyword match in title, abstract, or claims
    keyword_clause = " OR ".join(f'"{kw}"' for kw in keywords)

    must_clauses = [
        {"query_string": {"query": keyword_clause, "fields": ["title", "abstract", "claims.text"]}}
    ]

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
    # Title may be a list of objects with language codes
    title = _extract_title(patent)
    abstract = _extract_abstract(patent)

    # Applicants (organizations that filed the patent) often carry location
    city, country = _extract_location(patent)

    year = None
    date_pub = patent.get("date_published", "")
    if date_pub:
        try:
            year = int(date_pub[:4])
        except (ValueError, TypeError):
            pass

    return {
        "lens_id": patent.get("lens_id", ""),
        "title": title,
        "abstract": abstract,
        "year": year,
        "city": city,
        "country": country,
    }


def _extract_title(patent: dict) -> str:
    title = patent.get("title", "")
    if isinstance(title, list):
        # Pick English title if available, otherwise first
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

    Lens.org applicant objects may have a "residence" or "address" field.
    """
    for applicant in patent.get("applicants", []):
        residence = applicant.get("residence", {})
        country = residence.get("country_code") or applicant.get("country_code")
        city = residence.get("city") or applicant.get("city")
        if country:
            return city, country
    return None, None
