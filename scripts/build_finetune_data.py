"""
Step 4b — Build fine-tuning training data for SPECTER2 domain adaptation.

Constructs (anchor, positive) text pairs from the heterogeneous citation graph:

  Edge type        Source file                      Count (approx)
  ─────────────────────────────────────────────────────────────────
  paper → paper    papers.csv cited_works            ~39 000
  part  → paper    part_source_papers.csv            ~4 100
  paper → part     paper_mentions_part.csv           ~1 800
  project → part   projects.csv + parts.csv (join)  ~65 000

All four edge types encode the same "built upon / used" signal.
SPECTER2's training objective (InfoNCE) treats same-edge pairs as positives
and all other items in the batch as negatives.

Output
------
  data/finetune/pairs_train.jsonl   90 % of pairs, shuffled
  data/finetune/pairs_val.jsonl     10 % holdout

Each JSONL line:
  {
    "anchor_id":    "<artifact id>",
    "anchor_text":  "<title + body>",
    "positive_id":  "<artifact id>",
    "positive_text":"<title + body>",
    "edge_type":    "paper_paper | part_paper | paper_part | project_part"
  }

Usage
-----
  python scripts/build_finetune_data.py
"""

import json
import random
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PROCESSED = REPO_ROOT / "data" / "processed"
OUT_DIR   = REPO_ROOT / "data" / "finetune"

# Minimum text length (characters) to include an artifact as anchor or positive.
# Very short texts don't carry enough signal to be useful supervision.
MIN_TEXT_LEN = 30

RANDOM_SEED = 42


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def clean_text(text) -> str:
    """Return stripped text, or empty string if null/whitespace."""
    if pd.isna(text):
        return ""
    return str(text).strip()


def build_text_lookup(df: pd.DataFrame, id_col: str = "id", text_col: str = "text") -> dict:
    """
    Build a dict mapping artifact id → text.
    Drops rows where id or text is missing or too short.
    """
    lookup = {}
    for _, row in df.iterrows():
        artifact_id = clean_text(row[id_col])
        text = clean_text(row.get(text_col, ""))
        if artifact_id and len(text) >= MIN_TEXT_LEN:
            lookup[artifact_id] = text
    return lookup


# ─────────────────────────────────────────────────────────────────────────────
# Load all artifact text
# ─────────────────────────────────────────────────────────────────────────────

