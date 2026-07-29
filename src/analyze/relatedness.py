"""
relatedness.py — city-level cluster co-membership across artifact types.

This is the decisive test of the thesis, generalised from two artifact types
(notebook 01, papers vs projects) to three (projects, papers, patents).

The idea, in one line: cluster every document into a topic, then ask whether a
city's different artifact types land in the SAME topics more than chance.

Why co-membership and not centroid similarity?
  Centroid overlap is dominated by city size — bigger cities have steadier
  centroids that sit nearer the field-wide average, so overlap rises with size
  regardless of any local link (notebook 01). Cluster co-membership throws away
  the vector magnitudes and keeps only the topic partition, and it is symmetric,
  so it is immune both to that size artifact and to the papers-as-hub asymmetry
  of the fine-tuned embedding space.

For a city and an artifact type we build a cluster-frequency vector: how many of
that type's documents fall in each topic cluster, L2-normalised. The relatedness
of two types in a city is the cosine of their two frequency vectors. Noise
documents (HDBSCAN label -1) belong to no topic and are dropped.

The decisive test is a within-country re-pairing permutation. The null keeps each
country's set of cities and each type's document counts fixed, and only breaks the
specific pairing — so beating it means a city's own types are more topically
aligned than a random same-country city's types, which size and country cannot
explain. References for the permutation logic: notebook 01 §8; Boschma et al.
(2014) on relatedness nulls.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd


def build_city_type_vectors(
    clustered: pd.DataFrame,
    k_clusters: int,
    type_col: str = "type",
    city_col: str = "city_key",
    label_col: str = "cluster_label",
    norm: str = "l2",
) -> tuple[dict, dict]:
    """
    Build per-city, per-type cluster-frequency vectors.

    norm : "l2" (default) gives unit vectors whose dot product is the cosine used
           by the decisive test. "l1" gives probability distributions over topics
           whose dot product is P(a random doc of each type lands in the same
           topic) — the interpretable co-location statistic.

    Returns
    -------
    vecs : {type: {city: normalised frequency vector of length k_clusters}}
    counts : {type: {city: number of non-noise documents}}
    """
    valid = clustered[clustered[label_col] >= 0]
    vecs: dict = {}
    counts: dict = {}
    for typ, g in valid.groupby(type_col):
        tv, tc = {}, {}
        for city, gg in g.groupby(city_col):
            v = np.zeros(k_clusters, dtype=np.float64)
            for c, n in gg[label_col].value_counts().items():
                v[int(c)] = n
            denom = np.linalg.norm(v) if norm == "l2" else v.sum()
            if denom > 0:
                tv[city] = v / denom
                tc[city] = int(len(gg))
        vecs[typ] = tv
        counts[typ] = tc
    return vecs, counts


def comembership_table(
    vecs: dict,
    counts: dict,
    type_a: str,
    type_b: str,
    min_docs: int,
    country_of: dict,
    city_names: dict | None = None,
) -> pd.DataFrame:
    """
    One row per city that has >= min_docs of BOTH types, with the cosine overlap
    of their cluster-frequency vectors and the log document counts (for the size
    control OLS).
    """
    va, vb = vecs[type_a], vecs[type_b]
    ca, cb = counts[type_a], counts[type_b]
    rows = []
    for city in set(va) & set(vb):
        if ca.get(city, 0) < min_docs or cb.get(city, 0) < min_docs:
            continue
        rows.append({
            "city_key":       city,
            "city":           (city_names or {}).get(city, city),
            "country":        country_of.get(city),
            "overlap":        float(np.dot(va[city], vb[city])),
            f"n_{type_a}":    ca[city],
            f"n_{type_b}":    cb[city],
            f"log_n_{type_a}": float(np.log1p(ca[city])),
            f"log_n_{type_b}": float(np.log1p(cb[city])),
        })
    return pd.DataFrame(rows)


def own_vs_other(vecs: dict, type_a: str, type_b: str, cities: list) -> np.ndarray:
    """
    Per-city delta = cosine(own A, own B) - mean cosine(own A, every OTHER city's B).
    Positive means a city's two types are more alike than that city's A is to other
    cities' B. Used for the measurement-floor robustness curve.
    """
    A = np.vstack([vecs[type_a][c] for c in cities])
    B = np.vstack([vecs[type_b][c] for c in cities])
    S = A @ B.T
    n = len(cities)
    deltas = []
    for i in range(n):
        sim_own = S[i, i]
        sim_other = (S[i].sum() - sim_own) / (n - 1)
        deltas.append(sim_own - sim_other)
    return np.asarray(deltas)


def _grouped(cities: list, country_of: dict) -> dict:
    groups = defaultdict(list)
    for c in cities:
        groups[country_of.get(c)].append(c)
    return groups


def pair_permutation(
    vecs: dict,
    type_a: str,
    type_b: str,
    cities: list,
    country_of: dict,
    n_perm: int = 2000,
    seed: int = 42,
) -> dict:
    """
    Within-country re-pairing permutation test for one type pair.

    Observed = mean over cities of cosine(A_city, B_city). Under the null, inside
    each country we shuffle which city's B-vector is paired with each city's
    A-vector, so country composition and every document count are held fixed and
    only the local pairing is broken. Singleton countries contribute their true
    (unpermutable) pair to both observed and null, so they cannot manufacture
    signal.
    """
    va, vb = vecs[type_a], vecs[type_b]
    observed = float(np.mean([np.dot(va[c], vb[c]) for c in cities]))

    groups = _grouped(cities, country_of)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for t in range(n_perm):
        sims = []
        for gc in groups.values():
            if len(gc) == 1:
                sims.append(np.dot(va[gc[0]], vb[gc[0]]))
            else:
                perm = rng.permutation(gc)
                sims.extend(np.dot(va[a], vb[b]) for a, b in zip(gc, perm))
        null[t] = np.mean(sims)

    p = (np.sum(null >= observed) + 1) / (n_perm + 1)
    return {
        "type_a": type_a, "type_b": type_b, "n_cities": len(cities),
        "observed": observed, "null_mean": float(null.mean()),
        "null_p95": float(np.quantile(null, 0.95)),
        "excess": observed - float(null.mean()),
        "p_value": float(p), "null": null,
    }


def three_way_score(vecs: dict, types: tuple, cities: list) -> float:
    """Mean over cities of the average pairwise cluster-overlap among the three types."""
    a, b, c = types
    va, vb, vc = vecs[a], vecs[b], vecs[c]
    per = [
        (np.dot(va[city], vb[city]) + np.dot(vb[city], vc[city]) + np.dot(va[city], vc[city])) / 3.0
        for city in cities
    ]
    return float(np.mean(per))


def three_way_permutation(
    vecs: dict,
    types: tuple,
    cities: list,
    country_of: dict,
    n_perm: int = 2000,
    seed: int = 42,
) -> dict:
    """
    Exploratory three-way test. Per-city score = average of the three pairwise
    cluster-overlaps. The null holds type A fixed and independently re-pairs types
    B and C within country, so no city keeps its true triple while country and
    counts stay fixed.
    """
    a, b, c = types
    va, vb, vc = vecs[a], vecs[b], vecs[c]
    observed = three_way_score(vecs, types, cities)

    groups = _grouped(cities, country_of)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for t in range(n_perm):
        per = []
        for gc in groups.values():
            if len(gc) == 1:
                city = gc[0]
                per.append((np.dot(va[city], vb[city]) + np.dot(vb[city], vc[city])
                            + np.dot(va[city], vc[city])) / 3.0)
            else:
                pb = rng.permutation(gc)
                pc = rng.permutation(gc)
                for city, cb_, cc_ in zip(gc, pb, pc):
                    per.append((np.dot(va[city], vb[cb_]) + np.dot(vb[cb_], vc[cc_])
                                + np.dot(va[city], vc[cc_])) / 3.0)
        null[t] = np.mean(per)

    p = (np.sum(null >= observed) + 1) / (n_perm + 1)
    return {
        "types": types, "n_cities": len(cities),
        "observed": observed, "null_mean": float(null.mean()),
        "null_p95": float(np.quantile(null, 0.95)),
        "excess": observed - float(null.mean()),
        "p_value": float(p), "null": null,
    }


def relatedness_lift(
    clustered: pd.DataFrame,
    k_clusters: int,
    type_a: str,
    type_b: str,
    min_docs: int = 1,
    type_col: str = "type",
    city_col: str = "city_key",
    label_col: str = "cluster_label",
    topic_fe: bool = True,
) -> dict:
    """
    How much more likely is a city to be active in artifact type B in a research
    cluster where it is already active in type A, net of how big the city is and how
    popular the cluster is?

    This turns the abstract co-membership result into a plain effect size. The unit is
    a city x cluster cell; the "treatment" is "this city has type A here" and the
    outcome is "this city has type B here". City and cluster fixed effects play the
    role of the two difference-in-differences subtractions: the city effect removes
    each city's overall productivity (a prolific city is active everywhere), the
    cluster effect removes each cluster's overall popularity (a crowded topic attracts
    everyone). What is left on the treatment coefficient is the within-city,
    within-field co-location -- type B concentrating in the same clusters as type A.

    This is the principle of relatedness (Hidalgo et al. 2007, Science; Neffke, Henning
    & Boschma 2011, Economic Geography) read on the shared topic space, where "related"
    is literally "same cluster" rather than a proxy. It is an association, not a cause:
    the fixed effects strip out size and popularity but not a city's shared local
    interest in a topic, which can pull all three artifact types at once. It is also
    near-symmetric, so it does not on its own say A came before B.

    Cities are those active in BOTH registers, since a city with no type-B activity
    anywhere carries no within-city variation to learn from.

    topic_fe toggles the second subtraction. With topic_fe=True (default) the model
    removes both city size and cluster popularity -- the strict, standard relatedness
    specification. With topic_fe=False it removes only city size, so the lift also
    counts a city's shared pull toward globally popular clusters; the gap between the
    two tells you how much of the co-location is local specificity versus popularity.

    Returns the linear-probability lift in percentage points (`lpm_pp`) and an adjusted
    relative risk (`adj_rel_risk`, "x times as likely").
    """
    import statsmodels.formula.api as smf

    valid = clustered[clustered[label_col] >= 0]
    cities_a = set(valid.loc[valid[type_col] == type_a, city_col])
    cities_b = set(valid.loc[valid[type_col] == type_b, city_col])
    cities = sorted(cities_a & cities_b)

    def _presence(typ: str) -> dict:
        cnt = valid[valid[type_col] == typ].groupby([city_col, label_col]).size()
        out = defaultdict(set)
        for (c, k), n in cnt.items():
            if n >= min_docs:
                out[c].add(int(k))
        return out
    pa, pb = _presence(type_a), _presence(type_b)

    rows = []
    for c in cities:
        ta, tb = pa.get(c, set()), pb.get(c, set())
        for k in range(k_clusters):
            rows.append((c, k, int(k in ta), int(k in tb)))
    df = pd.DataFrame(rows, columns=["city", "topic", "treat", "outcome"])

    # Fixed-effects linear probability model, SEs clustered by city. City FE always;
    # topic FE optional (the second, popularity-removing subtraction).
    formula = "outcome ~ treat + C(city)" + (" + C(topic)" if topic_fe else "")
    m = smf.ols(formula, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["city"]})
    pp = float(m.params["treat"])

    # Adjusted relative risk: mean predicted P(B) if every cell were treated vs not.
    # Only meaningful when the linear model's average predictions stay in (0, 1];
    # a negative lift can push them out of range, where a risk ratio is undefined.
    _p1 = float(m.predict(df.assign(treat=1)).mean())
    _p0 = float(m.predict(df.assign(treat=0)).mean())
    _rr = (_p1 / _p0) if (_p0 > 0 and _p1 >= 0) else float("nan")

    return {
        "type_a": type_a, "type_b": type_b, "topic_fe": topic_fe,
        "n_cities": len(cities), "n_obs": int(len(df)),
        "base_rate": float(df["outcome"].mean()),
        "treated_rate": float(df.loc[df.treat == 1, "outcome"].mean()),
        "untreated_rate": float(df.loc[df.treat == 0, "outcome"].mean()),
        "lpm_pp": pp, "lpm_se": float(m.bse["treat"]), "lpm_p": float(m.pvalues["treat"]),
        "adj_rel_risk": _rr,
    }
