"""
Step 4d — Cross-genre retrieval evaluation (recall@k).

Purpose
-------
This is the validation that justifies the shared-embedding method in the
manuscript. The whole point of fine-tuning SPECTER2 is to place papers,
patents, projects and parts in ONE comparable semantic space. This script
measures whether that actually works, by testing cross-genre retrieval:

  "Given a patent, does its linked paper rank near the top of all candidate
   papers?"  — and the same for project↔paper links.

We report the standard information-retrieval metrics:
  recall@k — fraction of queries whose correct match is in the top k results.
  MRR      — mean reciprocal rank (1/rank of the correct match, averaged);
             rewards putting the right answer higher, not just in the top k.
  Reference: Manning, Raghavan & Schütze (2008), *Introduction to Information
             Retrieval*, ch. 8 (evaluation of ranked retrieval).

We run the SAME test on two encoders and compare:
  baseline  — off-the-shelf SPECTER2 (base + proximity adapter), as used in
              src/embed/embeddings.py.
  finetuned — SPECTER2 base + our fine-tuned adapter (models/specter2_synbio).
If fine-tuning helped cross-genre comparability, the finetuned column should
show higher recall@k and MRR, especially on the patent and project edges.

Test data
---------
The held-out validation pairs (data/finetune/pairs_val.jsonl), restricted to
the cross-genre edge types — these documents were never seen in training.

For each directed edge type (e.g. patent_paper = query is a patent, target is
its paper) we build a retrieval task:
  queries    = the distinct anchor documents
  candidates = the distinct positive documents (the pool to rank)
  relevant   = for each anchor, the positive(s) it is actually linked to
A query "hits at k" if any of its relevant targets is in the top k candidates.

Usage
-----
  python scripts/eval_recall_at_k.py
  python scripts/eval_recall_at_k.py --adapter models/specter2_synbio/final
  python scripts/eval_recall_at_k.py --edges patent_paper project_paper
  python scripts/eval_recall_at_k.py --baseline-only    # before training exists
  python scripts/eval_recall_at_k.py --pool-size 5000   # realistic large pool
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

FINETUNE_DIR = REPO_ROOT / "data" / "finetune"
PROCESSED = REPO_ROOT / "data" / "processed"
DEFAULT_ADAPTER = REPO_ROOT / "models" / "specter2_synbio" / "best"

# Corpus files used to draw extra "distractor" documents for the larger-pool
# evaluation. Each maps an artifact type to the CSV holding its id + text. The
# candidate ids in the val pairs are exactly these CSV ids, so membership tells
# us each document's type (and lets us pull same-type distractors).
CORPUS_FILES = {
    "paper":   PROCESSED / "papers.csv",
    "patent":  PROCESSED / "patents.csv",
    "project": PROCESSED / "projects.csv",
}

# The cross-genre edges we care about — the ones that test whether different
# artifact types share a comparable space. (paper_paper and project_part are
# within-genre or already-easy, so they are not the interesting validation.)
DEFAULT_EDGES = [
    "patent_paper",       # given a patent, find its paper
    "paper_patent",       # given a paper, find its patent
    "project_paper",      # given a project, find a paper it cited (wiki)
    "paper_project",      # given a paper, find a project that cited it (wiki)
    "project_paper_part", # given a project, find a paper via a shared part
]


# ─────────────────────────────────────────────────────────────────────────────
# Encoders
# ─────────────────────────────────────────────────────────────────────────────

def _pick_device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_finetuned_encoder(adapter_path: Path, device: str):
    """
    Load SPECTER2 base + our fine-tuned adapter.

    Reuses Specter2Model.encode() (CLS pooling, title[SEP]abstract, max_len 256)
    so the baseline and fine-tuned models are embedded identically — only the
    adapter differs. This is important: any metric gap must come from the
    adapter, not from a difference in how we encode.
    """
    from src.embed.embeddings import Specter2Model
    from transformers import AutoTokenizer
    from adapters import AutoAdapterModel

    enc = Specter2Model.__new__(Specter2Model)  # skip __init__ (it loads proximity)
    enc.device = device
    enc.tokenizer = AutoTokenizer.from_pretrained(Specter2Model.BASE_MODEL)
    enc.model = AutoAdapterModel.from_pretrained(Specter2Model.BASE_MODEL)
    name = enc.model.load_adapter(str(adapter_path), set_active=True)
    enc.model.set_active_adapters(name)
    enc.model.to(device)
    enc.model.eval()
    return enc


# ─────────────────────────────────────────────────────────────────────────────
# Load evaluation pairs
# ─────────────────────────────────────────────────────────────────────────────

def load_edge_tasks(val_path: Path, edges: list) -> dict:
    """
    Read pairs_val.jsonl and group into per-edge retrieval tasks.

    Returns {edge_type: {
        "queries":    [(anchor_id, anchor_text), ...]        (deduped),
        "candidates": [(positive_id, positive_text), ...]    (deduped),
        "relevant":   {anchor_id: set(positive_id, ...)},
    }}
    """
    by_edge = defaultdict(list)
    with open(val_path) as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("edge_type") in edges:
                by_edge[rec["edge_type"]].append(rec)

    tasks = {}
    for edge, recs in by_edge.items():
        q_text, c_text = {}, {}
        relevant = defaultdict(set)
        for r in recs:
            q_text[r["anchor_id"]]   = r["anchor_text"]
            c_text[r["positive_id"]] = r["positive_text"]
            relevant[r["anchor_id"]].add(r["positive_id"])
        tasks[edge] = {
            "queries":    list(q_text.items()),
            "candidates": list(c_text.items()),
            "relevant":   dict(relevant),
        }
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_edge(task: dict, id2vec: dict, ks: list) -> dict:
    """
    Compute recall@k and MRR for one edge's retrieval task, given precomputed,
    L2-normalised embeddings (id → vector) for every query and candidate.

    Steps:
      1. Look up query and candidate vectors (both already unit-normalised, so a
         dot product is the cosine similarity).
      2. For each query, rank candidates by similarity and find the best
         (smallest) rank among its relevant targets.
      3. recall@k = fraction of queries whose best rank is < k; MRR = mean 1/rank.

    Embeddings are precomputed once per model in run() and shared here, so a large
    distractor pool (which many edges reuse) is only encoded once.
    """
    q_ids = [qid for qid, _ in task["queries"]   if qid in id2vec]
    c_ids = [cid for cid, _ in task["candidates"] if cid in id2vec]
    if not q_ids or not c_ids:
        return None

    q_vecs = np.array([id2vec[i] for i in q_ids], dtype=np.float32)
    c_vecs = np.array([id2vec[i] for i in c_ids], dtype=np.float32)

    sims = q_vecs @ c_vecs.T                      # (n_queries, n_candidates)
    ranked = np.argsort(-sims, axis=1)            # ranked candidate indices per query
    c_index = {cid: i for i, cid in enumerate(c_ids)}

    hits = {k: 0 for k in ks}
    rr_sum = 0.0
    n = 0
    for i, qid in enumerate(q_ids):
        rel_cols = {c_index[r] for r in task["relevant"][qid] if r in c_index}
        if not rel_cols:
            continue
        n += 1
        order = ranked[i]
        best_rank = min(np.where(order == col)[0][0] for col in rel_cols)
        rr_sum += 1.0 / (best_rank + 1)
        for k in ks:
            if best_rank < k:
                hits[k] += 1

    return {
        "n_queries":  n,
        "pool_size":  len(c_ids),
        "recall":     {k: hits[k] / n if n else 0.0 for k in ks},
        "mrr":        rr_sum / n if n else 0.0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Larger-pool distractors
# ─────────────────────────────────────────────────────────────────────────────

def load_corpus_by_type() -> dict:
    """
    Load {type → {id: text}} from the processed CSVs, for drawing distractors.
    """
    import pandas as pd
    corpus = {}
    for typ, path in CORPUS_FILES.items():
        df = pd.read_csv(path)
        lut = {}
        for _, row in df.iterrows():
            cid = str(row.get("id", "")).strip()
            txt = row.get("text", "")
            if cid and isinstance(txt, str) and txt.strip():
                lut[cid] = txt.strip()
        corpus[typ] = lut
        print(f"  corpus {typ:<8} {len(lut):>6} docs")
    return corpus


def add_distractors(tasks: dict, corpus: dict, pool_size: int, seed: int = 0):
    """
    Expand each edge's candidate pool to ~pool_size by adding random same-type
    documents from the corpus that are NOT the answer to any query.

    Why: the raw val pools are tiny (~50-200), which inflates recall. A retrieval
    task over a realistic pool of same-type distractors (e.g. all ~10k papers)
    gives absolute numbers that mean something. The relevant sets are untouched,
    so a query still has exactly its true target(s) to find — just among far more
    look-alikes. Distractor sampling is seeded for reproducibility, and shared
    across edges of the same target type so it is embedded only once per model.
    """
    import random
    rng = random.Random(seed)

    # Classify every corpus id by type, and collect every id that is a true
    # answer somewhere (so we never add a real positive as a "distractor").
    id2type = {cid: typ for typ, lut in corpus.items() for cid in lut}
    positives = {cid for t in tasks.values() for cid, _ in t["candidates"]}

    shared_pool: dict = {}   # type → [(id, text), ...] sampled once, reused
    for edge, t in tasks.items():
        # Target type = the type of this edge's candidates (all one type).
        ttype = next((id2type[c] for c, _ in t["candidates"] if c in id2type), None)
        if ttype is None:
            print(f"  {edge}: could not identify target type — no distractors added")
            continue

        if ttype not in shared_pool:
            avail = [cid for cid in corpus[ttype] if cid not in positives]
            rng.shuffle(avail)
            shared_pool[ttype] = [(cid, corpus[ttype][cid]) for cid in avail[:pool_size]]

        existing = {c for c, _ in t["candidates"]}
        t["candidates"].extend(
            (cid, txt) for cid, txt in shared_pool[ttype] if cid not in existing
        )


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────

def print_report(results: dict, ks: list, model_names: list):
    """Print a per-edge comparison table across the evaluated models."""
    kcols = "  ".join(f"R@{k:<4}" for k in ks)
    header = f"{'edge':<20} {'model':<10} {'n':>5} {'pool':>6}  {kcols}  {'MRR':>6}"
    print("\n" + header)
    print("-" * len(header))
    for edge in results:
        for mname in model_names:
            r = results[edge].get(mname)
            if r is None:
                continue
            rec = "  ".join(f"{r['recall'][k]:.3f}" for k in ks)
            print(f"{edge:<20} {mname:<10} {r['n_queries']:>5} {r['pool_size']:>6}  "
                  f"{rec}  {r['mrr']:.3f}")
        print()


def run(args):
    device = _pick_device()
    print(f"Device: {device}")

    ks = sorted(int(k) for k in args.k)
    val_path = FINETUNE_DIR / "pairs_val.jsonl"
    tasks = load_edge_tasks(val_path, args.edges)

    print(f"Loaded {len(tasks)} edge tasks from {val_path.name}:")
    for edge, t in tasks.items():
        print(f"  {edge:<20} {len(t['queries']):>5} queries, "
              f"{len(t['candidates']):>5} candidates")

    # Optionally expand each candidate pool with same-type distractors so the
    # absolute recall reflects a realistic retrieval task, not a ~100-doc pool.
    if args.pool_size > 0:
        print(f"\nExpanding pools with up to {args.pool_size} distractors/type "
              f"(seed {args.seed})...")
        corpus = load_corpus_by_type()
        add_distractors(tasks, corpus, args.pool_size, seed=args.seed)
        for edge, t in tasks.items():
            print(f"  {edge:<20} pool now {len(t['candidates']):>6} candidates")

    # Which models to run
    model_names = []
    encoders = {}

    if not args.finetuned_only:
        from src.embed.embeddings import Specter2Model
        print("\nLoading baseline: SPECTER2 base + proximity adapter...")
        encoders["baseline"] = Specter2Model(device=device)
        model_names.append("baseline")

    if not args.baseline_only:
        adapter_path = Path(args.adapter)
        if not adapter_path.exists():
            print(f"\n⚠️  Fine-tuned adapter not found at {adapter_path} — "
                  f"skipping (run scripts/finetune_specter2.py first).")
        else:
            print(f"\nLoading fine-tuned: SPECTER2 base + {adapter_path}...")
            encoders["finetuned"] = load_finetuned_encoder(adapter_path, device)
            model_names.append("finetuned")

    # Gather every unique document (queries + candidates, incl. distractors) so
    # each is embedded exactly once per model — distractor pools are shared across
    # edges of the same type, so this avoids re-encoding thousands of docs.
    id2text = {}
    for t in tasks.values():
        for cid, txt in t["queries"]:
            id2text.setdefault(cid, txt)
        for cid, txt in t["candidates"]:
            id2text.setdefault(cid, txt)
    all_ids = list(id2text)
    all_texts = [id2text[i] for i in all_ids]

    # Evaluate
    results = {edge: {} for edge in tasks}
    for mname in model_names:
        print(f"\nEvaluating [{mname}] — encoding {len(all_ids):,} unique docs...")
        vecs = encoders[mname].encode(all_texts, batch_size=32, show_progress_bar=True)
        vecs = vecs / (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12)
        id2vec = {i: v for i, v in zip(all_ids, vecs)}
        for edge, task in tasks.items():
            results[edge][mname] = evaluate_edge(task, id2vec, ks)
            r = results[edge][mname]
            print(f"  {edge:<20} R@{ks[0]}={r['recall'][ks[0]]:.3f}  MRR={r['mrr']:.3f}")

    print_report(results, ks, model_names)

    # Save machine-readable results next to the adapter (or in models/)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"ks": ks, "models": model_names, "results": results}, indent=2))
    print(f"Saved: {out}")


def parse_args():
    p = argparse.ArgumentParser(description="Cross-genre recall@k evaluation for SPECTER2 fine-tuning.")
    p.add_argument("--adapter", default=str(DEFAULT_ADAPTER),
                   help=f"Fine-tuned adapter directory (default: {DEFAULT_ADAPTER})")
    p.add_argument("--edges", nargs="+", default=DEFAULT_EDGES,
                   help="Edge types to evaluate (default: the cross-genre edges)")
    p.add_argument("--k", nargs="+", default=[1, 5, 10],
                   help="Recall cutoffs (default: 1 5 10)")
    p.add_argument("--baseline-only", action="store_true",
                   help="Only run the off-the-shelf SPECTER2 baseline")
    p.add_argument("--finetuned-only", action="store_true",
                   help="Only run the fine-tuned adapter")
    p.add_argument("--pool-size", type=int, default=0,
                   help="Add up to this many same-type distractor docs to each "
                        "candidate pool for a realistic retrieval task (0 = off, "
                        "use only the val positives). E.g. 5000 ranks each target "
                        "against ~5000 look-alikes. Capped at the corpus size.")
    p.add_argument("--seed", type=int, default=0,
                   help="Seed for reproducible distractor sampling (default: 0)")
    p.add_argument("--out", default=str(REPO_ROOT / "models" / "specter2_synbio" / "recall_at_k.json"),
                   help="Where to save the results JSON")
    return p.parse_args()


if __name__ == "__main__":
    run(parse_args())
