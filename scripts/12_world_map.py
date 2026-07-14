"""
scripts/12_world_map.py
Three-panel world map showing geographic distribution of iGEM projects,
academic papers, and patents in synthetic biology.
Output: outputs/figures/world_map.png
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import geopandas as gpd
import geodatasets
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.style.use("default")
import matplotlib.patches as mpatches
import numpy as np

DATA = "data/processed/artifacts_tripartite_clustered.csv"
OUT  = "outputs/figures/world_map.png"

# --- load data ---------------------------------------------------------------
art = pd.read_csv(DATA)
art = art.dropna(subset=["lat", "lon"])

# aggregate to city × type counts
city_counts = (
    art.groupby(["type", "city", "lat", "lon"])
    .size()
    .reset_index(name="n")
)

# --- world basemap -----------------------------------------------------------
land = gpd.read_file(geodatasets.get_path("naturalearth.land"))

# --- colour / label config ---------------------------------------------------
TYPES   = ["project", "paper", "patent"]
TITLES  = ["iGEM student projects", "Academic papers", "Patents"]
COLORS  = ["#2ca02c", "#1f77b4", "#d62728"]   # green / blue / red
EDGEC   = ["#196319", "#1055a0", "#991b1b"]

# marker size: sqrt scaling, capped
def dot_size(n, scale=14, cap=200):
    return np.clip(np.sqrt(n) * scale, 4, cap)

# --- plot three panels -------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5),
                         subplot_kw={"aspect": "equal"})
fig.patch.set_facecolor("white")

for ax, atype, title, fc, ec in zip(axes, TYPES, TITLES, COLORS, EDGEC):
    # basemap
    land.plot(ax=ax, color="#e8e8e8", edgecolor="#b0b0b0", linewidth=0.3)

    sub = city_counts[city_counts["type"] == atype]
    # sort so small dots don't hide behind large ones
    sub = sub.sort_values("n", ascending=False)
    sizes = dot_size(sub["n"])

    ax.scatter(
        sub["lon"], sub["lat"],
        s=sizes, c=fc, edgecolors=ec, linewidths=0.35,
        alpha=0.75, zorder=3
    )

    # clean frame
    ax.set_xlim(-180, 180)
    ax.set_ylim(-65, 85)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title, fontsize=11, fontweight="bold", pad=6)
    ax.set_xlabel("", fontsize=0)
    ax.set_ylabel("", fontsize=0)
    ax.tick_params(left=False, bottom=False,
                   labelleft=False, labelbottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # per-panel annotation: city count + artifact count
    n_cities = sub["city"].nunique()
    n_arts   = int(sub["n"].sum())
    ax.annotate(
        f"{n_cities} cities · {n_arts:,} artifacts",
        xy=(0.02, 0.03), xycoords="axes fraction",
        fontsize=8, color="#444444",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#cccccc", alpha=0.85)
    )

# size legend (shared, bottom right of rightmost panel)
ax_leg = axes[2]
for n_ex, label in [(1, "1"), (10, "10"), (100, "100")]:
    ax_leg.scatter([], [], s=dot_size(n_ex), c="#888888",
                   edgecolors="#555555", linewidths=0.5,
                   label=label, alpha=0.8)
ax_leg.legend(
    title="Artifacts per city",
    title_fontsize=8, fontsize=8,
    loc="lower right", framealpha=0.9,
    handletextpad=0.4, borderpad=0.6,
    labelspacing=0.6
)

fig.suptitle(
    "Geographic distribution of synthetic biology artifacts",
    fontsize=13, fontweight="bold", y=1.01
)
fig.tight_layout(pad=0.8)
fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved {OUT}")
