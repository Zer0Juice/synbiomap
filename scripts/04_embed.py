"""
Step 4 — Generate embeddings.

Loads all processed CSVs, generates dense vector embeddings for each artifact
using a sentence-transformer model, and caches results.

The cache is incremental: already-embedded items are skipped, so it is safe
to re-run this script after adding new data.

Usage:
    python scripts/04_embed.py

Output:
    data/embeddings/embeddings.json
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
from src.utils.config import load_config
from src.embed.embeddings import load_model, generate_embeddings

def run():
    cfg = load_config()

    print("=== Step 4: Generate Embeddings ===\n")

    # --- 1. Load all processed CSVs ---
    processed_dir = REPO_ROOT / 'data' / 'processed'
    dfs = []
    for name in ['papers', 'patents', 'projects', 'parts']:
        path = processed_dir / f'{name}.csv'
        if path.exists() and path.stat().st_size > 0:
            try:
                df = pd.read_csv(path)
                if len(df) > 0:
                    dfs.append(df)
                    print(f"Loaded {len(df)} records from {name}.csv")
                else:
                    print(f"Empty: {name}.csv (skipping)")
            except Exception as e:
                print(f"Could not read {name}.csv: {e} (skipping)")
        else:
            print(f"Not found or empty: {name}.csv (skipping)")

    if not dfs:
        print("ERROR: No processed CSVs found. Run steps 01–03 first.")
        return None

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal: {len(combined)} artifacts across {combined['type'].nunique()} types")

    # --- 2. Load embedding model ---
    # Using SPECTER2 (allenai/specter2_base): a model trained on scientific
    # papers using citation-informed contrastive learning. It produces
    # 768-dimensional embeddings that capture scientific meaning well across
    # patents, papers, and student projects.
    # First run downloads ~440 MB (base model) + adapter weights.
    # Reference: Singh et al. (2022) "SciRepEval." arXiv:2211.13308.
    model_name = cfg['embedding']['model']
    print(f"\nLoading model: {model_name}")
    print("(First run downloads ~440 MB of model weights — this is normal.)")
    model = load_model(model_name)
    print("Model loaded.")

    # --- 3. Generate and cache embeddings ---
    cache_file = REPO_ROOT / 'data' / 'embeddings' / 'embeddings.json'
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    embedding_cache = generate_embeddings(
        df=combined,
        model=model,
        text_col=cfg['embedding']['text_field'],
        id_col='id',
        cache_file=cache_file,
        batch_size=cfg['embedding']['batch_size'],
    )

    print(f"\nEmbedding cache has {len(embedding_cache)} entries.")
    print(f"Saved to {cache_file.relative_to(REPO_ROOT)}")

    return embedding_cache


if __name__ == "__main__":
    run()
