"""
robustness.py — robustness checks for the cluster co-membership result.

Two questions a sceptic asks after the permutation test:

  1. Is the co-membership just city size wearing a new hat? We regress it on the
     log document counts (with country fixed effects) and check that size
     explains little — unlike the centroid measure, which size explained almost
     entirely.

  2. Does the result depend on one lucky clustering? We re-cluster the same
     embeddings at a range of granularities (KMeans, k from coarse to fine) and
     re-run the decisive test at each, so the signal has to hold across the sweep,
     not at a single magic k.

These complement, rather than replace, the within-country permutation in
relatedness.py — convergent evidence from methods that fail in different ways.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .relatedness import build_city_type_vectors, comembership_table, pair_permutation


def size_control_ols(tab: pd.DataFrame, type_a: str, type_b: str, min_country: int = 2) -> dict:
    """
    Regress a pair's cluster co-membership on the two log document counts, then
    add country fixed effects. Returns the R-squared and size coefficients.

    A LOW size R-squared is the point: it says co-membership is not a restatement
    of how much a city produces (contrast the centroid measure, where size R^2 was
    high). Standard errors are HC3 (heteroskedasticity-robust).
    """
    import statsmodels.formula.api as smf

    df = tab.dropna(subset=["overlap"]).copy()
    la, lb = f"log_n_{type_a}", f"log_n_{type_b}"
    formula = f"overlap ~ {la} + {lb}"

    # Cluster-robust standard errors by country: cities in one country are not
    # independent (a single country can supply a third of the sample), so plain
    # or HC3 errors would understate uncertainty. R^2 is unaffected by the choice.
    if df["country"].nunique() >= 2:
        m1 = smf.ols(formula, data=df).fit(
            cov_type="cluster", cov_kwds={"groups": df["country"]})
    else:
        m1 = smf.ols(formula, data=df).fit(cov_type="HC3")
    out = {
        "type_a": type_a, "type_b": type_b, "n": int(len(df)),
        "r2_size": float(m1.rsquared),
        f"beta_{la}": float(m1.params[la]), f"p_{la}": float(m1.pvalues[la]),
        f"beta_{lb}": float(m1.params[lb]), f"p_{lb}": float(m1.pvalues[lb]),
        "r2_country_fe": None, "n_fe": None,
    }

    vc = df["country"].value_counts()
    df_fe = df[df["country"].isin(vc[vc >= min_country].index)]
    if df_fe["country"].nunique() >= 2 and len(df_fe) > df_fe["country"].nunique() + 3:
        m2 = smf.ols(formula + " + C(country)", data=df_fe).fit(cov_type="HC3")
        out["r2_country_fe"] = float(m2.rsquared)
        out["n_fe"] = int(len(df_fe))
    return out


def kmeans_labels(X: np.ndarray, k: int, seed: int = 42) -> np.ndarray:
    """
    Cluster L2-normalised embeddings into k topics with KMeans. Normalising first
    makes Euclidean KMeans approximate spherical (cosine) k-means, which suits
    text embeddings. Returns integer labels 0..k-1 (no noise label).
    """
    from sklearn.cluster import KMeans

    Xn = X / np.clip(np.linalg.norm(X, axis=1, keepdims=True), 1e-8, None)
    km = KMeans(n_clusters=k, random_state=seed, n_init=10)
    return km.fit_predict(Xn)


def leave_one_city_out(
    vecs: dict,
    type_a: str,
    type_b: str,
    cities: list,
    country_of: dict,
    n_perm: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Drop each city once, re-run the decisive permutation on the rest, and record
    the p-value and excess without that city. If the result is genuinely local and
    spread across many cities, no single removal should move the p-value much; if
    one hub city (Boston, say) is carrying it, dropping that city sends the p-value
    up. One row per dropped city, sorted worst (highest) p-value first.
    """
    rows = []
    for drop in cities:
        rest = [c for c in cities if c != drop]
        r = pair_permutation(vecs, type_a, type_b, rest, country_of,
                             n_perm=n_perm, seed=seed)
        rows.append({"dropped": drop, "n_cities": r["n_cities"],
                     "excess": r["excess"], "p_value": r["p_value"]})
    return pd.DataFrame(rows).sort_values("p_value", ascending=False).reset_index(drop=True)


