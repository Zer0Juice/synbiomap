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
  - Parts data: available from the iGEM Parts Registry API at
    http://parts.igem.org/partsdb/

Methodology note:
  iGEM projects are treated as the "student innovation" layer in our model.
  Each project is geo-tagged by the team's institution city.
  Projects are included if they mention relevant keywords in their
  abstract or project description.
"""

from __future__ import annotations
import csv
import io
import logging
import time
from pathlib import Path
from typing import Iterator

import pandas as pd
import requests

logger = logging.getLogger(__name__)

PARTS_REGISTRY_BASE = "http://parts.igem.org/partsdb"
SYNBIOHUB_SPARQL = "https://synbiohub.org/sparql"

# Expected columns in the raw iGEM projects CSV
IGEM_PROJECT_COLUMNS = {
    "team_name": str,
    "year": "Int64",
    "university": str,
    "city": str,
    "country": str,
    "track": str,          # competition track, e.g. "Environment", "Foundational Advance"
    "abstract": str,
    "wiki_url": str,
}

# Expected columns in the raw iGEM parts CSV
IGEM_PARTS_COLUMNS = {
    "part_name": str,      # BioBrick ID, e.g. "BBa_K12345"
    "part_type": str,      # e.g. "Coding", "Promoter", "RBS"
    "short_desc": str,
    "long_desc": str,
    "team_name": str,
    "year": "Int64",
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
    Load iGEM parts registry data from a CSV file.

    Parameters
    ----------
    filepath : path to the raw iGEM parts CSV

    Returns
    -------
    DataFrame with columns matching IGEM_PARTS_COLUMNS (best effort)
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(
            f"iGEM parts file not found at {filepath}.\n"
            "Download it from http://parts.igem.org/partsdb/ "
            "and place it at data/raw/parts/igem_parts.csv"
        )

    df = pd.read_csv(filepath, dtype=str, encoding="utf-8")
    logger.info(f"Loaded {len(df)} iGEM parts from {filepath}")
    return df


def extract_project_fields(row: pd.Series) -> dict:
    """
    Extract and clean fields from a single iGEM project row.

    Returns a flat dict ready to be passed to normalize.py.
    """
    return {
        "igem_team": str(row.get("team_name", "") or ""),
        "title": str(row.get("team_name", "") or ""),  # team name is the best title
        "abstract": str(row.get("abstract", "") or ""),
        "year": _safe_int(row.get("year")),
        "university": str(row.get("university", "") or ""),
        "city": str(row.get("city", "") or "") or None,
        "country": str(row.get("country", "") or "") or None,
        "track": str(row.get("track", "") or ""),
        "wiki_url": str(row.get("wiki_url", "") or ""),
    }


def extract_part_fields(row: pd.Series) -> dict:
    """
    Extract and clean fields from a single iGEM part row.

    Returns a flat dict ready to be passed to normalize.py.
    """
    description = " ".join(filter(None, [
        str(row.get("short_desc", "") or ""),
        str(row.get("long_desc", "") or ""),
    ]))
    return {
        "part_name": str(row.get("part_name", "") or ""),
        "title": str(row.get("part_name", "") or ""),
        "abstract": description,
        "year": _safe_int(row.get("year")),
        "team_name": str(row.get("team_name", "") or ""),
        "part_type": str(row.get("part_type", "") or ""),
    }


def fetch_parts_from_registry(
    max_results: int = 100_000,
    per_page: int = 10_000,
    delay: float = 1.0,
) -> Iterator[dict]:
    """
    Fetch all parts from the iGEM Parts Registry CSV export API.

    The Registry exposes a search interface at parts.igem.org/partsdb/search.cgi.
    We request all parts (q=type:all) in CSV format with pagination.

    Each yielded dict has keys matching IGEM_PARTS_COLUMNS plus:
      - "uses"       : semicolon-separated sub-part names (for composite parts)
      - "group_name" : the submitting team (may differ from "team_name" in older data)
      - "author"     : part author(s)

    Parameters
    ----------
    max_results : stop after this many parts (safety cap)
    per_page    : results per request (Registry default is 10,000)
    delay       : seconds between requests (be polite)

    Note: The Registry API is lightly documented. If the response format
    changes or the endpoint is unavailable, check parts.igem.org for
    current export options. The column names below reflect the format
    observed as of 2024; the "uses" column may be absent in some exports.
    """
    start = 0
    yielded = 0

    while yielded < max_results:
        params = {
            "q": "type:all",
            "return": "csv",
            "start": start,
            "limit": per_page,
        }

        try:
            response = requests.get(
                f"{PARTS_REGISTRY_BASE}/search.cgi",
                params=params,
                timeout=60,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Parts Registry request failed (start={start}): {e}")
            break

        text = response.text.strip()
        if not text:
            break

        reader = csv.DictReader(io.StringIO(text))
        rows_this_page = 0

        for row in reader:
            if yielded >= max_results:
                return

            # Normalize field names — the Registry sometimes uses "group_name"
            # instead of "team_name" and "part_name" vs "name"
            part = {
                "part_name": row.get("part_name") or row.get("name", ""),
                "part_type": row.get("part_type") or row.get("type", ""),
                "short_desc": row.get("short_desc") or row.get("short_description", ""),
                "long_desc": row.get("long_desc") or row.get("description", ""),
                "team_name": row.get("group_name") or row.get("team_name", ""),
                "author": row.get("author", ""),
                "year": row.get("year", ""),
                # "uses" is a semicolon-separated list of sub-part names.
                # Present for composite parts, empty for basic parts.
                "uses": row.get("uses", ""),
            }

            if not part["part_name"]:
                continue  # skip malformed rows

            yield part
            yielded += 1
            rows_this_page += 1

        logger.info(f"Fetched {rows_this_page} parts (total: {yielded})")

        if rows_this_page < per_page:
            break  # last page

        start += per_page
        time.sleep(delay)


def fetch_composition_edges_from_synbiohub(
    limit: int = 10_000,
    max_edges: int = 500_000,
    delay: float = 0.5,
) -> list[dict]:
    """
    Fetch composite-part → sub-part relationships from SynBioHub via SPARQL.

    SynBioHub (synbiohub.org) mirrors the iGEM Parts Registry in SBOL2 format.
    SBOL2 stores part composition explicitly:
      - ComponentDefinition = a part (basic or composite)
      - sbol:component      = links a composite to a Component instance
      - sbol:definition     = links that instance to the sub-part's definition

    We query for all such relationships within the iGEM collection, then strip
    SynBioHub URIs to bare part names (e.g. "BBa_K12345").

    Returns a list of dicts: {"parent": "BBa_K12345", "child": "BBa_B0034"}

    This graph directly encodes which parts depend on (i.e. "cite") which others.
    A composite part that uses a sub-part is analogous to a paper citing a prior
    work — it is a formal dependency on a prior knowledge artifact.

    Reference:
      Madsen et al. (2019) "The SBOL Stack: A Platform for Storing, Publishing,
      and Sharing Synthetic Biology Designs." ACS Synthetic Biology 8(7).
    """
    edges = []
    offset = 0

    # SBOL2 prefixes used by SynBioHub
    query_template = """
