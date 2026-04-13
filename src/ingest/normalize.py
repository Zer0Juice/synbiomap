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
# ISO 3166-1 alpha-3 → alpha-2 conversion
# ---------------------------------------------------------------------------
# All country codes are normalised to alpha-2 (e.g. "US", "CN") throughout
# the pipeline. iGEM geocoding produces alpha-3 codes (e.g. "USA", "CHN");
# this table converts them so all datasets use a consistent standard.
# Source: ISO 3166-1 (https://www.iso.org/iso-3166-country-codes.html)

_ALPHA3_TO_ALPHA2: dict[str, str] = {
    "AFG": "AF", "ALB": "AL", "DZA": "DZ", "AND": "AD", "AGO": "AO",
    "ARG": "AR", "ARM": "AM", "AUS": "AU", "AUT": "AT", "AZE": "AZ",
    "BHS": "BS", "BHR": "BH", "BGD": "BD", "BLR": "BY", "BEL": "BE",
    "BLZ": "BZ", "BEN": "BJ", "BTN": "BT", "BOL": "BO", "BIH": "BA",
    "BWA": "BW", "BRA": "BR", "BRN": "BN", "BGR": "BG", "BFA": "BF",
    "BDI": "BI", "CPV": "CV", "KHM": "KH", "CMR": "CM", "CAN": "CA",
    "CAF": "CF", "TCD": "TD", "CHL": "CL", "CHN": "CN", "COL": "CO",
    "COM": "KM", "COD": "CD", "COG": "CG", "CRI": "CR", "CIV": "CI",
    "HRV": "HR", "CUB": "CU", "CYP": "CY", "CZE": "CZ", "DNK": "DK",
    "DJI": "DJ", "DOM": "DO", "ECU": "EC", "EGY": "EG", "SLV": "SV",
    "GNQ": "GQ", "ERI": "ER", "EST": "EE", "SWZ": "SZ", "ETH": "ET",
    "FJI": "FJ", "FIN": "FI", "FRA": "FR", "GAB": "GA", "GMB": "GM",
    "GEO": "GE", "DEU": "DE", "GHA": "GH", "GRC": "GR", "GTM": "GT",
    "GIN": "GN", "GNB": "GW", "GUY": "GY", "HTI": "HT", "HND": "HN",
    "HKG": "HK", "HUN": "HU", "ISL": "IS", "IND": "IN", "IDN": "ID",
    "IRN": "IR", "IRQ": "IQ", "IRL": "IE", "ISR": "IL", "ITA": "IT",
    "JAM": "JM", "JPN": "JP", "JOR": "JO", "KAZ": "KZ", "KEN": "KE",
    "PRK": "KP", "KOR": "KR", "KWT": "KW", "KGZ": "KG", "LAO": "LA",
    "LVA": "LV", "LBN": "LB", "LSO": "LS", "LBR": "LR", "LBY": "LY",
    "LIE": "LI", "LTU": "LT", "LUX": "LU", "MDG": "MG", "MWI": "MW",
    "MYS": "MY", "MDV": "MV", "MLI": "ML", "MLT": "MT", "MRT": "MR",
    "MUS": "MU", "MEX": "MX", "MDA": "MD", "MCO": "MC", "MNG": "MN",
    "MNE": "ME", "MAR": "MA", "MOZ": "MZ", "MMR": "MM", "NAM": "NA",
    "NPL": "NP", "NLD": "NL", "NZL": "NZ", "NIC": "NI", "NER": "NE",
    "NGA": "NG", "MKD": "MK", "NOR": "NO", "OMN": "OM", "PAK": "PK",
    "PAN": "PA", "PNG": "PG", "PRY": "PY", "PER": "PE", "PHL": "PH",
    "POL": "PL", "PRT": "PT", "QAT": "QA", "ROU": "RO", "RUS": "RU",
    "RWA": "RW", "SAU": "SA", "SEN": "SN", "SRB": "RS", "SLE": "SL",
    "SGP": "SG", "SVK": "SK", "SVN": "SI", "SOM": "SO", "ZAF": "ZA",
    "SSD": "SS", "ESP": "ES", "LKA": "LK", "SDN": "SD", "SUR": "SR",
    "SWE": "SE", "CHE": "CH", "SYR": "SY", "TWN": "TW", "TJK": "TJ",
    "TZA": "TZ", "THA": "TH", "TLS": "TL", "TGO": "TG", "TTO": "TT",
    "TUN": "TN", "TUR": "TR", "TKM": "TM", "UGA": "UG", "UKR": "UA",
    "ARE": "AE", "GBR": "GB", "USA": "US", "URY": "UY", "UZB": "UZ",
    "VEN": "VE", "VNM": "VN", "YEM": "YE", "ZMB": "ZM", "ZWE": "ZW",
}


def _normalise_country(code) -> str | None:
    """Convert ISO alpha-3 to alpha-2. Alpha-2 codes pass through unchanged."""
    if code is None:
        return None
    import math
    if isinstance(code, float) and math.isnan(code):
        return None
    code = str(code).strip().upper()
    if not code or code == "NAN":
        return None
    if len(code) == 3:
        return _ALPHA3_TO_ALPHA2.get(code, code)  # fall back to original if unknown
    return code


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
            "country": _normalise_country(rec.get("country")),
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
    Normalize a list of PatentsView patent dicts to the shared schema.

    Parameters
    ----------
    raw_records : output of patentsview.extract_fields() for each patent
    carbon_keywords : list of carbon-capture keywords for case study tagging
    """
    rows = []
    for rec in raw_records:
        title = rec.get("title", "") or ""
        abstract = rec.get("abstract", "") or ""
        text = build_text_field(title, abstract)
        patent_number = rec.get("patent_number", "")

        row = {
            "id": patent_number or _make_id("patent", title),
            "type": "patent",
            "title": title,
            "text": text,
            "year": rec.get("year"),
            "city": rec.get("city"),
            "country": _normalise_country(rec.get("country")),
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
            "country": _normalise_country(rec.get("country")),
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
