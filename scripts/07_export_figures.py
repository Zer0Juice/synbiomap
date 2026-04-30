"""
Step 7 — Export interactive figures for the website.

Produces four self-contained Plotly HTML files saved to outputs/figures/:

  fig1_umap_all.html          — UMAP of all artifacts, colored by type,
                                 carbon-capture highlighted
  fig2_umap_cc.html           — UMAP zoomed to carbon-capture subset,
                                 labeled by cluster
  fig3_city_overlap.html      — Top-30 cities ranked by semantic overlap
  fig4_cc_timeline.html       — Carbon-capture activity per city per year

Also generates:
  data/processed/city_level_carbon_capture.csv  — city-level CC overlap scores

Usage:
    python scripts/07_export_figures.py

Prerequisites:
    - data/processed/all_artifacts.csv  (output of steps 3–5b)
    - data/processed/city_level.csv     (output of 01_city_level_analysis.ipynb)
    - data/embeddings/                  (embedding cache, for CC overlap computation)
"""

import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.embed.embeddings import _load_cache

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
FIGURES_DIR = REPO_ROOT / "outputs" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_DIR = REPO_ROOT / "data" / "processed"
EMB_FILE      = REPO_ROOT / "data" / "embeddings" / "embeddings.json"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

print("Loading data…")
df = pd.read_csv(PROCESSED_DIR / "all_artifacts.csv")
city_df = pd.read_csv(PROCESSED_DIR / "city_level.csv")

# Tidy type labels for display
TYPE_LABELS = {"paper": "Paper", "project": "iGEM Project"}
df["Type"] = df["type"].map(TYPE_LABELS).fillna(df["type"])

# Named cluster or "Other" or "" (noise)
df["Cluster"] = df["cluster_name"].fillna("").astype(str)
df.loc[df["Cluster"] == "", "Cluster"] = "Unlabeled"

print(f"  {len(df):,} artifacts, {df.case_study_flag.sum()} CC-flagged")
print(f"  {len(city_df):,} cities")


# ===========================================================================
# Figure 1 — UMAP: all artifacts, colored by type, CC highlighted
# ===========================================================================

print("\nFigure 1: UMAP (all artifacts)…")

# Separate CC and non-CC points so CC can be drawn on top as a layer
non_cc = df[~df["case_study_flag"]].copy()
cc     = df[df["case_study_flag"]].copy()

fig1 = go.Figure()

# Background: non-CC points by artifact type
type_colors = {"Paper": "#4C9BE8", "iGEM Project": "#F4A24C"}
for atype, color in type_colors.items():
    subset = non_cc[non_cc["Type"] == atype]
    fig1.add_trace(go.Scattergl(
        x=subset["umap_x"],
        y=subset["umap_y"],
        mode="markers",
        name=atype,
        marker=dict(color=color, size=3, opacity=0.5),
        text=subset["title"].str[:80],
        hovertemplate="<b>%{text}</b><br>Type: " + atype + "<br>Year: %{customdata[0]}<br>City: %{customdata[1]}<extra></extra>",
        customdata=subset[["year", "city"]].values,
    ))

# Foreground: carbon-capture points, distinct color + larger marker
fig1.add_trace(go.Scattergl(
    x=cc["umap_x"],
    y=cc["umap_y"],
    mode="markers",
    name="Carbon Capture",
    marker=dict(
        color="#2CA02C",
        size=6,
        opacity=0.85,
        symbol="diamond",
        line=dict(width=0.5, color="white"),
    ),
    text=cc["title"].str[:80],
    hovertemplate="<b>%{text}</b><br>Type: %{customdata[0]}<br>Year: %{customdata[1]}<br>City: %{customdata[2]}<extra></extra>",
    customdata=cc[["Type", "year", "city"]].values,
))

fig1.update_layout(
    title="Semantic Space of Synthetic Biology Artifacts",
    xaxis=dict(title="UMAP dimension 1", showgrid=False, zeroline=False),
    yaxis=dict(title="UMAP dimension 2", showgrid=False, zeroline=False),
    legend=dict(title="Artifact type", orientation="v", x=1.01, y=0.5),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=600,
    margin=dict(l=40, r=40, t=60, b=40),
)

out1 = FIGURES_DIR / "fig1_umap_all.html"
fig1.write_html(str(out1), include_plotlyjs="cdn", full_html=True)
print(f"  Saved: {out1.name}")


# ===========================================================================
# Figure 2 — UMAP: carbon-capture subset, labeled by cluster
# ===========================================================================

print("\nFigure 2: UMAP (carbon-capture subset)…")

cc_named = cc[cc["Cluster"] != "Unlabeled"].copy()
cc_unnamed = cc[cc["Cluster"] == "Unlabeled"].copy()

# Color palette for clusters (use Plotly's qualitative scale)
cluster_list = cc_named["Cluster"].value_counts().index.tolist()
palette = px.colors.qualitative.Plotly + px.colors.qualitative.Safe + px.colors.qualitative.Prism

