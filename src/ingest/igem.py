"""
igem.py — load and parse iGEM project and parts data.

iGEM (International Genetically Engineered Machine) is a synthetic biology
competition where student teams build projects using standardized biological
parts. Each team produces:
  - A project wiki page describing their work
  - A set of BioBrick parts submitted to the Registry

Data sources:
  - iGEM project metadata: available from the iGEM API or scraped from the
    iGEM website. The community-maintained dataset at
    https://github.com/igemlabs/igem-data provides a cleaned CSV.
  - Parts data: the new iGEM Registry REST API at api.registry.igem.org
    (launched August 2025). No authentication required for read endpoints.

Parts API overview:
  - GET /v1/parts?pageSize=N&page=N  — paginated list of all parts
  - GET /v1/parts/{uuid}/authors     — returns organisationUUID for each author
  - GET /v1/organisations/{uuid}     — returns team name like "ABOA (2025)"
  - GET /v1/parts/{uuid}/composition — sub-part list (composition graph)
  Team matching chain: part → authors → organisationUUID → org name → projects.csv

Methodology note:
  iGEM projects are treated as the "student innovation" layer in our model.
  Each project is geo-tagged by the team's institution city.
  Parts are linked to projects via team name + year, inheriting the project's
  geo data since parts themselves have no location metadata.
"""

from __future__ import annotations
import json
import logging
import time
from pathlib import Path
from typing import Iterator

import pandas as pd
import requests

logger = logging.getLogger(__name__)

REGISTRY_API_BASE = "https://api.registry.igem.org/v1"
REQUEST_DELAY = 3.0    # seconds between requests — the iGEM API allows 200 req/600s (large window),
                       # which works out to 1 request every 3 seconds sustained.

# Expected columns in the raw iGEM projects CSV
IGEM_PROJECT_COLUMNS = {
    "team_name": str,
    "year": "Int64",
    "university": str,
    "city": str,
    "country": str,
    "track": str,     # competition track, e.g. "Environment", "Foundational Advance"
    "abstract": str,
    "wiki_url": str,
}


def load_projects(filepath: str | Path) -> pd.DataFrame:
    """
    Load iGEM project metadata from a CSV file.

    Parameters
    ----------
    filepath : path to the raw iGEM projects CSV

    Returns
    -------
    DataFrame with columns matching IGEM_PROJECT_COLUMNS (best effort)
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(
            f"iGEM projects file not found at {filepath}.\n"
            "Download it from https://github.com/igemlabs/igem-data "
            "or from the iGEM API and place it at data/raw/projects/igem_projects.csv"
        )

    df = pd.read_csv(filepath, dtype=str, encoding="utf-8")
    logger.info(f"Loaded {len(df)} iGEM projects from {filepath}")
    return df


def load_parts(filepath: str | Path) -> pd.DataFrame:
    """
    Load processed iGEM parts from a CSV file.

    Parameters
    ----------
    filepath : path to the processed parts CSV (data/processed/parts.csv)
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(
            f"iGEM parts file not found at {filepath}.\n"
            "Run scripts/03b_fetch_parts.py to fetch parts from the Registry API."
        )
    df = pd.read_csv(filepath, dtype=str, encoding="utf-8")
    logger.info(f"Loaded {len(df)} iGEM parts from {filepath}")
    return df


def extract_project_fields(row: pd.Series) -> dict:
    """
    Extract and clean fields from a single iGEM project row.

    Returns a flat dict ready to be passed to normalize.py.
    """
    # Support both old column names (team_name, abstract, …) and the
    # actual downloaded CSV column names (name, projectAbstract, …).
    team_name = str(row.get("team_name") or row.get("name") or "")
    title     = str(row.get("projectTitle") or row.get("team_name") or row.get("name") or "")
    abstract  = str(row.get("abstract") or row.get("projectAbstract") or "")
    univ      = str(row.get("university") or row.get("institution") or "")
    track     = str(row.get("track") or row.get("section") or row.get("village") or "")
    wiki_url  = str(row.get("wiki_url") or row.get("wikiURL") or "")

    def _safe_float(v):
        try:
            f = float(v)
            return f if f == f else None  # filter NaN
        except (TypeError, ValueError):
            return None

    return {
        "igem_team": team_name,
        "title": title if title else team_name,
        "abstract": abstract,
        "year": _safe_int(row.get("year")),
        "university": univ,
        "city": str(row.get("city", "") or "") or None,
        "country": str(row.get("country", "") or "") or None,
        "lat": _safe_float(row.get("lat")),
        "lon": _safe_float(row.get("lon")),
        "track": track,
        "wiki_url": wiki_url,
    }


