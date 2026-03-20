#!/usr/bin/env python3
"""
fetch_neffke.py — Build frankGPT's knowledge base from Frank Neffke's OpenAlex works.

What this script does:
1. Queries OpenAlex for all publications by Frank Neffke (identified by ORCID)
2. Downloads any open-access PDFs that are freely available
3. Converts each PDF to a compressed, token-efficient markdown file using pdf-to-context
4. Generates a papers_index.md — a compact structured summary of all works that
   frankGPT loads in every conversation to know what literature exists

Why this architecture:
- The index (~100 tokens/paper) is always in context — frankGPT always knows what exists
- Full compressed papers (~2,000–6,000 tokens each) are only loaded when specifically relevant
- This keeps baseline token cost low while enabling deep engagement with specific papers

Usage:
    python fetch_neffke.py                 # fetch all, download OA PDFs, compress
    python fetch_neffke.py --no-pdf        # metadata only, skip PDF download
    python fetch_neffke.py --no-compress   # download PDFs but skip pdf-to-context
    python fetch_neffke.py --limit 10      # process only first 10 works (for testing)

Requirements:
    pip install requests
    pip install marker-pdf          (only needed for --compress, the default)
    ollama pull gemma3:12b          (only needed for --compress)
"""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

# ── Constants ────────────────────────────────────────────────────────────────

NEFFKE_ORCID = "0000-0002-3924-6636"
OPENALEX_BASE = "https://api.openalex.org"
EMAIL = "polite-pool@frankgpt.local"  # OpenAlex asks for an email for the polite pool

# Where this script lives; knowledge base is one level up
SCRIPT_DIR = Path(__file__).parent
KNOWLEDGE_DIR = SCRIPT_DIR.parent / "knowledge"
PDF_DIR = KNOWLEDGE_DIR / "pdfs"
COMPRESSED_DIR = KNOWLEDGE_DIR / "compressed"
INDEX_PATH = KNOWLEDGE_DIR / "papers_index.md"
METADATA_PATH = KNOWLEDGE_DIR / "papers_metadata.json"

PDF_DIR.mkdir(parents=True, exist_ok=True)
COMPRESSED_DIR.mkdir(parents=True, exist_ok=True)


# ── OpenAlex fetch ───────────────────────────────────────────────────────────

def fetch_neffke_works(limit=None):
    """
    Fetch all of Neffke's works from OpenAlex using cursor-based pagination.

    OpenAlex returns up to 200 results per page. We loop through all pages
    using the 'next_cursor' field until we have everything.

    Returns a list of work dicts with the fields we care about.
    """
    works = []
    cursor = "*"  # OpenAlex pagination starts with "*"
    page_num = 0

    print(f"[1/4] Querying OpenAlex for ORCID {NEFFKE_ORCID} ...")

    while True:
        page_num += 1
        url = (
            f"{OPENALEX_BASE}/works"
            f"?filter=authorships.author.orcid:{NEFFKE_ORCID}"
            f"&per_page=200"
            f"&cursor={cursor}"
            f"&mailto={EMAIL}"
        )

        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            break

        for w in results:
            # Extract the fields we need and nothing else
            oa_url = None
            if w.get("open_access", {}).get("is_oa"):
                oa_url = w["open_access"].get("oa_url")

            # Abstract is stored as an inverted index in OpenAlex — reconstruct it
            abstract = reconstruct_abstract(w.get("abstract_inverted_index"))

            # Get up to 3 co-authors (excluding Neffke himself)
            coauthors = [
                a["author"]["display_name"]
                for a in w.get("authorships", [])
                if NEFFKE_ORCID not in (a["author"].get("orcid") or "")
            ][:3]

            works.append({
                "id": w["id"],
                "doi": w.get("doi"),
                "title": w.get("title", "Untitled"),
                "year": w.get("publication_year"),
                "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
                "cited_by_count": w.get("cited_by_count", 0),
                "is_oa": w.get("open_access", {}).get("is_oa", False),
                "oa_url": oa_url,
                "abstract": abstract,
                "coauthors": coauthors,
                "concepts": [
                    c["display_name"] for c in (w.get("concepts") or [])
                    if c.get("score", 0) > 0.4
                ][:5],
            })

        print(f"  page {page_num}: fetched {len(results)} works (total so far: {len(works)})")

        # Check if there's a next page
        meta = data.get("meta", {})
        cursor = meta.get("next_cursor")
        if not cursor:
            break

        # Polite pool: wait 100ms between requests
        time.sleep(0.15)

        if limit and len(works) >= limit:
            works = works[:limit]
            break

    print(f"  → {len(works)} works total")
    return works


def reconstruct_abstract(inverted_index):
    """
    OpenAlex stores abstracts as {word: [position, position, ...]} dicts.
    This function reconstructs the plain-text abstract.
    Returns None if no abstract is available.
    """
    if not inverted_index:
        return None
    positions = {}
    for word, locs in inverted_index.items():
        for loc in locs:
            positions[loc] = word
    if not positions:
        return None
    return " ".join(positions[i] for i in sorted(positions))


