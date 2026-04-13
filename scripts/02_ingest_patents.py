"""
Step 2 — Ingest patents from PatentsView using a layered keyword strategy.

PatentsView (https://patentsview.org) is the USPTO's open-data API for US
patents. It is free, requires no API key, and provides stable, citable access
to US patent data. Coverage: all US-granted patents from 1976 to present.

Scope note: PatentsView covers US patents only. This introduces a geographic
bias toward US assignees, but the US is the largest single jurisdiction for
synthetic biology patents (Oldham & Hall, 2018, doi:10.1101/483826), and the
reproducibility benefits of a no-auth, open-government API outweigh the
coverage trade-off for a thesis project.

Synthetic biology has no dedicated IPC/CPC patent classification code.
Keyword-only searches can overestimate activity due to overlap with general
biotechnology (Oldham & Hall, 2018). We adopt the keyword-layer strategy
from van Doren, Koenigstein & Reiss (2013, doi:10.1007/s11693-013-9121-7),
searching patent titles and abstracts with two keyword groups.

Layer 1 — Core self-identifying keywords (high precision):
    "synthetic biology", "synthetic genomics", "synthetic genome"

Layer 2 — Subfield/enabling keywords (broader, catches adjacent work):
    "genetic circuit", "gene synthesis", "DNA assembly", "BioBrick", etc.

Both layers are deduplicated on USPTO patent number. Each patent carries a
`retrieval_reason` field recording which layer found it first.

Checkpointing: completed layers are saved to data/raw/patents_layer*.json
so that the script can be restarted without re-fetching completed layers.
Delete those files to force a full re-fetch.

Usage:
    python scripts/02_ingest_patents.py

No credentials required. PatentsView is fully open.
"""

import sys
import json
import time
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import patentsview, normalize

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

CACHE_DIR = REPO_ROOT / "data" / "raw"


def _load_cache(layer_name: str) -> list[dict] | None:
    """
    Return cached extracted-field records for this layer, or None if not cached.

    The cache stores dicts in the same shape as patentsview.extract_fields():
    {patent_number, title, abstract, year, city, country, retrieval_reason}
    """
    path = CACHE_DIR / f"patents_{layer_name}.json"
    if path.exists():
        logger.info(f"Loading cached {layer_name} from {path.name}")
        with open(path) as f:
            return json.load(f)
    return None


def _save_cache(layer_name: str, extracted_records: list[dict]) -> None:
    """Save already-extracted field dicts for this layer to disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"patents_{layer_name}.json"
    with open(path, "w") as f:
        json.dump(extracted_records, f)
    logger.info(f"Cached {len(extracted_records)} records → {path.name}")


def run():
    cfg = load_config()
    corpus_cfg = cfg["corpus"]

    ipc_codes     = corpus_cfg["patent_ipc_codes"]
    core_kws      = corpus_cfg["patent_core_keywords"]
    subfield_kws  = corpus_cfg["patent_subfield_keywords"]
    max_results   = corpus_cfg["patentsview_max_results"]
    year_min      = corpus_cfg["year_min"]
    year_max      = corpus_cfg.get("year_max")

    print("=== Step 2: Ingest Patents from PatentsView ===\n")
    print(f"Core keywords:     {core_kws}")
    print(f"Subfield keywords: {subfield_kws}")
    print(f"Max results/layer: {max_results}")
    print(f"Cache dir:         {CACHE_DIR}\n")
    print("(Delete data/raw/patents_layer*.json to force a full re-fetch.)\n")
    print("Note: PatentsView covers US patents only (USPTO grants since 1976).\n")

    seen_ids: dict[str, str] = {}
    raw_records: list[dict] = []

    def _collect_raw(patents: list[dict], reason: str) -> list[dict]:
        """Extract fields from raw API records, deduplicate, and accumulate."""
        extracted = []
        for patent in patents:
            fields = patentsview.extract_fields(patent)
            fields["retrieval_reason"] = reason
            pid = fields.get("patent_number", "")
            if pid and pid in seen_ids:
                continue
            if pid:
                seen_ids[pid] = reason
            raw_records.append(fields)
            extracted.append(fields)
        return extracted

    def _collect_extracted(extracted: list[dict]) -> None:
        """Add already-extracted field dicts (from cache), deduplicating."""
        for fields in extracted:
            pid = fields.get("patent_number", "")
            if pid and pid in seen_ids:
                continue
            if pid:
                seen_ids[pid] = fields.get("retrieval_reason", "unknown")
            raw_records.append(fields)

    # ------------------------------------------------------------------
    # Layer 1: Core keywords
    # ------------------------------------------------------------------
    print("--- Layer 1: Core keywords ---")
    cached_l1 = _load_cache("layer1")
    if cached_l1 is not None:
        print(f"Using cache: {len(cached_l1)} extracted records")
        _collect_extracted(cached_l1)
    else:
        patents_l1_raw = patentsview.search_patents(
            keywords=core_kws,
            ipc_codes=ipc_codes,
            year_min=year_min,
            year_max=year_max,
            max_results=max_results,
            retrieval_reason="core_keyword",
        )
        extracted_l1 = _collect_raw(patents_l1_raw, "core_keyword")
        _save_cache("layer1", extracted_l1)

    print(f"Layer 1 total: {len(raw_records)} patents\n")

    # ------------------------------------------------------------------
    # Layer 2: Subfield/enabling keywords
    # ------------------------------------------------------------------
    # Pause between layers if layer 1 was freshly fetched (not cached),
    # to avoid hitting PatentsView rate limits on rapid successive queries.
    if cached_l1 is None:
        print("Pausing 10s between layers...")
        time.sleep(10)

    print("--- Layer 2: Subfield/enabling keywords ---")
    cached_l2 = _load_cache("layer2")
    if cached_l2 is not None:
        print(f"Using cache: {len(cached_l2)} extracted records")
        before = len(raw_records)
        _collect_extracted(cached_l2)
    else:
        patents_l2_raw = patentsview.search_patents(
            keywords=subfield_kws,
            ipc_codes=ipc_codes,
            year_min=year_min,
            year_max=year_max,
            max_results=max_results,
            retrieval_reason="subfield_keyword",
        )
        before = len(raw_records)
        extracted_l2 = _collect_raw(patents_l2_raw, "subfield_keyword")
        _save_cache("layer2", extracted_l2)

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
