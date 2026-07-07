"""
scripts/13_cc_heatmap.py
Temporal presence heatmap for the carbon-capture case study.
Rows = top CC cities (by total artifact count), sub-divided by artifact type.
Columns = years.
A filled cell means ≥1 artifact of that type in that city in that year.
Output: outputs/figures/cc_temporal_heatmap.png
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import matplotlib.ticker as ticker

DATA = "data/processed/artifacts_tripartite_clustered.csv"
OUT  = "outputs/figures/cc_temporal_heatmap.png"

YEAR_MIN, YEAR_MAX = 2004, 2024
N_CITIES = 20        # how many cities to show

# artifact type → colour
TYPE_COLOR = {
    "project": "#2ca02c",   # green
    "paper":   "#1f77b4",   # blue
    "patent":  "#d62728",   # red
}
TYPE_ORDER = ["project", "paper", "patent"]
TYPE_LABEL = ["iGEM project", "Academic paper", "Patent"]

# --- load & filter -----------------------------------------------------------
art = pd.read_csv(DATA)
cc  = art[art["case_study_flag"] == 1].copy()
cc  = cc[(cc["year"] >= YEAR_MIN) & (cc["year"] <= YEAR_MAX)]
cc  = cc.dropna(subset=["city"])

# select top cities by total CC artifact count
top_cities = (
    cc.groupby("city")
    .size()
    .sort_values(ascending=False)
    .head(N_CITIES)
    .index.tolist()
)
cc = cc[cc["city"].isin(top_cities)]

# build presence matrix: (city, type, year) → 1/0
years = list(range(YEAR_MIN, YEAR_MAX + 1))
presence = {}
for city in top_cities:
    for atype in TYPE_ORDER:
        sub = cc[(cc["city"] == city) & (cc["type"] == atype)]
        row = {y: int(y in sub["year"].values) for y in years}
        presence[(city, atype)] = row

# order cities: sort by year of first iGEM project, then name
first_proj = {}
for city in top_cities:
    proj_years = cc[(cc["city"] == city) & (cc["type"] == "project")]["year"]
    first_proj[city] = int(proj_years.min()) if len(proj_years) > 0 else 9999
top_cities_sorted = sorted(top_cities, key=lambda c: (first_proj[c], c))

# --- figure layout -----------------------------------------------------------
# Each city gets 3 narrow rows (project / paper / patent) + 1 separator gap
ROW_H   = 0.25   # height per type row in inches
GAP_H   = 0.12   # gap between cities
N_YEARS = len(years)

fig_h = (ROW_H * 3 + GAP_H) * N_CITIES + 1.2   # +header
fig_w = 0.38 * N_YEARS + 2.2                     # +left labels

fig, ax = plt.subplots(figsize=(fig_w, fig_h))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

cell_w = 1.0
row_unit = 1.0   # each type row occupies 1 unit; gap between city blocks = 0.4

y_positions = []   # (city, ystart) for label placement
y = 0
for city in reversed(top_cities_sorted):   # reversed so top city is at top
    city_y0 = y
    for i, atype in enumerate(reversed(TYPE_ORDER)):  # patent at bottom, project at top
        row_y = y + i
        fc = TYPE_COLOR[atype]
        for j, yr in enumerate(years):
            if presence[(city, atype)][yr]:
                rect = plt.Rectangle(
                    (j * cell_w, row_y),
                    cell_w * 0.88, row_unit * 0.82,
                    facecolor=fc, edgecolor="white", linewidth=0.0,
                    zorder=2
                )
                ax.add_patch(rect)
            else:
                # empty cell: light grey background
                rect = plt.Rectangle(
                    (j * cell_w, row_y),
                    cell_w * 0.88, row_unit * 0.82,
                    facecolor="#f0f0f0", edgecolor="white", linewidth=0.0,
                    zorder=1
                )
                ax.add_patch(rect)
    y_positions.append((city, city_y0 + 1.0))  # label at middle type row
    y += 3 + 0.5   # 3 rows + gap

total_height = y
ax.set_xlim(-0.1, N_YEARS * cell_w + 0.2)
ax.set_ylim(-0.3, total_height)

# x-axis: year labels every 2 years
ax.set_xticks([j * cell_w + cell_w * 0.44 for j, yr in enumerate(years) if yr % 2 == 0])
ax.set_xticklabels([yr for yr in years if yr % 2 == 0],
                   fontsize=8, rotation=45, ha="right")

# y-axis: city labels
ax.set_yticks([yp for _, yp in y_positions])
ax.set_yticklabels([city for city, _ in y_positions], fontsize=8.5)
ax.yaxis.set_tick_params(length=0)
ax.xaxis.set_tick_params(length=2, pad=2)

for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)

# draw light year gridlines
for j in range(N_YEARS):
    ax.axvline(j * cell_w, color="white", linewidth=0.4, zorder=0)

# legend
handles = [
    mpatches.Patch(facecolor=TYPE_COLOR[t], label=l)
    for t, l in zip(TYPE_ORDER, TYPE_LABEL)
]
ax.legend(
    handles=handles,
    loc="upper right",
    fontsize=8.5,
    framealpha=0.95,
    title="Artifact type",
    title_fontsize=8.5,
    borderpad=0.6,
    handlelength=1.2
)

ax.set_title(
    "Carbon-capture activity by city and year\n"
    "(top 20 cities by total artifact count; "
    "filled cell = ≥1 artifact in that city–year)",
    fontsize=10, fontweight="bold", pad=8, loc="left"
)

fig.tight_layout(pad=0.8)
fig.savefig(OUT, dpi=180, bbox_inches="tight", facecolor="white")
print(f"Saved {OUT}")
