"""
Step 3f — BLAST BioBrick sequences against NCBI patent sequence database.

Checks whether BioBrick DNA sequences from the iGEM Registry appear (or have
close homologs) in patent sequence databases. Uses NCBI BLAST against the
'patsq' database (patent nucleotide sequences from USPTO, EPO, and WIPO).

This gives direct sequence-level evidence — much stronger than text similarity
— that a specific biological part was incorporated into a patented invention.

Batch approach
--------------
Instead of submitting one sequence at a time (which takes 17–34 hours for the
carbon-capture subset), this script submits sequences in batches of 50 using
the NCBI BLAST URL API. NCBI processes the whole batch as one job and returns
results for all sequences together. This reduces the carbon-capture run to
roughly 1–3 hours.

How it works:
  1. Group sequences into batches of BATCH_SIZE (default 50)
  2. POST each batch as a multi-FASTA to the NCBI BLAST URL API
  3. Receive a Request ID (RID) — NCBI's reference for this job
  4. Poll the API every 30 seconds until the job is done
  5. Download XML results containing hits for all sequences in the batch
  6. Cache the XML so re-runs skip completed batches
  7. Parse all cached results and write patent_sequence_hits.csv

NCBI BLAST URL API reference:
  https://blast.ncbi.nlm.nih.gov/doc/blast-help/urlapi.html

Caching
-------
Each completed batch is saved to data/raw/blast/patsq/batch_{N:04d}.xml.
Re-runs skip batches whose cache file already exists, so the script is safe
to interrupt and resume at any point.

Usage
-----
    # Carbon-capture parts (default, ~1–3 hours):
    python scripts/03f_blast_patent_sequences.py

    # All parts with sequences (1–4 days, not recommended on free NCBI):
    python scripts/03f_blast_patent_sequences.py --filter all

    # Single named part (for testing):
    python scripts/03f_blast_patent_sequences.py --part BBa_K1172301

    # Change batch size or identity threshold:
    python scripts/03f_blast_patent_sequences.py --batch-size 25 --min-identity 85

Rate limits
-----------
With an NCBI API key (NCBI_API_KEY in .env) you may submit up to 10 requests
per second. Each batch submission counts as one request. Polling also counts.
The script adds a short delay between submissions to stay within limits.

References
----------
- Altschul et al. (1990) Basic local alignment search tool. J Mol Biol.
  doi:10.1016/S0022-2836(05)80360-2
- NCBI BLAST URL API: https://blast.ncbi.nlm.nih.gov/doc/blast-help/urlapi.html
- patsq: NCBI patent nucleotide sequence database (USPTO/EPO/WIPO deposits)
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from Bio.Blast import NCBIXML

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PARTS_CACHE = REPO_ROOT / "data" / "raw" / "parts" / "parts_cache.jsonl"
PARTS_CSV   = REPO_ROOT / "data" / "processed" / "parts.csv"
BLAST_CACHE = REPO_ROOT / "data" / "raw" / "blast" / "patsq"
HITS_OUT    = REPO_ROOT / "data" / "processed" / "patent_sequence_hits.csv"

# ---------------------------------------------------------------------------
# BLAST settings
# ---------------------------------------------------------------------------
BLAST_URL        = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi"
BLAST_PROGRAM    = "blastn"   # nucleotide vs nucleotide
BLAST_DATABASE   = "patsq"   # NCBI patent nucleotide sequence database
BLAST_HITLIST    = 25        # max hits returned per query sequence
BLAST_EXPECT     = 1e-5      # E-value cutoff — only report statistically significant hits
MIN_SEQ_LENGTH   = 50        # skip sequences shorter than this (too many spurious hits)
MAX_SEQ_LENGTH   = 10_000    # skip very long sequences (server timeouts)
DEFAULT_BATCH    = 50        # sequences per API submission
DEFAULT_MIN_ID   = 90.0      # minimum percent identity to report a hit
POLL_INTERVAL    = 30        # seconds between status checks
POLL_TIMEOUT     = 600       # give up after this many seconds waiting for one batch

# ---------------------------------------------------------------------------
# Carbon-capture keyword filter
# ---------------------------------------------------------------------------
CARBON_CAPTURE_KEYWORDS = [
    "carbon", "co2", "carbon dioxide", "fixation", "carbonic",
    "rubisco", "ribulose", "carboxylase", "oxygenase",
    "capture", "sequestration", "calvin", "cbb cycle",
    "bicarbonate", "formate", "formate dehydrogenase", "fdh",
    "methanol", "methanotroph", "photorespiration",
]


# ---------------------------------------------------------------------------
# Load sequences from parts_cache.jsonl
# ---------------------------------------------------------------------------

def load_sequences(cache_file: Path) -> dict[str, str]:
    """
    Load part_name → DNA sequence from the iGEM Registry parts cache.

    The cache is a newline-delimited JSON file where each line is a full
    part object. The 'sequence' field holds the DNA string, or None if the
    part has no deposited sequence.
    """
    if not cache_file.exists():
        raise FileNotFoundError(
            f"Parts cache not found: {cache_file}\n"
            "Run scripts/03b_fetch_parts.py first."
        )
    sequences = {}
    with open(cache_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                part = json.loads(line)
                name = part.get("name", "")
                seq  = part.get("sequence", "")
                if name and seq:
                    sequences[name] = seq.upper().strip()
            except json.JSONDecodeError:
                continue
    logger.info(f"Loaded sequences for {len(sequences)} parts")
    return sequences


# ---------------------------------------------------------------------------
# Filter parts to BLAST
# ---------------------------------------------------------------------------

def filter_parts(
    parts_df: pd.DataFrame,
    sequences: dict[str, str],
    mode: str,
    part_name: str | None,
) -> list[tuple[str, str]]:
    """
    Return a list of (part_name, sequence) pairs to BLAST.

    Applies the chosen filter mode, then keeps only parts that have a
    deposited sequence within the accepted length range.
    """
    if part_name:
        # Single-part mode for testing
        if part_name not in sequences:
            raise ValueError(f"No sequence found for part '{part_name}'")
        return [(part_name, sequences[part_name])]

    if mode == "all":
        candidate_names = set(parts_df["part_name"].dropna())
    else:
        # Carbon-capture keyword filter: search title and text columns
        mask = pd.Series(False, index=parts_df.index)
        for col in ["title", "text"]:
            if col in parts_df.columns:
                col_lower = parts_df[col].fillna("").str.lower()
                for kw in CARBON_CAPTURE_KEYWORDS:
                    mask |= col_lower.str.contains(kw, regex=False)
        candidate_names = set(parts_df.loc[mask, "part_name"].dropna())
        logger.info(f"Carbon-capture keyword filter: {len(candidate_names)} parts")

    # Keep only parts with a blastable sequence
    result = []
    skipped_short = skipped_long = skipped_no_seq = 0
    for name in sorted(candidate_names):
        seq = sequences.get(name, "")
        if not seq:
            skipped_no_seq += 1
        elif len(seq) < MIN_SEQ_LENGTH:
            skipped_short += 1
        elif len(seq) > MAX_SEQ_LENGTH:
            skipped_long += 1
        else:
            result.append((name, seq))

    logger.info(
        f"Skipped: {skipped_no_seq} no sequence, "
        f"{skipped_short} too short (<{MIN_SEQ_LENGTH}bp), "
        f"{skipped_long} too long (>{MAX_SEQ_LENGTH}bp)"
    )
    return result


# ---------------------------------------------------------------------------
# NCBI BLAST URL API — submit and poll
# ---------------------------------------------------------------------------

def make_fasta(pairs: list[tuple[str, str]]) -> str:
    """
    Build a multi-FASTA string from (name, sequence) pairs.

    NCBI BLAST accepts multiple queries in one submission when given a
    FASTA file with more than one record. Each record becomes an independent
    BLAST search; results are returned together when the batch job finishes.
    """
    lines = []
    for name, seq in pairs:
        lines.append(f">{name}")
        # Wrap sequence at 60 characters per line (FASTA convention)
        for i in range(0, len(seq), 60):
            lines.append(seq[i:i+60])
    return "\n".join(lines)


def submit_blast_batch(
    fasta: str,
    api_key: str | None,
) -> str | None:
    """
    Submit a multi-FASTA to NCBI BLAST and return the Request ID (RID).

    The RID is NCBI's handle for this batch job. We use it to poll for
    status and then download results. RIDs expire after 36 hours.

    Returns None if submission fails.
    """
    params = {
        "CMD":          "Put",
        "PROGRAM":      BLAST_PROGRAM,
        "DATABASE":     BLAST_DATABASE,
        "QUERY":        fasta,
        "FORMAT_TYPE":  "XML",
        "HITLIST_SIZE": BLAST_HITLIST,
        "EXPECT":       BLAST_EXPECT,
        "MEGABLAST":    "on",   # faster algorithm for high-identity searches
    }
    if api_key:
        params["api_key"] = api_key

    try:
        resp = requests.post(BLAST_URL, data=params, timeout=60)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Batch submission failed: {e}")
        return None

    # Extract RID from the HTML response using regex
    # NCBI returns something like: QBlastInfoBegin\n    RID = ABC12345\nQBlastInfoEnd
    m = re.search(r"RID\s*=\s*(\S+)", resp.text)
    if not m:
        logger.error("Could not find RID in NCBI response")
        logger.debug(resp.text[:500])
        return None

    return m.group(1)


def poll_blast_batch(rid: str, api_key: str | None) -> str | None:
    """
    Poll NCBI until the batch job with this RID is ready, then return the XML.

    NCBI returns one of three statuses:
      WAITING  — still running, check again later
      FAILED   — job failed (e.g. bad sequences or server error)
      (none)   — results are ready, parse the response body as XML

    Returns the XML string, or None if the job failed or timed out.
    """
    poll_params = {
        "CMD":         "Get",
        "RID":         rid,
        "FORMAT_TYPE": "XML",
    }
    if api_key:
        poll_params["api_key"] = api_key

    elapsed = 0
    while elapsed < POLL_TIMEOUT:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        try:
            resp = requests.get(BLAST_URL, params=poll_params, timeout=60)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Poll request failed (RID {rid}): {e}")
            continue

        body = resp.text
        if "Status=WAITING" in body:
            logger.debug(f"  RID {rid}: still waiting ({elapsed}s elapsed)…")
            continue
        if "Status=FAILED" in body:
            logger.error(f"  RID {rid}: job FAILED")
            return None

        # No WAITING or FAILED status means results are ready
        return body

    logger.error(f"  RID {rid}: timed out after {POLL_TIMEOUT}s")
    return None


# ---------------------------------------------------------------------------
# Parse BLAST XML results
# ---------------------------------------------------------------------------

def parse_blast_xml(xml_str: str, min_identity: float) -> list[dict]:
    """
    Parse a BLAST XML result containing one or more query records.

    Each record corresponds to one sequence from the submitted batch.
    For each record, we extract hits that pass the identity and coverage
    thresholds.

    Parameters
    ----------
    xml_str      : raw XML from NCBI (may contain results for many queries)
    min_identity : minimum percent identity to include a hit

    Returns
    -------
    list of dicts, one per passing hit, with fields:
      part_name, patent_accession, patent_title, pct_identity,
      alignment_length, query_coverage, query_length, e_value, bit_score
    """
    hits = []
    try:
        records = list(NCBIXML.parse(StringIO(xml_str)))
    except Exception as e:
        logger.warning(f"Could not parse BLAST XML: {e}")
        return hits

    for record in records:
        # query is the FASTA header we submitted (the part name)
        part_name    = record.query.strip()
        query_length = record.query_length

        for alignment in record.alignments:
            for hsp in alignment.hsps:
                pct_identity   = 100.0 * hsp.identities / hsp.align_length
                query_coverage = 100.0 * hsp.align_length / query_length if query_length else 0

                if pct_identity < min_identity:
                    continue
                if query_coverage < 50.0:
                    # Alignment covers less than half the query — likely a
                    # conserved domain fragment, not a whole-sequence match
                    continue

                hits.append({
                    "part_name":        part_name,
                    "patent_accession": alignment.accession,
                    "patent_title":     alignment.title[:200],
                    "pct_identity":     round(pct_identity, 2),
                    "alignment_length": hsp.align_length,
                    "query_coverage":   round(query_coverage, 2),
                    "query_length":     query_length,
                    "e_value":          hsp.expect,
                    "bit_score":        hsp.score,
                })

    return hits


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(filter_mode: str, part_name: str | None, batch_size: int, min_identity: float):
    print("=== Step 3f: Batch BLAST BioBrick Sequences Against Patent Database ===\n")

    BLAST_CACHE.mkdir(parents=True, exist_ok=True)

    api_key = os.getenv("NCBI_API_KEY")
    if api_key:
        print(f"NCBI API key found — using 10 req/s rate limit")
    else:
        print("No NCBI_API_KEY in .env — using 3 req/s rate limit")
    print()

    # Load data
    print("Loading sequences from parts_cache.jsonl…")
    sequences = load_sequences(PARTS_CACHE)

    print("Loading parts.csv…")
    parts_df = pd.read_csv(PARTS_CSV)

    print("Filtering parts…")
    to_blast = filter_parts(parts_df, sequences, filter_mode, part_name)
    print(f"  {len(to_blast)} parts selected for BLAST\n")

    if not to_blast:
        print("Nothing to BLAST. Exiting.")
        return

    # Divide into batches
    batches = [
        to_blast[i:i + batch_size]
        for i in range(0, len(to_blast), batch_size)
    ]
    n_batches = len(batches)

    # Count cached batches
    cached = sum(1 for i in range(n_batches) if (BLAST_CACHE / f"batch_{i:04d}.xml").exists())
    remaining = n_batches - cached

    print(f"Batch size:      {batch_size} sequences per submission")
    print(f"Total batches:   {n_batches}")
    print(f"Already cached:  {cached}")
    print(f"To submit:       {remaining}")
    if remaining > 0:
        lo = remaining * 1 / 60
        hi = remaining * 4 / 60
        print(f"Estimated time:  {lo:.1f}–{hi:.1f} hours")
    print("(Safe to interrupt — each batch is cached before moving on)\n")

    # Submit and poll each batch
    for i, batch in enumerate(batches):
        cache_file = BLAST_CACHE / f"batch_{i:04d}.xml"

        if cache_file.exists():
            logger.debug(f"Batch {i+1}/{n_batches}: cached, skipping")
            continue

        names = [name for name, _ in batch]
        fasta = make_fasta(batch)

        print(f"Batch {i+1}/{n_batches}: submitting {len(batch)} sequences "
              f"({names[0]} … {names[-1]})")

        rid = submit_blast_batch(fasta, api_key)
        if rid is None:
            logger.error(f"  Batch {i+1}: submission failed, skipping")
            continue

        print(f"  RID: {rid} — polling every {POLL_INTERVAL}s…")
        xml = poll_blast_batch(rid, api_key)
        if xml is None:
            logger.error(f"  Batch {i+1}: polling failed or timed out")
            continue

        cache_file.write_text(xml)
        print(f"  Batch {i+1}: done, cached to {cache_file.name}")

        # Brief pause between submissions to respect rate limits
        time.sleep(3 if api_key else 10)

    # Parse all cached results
    print("\nParsing cached BLAST results…")
    all_hits = []
    for i in range(n_batches):
        cache_file = BLAST_CACHE / f"batch_{i:04d}.xml"
        if not cache_file.exists():
            logger.warning(f"  Batch {i}: cache file missing, skipping")
            continue
        xml = cache_file.read_text()
        batch_hits = parse_blast_xml(xml, min_identity)
        all_hits.extend(batch_hits)
        if batch_hits:
            logger.info(f"  Batch {i}: {len(batch_hits)} hit(s)")

    print(f"\n{'='*60}")
    print(f"Total hits at ≥{min_identity}% identity: {len(all_hits)}\n")

    # Build output table
    if all_hits:
        hits_df = pd.DataFrame(all_hits)

        # Merge in part metadata for context
        meta_cols = ["part_name", "title", "part_type", "year", "city",
                     "country", "case_study_flag"]
        meta = parts_df[[c for c in meta_cols if c in parts_df.columns]].copy()
        hits_df = hits_df.merge(meta, on="part_name", how="left")
        hits_df = hits_df.sort_values(
            ["pct_identity", "bit_score"], ascending=[False, False]
        )

        hits_df.to_csv(HITS_OUT, index=False)
        print(f"Saved {len(hits_df)} hits → {HITS_OUT.relative_to(REPO_ROOT)}")

        display_cols = ["part_name", "patent_accession", "pct_identity",
                        "query_coverage", "e_value"]
        print("\nTop 10 matches:")
        print(hits_df[[c for c in display_cols if c in hits_df.columns]].head(10).to_string(index=False))

    else:
        print(f"No hits found at ≥{min_identity}% identity.")
        pd.DataFrame(columns=[
            "part_name", "patent_accession", "patent_title",
            "pct_identity", "alignment_length", "query_coverage",
            "query_length", "e_value", "bit_score",
        ]).to_csv(HITS_OUT, index=False)
        print(f"Saved empty hits file → {HITS_OUT.relative_to(REPO_ROOT)}")

    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch BLAST BioBrick sequences against NCBI patent sequence database"
    )
    parser.add_argument(
        "--filter",
        choices=["carbon-capture", "all"],
        default="carbon-capture",
        help=(
            "'carbon-capture' (default): keyword-filtered subset (~2,050 parts, ~1–3h). "
            "'all': every part with a sequence (~77,000 parts, days)."
        ),
    )
    parser.add_argument(
        "--part",
        default=None,
        metavar="PART_NAME",
        help="BLAST a single named part (e.g. BBa_K1172301). Overrides --filter.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH,
        help=f"Sequences per NCBI submission (default: {DEFAULT_BATCH})",
    )
    parser.add_argument(
        "--min-identity",
        type=float,
        default=DEFAULT_MIN_ID,
        help=f"Minimum percent identity to report a hit (default: {DEFAULT_MIN_ID})",
    )
    args = parser.parse_args()
    run(
        filter_mode=args.filter,
        part_name=args.part,
        batch_size=args.batch_size,
        min_identity=args.min_identity,
    )
