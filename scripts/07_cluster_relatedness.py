"""
Step 7 — City-level cluster co-membership ("local relatedness") analysis.

WHY THIS SCRIPT EXISTS
----------------------
The headline city-level measure in notebook 01 is the cosine between a city's
paper-embedding centroid and its project-embedding centroid (`semantic_overlap`).
That measure is dominated by a field-level baseline: every synthetic-biology
document is similar to every other, so the cosine sits near 0.95-0.98 for almost
every city, and a within-country permutation test showed the cross-sectional
result is a centroid-stability artifact (see notebook 01, Section 7).

This script tests a sharper alternative the student proposed: instead of comparing
average vectors, compare *which specific topic clusters* a city's papers and
projects fall into. Each document already has an HDBSCAN `cluster_label`
(from scripts/05_cluster.py, stored in data/processed/all_artifacts.csv).

    For a city:
      p = paper cluster-frequency vector   (share of its papers in each cluster)
      q = project cluster-frequency vector (share of its projects in each cluster)
      cluster_overlap = cosine(p, q)

cluster_overlap is high only when a city's papers and projects concentrate in the
SAME specific topics -- which is the "local relatedness" we set out to measure.

WHAT WE REPORT
--------------
1. Distribution of cluster_overlap vs. the old centroid measure.
2. Robustness to the minimum-documents-per-type threshold (sparsity check).
3. OLS: cluster_overlap ~ log_n_papers + log_n_projects (+ country FE),
   HC3 heteroskedasticity-robust SEs (mirrors notebook 01 Section 5.7).
4. The DECISIVE test: a re-pairing permutation test. We break the link between a
   city's own papers and its own projects (shuffling which project-vector pairs
   with which paper-vector, within country) and ask whether the observed mean
   overlap is higher than this null. This is the cluster-space analogue of the
   permutation test that killed the centroid result, and it is what distinguishes
   genuine local relatedness from a new baseline artifact.

References for the methods used here:
  - HDBSCAN clustering: Campello, Moulavi & Sander (2013).
  - Permutation / randomization inference: Good (2005), "Permutation, Parametric,
    and Bootstrap Tests of Hypotheses".
  - HC3 robust SEs: MacKinnon & White (1985).

Usage:  .venv/bin/python scripts/07_cluster_relatedness.py
"""

from pathlib import Path
import numpy as np
import pandas as pd
from numpy.linalg import norm
from scipy import stats

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data" / "processed" / "all_artifacts.csv"
CITY = REPO / "data" / "processed" / "city_level.csv"

RNG = np.random.default_rng(42)   # fixed seed -> reproducible permutation results
N_PERM = 2000


def freq_vec(sub, K):
    """Cluster-frequency vector for a set of documents (sums to 1; None if empty)."""
    v = np.zeros(K)
    for c, n in sub["cluster_label"].value_counts().items():
        v[int(c)] = n
    s = v.sum()
    return v / s if s > 0 else None


def build_city_vectors(valid, K, min_docs):
    """Return dict city_key -> (paper_vec, project_vec, n_papers, n_projects)
    for cities with >= min_docs non-noise documents of BOTH types."""
    out = {}
    for ck, g in valid.groupby("city_key"):
        pg = g[g["type"] == "paper"]
        qg = g[g["type"] == "project"]
        if len(pg) >= min_docs and len(qg) >= min_docs:
            out[ck] = (freq_vec(pg, K), freq_vec(qg, K), len(pg), len(qg))
    return out


def cosine(a, b):
    return float(a @ b / (norm(a) * norm(b)))


