#!/usr/bin/env python3
"""
build_neffke_spine.py — Replace the monolithic Neffke index with a spine + per-theme system.

Problem: index_neffke.md is ~9,200 tokens for 81 papers. Most of those tokens
are wasted — 67% of the papers have fewer than 10 citations and only need to
be consulted occasionally. Loading all of them every session is expensive.

Solution: two-level structure
  1. index_neffke_spine.md  (~900 tokens, always loaded)
       For each theme: a 2-sentence characterization of Neffke's contribution
       + the top 3 papers (title, year, cites only — no abstracts)
       + a pointer to the full per-theme file.
  2. index_neffke_<theme>.md  (loaded on demand, ~1,500-2,500 tokens each)
       Full entries with abstract digests for all papers in that theme.

Themes (assigned by title keyword matching):
  relatedness   — how regions branch into related industries; density, coherence
  agglomeration — co-location, externalities, industry life-cycles
  labor         — displaced workers, skill mismatch, mobility, complementarity
  complexity    — network backboning, information-theoretic approaches, diffusion
  other         — applied case studies, AI geography, emerging work

Usage:
    python build_neffke_spine.py
"""

import json
import re
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

SKILL_DIR     = Path(__file__).parent.parent
METADATA_PATH  = SKILL_DIR / "knowledge" / "papers_metadata.json"
OUT_DIR        = SKILL_DIR / "knowledge"
COMPRESSED_DIR = SKILL_DIR / "knowledge" / "compressed"

# ── Theme definitions ─────────────────────────────────────────────────────────
# Each theme has:
#   keywords  — matched (case-insensitive) against the paper title
#   label     — human-readable name
#   summary   — 2-sentence characterization of Neffke's work in this area
#               (written by hand — do not auto-generate, this is the spine's value)

THEMES = [
    {
        "name": "relatedness",
        "label": "Relatedness & Regional Diversification",
        "keywords": [
            "relatedness", "diversif", "branch", "coherenc", "density",
            "product space", "proximity", "how do regions", "path dependenc",
            "principle of relat", "revealed relat", "revealed comparative",
            "productive places", "industry space", "skill relat",
        ],
        "summary": (
            "Neffke's core contribution: regions diversify into industries that are "
            "skill-related to their existing portfolio, not randomly. "
            "He operationalises relatedness through co-worker flows between industries "
            "(skill relatedness) and shows density in the industry-space predicts entry, "
            "exit, and growth — the empirical backbone of evolutionary economic geography."
        ),
    },
    {
        "name": "agglomeration",
        "label": "Agglomeration & Co-location",
        "keywords": [
            "agglomer", "coagg", "co-agg", "coloc", "co-loc",
            "externali", "marshallian", "locali", "life cycle",
            "industries coagg", "cluster", "why do industries",
            "dynamics of agglomeration",
        ],
        "summary": (
            "Neffke studies *why* industries concentrate spatially and together: "
            "Marshallian externalities (labour pooling, input sharing, knowledge spillovers) "
            "vary by industry age and technological relatedness. "
            "This work links agglomeration theory to the capability-relatedness framework."
        ),
    },
    {
        "name": "labor",
        "label": "Labor Mobility & Skill",
        "keywords": [
            "labor", "labour", "worker", "displac", "mobil",
            "skill", "wage", "earning", "workforce", "mismatch",
            "complementar", "co-worker", "coworker", "pioneer plant",
            "job", "employ", "hiring", "inter-industry", "return migr",
        ],
        "summary": (
            "Workers are the primary channel through which capabilities move: "
            "Neffke documents that inter-industry labor flows track skill relatedness, "
            "that displaced workers' re-employment wages depend on how related their "
            "new industry is to their old one, and that coworker complementarity "
            "generates measurable productivity effects."
        ),
    },
    {
        "name": "complexity",
        "label": "Networks, Complexity & Methods",
        "keywords": [
            "network", "backbon", "complex", "information-theoret",
            "diffusion", "business travel", "node vector", "random treatment",
            "nonexperimental", "bayesian", "multination", "catalyst",
            "AI", "generative", "stack overflow", "consumer behavior",
            "urban system", "large cities", "size in firms",
        ],
        "summary": (
            "A methodological and applied strand: network backboning to extract "
            "latent structure from noisy networks; information-theoretic tests for "
            "co-location; using millions of 'random treatments' in observational data "
            "as a natural experiment design; and empirical work on knowledge diffusion "
            "via business travel, AI adoption, and firm information consumption."
        ),
    },
]

