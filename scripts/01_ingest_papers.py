"""
Step 1 — Ingest papers from OpenAlex using a three-layer corpus strategy.

Layer 1 — Core keywords (e.g. "synthetic biology", "synthetic genome")
    High-precision retrieval. Papers using these terms almost certainly
    belong to the synthetic biology field.

Layer 2 — Subfield keywords (e.g. "BioBrick", "repressilator", "minimal genome")
    Catches foundational work that predates the "synthetic biology" label
    or comes from adjacent subfields.

Layer 3 — Citation expansion from Layer 1 seed papers
    Backward snowball: papers that Layer 1 papers cite.
    Forward snowball: papers that cite Layer 1 papers.
    Captures related work that uses different terminology.

All three layers are deduplicated on OpenAlex ID. Each paper carries a
`retrieval_reason` field recording which layer found it first.

Strategy based on:
    Shapira, Kwon & Youtie (2017). "Tracking the emergence of synthetic
    biology." Scientometrics 112(3), 1457–1478.

Usage:
    python scripts/01_ingest_papers.py
"""

import sys
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import openalex, normalize

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


def run():
    cfg = load_config()
    corpus_cfg = cfg["corpus"]
    expansion_cfg = corpus_cfg.get("citation_expansion", {})

    print("=== Step 1: Ingest Papers from OpenAlex ===\n")
    print(f"Core keywords:     {corpus_cfg['core_keywords']}")
    print(f"Subfield keywords: {corpus_cfg['subfield_keywords']}")
    print(f"Citation expansion enabled: {expansion_cfg.get('enabled', False)}\n")

    # seen_ids tracks which papers we already have so we can deduplicate.
    # The value is the retrieval_reason the paper was first found by.
    seen_ids: dict[str, str] = {}
    raw_records: list[dict] = []

    def _collect(work: dict, reason: str):
        """Add a work to raw_records if we haven't seen its ID yet.

        We skip papers without an abstract — the API filter (has_abstract:true)
        should already exclude them, but this is a safety check.
        """
        fields = openalex.extract_fields(work)
        fields["retrieval_reason"] = reason

        # Skip if no abstract (can't embed or cluster without text)
        if not fields.get("abstract", "").strip():
            return

        oa_id = fields.get("openalex_id", "")
        if oa_id and oa_id in seen_ids:
            return  # already in corpus from an earlier layer
        if oa_id:
            seen_ids[oa_id] = reason
        raw_records.append(fields)

    # ------------------------------------------------------------------
    # Layer 1: Core keywords
    # ------------------------------------------------------------------
    print("--- Layer 1: Core keywords ---")
    for work in openalex.search_papers(
        keywords=corpus_cfg["core_keywords"],
        year_min=corpus_cfg["year_min"],
        year_max=corpus_cfg.get("year_max"),
        max_results=corpus_cfg["openalex_max_results"],
        retrieval_reason="core_keyword",
    ):
        _collect(work, "core_keyword")

    layer1_count = len(raw_records)
    print(f"Layer 1 total: {layer1_count} papers\n")

    # ------------------------------------------------------------------
    # Layer 2: Subfield keywords
    # ------------------------------------------------------------------
    print("--- Layer 2: Subfield keywords ---")
    before = len(raw_records)
    for work in openalex.search_papers(
        keywords=corpus_cfg["subfield_keywords"],
        year_min=corpus_cfg["year_min"],
        year_max=corpus_cfg.get("year_max"),
        max_results=corpus_cfg["openalex_max_results"],
        retrieval_reason="subfield_keyword",
    ):
        _collect(work, "subfield_keyword")

    layer2_new = len(raw_records) - before
    print(f"Layer 2 added {layer2_new} new papers (total: {len(raw_records)})\n")

    # ------------------------------------------------------------------
    # Layer 3: Citation expansion from Layer 1 seed papers
    # ------------------------------------------------------------------
    if expansion_cfg.get("enabled", False):
        print("--- Layer 3: Citation expansion ---")

        # Get the OpenAlex IDs of all Layer 1 papers (our seed set)
        seed_ids = [
            oa_id for oa_id, reason in seen_ids.items()
            if reason == "core_keyword"
        ]
        print(f"Expanding from {len(seed_ids)} Layer 1 seed papers...")

        max_ref = expansion_cfg.get("max_references_per_paper", 200)
        max_cit = expansion_cfg.get("max_citing_per_paper", 200)
        before = len(raw_records)

        # Backward snowball: papers cited by each seed
        print("  Backward snowball (references)...")
        all_ref_ids: list[str] = []
        for i, seed_id in enumerate(seed_ids):
            ref_ids = openalex.get_referenced_work_ids(seed_id)
            all_ref_ids.extend(ref_ids[:max_ref])
            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{len(seed_ids)} seeds processed...")

        # Deduplicate reference IDs before fetching
        new_ref_ids = [rid for rid in set(all_ref_ids) if rid not in seen_ids]
        print(f"  Fetching {len(new_ref_ids)} unique referenced works...")
        for work in openalex.fetch_works_by_ids(new_ref_ids, retrieval_reason="citation_backward"):
            _collect(work, "citation_backward")

        # Forward snowball: papers that cite each seed
        print("  Forward snowball (citing works)...")
        for i, seed_id in enumerate(seed_ids):
            n = 0
            for work in openalex.get_citing_works(seed_id, max_results=max_cit):
                _collect(work, "citation_forward")
                n += 1
            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{len(seed_ids)} seeds processed...")

        layer3_new = len(raw_records) - before
        print(f"Layer 3 added {layer3_new} new papers (total: {len(raw_records)})\n")
    else:
        print("--- Layer 3: Citation expansion SKIPPED (set citation_expansion.enabled: true to run) ---\n")

    # ------------------------------------------------------------------
    # Summary of retrieval reasons
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
    papers_df = normalize.normalize_papers(
        raw_records=raw_records,
        carbon_keywords=corpus_cfg["carbon_capture_keywords"],
    )

    print(f"Carbon capture tagged: {papers_df['case_study_flag'].sum()} papers")

    # Note: city/lat/lon are NOT filled here. OpenAlex works responses contain
    # dehydrated institution objects that lack geo data. Run the next step:
    #   python scripts/geocode_papers.py
    # That script uses the institution_ids column saved here to batch-fetch
    # full institution objects from OpenAlex, which do include city/lat/lon.

    output_path = REPO_ROOT / "data" / "processed" / "papers.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    papers_df.to_csv(output_path, index=False)
    print(f"Saved to {output_path.relative_to(REPO_ROOT)}")

    print(f"\nYear range: {papers_df['year'].min()} — {papers_df['year'].max()}")
    print(f"Institution IDs saved: {(papers_df['institution_ids'] != '').sum()} / {len(papers_df)} papers")
    print("Run scripts/geocode_papers.py next to fill in city/lat/lon.")
    print("\nTop countries:")
    print(papers_df["country"].value_counts().head(10).to_string())

    # Citation link summary
    papers_with_citations = (papers_df["cited_works"].str.len() > 0).sum()
    total_citation_links = papers_df["cited_works"].dropna().apply(
        lambda x: len(x.split(";")) if x else 0
    ).sum()
    print(f"\nCitation links: {papers_with_citations} papers have cited_works "
          f"({total_citation_links:,} total edges)")

    return papers_df


if __name__ == "__main__":
    run()
