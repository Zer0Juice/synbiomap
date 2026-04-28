"""
Step 3d — Fetch part composition edges from the iGEM Registry API.

A composite part is built from one or more sub-parts. This script fetches
the composition for every part in the registry and writes a directed edge
table: parent_part → child_part.

These edges can be used to:
  - identify which parts are foundational (high in-degree)
  - build a team→team knowledge-flow graph (Team B used a part Team A made)
  - analyse reuse patterns across cities and years

This is a long-running fetch (~89,000 API calls at 3s each ≈ 70 hours).
Run it in the background:

    nohup python scripts/03d_fetch_composition.py > logs/composition.log 2>&1 &

It is safe to interrupt and resume at any time — progress is saved to
data/raw/parts/composition_cache.json every 500 parts.

Output
------
  data/processed/part_composition_edges.csv
      Columns: parent, child
      One row per sub-part relationship. Only parts with at least one
      sub-part appear. Parts with no composition data are silently skipped.
"""

import json
import logging
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.ingest.igem import fetch_part_composition, _check_rate_limit_headers, REQUEST_DELAY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

RAW_DIR       = REPO_ROOT / "data" / "raw" / "parts"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

PARTS_CACHE       = RAW_DIR / "parts_cache.jsonl"
COMPOSITION_CACHE = RAW_DIR / "composition_cache.json"
EDGES_OUT         = PROCESSED_DIR / "part_composition_edges.csv"

SAVE_INTERVAL = 500  # flush to disk every N parts


def load_all_uuids() -> list[tuple[str, str]]:
    """Return (uuid, part_name) for every part in the cache."""
    parts = []
    with open(PARTS_CACHE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            p = json.loads(line)
            uuid = p.get("uuid", "")
            name = p.get("name", "")
            if uuid and name:
                parts.append((uuid, name))
    return parts


def run():
    if not PARTS_CACHE.exists():
        print("ERROR: parts_cache.jsonl not found. Run 03b_fetch_parts.py first.")
        return

    all_parts = load_all_uuids()
    logger.info(f"Loaded {len(all_parts)} parts from cache.")

    # Load existing composition cache.
    # Format: {part_uuid: [child_name, ...]}  — empty list means no composition.
    if COMPOSITION_CACHE.exists():
        with open(COMPOSITION_CACHE) as f:
            comp_cache: dict = json.load(f)
    else:
        comp_cache = {}

    done = set(comp_cache.keys())
    to_fetch = [(uuid, name) for uuid, name in all_parts if uuid not in done]

    logger.info(f"Already fetched: {len(done)}")
    logger.info(f"Remaining:       {len(to_fetch)}")

    if not to_fetch:
        logger.info("Composition cache complete — writing edges CSV.")
    else:
        session = requests.Session()

        for i, (uuid, name) in enumerate(to_fetch):
            components = fetch_part_composition(uuid, session, delay=REQUEST_DELAY)
            children = [
                c.get("componentName", "")
                for c in components
                if c.get("componentName") and c.get("componentName") != name
            ]
            comp_cache[uuid] = children

            if (i + 1) % SAVE_INTERVAL == 0:
                with open(COMPOSITION_CACHE, "w") as f:
                    json.dump(comp_cache, f)
                pct = (len(done) + i + 1) / len(all_parts) * 100
                logger.info(f"{i+1}/{len(to_fetch)} done ({pct:.1f}% total) — saved.")

        # Final save
        with open(COMPOSITION_CACHE, "w") as f:
            json.dump(comp_cache, f)
        logger.info("Fetch complete.")

    # Build edge table from cache
    # Build a uuid → name lookup for resolving child names (children are
    # already stored as BBa_ names, not UUIDs, so no lookup needed).
    uuid_to_name = {uuid: name for uuid, name in all_parts}

    edges = []
    for uuid, children in comp_cache.items():
        parent_name = uuid_to_name.get(uuid, "")
        if not parent_name:
            continue
        for child in children:
            if child:
                edges.append({"parent": parent_name, "child": child})

    edges_df = pd.DataFrame(edges) if edges else pd.DataFrame(columns=["parent", "child"])
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    edges_df.to_csv(EDGES_OUT, index=False)

    composite_parts = edges_df["parent"].nunique() if not edges_df.empty else 0
    logger.info(f"Composition edges: {len(edges_df)} ({composite_parts} composite parts)")
    logger.info(f"Saved to {EDGES_OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    run()