def leave_one_country_out(
    vecs: dict,
    type_a: str,
    type_b: str,
    cities: list,
    country_of: dict,
    n_perm: int = 2000,
    seed: int = 42,
    min_drop: int = 2,
) -> pd.DataFrame:
    """
    Drop one whole country at a time and re-run the decisive permutation on the
    rest. This is the sharp version of the jackknife: when one country (the US)
    supplies a third or more of the cities, "within-country re-pairing" is mostly
    "within-US re-pairing", so the honest question is whether the signal survives
    removing that country entirely. One row per dropped country (only countries
    with >= min_drop cities), sorted by how many cities they contribute.
    """
    from collections import Counter

    cnt = Counter(country_of.get(c) for c in cities)
    rows = []
    for country, n in sorted(cnt.items(), key=lambda kv: (-kv[1], str(kv[0]))):
        if n < min_drop:
            continue
        rest = [c for c in cities if country_of.get(c) != country]
        if len(rest) < 5:
            continue
        r = pair_permutation(vecs, type_a, type_b, rest, country_of,
                             n_perm=n_perm, seed=seed)
        rows.append({"dropped_country": country, "n_dropped": int(n),
                     "n_cities": r["n_cities"], "excess": r["excess"],
                     "p_value": r["p_value"]})
    return pd.DataFrame(rows)


def downsample_power(
    vecs: dict,
    type_a: str,
    type_b: str,
    cities: list,
    country_of: dict,
    target_n: int,
    n_draws: int = 200,
    n_perm: int = 500,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict:
    """
    Ask whether a WORKING link would still look significant if it only had as many
    cities as the failed one. We take a strong pair (e.g. paper-project, 120 cities),
    repeatedly keep a random `target_n` of its cities (e.g. 28, matching the
    project-patent link), and re-run the decisive permutation on each subset.

    Returns the share of random subsets that stay significant at `alpha`. If that
    share is LOW, then 28 cities is simply too few to detect this size of effect,
    so the project-patent null is "underpowered", not "no link". If it stays HIGH,
    28 cities was plenty and the null is a real absence.
    """
    rng = np.random.default_rng(seed)
    cities = list(cities)
    ps, exc = [], []
    for d in range(n_draws):
        sub = list(rng.choice(cities, size=target_n, replace=False))
        r = pair_permutation(vecs, type_a, type_b, sub, country_of,
                             n_perm=n_perm, seed=int(rng.integers(1 << 31)))
        ps.append(r["p_value"]); exc.append(r["excess"])
    ps = np.asarray(ps)
    return {
        "type_a": type_a, "type_b": type_b,
        "full_n": len(cities), "target_n": target_n, "n_draws": n_draws,
        "share_significant": float(np.mean(ps <= alpha)),
        "median_p": float(np.median(ps)),
        "median_excess": float(np.median(exc)),
        "p_values": ps,
    }


def decisive_for_labels(
    arts: pd.DataFrame,
    labels: np.ndarray,
    valid_ids: list,
    k: int,
    pairs: list,
    min_docs: int,
    country_of: dict,
    city_name: dict,
    n_perm: int = 1000,
    seed: int = 42,
) -> list:
    """
    Run the decisive co-membership permutation for each type pair, given an
    arbitrary partition (labels aligned to valid_ids). Used by the k-sweep.
    """
    lab = dict(zip(valid_ids, labels))
    tmp = arts.copy()
    tmp["cluster_label"] = tmp["id"].map(lambda i: lab.get(i, -1))

    vecs, counts = build_city_type_vectors(tmp, k)
    rows = []
    for a, b in pairs:
        tab = comembership_table(vecs, counts, a, b, min_docs, country_of, city_name)
        if len(tab) < 5:
            rows.append({"k": k, "type_a": a, "type_b": b, "n_cities": len(tab),
                         "observed": np.nan, "null_mean": np.nan,
                         "excess": np.nan, "p_value": np.nan})
            continue
        r = pair_permutation(vecs, a, b, list(tab.city_key), country_of,
                             n_perm=n_perm, seed=seed)
        rows.append({"k": k, "type_a": a, "type_b": b, "n_cities": r["n_cities"],
                     "observed": r["observed"], "null_mean": r["null_mean"],
                     "excess": r["excess"], "p_value": r["p_value"]})
    return rows
