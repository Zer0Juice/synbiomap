# ── Step 5 preview plots ───────────────────────────────────────────────────────
# Three views of the same 2D layout to help judge whether parameters look right.
#   fig5  — coloured by cluster (original)
#   fig5b — coloured by artifact type (paper=blue, project=green)
#   fig5c — per-cluster composition vs. expected baseline (papers vs. projects)

import json
import yaml
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ → repo root

# When this script is %run from a Jupyter notebook, render plots inline.
# When run from the terminal, fall back to the default (browser).
try:
    get_ipython()
    pio.renderers.default = 'notebook'
except NameError:
    pass

# Read UMAP/HDBSCAN parameters from settings.yaml so the plot titles are accurate.
# The notebook parameters cell writes these values before running any script.
_cfg_path = REPO_ROOT / 'config' / 'settings.yaml'
with open(_cfg_path) as _f:
    _cfg = yaml.safe_load(_f)

UMAP_N_NEIGHBORS         = _cfg['umap']['n_neighbors']
UMAP_MIN_DIST            = _cfg['umap']['min_dist']
HDBSCAN_MIN_CLUSTER_SIZE = _cfg['clustering']['min_cluster_size']
HDBSCAN_MIN_SAMPLES      = _cfg['clustering']['min_samples']

# Load the projections saved by the script
_proj_path = REPO_ROOT / 'data' / 'embeddings' / 'projections.json'
with open(_proj_path) as _f:
    _proj = pd.DataFrame(json.load(_f))

_counts     = _proj['cluster'].value_counts().sort_index()
_n_clusters = int((_counts.index >= 0).sum())
_n_noise    = int(_counts.get(-1, 0))

_proj['cluster_str'] = _proj['cluster'].apply(
    lambda c: 'noise' if c == -1 else f'cluster {c}'
)

_noise     = _proj[_proj['cluster'] == -1]
_clustered = _proj[_proj['cluster'] >= 0]

# Merge in metadata (title, type, year) for hover text
_artifacts_path = REPO_ROOT / 'data' / 'processed' / 'all_artifacts.csv'
_meta = pd.read_csv(_artifacts_path)[['id', 'title', 'type', 'year']]
_clustered = _clustered.merge(_meta, on='id', how='left')
_noise     = _noise.merge(_meta, on='id', how='left')
# Full merge (including noise) for the type-coloured plot
_proj_meta = _proj.merge(_meta, on='id', how='left')

# ── Plot 1: coloured by cluster ────────────────────────────────────────────────
fig5 = px.scatter(
    _clustered,
    x='x', y='y',
    color='cluster_str',
    hover_data=['title', 'type', 'year'],
    opacity=0.7,
    title=(
        f'UMAP 2D Projection — {_n_clusters} clusters, {_n_noise} noise points<br>'
        f'<sup>n_neighbors={UMAP_N_NEIGHBORS}  min_dist={UMAP_MIN_DIST}  '
        f'min_cluster_size={HDBSCAN_MIN_CLUSTER_SIZE}  min_samples={HDBSCAN_MIN_SAMPLES}</sup>'
    ),
    labels={'x': 'UMAP 1', 'y': 'UMAP 2', 'cluster_str': 'Cluster'},
)
fig5.update_traces(marker_size=3)
fig5.add_scatter(
    x=_noise['x'], y=_noise['y'],
    mode='markers',
    marker=dict(size=2, color='#cccccc', opacity=0.3),
    name='noise',
    hovertemplate='noise<br>%{customdata[0]}',
    customdata=_noise[['title']].values,
)
fig5.update_layout(
    showlegend=False,
    xaxis=dict(showticklabels=False),
    yaxis=dict(showticklabels=False),
    height=600,
)
fig5.show()

print(f"\nCluster size distribution (top 20):")
print(_counts.head(21).to_string())

# ── Plot 2: coloured by artifact type ─────────────────────────────────────────
# Papers = blue, Projects = green, noise = light grey.
# Each type is drawn as a separate trace so the legend is clean.

_TYPE_COLORS = {
    'paper':   '#4c72b0',   # blue
    'project': '#55a868',   # green
    'patent':  '#dd8452',   # orange (if present)
}

fig5b = go.Figure()

