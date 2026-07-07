"""
scripts/14_fig_pipeline_concept.py
Conceptual diagram of the three-artifact innovation ladder with temporal offsets
and mechanism labels. Saved as a high-resolution PNG for inclusion in the manuscript.
Output: outputs/figures/pipeline_concept.png
"""

import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

OUT = "outputs/figures/pipeline_concept.png"

# ---- colour scheme ----------------------------------------------------------
C_PROJ   = "#2ca02c"   # green
C_PAPER  = "#1f77b4"   # blue
C_PATENT = "#d62728"   # red
C_ARROW  = "#555555"
C_MECH   = "#444444"
C_TIME   = "#888888"

# ---- figure setup -----------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 4.5))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.5)
ax.axis("off")

# ---- helper: draw a rounded box with label ----------------------------------
BOX_W, BOX_H = 2.4, 1.0
BOX_Y = 2.6   # vertical centre of boxes

def draw_box(cx, color, line1, line2, sublabel):
    box = FancyBboxPatch(
        (cx - BOX_W/2, BOX_Y - BOX_H/2),
        BOX_W, BOX_H,
        boxstyle="round,pad=0.08",
        linewidth=1.8,
        edgecolor=color,
        facecolor=color + "22",   # 13% opacity fill
        zorder=3
    )
    ax.add_patch(box)
    ax.text(cx, BOX_Y + 0.22, line1, ha="center", va="center",
            fontsize=11, fontweight="bold", color=color, zorder=4)
    ax.text(cx, BOX_Y - 0.22, line2, ha="center", va="center",
            fontsize=9.5, color=color, zorder=4)
    ax.text(cx, BOX_Y - BOX_H/2 - 0.32, sublabel,
            ha="center", va="top", fontsize=8, color="#666666",
            style="italic", zorder=4)

# box x positions
X_PROJ, X_PAPER, X_PAT = 2.2, 6.0, 9.8

draw_box(X_PROJ,  C_PROJ,  "iGEM project",  "student wiki", "open-source designs\nBioBrick parts")
draw_box(X_PAPER, C_PAPER, "Academic paper","title + abstract", "peer-reviewed\nmethodology")
draw_box(X_PAT,   C_PATENT,"Patent",        "claim + abstract", "commercial\napplication")

# ---- arrows with mechanism labels ------------------------------------------
def draw_arrow_with_label(x0, x1, y, color, mech_label):
    ax.annotate(
        "", xy=(x1 - BOX_W/2 - 0.08, y), xytext=(x0 + BOX_W/2 + 0.08, y),
        arrowprops=dict(
            arrowstyle="-|>", color=color,
            lw=2.0, mutation_scale=16,
            connectionstyle="arc3,rad=0.0"
        ),
        zorder=5
    )
    xm = (x0 + x1) / 2
    ax.text(xm, y + 0.28, mech_label,
            ha="center", va="bottom", fontsize=9, color=C_MECH,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.85))

draw_arrow_with_label(X_PROJ, X_PAPER, BOX_Y, "#2ca02c",
                      "direct knowledge transfer")
draw_arrow_with_label(X_PAPER, X_PAT,  BOX_Y, "#1f77b4",
                      "applied translation")

# ---- timeline bar at bottom ------------------------------------------------
TL_Y = 0.75
TL_X0 = X_PROJ - 0.5
TL_X1 = X_PAT  + 0.5
ax.plot([TL_X0, TL_X1], [TL_Y, TL_Y], color=C_TIME, lw=1.8, zorder=2)
ax.text((TL_X0 + TL_X1)/2, TL_Y - 0.38,
        "time", ha="center", va="top", fontsize=9, color=C_TIME, style="italic")

for xpos, label in [(X_PROJ, "Year $t$"), (X_PAPER, "Year $t+3$"), (X_PAT, "Year $t+6$")]:
    ax.plot([xpos, xpos], [TL_Y - 0.1, TL_Y + 0.1], color=C_TIME, lw=1.4)
    ax.text(xpos, TL_Y - 0.18, label,
            ha="center", va="top", fontsize=8.5, color=C_TIME)
    # dashed vertical connecting box to timeline
    ax.plot([xpos, xpos], [BOX_Y - BOX_H/2 - 0.62, TL_Y + 0.1],
            color=C_TIME, lw=0.8, linestyle="--", zorder=1, alpha=0.5)

# ---- shared-environment brace at bottom ------------------------------------
# simple bracket
BRACE_Y = 0.22
ax.annotate(
    "", xy=(TL_X1 - 0.05, BRACE_Y), xytext=(TL_X0 + 0.05, BRACE_Y),
    arrowprops=dict(arrowstyle="<->", color="#aaaaaa", lw=1.4)
)
ax.text((TL_X0 + TL_X1)/2, BRACE_Y - 0.14,
        "shared institutional environment (city)",
        ha="center", va="top", fontsize=8.5, color="#888888", style="italic")

fig.tight_layout(pad=0.5)
fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved {OUT}")
