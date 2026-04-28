"""
Step 5b — Label clusters with Claude Haiku and optionally sub-cluster large clusters.

For each HDBSCAN cluster, this script:
  1. Finds the most representative titles (closest to the cluster centroid in
     high-dimensional UMAP space).
  2. Sends batches of clusters to Claude Haiku and gets back short topic labels
     like "CRISPR gene editing tools" or "cell-free protein synthesis".
  3. Caches results in cluster_labels.json — re-running is cheap because
     already-labeled clusters are skipped.
  4. If subclustering is enabled in config, runs a second HDBSCAN pass on large
     clusters (≥ size_threshold points) and labels each sub-cluster.
  5. Merges all labels back into all_artifacts.csv and projections.json.

Usage:
    python scripts/05b_label_clusters.py          # label new/missing clusters
    python scripts/05b_label_clusters.py --force  # clear cache and re-label all

Prerequisites:
    Run scripts/05_cluster.py first to generate:
      data/embeddings/coords_nd.npy
      data/embeddings/valid_ids.json
      data/processed/all_artifacts.csv

IMPORTANT: If you re-run step 5 (05_cluster.py), cluster integers may renumber.
Delete cluster_labels.json (and subcluster_labels.json) before running this
script so labels match the new clustering.

Output:
    data/embeddings/cluster_labels.json     — cluster_id (str) → label (str)
    data/embeddings/subcluster_labels.json  — "cluster.sub" (str) → label (str)
    data/processed/all_artifacts.csv        — adds cluster_name, subcluster_name cols
    data/embeddings/projections.json        — adds "label" and "sublabel" fields
"""

import sys
import re
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from src.utils.config import load_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_api_key() -> str:
    """Read ANTHROPIC_API_KEY from .env or environment."""
    from dotenv import load_dotenv
    import os
    load_dotenv(REPO_ROOT / '.env')
    return os.getenv('ANTHROPIC_API_KEY', '')