# ── PDF download ─────────────────────────────────────────────────────────────

def download_pdfs(works, verbose=True):
    """
    For each work that has an open-access PDF URL, download the PDF.

    PDFs are saved to knowledge/pdfs/<safe_title>_<year>.pdf
    Skips files that already exist (idempotent — safe to re-run).

    Returns a dict mapping work ID → local PDF path (or None if no PDF).
    """
    print(f"\n[2/4] Downloading open-access PDFs ...")
    pdf_paths = {}
    downloaded = 0
    skipped = 0
    unavailable = 0

    for w in works:
        safe_name = safe_filename(w["title"], w["year"])
        pdf_path = PDF_DIR / f"{safe_name}.pdf"

        if not w["oa_url"]:
            unavailable += 1
            pdf_paths[w["id"]] = None
            continue

        if pdf_path.exists():
            skipped += 1
            pdf_paths[w["id"]] = pdf_path
            if verbose:
                print(f"  [skip] {safe_name}.pdf (already exists)")
            continue

        try:
            # Some URLs redirect to HTML pages — check content-type
            resp = requests.get(w["oa_url"], timeout=60, stream=True,
                                headers={"User-Agent": "frankGPT/1.0 (research tool)"})
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if "pdf" not in content_type and "octet-stream" not in content_type:
                # Not actually a PDF — try appending .pdf to the URL or skip
                if verbose:
                    print(f"  [skip] {safe_name} — URL returned {content_type}, not PDF")
                pdf_paths[w["id"]] = None
                unavailable += 1
                time.sleep(0.15)
                continue

            with open(pdf_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            downloaded += 1
            pdf_paths[w["id"]] = pdf_path
            if verbose:
                print(f"  [ok]   {safe_name}.pdf")

        except Exception as e:
            if verbose:
                print(f"  [err]  {safe_name}: {e}")
            pdf_paths[w["id"]] = None

        time.sleep(0.15)  # polite

    print(f"  → {downloaded} downloaded, {skipped} already existed, {unavailable} unavailable")
    return pdf_paths


# ── PDF compression ──────────────────────────────────────────────────────────

def compress_pdfs(works, pdf_paths, pdf_to_context_script, ollama_model, no_llm=False):
    """
    Run pdf-to-context on each downloaded PDF to produce a compressed markdown file.

    The pdf-to-context script (in the pdf-to-context skill) does two things:
    1. Extracts text from the PDF using marker-pdf (an ML-based extractor)
    2. Strips boilerplate, headers, footers, and image references

    Compressed files go to knowledge/compressed/<safe_name>.md
    Returns a dict mapping work ID → compressed md path (or None).
    """
    print(f"\n[3/4] Compressing PDFs to markdown ...")

    if not Path(pdf_to_context_script).exists():
        print(f"  WARNING: pdf_to_context.py not found at {pdf_to_context_script}")
        print("  Skipping compression. Run with --no-compress to suppress this warning.")
        return {w["id"]: None for w in works}

    compressed_paths = {}
    import subprocess

    for w in works:
        pdf_path = pdf_paths.get(w["id"])
        if not pdf_path or not Path(pdf_path).exists():
            compressed_paths[w["id"]] = None
            continue

        safe_name = safe_filename(w["title"], w["year"])
        out_path = COMPRESSED_DIR / f"{safe_name}.md"

        if out_path.exists():
            print(f"  [skip] {safe_name}.md (already exists)")
            compressed_paths[w["id"]] = out_path
            continue

        # Use the marker venv Python which has pdftext installed
        venv_python = Path.home() / "marker-venv" / "bin" / "python"
        python_exe = str(venv_python) if venv_python.exists() else sys.executable

        cmd = [
            python_exe, str(pdf_to_context_script),
            str(pdf_path),
            "-o", str(out_path),
            "--strip-references",
            "--format", "md",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"  [ok]   {safe_name}.md")
                compressed_paths[w["id"]] = out_path
            else:
                print(f"  [err]  {safe_name}: {result.stderr[:200]}")
                compressed_paths[w["id"]] = None
        except subprocess.TimeoutExpired:
            print(f"  [timeout] {safe_name} — took >600s, skipping")
            compressed_paths[w["id"]] = None
        except Exception as e:
            print(f"  [err]  {safe_name}: {e}")
            compressed_paths[w["id"]] = None

    return compressed_paths


# ── Index generation ─────────────────────────────────────────────────────────

def build_index(works, pdf_paths, compressed_paths):
    """
    Generate papers_index.md — the compact knowledge index that frankGPT reads
    in every conversation.

    Each paper gets ~100 tokens covering:
    - citation info (title, year, venue, coauthors)
    - citation count (signals importance)
    - key concepts
    - 2-sentence abstract digest
    - whether a full compressed version is available to load

    The index is sorted by citation count (most influential first) so frankGPT
    naturally reaches for the canonical papers.
    """
    print(f"\n[4/4] Building papers_index.md ...")

    # Sort by citation count descending
    sorted_works = sorted(works, key=lambda w: w.get("cited_by_count", 0), reverse=True)

    lines = [
        "# Frank Neffke — Knowledge Index",
        "",
        "This index is loaded by frankGPT at the start of every conversation.",
        "It lists all known works. For papers marked `[full text available]`,",
        "the compressed markdown can be loaded with Read(compressed/<filename>.md).",
        "",
        f"Total works indexed: {len(works)}",
        "",
        "---",
        "",
    ]

    for w in sorted_works:
        safe_name = safe_filename(w["title"], w["year"])
        has_full = bool(compressed_paths.get(w["id"]))
        has_pdf = bool(pdf_paths.get(w["id"]))

        coauthor_str = ", ".join(w["coauthors"]) if w["coauthors"] else "sole author"
        venue_str = w["venue"] or "venue unknown"
        concepts_str = ", ".join(w["concepts"]) if w["concepts"] else ""
        cite_str = f"{w['cited_by_count']} citations" if w['cited_by_count'] else "no citation data"

        # Truncate abstract to ~2 sentences for token efficiency
        abstract_digest = ""
        if w["abstract"]:
            sentences = w["abstract"].replace("  ", " ").split(". ")
            abstract_digest = ". ".join(sentences[:2]).strip()
            if not abstract_digest.endswith("."):
                abstract_digest += "."
            if len(abstract_digest) > 400:
                abstract_digest = abstract_digest[:400] + "..."

        availability = []
        if has_full:
            availability.append(f"`[full text: compressed/{safe_name}.md]`")
        elif has_pdf:
            availability.append("`[PDF only]`")
        else:
            availability.append("`[metadata only]`")

        block = [
            f"## {w['title']} ({w['year']})",
            f"**Authors:** Neffke + {coauthor_str}  |  **Venue:** {venue_str}  |  **{cite_str}**",
        ]
        if concepts_str:
            block.append(f"**Topics:** {concepts_str}")
        if w["doi"]:
            block.append(f"**DOI:** {w['doi']}")
        if abstract_digest:
            block.append(f"**Abstract digest:** {abstract_digest}")
        block.append(f"**Availability:** {' '.join(availability)}")
        block.append("")

        lines.extend(block)

    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"  → Wrote {INDEX_PATH} ({len(sorted_works)} entries)")


