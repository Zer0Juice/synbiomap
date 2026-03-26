"""
Step 3b — Fetch iGEM parts and build part relationship edge lists.

This script pulls parts data from two sources:

  1. iGEM Parts Registry (parts.igem.org/partsdb/)
     Bulk CSV export of all submitted parts, including part name, type,
     description, submitting team, and year. Also includes a "uses" column
     for composite parts listing their sub-parts directly.

  2. SynBioHub (synbiohub.org) via SPARQL
     SynBioHub mirrors the iGEM Registry in SBOL2 format, which explicitly
     encodes part composition as a graph. We query it to get composite →
     sub-part edges that may be more complete than the "uses" column.

Outputs
-------
  data/raw/parts/igem_parts.csv
      One row per part. All metadata from the Registry.

  data/processed/part_team_edges.csv
      Columns: part_name, team_name, year
      Links each part to the team that submitted it.
      Join key between parts.csv and projects.csv.

  data/processed/part_composition_edges.csv
      Columns: parent, child
      A directed edge means the parent (composite) part contains the child
      (sub-part). Analogous to a citation: the parent "builds on" the child.

Usage:
    python scripts/03b_fetch_parts.py

Note:
    The Parts Registry API is lightly documented and occasionally slow.
    The SynBioHub SPARQL query may take several minutes for the full corpus.
    Both steps cache to disk so re-runs are fast.
"""

import sys
import logging
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.ingest import igem

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


def run():
    print("=== Step 3b: Fetch iGEM Parts and Build Edge Lists ===\n")

    raw_parts_path = REPO_ROOT / "data" / "raw" / "parts" / "igem_parts.csv"
    processed_dir = REPO_ROOT / "data" / "processed"
    raw_parts_path.parent.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Fetch parts from the iGEM Parts Registry
    # ------------------------------------------------------------------
    # If a cached raw file already exists, skip the fetch.
    if raw_parts_path.exists():
        print(f"Raw parts file already exists at {raw_parts_path.relative_to(REPO_ROOT)}")
        print("Loading from cache. Delete the file to re-fetch.\n")
        parts_df = pd.read_csv(raw_parts_path, dtype=str)
    else:
        print("Fetching parts from iGEM Parts Registry...")
        print("(This may take a few minutes — the Registry returns ~50,000+ parts)\n")

        raw_records = list(igem.fetch_parts_from_registry())

        if not raw_records:
            print("ERROR: No parts returned from the Parts Registry.")
            print("The API may be temporarily unavailable.")
            print("Try downloading manually from parts.igem.org/partsdb/search.cgi?q=type:all&return=csv")
            print("and saving to data/raw/parts/igem_parts.csv")
            return

        parts_df = pd.DataFrame(raw_records)
        parts_df.to_csv(raw_parts_path, index=False)
        print(f"Saved {len(parts_df)} parts to {raw_parts_path.relative_to(REPO_ROOT)}\n")

    print(f"Parts loaded: {len(parts_df)}")
    print(f"Part types:\n{parts_df['part_type'].value_counts().head(10).to_string()}\n")

    # ------------------------------------------------------------------
    # 2. Build part → team edge list (from the parts CSV directly)
    # ------------------------------------------------------------------
    print("Building part → team edges...")
    part_team_edges = igem.build_part_team_edges(parts_df)
    part_team_path = processed_dir / "part_team_edges.csv"
    part_team_edges.to_csv(part_team_path, index=False)
    print(f"Saved {len(part_team_edges)} part-team edges to {part_team_path.relative_to(REPO_ROOT)}\n")

    # ------------------------------------------------------------------
    # 3. Build composite part → sub-part edges
    # ------------------------------------------------------------------
    # Strategy: prefer the "uses" column from the Registry CSV (fast, no
    # extra requests) and supplement with SynBioHub SPARQL (more complete).

    composition_path = processed_dir / "part_composition_edges.csv"

    edges_from_registry = _build_composition_from_uses_column(parts_df)
    print(f"Composition edges from Registry 'uses' column: {len(edges_from_registry)}")

    # SynBioHub SPARQL — fetch and merge
    print("\nFetching composition edges from SynBioHub SPARQL...")
    print("(This queries the iGEM collection for SBOL2 component relationships)")
    edges_from_synbiohub = igem.fetch_composition_edges_from_synbiohub()
    print(f"Composition edges from SynBioHub: {len(edges_from_synbiohub)}")

    # Merge and deduplicate
    all_edges = pd.concat([
        edges_from_registry,
        pd.DataFrame(edges_from_synbiohub),
    ], ignore_index=True).drop_duplicates(subset=["parent", "child"])

    all_edges.to_csv(composition_path, index=False)
    print(f"\nSaved {len(all_edges)} unique composition edges to {composition_path.relative_to(REPO_ROOT)}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    composite_parts = all_edges["parent"].nunique()
    print(f"\nComposite parts (have at least one sub-part): {composite_parts}")
    print(f"Unique sub-parts referenced: {all_edges['child'].nunique()}")

    # How many composition edges link to parts we have in our corpus?
    known_parts = set(parts_df["part_name"].dropna())
    internal_edges = all_edges[
        all_edges["parent"].isin(known_parts) & all_edges["child"].isin(known_parts)
    ]
    print(f"Edges where both parent and child are in our corpus: {len(internal_edges)}")
    print("\nDone.")


def _build_composition_from_uses_column(parts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse the 'uses' column from the Parts Registry CSV into an edge list.

    The 'uses' column contains semicolon-separated sub-part names for
    composite parts (e.g. "BBa_B0034;BBa_E0040"). We explode this into
    one row per parent-child pair.
    """
    rows = []
    if "uses" not in parts_df.columns:
        logger.warning("No 'uses' column found in parts data — skipping Registry composition edges")
        return pd.DataFrame(columns=["parent", "child"])

    for _, row in parts_df.iterrows():
        parent = str(row.get("part_name", "") or "").strip()
        uses_str = str(row.get("uses", "") or "").strip()
        if not parent or not uses_str:
            continue
        for child in uses_str.split(";"):
            child = child.strip()
            if child and child != parent:
                rows.append({"parent": parent, "child": child})

    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["parent", "child"])


if __name__ == "__main__":
    run()
