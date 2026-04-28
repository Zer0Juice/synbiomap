"""
Step 2 — Ingest patents from Lens.org using a layered keyword strategy.

Synthetic biology has no dedicated IPC/CPC patent classification code.
Keyword-only searches can overestimate activity due to overlap with
general biotechnology (Oldham & Hall, 2018, doi:10.1101/483826).

We adopt the keyword-layer strategy from van Doren, Koenigstein & Reiss
(2013, doi:10.1007/s11693-013-9121-7), searching full patent text with
two keyword groups. IPC filtering is not used here because the Lens.org
standard API plan does not expose IPC classification symbols as a
searchable field (see src/ingest/lens.py for details).

DATA SOURCE NOTE:
  We use the Lens.org API rather than PatentsView/USPTO directly.
  Lens.org aggregates USPTO data (plus EP, WO, and other jurisdictions)
  and provides it through a free REST API. The PatentsView API (the
  previous standard for programmatic USPTO access) was discontinued in
  2024. The new USPTO Open Data Portal (data.uspto.gov) is a browser-only
  application with no accessible REST API at time of writing.

  To scope the corpus to US patents specifically, set the `lens_us_only`
  flag in config/settings.yaml to add a jurisdiction filter.

Layer 1 — Core self-identifying keywords (high precision):
    "synthetic biology", "synthetic genomics", "synthetic genome"

Layer 2 — Subfield/enabling keywords (broader, catches adjacent work):
    "genetic circuit", "gene synthesis", "DNA assembly", "BioBrick", etc.

Both layers are deduplicated on Lens ID. Each patent carries a
`retrieval_reason` field recording which layer found it first.

Checkpointing: completed layers are saved to data/raw/patents_layer*.json
so that the script can be restarted without re-fetching completed layers.
Delete those files to force a full re-fetch.

Usage:
    python scripts/02_ingest_patents.py

Requires:
    LENS_API_TOKEN set in .env
    Get a free token at https://www.lens.org/lens/user/subscriptions
"""

import sys
import json
import time
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import lens, normalize

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

CACHE_DIR = REPO_ROOT / "data" / "raw"


def _load_cache(layer_name: str) -> list[dict] | None:
    """
    Return cached extracted-field records for this layer, or None if not cached.

    The cache stores dicts in the same shape as lens.extract_fields() output:
    {lens_id, title, abstract, year, city, country, retrieval_reason}
    This format can be seeded from an existing patents.csv if needed.
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

    ipc_codes      = corpus_cfg["patent_ipc_codes"]
    core_kws       = corpus_cfg["patent_core_keywords"]
    subfield_kws   = corpus_cfg["patent_subfield_keywords"]
    max_results    = corpus_cfg["lens_max_results"]
    year_min       = corpus_cfg["year_min"]
    year_max       = corpus_cfg.get("year_max")

    print("=== Step 2: Ingest Patents from Lens.org ===\n")
    print(f"Core keywords:     {core_kws}")
    print(f"Subfield keywords: {subfield_kws}")
    print(f"Max results/layer: {max_results}")
    print(f"Cache dir:         {CACHE_DIR}\n")
    print("(Delete data/raw/patents_layer*.json to force a full re-fetch.)\n")

    seen_ids: dict[str, str] = {}
    raw_records: list[dict] = []

    def _collect_raw(patents: list[dict], reason: str) -> list[dict]:
        """Extract fields from raw API records, deduplicate, and accumulate."""
        extracted = []
        for patent in patents:
            fields = lens.extract_fields(patent)
            fields["retrieval_reason"] = reason
            lid = fields.get("lens_id", "")
            if lid and lid in seen_ids:
                continue
            if lid:
                seen_ids[lid] = reason
            raw_records.append(fields)
            extracted.append(fields)
        return extracted

    def _collect_extracted(extracted: list[dict]) -> None:
        """Add already-extracted field dicts (from cache), deduplicating."""
        for fields in extracted:
            lid = fields.get("lens_id", "")
            if lid and lid in seen_ids:
                continue
            if lid:
                seen_ids[lid] = fields.get("retrieval_reason", "unknown")
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
        patents_l1_raw = lens.search_patents(
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
    # Wait between layers if layer 1 was freshly fetched (not cached),
    # to give the rate limit time to reset before starting layer 2.
    if cached_l1 is None:
        print("Pausing 60s between layers to respect Lens.org rate limits...")
        time.sleep(60)

    print("--- Layer 2: Subfield/enabling keywords ---")
    cached_l2 = _load_cache("layer2")
    if cached_l2 is not None:
        print(f"Using cache: {len(cached_l2)} extracted records")
        before = len(raw_records)
        _collect_extracted(cached_l2)
    else:
        patents_l2_raw = lens.search_patents(
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
