"""
Step 2 — Ingest patents from the USPTO Open Data Portal (ODP) API.

Synthetic biology has no dedicated IPC/CPC patent classification code.
Keyword-only searches can overestimate activity due to overlap with
general biotechnology (Oldham & Hall, 2018, doi:10.1101/483826).

We adopt the two-layer keyword strategy from van Doren, Koenigstein & Reiss
(2013, doi:10.1007/s11693-013-9121-7): narrow self-identifying terms in Layer 1
for high precision, broader enabling-technology terms in Layer 2. Both layers
are deduplicated and combined into a single corpus.

DATA SOURCE:
  We use the USPTO Open Data Portal (api.uspto.gov), which replaced the old
  PatentsView API (discontinued May 2025) and Lens.org as the authoritative
  programmatic source for US patent data. The ODP Patent File Wrapper API
  provides bibliographic metadata for applications filed on or after 2001.

  Results are filtered to granted utility patents only (applicationTypeCode=UTL,
  grantDate present), ensuring we include only issued patents relevant to
  technology development rather than pending applications or design patents.

  Note: The ODP does not return patent abstract text — only the title
  (inventionTitle) is available from the file wrapper API. This is used
  as the text field for semantic embedding.

  API key: set USPTO_ODP_KEY in .env
  Documentation: https://data.uspto.gov/apis/getting-started

Layer 1 — Core self-identifying keywords (high precision):
    "synthetic biology", "synthetic genomics", "synthetic genome"

Layer 2 — Subfield/enabling keywords (broader, catches adjacent work):
    "genetic circuit", "gene synthesis", "DNA assembly", "BioBrick", etc.

Both layers are deduplicated on patent ID. Each patent carries a
`retrieval_reason` field recording which layer found it first.

Checkpointing: completed layers are saved to data/raw/patents_layer*.json
so the script can be restarted without re-fetching completed layers.
Delete those files to force a full re-fetch.

Usage:
    python scripts/02_ingest_patents.py

Requires:
    USPTO_ODP_KEY set in .env
    Get a free key at https://data.uspto.gov/apis/getting-started
"""

import sys
import json
import time
import logging
from pathlib import Path
from collections import Counter

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import load_config
from src.ingest import odp, normalize
from src.geo.geocode import geocode_dataframe

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

CACHE_DIR  = REPO_ROOT / "data" / "raw"
ABS_CACHE  = CACHE_DIR / "patents_abstracts.json"          # number -> abstract text
GEO_CACHE  = REPO_ROOT / "data" / "geo" / "geocoding_cache.json"   # shared city cache
WEIGHTS_PATH = REPO_ROOT / "data" / "processed" / "patent_city_weights.csv"

# Polite delay between grant-XML abstract downloads (ODP file endpoint).
ABS_DELAY = 0.6


