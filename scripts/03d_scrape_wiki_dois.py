"""
Step 3d — Scrape every iGEM team wiki for the DOIs it cites.

What this produces
------------------
A document-level bridge from the *student* layer of our corpus to the *academic*
layer: for each iGEM team it lists the academic papers (by DOI) cited anywhere on
that team's project wiki. That lets us ask whether student projects point at the
same research that shows up in local papers and patents — the project's core
question — at the level of actual citations, not just embedding similarity.

This extends, rather than replaces, the part-level DOIs we already pull from the
Registry `source` field (scripts/03b_fetch_parts.py): wikis cite far more papers
than part pages do.

How it works
------------
The raw teams CSV gives each team a landing-page URL (`wikiURL`). For every team
we breadth-first crawl that team's own wiki namespace and scan each sub-page for
DOIs — see src/ingest/igem_wiki.py for the crawl/extraction logic and the two
wiki eras (2009–2021 MediaWiki vs 2022–2025 igem.wiki) it handles.

Restartable & polite
--------------------
Every team's crawl result is cached to data/raw/igem_wiki/{team_id}.json, so an
interrupted run resumes for free (already-cached teams are skipped). Requests are
rate-limited and use a descriptive User-Agent. Use --refresh to re-crawl.

Output (data/processed/igem_wiki_dois.csv), one row per (team, DOI):
    project_id, team_id, team_name, year, doi, doi_url,
    n_source_pages, source_pages, wiki_url, pages_crawled, status

Usage
-----
    # Quick test on a handful of teams:
    python scripts/03d_scrape_wiki_dois.py --limit 5

    # Just the carbon-capture case-study teams (small, fast):
    python scripts/03d_scrape_wiki_dois.py --case-study \\
        --out data/processed/igem_wiki_dois_carbon_capture.csv

    # One competition year:
    python scripts/03d_scrape_wiki_dois.py --year 2023

    # The full corpus (this takes a while — run it in the background):
    python scripts/03d_scrape_wiki_dois.py --workers 6

    # Rebuild the CSV from existing caches without crawling:
    python scripts/03d_scrape_wiki_dois.py --aggregate-only
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.ingest.igem_wiki import crawl_team_wiki, USER_AGENT  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# Inputs / outputs
RAW_TEAMS = REPO_ROOT / "data" / "raw" / "projects" / "igem_teams_with_descriptions_2004_2025.csv"
PROJECTS  = REPO_ROOT / "data" / "processed" / "projects.csv"
CACHE_DIR = REPO_ROOT / "data" / "raw" / "igem_wiki"          # gitignored (re-fetchable)
OUT_PATH  = REPO_ROOT / "data" / "processed" / "igem_wiki_dois.csv"

# Cap on how many crawled sub-pages to record per DOI in the CSV (keeps the
# source_pages column readable; the full list is always in the cache JSON).
MAX_PAGES_LISTED = 5


def _rel(path: Path) -> str:
    """Show a repo-relative path when possible, else the absolute path."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# Loading & selecting teams
# ---------------------------------------------------------------------------

def load_teams(args) -> pd.DataFrame:
    """Load the raw teams CSV, attach the matching project_id, and apply filters."""
    if not RAW_TEAMS.exists():
        raise FileNotFoundError(f"Raw teams CSV not found at {RAW_TEAMS}")

    teams = pd.read_csv(RAW_TEAMS, dtype=str)
    teams = teams.rename(columns={"id": "team_id", "name": "team_name", "wikiURL": "wiki_url"})
    teams = teams[["team_id", "team_name", "year", "wiki_url"]].copy()

    # Attach project_id (and the carbon-capture flag) from the processed corpus
    # by joining on team_id. Teams filtered out of projects.csv simply get blanks.
    if PROJECTS.exists():
        proj = pd.read_csv(PROJECTS, dtype=str)
        proj = proj.rename(columns={"id": "project_id"})
        keep = ["team_id", "project_id"]
        if "case_study_flag" in proj.columns:
            keep.append("case_study_flag")
        teams = teams.merge(proj[keep].drop_duplicates("team_id"), on="team_id", how="left")
    else:
        logger.warning("projects.csv not found — project_id and --case-study unavailable.")
        teams["project_id"] = ""
        teams["case_study_flag"] = ""

    # --- filters ---
    if args.case_study:
        if "case_study_flag" not in teams.columns:
            raise SystemExit("--case-study requested but projects.csv has no case_study_flag column.")
        flag = teams["case_study_flag"].astype(str).str.lower().isin(["true", "1"])
        teams = teams[flag]
    if args.year:
        teams = teams[teams["year"].astype(str).isin([str(y) for y in args.year])]

    teams = teams.dropna(subset=["wiki_url"])
    teams = teams[teams["wiki_url"].str.strip() != ""]
    teams = teams.drop_duplicates("team_id").reset_index(drop=True)

    if args.limit:
        teams = teams.head(args.limit)
    return teams


# ---------------------------------------------------------------------------
# Crawling (cached, restartable)
# ---------------------------------------------------------------------------

def cache_path(team_id: str) -> Path:
    return CACHE_DIR / f"{team_id}.json"