def extract_part_fields(part: dict) -> dict:
    """
    Extract and clean fields from a raw part object returned by the Registry API.

    Parameters
    ----------
    part : dict from GET /v1/parts or GET /v1/parts/{uuid}

    Returns a flat dict. team_name, city, lat, lon are not in the API response
    and must be joined from projects.csv after fetching.
    """
    import re

    # Year is not a direct field — derive it from the submission timestamp.
    # audit.created is an ISO 8601 string like "2025-12-09T21:50:38.273Z".
    year = None
    audit_created = (part.get("audit") or {}).get("created", "")
    if audit_created:
        try:
            year = int(audit_created[:4])
        except (ValueError, IndexError):
            pass

    # The source field is free text like:
    #   "Source of the amino acid sequence: A. Dixon et al., doi: https://doi.org/10.1021/..."
    # Extract all DOIs using a regex. Some parts cite multiple papers.
    source_text = part.get("source") or ""
    dois = re.findall(
        r"10\.\d{4,9}/[^\s,;\]\)\">]+",
        source_text,
    )
    # Normalise: strip trailing punctuation that sometimes gets captured
    dois = [d.rstrip(".,;)>\"'") for d in dois]

    return {
        "part_name": part.get("name", ""),          # BioBrick ID, e.g. BBa_K12345
        "part_uuid": part.get("uuid", ""),
        "title": part.get("title") or part.get("name", ""),
        "description": part.get("description", "") or "",
        "part_type": (part.get("type") or {}).get("label", ""),
        "part_role": (part.get("role") or {}).get("label", ""),
        "year": year,
        "source_text": source_text,
        "source_dois": ";".join(dois),              # semicolon-separated DOIs, empty if none
        # team_name, org_uuid filled in by 03b_fetch_parts.py after author lookup
        "team_name": None,
        "org_uuid": None,
    }


def extract_source_dois(source_text: str) -> list[str]:
    """
    Extract DOIs from a free-text source field.

    The Registry stores source citations as unstructured text, e.g.:
      "Source of the amino acid sequence: A. Dixon et al., doi: https://doi.org/10.1021/acschembio.5b00753."

    Returns a list of normalised DOI strings (without https://doi.org/ prefix).
    """
    import re
    raw = re.findall(r"10\.\d{4,9}/[^\s,;\]\)\">]+", source_text)
    return [d.rstrip(".,;)>\"'") for d in raw]


# ---------------------------------------------------------------------------
# API fetch helpers — used by scripts/03b_fetch_parts.py
# ---------------------------------------------------------------------------

