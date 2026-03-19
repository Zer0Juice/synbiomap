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
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

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


def _safe_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