PREFIX sbol: <http://sbols.org/v2#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?parent ?child
WHERE {{
  ?parent a sbol:ComponentDefinition .
  ?parent sbol:component ?comp_instance .
  ?comp_instance sbol:definition ?child .
  FILTER(CONTAINS(STR(?parent), "/public/igem/"))
  FILTER(CONTAINS(STR(?child), "/public/igem/"))
  FILTER(CONTAINS(STR(?parent), "BBa_"))
  FILTER(CONTAINS(STR(?child), "BBa_"))
}}
LIMIT {limit}
OFFSET {offset}
"""

    while len(edges) < max_edges:
        query = query_template.format(limit=limit, offset=offset)

        try:
            response = requests.get(
                SYNBIOHUB_SPARQL,
                params={"query": query, "format": "json"},
                headers={"Accept": "application/sparql-results+json"},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"SynBioHub SPARQL request failed (offset={offset}): {e}")
            break
        except ValueError as e:
            logger.error(f"SynBioHub SPARQL response could not be parsed: {e}")
            break

        bindings = data.get("results", {}).get("bindings", [])
        if not bindings:
            break

        for binding in bindings:
            parent_uri = binding.get("parent", {}).get("value", "")
            child_uri = binding.get("child", {}).get("value", "")

            # Extract bare part name from URI:
            # "https://synbiohub.org/public/igem/BBa_K12345/1" → "BBa_K12345"
            parent_name = _extract_part_name_from_uri(parent_uri)
            child_name = _extract_part_name_from_uri(child_uri)

            if parent_name and child_name and parent_name != child_name:
                edges.append({"parent": parent_name, "child": child_name})

        logger.info(f"SynBioHub: fetched {len(bindings)} edges (total: {len(edges)})")

        if len(bindings) < limit:
            break  # last page

        offset += limit
        time.sleep(delay)

    return edges


def build_part_team_edges(parts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a part → team edge list from the parts DataFrame.

    Returns a DataFrame with columns: part_name, team_name, year.
    Rows where team_name is missing are dropped.
    """
    edges = parts_df[["part_name", "team_name", "year"]].copy()
    edges = edges[edges["team_name"].notna() & (edges["team_name"] != "")]
    edges = edges.drop_duplicates(subset=["part_name", "team_name"])
    return edges.reset_index(drop=True)


def _extract_part_name_from_uri(uri: str) -> str:
    """
    Extract a bare BioBrick ID from a SynBioHub URI.

    Example:
      "https://synbiohub.org/public/igem/BBa_K12345/1" → "BBa_K12345"
    """
    parts = [p for p in uri.rstrip("/").split("/") if p.startswith("BBa_")]
    return parts[0] if parts else ""


def _safe_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
