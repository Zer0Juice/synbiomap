"""
Build a 3D embedding visualization for iGEM projects and academic papers.

Loads directly from the source CSVs and embedding cache — no dependency on
stale intermediate files (coords_nd.npy, combined_meta.json).

Pipeline:
  1. Load papers.csv and projects.csv
  2. Load embedding cache (embeddings_batches/)
  3. Build embedding matrix for all items with cached embeddings
  4. Run UMAP 3D on the 768-D embeddings
  5. Save interactive Plotly HTML

Output:
  data/embeddings/projects_papers_3d.csv
  outputs/figures/projects_papers_3d.html
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import umap
import plotly.graph_objects as go

from src.embed.embeddings import _load_cache, embeddings_to_matrix

PAPERS_PATH   = REPO_ROOT / "data/processed/papers.csv"
PROJECTS_PATH = REPO_ROOT / "data/processed/projects.csv"
CACHE_PATH    = REPO_ROOT / "data/embeddings/embeddings.json"
PROJ_PATH     = REPO_ROOT / "data/embeddings/projections.json"
CSV_OUT       = REPO_ROOT / "data/embeddings/projects_papers_3d.csv"
HTML_OUT      = REPO_ROOT / "outputs/figures/projects_papers_3d.html"

UMAP_SEED        = 42
UMAP_N_NEIGHBORS = 30
UMAP_METRIC      = "cosine"  # correct for SPECTER text embeddings

# Two-stage reduction (768D → 30D → 3D) matches the approach used in 05_cluster.py.
# Going 768D → 3D directly loses cluster topology; the intermediate step preserves it.
# See: Grootendorst (2022) "BERTopic" arXiv:2203.05794
ND_COMPONENTS = 30   # stage 1: compress to this many dims first
ND_MIN_DIST   = 0.0  # tight packing for the intermediate step
VIZ_MIN_DIST  = 0.05 # slight spacing in the final 3D for visual clarity

# ── 1. Load source data ───────────────────────────────────────────────────────
print("Loading papers and projects …")
papers   = pd.read_csv(PAPERS_PATH,   low_memory=False)
projects = pd.read_csv(PROJECTS_PATH, low_memory=False)
print(f"  papers.csv:   {len(papers):,} rows")
print(f"  projects.csv: {len(projects):,} rows")

combined = pd.concat([papers, projects], ignore_index=True)

# ── 2. Load embeddings ────────────────────────────────────────────────────────
print("Loading embedding cache …")
cache = _load_cache(str(CACHE_PATH))
print(f"  {len(cache):,} cached embeddings")

matrix, valid_ids = embeddings_to_matrix(combined, cache)
print(f"  {matrix.shape[0]:,} items have embeddings")

# Subset combined to only rows with embeddings (same order as matrix)
valid_set  = set(valid_ids)
meta       = combined[combined["id"].astype(str).isin(valid_set)].copy()
# Re-order to match the valid_ids order from embeddings_to_matrix
id_to_idx  = {vid: i for i, vid in enumerate(valid_ids)}
meta       = meta.assign(_sort=meta["id"].astype(str).map(id_to_idx))
meta       = meta.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)

# Attach 2D cluster labels from projections.json (built by 05_cluster.py) if available
if PROJ_PATH.exists():
    import json
    proj = pd.DataFrame(json.load(open(PROJ_PATH)))[["id", "cluster", "label"]]
    meta = meta.merge(proj, on="id", how="left")
else:
    meta["cluster"] = -1
    meta["label"]   = "unlabelled"

# ── 3. Two-stage UMAP: 768D → 30D → 3D ──────────────────────────────────────
print(f"Stage 1 — UMAP {matrix.shape[1]}D → {ND_COMPONENTS}D …")
stage1 = umap.UMAP(
    n_components=ND_COMPONENTS,
    n_neighbors=UMAP_N_NEIGHBORS,
    min_dist=ND_MIN_DIST,
    metric=UMAP_METRIC,
    random_state=UMAP_SEED,
    verbose=True,
)
coords_nd = stage1.fit_transform(matrix)

print(f"Stage 2 — UMAP {ND_COMPONENTS}D → 3D …")
stage2 = umap.UMAP(
    n_components=3,
    n_neighbors=UMAP_N_NEIGHBORS,
    min_dist=VIZ_MIN_DIST,
    metric="euclidean",
    random_state=UMAP_SEED,
    verbose=True,
)
xyz = stage2.fit_transform(coords_nd)

meta["x"] = xyz[:, 0]
meta["y"] = xyz[:, 1]
meta["z"] = xyz[:, 2]

# ── 4. Save CSV ───────────────────────────────────────────────────────────────
out_cols = ["id", "type", "title", "year", "city", "country",
            "case_study_flag", "cluster", "label", "x", "y", "z"]
meta[[c for c in out_cols if c in meta.columns]].to_csv(CSV_OUT, index=False)
print(f"Saved CSV → {CSV_OUT}")

# ── 5. Build Plotly figure ────────────────────────────────────────────────────
COLORS = {
    "project": "#4daf4a",   # green
    "paper":   "#377eb8",   # blue
}

traces = []
for artifact_type, group in meta.groupby("type"):
    color = COLORS.get(artifact_type, "#999999")

    hover = (
        "<b>" + group["title"].fillna("(no title)").str[:80] + "</b><br>"
        + "Year: " + group["year"].astype(str) + "<br>"
        + "City: " + group["city"].fillna("?") + "<br>"
        + "Cluster: " + group["label"].fillna("?") + "<extra></extra>"
    )

    traces.append(
        go.Scatter3d(
            x=group["x"], y=group["y"], z=group["z"],
            mode="markers",
            name=artifact_type.capitalize() + f" (n={len(group):,})",
            text=hover,
            hovertemplate="%{text}",
            marker=dict(
                size=2.5 if artifact_type == "paper" else 3.5,
                color=color,
                opacity=0.65,
                line=dict(width=0),
            ),
        )
    )

fig = go.Figure(data=traces)
fig.update_layout(
    title=dict(text="iGEM Projects & Papers — 3D Semantic Space", font=dict(size=18)),
    scene=dict(
        xaxis_title="UMAP 1",
        yaxis_title="UMAP 2",
        zaxis_title="UMAP 3",
        bgcolor="#0d1117",
        xaxis=dict(gridcolor="#2a3040", showbackground=True, backgroundcolor="#0d1117"),
        yaxis=dict(gridcolor="#2a3040", showbackground=True, backgroundcolor="#0d1117"),
        zaxis=dict(gridcolor="#2a3040", showbackground=True, backgroundcolor="#0d1117"),
    ),
    paper_bgcolor="#0d1117",
    font=dict(color="#e6edf3"),
    legend=dict(title="Artifact type", itemsizing="constant", font=dict(size=12)),
    margin=dict(l=0, r=0, t=50, b=0),
    height=800,
)

ROTATE_JS = """
(function() {
    var gd = document.querySelector('.plotly-graph-div');
    var angle = 0, r = 1.6, elev = 0.65;
    var lastInteraction = 0;
    var wasIdle = true;
    var RESUME_AFTER = 1500;
    var enabled = true;

    // ── Toggle button ─────────────────────────────────────────────────────────
    var btn = document.createElement('button');
    btn.textContent = '⏸ Pause rotation';
    btn.style.cssText = [
        'position:absolute', 'top:12px', 'right:16px', 'z-index:999',
        'background:#1e2736', 'color:#e6edf3', 'border:1px solid #3a4a60',
        'border-radius:6px', 'padding:6px 14px', 'font-size:13px',
        'cursor:pointer', 'transition:background 0.15s'
    ].join(';');
    btn.addEventListener('mouseover', function() { btn.style.background = '#2a3a50'; });
    btn.addEventListener('mouseout',  function() { btn.style.background = '#1e2736'; });
    btn.addEventListener('click', function() {
        enabled = !enabled;
        if (enabled) {
            var cam = gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene.camera;
            if (cam && cam.eye) {
                var newR = Math.sqrt(cam.eye.x * cam.eye.x + cam.eye.y * cam.eye.y);
                if (newR > 0.05) r = newR;
                elev  = cam.eye.z;
                angle = Math.atan2(cam.eye.y, cam.eye.x);
            }
            wasIdle = true;
            lastInteraction = 0;
        }
        btn.textContent = enabled ? '⏸ Pause rotation' : '▶ Resume rotation';
    });
    gd.style.position = 'relative';
    gd.appendChild(btn);

    // ── Interaction detection ─────────────────────────────────────────────────
    gd.addEventListener('mousedown', function() { lastInteraction = Date.now(); });
    gd.addEventListener('wheel',     function() { lastInteraction = Date.now(); });

    // ── Rotation loop ─────────────────────────────────────────────────────────
    setInterval(function() {
        if (!enabled) return;

        var idle = Date.now() - lastInteraction > RESUME_AFTER;
        if (!idle) {
            wasIdle = false;
            return;
        }

        if (!wasIdle) {
            var cam = gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene.camera;
            if (cam && cam.eye) {
                var newR = Math.sqrt(cam.eye.x * cam.eye.x + cam.eye.y * cam.eye.y);
                if (newR > 0.05) r = newR;
                elev  = cam.eye.z;
                angle = Math.atan2(cam.eye.y, cam.eye.x);
            }
            wasIdle = true;
        }

        angle += 0.004;
        Plotly.relayout(gd, {
            'scene.camera': {
                eye: { x: r * Math.cos(angle), y: r * Math.sin(angle), z: elev },
                up:  { x: 0, y: 0, z: 1 }
            }
        });
    }, 30);
})();
"""

fig.write_html(str(HTML_OUT), include_plotlyjs="cdn", post_script=ROTATE_JS)
print(f"Saved HTML → {HTML_OUT}")
print(f"  {len(meta):,} total  |  papers: {(meta.type=='paper').sum():,}  projects: {(meta.type=='project').sum():,}")

cs = meta[meta.get("case_study_flag", pd.Series(False, index=meta.index)).astype(bool)]
if len(cs):
    print(f"  carbon-capture items: {len(cs):,}")