fig2 = go.Figure()

# Named clusters first
for i, cluster in enumerate(cluster_list):
    subset = cc_named[cc_named["Cluster"] == cluster]
    fig2.add_trace(go.Scattergl(
        x=subset["umap_x"],
        y=subset["umap_y"],
        mode="markers",
        name=cluster,
        marker=dict(color=palette[i % len(palette)], size=8, opacity=0.8),
        text=subset["title"].str[:80],
        hovertemplate="<b>%{text}</b><br>Cluster: " + cluster + "<br>Type: %{customdata[0]}<br>Year: %{customdata[1]}<br>City: %{customdata[2]}<extra></extra>",
        customdata=subset[["Type", "year", "city"]].values,
    ))

# Unlabeled CC points
if len(cc_unnamed):
    fig2.add_trace(go.Scattergl(
        x=cc_unnamed["umap_x"],
        y=cc_unnamed["umap_y"],
        mode="markers",
        name="Unlabeled",
        marker=dict(color="#BBBBBB", size=6, opacity=0.5),
        text=cc_unnamed["title"].str[:80],
        hovertemplate="<b>%{text}</b><br>Type: %{customdata[0]}<br>Year: %{customdata[1]}<extra></extra>",
        customdata=cc_unnamed[["Type", "year"]].values,
    ))

fig2.update_layout(
    title="Carbon Capture Artifacts in Semantic Space",
    xaxis=dict(title="UMAP dimension 1", showgrid=False, zeroline=False),
    yaxis=dict(title="UMAP dimension 2", showgrid=False, zeroline=False),
    legend=dict(title="Cluster", orientation="v", x=1.01, y=0.5),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=600,
    margin=dict(l=40, r=160, t=60, b=40),
)

out2 = FIGURES_DIR / "fig2_umap_cc.html"
fig2.write_html(str(out2), include_plotlyjs="cdn", full_html=True)
print(f"  Saved: {out2.name}")


# ===========================================================================
# Figure 3 — City semantic overlap: top 30 cities
# ===========================================================================

print("\nFigure 3: City semantic overlap…")

# Sort by overlap score and take top 30
top_cities = city_df.nlargest(30, "semantic_overlap").copy()
top_cities["label"] = top_cities["city"] + " (" + top_cities["country"] + ")"

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=top_cities["semantic_overlap"],
    y=top_cities["label"],
    orientation="h",
    marker=dict(
        color=top_cities["semantic_overlap"],
        colorscale="Blues",
        cmin=top_cities["semantic_overlap"].min() * 0.98,
        cmax=top_cities["semantic_overlap"].max(),
        showscale=False,
    ),
    text=top_cities["semantic_overlap"].round(3),
    textposition="inside",
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Semantic overlap: %{x:.4f}<br>"
        "Papers: %{customdata[0]}<br>"
        "iGEM projects: %{customdata[1]}<extra></extra>"
    ),
    customdata=top_cities[["n_papers", "n_projects"]].values,
))

