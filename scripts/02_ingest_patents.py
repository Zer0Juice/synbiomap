"""
Step 2 — Ingest patents from Lens.org using IPC codes + keyword strategy.

Synthetic biology has no dedicated IPC/CPC patent classification code.
Keyword-only searches radically overestimate activity due to overlap with
general biotechnology (Oldham & Hall, 2018, doi:10.1101/483826).

We follow van Doren, Koenigstein & Reiss (2013, doi:10.1007/s11693-013-9121-7):
combine an IPC class scope filter with keyword groups using AND logic.

Layer 1 — Core keywords + IPC filter
    "synthetic biology", "synthetic genomics", "synthetic genome"
    AND IPC: C12N, C12P, C12Q, C12S, C40B

Layer 2 — Subfield/enabling keywords + IPC filter
    "genetic circuit", "gene synthesis", "DNA assembly", "BioBrick", etc.
    AND IPC: same scope filter

Both layers are deduplicated on Lens ID. Each patent carries a
`retrieval_reason` field recording which layer found it first.

Usage:
    python scripts/02_ingest_patents.py

Requires:
    LENS_API_TOKEN set in .env
    Get a free token at https://www.lens.org/lens/user/subscriptions
"""

import sys
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import lens, normalize

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


def run():
    cfg = load_config()
    corpus_cfg = cfg["corpus"]

    ipc_codes      = corpus_cfg["patent_ipc_codes"]
    core_kws       = corpus_cfg["patent_core_keywords"]
    subfield_kws   = corpus_cfg["patent_subfield_keywords"]
    max_results    = corpus_cfg["lens_max_results"]
    year_min       = corpus_cfg["year_min"]
    year_max       = corpus_cfg.get("year_max")

    print("=== Step 2: Ingest Patents from Lens.org ===\n")
    print(f"IPC scope filter:  {ipc_codes}")
    print(f"Core keywords:     {core_kws}")
    print(f"Subfield keywords: {subfield_kws}\n")

    seen_ids: dict[str, str] = {}
    raw_records: list[dict] = []

    def _collect(patents: list[dict], reason: str):
        """Deduplicate by Lens ID; first layer to find a patent wins."""
        for patent in patents:
            fields = lens.extract_fields(patent)
            fields["retrieval_reason"] = reason
            lid = fields.get("lens_id", "")
            if lid and lid in seen_ids:
                continue
            if lid:
                seen_ids[lid] = reason
            raw_records.append(fields)

    # ------------------------------------------------------------------
    # Layer 1: Core keywords + IPC filter
    # ------------------------------------------------------------------
    print("--- Layer 1: Core keywords + IPC filter ---")
    patents_l1 = lens.search_patents(
        keywords=core_kws,
        ipc_codes=ipc_codes,
        year_min=year_min,
        year_max=year_max,
        max_results=max_results,
        retrieval_reason="core_keyword",
    )
    _collect(patents_l1, "core_keyword")
    print(f"Layer 1 total: {len(raw_records)} patents\n")

    # ------------------------------------------------------------------
    # Layer 2: Subfield/enabling keywords + IPC filter
    # ------------------------------------------------------------------
    print("--- Layer 2: Subfield/enabling keywords + IPC filter ---")
    before = len(raw_records)
    patents_l2 = lens.search_patents(
        keywords=subfield_kws,
        ipc_codes=ipc_codes,
        year_min=year_min,
        year_max=year_max,
        max_results=max_results,
        retrieval_reason="subfield_keyword",
    )
    _collect(patents_l2, "subfield_keyword")
    print(f"Layer 2 added {len(raw_records) - before} new patents (total: {len(raw_records)})\n")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    reason_counts: dict[str, int] = {}
    for rec in raw_records:
        r = rec.get("retrieval_reason", "unknown")
        reason_counts[r] = reason_counts.get(r, 0) + 1

    print("Retrieval breakdown:")
    for reason, count in sorted(reason_counts.items()):
        print(f"  {reason:<25} {count}")
    print(f"  {'TOTAL':<25} {len(raw_records)}\n")

    # ------------------------------------------------------------------
    # Normalize and save
    # ------------------------------------------------------------------
    patents_df = normalize.normalize_patents(
        raw_records=raw_records,
        carbon_keywords=corpus_cfg["carbon_capture_keywords"],
    )

    print(f"Carbon capture tagged: {patents_df['case_study_flag'].sum()} patents")

    output_path = REPO_ROOT / "data" / "processed" / "patents.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    patents_df.to_csv(output_path, index=False)
    print(f"Saved to {output_path.relative_to(REPO_ROOT)}")

    print("\nTop countries:")
    print(patents_df["country"].value_counts().head(10).to_string())

    return patents_df


if __name__ == "__main__":
    run()
