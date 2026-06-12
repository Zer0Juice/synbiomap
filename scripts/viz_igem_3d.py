"""
Render igem-composite-3d.csv as an interactive 3D scatter plot.

Each point is an iGEM Registry part. X/Y/Z are pre-computed 3D embedding
coordinates (from HPI Potsdam 2025). Points are coloured by part_type.

Output: outputs/figures/igem_3d.html  (self-contained, open in any browser)
"""

import pandas as pd
import plotly.graph_objects as go

CSV_PATH = "data/embeddings/igem-composite-3d.csv"
OUT_PATH = "outputs/figures/igem_3d.html"

# ── colour palette (one per part type, cycles if needed) ────────────────────
PALETTE = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
    "#a65628", "#f781bf", "#999999", "#66c2a5", "#fc8d62",
    "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", "#e5c494",
    "#b3b3b3", "#1b9e77", "#d95f02", "#7570b3", "#e7298a",
    "#66a61e", "#e6ab02", "#a6761d", "#666666",
]

df = pd.read_csv(CSV_PATH)
part_types = sorted(df["part_type"].unique())

traces = []
for i, pt in enumerate(part_types):
    mask = df["part_type"] == pt
    sub = df[mask]
    color = PALETTE[i % len(PALETTE)]
    traces.append(
        go.Scatter3d(
            x=sub["x"],
            y=sub["y"],
            z=sub["z"],
            mode="markers",
            name=pt,
            text=sub["name"],
            hovertemplate="<b>%{text}</b><br>type: " + pt + "<extra></extra>",
            marker=dict(
                size=2,
                color=color,
                opacity=0.7,
                line=dict(width=0),
            ),
        )
    )

fig = go.Figure(data=traces)
fig.update_layout(
    title=dict(
        text="iGEM Registry Parts — 3D Embedding Space",
        font=dict(size=18),
    ),
    scene=dict(
        xaxis_title="Dim 1",
        yaxis_title="Dim 2",
        zaxis_title="Dim 3",
        bgcolor="#0d1117",
        xaxis=dict(gridcolor="#333", showbackground=True, backgroundcolor="#0d1117"),
        yaxis=dict(gridcolor="#333", showbackground=True, backgroundcolor="#0d1117"),
        zaxis=dict(gridcolor="#333", showbackground=True, backgroundcolor="#0d1117"),
    ),
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(color="#e6edf3"),
    legend=dict(
        title="Part type",
        itemsizing="constant",
        font=dict(size=11),
    ),
    margin=dict(l=0, r=0, t=50, b=0),
    height=800,
)

fig.write_html(OUT_PATH, include_plotlyjs="cdn")
print(f"Saved → {OUT_PATH}")
print(f"  {len(df):,} parts  |  {len(part_types)} types")
