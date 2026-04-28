"""
Step 3b — Fetch iGEM parts from the Registry API and match them to projects.

This script uses the iGEM Registry REST API (api.registry.igem.org, launched
August 2025). No authentication is required. The old CSV export from
parts.igem.org/partsdb/ and SynBioHub SPARQL are no longer used.

Pipeline (four phases, each cached so re-runs are fast):
  1. Fetch all parts from the Registry API → cache as JSONL
  2. Fetch authors for each part → cache as JSON (part UUID → org UUID)
  3. Fetch organisations for each unique org UUID → cache as JSON
  4. Build outputs: parts.csv, part_team_edges.csv, part_composition_edges.csv

Team matching:
  Parts have no location data. We link them to teams via:
    part → /authors → organisationUUID → /organisations/{uuid} → "TeamName (YYYY)"
  Then match "TeamName" + year against projects.csv to inherit city/lat/lon.

Composition edges:
  We fetch sub-part composition only for parts that matched to a project team.
  A composite part that includes a sub-part is analogous to a citation —
  it formally depends on and builds upon that prior part.
  This is fetched last because it requires one API call per part.

Outputs
-------
  data/raw/parts/parts_cache.jsonl
      One JSON object per line. All parts from the Registry API.
      Delete this file to re-fetch from scratch.

  data/raw/parts/authors_cache.json
      Maps part UUID → list of author objects (including organisationUUID).

  data/raw/parts/orgs_cache.json
      Maps org UUID → organisation object (name, type, link).

  data/processed/parts.csv
      One row per part, in the shared artifact schema.

  data/processed/part_team_edges.csv
      Columns: part_name, team_name, year, org_uuid
      Links parts to iGEM project teams.

  data/processed/part_composition_edges.csv
      Columns: parent, child
      A directed edge means the parent (composite) part contains the child.

  data/processed/part_paper_edges.csv
      Columns: part_name, doi, paper_id
      Links parts to papers via DOIs extracted from the source field.
      paper_id is filled in where the DOI matches a paper in papers.csv;
      otherwise it is blank (the paper exists but wasn't in our corpus).

Usage:
    python scripts/03b_fetch_parts.py

    # Skip slow author-fetching phase (only basic part data, no team matching):
    python scripts/03b_fetch_parts.py --skip-authors

    # Limit parts fetched (useful for testing):
    python scripts/03b_fetch_parts.py --max-parts 500

Note on run time:
  Phase 1 (list all parts): ~5-10 minutes for ~57,000 parts.
  Phase 2 (fetch authors): ~2 hours for ~57,000 parts. This is the slow phase.
    The script is safe to interrupt and resume — the cache is written after
    each part, so progress is never lost.
  Phase 3 (fetch orgs): a few minutes for the unique org UUIDs.
  Phase 4 (composition): a few minutes for the matched subset.
"""

