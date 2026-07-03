#!/usr/bin/env python3
"""
export_paper_assets.py
======================

Regenerate the figures, tables, and key numbers that the LaTeX manuscript needs,
in a clean *white* style suited to a printed document (the notebook itself uses a
Solarized theme that matches the slides; that looks washed out on white paper).

Why a separate script instead of the notebook?
-----------------------------------------------
Hand-copying a number like "0.946" or "387 cities" from a notebook into the
manuscript is fragile: re-run the analysis and the prose silently goes stale.
This script records every figure, table, and quoted number once, and writes them
to ``manuscript/generated/`` so the manuscript can pull them in directly:

    \\graphicspath{{generated/figures/}}      % then \\includegraphics{overlap_distribution}
    \\input{generated/stats.tex}              % defines \\statOverlapMean, etc.
    \\input{generated/tables/summary_stats.tex}

It reuses the analysis that already lives in ``notebooks/01_city_level_analysis.ipynb``
but reads only *saved* artifacts, so it runs in a couple of minutes without the
embedding model:
  - ``data/processed/city_level.csv``  (already has the semantic-overlap measure)
  - ``data/processed/projects.csv`` / ``papers.csv``  (counts, years, cities)
  - ``data/processed/parts.csv``       (BioBrick part-type composition)
  - ``data/embeddings/embeddings_batches/``  (cached SPECTER2 vectors, via _load_cache)

Cluster co-membership (notebook "Section 8")
--------------------------------------------
``stage_cluster`` exports the cluster co-membership measure, its within-country
re-pairing permutation test, and the cross-modal Mantel test. It reads the
document-level HDBSCAN labels persisted in ``data/processed/all_artifacts.csv``
(written by ``scripts/05_cluster.py``), so it also needs no embedding model.

Usage
-----
    python scripts/export_paper_assets.py                # everything
    python scripts/export_paper_assets.py --no-embeddings  # skip alignment/DiD/lead-lag

Methods references (kept next to the code that uses them):
  - Hidalgo et al. (2007), Neffke & Henning (2013) — relatedness via co-occurrence,
    here applied to text centroids.
  - Turney & Pantel (2010) — centroid-based semantic similarity.
  - Angrist & Pischke (2009), Ch. 5 — difference-in-differences.
  - Granger (1969) — lead-lag / temporal precedence (described, not claimed causal).
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display needed; we only save files
import matplotlib.pyplot as plt
from matplotlib import cycler
import scipy.stats as stats

warnings.filterwarnings("ignore", category=FutureWarning)

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent
DATA     = ROOT / "data" / "processed"
EMB_FILE = ROOT / "data" / "embeddings" / "embeddings.json"  # _load_cache reads the *_batches/ dir next to it
GEN_DIR  = ROOT / "manuscript" / "generated"
FIG_DIR  = GEN_DIR / "figures"
TAB_DIR  = GEN_DIR / "tables"
sys.path.insert(0, str(ROOT / "src"))

# ──────────────────────────────────────────────────────────────────────────────
# White publication style — reuse the project's accent colours on a white ground
# ──────────────────────────────────────────────────────────────────────────────
BLUE, CYAN, ORANGE = "#268bd2", "#2aa198", "#cb4b16"   # papers / projects / highlight
YELLOW, RED, MUTED = "#b58900", "#dc322f", "#93a1a1"
FILL = "#cfe2f0"  # light blue histogram fill

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "axes.edgecolor": "#333333", "axes.labelcolor": "#1a1a1a", "text.color": "#1a1a1a",
    "xtick.color": "#333333", "ytick.color": "#333333",
    "axes.grid": False, "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 11, "axes.titlesize": 12, "figure.dpi": 120,
    "axes.prop_cycle": cycler(color=[BLUE, CYAN, ORANGE, YELLOW, RED]),
    "pdf.fonttype": 42, "ps.fonttype": 42,  # keep text selectable/editable in the PDF
})

# ──────────────────────────────────────────────────────────────────────────────
# Tiny export helpers: one place that writes figures, tables, and the stats macros
# ──────────────────────────────────────────────────────────────────────────────
STATS: dict[str, dict] = {}


def save_fig(name: str, fig=None, dpi: int = 300) -> None:
    """Save the current (or given) figure as PDF + PNG into manuscript/generated/figures."""
    fig = fig or plt.gcf()
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"{name}.{ext}", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"  figure  → figures/{name}.pdf (+ .png)")


def _macro(key: str) -> str:
    """snake_case key → LaTeX-safe macro name, e.g. 'overlap_mean' → 'statOverlapMean'.
    (LaTeX command names cannot contain digits or underscores, so keys must be letters only.)"""
    parts = [p for p in key.replace("-", "_").split("_") if p]
    return "stat" + "".join(p.capitalize() for p in parts)


def record(key: str, value, fmt: str | None = None, note: str = "") -> None:
    """Record a single number the manuscript will quote. `fmt` is a Python format spec
    like '.3f' or '+.4f' or ',d'; leave it None for strings/integers shown as-is."""
    formatted = format(value, fmt) if fmt else str(value)
    STATS[key] = {"macro": _macro(key), "value": value, "formatted": formatted, "note": note}
    print(f"  stat    → \\{_macro(key)} = {formatted}")


def save_table(df: pd.DataFrame, name: str, caption: str = "", label: str = "",
               index: bool = False, float_format: str = "%.3f") -> None:
    """Write a dataframe as CSV (for inspection) + a booktabs LaTeX table (for \\input)."""
    df.to_csv(TAB_DIR / f"{name}.csv", index=index)
    try:
        body = df.to_latex(index=index, escape=True, booktabs=True,
                           float_format=lambda x: float_format % x)
    except TypeError:  # very old/new pandas without the booktabs kwarg
        body = df.to_latex(index=index, escape=True,
                           float_format=lambda x: float_format % x)
    lines = ["% Auto-generated by scripts/export_paper_assets.py — do not edit by hand."]
    if caption or label:
        lines += ["\\begin{table}[htbp]", "\\centering"]
        if caption:
            lines.append(f"\\caption{{{caption}}}")
        if label:
            lines.append(f"\\label{{{label}}}")
    lines.append(body)
    if caption or label:
        lines.append("\\end{table}")
    (TAB_DIR / f"{name}.tex").write_text("\n".join(lines))
    print(f"  table   → tables/{name}.tex (+ .csv)")


def write_stats() -> None:
    """Emit stats.tex (LaTeX macros) and stats.json (human-readable record)."""
    header = [
        "% Auto-generated by scripts/export_paper_assets.py — do not edit by hand.",
        "% Each macro is a number quoted in the manuscript; re-run the script to refresh.",
        "% Usage in main.tex:  \\input{generated/stats.tex}   then e.g.  \\statOverlapMean",
        "",
    ]
    body = [f"\\newcommand{{\\{v['macro']}}}{{{v['formatted']}}}" for v in STATS.values()]
    (GEN_DIR / "stats.tex").write_text("\n".join(header + body) + "\n")
    (GEN_DIR / "stats.json").write_text(json.dumps(STATS, indent=2, default=str))
    print(f"\nWrote {len(STATS)} stats → generated/stats.tex (+ stats.json)")


# ──────────────────────────────────────────────────────────────────────────────
# Embedding helpers (only needed for the alignment / DiD / lead-lag stages)
# ──────────────────────────────────────────────────────────────────────────────
def unit_centroid(vectors: np.ndarray) -> np.ndarray | None:
    """Mean of a set of embedding vectors, L2-normalised (None if it has zero length)."""
    c = vectors.mean(axis=0)
    n = np.linalg.norm(c)
    return c / n if n > 0 else None


def attach_embeddings(df: pd.DataFrame, cache: dict) -> pd.DataFrame:
    """Keep only rows whose id has a cached embedding; add an 'emb' column of np arrays."""
    df = df.copy()
    df["emb"] = df["id"].map(lambda i: cache.get(i))
    df = df.dropna(subset=["emb"]).reset_index(drop=True)
    df["emb"] = df["emb"].map(lambda v: np.asarray(v, dtype=np.float32))
    return df


def cluster_robust_mean(values, groups):
    """Mean of `values` with a *cluster-robust* standard error and t-stat.

    Why this matters: our project-level tests treat each iGEM project as an
    observation, but projects from the same city are compared against the *same*
    paper centroid, so their errors are correlated. A naive t-test then acts as
    if it has thousands of independent observations when it really has a few
    hundred cities. Clustering the standard error at the city level fixes this:
    it is the intercept-only case of the cluster-robust ("clustered") estimator
    of Cameron & Miller (2015), and the resulting t-stat reflects roughly the
    number of cities, not the number of projects.

    Returns (mean, se, t, n_obs, n_clusters).
    """
    v = np.asarray(values, dtype=float)
    g = np.asarray(groups)
    n = len(v)
    beta = v.mean()
    resid = v - beta
    # Meat of the sandwich: sum over clusters of (sum of residuals in cluster)^2.
    cluster_sums = pd.DataFrame({"r": resid, "g": g}).groupby("g")["r"].sum()
    G = len(cluster_sums)
    meat = float((cluster_sums ** 2).sum())
    # (X'X)^-1 = 1/n for X = a column of ones; small-sample correction G/(G-1).
    var = (G / (G - 1)) * meat / (n * n)
    se = float(np.sqrt(var))
    t = beta / se if se > 0 else np.nan
    return beta, se, t, n, G


# ──────────────────────────────────────────────────────────────────────────────
# Stage A — straight from city_level.csv (no embeddings needed)
# ──────────────────────────────────────────────────────────────────────────────
def stage_city_level() -> pd.DataFrame:
    print("\n[A] City-level overlap (from city_level.csv)")
    city = pd.read_csv(DATA / "city_level.csv")
    record("n_cities_analyzed", len(city), ",d", "cities with both papers and projects")

    # --- Distribution of semantic overlap (histogram + QQ plot) ---
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    med, mean = city.semantic_overlap.median(), city.semantic_overlap.mean()
    axes[0].hist(city.semantic_overlap, bins=30, color=FILL, edgecolor="white")
    axes[0].axvline(med, color=ORANGE, linestyle="--", label=f"Median = {med:.3f}")
    axes[0].axvline(mean, color=YELLOW, linestyle="--", label=f"Mean = {mean:.3f}")
    axes[0].set(xlabel="Semantic overlap (cosine similarity)", ylabel="Number of cities",
                title="Distribution of city-level semantic overlap")
    axes[0].legend()
    stats.probplot(city.semantic_overlap, plot=axes[1])
    axes[1].set_title("QQ plot: semantic overlap vs. normal")
    axes[1].get_lines()[0].set(marker="o", markersize=3, color=BLUE, alpha=0.6)
    axes[1].get_lines()[1].set(color=ORANGE)
    save_fig("overlap_distribution")
    record("overlap_mean", mean, ".3f")
    record("overlap_median", med, ".3f")
    record("overlap_skew", city.semantic_overlap.skew(), ".2f")
    record("overlap_kurt", city.semantic_overlap.kurt(), ".2f")

    # --- Is overlap driven by city size? (the diversity-vs-relatedness check) ---
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, col, key in [(axes[0], "n_papers", "papers"), (axes[1], "n_projects", "projects")]:
        x = np.log1p(city[col])
        ax.scatter(x, city.semantic_overlap, alpha=0.4, s=20, color=BLUE)
        z = np.polyfit(x, city.semantic_overlap, 1)
        xr = np.linspace(x.min(), x.max(), 100)
        ax.plot(xr, np.poly1d(z)(xr), color=ORANGE, linewidth=1.5)
        r, p = stats.pearsonr(x, city.semantic_overlap)
        ax.set(xlabel=f"log(1 + {key})", ylabel="Semantic overlap",
               title=f"Overlap vs. city size\nr = {r:.2f}, p = {p:.3f}")
        record(f"size_{key}_r", r, "+.2f")
        record(f"size_{key}_p", p, ".3f")
    save_fig("overlap_vs_size")

    # --- Summary-statistics table + top/bottom cities ---
    summary_cols = ["semantic_overlap", "n_papers", "n_projects",
                    "cs_paper_share", "cs_project_share", "proj_year_span"]
    save_table(city[summary_cols].describe().round(3).reset_index().rename(columns={"index": "statistic"}),
               "summary_stats", caption="Summary statistics for the city-level dataset.",
               label="tab:summary")

    disp = ["city", "country", "n_papers", "n_projects", "semantic_overlap"]
    ranked = city.sort_values("semantic_overlap", ascending=False)
    save_table(ranked[disp].head(15), "top15_cities",
               caption="Top 15 cities by semantic overlap.", label="tab:top15")
    save_table(ranked[disp].tail(15), "bottom15_cities",
               caption="Bottom 15 cities by semantic overlap.", label="tab:bottom15")
    return city


# ──────────────────────────────────────────────────────────────────────────────
# Stage A1 — centroid-overlap regression + within-country permutation (the artifact)
# ──────────────────────────────────────────────────────────────────────────────
def stage_overlap_regression(city: pd.DataFrame) -> None:
    """Nested OLS for centroid overlap: how much of it is just city size?

    Overlap is pinned near 1.0 by the synthetic-biology field baseline, and this
    regression shows the rest is mostly a size effect: log paper/project counts alone
    explain R^2 ~ 0.63, country fixed effects add a little, and the carbon-capture
    shares add essentially nothing. That is the diversity-vs-relatedness /
    centroid-stability point made quantitative, and it is why the sharper cluster
    co-membership test (stage_cluster) is the one that carries the local signal.

    Standard errors are clustered by country: the fixed-effects design has 23
    singleton countries that make naive and HC3 SEs degenerate. Mirrors notebook
    01 §5.7. (The 'is the overlap itself an artifact' question is answered by the
    re-pairing permutation of centroids, not by permuting this regression.)
    """
    print("\n[A1] Centroid-overlap regression (city size vs. field baseline)")
    import statsmodels.formula.api as smf
    df = city.copy()
    df["log_n_papers"] = np.log1p(df["n_papers"])
    df["log_n_projects"] = np.log1p(df["n_projects"])
    clu = {"groups": df["country"]}

    m1 = smf.ols("semantic_overlap ~ log_n_papers + log_n_projects",
                 data=df).fit(cov_type="HC3")
    m2 = smf.ols("semantic_overlap ~ log_n_papers + log_n_projects + C(country)",
                 data=df).fit(cov_type="cluster", cov_kwds=clu)
    m3 = smf.ols("semantic_overlap ~ log_n_papers + log_n_projects + C(country)"
                 " + cs_paper_share + cs_project_share",
                 data=df).fit(cov_type="cluster", cov_kwds=clu)
    fe_only = smf.ols("semantic_overlap ~ C(country)", data=df).fit()

    record("ols_rsq_model_one", m1.rsquared, ".3f", "size only")
    record("ols_rsq_model_two", m2.rsquared, ".3f", "+ country fixed effects")
    record("ols_rsq_model_three", m3.rsquared, ".3f", "+ carbon-capture shares")
    record("ols_rsq_country_only", fe_only.rsquared, ".3f", "country FE alone")
    record("ols_beta_papers", m2.params["log_n_papers"], "+.4f")
    record("ols_beta_projects", m2.params["log_n_projects"], "+.4f")
    record("ols_size_p_max", max(m2.pvalues["log_n_papers"],
                                 m2.pvalues["log_n_projects"]), ".1e",
           "max p over the two size coefficients (cluster-robust by country)")
    record("ols_cc_paper_p", m3.pvalues["cs_paper_share"], ".2f")
    record("ols_cc_project_p", m3.pvalues["cs_project_share"], ".2f")

    save_table(pd.DataFrame({
        "Model": ["(1) size only", "(2) + country fixed effects",
                  "(3) + carbon-capture shares"],
        "R2": [m1.rsquared, m2.rsquared, m3.rsquared]}),
        "overlap_regression", float_format="%.3f",
        caption="Nested OLS models for city-level semantic overlap. City size (log "
                "paper and project counts) alone explains most of the variance; "
                "country fixed effects add a little, and carbon-capture shares add "
                "essentially nothing.", label="tab:overlapreg")

    # Coefficient plot for the size effect (Model 2, cluster-robust 95% CI).
    ci = m2.conf_int().loc[["log_n_papers", "log_n_projects"]]
    est = m2.params.loc[["log_n_papers", "log_n_projects"]]
    fig, ax = plt.subplots(figsize=(7, 3))
    ypos = np.arange(len(est))
    ax.errorbar(est.values, ypos,
                xerr=[est.values - ci[0].values, ci[1].values - est.values],
                fmt="o", color=BLUE, capsize=4)
    ax.axvline(0, color=MUTED, linestyle="--", linewidth=1)
    ax.set_yticks(ypos); ax.set_yticklabels(["log(1 + papers)", "log(1 + projects)"])
    ax.set(xlabel="Coefficient on semantic overlap (cluster-robust 95% CI)",
           title="City size predicts overlap (Model 2)")
    save_fig("coef_plot_overlap")


# ──────────────────────────────────────────────────────────────────────────────
# Stage A2 — cluster co-membership: a baseline-free test of local relatedness
# ──────────────────────────────────────────────────────────────────────────────
def stage_cluster() -> None:
    """City-level cluster co-membership: do a city's papers and projects fall in the
    *same* HDBSCAN topic clusters more than a within-country re-pairing would?

    This is the baseline-free counterpart to the centroid overlap (which is pinned
    near 1.0 by the synthetic-biology field baseline). It reads the document-level
    cluster labels persisted in all_artifacts.csv by scripts/05_cluster.py, so it
    needs no embedding model. Closes the gap noted in this script's header.

    References: HDBSCAN (Campello et al. 2013); permutation inference (Good 2005);
    Mantel (1967) for the two-matrix correlation; MacKinnon & White (1985) for HC3.
    """
    print("\n[A2] Cluster co-membership (from all_artifacts.csv)")
    art = pd.read_csv(DATA / "all_artifacts.csv", low_memory=False)
    art["city_key"] = art["city"].astype(str).str.strip().str.lower()
    valid = art[art["cluster_label"] >= 0]          # drop HDBSCAN noise (label -1)
    K = int(valid["cluster_label"].max()) + 1

    def freq(sub):
        """L2-normalised length-K cluster-frequency vector (None if no clustered docs)."""
        v = np.zeros(K)
        for c, n in sub["cluster_label"].value_counts().items():
            v[int(c)] = n
        nrm = np.linalg.norm(v)
        return v / nrm if nrm > 0 else None

    city = pd.read_csv(DATA / "city_level.csv")[["city_key", "country", "semantic_overlap"]]
    pvec, qvec, rows = {}, {}, []
    for ck, g in valid.groupby("city_key"):
        pg, qg = g[g.type == "paper"], g[g.type == "project"]
        if len(pg) == 0 or len(qg) == 0:
            continue
        p, q = freq(pg), freq(qg)
        if p is None or q is None:
            continue
        pvec[ck], qvec[ck] = p, q
        rows.append({"city_key": ck, "n_cl_papers": len(pg), "n_cl_projects": len(qg),
                     "cluster_overlap": float(np.dot(p, q))})  # both unit-norm -> dot = cosine
    co = pd.DataFrame(rows).merge(city, on="city_key", how="left")
    co["log_n_cl_papers"] = np.log1p(co["n_cl_papers"])
    co["log_n_cl_projects"] = np.log1p(co["n_cl_projects"])
    record("cluster_n_cities_all", len(co), ",d", "cities with >=1 clustered doc of each type")

    # Primary sample: cities dense enough to estimate a topic distribution at all.
    # Below this, the K-dim vectors are so sparse that papers and projects miss each
    # other by chance (a measurement floor), so the signal is unmeasurable, not absent.
    MIN = 8
    dense = co[(co.n_cl_papers >= MIN) & (co.n_cl_projects >= MIN)].copy()
    record("cluster_min_docs", MIN)
    record("cluster_n_cities_dense", len(dense), ",d", f">= {MIN} clustered docs of each type")

    # OLS: is the overlap just a city-size effect? (mirror of the centroid regression)
    import statsmodels.formula.api as smf
    ols = smf.ols("cluster_overlap ~ log_n_cl_papers + log_n_cl_projects",
                  data=dense).fit(cov_type="HC3")
    record("cluster_ols_rsq", ols.rsquared, ".3f")
    record("cluster_size_papers_p", ols.pvalues["log_n_cl_papers"], ".3f")
    record("cluster_size_projects_p", ols.pvalues["log_n_cl_projects"], ".3f")

    # The decisive test: within-country re-pairing permutation. Break the link between
    # a city's own papers and own projects (shuffle which project-vector pairs with
    # which paper-vector, within country) and recompute the mean. Observed >> null
    # means the own pairing is genuinely related beyond same-country chance.
    from collections import defaultdict
    rng = np.random.default_rng(42)
    cities = list(dense.city_key)
    observed = float(np.mean([np.dot(pvec[c], qvec[c]) for c in cities]))
    country_of = dict(zip(dense.city_key, dense.country))
    groups = defaultdict(list)
    for c in cities:
        groups[country_of[c]].append(c)
    N_PERM = 2000
    null = np.empty(N_PERM)
    for t in range(N_PERM):
        sims = []
        for gc in groups.values():
            if len(gc) == 1:                          # singletons can't be shuffled
                sims.append(np.dot(pvec[gc[0]], qvec[gc[0]]))
            else:
                perm = rng.permutation(gc)
                sims.extend(np.dot(pvec[a], qvec[b]) for a, b in zip(gc, perm))
        null[t] = np.mean(sims)
    p_perm = (np.sum(null >= observed) + 1) / (N_PERM + 1)
    record("cluster_perm_observed", observed, ".4f")
    record("cluster_perm_null_mean", null.mean(), ".4f")
    record("cluster_perm_p", p_perm, ".4f")
    record("cluster_perm_excess", observed - null.mean(), "+.4f")

    # Figure: centroid-vs-cluster contrast (left) + permutation null (right)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].hist(co.semantic_overlap.dropna(), bins=30, color=FILL, edgecolor="white",
                 label="centroid overlap")
    axes[0].hist(co.cluster_overlap, bins=30, color=ORANGE, alpha=0.7, edgecolor="white",
                 label="cluster co-membership")
    axes[0].set(xlabel="City-level overlap", ylabel="Number of cities",
                title="Centroid overlap is pinned near 1.0;\ncluster co-membership is discriminative")
    axes[0].legend(fontsize=8)
    axes[1].hist(null, bins=40, color=FILL, edgecolor="white", label="re-paired null")
    axes[1].axvline(observed, color=ORANGE, linewidth=2,
                    label=f"observed = {observed:.3f}  (p = {p_perm:.4f})")
    axes[1].axvline(null.mean(), color=MUTED, linestyle="--", linewidth=1)
    axes[1].set(xlabel="Mean city cluster co-membership", ylabel="Permutations",
                title="Survives the within-country\nre-pairing permutation test")
    axes[1].legend(fontsize=8)
    save_fig("cluster_comembership")

    # Cross-modal Mantel test: do part-type space and cluster space agree across cities?
    # (An independent corroboration: parts are measured with no reference to the text.)
    try:
        parts = pd.read_csv(DATA / "parts.csv", usecols=["team_id", "biobrick_part_type"]).dropna()
        parts["team_id"] = parts["team_id"].astype(int)
        proj = pd.read_csv(DATA / "projects.csv", usecols=["team_id", "city"]).dropna()
        proj["city_key"] = proj["city"].astype(str).str.strip().str.lower()
        proj["team_id"] = proj["team_id"].astype(int)
        tc = proj[["team_id", "city_key"]].drop_duplicates("team_id")
        parts = parts.merge(tc, on="team_id", how="left").dropna(subset=["city_key"])
        pcount = parts.groupby(["city_key", "biobrick_part_type"]).size().unstack(fill_value=0)
        pcount = pcount[pcount.sum(axis=1) >= 10]
        pprops = pcount.div(pcount.sum(axis=1), axis=0)
        common = [c for c in qvec if c in pprops.index]    # cities with both representations
        from sklearn.metrics.pairwise import cosine_similarity as cossim
        Sc = cossim(np.vstack([qvec[c] for c in common]))        # cluster-space similarity
        Sp = cossim(np.vstack([pprops.loc[c].values for c in common]))  # part-type similarity
        tri = np.triu_indices(len(common), k=1)
        r_obs = float(stats.spearmanr(Sc[tri], Sp[tri]).statistic)
        rng2 = np.random.default_rng(42)
        perm = np.array([stats.spearmanr(Sp[tri], Sc[(o := rng2.permutation(len(common)))][:, o][tri]).statistic
                         for _ in range(999)])
        mp = (np.sum(np.abs(perm) >= abs(r_obs)) + 1) / (999 + 1)
        record("mantel_r", r_obs, "+.2f")
        record("mantel_p", mp, ".4f")
        record("mantel_n_cities", len(common), ",d")
    except Exception as e:
        print(f"  mantel test skipped ({type(e).__name__}: {e})")


# ──────────────────────────────────────────────────────────────────────────────
# Stage B — activity over time (cheap: just counts)
# ──────────────────────────────────────────────────────────────────────────────
def stage_activity(papers: pd.DataFrame, projects: pd.DataFrame) -> None:
    print("\n[B] Activity over time")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    papers.groupby("year").size().plot(ax=axes[0], color=BLUE)
    axes[0].set(title="Papers per year", xlabel="Year", ylabel="Count")
    projects.groupby("year").size().plot(ax=axes[1], color=CYAN)
    axes[1].set(title="iGEM projects per year", xlabel="Year", ylabel="Count")
    save_fig("activity_by_year")
    record("n_papers_total", len(papers), ",d")
    record("n_projects_total", len(projects), ",d")
    record("paper_year_min", int(papers.year.min()))
    record("paper_year_max", int(papers.year.max()))
    record("project_year_min", int(projects.year.min()))
    record("project_year_max", int(projects.year.max()))


# ──────────────────────────────────────────────────────────────────────────────
# Stage C — embedding-based local alignment, DiD, and lead-lag
# ──────────────────────────────────────────────────────────────────────────────
def stage_embeddings(papers: pd.DataFrame, projects: pd.DataFrame) -> None:
    print("\n[C] Embedding-based alignment / DiD / lead-lag")
    from embed.embeddings import _load_cache
    cache = _load_cache(EMB_FILE)
    print(f"  loaded {len(cache):,} cached embeddings")
    if not cache:
        print("  no embeddings found — skipping stage C")
        return

    pap = attach_embeddings(papers, cache)
    proj = attach_embeddings(projects, cache)
    print(f"  papers w/ emb: {len(pap):,}   projects w/ emb: {len(proj):,}")

    # --- Eligible city paper-centroids (>= 3 papers for stability) ---
    MIN_CITY_PAPERS = 3
    counts = pap.groupby("city_key").size()
    eligible = [c for c, n in counts.items() if n >= MIN_CITY_PAPERS]
    cmat = np.stack([unit_centroid(np.stack(pap.loc[pap.city_key == c, "emb"].to_numpy()))
                     for c in eligible]).astype(np.float32)
    idx = {c: i for i, c in enumerate(eligible)}

    # --- Project-level local alignment: own city vs other cities ---
    pv = proj[proj.city_key.isin(idx)].reset_index(drop=True)
    P = np.stack(pv["emb"].to_numpy()).astype(np.float32)
    P /= np.clip(np.linalg.norm(P, axis=1, keepdims=True), 1e-8, None)
    sims = P @ cmat.T
    own = sims[np.arange(len(pv)), pv.city_key.map(idx).to_numpy()]
    other = (sims.sum(axis=1) - own) / (len(eligible) - 1)
    delta = own - other
    t, p = stats.ttest_1samp(delta, 0, alternative="greater")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].hist(delta, bins=60, color=FILL, edgecolor="white")
    axes[0].axvline(0, color=MUTED, linestyle="--")
    axes[0].axvline(delta.mean(), color=ORANGE, linewidth=2, label=f"Mean δ = {delta.mean():+.4f}")
    axes[0].set(xlabel="sim(own city) − mean sim(other cities)", ylabel="Projects",
                title="Project-level local alignment")
    axes[0].legend()
    axes[1].scatter(other, own, alpha=0.25, s=8, color=BLUE)
    lo, hi = min(own.min(), other.min()) - 0.002, max(own.max(), other.max()) + 0.002
    axes[1].plot([lo, hi], [lo, hi], "k--", linewidth=1, label="y = x (no difference)")
    axes[1].set(xlabel="Mean similarity to other cities", ylabel="Similarity to own city",
                title="Own-city vs. other-city similarity")
    axes[1].legend(fontsize=8)
    save_fig("project_level_alignment")
    record("align_mean_delta", delta.mean(), "+.4f")
    record("align_frac_pos", (delta > 0).mean(), ".3f")
    record("align_t", t, ".2f")
    record("align_p", p, ".4f")
    record("align_n_projects", len(pv), ",d")

    # --- City-clustered inference (projects within a city are not independent) ---
    city_keys = pv.city_key.to_numpy()
    _, _, t_clu, _, n_cities = cluster_robust_mean(delta, city_keys)
    record("align_t_clustered", t_clu, ".2f")
    record("align_n_cities", n_cities, ",d")

    # City as the unit of analysis: average delta within each city, then test.
    city_delta = pd.Series(delta).groupby(city_keys).mean()
    t_city, p_city = stats.ttest_1samp(city_delta, 0, alternative="greater")
    record("align_delta_city", city_delta.mean(), "+.4f")
    record("align_t_city", t_city, ".2f")
    record("align_frac_cities_pos", (city_delta > 0).mean(), ".3f")

    # --- Heterogeneity: is the local advantage concentrated in large cities? ---
    # "Size" = number of embedded papers a project's home city has.
    city_npapers = counts.reindex(city_delta.index)
    r_sz, p_sz = stats.pearsonr(np.log1p(city_npapers.to_numpy()), city_delta.to_numpy())
    record("align_size_r", r_sz, "+.2f")
    record("align_size_p", p_sz, ".3f")
    med_np = float(city_npapers.median())
    home_np = pv.city_key.map(counts).to_numpy()
    big = home_np >= med_np
    record("align_delta_large", delta[big].mean(), "+.4f")
    record("align_delta_small", delta[~big].mean(), "+.4f")

    # --- Carbon-capture slice: does the case-study subset align locally too? ---
    cc_col = pv.get("case_study_flag")
    if cc_col is not None:
        cc = cc_col.fillna(False).astype(bool).to_numpy()
        if cc.sum() >= 5:
            cc_delta = delta[cc]
            _, _, cc_t, _, cc_ncity = cluster_robust_mean(cc_delta, city_keys[cc])
            record("cc_align_n", int(cc.sum()), ",d")
            record("cc_align_n_cities", cc_ncity, ",d")
            record("cc_align_mean_delta", cc_delta.mean(), "+.4f")
            record("cc_align_frac_pos", (cc_delta > 0).mean(), ".3f")
            record("cc_align_t_clustered", cc_t, ".2f")

    # --- Difference-in-differences: is the local advantage stronger in the project's own year? ---
    MIN_ANNUAL_PAPERS = 2
    annual = {}
    for (c, y), g in pap.groupby(["city_key", "year"]):
        if len(g) >= MIN_ANNUAL_PAPERS:
            v = unit_centroid(np.stack(g["emb"].to_numpy()))
            if v is not None:
                annual[(c, int(y))] = v
    keys = list(annual)
    acity = np.array([k[0] for k in keys])
    ayear = np.array([k[1] for k in keys])
    amat = np.stack([annual[k] for k in keys]).astype(np.float32)
    have = [(r.city_key, int(r.year)) in annual for r in pv.itertuples()]
    pd_ = pv[have].reset_index(drop=True)
    PD = np.stack(pd_["emb"].to_numpy()).astype(np.float32)
    PD /= np.clip(np.linalg.norm(PD, axis=1, keepdims=True), 1e-8, None)
    sfull = PD @ amat.T
    rows = []
    for i, r in enumerate(pd_.itertuples()):
        sc, sy = acity == r.city_key, ayear == int(r.year)
        aa, ab, ba, bb = sc & sy, sc & ~sy, ~sc & sy, ~sc & ~sy
        if not (aa.any() and ab.any() and ba.any() and bb.any()):
            continue
        s = sfull[i]
        AA, AB, BA, BB = s[aa].mean(), s[ab].mean(), s[ba].mean(), s[bb].mean()
        rows.append({"city_key": r.city_key,
                     "sim_AA": AA, "sim_AB": AB, "sim_BA": BA, "sim_BB": BB,
                     "did": (AA - BA) - (AB - BB)})
    did = pd.DataFrame(rows)
    m = did[["sim_AA", "sim_AB", "sim_BA", "sim_BB", "did"]].mean()
    t_d, p_d = stats.ttest_1samp(did["did"], 0, alternative="greater")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    labels = ["AA\nown city,\nown year", "BA\nother cities,\nown year",
              "AB\nown city,\nother years", "BB\nother cities,\nother years"]
    vals = [m.sim_AA, m.sim_BA, m.sim_AB, m.sim_BB]
    axes[0].bar(labels, vals, color=[BLUE, CYAN, BLUE, CYAN], alpha=0.85, edgecolor="white")
    axes[0].set(ylabel="Mean cosine similarity", title="DiD: similarity by city × year cell",
                ylim=(min(vals) - 0.01, max(vals) + 0.006))
    axes[1].hist(did["did"], bins=60, color=FILL, edgecolor="white")
    axes[1].axvline(0, color=MUTED, linestyle="--")
    axes[1].axvline(m.did, color=ORANGE, linewidth=2, label=f"Mean DiD = {m.did:+.4f}")
    axes[1].set(xlabel="DiD per project", ylabel="Count",
                title=f"Project-level DiD (t = {t_d:.2f}, p = {p_d:.4f})")
    axes[1].legend(fontsize=9)
    save_fig("did_alignment")
    record("did_estimate", m.did, "+.4f")
    record("did_t", t_d, ".2f")
    record("did_p", p_d, ".4f")
    record("did_n", len(did), ",d")
    # City-clustered inference for the DiD, same logic as the alignment test.
    _, _, did_t_clu, _, did_ncity = cluster_robust_mean(did["did"], did["city_key"])
    record("did_t_clustered", did_t_clu, ".2f")
    record("did_n_cities", did_ncity, ",d")
    save_table(pd.DataFrame({"": ["Own year", "Other years"],
                             "Own city": [m.sim_AA, m.sim_AB],
                             "Other cities": [m.sim_BA, m.sim_BB]}),
               "did_cells", float_format="%.4f",
               caption="Difference-in-differences cells: mean cosine similarity between iGEM "
                       "projects and annual paper centroids.", label="tab:did")

    # --- Lead-lag: are project topics in year t closest to paper topics at t+k? ---
    LAGS = range(-3, 4)
    np.random.seed(42)

    def annual_centroids(df):
        out = {}
        for (c, y), g in df.groupby(["city_key", "year"]):
            out[(c, int(y))] = unit_centroid(np.stack(g["emb"].to_numpy()))
        return out

    pa, qa = annual_centroids(pap), annual_centroids(proj)
    lag_sims = {k: [] for k in LAGS}
    for (c, y), v in qa.items():
        if v is None:
            continue
        for k in LAGS:
            w = pa.get((c, y + k))
            if w is not None:
                lag_sims[k].append(float(np.dot(v, w)))
    lrows = []
    for k in LAGS:
        a = np.array(lag_sims[k])
        if not len(a):
            continue
        boot = [np.mean(np.random.choice(a, len(a), replace=True)) for _ in range(1000)]
        lrows.append({"lag": k, "n_pairs": len(a), "mean_sim": a.mean(),
                      "ci_lo": np.percentile(boot, 2.5), "ci_hi": np.percentile(boot, 97.5)})
    lag = pd.DataFrame(lrows)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.errorbar(lag.lag, lag.mean_sim,
                yerr=[lag.mean_sim - lag.ci_lo, lag.ci_hi - lag.mean_sim],
                fmt="o-", color=BLUE, capsize=5, linewidth=2)
    ax.axvline(0, color="#666666", linestyle="--", linewidth=0.8, label="k = 0 (same year)")
    ax.axvspan(0, max(LAGS) + 0.4, alpha=0.06, color=CYAN, label="projects lead")
    ax.axvspan(min(LAGS) - 0.4, 0, alpha=0.06, color=ORANGE, label="papers lead")
    ax.set(xlabel="Lag k  (positive → papers come after projects)",
           ylabel="Mean cosine similarity", title="Lead-lag profile (95% bootstrap CI)",
           xticks=list(LAGS))
    ax.legend(fontsize=8)
    save_fig("lead_lag_profile")
    save_table(lag.round(4), "lead_lag", float_format="%.4f",
               caption="Lead-lag similarity profile between project and paper centroids.",
               label="tab:leadlag")
    best = lag.loc[lag.mean_sim.idxmax()]
    record("leadlag_best_lag", int(best.lag), "+d")
    record("leadlag_best_sim", best.mean_sim, ".4f")


# ──────────────────────────────────────────────────────────────────────────────
# Stage D — BioBrick part-type composition (cheap)
# ──────────────────────────────────────────────────────────────────────────────
def stage_parts(projects: pd.DataFrame) -> None:
    print("\n[D] Part-type composition (from parts.csv)")
    parts = pd.read_csv(DATA / "parts.csv",
                        usecols=["team_id", "biobrick_part_type"]).dropna()
    parts["team_id"] = parts["team_id"].astype(int)
    team_city = (projects[["team_id", "city_key"]].dropna()
                 .drop_duplicates("team_id"))
    team_city["team_id"] = team_city["team_id"].astype(int)
    parts = parts.merge(team_city, on="team_id", how="left").dropna(subset=["city_key"])

    MIN_PARTS = 10
    counts = parts.groupby(["city_key", "biobrick_part_type"]).size().unstack(fill_value=0)
    counts = counts[counts.sum(axis=1) >= MIN_PARTS]
    props = counts.div(counts.sum(axis=1), axis=0)
    entropy = props.apply(lambda r: float(stats.entropy(r[r > 0])), axis=1)
    record("n_cities_parts", len(counts), ",d", f"cities with >= {MIN_PARTS} registered parts")
    record("part_entropy_median", entropy.median(), ".3f")
    record("part_entropy_max", float(np.log(props.shape[1])), ".3f", "uniform over all part types")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    axes[0].hist(entropy, bins=30, color=FILL, edgecolor="white")
    axes[0].axvline(entropy.median(), color=ORANGE, linestyle="--",
                    label=f"Median = {entropy.median():.2f} nats")
    axes[0].axvline(np.log(props.shape[1]), color=MUTED, linestyle=":",
                    label=f"Max (uniform) = {np.log(props.shape[1]):.2f} nats")
    axes[0].set(xlabel="Shannon entropy of part-type mix (nats)\nlow = specialised | high = diverse",
                ylabel="Number of cities", title="How specialised are cities in part types?")
    axes[0].legend()

    top_types = parts.biobrick_part_type.value_counts().head(10).index.tolist()
    top_keys = counts.sum(axis=1).nlargest(30).index
    hm = props.loc[top_keys].copy()
    hm["_dom"] = hm.idxmax(axis=1)
    hm = hm.sort_values("_dom").drop(columns="_dom")
    other = [c for c in hm.columns if c not in top_types]
    plot = hm[top_types].copy()
    if other:
        plot["other"] = hm[other].sum(axis=1)
    im = axes[1].imshow(plot.values, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    axes[1].set_xticks(range(len(plot.columns)))
    axes[1].set_xticklabels(plot.columns, rotation=45, ha="right", fontsize=8)
    axes[1].set_yticks(range(len(plot)))
    axes[1].set_yticklabels(plot.index.tolist(), fontsize=7)
    axes[1].set(xlabel="BioBrick part type",
                title="Part-type composition — top 30 cities by total parts")
    fig.colorbar(im, ax=axes[1], fraction=0.025, pad=0.04, label="Proportion of city's parts")
    save_fig("part_type_composition")


# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-embeddings", action="store_true",
                    help="skip the alignment/DiD/lead-lag stage (no cached vectors needed)")
    args = ap.parse_args()

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Writing manuscript assets to: {GEN_DIR}")

    # Shared loads: only the columns we actually need (papers.csv is large)
    papers = pd.read_csv(DATA / "papers.csv", usecols=["id", "city", "year"])
    projects = pd.read_csv(DATA / "projects.csv",
                           usecols=["id", "team_id", "city", "year", "case_study_flag"])
    for df in (papers, projects):
        df["city_key"] = df["city"].astype(str).str.strip().str.lower()
        df.dropna(subset=["year"], inplace=True)
        df["year"] = df["year"].astype(int)

    city = stage_city_level()
    stage_overlap_regression(city)
    stage_cluster()
    stage_activity(papers, projects)

    # Coverage: which cities have papers, projects, or both (the analysis needs both).
    pk, qk = set(papers["city_key"]), set(projects["city_key"])
    record("n_cities_papers_only", len(pk - qk), ",d")
    record("n_cities_projects_only", len(qk - pk), ",d")
    record("n_cities_both", len(pk & qk), ",d")
    try:
        record("n_biobrick_papers", len(pd.read_csv(DATA / "biobrick_papers.csv")), ",d",
               "papers citing a BioBrick ID (PubMedCentral full-text)")
    except Exception as e:
        print(f"  biobrick_papers count skipped ({e})")

    if not args.no_embeddings:
        try:
            stage_embeddings(papers, projects)
        except Exception as e:  # never let the heavy stage block the cheap exports
            print(f"  stage C failed ({type(e).__name__}: {e}) — skipping embedding figures")
    stage_parts(projects)

    write_stats()
    print("\nDone. In main.tex add:  \\graphicspath{{generated/figures/}}  and  \\input{generated/stats.tex}")


if __name__ == "__main__":
    main()
