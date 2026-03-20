#!/usr/bin/env python3
"""
build_knowledge_base.py — Build frankGPT's multi-section knowledge index.

This replaces fetch_neffke.py as the primary build script. It reads
knowledge_config.json and produces one thematic index file per section,
so frankGPT can load only the sections relevant to each conversation.

Sections defined in knowledge_config.json:
  - neffke       (always loaded — Frank Neffke's full body of work)
  - eeg          (Evolutionary Economic Geography — load for regional/EEG questions)
  - complexity   (Economic Complexity — load for product-space/ECI questions)
  - agglomeration (Urban/agglomeration — load for cities/density questions)
  - methods      (Econometrics methods — load for empirical design questions)

Each section produces:
  knowledge/index_<name>.md     compact structured index (~40-60 tokens/paper)

Usage:
    python build_knowledge_base.py                   # build all sections
    python build_knowledge_base.py --section neffke  # rebuild one section
    python build_knowledge_base.py --no-cache        # re-fetch even if cached

Why thematic sections rather than one big file:
  A single flat index of all papers would be ~25,000 tokens — too large to load
  by default. Splitting lets frankGPT load only relevant sections, keeping the
  typical context cost to ~6,000-10,000 tokens.

Requirements:
    pip install requests
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

# ── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).parent
SKILL_DIR    = SCRIPT_DIR.parent
CONFIG_PATH  = SKILL_DIR / "knowledge_config.json"
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
CACHE_DIR    = KNOWLEDGE_DIR / "_cache"   # raw API responses, not checked into git

KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

OPENALEX_BASE = "https://api.openalex.org"
EMAIL = "frankgpt-builder@local"


# ── OpenAlex fetching ────────────────────────────────────────────────────────

def fetch_by_orcid(orcid: str, top_n: int | None, use_cache: bool) -> list[dict]:
    """
    Fetch works for a researcher identified by ORCID.

    top_n: if set, return only the top-N papers by citation count.
    Returns a list of normalized work dicts.
    """
    cache_file = CACHE_DIR / f"orcid_{orcid.replace('/', '_')}.json"
    if use_cache and cache_file.exists():
        return json.loads(cache_file.read_text())[:top_n] if top_n else json.loads(cache_file.read_text())

    works = []
    cursor = "*"
    while True:
        url = (f"{OPENALEX_BASE}/works"
               f"?filter=authorships.author.orcid:{orcid}"
               f"&per_page=200&cursor={cursor}&mailto={EMAIL}")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("results", [])
        if not batch:
            break
        works.extend(normalize(w) for w in batch)
        cursor = (data.get("meta") or {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(0.15)

    # Sort by citation count descending so top_n gives most influential
    works.sort(key=lambda w: w["cited_by_count"], reverse=True)
    cache_file.write_text(json.dumps(works, ensure_ascii=False))

    return works[:top_n] if top_n else works


def fetch_by_openalex_id(author_id: str, top_n: int | None, use_cache: bool) -> list[dict]:
    """
    Fetch works for a researcher identified by OpenAlex author ID (for authors
    without an ORCID, like Glaeser).
    """
    cache_file = CACHE_DIR / f"oaid_{author_id}.json"
    if use_cache and cache_file.exists():
        raw = json.loads(cache_file.read_text())
        return raw[:top_n] if top_n else raw

    works = []
    cursor = "*"
    while True:
        url = (f"{OPENALEX_BASE}/works"
               f"?filter=authorships.author.id:{author_id}"
               f"&per_page=200&cursor={cursor}&mailto={EMAIL}")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("results", [])
        if not batch:
            break
        works.extend(normalize(w) for w in batch)
        cursor = (data.get("meta") or {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(0.15)

    works.sort(key=lambda w: w["cited_by_count"], reverse=True)
    cache_file.write_text(json.dumps(works, ensure_ascii=False))
    return works[:top_n] if top_n else works


def fetch_by_doi(doi: str, use_cache: bool) -> dict | None:
    """Fetch a single paper by DOI. Returns a normalized work dict or None."""
    safe = doi.replace("/", "_").replace(":", "_")
    cache_file = CACHE_DIR / f"doi_{safe}.json"
    if use_cache and cache_file.exists():
        return json.loads(cache_file.read_text())

    url = f"{OPENALEX_BASE}/works/https://doi.org/{doi}?mailto={EMAIL}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 404:
            print(f"    [404] DOI not found: {doi}")
            return None
        resp.raise_for_status()
        w = normalize(resp.json())
        cache_file.write_text(json.dumps(w, ensure_ascii=False))
        return w
    except Exception as e:
        print(f"    [err] DOI {doi}: {e}")
        return None
    finally:
        time.sleep(0.15)


def normalize(w: dict) -> dict:
    """
    Extract the fields we care about from a raw OpenAlex work dict.
    Keeps things lean — no raw inverted-index abstracts, no full author lists.
    """
    # Reconstruct abstract from OpenAlex's inverted-index format
    abstract = reconstruct_abstract(w.get("abstract_inverted_index"))

    return {
        "id":             w.get("id", ""),
        "doi":            w.get("doi", ""),
        "title":          (w.get("title") or "Untitled").strip(),
        "year":           w.get("publication_year"),
        "venue":          ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "cited_by_count": w.get("cited_by_count", 0),
        "is_oa":          (w.get("open_access") or {}).get("is_oa", False),
        "oa_url":         (w.get("open_access") or {}).get("oa_url"),
        "abstract":       abstract,
        "topics":         [
            t["display_name"]
            for t in (w.get("topics") or w.get("concepts") or [])
            if (t.get("score") or t.get("value") or 1) > 0.4
        ][:4],
    }


def reconstruct_abstract(inv: dict | None) -> str | None:
    """Reconstruct plain-text abstract from OpenAlex's inverted-index format."""
    if not inv:
        return None
    pos = {}
    for word, locs in inv.items():
        for loc in locs:
            pos[loc] = word
    if not pos:
        return None
    return " ".join(pos[i] for i in sorted(pos))