# Papers not matching any theme go here
FALLBACK_THEME = {
    "name": "other",
    "label": "Applied & Emerging Work",
    "summary": (
        "Case studies, policy applications, and newer work including urban coherence, "
        "AI and the geography of coding, green transition, and tourism exports. "
        "These papers apply the relatedness and capability framework to specific "
        "empirical contexts rather than developing the core theory."
    ),
}


# ── Assignment ────────────────────────────────────────────────────────────────

def assign_theme(title: str) -> str:
    """
    Assign a paper to a theme by checking its title against keyword lists.
    Returns the theme name. Falls back to 'other' if no keywords match.

    Priority: themes are checked in order, first match wins.
    This means relatedness keywords take priority over labor keywords,
    which matters for papers at the intersection (e.g. skill-relatedness
    and diversification belong in 'relatedness', not 'labor').
    """
    t = title.lower()
    for theme in THEMES:
        if any(kw in t for kw in theme["keywords"]):
            return theme["name"]
    return FALLBACK_THEME["name"]


# ── Rendering ─────────────────────────────────────────────────────────────────

def abstract_digest(text: str | None, max_chars: int = 250) -> str:
    """Two sentences, hard capped at max_chars."""
    if not text:
        return ""
    sentences = text.replace("  ", " ").split(". ")
    out = ". ".join(sentences[:2]).strip()
    if not out.endswith("."):
        out += "."
    if len(out) > max_chars:
        out = out[:max_chars] + "..."
    return out


def render_spine(theme_groups: dict[str, list[dict]]) -> str:
    """
    Render the always-loaded spine. For each theme:
      - 2-sentence summary of Neffke's contribution
      - Top 3 papers by citations (title + year + cites — no abstracts)
      - Total count + pointer to full file
    """
    all_themes = THEMES + [FALLBACK_THEME]
    lines = [
        "# Frank Neffke — Research Spine",
        "",
        "This file is always loaded by frankGPT. It gives enough orientation to "
        "advise on any topic Neffke has worked on and to cite his most influential papers.",
        "",
        "For the full paper list in a theme, load the corresponding detail file:",
        "`.claude/skills/frankGPT/knowledge/index_neffke_<theme>.md`",
        "",
        "---",
        "",
    ]

    for theme_def in all_themes:
        name    = theme_def["name"]
        label   = theme_def["label"]
        summary = theme_def["summary"]
        papers  = theme_groups.get(name, [])

        if not papers:
            continue

        top3    = sorted(papers, key=lambda w: w["cited_by_count"], reverse=True)[:3]
        n_total = len(papers)

        lines.append(f"## {label}  ({n_total} papers)")
        lines.append("")
        lines.append(summary)
        lines.append("")
        lines.append("**Key papers:**")

        for w in top3:
            cites = f"{w['cited_by_count']}c" if w["cited_by_count"] else "n.c."
            venue = w.get("venue") or ""
            venue_str = f"  *{venue}*" if venue else ""
            lines.append(f"- {w['title']} ({w['year']}, {cites}){venue_str}")

        lines.append(f"→ Full list: `index_neffke_{name}.md`")
        lines.append("")

    return "\n".join(lines)