fig3.update_layout(
    title="Top 30 Cities: Semantic Overlap Between Papers and iGEM Projects",
    xaxis=dict(
        title="Semantic overlap (cosine similarity)",
        range=[top_cities["semantic_overlap"].min() * 0.98, 1.0],
    ),
    yaxis=dict(title="", autorange="reversed"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=700,
    margin=dict(l=200, r=40, t=60, b=60),
)

out3 = FIGURES_DIR / "fig3_city_overlap.html"
fig3.write_html(str(out3), include_plotlyjs="cdn", full_html=True)
print(f"  Saved: {out3.name}")


# ===========================================================================
# Carbon capture city-level overlap (generates city_level_carbon_capture.csv)
# ===========================================================================

print("\nComputing carbon-capture city-level overlap…")

papers   = pd.read_csv(PROCESSED_DIR / "papers.csv")
projects = pd.read_csv(PROCESSED_DIR / "projects.csv")

cache = _load_cache(EMB_FILE)
print(f"  Loaded {len(cache):,} cached embeddings")

papers["city_key"]   = papers["city"].str.strip().str.lower()
projects["city_key"] = projects["city"].str.strip().str.lower()
papers["embedding"]   = papers["id"].map(cache)
projects["embedding"] = projects["id"].map(cache)

cs_papers   = papers[(papers["case_study_flag"] == True) & papers["embedding"].notna()].copy()
cs_projects = projects[(projects["case_study_flag"] == True) & projects["embedding"].notna()].copy()
print(f"  CC papers with embeddings: {len(cs_papers)}, CC projects: {len(cs_projects)}")

MIN_DOCS = 2

def filtered_centroid(df_subset, city, min_docs=MIN_DOCS):
    sub = df_subset[df_subset["city_key"] == city]
    if len(sub) < min_docs:
        return None
    vecs = np.array(sub["embedding"].tolist(), dtype=np.float32)
    c = vecs.mean(axis=0)
    norm = np.linalg.norm(c)
    return c / norm if norm > 0 else None

cs_shared = set(cs_papers["city_key"]) & set(cs_projects["city_key"])
print(f"  Cities with CC docs of both types: {len(cs_shared)}")

cs_rows = []
for city in cs_shared:
    pap_vec  = filtered_centroid(cs_papers, city)
    proj_vec = filtered_centroid(cs_projects, city)
    if pap_vec is None or proj_vec is None:
        continue
    overlap = float(np.dot(pap_vec, proj_vec))
    city_papers_all   = papers[papers["city_key"] == city]
    city_projects_all = projects[projects["city_key"] == city]
    cs_rows.append({
        "city_key":            city,
        "city":                city_papers_all["city"].iloc[0] if len(city_papers_all) else city,
        "country":             city_papers_all["country"].iloc[0] if len(city_papers_all) else "",
        "lat":                 city_papers_all["lat"].iloc[0] if len(city_papers_all) else None,
        "lon":                 city_papers_all["lon"].iloc[0] if len(city_papers_all) else None,
        "cs_semantic_overlap": overlap,
        "n_cs_papers":         len(cs_papers[cs_papers["city_key"] == city]),
        "n_cs_projects":       len(cs_projects[cs_projects["city_key"] == city]),
    })

cs_city_df = pd.DataFrame(cs_rows).sort_values("cs_semantic_overlap", ascending=False).reset_index(drop=True)
cs_out = PROCESSED_DIR / "city_level_carbon_capture.csv"
cs_city_df.to_csv(cs_out, index=False)
print(f"  Saved {len(cs_city_df)} cities → {cs_out.name}")
print(cs_city_df[["city", "country", "n_cs_papers", "n_cs_projects", "cs_semantic_overlap"]].head(10).to_string())


# ===========================================================================
# Figure 4 — Carbon-capture activity per city per year (top CC cities)
# ===========================================================================

print("\nFigure 4: Carbon-capture timeline…")

# Carbon-capture artifacts with year and city
cc_all = df[df["case_study_flag"]].dropna(subset=["city", "year"]).copy()
cc_all["city_key"] = cc_all["city"].str.strip().str.lower()

# Pick top 12 cities by total CC artifacts
top_cc_cities = cc_all["city"].value_counts().head(12).index.tolist()
cc_top = cc_all[cc_all["city"].isin(top_cc_cities)].copy()

# Aggregate by city, year, type
agg = (
    cc_top.groupby(["city", "year", "type"])
    .size()
    .reset_index(name="count")
)

fig4 = go.Figure()
type_colors4 = {"paper": "#4C9BE8", "project": "#F4A24C"}
type_labels4 = {"paper": "Paper", "project": "iGEM Project"}

for atype in ["paper", "project"]:
    subset = agg[agg["type"] == atype]
    fig4.add_trace(go.Bar(
        x=subset["year"],
        y=subset["count"],
        name=type_labels4[atype],
        marker_color=type_colors4[atype],
        hovertemplate=f"<b>{type_labels4[atype]}</b><br>Year: %{{x}}<br>Count: %{{y}}<extra></extra>",
    ))

fig4.update_layout(
    barmode="stack",
    title="Carbon Capture in Synthetic Biology: Activity Over Time (Top 12 Cities)",
    xaxis=dict(title="Year"),
    yaxis=dict(title="Number of artifacts"),
    legend=dict(title="Artifact type"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500,
    margin=dict(l=60, r=40, t=60, b=60),
)

# Add a dropdown to filter by city
buttons = [dict(
    label="All top cities",
    method="update",
    args=[{"x": [agg[agg["type"] == t]["year"] for t in ["paper", "project"]],
           "y": [agg[agg["type"] == t]["count"] for t in ["paper", "project"]]},
          {"title": "Carbon Capture in Synthetic Biology: Activity Over Time (All Top Cities)"}]
)]
for city in top_cc_cities:
    city_agg = agg[agg["city"] == city]
    buttons.append(dict(
        label=city,
        method="update",
        args=[{"x": [city_agg[city_agg["type"] == t]["year"] for t in ["paper", "project"]],
               "y": [city_agg[city_agg["type"] == t]["count"] for t in ["paper", "project"]]},
              {"title": f"Carbon Capture Activity: {city}"}]
    ))

fig4.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.01, y=1.10,
        xanchor="left",
    )]
)

out4 = FIGURES_DIR / "fig4_cc_timeline.html"
fig4.write_html(str(out4), include_plotlyjs="cdn", full_html=True)
print(f"  Saved: {out4.name}")


print("\n=== Done ===")
print(f"Figures in: {FIGURES_DIR}")
for f in sorted(FIGURES_DIR.glob("fig*.html")):
    size_kb = f.stat().st_size // 1024
    print(f"  {f.name}  ({size_kb} KB)")
