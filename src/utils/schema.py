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
    "city",             # City name (string, may be NaN)
    "country",          # Country name (string, may be NaN)
    "lat",              # Latitude (float, may be NaN)
    "lon",              # Longitude (float, may be NaN)
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
    city: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
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
