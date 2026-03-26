"""
schema.py — shared data schema for all artifact types.

Every dataset (papers, patents, projects, parts) is normalized to this
same set of columns before any analysis. Having a single schema makes it
easy to combine datasets, compare them, and feed them into the embedding
and clustering pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import pandas as pd

# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------

# These are the columns every processed CSV must contain.
# Optional columns may be NaN when not available for a given artifact type.
REQUIRED_COLUMNS = [
    "id",               # Unique identifier (string)
    "type",             # One of: "paper", "patent", "project", "part"
    "title",            # Title of the artifact
    "text",             # Combined title + abstract (used for embedding)
    "year",             # Year of publication/filing/team submission (int)
    # ── Geography ──────────────────────────────────────────────────────────
    # Many artifacts are associated with more than one city (e.g. a paper with
    # authors at MIT and ETH Zurich, or an iGEM team from two universities).
    # We follow a two-level geography model:
    #
    #   city / lat / lon  — PRIMARY location (first/lead institution, or
    #                        corresponding author).  Used as the default for
    #                        single-city analyses, maps, and labelling.
    #
    #   all_cities        — JSON array of ALL geocoded city names for this
    #                        artifact, e.g. ["Cambridge", "Zurich"].
    #                        Includes the primary city as the first entry.
    #
    #   all_coords        — JSON array of [lat, lon] pairs, one per entry in
    #                        all_cities, in the same order.
    #
    # Use explode_by_city(df) (defined below) when you need one row per city
    # — for example when computing city-level artifact counts or building the
    # geographic map.  The embedding and clustering pipeline works on the
    # primary row to avoid double-counting artifacts in semantic space.
    "city",             # Primary city name (string, may be NaN)
    "country",          # Country name (string, may be NaN)
    "lat",              # Primary latitude (float, may be NaN)
    "lon",              # Primary longitude (float, may be NaN)
    "all_cities",       # JSON array of all city names (string, may be NaN)
    "all_coords",       # JSON array of [lat, lon] pairs  (string, may be NaN)
    # ── Themes & case study ────────────────────────────────────────────────
    "theme_primary",    # Primary topical theme (assigned during clustering)
    "theme_secondary",  # Secondary topical theme (may be NaN)
    "case_study_flag",  # True if this artifact belongs to the carbon capture case study
    "case_study_confidence",  # Float 0–1 indicating how confidently it was tagged
    "retrieval_reason", # How this artifact was found (e.g. "keyword:carbon capture")
]

ARTIFACT_TYPES = {"paper", "patent", "project", "part"}


# ---------------------------------------------------------------------------
# Dataclass for a single artifact
# ---------------------------------------------------------------------------

@dataclass
class Artifact:
    """A single research artifact — paper, patent, project, or part."""
    id: str
    type: str                        # must be one of ARTIFACT_TYPES
    title: str
    text: str                        # title + abstract concatenated
    year: Optional[int] = None
    city: Optional[str] = None       # primary city
    country: Optional[str] = None
    lat: Optional[float] = None      # primary latitude
    lon: Optional[float] = None      # primary longitude
    all_cities: Optional[str] = None # JSON array, e.g. '["Cambridge", "Zurich"]'
    all_coords: Optional[str] = None # JSON array, e.g. '[[42.36, -71.10], [47.37, 8.54]]'
    theme_primary: Optional[str] = None
    theme_secondary: Optional[str] = None
    case_study_flag: bool = False
    case_study_confidence: float = 0.0
    retrieval_reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def validate(self):
        """Raise ValueError if the artifact is missing required fields."""
        if not self.id:
            raise ValueError("Artifact must have a non-empty id.")
        if self.type not in ARTIFACT_TYPES:
            raise ValueError(f"type must be one of {ARTIFACT_TYPES}, got '{self.type}'.")
        if not self.title:
            raise ValueError("Artifact must have a non-empty title.")


# ---------------------------------------------------------------------------
# DataFrame utilities
# ---------------------------------------------------------------------------

def make_empty_dataframe() -> pd.DataFrame:
    """Return an empty DataFrame with all required columns."""
    return pd.DataFrame(columns=REQUIRED_COLUMNS)


def validate_dataframe(df: pd.DataFrame) -> list[str]:
    """
    Check that a DataFrame has all required columns.
    Returns a list of missing column names (empty list = all good).
    """
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def combine_datasets(*dfs: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate multiple normalized DataFrames into one.
    All inputs must have the required columns.
    """
    for df in dfs:
        missing = validate_dataframe(df)
        if missing:
            raise ValueError(f"DataFrame is missing columns: {missing}")
    combined = pd.concat(list(dfs), ignore_index=True)
    return combined


def explode_by_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand a normalized DataFrame so there is one row per (artifact, city).

    Use this when you need city-level counts or geographic analysis.  Each
    artifact that is associated with N cities produces N rows, all with the
    same id, text, and metadata but different city/lat/lon values.

    Artifacts with no city data (city is NaN and all_cities is NaN) are
    kept as single rows with NaN geography so they are not silently dropped.

    The returned DataFrame has the same columns as the input, plus:
      - "city_rank": integer position of this city (0 = primary, 1 = second, …)
      - "is_primary_city": True for the first city of each artifact

    Example
    -------
    An artifact with all_cities='["Cambridge", "Zurich"]' and
    all_coords='[[42.36, -71.10], [47.37, 8.54]]' becomes two rows:

        id   city       lat    lon    city_rank  is_primary_city
        X    Cambridge  42.36  -71.10  0          True
        X    Zurich     47.37   8.54   1          False

    Notes
    -----
    - The "city" / "lat" / "lon" columns in the output reflect the per-row
      city, not the original primary city.
    - For artifacts with only a primary city and no all_cities data, the
      single row is returned unchanged (city_rank=0, is_primary_city=True).
    - Deduplication: if all_cities lists the same city twice it is included
      only once per artifact.
    """
    import json

    exploded_rows = []

    for _, row in df.iterrows():
        raw_cities  = row.get("all_cities")
        raw_coords  = row.get("all_coords")

        cities_list = None
        coords_list = None

        if pd.notna(raw_cities):
            try:
                cities_list = json.loads(raw_cities)
                coords_list = json.loads(raw_coords) if pd.notna(raw_coords) else None
            except (json.JSONDecodeError, TypeError):
                pass

        if cities_list:
            seen = set()
            rank = 0
            for i, city in enumerate(cities_list):
                if city in seen:
                    continue
                seen.add(city)
                new_row = row.copy()
                new_row["city"] = city
                if coords_list and i < len(coords_list):
                    new_row["lat"] = coords_list[i][0]
                    new_row["lon"] = coords_list[i][1]
                else:
                    new_row["lat"] = pd.NA
                    new_row["lon"] = pd.NA
                new_row["city_rank"]        = rank
                new_row["is_primary_city"]  = (rank == 0)
                exploded_rows.append(new_row)
                rank += 1
        else:
            # No multi-city data — keep the row as-is
            new_row = row.copy()
            new_row["city_rank"]       = 0
            new_row["is_primary_city"] = True
            exploded_rows.append(new_row)

    return pd.DataFrame(exploded_rows).reset_index(drop=True)


def build_text_field(title: str, abstract: str) -> str:
    """
    Combine title and abstract into a single text field for embedding.
    The title is prepended to give it slightly more weight.
    """
    title = (title or "").strip()
    abstract = (abstract or "").strip()
    if title and abstract:
        return f"{title}. {abstract}"
    return title or abstract
