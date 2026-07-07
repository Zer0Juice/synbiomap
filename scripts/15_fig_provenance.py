"""
scripts/15_fig_provenance.py
Data pipeline and provenance flowchart showing artifact counts at each stage.
Output: outputs/figures/data_provenance.png
"""

import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

OUT = "outputs/figures/data_provenance.png"

# ---- colours ----------------------------------------------------------------
C_PROJ   = "#2ca02c"   # green   — projects
C_PAPER  = "#1f77b4"   # blue    — papers
C_PAT    = "#d62728"   # red     — patents
C_SHARED = "#555555"   # dark grey — shared stages
C_OUT    = "#222222"   # black   — output boxes
BG       = "#f9f9f9"

fig, ax = plt.subplots(figsize=(13, 9))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

# ---- helpers ----------------------------------------------------------------
def box(ax, cx, cy, w, h, color, text, fontsize=9, alpha_fill=0.12, bold=False):
    fc = color + "1e" if alpha_fill < 0.15 else color + "28"  # approximate hex alpha
    rect = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.06",
        linewidth=1.4, edgecolor=color, facecolor="white",
        zorder=3
    )
    ax.add_patch(rect)
    # thin fill
    fill = FancyBboxPatch(
        (cx - w/2 + 0.03, cy - h/2 + 0.03), w - 0.06, h - 0.06,
        boxstyle="round,pad=0.04",
        linewidth=0, facecolor=color, alpha=alpha_fill, zorder=2
    )
    ax.add_patch(fill)
    fw = "bold" if bold else "normal"
    ax.text(cx, cy, text, ha="center", va="center",
            fontsize=fontsize, color=color, fontweight=fw, zorder=4,
            multialignment="center")

def arrow(ax, x0, y0, x1, y1, color=C_SHARED):
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3,
                        mutation_scale=12),
        zorder=5
    )

def label(ax, cx, cy, text, color="#777777", fontsize=8):
    ax.text(cx, cy, text, ha="center", va="center",
            fontsize=fontsize, color=color, style="italic", zorder=4)

# ---- ROW 1: data source labels (titles) ------------------------------------
y_src = 8.4
for cx, color, txt in [
    (2.0, C_PROJ,  "iGEM\nRegistry API"),
    (6.5, C_PAPER, "OpenAlex\n(keyword + citation)"),
    (11.0, C_PAT,  "Oldham et al. (2020)\nUSPTO full-texts")
]:
    box(ax, cx, y_src, 2.6, 0.75, color, txt, fontsize=9.5, bold=True, alpha_fill=0.08)

# ---- ROW 2: raw counts -----------------------------------------------------
y_raw = 7.2
box(ax, 2.0,  y_raw, 2.6, 0.72, C_PROJ,
    "4,606 projects\n634 teams · 2004–2023")
box(ax, 6.5,  y_raw, 2.8, 0.72, C_PAPER,
    "10,319 papers\nkeyword + citation exp.")
box(ax, 11.0, y_raw, 2.6, 0.72, C_PAT,
    "2,901 patents\nsynth. bio. subfield")

for cx in [2.0, 6.5, 11.0]:
    arrow(ax, cx, y_src - 0.38, cx, y_raw + 0.36)

# ---- ROW 3: geocoding ------------------------------------------------------
y_geo = 5.95
box(ax, 2.0,  y_geo, 2.6, 0.72, C_PROJ,
    "4,574 geocoded\n32 dropped  (0.7%)")
box(ax, 6.5,  y_geo, 2.8, 0.72, C_PAPER,
    "10,319 geocoded\nmulti-tier resolution")
box(ax, 11.0, y_geo, 2.6, 0.72, C_PAT,
    "2,866 geocoded\n35 dropped  (1.2%)")

for cx in [2.0, 6.5, 11.0]:
    arrow(ax, cx, y_raw - 0.36, cx, y_geo + 0.36)

label(ax, 12.7, y_geo, "city / country\nlat / lon", fontsize=7.5)

