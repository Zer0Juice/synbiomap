#!/usr/bin/env python3
"""PDF to token-efficient markdown. pdftext extraction → compression.

Requires: pip install pdftext
  (pdftext uses pypdfium2 under the hood — no ML models, fast, batch-friendly)

Run with the marker venv python for best results:
  ~/marker-venv/bin/python pdf_to_context.py INPUT [-o OUTPUT] [OPTIONS]
"""

import argparse, os, re, sys
from collections import Counter
from pathlib import Path

# ── Extraction ──────────────────────────────────────────────────────────────

def extract(pdf_path):
    """Extract plain text from a PDF using pdftext (no ML models required)."""
    try:
        from pdftext.extraction import plain_text_output
        # sort=True preserves reading order across columns
        return plain_text_output(pdf_path, sort=True, hyphens=False)
    except ImportError:
        print(
            "ERROR: pdftext not installed.\n"
            "Run: pip install pdftext\n"
            "Or use the marker venv: ~/marker-venv/bin/python pdf_to_context.py ...",
            file=sys.stderr,
        )
        sys.exit(1)


def count_pages(pdf_path):
    """Count pages using pypdfium2 (installed alongside pdftext)."""
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(pdf_path)
        n = len(doc)
        doc.close()
        return n
    except Exception:
        return 0

# ── Compression ─────────────────────────────────────────────────────────────

COPYRIGHT_RE = re.compile(
    r"©.*\d{4}|copyright\s+\d{4}|all\s+rights\s+reserved|"
    r"confidential\s+and\s+proprietary|do\s+not\s+distribute|for\s+internal\s+use\s+only",
    re.IGNORECASE,
)
TOC_RE = re.compile(r"^\s*(table\s+of\s+contents|contents)\s*$", re.IGNORECASE)
PAGE_NUM_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"^\d{1,4}$", r"^page\s+\d+(\s+of\s+\d+)?$",
        r"^-\s*\d+\s*-$", r"^\d+\s*/\s*\d+$", r"^\[\d+\]$",
    ]
]


def find_repeated_lines(text, threshold_pct=0.3, min_occ=3):
    """Find lines that appear repeatedly across pages (headers/footers)."""
    pages = text.split("\f") if "\f" in text else [text]
    if len(pages) < 3:
        return set()
    counts = Counter()
    for page in pages:
        for line in set(l.strip() for l in page.splitlines() if len(l.strip()) > 2):
            counts[line] += 1
    threshold = max(min_occ, len(pages) * threshold_pct)
    return {l for l, c in counts.items() if c >= threshold}


def is_page_number(s):
    return any(p.fullmatch(s) for p in PAGE_NUM_PATTERNS)


def is_decorative(s):
    if len(s) < 3:
        return False
    chars = set(s.replace(" ", ""))
    return len(chars) <= 2 and all(c in "-=_*~•·.+" for c in chars)


def is_toc_entry(s):
    return bool(re.search(r"\.{3,}\s*\d+\s*$", s) or re.search(r"\s{4,}\d+\s*$", s))


def compress(text, keep_headers=False, strip_refs=False, max_tokens=None):
    """Strip boilerplate (headers, footers, page numbers, TOC, copyright) from extracted text."""
    repeated = find_repeated_lines(text) if not keep_headers else set()
    lines, out = text.splitlines(), []
    in_toc = in_code = False

    for line in lines:
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code; out.append(line); continue
        if in_code:
            out.append(line); continue
        if not s:
            out.append(""); continue
        if not keep_headers and s in repeated:
            continue
        if is_page_number(s) or (is_decorative(s) and not s.startswith("#")):
            continue
        if COPYRIGHT_RE.search(s) and len(s) < 120:
            continue
        if TOC_RE.match(s):
            in_toc = True; continue
        if in_toc:
            if is_toc_entry(s): continue
            else: in_toc = False
        if re.fullmatch(r"!\[.*?\]\(.*?\)", s):
            continue
        out.append(line)

    result = "\n".join(out)

    if strip_refs:
        for pat in [r"\n#{1,3}\s*References?\s*\n", r"\n#{1,3}\s*Bibliography\s*\n",
                     r"\nREFERENCES?\s*\n", r"\nBIBLIOGRAPHY\s*\n"]:
            m = re.search(pat, result, re.IGNORECASE)
            if m:
                rest = result[m.end():]
                nxt = re.search(r"\n#{1,3}\s+\S", rest)
                result = result[:m.start()] + ("\n" + rest[nxt.start():] if nxt else "\n")
                break

    result = re.sub(r"\n{3,}", "\n\n", result)
    result = "\n".join(l.rstrip() for l in result.splitlines()).strip() + "\n"

    if max_tokens:
        max_c = max_tokens * 4
        if len(result) > max_c:
            cut = result[:max_c]
            brk = cut.rfind("\n\n")
            if brk > max_c * 0.8:
                cut = cut[:brk]
            result = cut + f"\n\n[... truncated to ~{max_tokens} tokens ...]\n"

    return result