for _type, _color in _TYPE_COLORS.items():
    _subset = _proj_meta[
        (_proj_meta['type'] == _type) & (_proj_meta['cluster'] >= 0)
    ]
    if _subset.empty:
        continue
    fig5b.add_scatter(
        x=_subset['x'], y=_subset['y'],
        mode='markers',
        marker=dict(size=3, color=_color, opacity=0.6),
        name=_type.capitalize(),
        customdata=_subset[['title', 'year']].values,
        hovertemplate='%{customdata[0]}<br>%{customdata[1]}',
    )

# Noise points — same grey regardless of type
_noise_all = _proj_meta[_proj_meta['cluster'] == -1]
fig5b.add_scatter(
    x=_noise_all['x'], y=_noise_all['y'],
    mode='markers',
    marker=dict(size=2, color='#cccccc', opacity=0.25),
    name='noise',
    hovertemplate='noise<br>%{customdata[0]}',
    customdata=_noise_all[['title']].values,
)

fig5b.update_layout(
    title='UMAP 2D Projection — coloured by artifact type',
    xaxis=dict(title='UMAP 1', showticklabels=False),
    yaxis=dict(title='UMAP 2', showticklabels=False),
    legend_title_text='Type',
    height=600,
)
fig5b.show()

# ── Plot 3: per-cluster composition vs. expected baseline ──────────────────────
# For each cluster, show the share of papers and projects.
# Dashed lines mark the global corpus baseline so you can see which clusters
# are disproportionately paper-heavy or project-heavy.

_comp = (
    _clustered[_clustered['type'].isin(['paper', 'project'])]
    .groupby(['cluster', 'type'])
    .size()
    .reset_index(name='n')
)

# Global expected proportions (among clustered, non-noise points only)
_global = _comp.groupby('type')['n'].sum()
_global_total = _global.sum()
_expected = {t: _global.get(t, 0) / _global_total for t in ['paper', 'project']}
print(f"\nGlobal baseline — paper: {_expected['paper']:.1%}  project: {_expected['project']:.1%}")

# Pivot to one row per cluster, compute proportions
_comp_pivot = (
    _comp.pivot_table(index='cluster', columns='type', values='n', fill_value=0)
    .reset_index()
)
for _t in ['paper', 'project']:
    if _t not in _comp_pivot.columns:
        _comp_pivot[_t] = 0
_comp_pivot['total']       = _comp_pivot['paper'] + _comp_pivot['project']
_comp_pivot['pct_paper']   = _comp_pivot['paper']   / _comp_pivot['total']
_comp_pivot['pct_project'] = _comp_pivot['project'] / _comp_pivot['total']

# Drop very small clusters to keep the chart readable
_comp_pivot = _comp_pivot[_comp_pivot['total'] >= 5].sort_values('cluster')
_comp_pivot['label'] = _comp_pivot['cluster'].apply(lambda c: f'C{c}')

fig5c = go.Figure()
fig5c.add_bar(
    x=_comp_pivot['label'], y=_comp_pivot['pct_paper'],
    name='Paper', marker_color='#4c72b0',
)
fig5c.add_bar(
    x=_comp_pivot['label'], y=_comp_pivot['pct_project'],
    name='Project', marker_color='#55a868',
)

# Dashed reference lines for the global expected shares
fig5c.add_hline(
    y=_expected['paper'], line_dash='dash', line_color='#4c72b0', opacity=0.6,
    annotation_text=f"expected paper ({_expected['paper']:.0%})",
    annotation_position='top right',
)
fig5c.add_hline(
    y=_expected['project'], line_dash='dash', line_color='#55a868', opacity=0.6,
    annotation_text=f"expected project ({_expected['project']:.0%})",
    annotation_position='bottom right',
)

fig5c.update_layout(
    barmode='stack',
    title=(
        'Per-cluster composition: papers vs. projects<br>'
        '<sup>Dashed lines = global corpus baseline. '
        'Bars above/below the dashed line show disproportionate concentration.</sup>'
    ),
    xaxis_title='Cluster',
    yaxis=dict(title='Share of cluster', tickformat='.0%', range=[0, 1]),
    legend_title_text='Type',
    height=500,
)
fig5c.show()