def render_detail(theme_def: dict, papers: list[dict]) -> str:
    """
    Render a per-theme detail file. Full entries with abstract digests,
    sorted by citation count descending.
    """
    name    = theme_def["name"]
    label   = theme_def["label"]
    summary = theme_def["summary"]

    lines = [
        f"# Neffke — {label}",
        "",
        summary,
        "",
        f"**{len(papers)} papers.** Sorted by citation count.",
        "",
        "---",
        "",
    ]

    for w in sorted(papers, key=lambda x: x["cited_by_count"], reverse=True):
        year   = w.get("year") or "n.d."
        venue  = w.get("venue") or "venue unknown"
        cites  = w.get("cited_by_count", 0)
        doi    = w.get("doi") or ""
        digest = abstract_digest(w.get("abstract"))

        cite_str = f"{cites:,} citations" if cites else "no citation data"

        # Check if a compressed full-text version exists for this paper
        compressed_matches = list(COMPRESSED_DIR.glob(f"{year}_*.md")) if COMPRESSED_DIR.exists() else []
        title_slug = re.sub(r"[^a-z0-9]+", "_", w["title"].lower())[:40]
        full_text_file = next(
            (f for f in compressed_matches if title_slug[:20] in f.stem.lower()),
            None
        )

        block = [f"## {w['title']} ({year})"]
        block.append(f"**{venue}** | {cite_str}")
        if doi:
            block.append(f"DOI: {doi}")
        if full_text_file:
            block.append(f"**Full text:** `compressed/{full_text_file.name}`")
        if digest:
            block.append(digest)
        block.append("")
        lines.extend(block)

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    papers = json.loads(METADATA_PATH.read_text())

    # Deduplicate by DOI (some papers appear multiple times in the raw metadata
    # from OpenAlex pagination if a work is indexed under multiple IDs)
    seen: set[str] = set()
    deduped = []
    for w in papers:
        key = w.get("doi") or w.get("id") or w["title"]
        if key not in seen:
            seen.add(key)
            # Clean up titles: remove embedded newlines and extra spaces
            w["title"] = " ".join(w["title"].split())
            deduped.append(w)
    papers = deduped
    print(f"After dedup: {len(papers)} unique papers (from {len(json.loads(METADATA_PATH.read_text()))} raw)")

    # Assign each paper to a theme
    theme_groups: dict[str, list[dict]] = {t["name"]: [] for t in THEMES}
    theme_groups[FALLBACK_THEME["name"]] = []

    for w in papers:
        theme = assign_theme(w["title"])
        theme_groups[theme].append(w)

    # Report assignment
    print("Theme assignment:")
    all_themes = THEMES + [FALLBACK_THEME]
    for t in all_themes:
        n = len(theme_groups[t["name"]])
        titles = [w["title"][:55] for w in theme_groups[t["name"]]]
        print(f"  {t['name']:<15} {n:>3} papers")
        for title in titles:
            print(f"             • {title}")

    # Write spine
    spine_md = render_spine(theme_groups)
    spine_path = OUT_DIR / "index_neffke_spine.md"
    spine_path.write_text(spine_md, encoding="utf-8")
    spine_tokens = len(spine_md) // 4
    print(f"\nWrote spine → {spine_path}  (~{spine_tokens:,} tokens)")

    # Write per-theme detail files
    for theme_def in all_themes:
        name   = theme_def["name"]
        papers = theme_groups[name]
        if not papers:
            continue
        md = render_detail(theme_def, papers)
        out_path = OUT_DIR / f"index_neffke_{name}.md"
        out_path.write_text(md, encoding="utf-8")
        tokens = len(md) // 4
        print(f"Wrote detail → {out_path.name}  ({len(papers)} papers, ~{tokens:,} tokens)")

    print(f"\nToken summary:")
    print(f"  Before: index_neffke.md            ~9,200 tokens (always loaded)")
    print(f"  After:  index_neffke_spine.md       ~{spine_tokens:,} tokens (always loaded)")
    print(f"          index_neffke_<theme>.md     loaded on demand only")

    # Remind about SKILL.md update
    print(f"\nDone. Update SKILL.md to load 'index_neffke_spine.md' instead of 'index_neffke.md'.")


if __name__ == "__main__":
    main()