def crawl_one(row: dict, args) -> str:
    """Crawl one team unless it's already cached. Returns the team_id."""
    team_id = row["team_id"]
    cf = cache_path(team_id)
    if cf.exists() and not args.refresh:
        return team_id

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    try:
        result = crawl_team_wiki(
            row["wiki_url"],
            session=session,
            max_pages=args.max_pages,
            delay=args.delay,
        )
    finally:
        session.close()

    record = {
        "team_id": team_id,
        "team_name": row.get("team_name"),
        "year": row.get("year"),
        "wiki_url": row.get("wiki_url"),
        "crawled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **result.to_dict(),
    }
    cf.parent.mkdir(parents=True, exist_ok=True)
    cf.write_text(json.dumps(record))
    return team_id


def run_crawl(teams: pd.DataFrame, args) -> None:
    rows = teams.to_dict("records")
    todo = [r for r in rows if args.refresh or not cache_path(r["team_id"]).exists()]
    print(f"Teams selected: {len(rows)} | to crawl now: {len(todo)} "
          f"| already cached: {len(rows) - len(todo)}")
    if not todo:
        return

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(crawl_one, r, args): r for r in todo}
        for fut in as_completed(futures):
            r = futures[fut]
            try:
                fut.result()
            except Exception as e:  # one team failing must not stop the run
                logger.warning("crawl failed for team %s (%s): %s",
                               r["team_id"], r.get("team_name"), e)
            done += 1
            if done % 25 == 0 or done == len(todo):
                print(f"  crawled {done}/{len(todo)} teams")


# ---------------------------------------------------------------------------
# Aggregation: cache JSON -> tidy CSV
# ---------------------------------------------------------------------------

def aggregate(teams: pd.DataFrame, args) -> pd.DataFrame:
    """Read each selected team's cache file and build the one-row-per-DOI table."""
    rows = []
    n_with_cache = 0
    for r in teams.to_dict("records"):
        cf = cache_path(r["team_id"])
        if not cf.exists():
            continue
        n_with_cache += 1
        rec = json.loads(cf.read_text())
        page_dois: dict[str, list[str]] = rec.get("page_dois", {})

        # Invert page -> [dois] into doi -> [pages].
        doi_pages: dict[str, list[str]] = {}
        for url, dois in page_dois.items():
            for d in dois:
                doi_pages.setdefault(d, []).append(url)

        for doi in rec.get("dois", []):
            pages = doi_pages.get(doi, [])
            rows.append({
                "project_id": r.get("project_id") or "",
                "team_id": r["team_id"],
                "team_name": rec.get("team_name") or r.get("team_name") or "",
                "year": rec.get("year") or r.get("year") or "",
                "doi": doi,
                "doi_url": f"https://doi.org/{doi}",
                "n_source_pages": len(pages),
                "source_pages": ";".join(pages[:MAX_PAGES_LISTED]),
                "wiki_url": rec.get("wiki_url") or r.get("wiki_url") or "",
                "pages_crawled": rec.get("pages_crawled", 0),
                "status": rec.get("status", ""),
            })

    out = pd.DataFrame(rows, columns=[
        "project_id", "team_id", "team_name", "year", "doi", "doi_url",
        "n_source_pages", "source_pages", "wiki_url", "pages_crawled", "status",
    ])
    out = out.sort_values(["year", "team_name", "doi"]).reset_index(drop=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)

    # --- summary ---
    teams_crawled = n_with_cache
    teams_with_dois = out["team_id"].nunique()
    print(f"\nSaved {len(out)} (team, DOI) rows -> {_rel(args.out)}")
    print(f"Teams with a cached crawl: {teams_crawled}")
    print(f"Teams citing >=1 DOI:      {teams_with_dois}")
    print(f"Unique DOIs overall:       {out['doi'].nunique()}")
    if len(out):
        ex = out.iloc[0]
        print(f"\nExample: {ex['team_name']} ({ex['year']}) -> {ex['doi']}")
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Scrape iGEM team wikis for cited DOIs.")
    p.add_argument("--case-study", action="store_true",
                   help="Only crawl carbon-capture case-study teams (case_study_flag).")
    p.add_argument("--year", type=int, nargs="+",
                   help="Only crawl these competition year(s), e.g. --year 2023 2024.")
    p.add_argument("--limit", type=int,
                   help="Only crawl the first N selected teams (handy for testing).")
    p.add_argument("--workers", type=int, default=6,
                   help="Parallel team crawls (default 6). Lower = gentler on iGEM servers.")
    p.add_argument("--delay", type=float, default=0.3,
                   help="Seconds between requests within a team crawl (default 0.3).")
    p.add_argument("--max-pages", type=int, default=40,
                   help="Max sub-pages to fetch per team (default 40).")
    p.add_argument("--refresh", action="store_true",
                   help="Re-crawl teams even if a cache file already exists.")
    p.add_argument("--aggregate-only", action="store_true",
                   help="Skip crawling; just rebuild the CSV from existing caches.")
    p.add_argument("--out", type=Path, default=OUT_PATH,
                   help=f"Output CSV path (default {OUT_PATH.relative_to(REPO_ROOT)}).")
    return p.parse_args()


def run():
    args = parse_args()
    args.out = args.out.resolve()
    print("=== Step 3d: Scrape iGEM wikis for cited DOIs ===\n")
    teams = load_teams(args)
    print(f"Teams in scope after filters: {len(teams)}")

    if not args.aggregate_only:
        run_crawl(teams, args)

    aggregate(teams, args)


if __name__ == "__main__":
    run()