def _load_cache(layer_name: str) -> list[dict] | None:
    """
    Return cached extracted-field records for this layer, or None if absent.

    The cache stores flat dicts in the same shape as odp.extract_fields():
    {patent_id, title, year, city, country, retrieval_reason}
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


def _geo_key(city: str, state: str, country: str) -> tuple[str, str]:
    """(geo_city, geo_country) for the geocoder; US cities carry the state."""
    country = (country or "").upper()
    if country == "US" and state:
        return f"{city}, {state}", country
    return city, country


def _fetch_abstracts(records: list[dict]) -> None:
    """
    Fill rec['abstract'] for every record by downloading its grant XML.

    The ODP bibliographic API has no abstract; each patent's grant XML (linked
    by file_uri) does. Cached by patent number in patents_abstracts.json and
    saved incrementally, so the run is restartable. Patents with no grant-XML
    link (a few older grants) get an empty abstract.
    """
    ABS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(ABS_CACHE.read_text()) if ABS_CACHE.exists() else {}

    # Patents without a grant-XML link can't be fetched: mark empty.
    for r in records:
        if r["number"] and not r.get("file_uri"):
            cache.setdefault(r["number"], "")

    todo = [r for r in records if r["number"] and r.get("file_uri") and r["number"] not in cache]
    print(f"\n--- Fetching abstracts for {len(todo)} patents "
          f"({len(records) - len(todo)} already cached or unavailable) ---")
    for i, r in enumerate(todo, 1):
        xml = odp.fetch_grant_xml(r["file_uri"])
        if xml is None:
            continue                     # transient failure: retry next run
        cache[r["number"]] = odp.extract_abstract_from_grant_xml(xml)
        time.sleep(ABS_DELAY)
        if i % 25 == 0:
            ABS_CACHE.write_text(json.dumps(cache))
            logger.info(f"  abstracts: {i}/{len(todo)} fetched")
    ABS_CACHE.write_text(json.dumps(cache))

    for r in records:
        r["abstract"] = cache.get(r["number"], "") or ""


def _enrich_and_geocode(records: list[dict]) -> list[dict]:
    """
    Add primary city/country/lat/lon, all_cities/all_coords, and return the
    fractional (patent, city) weight rows.

    Every inventor's location is used: each patent contributes a total weight
    of 1, split across the distinct cities of its located inventors (OECD
    REGPAT convention). The first located inventor is the primary point for
    single-dot map placement.
    """
    distinct: set[tuple[str, str]] = set()
    for r in records:
        located = [l for l in (r.get("locations") or []) if l.get("city")]
        counts: Counter = Counter()
        primary = None
        for l in located:
            gc = _geo_key(l["city"], l.get("state", ""), l.get("country", ""))
            counts[gc] += 1
            distinct.add(gc)
            if primary is None:
                primary = l
        r["_counts"] = counts
        if primary:
            r["city"] = primary["city"]
            r["country"] = (primary.get("country") or "").upper()
            r["_primary_geo"] = _geo_key(primary["city"], primary.get("state", ""),
                                         primary.get("country", ""))
        else:
            r["city"], r["country"], r["_primary_geo"] = "", "", None

    # Geocode each distinct inventor city once (shared cache).
    weights: list[dict] = []
    coord: dict[tuple[str, str], tuple] = {}
    if distinct:
        dd = pd.DataFrame(sorted(distinct), columns=["geo_city", "country"])
        print(f"\n--- Geocoding {len(dd)} distinct inventor cities "
              f"(cached in {GEO_CACHE.name}) ---")
        dd = geocode_dataframe(dd, cache_file=GEO_CACHE,
                               city_col="geo_city", country_col="country")
        coord = {(row.geo_city, row.country): (row.lat, row.lon)
                 for row in dd.itertuples()}

    for r in records:
        pg = r.get("_primary_geo")
        r["lat"], r["lon"] = coord.get(pg, (None, None)) if pg else (None, None)
        names, coords = [], []
        n_located = sum(r["_counts"].values())
        for gc, k in r["_counts"].items():
            names.append(gc[0])
            ll = coord.get(gc)
            if ll and ll[0] is not None:
                coords.append([ll[0], ll[1]])
            weights.append({"id": r["patent_id"], "geo_city": gc[0], "country": gc[1],
                            "weight": k / n_located,
                            "lat": ll[0] if ll else None, "lon": ll[1] if ll else None})
        r["all_cities"], r["all_coords"] = names, coords

    return weights


def run():
    cfg = load_config()
    corpus_cfg = cfg["corpus"]

    core_kws     = corpus_cfg["patent_core_keywords"]
    subfield_kws = corpus_cfg["patent_subfield_keywords"]
    max_results  = corpus_cfg["lens_max_results"]   # reusing same config key
    year_min     = corpus_cfg["year_min"]
    year_max     = corpus_cfg.get("year_max")

    print("=== Step 2: Ingest Patents from USPTO Open Data Portal ===\n")
    print(f"Core keywords:     {core_kws}")
    print(f"Subfield keywords: {subfield_kws}")
    print(f"Max results/layer: {max_results}")
    print(f"Year range:        {year_min} – {year_max or 'present'}")
    print(f"Cache dir:         {CACHE_DIR}\n")
    print("(Delete data/raw/patents_layer*.json to force a full re-fetch.)\n")

    seen_ids: dict[str, str] = {}
    raw_records: list[dict] = []

    def _collect_raw(patents: list[dict], reason: str) -> list[dict]:
        """Extract fields, deduplicate by patent_id, and accumulate."""
        extracted = []
        for patent in patents:
            fields = odp.extract_patent_record(patent)
            fields["retrieval_reason"] = reason
            pid = fields.get("patent_id", "")
            if pid and pid in seen_ids:
                continue
            if pid:
                seen_ids[pid] = reason
            raw_records.append(fields)
            extracted.append(fields)
        return extracted

    def _collect_extracted(extracted: list[dict]) -> None:
        """Add already-extracted field dicts from cache, deduplicating."""
        for fields in extracted:
            pid = fields.get("patent_id", "")
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
        patents_l1_raw = odp.search_patents(
            keywords=core_kws,
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
    # Wait between layers if layer 1 was freshly fetched to let the
    # ODP rate limit reset before starting layer 2.
    if cached_l1 is None:
        print("Pausing 30s between layers to respect ODP rate limits...")
        time.sleep(30)

    print("--- Layer 2: Subfield/enabling keywords ---")
    cached_l2 = _load_cache("layer2")
    if cached_l2 is not None:
        print(f"Using cache: {len(cached_l2)} extracted records")
        before = len(raw_records)
        _collect_extracted(cached_l2)
    else:
        patents_l2_raw = odp.search_patents(
            keywords=subfield_kws,
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
    # Enrich: abstracts (for embedding text) + all-inventor geocoding.
    # ------------------------------------------------------------------
    _fetch_abstracts(raw_records)
    weights = _enrich_and_geocode(raw_records)

    # ------------------------------------------------------------------
    # Normalize and save
    # ------------------------------------------------------------------
    patents_df = normalize.normalize_patents_odp(
        raw_records=raw_records,
        carbon_keywords=corpus_cfg["carbon_capture_keywords"],
    )

    output_path = REPO_ROOT / "data" / "processed" / "patents.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    patents_df.to_csv(output_path, index=False)
    pd.DataFrame(weights).to_csv(WEIGHTS_PATH, index=False)

    n_abs = sum(1 for r in raw_records if r.get("abstract"))
    n_geo = patents_df["lat"].notna().sum()
    print(f"\nSaved {len(patents_df)} patents -> {output_path.relative_to(REPO_ROOT)}")
    print(f"Saved {len(weights)} (patent,city) rows -> {WEIGHTS_PATH.relative_to(REPO_ROOT)}")
    print(f"  with abstract:        {n_abs}/{len(patents_df)} ({n_abs/max(len(patents_df),1):.0%})")
    print(f"  with coordinates:     {n_geo}/{len(patents_df)} ({n_geo/max(len(patents_df),1):.0%})")
    print(f"  carbon-capture tagged: {patents_df['case_study_flag'].sum()}")
    print("\nTop countries:")
    print(patents_df["country"].value_counts().head(10).to_string())

    return patents_df


if __name__ == "__main__":
    run()
