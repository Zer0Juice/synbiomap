"""
make_centroid_widget_data.py — export per-city data for the centroid-relatedness widget.

The "Average Relatedness" slide shows the *centroid* measure: average a city's
project embeddings into one vector and its papers into another, then take the
cosine between them (stored as `semantic_overlap` in city_level.csv). This measure
is a known size artifact — averaging many vectors pulls both centroids toward the
field-wide mean, so cities that publish a lot score high automatically. See the
docstring of relatedness.py (co-membership is used instead precisely to avoid this).

This script trims city_level.csv down to just what the interactive widget needs and
writes it as a small JSON to the website assets. No embeddings are recomputed; the
centroid cosine already lives in the CSV. Re-run whenever city_level.csv changes:

    python src/analyze/make_centroid_widget_data.py

Reads : data/processed/city_level.csv
Writes: website/assets/data/centroid_relatedness.json
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "city_level.csv"
OUT = ROOT / "website" / "assets" / "data" / "centroid_relatedness.json"


def pearson(xs, ys):
    """Plain Pearson correlation, used only to log the size artifact for a sanity check."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sxy / (sx * sy) if sx and sy else float("nan")


def main():
    rows = []
    with open(SRC, newline="") as f:
        for r in csv.DictReader(f):
            try:
                overlap = float(r["semantic_overlap"])
                papers = int(r["n_papers"])
                projects = int(r["n_projects"])
            except (KeyError, ValueError):
                continue
            if papers <= 0 or projects <= 0:
                continue  # need both types for a project-vs-paper centroid
            rows.append(
                {
                    "city": r["city"].strip(),
                    "country": (r.get("country") or "").strip(),
                    "papers": papers,
                    "projects": projects,
                    "overlap": round(overlap, 4),
                }
            )

    # Sanity check the size confound the widget is meant to expose.
    ov = [x["overlap"] for x in rows]
    log_papers = [math.log1p(x["papers"]) for x in rows]
    r = pearson(ov, log_papers)
    print(f"{len(rows)} cities · overlap {min(ov):.3f}–{max(ov):.3f} · "
          f"r(overlap, log papers) = {r:.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(rows, f, separators=(",", ":"))
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