# ── Utilities ────────────────────────────────────────────────────────────────

def safe_filename(title, year):
    """Convert a paper title + year to a safe filename (no spaces, no special chars)."""
    import re
    s = f"{year}_{title}"
    s = re.sub(r"[^a-zA-Z0-9_\- ]", "", s)  # strip special chars
    s = re.sub(r"\s+", "_", s.strip())        # spaces → underscores
    return s[:80]                              # cap length


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build frankGPT knowledge base from OpenAlex")
    parser.add_argument("--no-pdf", action="store_true",
                        help="Skip PDF download (metadata index only)")
    parser.add_argument("--no-compress", action="store_true",
                        help="Skip pdf-to-context compression step")
    parser.add_argument("--no-llm", action="store_true",
                        help="Use marker without Ollama LLM (faster but lower quality)")
    parser.add_argument("--ollama-model", default="gemma3:12b",
                        help="Ollama model for pdf-to-context (default: gemma3:12b)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process only first N works (for testing)")
    parser.add_argument("--pdf-to-context", default=None,
                        help="Path to pdf_to_context.py (auto-detected if not given)")
    args = parser.parse_args()

    # Auto-detect pdf-to-context script location
    pdf_to_context_script = args.pdf_to_context
    if pdf_to_context_script is None:
        # Look relative to the skills directory
        candidate = SCRIPT_DIR.parent.parent / "pdf-to-context" / "scripts" / "pdf_to_context.py"
        pdf_to_context_script = str(candidate)

    # Step 1: fetch metadata
    works = fetch_neffke_works(limit=args.limit)

    # Save raw metadata for debugging / re-runs
    METADATA_PATH.write_text(json.dumps(works, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved raw metadata to {METADATA_PATH}")

    # Step 2: download PDFs
    if args.no_pdf:
        print("\n[2/4] Skipping PDF download (--no-pdf)")
        pdf_paths = {w["id"]: None for w in works}
    else:
        pdf_paths = download_pdfs(works)

    # Step 3: compress PDFs
    if args.no_compress or args.no_pdf:
        print("\n[3/4] Skipping compression")
        compressed_paths = {w["id"]: None for w in works}
    else:
        compressed_paths = compress_pdfs(works, pdf_paths, pdf_to_context_script,
                                         ollama_model=args.ollama_model,
                                         no_llm=args.no_llm)

    # Step 4: build index
    build_index(works, pdf_paths, compressed_paths)

    print("\nDone. frankGPT knowledge base is ready.")
    print(f"  Index:      {INDEX_PATH}")
    print(f"  PDFs:       {PDF_DIR} ({len([v for v in pdf_paths.values() if v])} files)")
    print(f"  Compressed: {COMPRESSED_DIR} ({len([v for v in compressed_paths.values() if v])} files)")


if __name__ == "__main__":
    main()
