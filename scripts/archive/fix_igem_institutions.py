"""
fix_igem_institutions.py — patch the iGEM teams CSV with clean institution names.

Two things this script does:
  1. Clears the 'city' column for years 2009–2023, because those values came from
     poor early geocoding and are unreliable. The 2024 and 2025 city values (fetched
     directly from the iGEM API) are trustworthy and are left alone.

  2. Adds an 'institution' column by calling GET /v1/teams/{id} for every team.
     The API returns a structured 'institutions' array; we take the first entry's
     'name' field (stripping any embedded address text in older records).

Caching:
  Results are saved to data/raw/projects/igem_institutions_cache.json after every
  50 teams. If the script is interrupted, re-running it will skip teams already
  in the cache.

Usage:
    python scripts/fix_igem_institutions.py

Output:
    Overwrites data/raw/projects/igem_teams_with_descriptions_2004_2025.csv
    in-place with the updated columns.
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "raw" / "projects" / "igem_teams_with_descriptions_2004_2025.csv"
CACHE_PATH = REPO_ROOT / "data" / "raw" / "projects" / "igem_institutions_cache.json"

API_BASE = "https://api.igem.org/v1/teams"
WORKERS = 8       # concurrent requests — polite for a small API
SAVE_EVERY = 100  # flush cache to disk every N completions


def fetch_institution(team_id: int) -> tuple[int, str]:
    """
    Fetch the first institution name for a team from the iGEM API.

    Returns (team_id, institution_name).
    Returns an empty string if the team has no institutions or the request fails.
    """
    try:
        r = requests.get(f"{API_BASE}/{team_id}", timeout=15)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        print(f"  WARNING: team {team_id} — request failed: {e}", flush=True)
        return team_id, ""

    institutions = data.get("institutions") or []
    if not institutions:
        return team_id, ""

    raw_name = institutions[0].get("name") or ""

    # Older records (pre-2020) embed the full address in the name field,
    # separated by \r\n or \r\r\n.  Take only the first non-empty line.
    first_line = raw_name.replace("\r\r\n", "\n").replace("\r\n", "\n").split("\n")[0].strip()
    return team_id, first_line


def load_cache() -> dict:
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def main():
    # ------------------------------------------------------------------
    # 1. Load CSV
    # ------------------------------------------------------------------
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} teams from {CSV_PATH.name}")

    # ------------------------------------------------------------------
    # 2. Clear city for 2009–2023
    # ------------------------------------------------------------------
    old_mask = df["year"] <= 2023
    n_cleared = old_mask.sum()
    df.loc[old_mask, "city"] = None
    print(f"Cleared city for {n_cleared} teams (years 2009–2023)")

    # ------------------------------------------------------------------
    # 3. Fetch institution names with caching
    # ------------------------------------------------------------------
    cache: dict = load_cache()  # {str(team_id): institution_name}
    team_ids = df["id"].tolist()
    missing_ids = [tid for tid in team_ids if str(tid) not in cache]
    print(f"Institution cache has {len(cache)} entries; need to fetch {len(missing_ids)} more")

    if missing_ids:
        completed = 0
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {pool.submit(fetch_institution, tid): tid for tid in missing_ids}
            for future in as_completed(futures):
                tid, name = future.result()
                cache[str(tid)] = name
                completed += 1
                if completed % 50 == 0:
                    print(f"  {completed}/{len(missing_ids)} fetched…", flush=True)
                if completed % SAVE_EVERY == 0:
                    save_cache(cache)

        save_cache(cache)
        print(f"Done. Fetched {completed} institutions.")

    # ------------------------------------------------------------------
    # 4. Add institution column
    # ------------------------------------------------------------------
    df["institution"] = df["id"].apply(lambda tid: cache.get(str(tid), ""))

    filled = (df["institution"] != "").sum()
    print(f"Institution column: {filled}/{len(df)} teams have a non-empty value")

    # ------------------------------------------------------------------
    # 5. Save updated CSV
    # ------------------------------------------------------------------
    df.to_csv(CSV_PATH, index=False)
    print(f"\nSaved updated CSV to {CSV_PATH.relative_to(REPO_ROOT)}")
    print("Preview (first 3 rows):")
    print(df[["id", "name", "year", "city", "institution", "country"]].head(3).to_string())


if __name__ == "__main__":
    main()
