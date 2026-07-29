"""
cluster_entry_test.py — do projects enter topic clusters their own city already publishes in?

Reproduces the project-level "in_known" test (frank_talk slide 13) on the CURRENT
tripartite, 80-cluster data (papers + projects + patents, Oldham patent set), so the
number is consistent with the rest of the deck rather than the older two-type run.

Test (temporal direction: paper BEFORE project)
------------------------------------------------
For each non-noise project in cluster k, city c, year y:
    own_known = 1 if city c has a PAPER in cluster k with year < y, else 0
    baseline  = (# paper-cities with a paper in cluster k before year y) / (# paper-cities)
                i.e. the chance a *randomly chosen* city would already know cluster k
    delta     = own_known - baseline

We report the own-city entry rate, the mean random-city baseline, their ratio (the
"~5x" headline), and a one-sample t-test of H0: mean(delta) = 0. A city key is
(city, country) so e.g. Cambridge US and Cambridge UK are not merged.

Data: data/processed/artifacts_tripartite_clustered.csv  (cluster_label = -1 is noise)
Run : python src/analyze/cluster_entry_test.py
"""

import csv
import math
from bisect import bisect_left
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "artifacts_tripartite_clustered.csv"


def load_docs():
    """Yield (type, city_key, year, cluster) for rows with a cluster, city, and year."""
    with open(SRC, newline="") as f:
        reader = csv.DictReader(f)
        has_country = "country" in reader.fieldnames
        for r in reader:
            try:
                cluster = int(float(r["cluster_label"]))
                year = int(float(r["year"]))
            except (KeyError, ValueError):
                continue
            city = (r.get("city") or "").strip()
            if not city:
                continue
            country = (r.get("country") or "").strip() if has_country else ""
            yield r["type"], (city, country), year, cluster


def main():
    papers, projects = [], []
    for typ, ckey, year, cluster in load_docs():
        if cluster < 0:  # HDBSCAN noise
            continue
        if typ == "paper":
            papers.append((ckey, year, cluster))
        elif typ == "project":
            projects.append((ckey, year, cluster))

    # Per cluster: earliest paper year for each city that ever published in it.
    # first_year[cluster][city] = min paper year  ->  used for the own-city test.
    first_year = defaultdict(dict)
    paper_cities = set()
    for ckey, year, cluster in papers:
        paper_cities.add(ckey)
        d = first_year[cluster]
        if ckey not in d or year < d[ckey]:
            d[ckey] = year
    n_paper_cities = len(paper_cities)

    # Per cluster: sorted list of those earliest years, so "how many cities already
    # knew cluster k before year y" is a binary search (bisect), not a rescan.
    sorted_first_years = {k: sorted(v.values()) for k, v in first_year.items()}

    deltas, own_flags, base_vals = [], [], []
    for ckey, y, k in projects:
        fy = first_year.get(k)
        own = 1.0 if (fy and ckey in fy and fy[ckey] < y) else 0.0
        years_k = sorted_first_years.get(k, [])
        n_known = bisect_left(years_k, y)          # cities whose first paper-year < y
        baseline = n_known / n_paper_cities if n_paper_cities else 0.0
        own_flags.append(own)
        base_vals.append(baseline)
        deltas.append(own - baseline)

    n = len(deltas)
    own_rate = sum(own_flags) / n
    base_rate = sum(base_vals) / n
    mean_delta = sum(deltas) / n
    sd = math.sqrt(sum((d - mean_delta) ** 2 for d in deltas) / (n - 1))
    se = sd / math.sqrt(n)
    t = mean_delta / se
    ratio = own_rate / base_rate if base_rate else float("inf")

    # Two-sided p; use scipy if present, else a large-n normal approximation.
    try:
        from scipy import stats
        p = float(stats.t.sf(abs(t), df=n - 1) * 2)
        p_src = "scipy t"
    except Exception:
        p = math.erfc(abs(t) / math.sqrt(2))       # normal approx, fine for large n
        p_src = "normal approx"

    print(f"source            : {SRC.relative_to(ROOT)}")
    print(f"non-noise papers  : {len(papers):,}  (paper-cities = {n_paper_cities:,})")
    print(f"projects tested   : {n:,}")
    print("-" * 46)
    print(f"own-city entry rate : {own_rate*100:.2f}%")
    print(f"baseline (random)   : {base_rate*100:.2f}%")
    print(f"mean delta          : {mean_delta:+.4f}")
    print(f"ratio (own/base)    : {ratio:.2f}x")
    print(f"t ({n-1} df)          : {t:.2f}")
    print(f"p-value             : {p:.2e}  ({p_src})")


if __name__ == "__main__":
    main()