def _load_cache(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(cache, f, indent=2)


def _centroid_titles(
    cluster_id: int,
    labels_array: np.ndarray,
    coords_nd: np.ndarray,
    titles: list[str],
    sample_size: int,
) -> list[str]:
    """
    Return the `sample_size` titles closest to the cluster centroid in
    high-dimensional UMAP space. These are the most 'typical' members of the
    cluster — a better prompt than a random sample.
    """
    mask = labels_array == cluster_id
    if mask.sum() == 0:
        return []
    cluster_coords = coords_nd[mask]
    cluster_titles = [t for t, m in zip(titles, mask) if m]
    centroid = cluster_coords.mean(axis=0)
    dists = np.linalg.norm(cluster_coords - centroid, axis=1)
    top_idx = np.argsort(dists)[:sample_size]
    return [cluster_titles[i] for i in top_idx]


def _call_haiku(client, cluster_batches: list[list[dict]], model: str) -> list[str]:
    """
    Send one batch of clusters to Claude Haiku and return labels.

    cluster_batches: list of {"idx": int, "titles": [str, ...]} dicts
    Returns a list of label strings aligned to the input order.
    Robustly handles malformed JSON with a regex fallback.
    """
    lines = "\n".join(
        f'{item["idx"]}. Titles: {json.dumps(item["titles"])}'
        for item in cluster_batches
    )
    prompt = (
        "You are a scientific topic labeler for a synthetic biology research corpus.\n"
        "For each numbered cluster below I give you representative titles from papers, "
        "patents, and student projects.\n"
        "Write a short topic label (3–6 words) that captures the shared theme.\n\n"
        "Rules:\n"
        "- 3–6 words only\n"
        "- Do NOT start with 'synthetic biology' — that is the whole corpus\n"
        "- Use plain noun phrases: 'CRISPR gene editing', 'cell-free protein synthesis'\n"
        "- No verbs, no punctuation, no trailing period\n\n"
        f"Clusters:\n{lines}\n\n"
        'Reply ONLY with valid JSON — no explanation:\n'
        '[{"cluster_id": <number>, "label": "<label>"}, ...]'
    )

    import anthropic
    try:
        msg = client.messages.create(
            model=model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        parsed = json.loads(match.group(0)) if match else []
    except Exception as e:
        print(f"    Haiku error: {e}", flush=True)
        parsed = []

    # Build aligned output — fall back to empty string for missing slots
    result_map = {item['cluster_id']: item.get('label', '') for item in parsed}
    return [result_map.get(item['idx'], '') for item in cluster_batches]


# ---------------------------------------------------------------------------
# Main labeling function
# ---------------------------------------------------------------------------

def label_clusters(
    cluster_ids: list[int],
    labels_array: np.ndarray,
    coords_nd: np.ndarray,
    titles: list[str],
    cache: dict,
    cfg_label: dict,
    client,
) -> dict:
    """
    Label each cluster in cluster_ids. Returns updated cache dict.
    Already-cached clusters are skipped.
    """
    sample_size = cfg_label.get('sample_size', 20)
    batch_size  = cfg_label.get('batch_size', 10)
    model       = cfg_label.get('model', 'claude-haiku-4-5-20251001')

    todo = [cid for cid in cluster_ids if str(cid) not in cache]
    if not todo:
        print(f"  All {len(cluster_ids)} clusters already labeled — nothing to do.")
        return cache

    print(f"  Labeling {len(todo)} clusters (skipping {len(cluster_ids) - len(todo)} cached)…")

    for batch_start in range(0, len(todo), batch_size):
        batch_ids = todo[batch_start : batch_start + batch_size]
        batch_items = []
        for seq_idx, cid in enumerate(batch_ids, start=1):
            sample = _centroid_titles(cid, labels_array, coords_nd, titles, sample_size)
            batch_items.append({"idx": seq_idx, "cluster_id": cid, "titles": sample})

        labels_out = _call_haiku(client, [{"idx": b["idx"], "titles": b["titles"]} for b in batch_items], model)

        for item, label in zip(batch_items, labels_out):
            cache[str(item['cluster_id'])] = label

        done = min(batch_start + batch_size, len(todo))
        print(f"  {done}/{len(todo)} clusters labeled", flush=True)

    return cache


# ---------------------------------------------------------------------------
# Sub-clustering
# ---------------------------------------------------------------------------

def run_subclustering(
    cluster_ids: list[int],
    labels_array: np.ndarray,
    coords_nd: np.ndarray,
    titles: list[str],
    sub_cache: dict,
    cfg_sub: dict,
    cfg_label: dict,
    client,
) -> dict:
    """
    For each large cluster (≥ size_threshold), run a second HDBSCAN pass on
    the slice of coords_nd belonging to that cluster, then label each sub-cluster.

    Sub-cluster IDs are stored as "parent_id.sub_id" strings, e.g. "5.2".
    Returns updated sub_cache dict.
    """
    import hdbscan as hdbscan_lib

    size_threshold   = cfg_sub.get('size_threshold', 100)
    min_cluster_size = cfg_sub.get('min_cluster_size', 15)
    min_samples      = cfg_sub.get('min_samples', 5)

    large_clusters = [cid for cid in cluster_ids if (labels_array == cid).sum() >= size_threshold]
    if not large_clusters:
        print("  No clusters meet the size threshold — nothing to sub-cluster.")
        return sub_cache

    print(f"  Sub-clustering {len(large_clusters)} large clusters (≥ {size_threshold} pts)…")

    for cid in large_clusters:
        mask = labels_array == cid
        sub_coords = coords_nd[mask]
        sub_titles = [t for t, m in zip(titles, mask) if m]

        # Run HDBSCAN on the slice
        clusterer = hdbscan_lib.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric='euclidean',
            prediction_data=True,
        )
        sub_labels = clusterer.fit_predict(sub_coords)

        unique_subs = sorted(set(sub_labels))
        n_subs = sum(1 for s in unique_subs if s >= 0)

        if n_subs < 2:
            # No meaningful split — leave as-is
            print(f"    Cluster {cid}: no sub-split found (size {mask.sum()}), skipping.")
            continue

        print(f"    Cluster {cid}: {n_subs} sub-clusters from {mask.sum()} points")

        # Label each sub-cluster
        sub_ids = [s for s in unique_subs if s >= 0]
        sub_labels_dict = label_clusters(
            cluster_ids=sub_ids,
            labels_array=sub_labels,
            coords_nd=sub_coords,
            titles=sub_titles,
            cache={k.split('.')[1]: v for k, v in sub_cache.items()
                   if k.startswith(f"{cid}.")},
            cfg_label=cfg_label,
            client=client,
        )

        # Store under composite keys "parent.sub"
        for sub_id, label in sub_labels_dict.items():
            sub_cache[f"{cid}.{sub_id}"] = label

        # Store the sub_labels aligned to valid_ids so we can merge back
        # We write them into the sub_cache with a special "_assignments" key
        # Format: list of (valid_ids index within cluster, sub_label int)
        indices = [i for i, m in enumerate(mask) if m]
        sub_cache[f"_assignments_{cid}"] = list(zip(indices, sub_labels.tolist()))

    return sub_cache


# ---------------------------------------------------------------------------
# Merge labels back into projections.json and all_artifacts.csv
# ---------------------------------------------------------------------------

def merge_labels(
    projections_path: Path,
    artifacts_path: Path,
    valid_ids: list[str],
    labels_array: np.ndarray,
    cluster_labels: dict,
    subcluster_labels: dict,
    subclustering_enabled: bool,
):
    """
    Inject cluster_name and (optionally) subcluster_name into:
      - data/embeddings/projections.json
      - data/processed/all_artifacts.csv
    """
    # --- projections.json ---
    with open(projections_path) as f:
        proj = json.load(f)

    # Build lookup: valid_id → sub-cluster key
    sub_key_by_id: dict[str, str] = {}
    if subclustering_enabled:
        for key, val in subcluster_labels.items():
            if key.startswith('_assignments_'):
                parent_id = int(key.split('_assignments_')[1])
                for idx, sub_id in val:
                    if sub_id >= 0:
                        vid = valid_ids[idx]
                        sub_key_by_id[vid] = f"{parent_id}.{sub_id}"

    for entry in proj:
        cid = entry.get('cluster', -1)
        entry['label'] = cluster_labels.get(str(cid), '') if cid >= 0 else ''
        if subclustering_enabled:
            sub_key = sub_key_by_id.get(entry['id'], '')
            entry['sublabel'] = subcluster_labels.get(sub_key, '') if sub_key else ''

    with open(projections_path, 'w') as f:
        json.dump(proj, f)
    print(f"  Updated projections.json with cluster labels")

    # --- all_artifacts.csv ---
    df = pd.read_csv(artifacts_path)

    df['cluster_name'] = df['cluster_label'].apply(
        lambda c: cluster_labels.get(str(int(c)), '') if pd.notnull(c) and int(c) >= 0 else ''
    )

    if subclustering_enabled:
        id_to_sub_key = sub_key_by_id
        df['subcluster_label'] = df['id'].map(lambda i: id_to_sub_key.get(i, ''))
        df['subcluster_name']  = df['subcluster_label'].apply(
            lambda k: subcluster_labels.get(k, '') if k else ''
        )

    df.to_csv(artifacts_path, index=False)
    print(f"  Updated all_artifacts.csv with cluster_name"
          + (" and subcluster_name" if subclustering_enabled else ""))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(force: bool = False):
    cfg = load_config()
    cfg_label = cfg.get('labeling', {})
    cfg_sub   = cfg_label.get('subclustering', {})
    subclustering_enabled = cfg_sub.get('enabled', False)

    print("=== Step 5b: Label Clusters with Claude Haiku ===\n")

    embeddings_dir = REPO_ROOT / 'data' / 'embeddings'
    processed_dir  = REPO_ROOT / 'data' / 'processed'

    # --- Load prerequisites ---
    coords_nd_path = embeddings_dir / 'coords_nd.npy'
    valid_ids_path = embeddings_dir / 'valid_ids.json'
    artifacts_path = processed_dir / 'all_artifacts.csv'
    proj_path      = embeddings_dir / 'projections.json'

    for p in [coords_nd_path, valid_ids_path, artifacts_path, proj_path]:
        if not p.exists():
            print(f"ERROR: {p.name} not found. Run scripts/05_cluster.py first.")
            return

    coords_nd  = np.load(str(coords_nd_path))
    with open(valid_ids_path) as f:
        valid_ids = json.load(f)
    df = pd.read_csv(artifacts_path)

    # Build aligned titles array (same order as valid_ids / coords_nd rows)
    id_to_title = dict(zip(df['id'], df['title'].fillna('')))
    titles = [id_to_title.get(vid, '') for vid in valid_ids]
    labels_array = np.array([
        id_to_title.get(vid, None) for vid in valid_ids  # placeholder
    ])
    # Use cluster_label from df aligned to valid_ids
    id_to_cluster = dict(zip(df['id'], df['cluster_label']))
    labels_array = np.array([int(id_to_cluster.get(vid, -1)) for vid in valid_ids])

    cluster_ids = sorted(set(labels_array[labels_array >= 0].tolist()))
    print(f"Loaded {len(valid_ids)} artifacts, {len(cluster_ids)} clusters, "
          f"coords_nd shape {coords_nd.shape}")

    # --- Load or initialise caches ---
    label_cache_path = REPO_ROOT / cfg_label.get('cache_file', 'data/embeddings/cluster_labels.json')
    sub_cache_path   = REPO_ROOT / cfg_sub.get('cache_file', 'data/embeddings/subcluster_labels.json')

    if force:
        print("--force: clearing label caches.\n")
        cluster_labels    = {}
        subcluster_labels = {}
    else:
        cluster_labels    = _load_cache(label_cache_path)
        subcluster_labels = _load_cache(sub_cache_path)

    # --- Initialise Haiku client ---
    api_key = _load_api_key()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Add it to .env.")
        return
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    # --- Label clusters ---
    print(f"Labeling {len(cluster_ids)} clusters…")
    cluster_labels = label_clusters(
        cluster_ids=cluster_ids,
        labels_array=labels_array,
        coords_nd=coords_nd,
        titles=titles,
        cache=cluster_labels,
        cfg_label=cfg_label,
        client=client,
    )
    _save_cache(cluster_labels, label_cache_path)
    print(f"Saved {len(cluster_labels)} labels → {label_cache_path.name}\n")

    # --- Sub-clustering (optional) ---
    if subclustering_enabled:
        print("Sub-clustering enabled…")
        subcluster_labels = run_subclustering(
            cluster_ids=cluster_ids,
            labels_array=labels_array,
            coords_nd=coords_nd,
            titles=titles,
            sub_cache=subcluster_labels,
            cfg_sub=cfg_sub,
            cfg_label=cfg_label,
            client=client,
        )
        _save_cache(subcluster_labels, sub_cache_path)
        n_sub = sum(1 for k in subcluster_labels if not k.startswith('_'))
        print(f"Saved {n_sub} sub-cluster labels → {sub_cache_path.name}\n")

    # --- Merge labels into output files ---
    print("Merging labels into projections.json and all_artifacts.csv…")
    merge_labels(
        projections_path=proj_path,
        artifacts_path=artifacts_path,
        valid_ids=valid_ids,
        labels_array=labels_array,
        cluster_labels=cluster_labels,
        subcluster_labels=subcluster_labels,
        subclustering_enabled=subclustering_enabled,
    )

    print("\nDone. Run scripts/06_visualize.py to push labels to the website.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Label HDBSCAN clusters with Claude Haiku.")
    parser.add_argument('--force', action='store_true',
                        help="Clear the label cache and re-label all clusters from scratch.")
    args = parser.parse_args()
    run(force=args.force)