# ── Deduplication ─────────────────────────────────────────────────────────────

def dedup(works: list[dict]) -> list[dict]:
    """Remove duplicate papers (same DOI or same OpenAlex ID)."""
    seen_doi = set()
    seen_id  = set()
    out = []
    for w in works:
        key_doi = w.get("doi") or ""
        key_id  = w.get("id") or ""
        if (key_doi and key_doi in seen_doi) or (key_id and key_id in seen_id):
            continue
        if key_doi:
            seen_doi.add(key_doi)
        if key_id:
            seen_id.add(key_id)
        out.append(w)
    return out


# ── Index rendering ──────────────────────────────────────────────────────────

def render_index(section: dict, works: list[dict]) -> str:
    """
    Render a thematic section's index as markdown.

    Entry format is intentionally compact (~40-60 tokens per paper):
      ## Title (Year)
      Venue | N citations | [full text / metadata only]
      Abstract digest (max 2 sentences)

    Papers are sorted by citation count (most canonical first).
    """
    label       = section["label"]
    description = section.get("description", "")
    always      = section.get("always_load", False)

    header = [
        f"# {label} — Knowledge Index",
        "",
        description,
        "",
        f"**Load trigger:** {'Always loaded by frankGPT.' if always else 'Load this file when relevant to the question.'}",
        f"**Papers indexed:** {len(works)}",
        "",
        "---",
        "",
    ]

    entries = []
    for w in sorted(works, key=lambda x: x.get("cited_by_count", 0), reverse=True):
        year   = w.get("year") or "n.d."
        venue  = w.get("venue") or "venue unknown"
        cites  = w.get("cited_by_count", 0)
        doi    = w.get("doi") or ""
        topics = ", ".join(w.get("topics") or [])

        # Short abstract: first 2 sentences, max 300 chars
        digest = ""
        if w.get("abstract"):
            sentences = w["abstract"].replace("  ", " ").split(". ")
            digest = ". ".join(sentences[:2]).strip()
            if not digest.endswith("."):
                digest += "."
            if len(digest) > 300:
                digest = digest[:300] + "..."

        cite_str = f"{cites:,} citations" if cites else "no citation data"

        block = [
            f"## {w['title']} ({year})",
            f"**{venue}** | **{cite_str}**",
        ]
        if topics:
            block.append(f"*{topics}*")
        if doi:
            block.append(f"DOI: {doi}")
        if digest:
            block.append(digest)
        block.append("")
        entries.append("\n".join(block))

    return "\n".join(header) + "\n".join(entries)