# ── Pipeline ────────────────────────────────────────────────────────────────

def convert(pdf_path, output_path=None, keep_headers=False, strip_refs=False,
            max_tokens=None, fmt="md", verbose=False):
    pdf_path = os.path.abspath(pdf_path)
    name = os.path.basename(pdf_path)
    if verbose: print(f"Processing: {name}")

    raw = extract(pdf_path)
    pages = count_pages(pdf_path)
    raw_tok = len(raw) // 4

    if verbose: print(f"  Extractor: pdftext | Pages: {pages} | Raw tokens: ~{raw_tok:,}")

    result = compress(raw, keep_headers, strip_refs, max_tokens)
    comp_tok = len(result) // 4
    pct = round((1 - comp_tok / max(raw_tok, 1)) * 100)

    header = (f"---\nsource: {name}\npages: {pages}\nextractor: pdftext\n"
              f"tokens_raw: {raw_tok}\ntokens_compressed: {comp_tok}\ncompression: {pct}%\n---\n\n")
    result = header + result

    if not output_path:
        output_path = os.path.splitext(pdf_path)[0] + (".md" if fmt == "md" else ".txt")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    Path(output_path).write_text(result, encoding="utf-8")

    if verbose: print(f"  Compressed: ~{comp_tok:,} tokens ({pct}% reduction) → {output_path}")
    return result


def batch(input_dir, output_dir=None, **kw):
    """Convert all PDFs in a directory."""
    input_dir = os.path.abspath(input_dir)
    output_dir = output_dir or os.path.join(input_dir, "_context")
    os.makedirs(output_dir, exist_ok=True)
    pdfs = sorted(Path(input_dir).glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs in {input_dir}", file=sys.stderr); sys.exit(1)
    ext = ".md" if kw.get("fmt", "md") == "md" else ".txt"
    for f in pdfs:
        print(f"Converting: {f.name}")
        convert(str(f), os.path.join(output_dir, f.stem + ext), **kw)
    print(f"\n{len(pdfs)} files → {output_dir}")


def main():
    p = argparse.ArgumentParser(description="PDF → token-efficient markdown via pdftext")
    p.add_argument("input", help="PDF file or directory of PDFs")
    p.add_argument("-o", "--output", help="Output path (default: same dir as PDF)")
    p.add_argument("--strip-references", action="store_true", help="Remove bibliography/references section")
    p.add_argument("--max-tokens", type=int, help="Truncate output to ~N tokens")
    p.add_argument("--keep-headers", action="store_true", help="Keep repeated headers/footers")
    p.add_argument("--format", choices=["md", "txt"], default="md", help="Output format (default: md)")
    p.add_argument("-v", "--verbose", action="store_true", help="Print per-file stats")
    a = p.parse_args()

    kw = dict(keep_headers=a.keep_headers, strip_refs=a.strip_references,
              max_tokens=a.max_tokens, fmt=a.format, verbose=a.verbose)

    if os.path.isdir(a.input):
        batch(a.input, a.output, **kw)
    elif os.path.isfile(a.input):
        convert(a.input, a.output, **kw)
    else:
        print(f"ERROR: {a.input} not found", file=sys.stderr); sys.exit(1)


if __name__ == "__main__":
    main()