# ---- ROW 4: fine-tuning signal box (spanning all three) --------------------
y_ft = 4.8
box(ax, 6.5, y_ft, 10.5, 0.72, C_SHARED,
    "Fine-tuning signal: 21,959 project→paper wiki-DOI links"
    "  +  Marx et al. patent→paper pairs",
    fontsize=9.5, alpha_fill=0.06)

# arrows: outer two sources converge to the wide box
arrow(ax, 2.0,  y_geo - 0.36, 2.0,  y_ft + 0.15)
ax.annotate("", xy=(1.3, y_ft + 0.36), xytext=(2.0, y_ft + 0.15),
            arrowprops=dict(arrowstyle="-", color=C_SHARED, lw=1.3), zorder=5)
ax.annotate("", xy=(1.3, y_ft), xytext=(1.3, y_ft + 0.36),
            arrowprops=dict(arrowstyle="-|>", color=C_SHARED, lw=1.3,
                            mutation_scale=12), zorder=5)

arrow(ax, 6.5,  y_geo - 0.36, 6.5,  y_ft + 0.36)

arrow(ax, 11.0, y_geo - 0.36, 11.0, y_ft + 0.15)
ax.annotate("", xy=(11.7, y_ft + 0.36), xytext=(11.0, y_ft + 0.15),
            arrowprops=dict(arrowstyle="-", color=C_SHARED, lw=1.3), zorder=5)
ax.annotate("", xy=(11.7, y_ft), xytext=(11.7, y_ft + 0.36),
            arrowprops=dict(arrowstyle="-|>", color=C_SHARED, lw=1.3,
                            mutation_scale=12), zorder=5)

# ---- ROW 5: SPECTER2 fine-tuning ------------------------------------------
y_spect = 3.75
box(ax, 6.5, y_spect, 7.0, 0.72, C_SHARED,
    "SPECTER2 fine-tuning  (triplet loss on cross-type pairs)", fontsize=9.5,
    alpha_fill=0.06)
arrow(ax, 6.5, y_ft - 0.36, 6.5, y_spect + 0.36)

# ---- ROW 6: shared embedding -----------------------------------------------
y_emb = 2.7
box(ax, 6.5, y_emb, 9.0, 0.72, C_SHARED,
    "17,826 artifacts  embedded in shared 768-dim semantic space",
    fontsize=10, bold=True, alpha_fill=0.08)
arrow(ax, 6.5, y_spect - 0.36, 6.5, y_emb + 0.36)

# ---- ROW 7: UMAP + HDBSCAN -------------------------------------------------
y_clust = 1.75
box(ax, 6.5, y_clust, 7.0, 0.65, C_SHARED,
    "UMAP (2-dim projection)  →  HDBSCAN clustering", fontsize=9.5,
    alpha_fill=0.06)
arrow(ax, 6.5, y_emb - 0.36, 6.5, y_clust + 0.32)

# ---- ROW 8: output ---------------------------------------------------------
y_out1 = 1.05
y_out2 = 0.35
box(ax, 4.0, y_out1, 4.0, 0.55, C_SHARED,
    "84 topic clusters  (human-reviewed labels)", fontsize=9,
    alpha_fill=0.06)
box(ax, 9.5, y_out1, 5.5, 0.55, C_SHARED,
    "387 cities  with ≥2 co-present artifact types", fontsize=9,
    alpha_fill=0.06)

ax.annotate("", xy=(4.0, y_out1 + 0.28), xytext=(5.5, y_clust - 0.32),
            arrowprops=dict(arrowstyle="-|>", color=C_SHARED, lw=1.3,
                            mutation_scale=12), zorder=5)
ax.annotate("", xy=(9.5, y_out1 + 0.28), xytext=(7.5, y_clust - 0.32),
            arrowprops=dict(arrowstyle="-|>", color=C_SHARED, lw=1.3,
                            mutation_scale=12), zorder=5)

fig.tight_layout(pad=0.4)
fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved {OUT}")