# ── Section builder ──────────────────────────────────────────────────────────

def build_section(section: dict, use_cache: bool) -> int:
    """
    Fetch all papers for a section and write its index file.
    Returns the number of papers indexed.
    """
    name  = section["name"]
    top_n = section.get("top_n") or None   # 0 → None (seed-only sections)

    print(f"\n{'='*60}")
    print(f"Section: {section['label']}  (index_{name}.md)")
    print(f"{'='*60}")

    all_works = []

    # Fetch by author
    for author in section.get("authors", []):
        author_name = author["name"]
        print(f"  Fetching {author_name} (top {top_n or 'all'}) ...")

        if author.get("orcid"):
            works = fetch_by_orcid(author["orcid"], top_n, use_cache)
        elif author.get("openalex_id"):
            works = fetch_by_openalex_id(author["openalex_id"], top_n, use_cache)
        else:
            print(f"    WARNING: no ORCID or OpenAlex ID for {author_name}, skipping")
            continue

        print(f"    → {len(works)} papers")
        all_works.extend(works)

    # Fetch seed papers by DOI
    for doi in section.get("seed_dois", []):
        print(f"  Fetching seed DOI: {doi}")
        w = fetch_by_doi(doi, use_cache)
        if w:
            all_works.append(w)
            print(f"    → {w.get('year')} {w.get('title', '')[:50]}")

    # Dedup, then render
    all_works = dedup(all_works)
    print(f"  Total after dedup: {len(all_works)} papers")

    md = render_index(section, all_works)
    out_path = KNOWLEDGE_DIR / f"index_{name}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"  Wrote → {out_path}")

    return len(all_works)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build frankGPT thematic knowledge indexes from OpenAlex"
    )
    parser.add_argument(
        "--section", default=None,
        help="Build only one section by name (e.g. --section neffke)"
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Re-fetch all data from OpenAlex even if cached"
    )
    args = parser.parse_args()

    use_cache = not args.no_cache

    config = json.loads(CONFIG_PATH.read_text())
    sections = config["sections"]

    if args.section:
        sections = [s for s in sections if s["name"] == args.section]
        if not sections:
            print(f"ERROR: section '{args.section}' not found in knowledge_config.json")
            sys.exit(1)

    print(f"Building {len(sections)} section(s). Cache: {'on' if use_cache else 'off'}")

    totals = {}
    built_neffke = False
    for section in sections:
        n = build_section(section, use_cache)
        totals[section["name"]] = n
        if section["name"] == "neffke":
            built_neffke = True

    # Always rebuild the Neffke spine after fetching fresh Neffke data
    if built_neffke:
        print(f"\n  → Rebuilding Neffke spine (build_neffke_spine.py) ...")
        import subprocess
        spine_script = SCRIPT_DIR / "build_neffke_spine.py"
        subprocess.run([sys.executable, str(spine_script)], check=True)

    print(f"\n{'='*60}")
    print("Done. Summary:")
    for name, n in totals.items():
        out_path = KNOWLEDGE_DIR / f"index_{name}.md"
        size_kb = out_path.stat().st_size // 1024 if out_path.exists() else 0
        print(f"  index_{name}.md:  {n} papers  ({size_kb} KB)")

    # Write a master README so frankGPT knows what sections exist
    readme_path = KNOWLEDGE_DIR / "README.md"
    lines = [
        "# frankGPT Knowledge Base",
        "",
        "Thematic index files. frankGPT loads these selectively based on the question.",
        "",
        "| File | Section | Always loaded? | Papers |",
        "|------|---------|----------------|--------|",
    ]
    for s in config["sections"]:
        n = totals.get(s["name"], "?")
        always = "Yes" if s.get("always_load") else "No"
        lines.append(f"| index_{s['name']}.md | {s['label']} | {always} | {n} |")
    lines += [
        "",
        "## Rebuild",
        "```bash",
        "python .claude/skills/frankGPT/scripts/build_knowledge_base.py",
        "```",
        "Add `--no-cache` to re-fetch from OpenAlex. Add `--section <name>` to rebuild one section.",
        "",
        "Cached API responses are in `_cache/` (excluded from git).",
    ]
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  {readme_path}")


if __name__ == "__main__":
    main()
