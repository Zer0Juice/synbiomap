"""
Step 9 — Embed the three-type corpus with the fine-tuned SPECTER2 adapter.

Reads data/processed/artifacts_tripartite.csv (papers + projects + patents) and
embeds every document with SPECTER2 base + our synbio adapter, so all three
artifact types live in one comparable space for the city-level analysis.

Caching
-------
Vectors are written under data/embeddings/finetuned/ (its own directory), kept
separate from the base/proximity cache because the two live in different vector
spaces. The run is cache-aware and restartable: re-running only embeds documents
not already cached, so an interrupted run resumes where it left off.

Usage
-----
  python scripts/09_embed_finetuned.py
  python scripts/09_embed_finetuned.py --batch-size 32
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.embed.embeddings import load_finetuned_model, generate_embeddings, _load_cache

PROCESSED   = REPO_ROOT / "data" / "processed"
DEFAULT_CORPUS = PROCESSED / "artifacts_tripartite.csv"
ADAPTER     = REPO_ROOT / "models" / "specter2_synbio" / "best"
DEFAULT_CACHE  = REPO_ROOT / "data" / "embeddings" / "finetuned" / "embeddings.json"


def run(batch_size: int, corpus: Path, cache_file: Path):
    df = pd.read_csv(corpus, low_memory=False)
    df = df[df["text"].notna()].copy()
    print(f"Corpus: {len(df):,} documents  {df['type'].value_counts().to_dict()}")

    cache = _load_cache(cache_file)
    already = int(df["id"].isin(cache).sum())
    print(f"Already embedded (cache): {already:,} / {len(df):,}")
    if already == len(df):
        print("Nothing to do — all documents already embedded.")
        return

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    print(f"Loading fine-tuned model from {ADAPTER} ...")
    model = load_finetuned_model(ADAPTER)

    cache = generate_embeddings(
        df, model,
        cache_file=cache_file,
        batch_size=batch_size,
        checkpoint_every=256,
    )
    print(f"Done. Cache now holds {len(cache):,} embeddings at {cache_file}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Embed the tripartite corpus with the fine-tuned adapter.")
    p.add_argument("--batch-size", type=int, default=32, help="Encoding batch size (default 32)")
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS,
                   help="Corpus CSV to embed (default artifacts_tripartite.csv).")
    p.add_argument("--cache", type=Path, default=DEFAULT_CACHE,
                   help="Embedding cache file; batch files live alongside it "
                        "(default data/embeddings/finetuned/embeddings.json).")
    args = p.parse_args()
    run(args.batch_size, args.corpus, args.cache)
