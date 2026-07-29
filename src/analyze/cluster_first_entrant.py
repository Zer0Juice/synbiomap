"""
cluster_first_entrant.py — within a city's topic cluster, which artifact type shows up first?

For every (city, cluster) cell we take the earliest year of each type present, then ask
who leads. Two views:

  A) Unconditional first entrant  — of all city-cluster cells, which type is earliest.
     Careful: this rewards whichever type is simply *present*, and papers are ~10x more
     numerous than patents, so it mostly reflects prevalence, not timing.

  B) Pairwise, conditional on co-occurrence — the fair test. Among city-clusters where
     BOTH type a and type b appear, how often does a predate b? This controls for how
     common each type is and directly measures lead/lag.

Year caveat: paper = publication year, project = iGEM competition year, patent = the year
in the Oldham set (application/grant), which lags the underlying invention. Read patents
as a late signal accordingly.

Data: data/processed/artifacts_tripartite_clustered.csv  (cluster_label = -1 is noise)
Run : python src/analyze/cluster_first_entrant.py
"""

import csv
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "artifacts_tripartite_clustered.csv"
TYPES = ["project", "paper", "patent"]


def main(year_min=None, year_max=None):
    # earliest[(city_key, cluster)][type] = min year seen for that type in that cell.
    # A year window (e.g. 2009-2018, where all three corpora coexist) removes the
    # coverage confound: patents in the Oldham set reach back before iGEM existed,
    # and projects only start in 2009, so the raw calendar unfairly makes patents
    # look early. Restricting to the overlap compares like with like.
    earliest = defaultdict(dict)
    with open(SRC, newline="") as f:
        reader = csv.DictReader(f)
        has_country = "country" in reader.fieldnames
        for r in reader:
            typ = r.get("type")
            if typ not in TYPES:
                continue
            try:
                cluster = int(float(r["cluster_label"]))
                year = int(float(r["year"]))
            except (KeyError, ValueError):
                continue
            if year_min is not None and year < year_min:
                continue
            if year_max is not None and year > year_max:
                continue
            city = (r.get("city") or "").strip()
            if not city or cluster < 0:  # need a city; skip HDBSCAN noise
                continue
            country = (r.get("country") or "").strip() if has_country else ""
            cell = earliest[((city, country), cluster)]
            if typ not in cell or year < cell[typ]:
                cell[typ] = year

    cells = list(earliest.values())
    window = "all years" if year_min is None and year_max is None else f"{year_min}-{year_max}"
    print(f"year window                   : {window}")
    print(f"city-cluster cells (non-noise): {len(cells):,}")
    print(f"cells containing each type    : " +
          ", ".join(f"{t} {sum(t in c for c in cells):,}" for t in TYPES))

    # ---- A) Unconditional first entrant --------------------------------------
    print("\nA) Unconditional — who is earliest in the cell (ties shared):")
    first = defaultdict(float)
    for c in cells:
        ymin = min(c.values())
        leaders = [t for t in c if c[t] == ymin]
        for t in leaders:
            first[t] += 1 / len(leaders)   # split ties evenly
    tot = sum(first.values())
    for t in TYPES:
        print(f"   {t:8s} first in {first[t]:8.1f} cells  ({first[t]/tot*100:4.1f}%)")

    # ---- B) Pairwise, conditional on co-occurrence ---------------------------
    print("\nB) Pairwise — among cells where BOTH appear, who comes first:")
    for a, b in combinations(TYPES, 2):
        both = [c for c in cells if a in c and b in c]
        a_first = sum(c[a] < c[b] for c in both)
        b_first = sum(c[b] < c[a] for c in both)
        ties = len(both) - a_first - b_first
        n = len(both) or 1
        print(f"   {a} vs {b}: {len(both):,} shared cells | "
              f"{a} first {a_first/n*100:4.1f}%  ·  "
              f"{b} first {b_first/n*100:4.1f}%  ·  tie {ties/n*100:4.1f}%")

    # ---- Median first-entry year per type (context) --------------------------
    def median(xs):
        xs = sorted(xs)
        n = len(xs)
        return (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2) if n else None
    print("\nMedian first-entry year across the cells each type appears in:")
    for t in TYPES:
        yrs = [c[t] for c in cells if t in c]
        print(f"   {t:8s} median {median(yrs)}  (n={len(yrs):,})")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Which artifact type enters a city's clusters first?")
    ap.add_argument("--min-year", type=int, default=None, help="earliest year to include")
    ap.add_argument("--max-year", type=int, default=None, help="latest year to include")
    args = ap.parse_args()
    main(args.min_year, args.max_year)