import argparse
import json
import sys
import logging
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.ingest.igem import (
    fetch_all_parts,
    fetch_all_orgs,
    fetch_org_parts,
    fetch_part_composition,
    extract_part_fields,
    parse_org_name,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# Paths
RAW_DIR       = REPO_ROOT / "data" / "raw" / "parts"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
PROJECTS_PATH = PROCESSED_DIR / "projects.csv"

PARTS_CACHE   = RAW_DIR / "parts_cache.jsonl"
ORGS_CACHE    = RAW_DIR / "orgs_cache.json"
TEAM_PARTS_CACHE = RAW_DIR / "team_parts_cache.json"  # org_uuid → [part_uuids]

PAPERS_PATH     = PROCESSED_DIR / "papers.csv"
PARTS_OUT       = PROCESSED_DIR / "parts.csv"
TEAM_EDGES_OUT  = PROCESSED_DIR / "part_team_edges.csv"
COMP_EDGES_OUT  = PROCESSED_DIR / "part_composition_edges.csv"
PAPER_EDGES_OUT = PROCESSED_DIR / "part_paper_edges.csv"


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def load_json_cache(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_json_cache(cache: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(cache, f)


# ---------------------------------------------------------------------------
# Phase 2: build part → team mapping via org-first sweep
# ---------------------------------------------------------------------------

def build_part_team_map(orgs: list[dict]) -> dict:
    """
    Fetch all parts for every organisation and return a part_uuid → team_info map.

    Instead of calling /parts/{uuid}/authors once per part (88,000+ calls),
    we call /organisations/{uuid}/parts once per org (~5,900 calls) — a 15x
    reduction. Each org response includes the full part objects, and we already
    know the team info from the orgs list fetched in Phase 1.

    The result is cached to TEAM_PARTS_CACHE. The cache stores the full map
    so re-runs are instant. Progress is saved every 100 orgs so the script
    can be safely interrupted and resumed.

    Returns
    -------
    dict : part_uuid → {team_id, team_name, year, org_uuid, org_link}
    """
    # Load existing cache if present
    cache: dict = load_json_cache(TEAM_PARTS_CACHE)

    # Track which org UUIDs we've already processed
    done_orgs: set[str] = set(cache.get("_done_orgs", []))
    part_map: dict = {k: v for k, v in cache.items() if k != "_done_orgs"}

    to_fetch = [o for o in orgs if o["uuid"] not in done_orgs]

    if not to_fetch:
        print(f"  Team-parts cache complete ({len(part_map)} parts mapped).")
        return part_map

    print(f"  Fetching parts for {len(to_fetch)} orgs "
          f"({len(done_orgs)} already done, {len(part_map)} parts mapped so far)…")
    print("  Safe to interrupt — progress is saved every 100 orgs.")

    session = requests.Session()
    save_interval = 100

    for i, org in enumerate(to_fetch):
        org_uuid  = org["uuid"]
        team_info = {
            "team_id":   org["team_id"],
            "team_name": org["team_name"],
            "year":      org["year"],
            "org_uuid":  org_uuid,
            "org_link":  org.get("link", ""),
        }

        org_parts = fetch_org_parts(org_uuid, session)
        for part in org_parts:
            part_uuid = part.get("uuid")
            if part_uuid:
                part_map[part_uuid] = team_info

        done_orgs.add(org_uuid)

        if (i + 1) % save_interval == 0:
            save_json_cache({**part_map, "_done_orgs": list(done_orgs)}, TEAM_PARTS_CACHE)
            print(f"  {i+1}/{len(to_fetch)} orgs done, {len(part_map)} parts mapped (saved)", flush=True)

    save_json_cache({**part_map, "_done_orgs": list(done_orgs)}, TEAM_PARTS_CACHE)
    print(f"  Done. {len(part_map)} parts mapped across {len(done_orgs)} orgs.")
    return part_map


# ---------------------------------------------------------------------------
# Phase 4: build outputs
# ---------------------------------------------------------------------------

def build_parts_df(
    parts: list[dict],
    part_map: dict,
    projects_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build parts.csv and part_team_edges.csv.

    Matching logic:
      part_map is a dict of part_uuid → team_info built by build_part_team_map().
      team_info contains a numeric team_id matching the `id` column in projects.csv.
      This is a direct integer join — no fuzzy name matching needed.

    Parts without a team match still appear in parts.csv but without
    team_id or team_name.
    """
    # Build a lookup: team_id (int) → project row
    proj_lookup: dict[int, pd.Series] = {}
    for _, row in projects_df.iterrows():
        try:
            tid = int(row["id"])
            proj_lookup[tid] = row
        except (ValueError, TypeError):
            continue

    rows = []
    team_edge_rows = []
    unmatched = 0

    for part in parts:
        uuid = part.get("uuid", "")
        fields = extract_part_fields(part)

        team_info = part_map.get(uuid) or {}
        team_id   = team_info.get("team_id")
        team_name = team_info.get("team_name")
        org_uuid  = team_info.get("org_uuid")
        year      = team_info.get("year") or fields["year"]

        proj_row = proj_lookup.get(team_id) if team_id else None

        city = country = lat = lon = None
        if proj_row is not None:
            city    = proj_row.get("city")
            country = proj_row.get("country")
            lat     = proj_row.get("lat")
            lon     = proj_row.get("lon")
            team_edge_rows.append({
                "part_name": fields["part_name"],
                "team_id":   team_id,
                "team_name": team_name,
                "year":      year,
                "org_uuid":  org_uuid,
            })
        else:
            unmatched += 1

        rows.append({
            "id":          f"igem_part_{fields['part_name']}",
            "type":        "part",
            "title":       fields["title"],
            "text":        fields["description"],
            "year":        year,
            "city":        city,
            "country":     country,
            "lat":         lat,
            "lon":         lon,
            "part_name":   fields["part_name"],
            "part_uuid":   uuid,
            "part_type":   fields["part_type"],
            "part_role":   fields["part_role"],
            "source_dois": fields["source_dois"],
            "team_id":     team_id,
            "team_name":   team_name,
            "org_uuid":    org_uuid,
            "theme_primary":         None,
            "theme_secondary":       None,
            "case_study_flag":       False,
            "case_study_confidence": 0.0,
            "retrieval_reason":      "igem_registry_api",
        })

    logger.info(f"Parts matched to a project team: {len(team_edge_rows)}")
    logger.info(f"Parts without a team match:      {unmatched}")

    parts_df      = pd.DataFrame(rows)
    team_edges_df = pd.DataFrame(team_edge_rows) if team_edge_rows else pd.DataFrame(
        columns=["part_name", "team_id", "team_name", "year", "org_uuid"]
    )
    return parts_df, team_edges_df


def build_composition_edges(
    parts_df: pd.DataFrame,
    matched_uuids: list[str],
) -> pd.DataFrame:
    """
    Fetch composition edges for parts that matched a project team.

    We only fetch composition for matched parts to limit API calls.
    A composite → sub-part edge encodes a formal dependency relationship,
    analogous to a citation between papers.

    Returns a DataFrame with columns: parent, child.
    """
    if not matched_uuids:
        return pd.DataFrame(columns=["parent", "child"])

    # Build a UUID → part_name lookup for matched parts
    uuid_to_name = dict(zip(parts_df["part_uuid"], parts_df["part_name"]))

    print(f"  Fetching composition for {len(matched_uuids)} matched parts…")
    session = requests.Session()
    edges = []

    for i, uuid in enumerate(matched_uuids):
        parent_name = uuid_to_name.get(uuid)
        if not parent_name:
            continue

        components = fetch_part_composition(uuid, session)
        for comp in components:
            child_name = comp.get("componentName", "")
            if child_name and child_name != parent_name:
                edges.append({"parent": parent_name, "child": child_name})

        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(matched_uuids)} done", flush=True)

    print(f"  Done. {len(edges)} composition edges found.")
    return pd.DataFrame(edges) if edges else pd.DataFrame(columns=["parent", "child"])


# ---------------------------------------------------------------------------
# Part → paper edges via DOI matching
# ---------------------------------------------------------------------------

def build_part_paper_edges(parts_df: pd.DataFrame, papers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Match parts to papers using DOIs extracted from the source field.

    Many parts cite the paper that describes the sequence they encode.
    The source field contains free text like:
      "doi: https://doi.org/10.1021/acschembio.5b00753"
    We already extracted these into the source_dois column (semicolon-separated).

    We match against papers.csv using the doi column. Parts that have a DOI
    but whose paper isn't in our corpus still get a row (paper_id will be blank)
    so we can see how much coverage we're missing.

    Returns a DataFrame with columns: part_name, doi, paper_id.
    """
    # Build DOI → paper id lookup from papers.csv
    # papers.csv stores DOIs as full URLs like "https://doi.org/10.1021/..."
    # Normalise both sides to bare DOIs (starting with "10.") for matching.
    doi_to_paper: dict[str, str] = {}
    if "doi" in papers_df.columns:
        for _, row in papers_df.iterrows():
            raw_doi = str(row.get("doi", "") or "")
            bare = raw_doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
            if bare.startswith("10."):
                doi_to_paper[bare.lower()] = str(row["id"])

    rows = []
    for _, part_row in parts_df.iterrows():
        raw_dois = str(part_row.get("source_dois", "") or "")
        if not raw_dois:
            continue
        for doi in raw_dois.split(";"):
            doi = doi.strip()
            if not doi:
                continue
            bare = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
            paper_id = doi_to_paper.get(bare.lower(), "")
            rows.append({
                "part_name": part_row["part_name"],
                "doi":       bare,
                "paper_id":  paper_id,
            })

    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["part_name", "doi", "paper_id"])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(skip_authors: bool = False, max_parts: int | None = None):
    print("=== Step 3b: Fetch iGEM Parts from Registry API ===\n")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Load projects for team matching.
    # The projects CSV must have a numeric `id` column matching teams.igem.org IDs.
    if not PROJECTS_PATH.exists():
        print("ERROR: projects.csv not found. Run 03_ingest_projects.py first.")
        return
    projects_df = pd.read_csv(PROJECTS_PATH)
    print(f"Loaded {len(projects_df)} projects for team matching.")

    # Load papers for DOI matching (optional — skip gracefully if missing)
    papers_df = pd.DataFrame()
    if PAPERS_PATH.exists():
        papers_df = pd.read_csv(PAPERS_PATH, usecols=["id", "doi"] if "doi" in pd.read_csv(PAPERS_PATH, nrows=0).columns else ["id"])
        print(f"Loaded {len(papers_df)} papers for DOI matching.")
    else:
        print("papers.csv not found — skipping part→paper DOI matching.")
    print()

    # --- Phase 1: Fetch all parts ---
    print("Phase 1: Fetch all parts from Registry API")
    parts = fetch_all_parts(PARTS_CACHE)
    if max_parts:
        parts = parts[:max_parts]
        print(f"  Limiting to {max_parts} parts (--max-parts flag).")
    print(f"  {len(parts)} parts loaded.\n")

    # --- Phase 2: Fetch all orgs, then sweep org → parts for team linkage ---
    if skip_authors:
        print("Phase 2: Skipping team lookup (--skip-authors). No team matching.\n")
        part_map = {}
    else:
        print("Phase 2a: Fetch all organisations (~60 API calls)")
        orgs = fetch_all_orgs(ORGS_CACHE)
        print(f"  {len(orgs)} orgs loaded.\n")

        print("Phase 2b: Fetch parts per org to build part → team map (~5,900 API calls)")
        part_map = build_part_team_map(orgs)
        print()

    # --- Phase 3: Build outputs ---
    print("Phase 3: Build outputs")

    parts_df, team_edges_df = build_parts_df(
        parts, part_map, projects_df
    )

    # Part → paper edges via DOI
    print("\nBuilding part → paper edges via DOI matching…")
    paper_edges_df = build_part_paper_edges(parts_df, papers_df)
    matched_paper_edges = paper_edges_df["paper_id"].notna() & (paper_edges_df["paper_id"] != "")

    # Save
    parts_df.to_csv(PARTS_OUT, index=False)
    team_edges_df.to_csv(TEAM_EDGES_OUT, index=False)
    paper_edges_df.to_csv(PAPER_EDGES_OUT, index=False)

    print(f"\nResults:")
    print(f"  Parts total:               {len(parts_df)}")
    print(f"  Parts with location:       {parts_df['lat'].notna().sum()}")
    print(f"  Parts with source DOIs:    {(parts_df['source_dois'].notna() & (parts_df['source_dois'] != '')).sum()}")
    print(f"  Team edges:                {len(team_edges_df)}")
    print(f"  Part→paper DOI edges:      {len(paper_edges_df)} ({matched_paper_edges.sum()} matched to corpus)")

    print(f"\nSaved:")
    print(f"  {PARTS_OUT.relative_to(REPO_ROOT)}")
    print(f"  {TEAM_EDGES_OUT.relative_to(REPO_ROOT)}")
    print(f"  {PAPER_EDGES_OUT.relative_to(REPO_ROOT)}")
    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch iGEM parts from Registry API")
    parser.add_argument(
        "--skip-authors",
        action="store_true",
        help="Skip fetching part authors (no team matching, much faster)",
    )
    parser.add_argument(
        "--max-parts",
        type=int,
        default=None,
        help="Limit total parts processed (useful for testing)",
    )
    args = parser.parse_args()
    run(skip_authors=args.skip_authors, max_parts=args.max_parts)
