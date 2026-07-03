"""
Step 4b — Build fine-tuning training data for SPECTER2 domain adaptation.

Constructs (anchor, positive) text pairs from the heterogeneous citation graph:

  Edge type        Source file                      Count (approx)
  ─────────────────────────────────────────────────────────────────
  paper → paper    papers.csv cited_works            ~39 000
  part  → paper    part_source_papers.csv            ~4 100
  paper → part     paper_mentions_part.csv           ~1 800
  project → part   projects.csv + parts.csv (join)  ~65 000
  paper ↔ patent   Marx & Fuegi PPP × Oldham corpus  ~2 900
  project ↔ paper  iGEM wiki DOIs × papers.csv        ~1 200
  project ↔ paper  project→part→paper (part bridge)   ~1 600

The paper↔patent edge is the ONLY one that brings the patent genre into
training, so it is what teaches the adapter to place patents in the same
semantic space as papers, parts and projects. Its patent side is matched to
our Oldham corpus via representative grant number; its paper side is taken
from papers.csv when present and otherwise fetched from OpenAlex (cached).

Project↔paper links come from two complementary sources: (1) papers a team
cited on its wiki (the most direct 'student project → literature' signal), and
(2) the part bridge project→part→paper, where a team's part is tied to the
paper it was derived from or that mentions it. Both are scoped in-corpus (kept
only when the paper is already in papers.csv); the wiki source needs a cached
DOI→OpenAlex-id lookup, the part-bridge source is fully offline.

All edge types encode the same "built upon / used" signal.
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

import argparse
import json
import random
import re
import sys
import time
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PROCESSED = REPO_ROOT / "data" / "processed"
OUT_DIR   = REPO_ROOT / "data" / "finetune"

# Marx & Fuegi Patent–Paper Pairs (paper → citing patent links) and the Oldham
# synthetic-biology patent corpus that our patents.csv is built from.
PPP_CSV          = REPO_ROOT / "data" / "raw" / "ppp" / "patent_paper_pairs.csv"
OLDHAM_ABSTRACTS = PROCESSED / "oldham_patent_abstracts.csv"
# Cache of OpenAlex-fetched abstracts for PPP-linked papers not in our corpus.
# Keyed by bare OpenAlex work id; empty string means "fetched, no abstract".
PPP_PAPER_CACHE  = OUT_DIR / "ppp_paper_text_cache.json"

# iGEM wiki-cited DOIs (project → paper), and a cache mapping each DOI to its
# OpenAlex work id. Keyed by normalised DOI; empty string means "resolved, not
# found in OpenAlex". Only a DOI→id lookup — no abstract text is fetched here.
WIKI_DOIS_CSV    = PROCESSED / "igem_wiki_dois.csv"
WIKI_DOI_CACHE   = OUT_DIR / "wiki_doi_openalex_cache.json"

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
# Edge type 5: paper ↔ patent (a USPTO patent cites this paper)
# ─────────────────────────────────────────────────────────────────────────────

def _bare_patent_number(value) -> str:
    """
    Reduce a USPTO grant number to a comparable bare digit string.

    Our corpus stores grants as 'US9121036' (oldham rep_patent) while the PPP
    dataset stores them as 'US-10000036'. Stripping to the digit run lets the
    two be joined. Returns "" when no number is present.
    """
    if not value:
        return ""
    m = re.search(r"(\d{5,})", str(value))
    return m.group(1) if m else ""


def build_patent_text_lookup() -> dict:
    """
    Map bare USPTO grant number → (patent_id, patent_text) for our corpus.

    patents.csv uses opaque family ids, but oldham_patent_abstracts.csv carries
    both that family id (`id`) and the representative grant number (`rep_patent`),
    plus a ready-made title+abstract `text` field. We key on the representative
    grant so PPP's citing-patent numbers can be matched back to a patent we hold,
    and we emit the family id so pairs stay traceable to patents.csv.
    """
    df = pd.read_csv(OLDHAM_ABSTRACTS)
    lookup = {}
    for _, row in df.iterrows():
        bare = _bare_patent_number(row.get("rep_patent"))
        pid  = clean_text(row.get("id"))
        text = clean_text(row.get("text"))
        if bare and pid and len(text) >= MIN_TEXT_LEN:
            lookup[bare] = (pid, text)
    return lookup


def _match_ppp_to_corpus(patent_lookup: dict) -> pd.DataFrame:
    """
    Stream the ~548k-row PPP file and keep only rows whose citing patent is one
    of ours. PPP is large, so we read it in chunks (usecols keeps it light).

    Returns a DataFrame with columns: paperid (bare W-id), bare_patent.
    """
    wanted = set(patent_lookup)
    kept = []
    for chunk in pd.read_csv(PPP_CSV, usecols=["paperid", "patent"], chunksize=100_000):
        chunk = chunk.copy()
        chunk["bare_patent"] = chunk["patent"].map(_bare_patent_number)
        hit = chunk[chunk["bare_patent"].isin(wanted)]
        if len(hit):
            kept.append(hit[["paperid", "bare_patent"]])
    if not kept:
        return pd.DataFrame(columns=["paperid", "bare_patent"])
    return pd.concat(kept, ignore_index=True)


def _fetch_ppp_paper_text(work_ids: list, cache_path: Path) -> dict:
    """
    Fetch title+abstract for PPP-linked papers that are not already in our
    corpus, returning {bare W-id → text}.

    Cache-aware and restartable: results are stored to JSON, so re-runs don't
    re-hit the API. Ids that come back without an abstract are cached as ""
    so they are not retried. Requires OPENALEX_EMAIL/API_KEY in .env for the
    polite pool (optional but faster).
    """
    cache = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())

    missing = [w for w in work_ids if w not in cache]
    if not missing:
        return cache

    # Lazy imports: only needed when we actually fetch.
    from src.ingest.openalex import fetch_works_by_ids, extract_fields
    from src.utils.schema import build_text_field
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")

    print(f"    fetching {len(missing)} PPP-linked papers from OpenAlex "
          f"(already cached: {len(cache)})...")
    got = 0
    for work in fetch_works_by_ids(missing, retrieval_reason="ppp_patent_link"):
        fields = extract_fields(work)
        wid    = fields["openalex_id"].split("/")[-1]
        text   = build_text_field(fields["title"], fields["abstract"])
        if wid and len(text) >= MIN_TEXT_LEN:
            cache[wid] = text
            got += 1

    # Record ids that returned nothing (no abstract → filtered out) so a re-run
    # doesn't keep asking OpenAlex for them.
    for w in missing:
        cache.setdefault(w, "")

    cache_path.write_text(json.dumps(cache))
    print(f"    fetched {got} new abstracts  (cache now {len(cache)})")
    return cache


def build_paper_patent_pairs(paper_text: dict, fetch_missing: bool = True) -> list:
    """
    Build paper ↔ patent positive pairs from Marx & Fuegi's Patent–Paper Pairs.

    PPP links an OpenAlex paper to a USPTO patent that cites it — a documented
    'science → technology' knowledge-use edge, the same 'built upon' signal the
    other edge types encode. This is the only edge type that introduces the
    patent genre, so it is what aligns patents with papers/parts/projects in the
    shared space.

    Patent side: matched to our corpus by representative grant number, text from
    oldham_patent_abstracts.csv. Paper side: from papers.csv when present, else
    fetched from OpenAlex (cached). Emitted in both orientations, matching the
    part↔paper convention above.

    Reference: Marx & Fuegi (2020), "Reliance on Science in Patenting",
      J. Economics & Management Strategy 29(1):72-93.
      Data: https://doi.org/10.7910/DVN/6RFQ7F
    """
    patent_lookup = build_patent_text_lookup()   # bare grant → (family id, text)
    print(f"  paper↔patent:   corpus patents with usable text: {len(patent_lookup)}")

    matched = _match_ppp_to_corpus(patent_lookup)
    print(f"                  PPP links to our patents: {len(matched)} rows "
          f"({matched['paperid'].nunique()} papers, "
          f"{matched['bare_patent'].nunique()} patents)")

    # papers.csv ids are full URLs; PPP paperids are bare (W...). Index by bare id.
    corpus_by_wid = {full.split("/")[-1]: full for full in paper_text}
    need_fetch = sorted({w for w in matched["paperid"].unique() if w not in corpus_by_wid})

    ppp_paper_text = {}
    if fetch_missing and need_fetch:
        ppp_paper_text = _fetch_ppp_paper_text(need_fetch, PPP_PAPER_CACHE)
    elif need_fetch:
        print(f"                  --no-fetch: skipping {len(need_fetch)} out-of-corpus papers")

    pairs = []
    missing = 0
    for _, row in matched.iterrows():
        wid = row["paperid"]
        pid, patent_txt = patent_lookup[row["bare_patent"]]

        if wid in corpus_by_wid:
            paper_id  = corpus_by_wid[wid]
            paper_txt = paper_text[paper_id]
        else:
            paper_id  = f"https://openalex.org/{wid}"
            paper_txt = ppp_paper_text.get(wid, "")

        if not paper_txt or not patent_txt:
            missing += 1
            continue

        pairs.append({
            "anchor_id":    paper_id,
            "anchor_text":  paper_txt,
            "positive_id":  pid,
            "positive_text": patent_txt,
            "edge_type":    "paper_patent",
        })
        pairs.append({
            "anchor_id":    pid,
            "anchor_text":  patent_txt,
            "positive_id":  paper_id,
            "positive_text": paper_txt,
            "edge_type":    "patent_paper",
        })

    print(f"                  {len(pairs):>6} pairs  ({missing} missing text)")
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Edge type 6: project ↔ paper (an iGEM team cited this paper on its wiki)
# ─────────────────────────────────────────────────────────────────────────────

def _normalise_doi(value) -> str:
    """Lowercase, strip, and drop any doi.org URL prefix."""
    if not value:
        return ""
    return (
        str(value).strip().lower()
        .replace("https://doi.org/", "")
        .replace("http://doi.org/", "")
    )


def _resolve_dois_to_wids(dois: list, cache_path: Path, fetch_missing: bool = True) -> dict:
    """
    Resolve DOIs to bare OpenAlex work ids, returning {normalised DOI → W-id}.

    This is a lightweight id lookup (select=id,doi) — no abstracts are fetched.
    Cache-aware and restartable: results are stored to JSON so re-runs don't
    re-hit the API. DOIs OpenAlex can't find are cached as "" so they are not
    retried. When fetch_missing is False, only already-cached DOIs are used
    (fully offline).
    """
    cache = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())

    missing = [d for d in dois if d not in cache]
    if not missing:
        return cache
    if not fetch_missing:
        print(f"                  --no-fetch: {len(missing)} DOIs unresolved (using {len(cache)} cached)")
        return cache

    import requests
    import os
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
    email = os.getenv("OPENALEX_EMAIL", "")
    base_params = {"mailto": email} if email else {}

    def query(chunk: list) -> dict:
        """Resolve a list of DOIs in one request. Raises on HTTP error."""
        doi_filter = "|".join(f"https://doi.org/{d}" for d in chunk)
        resp = requests.get(
            "https://api.openalex.org/works",
            params={"filter": f"doi:{doi_filter}", "per-page": len(chunk),
                    "select": "id,doi", **base_params},
            timeout=30,
        )
        resp.raise_for_status()
        out = {}
        for work in resp.json().get("results", []):
            got_doi = _normalise_doi(work.get("doi"))
            wid = work.get("id", "").split("/")[-1]
            if got_doi and wid:
                out[got_doi] = wid
        return out

    print(f"                  resolving {len(missing)} wiki DOIs via OpenAlex "
          f"(already cached: {len(cache)})...")
    batch = 50
    for i in range(0, len(missing), batch):
        chunk = missing[i : i + batch]
        try:
            cache.update(query(chunk))
        except requests.RequestException:
            # The scrape contains a few malformed DOIs (e.g. an appended
            # "pmid:..."), and one bad DOI 400s the whole batch. Fall back to
            # resolving this chunk one DOI at a time so the good ones still land.
            for d in chunk:
                try:
                    cache.update(query([d]))
                except requests.RequestException:
                    pass  # genuinely unresolvable DOI — left to cache as "" below
                time.sleep(0.05)
        time.sleep(0.15)  # polite pool

    # DOIs still unresolved after the call → cache as "" so we don't retry them.
    for d in missing:
        cache.setdefault(d, "")
    cache_path.write_text(json.dumps(cache))
    print(f"                  resolved {sum(1 for d in missing if cache.get(d))} "
          f"of {len(missing)} new DOIs")
    return cache


def build_project_paper_pairs(project_text: dict, paper_text: dict, fetch_missing: bool = True) -> list:
    """
    Build project ↔ paper positive pairs from the iGEM wiki DOI scrape.

    Each row of igem_wiki_dois.csv records a paper (by DOI) that a team cited on
    its project wiki — a direct 'the student project drew on this paper' signal,
    the most thesis-central of all the edge types (student project → literature).

    Scope: IN-CORPUS ONLY. We keep a pair only when the cited DOI resolves to a
    paper already in papers.csv, so the paper side stays inside the curated
    synthetic-biology corpus (no external text fetched). Resolving DOIs to
    OpenAlex ids is required because papers.csv is keyed by OpenAlex id, not DOI.

    Emitted in both orientations, matching the part↔paper convention above.
    """
    if not WIKI_DOIS_CSV.exists():
        print("  project↔paper:  igem_wiki_dois.csv not found — skipping")
        return []

    wiki = pd.read_csv(WIKI_DOIS_CSV)
    wiki = wiki[wiki["doi"].notna()].copy()
    wiki["doi"] = wiki["doi"].map(_normalise_doi)
    print(f"  project↔paper:  {len(wiki)} wiki (project, DOI) rows, "
          f"{wiki['doi'].nunique()} distinct DOIs")

    # Resolve DOIs → OpenAlex ids (cached), then keep only in-corpus papers.
    doi_to_wid = _resolve_dois_to_wids(
        sorted(wiki["doi"].unique()), WIKI_DOI_CACHE, fetch_missing=fetch_missing
    )
    corpus_by_wid = {full.split("/")[-1]: full for full in paper_text}

    pairs = []
    skipped = 0
    for _, row in wiki.iterrows():
        project_id = clean_text(row.get("project_id"))
        wid        = doi_to_wid.get(row["doi"], "")
        paper_id   = corpus_by_wid.get(wid, "")

        proj_txt  = project_text.get(project_id, "")
        paper_txt = paper_text.get(paper_id, "")
        if not proj_txt or not paper_txt:
            skipped += 1
            continue

        pairs.append({
            "anchor_id":    project_id,
            "anchor_text":  proj_txt,
            "positive_id":  paper_id,
            "positive_text": paper_txt,
            "edge_type":    "project_paper",
        })
        pairs.append({
            "anchor_id":    paper_id,
            "anchor_text":  paper_txt,
            "positive_id":  project_id,
            "positive_text": proj_txt,
            "edge_type":    "paper_project",
        })

    print(f"                  {len(pairs):>6} pairs  "
          f"({skipped} rows out-of-corpus or missing text)")
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Edge type 7: project ↔ paper via the part bridge (project → part → paper)
# ─────────────────────────────────────────────────────────────────────────────

def _norm_team(value) -> str:
    """Normalise a team id to a plain string. parts.csv stores it as float
    (e.g. 5794.0) while projects.csv uses int (173); coerce both to '5794'."""
    if pd.isna(value):
        return ""
    try:
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value).strip()


def build_project_paper_via_part_pairs(
    project_text: dict,
    paper_text: dict,
    doi_to_paper_id: dict,
) -> list:
    """
    Build project ↔ paper pairs by composing the two-hop path project → part → paper.

    A team's parts are already linked to papers (part_source_papers: the paper a
    part was derived from; paper_mentions_part: a paper that uses the part). Each
    part belongs to the team that submitted it, and that team has an iGEM project.
    Composing these gives a documented project ↔ paper link that is grounded in a
    shared biological part — complementary to the wiki-citation edge above, and
    often tighter (the project literally built on that paper's part).

    Fully in-corpus and offline: the paper side is resolved to papers already in
    papers.csv (paper_id directly from part_source_papers, or via doi_to_paper_id
    for paper_mentions_part). No network calls.

    Emitted in both orientations. A distinct edge_type keeps its provenance
    visible in the summary; global dedup in run() collapses any pair that also
    arises from the wiki edge.
    """
    projects = pd.read_csv(PROCESSED / "projects.csv", usecols=["id", "team_id"])
    parts    = pd.read_csv(PROCESSED / "parts.csv", usecols=["part_name", "team_id"])

    # team → projects (only projects we have text for)
    team_to_projects: dict = {}
    for _, row in projects.iterrows():
        pid  = clean_text(row.get("id"))
        team = _norm_team(row.get("team_id"))
        if team and pid in project_text:
            team_to_projects.setdefault(team, []).append(pid)

    # part_name → owning team (a registry part name is created by one team;
    # if it appears under several, we keep the first).
    partname_to_team: dict = {}
    for _, row in parts.iterrows():
        name = clean_text(row.get("part_name"))
        team = _norm_team(row.get("team_id"))
        if name and team and name not in partname_to_team:
            partname_to_team[name] = team

    # part_name → set of in-corpus paper ids, from both part↔paper sources.
    part_to_papers: dict = {}
    psp = pd.read_csv(PROCESSED / "part_source_papers.csv")
    for _, row in psp.iterrows():
        name = clean_text(row.get("part_name"))
        pid  = clean_text(row.get("paper_id"))
        if name and pid in paper_text:
            part_to_papers.setdefault(name, set()).add(pid)

    pmp = pd.read_csv(PROCESSED / "paper_mentions_part.csv")
    for _, row in pmp.iterrows():
        name = clean_text(row.get("part_name"))
        pid  = doi_to_paper_id.get(clean_text(row.get("doi")), "")
        if name and pid in paper_text:
            part_to_papers.setdefault(name, set()).add(pid)

    # Compose: for each part→paper link, fan out to the part's team's project(s).
    pairs = []
    seen  = set()  # local dedup so a team's many parts citing one paper count once
    for name, paper_ids in part_to_papers.items():
        team = partname_to_team.get(name)
        if not team:
            continue
        for project_id in team_to_projects.get(team, []):
            proj_txt = project_text.get(project_id, "")
            if not proj_txt:
                continue
            for paper_id in paper_ids:
                if (project_id, paper_id) in seen:
                    continue
                seen.add((project_id, paper_id))
                paper_txt = paper_text[paper_id]
                pairs.append({
                    "anchor_id":    project_id,
                    "anchor_text":  proj_txt,
                    "positive_id":  paper_id,
                    "positive_text": paper_txt,
                    "edge_type":    "project_paper_part",
                })
                pairs.append({
                    "anchor_id":    paper_id,
                    "anchor_text":  paper_txt,
                    "positive_id":  project_id,
                    "positive_text": proj_txt,
                    "edge_type":    "paper_project_part",
                })

    print(f"  project↔paper (via part): {len(pairs):>6} pairs  "
          f"({len(seen)} distinct project–paper links)")
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Combine, deduplicate, split, write
# ─────────────────────────────────────────────────────────────────────────────

def write_jsonl(path: Path, records: list):
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


def run(fetch_missing: bool = True):
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
    all_pairs.extend(build_paper_patent_pairs(paper_text, fetch_missing=fetch_missing))
    all_pairs.extend(build_project_paper_pairs(project_text, paper_text, fetch_missing=fetch_missing))
    all_pairs.extend(build_project_paper_via_part_pairs(project_text, paper_text, doi_to_paper_id))

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


def parse_args():
    p = argparse.ArgumentParser(
        description="Build (anchor, positive) fine-tuning pairs across papers, "
                    "parts, projects and patents."
    )
    p.add_argument(
        "--no-fetch",
        action="store_true",
        help="Do not call OpenAlex for PPP-linked papers missing from the corpus. "
             "Only paper↔patent pairs whose paper is already in papers.csv are kept.",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(fetch_missing=not args.no_fetch)