def main():
    df = pd.read_csv(ART, low_memory=False)
    cl = pd.read_csv(CITY)
    df["city_key"] = df["city"].astype(str).str.strip().str.lower()

    valid = df[df["cluster_label"] >= 0].copy()          # drop noise (-1)
    K = int(valid["cluster_label"].max()) + 1
    n_noise = (df["cluster_label"] < 0).sum()
    print(f"Documents: {len(df):,}  | non-noise: {len(valid):,}  "
          f"| noise: {n_noise:,} ({n_noise/len(df):.0%})  | clusters K={K}")

    # ---- 2. Sparsity / threshold robustness -------------------------------------
    print("\n=== Robustness to minimum docs-per-type threshold ===")
    print(f"{'min':>4} {'cities':>7} {'mean_overlap':>13} {'median':>8} "
          f"{'%==0':>6} {'mean_delta':>11} {'%delta>0':>9} {'wilcoxon_p':>11}")
    for min_docs in (3, 5, 8, 12, 20):
        cv = build_city_vectors(valid, K, min_docs)
        if len(cv) < 5:
            print(f"{min_docs:>4} {len(cv):>7}   (too few cities)")
            continue
        cks = list(cv.keys())
        ov = np.array([cosine(cv[c][0], cv[c][1]) for c in cks])
        Q = np.vstack([cv[c][1] for c in cks]); Qn = Q / norm(Q, axis=1, keepdims=True)
        deltas = []
        for i, c in enumerate(cks):
            pn = cv[c][0] / norm(cv[c][0])
            sims = Qn @ pn
            sim_own = sims[i]
            sim_other = (sims.sum() - sim_own) / (len(cks) - 1)
            deltas.append(sim_own - sim_other)
        deltas = np.array(deltas)
        w_p = stats.wilcoxon(deltas).pvalue if np.any(deltas != 0) else float("nan")
        print(f"{min_docs:>4} {len(cks):>7} {ov.mean():>13.4f} {np.median(ov):>8.4f} "
              f"{(ov == 0).mean():>6.0%} {deltas.mean():>11.4f} "
              f"{(deltas > 0).mean():>9.0%} {w_p:>11.3g}")

    # ---- Primary analysis at MIN=8 (dense enough to be meaningful) --------------
    MIN = 8
    cv = build_city_vectors(valid, K, MIN)
    cks = list(cv.keys())
    co_df = pd.DataFrame({
        "city_key": cks,
        "n_cl_papers": [cv[c][2] for c in cks],
        "n_cl_projects": [cv[c][3] for c in cks],
        "cluster_overlap": [cosine(cv[c][0], cv[c][1]) for c in cks],
    }).merge(cl[["city_key", "country", "semantic_overlap"]], on="city_key", how="left")
    co_df["log_n_papers"] = np.log1p(co_df["n_cl_papers"])
    co_df["log_n_projects"] = np.log1p(co_df["n_cl_projects"])
    print(f"\n=== PRIMARY ANALYSIS (min {MIN} docs/type): {len(co_df)} cities ===")
    print("cluster_overlap  :", co_df["cluster_overlap"].describe()[["mean","50%","std","max"]].round(4).to_dict())
    print("centroid overlap :", co_df["semantic_overlap"].describe()[["mean","50%","std","max"]].round(4).to_dict())

    # ---- 3. OLS (mirrors notebook 01 Section 5.7) -------------------------------
    import statsmodels.formula.api as smf
    print("\n--- OLS: cluster_overlap ~ log_n_papers + log_n_projects (HC3) ---")
    m1 = smf.ols("cluster_overlap ~ log_n_papers + log_n_projects", data=co_df).fit(cov_type="HC3")
    print(m1.summary().tables[1])
    print(f"R^2 = {m1.rsquared:.4f}")

    # country fixed effects (only countries with >=2 cities, like the notebook)
    vc = co_df["country"].value_counts()
    co_fe = co_df[co_df["country"].isin(vc[vc >= 2].index)].copy()
    m2 = smf.ols("cluster_overlap ~ log_n_papers + log_n_projects + C(country)",
                 data=co_fe).fit(cov_type="HC3")
    print(f"\n+ country FE ({co_fe['country'].nunique()} countries, {len(co_fe)} cities): "
          f"R^2 = {m2.rsquared:.4f}")
    print("  log_n_papers   beta = %.4f  p = %.3g" % (m2.params['log_n_papers'], m2.pvalues['log_n_papers']))
    print("  log_n_projects beta = %.4f  p = %.3g" % (m2.params['log_n_projects'], m2.pvalues['log_n_projects']))

    # ---- 4. DECISIVE re-pairing permutation test --------------------------------
    # Observed: mean cosine(own paper-vec, own project-vec).
    # Null: shuffle which project-vec is paired with which paper-vec, WITHIN country
    #       (countries with >=2 cities). Preserves each country's mix of vectors but
    #       destroys the city-level pairing. If observed >> null, a city's own papers
    #       and own projects are genuinely related beyond same-country chance.
    P = {c: cv[c][0] for c in cks}
    Qd = {c: cv[c][1] for c in cks}
    country = dict(zip(co_df["city_key"], co_df["country"]))

    obs = np.mean([cosine(P[c], Qd[c]) for c in cks])

    # group cities by country for within-country shuffling
    from collections import defaultdict
    groups = defaultdict(list)
    for c in cks:
        groups[country.get(c, "NA")].append(c)

    null = np.empty(N_PERM)
    for t in range(N_PERM):
        sims = []
        for g_cities in groups.values():
            if len(g_cities) == 1:
                c = g_cities[0]
                sims.append(cosine(P[c], Qd[c]))     # can't shuffle a singleton
            else:
                perm = RNG.permutation(g_cities)
                for c, c_perm in zip(g_cities, perm):
                    sims.append(cosine(P[c], Qd[c_perm]))
        null[t] = np.mean(sims)
    p_perm = (np.sum(null >= obs) + 1) / (N_PERM + 1)
    print("\n--- DECISIVE within-country re-pairing permutation test ---")
    print(f"observed mean cluster_overlap = {obs:.4f}")
    print(f"null mean  = {null.mean():.4f}   null 95th pct = {np.quantile(null, .95):.4f}")
    print(f"permutation p-value           = {p_perm:.4f}")
    excess = obs - null.mean()
    print(f"excess over null mean         = {excess:+.4f}")
    verdict = ("GENUINE local signal: own pairing beats the null."
               if p_perm < 0.05 else
               "NOT distinguishable from the same-country null (artifact-like).")
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
