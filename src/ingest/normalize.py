"""
normalize.py — convert raw records from any source into the shared schema.

Each data source (OpenAlex, Lens, iGEM) returns data in its own format.
This module converts all of them to the same set of columns defined in
src/utils/schema.py. A single shared schema makes it easy to combine
datasets and feed them into the embedding pipeline.

Methodology note:
  Case study tagging (carbon capture) is done here by keyword matching on
  the title + abstract text. The confidence score is the fraction of
  case-study keywords found in the text (normalized to [0, 1]).
  Any keyword match sets case_study_flag = True.
"""

from __future__ import annotations
import hashlib
import logging
import re
from typing import Sequence

import pandas as pd

from src.utils.schema import build_text_field, REQUIRED_COLUMNS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public normalization functions — one per data source
# ---------------------------------------------------------------------------

def normalize_papers(raw_records: list[dict], carbon_keywords: list[str]) -> pd.DataFrame:
    """
    Normalize a list of OpenAlex paper dicts to the shared schema.

    Parameters
    ----------
    raw_records : output of openalex.extract_fields() for each work
    carbon_keywords : list of carbon-capture keywords for case study tagging
    """
    rows = []
    for rec in raw_records:
        title = rec.get("title", "") or ""
        abstract = rec.get("abstract", "") or ""
        text = build_text_field(title, abstract)
        openalex_id = rec.get("openalex_id", "")

        row = {
            "id": openalex_id or _make_id("paper", title),
            "type": "paper",
            "title": title,
            "text": text,
            "year": rec.get("year"),
            "city": rec.get("city"),       # filled by geocode_papers.py
            "country": rec.get("country"),
            "lat": rec.get("lat"),         # filled by geocode_papers.py
            "lon": rec.get("lon"),         # filled by geocode_papers.py
            "theme_primary": None,         # filled in later by clustering
            "theme_secondary": None,
            "retrieval_reason": rec.get("retrieval_reason", "keyword"),
            # Semicolon-separated list of OpenAlex IDs this paper cites.
            # Used to draw citation edges in the semantic space explorer.
            "cited_works": rec.get("cited_works", ""),
            # Semicolon-separated list of OpenAlex institution IDs for this
            # paper's authors. Used by geocode_papers.py to look up city/lat/lon
            # from the full institution objects without re-fetching all works.
            "institution_ids": rec.get("institution_ids", ""),
        }
        row.update(_tag_case_study(text, carbon_keywords))
        rows.append(row)

    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS + ["cited_works", "institution_ids"])


def normalize_patents(raw_records: list[dict], carbon_keywords: list[str]) -> pd.DataFrame:
    """
    Normalize a list of Lens.org patent dicts to the shared schema.

    Parameters
    ----------
    raw_records : output of lens.extract_fields() for each patent
    carbon_keywords : list of carbon-capture keywords for case study tagging
    """
    rows = []
    for rec in raw_records:
        title = rec.get("title", "") or ""
        abstract = rec.get("abstract", "") or ""
        text = build_text_field(title, abstract)
        lens_id = rec.get("lens_id", "")

        row = {
            "id": lens_id or _make_id("patent", title),
            "type": "patent",
            "title": title,
            "text": text,
            "year": rec.get("year"),
            "city": rec.get("city"),
            "country": rec.get("country"),
            "lat": None,
            "lon": None,
            "theme_primary": None,
            "theme_secondary": None,
            "retrieval_reason": rec.get("retrieval_reason", "keyword"),
        }
        row.update(_tag_case_study(text, carbon_keywords))
        rows.append(row)

    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def normalize_projects(raw_records: list[dict], carbon_keywords: list[str]) -> pd.DataFrame:
    """
    Normalize a list of iGEM project dicts to the shared schema.

    Parameters
    ----------
    raw_records : output of igem.extract_project_fields() for each project
    carbon_keywords : list of carbon-capture keywords for case study tagging
    """
    rows = []
    for rec in raw_records:
        title = rec.get("title", "") or ""
        abstract = rec.get("abstract", "") or ""
        text = build_text_field(title, abstract)
        team = rec.get("igem_team", "")

        row = {
            "id": f"igem_{team}_{rec.get('year', 'unk')}" if team else _make_id("project", title),
            "type": "project",
            "title": title,
            "text": text,
            "year": rec.get("year"),
            "city": rec.get("city"),
            "country": rec.get("country"),
            "lat": rec.get("lat"),
            "lon": rec.get("lon"),
            "theme_primary": None,
            "theme_secondary": None,
            "retrieval_reason": rec.get("retrieval_reason", "igem"),
        }
        row.update(_tag_case_study(text, carbon_keywords))
        rows.append(row)

    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def normalize_parts(raw_records: list[dict], carbon_keywords: list[str]) -> pd.DataFrame:
    """
    Normalize a list of iGEM part dicts to the shared schema.

    Parts are associated with a team, so city/country are not directly
    available and will be joined from the projects table later.
    """
    rows = []
    for rec in raw_records:
        title = rec.get("title", "") or rec.get("part_name", "") or ""
        abstract = rec.get("abstract", "") or ""
        text = build_text_field(title, abstract)
        part_name = rec.get("part_name", "")

        row = {
            "id": f"part_{part_name}" if part_name else _make_id("part", title),
            "type": "part",
            "title": title,
            "text": text,
            "year": rec.get("year"),
            "city": None,    # joined from projects later
            "country": None,
            "lat": None,
            "lon": None,
            "theme_primary": None,
            "theme_secondary": None,
            "retrieval_reason": rec.get("retrieval_reason", "igem"),
        }
        row.update(_tag_case_study(text, carbon_keywords))
        rows.append(row)

    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


# ---------------------------------------------------------------------------
# Case study tagging
# ---------------------------------------------------------------------------

def _tag_case_study(text: str, keywords: Sequence[str]) -> dict:
    """
    Check whether the text contains carbon-capture keywords.

    Returns a dict with case_study_flag and case_study_confidence.
    confidence = number of matched keywords / total keywords.

    Methodology note:
      A simple keyword-match approach is used for transparency and
      reproducibility. More sophisticated methods (e.g. zero-shot
      classification) could be added later for comparison.
    """
    if not keywords or not text:
        return {"case_study_flag": False, "case_study_confidence": 0.0}

    text_lower = text.lower()
    matched = sum(1 for kw in keywords if kw.lower() in text_lower)
    confidence = matched / len(keywords)
    return {
        "case_study_flag": matched > 0,
        "case_study_confidence": round(confidence, 4),
    }


# ---------------------------------------------------------------------------
# ID generation
# ---------------------------------------------------------------------------

def _make_id(artifact_type: str, title: str) -> str:
    """
    Generate a stable ID for an artifact when no official ID is available.
    Uses a short hash of the type + title.
    """
    key = f"{artifact_type}:{title}"
    return f"{artifact_type}_{hashlib.md5(key.encode()).hexdigest()[:8]}"