def fetch_all_parts(
    cache_file: str | Path,
    page_size: int = 100,
    delay: float = REQUEST_DELAY,
) -> list[dict]:
    """
    Page through all parts in the Registry API and return them as a list.

    Results are cached to cache_file (newline-delimited JSON) so that
    re-runs skip the fetch entirely. Delete the cache file to re-fetch.

    Parameters
    ----------
    cache_file : path to cache file (data/raw/parts/parts_cache.jsonl)
    page_size  : parts per API request (100 is a safe default)
    delay      : seconds between requests

    Returns
    -------
    list of raw part dicts from the API
    """
    cache_file = Path(cache_file)
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        logger.info(f"Loading parts from cache: {cache_file}")
        parts = []
        with open(cache_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    parts.append(json.loads(line))
        logger.info(f"Loaded {len(parts)} parts from cache")
        return parts

    logger.info("Fetching all parts from Registry API (this may take several minutes)…")
    parts = []
    page = 1

    with open(cache_file, "w") as f:
        while True:
            try:
                resp = requests.get(
                    f"{REGISTRY_API_BASE}/parts",
                    params={"pageSize": page_size, "page": page},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as e:
                logger.error(f"Parts fetch failed at page {page}: {e}")
                break

            batch = data.get("data", [])
            if not batch:
                break

            for part in batch:
                f.write(json.dumps(part) + "\n")
                parts.append(part)

            logger.info(f"Page {page}: fetched {len(batch)} parts (total: {len(parts)})")
            page += 1
            time.sleep(delay)

    logger.info(f"Done. Cached {len(parts)} parts to {cache_file}")
    return parts


def _check_rate_limit_headers(headers: dict) -> None:
    """
    Read x-ratelimit-remaining-large and sleep proactively if the large
    bucket is nearly exhausted.

    The iGEM Registry API exposes three rate limit tiers via response headers:
      x-ratelimit-limit-large    : 200 requests
      x-ratelimit-remaining-large: requests left in the current window
      x-ratelimit-reset-large    : seconds until the window resets

    If fewer than 10 requests remain in the large window, we sleep until
    the window resets rather than hammering the API and triggering a 429.
    """
    try:
        remaining = int(headers.get("x-ratelimit-remaining-large", 999))
        reset_in  = int(headers.get("x-ratelimit-reset-large", 0))
    except (ValueError, TypeError):
        return

    if remaining < 10 and reset_in > 0:
        logger.info(
            f"Large rate-limit bucket nearly exhausted "
            f"({remaining} remaining, resets in {reset_in}s) — pausing."
        )
        time.sleep(reset_in + 1)


def _get_with_retry(
    session: requests.Session,
    url: str,
    delay: float = REQUEST_DELAY,
    max_retries: int = 10,
) -> requests.Response | None:
    """
    GET a URL with exponential backoff on 429 (rate limit) responses.

    Waits `delay` seconds before every request. On a 429, checks the
    Retry-After header first (the API sometimes provides this). If absent,
    doubles the wait time up to a 120-second cap. Retries up to max_retries
    times before giving up.

    The iGEM Registry API (NestJS throttler) imposes per-window request
    limits. A 429 means we hit the window limit; the correct response is
    to wait a full window (typically 60s) before resuming, not just a
    few seconds.
    """
    wait = delay
    for attempt in range(max_retries):
        time.sleep(wait)
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                reset_in    = resp.headers.get("x-ratelimit-reset-large")
                if retry_after:
                    wait = float(retry_after) + 1.0
                elif reset_in:
                    wait = float(reset_in) + 1.0
                else:
                    wait = min(wait * 2, 120)
                logger.warning(
                    f"429 rate limit on {url} — "
                    f"waiting {wait:.0f}s (attempt {attempt+1}/{max_retries})"
                )
                time.sleep(wait)
                continue
            _check_rate_limit_headers(resp.headers)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None
    logger.warning(f"Gave up after {max_retries} retries: {url}")
    return None


def fetch_all_orgs(
    cache_file: str | Path,
    page_size: int = 100,
    delay: float = REQUEST_DELAY,
) -> list[dict]:
    """
    Page through all organisations in the Registry and return them as a list.

    Each org object contains:
      - uuid     : org UUID (used to fetch that org's parts)
      - name     : e.g. "NYU-Abu-Dhabi (2025)"
      - link     : e.g. "https://teams.igem.org/5671"
      - team_id  : int extracted from the link (added by this function)
      - team_name: str parsed from name (added by this function)
      - year     : int parsed from name (added by this function)

    There are ~5,900 orgs total, so this takes ~60 API calls — very fast.
    Results are cached so re-runs are instant.
    """
    import re
    cache_file = Path(cache_file)
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        logger.info(f"Loading orgs from cache: {cache_file}")
        with open(cache_file) as f:
            orgs = json.load(f)
        # Guard against old cache format (dict keyed by org UUID).
        # The new format is a list of org objects.
        if isinstance(orgs, dict):
            logger.warning(
                f"orgs_cache.json is in the old dict format — deleting and re-fetching. "
                f"({cache_file})"
            )
            cache_file.unlink()
            orgs = None
        if orgs is not None:
            logger.info(f"Loaded {len(orgs)} orgs from cache")
            return orgs

    logger.info("Fetching all organisations from Registry API…")
    session = requests.Session()
    orgs = []
    page = 1

    while True:
        time.sleep(delay)
        try:
            r = session.get(
                f"{REGISTRY_API_BASE}/organisations",
                params={"pageSize": page_size, "page": page},
                timeout=30,
            )
            if r.status_code == 429:
                reset_in = r.headers.get("x-ratelimit-reset-large",
                           r.headers.get("Retry-After", 60))
                wait = float(reset_in) + 1.0
                logger.warning(f"429 fetching orgs page {page} — waiting {wait:.0f}s")
                time.sleep(wait)
                continue
            _check_rate_limit_headers(r.headers)
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:
            logger.error(f"Orgs fetch failed at page {page}: {e}")
            break

        batch = data.get("data", [])
        if not batch:
            break

        for org in batch:
            link = org.get("link", "")
            m = re.search(r"/(\d+)$", link)
            team_id = int(m.group(1)) if m else None
            team_name, year = parse_org_name(org.get("name", ""))
            org["team_id"]   = team_id
            org["team_name"] = team_name
            org["year"]      = year
            orgs.append(org)

        total = data.get("total", "?")
        logger.info(f"Page {page}: fetched {len(batch)} orgs (total so far: {len(orgs)} / {total})")
        page += 1

        if len(orgs) >= (data.get("total") or 0):
            break

    with open(cache_file, "w") as f:
        json.dump(orgs, f)
    logger.info(f"Done. Cached {len(orgs)} orgs to {cache_file}")
    return orgs


def fetch_org_parts(
    org_uuid: str,
    session: requests.Session,
    page_size: int = 100,
    delay: float = REQUEST_DELAY,
) -> list[dict]:
    """
    Fetch all parts submitted by a single organisation.

    Returns a list of raw part dicts (same schema as the /parts list endpoint).
    Handles pagination automatically — some teams have more than 100 parts.
    """
    parts = []
    page = 1

    while True:
        time.sleep(delay)
        try:
            resp = session.get(
                f"{REGISTRY_API_BASE}/organisations/{org_uuid}/parts",
                params={"pageSize": page_size, "page": page},
                timeout=30,
            )
            if resp.status_code == 429:
                reset_in = resp.headers.get("x-ratelimit-reset-large",
                           resp.headers.get("Retry-After", 60))
                wait = float(reset_in) + 1.0
                logger.warning(f"429 on org {org_uuid} parts — waiting {wait:.0f}s")
                time.sleep(wait)
                continue
            _check_rate_limit_headers(resp.headers)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.warning(f"Could not fetch parts for org {org_uuid}: {e}")
            break

        batch = data.get("data", [])
        parts.extend(batch)

        if len(parts) >= (data.get("total") or 0) or not batch:
            break
        page += 1

    return parts


def fetch_part_composition(
    part_uuid: str,
    session: requests.Session,
    delay: float = REQUEST_DELAY,
) -> list[dict]:
    """
    Fetch the sub-part composition for a composite part.

    Returns a list of component dicts, each containing:
      - componentName : BioBrick ID of the sub-part (e.g. "BBa_J32015")
      - start, end    : position within the composite sequence
      - strand        : "forward" or "reverse"

    An empty list means the part is not composite, or the fetch failed.

    Methodological note:
      Composite → sub-part relationships are analogous to citations: the
      composite part formally depends on and builds upon the sub-part.
      This graph can reveal which foundational parts underpin student work.
    """
    resp = _get_with_retry(session, f"{REGISTRY_API_BASE}/parts/{part_uuid}/composition", delay)
    if resp is None:
        logger.warning(f"Could not fetch composition for part {part_uuid}")
        return []
    return resp.json().get("data", [])


def parse_org_name(org_name: str) -> tuple[str, int | None]:
    """
    Parse an organisation name like "ABOA (2025)" into (team_name, year).

    The Registry stores team names with the competition year in parentheses.
    This function separates them for matching against projects.csv.

    Examples:
      "ABOA (2025)"     → ("ABOA", 2025)
      "MIT (2019)"      → ("MIT", 2019)
      "OldTeamNoYear"   → ("OldTeamNoYear", None)
    """
    import re
    m = re.match(r"^(.+?)\s*\((\d{4})\)\s*$", org_name.strip())
    if m:
        return m.group(1).strip(), int(m.group(2))
    return org_name.strip(), None


def _safe_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