def load_text_lookups():
    print("Loading processed CSVs...")

    papers   = pd.read_csv(PROCESSED / "papers.csv")
    projects = pd.read_csv(PROCESSED / "projects.csv")
    parts    = pd.read_csv(PROCESSED / "parts.csv")

    paper_text   = build_text_lookup(papers)
    project_text = build_text_lookup(projects)
    # Parts use part_name as the natural join key in edge files,
    # but the canonical id in parts.csv follows the shared schema.
    # We build two lookups so we can resolve either key.
    part_text_by_id   = build_text_lookup(parts)
    part_text_by_name = build_text_lookup(parts, id_col="part_name")

    # Short W-ID → full OpenAlex URL, for resolving cited_works references.
    # cited_works in papers.csv stores bare W-IDs (e.g. "W2113983551"),
    # while the papers id column stores the full URL.
    w_id_to_full = {}
    for full_id in paper_text:
        short = full_id.replace("https://openalex.org/", "")
        w_id_to_full[short] = full_id

    # DOI → full OpenAlex paper ID, built from part_source_papers which has both.
    doi_to_paper_id = {}
    psp = pd.read_csv(PROCESSED / "part_source_papers.csv")
    for _, row in psp.iterrows():
        doi = clean_text(row.get("doi", ""))
        pid = clean_text(row.get("paper_id", ""))
        if doi and pid:
            doi_to_paper_id[doi] = pid

    print(f"  Papers:   {len(paper_text):>6} with usable text")
    print(f"  Projects: {len(project_text):>6} with usable text")
    print(f"  Parts:    {len(part_text_by_name):>6} with usable text")

    return (
        paper_text, project_text,
        part_text_by_id, part_text_by_name,
        w_id_to_full, doi_to_paper_id,
        papers,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Edge type 1: paper → paper (within-corpus citations)
# ─────────────────────────────────────────────────────────────────────────────

def build_paper_paper_pairs(papers: pd.DataFrame, paper_text: dict, w_id_to_full: dict) -> list:
    """
    Each paper's cited_works field lists bare W-IDs of papers it cites.
    We keep only within-corpus pairs (both anchor and positive must be in paper_text).

    This edge type mirrors the exact supervision signal SPECTER2 was originally
    trained on — making it the strongest and most compatible edge type.
    """
    pairs = []
    skipped = 0

    for _, row in papers.iterrows():
        anchor_id   = clean_text(row.get("id", ""))
        cited_raw   = clean_text(row.get("cited_works", ""))
        anchor_text = paper_text.get(anchor_id, "")

        if not anchor_text or not cited_raw:
            continue

        for short_id in cited_raw.split(";"):
            short_id = short_id.strip()
            full_id  = w_id_to_full.get(short_id, "")
            pos_text = paper_text.get(full_id, "")
            if full_id and pos_text:
                pairs.append({
                    "anchor_id":    anchor_id,
                    "anchor_text":  anchor_text,
                    "positive_id":  full_id,
                    "positive_text": pos_text,
                    "edge_type":    "paper_paper",
                })
            else:
                skipped += 1

    print(f"  paper→paper:    {len(pairs):>6} pairs  ({skipped} cited outside corpus)")
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Edge type 2: part → paper (part was derived from / described in this paper)
# ─────────────────────────────────────────────────────────────────────────────

def build_part_paper_pairs(part_text_by_name: dict, paper_text: dict) -> list:
    """
    part_source_papers.csv records the paper that first described or provided
    each iGEM part. The relationship is asymmetric: the paper is the source,
    the part is the downstream artifact.

    We emit the pair in both orientations so the model sees:
      part → paper  (part was derived from this paper)
      paper → part  (paper produced this part)
    This doubles the signal without adding any new data.
    """
    psp = pd.read_csv(PROCESSED / "part_source_papers.csv")
    pairs = []
    missing = 0

    for _, row in psp.iterrows():
        part_name = clean_text(row.get("part_name", ""))
        paper_id  = clean_text(row.get("paper_id", ""))
        part_txt  = part_text_by_name.get(part_name, "")
        paper_txt = paper_text.get(paper_id, "")

        if not part_txt or not paper_txt:
            missing += 1
            continue

        # Both orientations
        pairs.append({
            "anchor_id":    part_name,
            "anchor_text":  part_txt,
            "positive_id":  paper_id,
            "positive_text": paper_txt,
            "edge_type":    "part_paper",
        })
        pairs.append({
            "anchor_id":    paper_id,
            "anchor_text":  paper_txt,
            "positive_id":  part_name,
            "positive_text": part_txt,
            "edge_type":    "paper_part",
        })

    print(f"  part↔paper:     {len(pairs):>6} pairs  ({missing} missing text)")
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Edge type 3: paper → part (paper explicitly mentions/uses this part)
# ─────────────────────────────────────────────────────────────────────────────

def build_paper_mentions_pairs(
    part_text_by_name: dict,
    paper_text: dict,
    doi_to_paper_id: dict,
) -> list:
    """
    paper_mentions_part.csv records papers that explicitly cite or use an
    iGEM part by name. We resolve the DOI to an OpenAlex paper ID and emit
    both orientations, same as edge type 2.
    """
    pmp = pd.read_csv(PROCESSED / "paper_mentions_part.csv")
    pairs = []
    missing = 0

    for _, row in pmp.iterrows():
        part_name = clean_text(row.get("part_name", ""))
        doi       = clean_text(row.get("doi", ""))
        paper_id  = doi_to_paper_id.get(doi, "")
        part_txt  = part_text_by_name.get(part_name, "")
        paper_txt = paper_text.get(paper_id, "")

        if not part_txt or not paper_txt:
            missing += 1
            continue

        pairs.append({
            "anchor_id":    paper_id,
            "anchor_text":  paper_txt,
            "positive_id":  part_name,
            "positive_text": part_txt,
            "edge_type":    "paper_part",
        })
        pairs.append({
            "anchor_id":    part_name,
            "anchor_text":  part_txt,
            "positive_id":  paper_id,
            "positive_text": paper_txt,
            "edge_type":    "part_paper",
        })

    print(f"  paper↔part:     {len(pairs):>6} pairs  ({missing} unresolvable DOIs or missing text)")
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Edge type 4: project → part (iGEM team created this part)
# ─────────────────────────────────────────────────────────────────────────────

def build_project_part_pairs(project_text: dict, part_text_by_id: dict) -> list:
    """
    An iGEM team submits both a project (wiki page) and one or more biological
    parts. We match them via team_id. The relationship is 'project used/produced
    this part', which is the same 'built upon' signal as a citation.

    We use part id (not part_name) here because project_text and part_text_by_id
    both use the shared-schema id column.
    """
    projects = pd.read_csv(PROCESSED / "projects.csv")
    parts    = pd.read_csv(PROCESSED / "parts.csv")

    # Filter to artifacts with usable text before joining
    proj_with_text = projects[projects["id"].isin(project_text)]
    part_with_text = parts[parts["id"].isin(part_text_by_id)]

    merged = proj_with_text[["id", "team_id"]].merge(
        part_with_text[["id", "team_id"]].rename(columns={"id": "part_id"}),
        on="team_id",
    )

    pairs = []
    for _, row in merged.iterrows():
        proj_id   = row["id"]
        part_id   = row["part_id"]
        proj_text = project_text.get(proj_id, "")
        part_text = part_text_by_id.get(part_id, "")

        if proj_text and part_text:
            pairs.append({
                "anchor_id":    proj_id,
                "anchor_text":  proj_text,
                "positive_id":  part_id,
                "positive_text": part_text,
                "edge_type":    "project_part",
            })

    print(f"  project→part:   {len(pairs):>6} pairs")
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Combine, deduplicate, split, write
# ─────────────────────────────────────────────────────────────────────────────

def write_jsonl(path: Path, records: list):
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (
        paper_text, project_text,
        part_text_by_id, part_text_by_name,
        w_id_to_full, doi_to_paper_id,
        papers,
    ) = load_text_lookups()

    print("\nBuilding positive pairs...")
    all_pairs = []
    all_pairs.extend(build_paper_paper_pairs(papers, paper_text, w_id_to_full))
    all_pairs.extend(build_part_paper_pairs(part_text_by_name, paper_text))
    all_pairs.extend(build_paper_mentions_pairs(part_text_by_name, paper_text, doi_to_paper_id))
    all_pairs.extend(build_project_part_pairs(project_text, part_text_by_id))

    print(f"\nTotal before dedup: {len(all_pairs):,}")

    # Deduplicate on (anchor_id, positive_id) — same pair can appear in
    # multiple edge files, especially part↔paper from the two part sources.
    seen = set()
    deduped = []
    for p in all_pairs:
        key = (p["anchor_id"], p["positive_id"])
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    print(f"Total after dedup:  {len(deduped):,}")

    # Shuffle before splitting so edge types are mixed throughout both sets.
    random.seed(RANDOM_SEED)
    random.shuffle(deduped)

    split = int(len(deduped) * 0.9)
    train = deduped[:split]
    val   = deduped[split:]

    write_jsonl(OUT_DIR / "pairs_train.jsonl", train)
    write_jsonl(OUT_DIR / "pairs_val.jsonl",   val)

    # Summary by edge type
    from collections import Counter
    train_counts = Counter(p["edge_type"] for p in train)
    val_counts   = Counter(p["edge_type"] for p in val)

    print(f"\nTrain: {len(train):,} pairs")
    for edge, n in sorted(train_counts.items()):
        print(f"  {edge:<20} {n:>6}")

    print(f"\nVal:   {len(val):,} pairs")
    for edge, n in sorted(val_counts.items()):
        print(f"  {edge:<20} {n:>6}")

    print(f"\nWrote:")
    print(f"  {OUT_DIR / 'pairs_train.jsonl'}")
    print(f"  {OUT_DIR / 'pairs_val.jsonl'}")


if __name__ == "__main__":
    run()
