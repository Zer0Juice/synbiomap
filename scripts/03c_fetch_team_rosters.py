"""
Step 3c — Fetch iGEM team rosters and add member names to projects.csv.

For each iGEM project in projects.csv, this script fetches the team roster
from the iGEM Teams API and records the member names. This lets us trace
which people contributed to each project — useful for cross-referencing with
paper authorship and building person-level innovation trajectories.

API endpoint used:
    GET https://api.igem.org/v1/teams/{team_id}/roster
    Returns a list of team members with names, roles, and institutions.
    No authentication required.

The numeric team ID comes from the raw projects CSV (the `id` column), which
is the same ID that appears in https://teams.igem.org/{id}.

Outputs
-------
  data/raw/projects/roster_cache.json
      Maps team_id (string) → list of member objects from the API.
      Delete this file to re-fetch from scratch. The script is safe to
      interrupt and resume — the cache is written incrementally.

  data/processed/projects.csv  (updated in place)
      Adds one new column:
        team_members        — semicolon-separated list of all member names

Usage:
    python scripts/03c_fetch_team_rosters.py

    # Test with a small batch first:
    python scripts/03c_fetch_team_rosters.py --max-teams 20

Note on run time:
    ~4,600 teams × ~0.1s per request ≈ 8 minutes.
    The cache means re-runs complete instantly.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

RAW_PROJECTS_DIR = REPO_ROOT / "data" / "raw" / "projects"
PROCESSED_DIR    = REPO_ROOT / "data" / "processed"

ROSTER_CACHE     = RAW_PROJECTS_DIR / "roster_cache.json"
PROJECTS_OUT     = PROCESSED_DIR / "projects.csv"

# Raw projects CSV — contains the numeric team IDs
RAW_PROJECTS_CSV = RAW_PROJECTS_DIR / "igem_teams_with_descriptions_2004_2025.csv"
RAW_PROJECTS_ALT = RAW_PROJECTS_DIR / "igem_projects.csv"

TEAMS_API_BASE   = "https://api.igem.org/v1"



# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def load_roster_cache(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_roster_cache(cache: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(cache, f)


# ---------------------------------------------------------------------------
# API fetch
# ---------------------------------------------------------------------------

def fetch_roster(session: requests.Session, team_id: int) -> list[dict]:
    """
    Fetch the roster for one team. Returns a list of member dicts, or an
    empty list if the team is not found or the request fails.
    """
    url = f"{TEAMS_API_BASE}/teams/{team_id}/roster"
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.warning(f"  Failed to fetch roster for team {team_id}: {e}")
        return []


# ---------------------------------------------------------------------------
# Member name extraction
# ---------------------------------------------------------------------------

def extract_names(members: list[dict]) -> list[str]:
    names = []
    for entry in members:
        member = entry.get("member") or {}
        user = member.get("user") or {}  # user is None for deleted accounts
        name = user.get("publicName", "").strip()
        if name:
            names.append(name)
    return names


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(max_teams: int | None = None) -> None:
    # --- Load raw projects to get numeric team IDs ---
    raw_path = RAW_PROJECTS_CSV if RAW_PROJECTS_CSV.exists() else RAW_PROJECTS_ALT
    if not raw_path.exists():
        logger.error(f"Raw projects CSV not found at {raw_path}")
        sys.exit(1)

    raw_df = pd.read_csv(raw_path)
    # The `id` column is the numeric iGEM team ID (same as in teams.igem.org/{id})
    # The `name` + `year` columns let us match back to processed projects.csv
    raw_df["project_id"] = "igem_" + raw_df["name"].astype(str) + "_" + raw_df["year"].astype(str)
    id_map = dict(zip(raw_df["project_id"], raw_df["id"].astype(int)))

    # --- Load processed projects ---
    if not PROJECTS_OUT.exists():
        logger.error(f"projects.csv not found at {PROJECTS_OUT}. Run 03_ingest_projects.py first.")
        sys.exit(1)

    projects_df = pd.read_csv(PROJECTS_OUT)
    logger.info(f"Loaded {len(projects_df)} projects from projects.csv")

    # --- Load cache ---
    cache = load_roster_cache(ROSTER_CACHE)
    logger.info(f"Roster cache has {len(cache)} teams already fetched")

    # --- Determine which teams need fetching ---
    # We key the cache by the string team ID for JSON compatibility
    to_fetch = []
    for proj_id in projects_df["id"]:
        team_id = id_map.get(proj_id)
        if team_id is None:
            continue  # no numeric ID found for this project
        if str(team_id) not in cache:
            to_fetch.append((proj_id, team_id))

    if max_teams:
        to_fetch = to_fetch[:max_teams]

    if to_fetch:
        logger.info(f"Fetching rosters for {len(to_fetch)} teams (press Ctrl+C to pause — cache is saved every 50 teams)…")
        session = requests.Session()
        session.headers.update({"User-Agent": "synbiomap-research/1.0"})

        for i, (proj_id, team_id) in enumerate(to_fetch):
            members = fetch_roster(session, team_id)
            cache[str(team_id)] = members
            time.sleep(0.05)  # ~20 requests/second — polite but fast

            if (i + 1) % 50 == 0:
                save_roster_cache(cache, ROSTER_CACHE)
                logger.info(f"  {i + 1}/{len(to_fetch)} done, cache saved")

        save_roster_cache(cache, ROSTER_CACHE)
        logger.info(f"Done fetching. Cache saved to {ROSTER_CACHE.relative_to(REPO_ROOT)}")
    else:
        logger.info("All teams already in cache — skipping fetch phase.")

    # --- Build team_members column for projects.csv ---
    logger.info("Building team_members column…")

    members_col = []
    for proj_id in projects_df["id"]:
        team_id = id_map.get(proj_id)
        if team_id is None or str(team_id) not in cache:
            members_col.append("")
            continue
        names = extract_names(cache[str(team_id)])
        members_col.append(";".join(names))

    projects_df["team_members"] = members_col

    # --- Save ---
    projects_df.to_csv(PROJECTS_OUT, index=False)
    logger.info(f"Saved updated projects.csv ({len(projects_df)} rows) to {PROJECTS_OUT.relative_to(REPO_ROOT)}")

    filled = (projects_df["team_members"] != "").sum()
    logger.info(f"  {filled}/{len(projects_df)} projects have roster data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--max-teams", type=int, default=None,
        help="Stop after fetching this many teams (useful for testing)"
    )
    args = parser.parse_args()
    run(max_teams=args.max_teams)
