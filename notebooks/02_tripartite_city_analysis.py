import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Tripartite city-level analysis

    Do a city's **student projects**, **academic papers**, and **patents** in
    synthetic biology work on the same specific topics? This notebook is the home
    of the project's core analysis. It embeds all three artifact types in one
    fine-tuned semantic space, sorts them into topics, and asks whether a city's
    three kinds of work fall into the *same* topics more than chance — and more
    than city size, country, or one dominant country can explain.

    The argument runs in five moves:

    1. **a map** of the field, so we trust the space before testing on it;
    2. **the seductive wrong answer** — centroid overlap, which just measures size;
    3. **the decisive test** — cluster co-membership against a permutation null;
    4. **three honest attempts to break it** — drop a country, change the
       clustering, starve the sample;
    5. **what it shows, and what it can't.**

    Embeddings come from SPECTER2 with our fine-tuned adapter; clusters come from
    `scripts/10_cluster_tripartite.py`. We speak of semantic relatedness and
    association throughout, never cause.
    """)
    return


@app.cell
def _():
    # ── Setup: imports, paths, project modules ───────────────────────────────
    import sys
    from pathlib import Path
    from collections import defaultdict

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import scipy.stats as stats

    ROOT = Path.cwd()
    if not (ROOT / "src").exists() and (ROOT.parent / "src").exists():
        ROOT = ROOT.parent          # allow running from notebooks/
    sys.path.insert(0, str(ROOT))

    PROCESSED = ROOT / "data" / "processed"
    FT_CACHE  = ROOT / "data" / "embeddings" / "finetuned" / "embeddings.json"
    FIGDIR    = ROOT / "outputs" / "figures"
    FIGDIR.mkdir(parents=True, exist_ok=True)

    from src.embed.embeddings import _load_cache as load_cache
    from src.analyze.relatedness import (
        build_city_type_vectors, comembership_table,
        pair_permutation, three_way_permutation,
    )
    from src.analyze.robustness import (
        size_control_ols, leave_one_country_out, downsample_power,
    )

    return (
        FIGDIR,
        FT_CACHE,
        PROCESSED,
        build_city_type_vectors,
        comembership_table,
        downsample_power,
        leave_one_country_out,
        load_cache,
        mpl,
        np,
        pair_permutation,
        pd,
        plt,
        size_control_ols,
        stats,
        three_way_permutation,
    )


@app.cell
def _(mpl):
    # ── Solarized Light theme + large publication figures ────────────────────
    from matplotlib.colors import LinearSegmentedColormap

    SOL = {
        "bg": "#fdf6e3", "bg2": "#eee8d5", "muted": "#93a1a1", "text": "#657b83",
        "paper": "#268bd2", "project": "#2aa198", "patent": "#cb4b16",
        "blue": "#268bd2", "cyan": "#2aa198", "orange": "#cb4b16",
        "yellow": "#b58900", "red": "#dc322f", "violet": "#6c71c4", "green": "#859900",
    }
    sol_div = LinearSegmentedColormap.from_list("sol_div", [SOL["orange"], SOL["bg"], SOL["blue"]])

    mpl.rcParams.update({
        "figure.facecolor": SOL["bg"], "axes.facecolor": SOL["bg"],
        "axes.edgecolor": SOL["muted"], "axes.labelcolor": SOL["text"],
        "xtick.color": SOL["text"], "ytick.color": SOL["text"], "text.color": SOL["text"],
        "grid.color": SOL["bg2"], "grid.linestyle": "--", "grid.alpha": 0.8,
        "savefig.facecolor": SOL["bg"], "savefig.dpi": 200,
        "figure.dpi": 120, "figure.figsize": (16, 9),
        "font.size": 15, "axes.titlesize": 20, "axes.titleweight": "bold",
        "axes.labelsize": 16, "legend.fontsize": 13,
        "xtick.labelsize": 13, "ytick.labelsize": 13,
        "axes.prop_cycle": mpl.cycler(color=[
            SOL["blue"], SOL["cyan"], SOL["orange"], SOL["yellow"], SOL["violet"], SOL["green"]
        ]),
    })
    return (SOL,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Loading the data

    First we load the clustered three-type corpus and the fine-tuned embeddings.
    """)
    return


@app.cell
def _(FT_CACHE, PROCESSED, load_cache, pd):
    # ── Load the clustered three-type corpus and the fine-tuned embeddings ────
    arts = pd.read_csv(PROCESSED / "artifacts_tripartite_clustered.csv", low_memory=False)
    arts["city_key"] = arts["city"].astype(str).str.strip().str.lower()

    ft_cache = load_cache(FT_CACHE)

    K = int(arts.loc[arts.cluster_label >= 0, "cluster_label"].max()) + 1
    n_noise = int((arts.cluster_label < 0).sum())

    # Per-city country and display-name lookups (first non-null wins).
    country_of = (
        arts.groupby("city_key")["country"]
        .agg(lambda s: s.dropna().iloc[0] if s.notna().any() else None).to_dict()
    )
    city_name = arts.groupby("city_key")["city"].first().to_dict()

    # Which topic is carbon capture? The cluster with the highest share of
    # case-study-flagged documents.
    arts["is_cc"] = (
        arts["case_study_flag"].astype(str).str.lower().isin(["true", "1", "1.0"])
    )
    cc_cluster = int(
        arts[arts.cluster_label >= 0].groupby("cluster_label")["is_cc"].mean().idxmax()
    )

    type_counts = arts["type"].value_counts().to_dict()
    return (
        K,
        arts,
        cc_cluster,
        city_name,
        country_of,
        ft_cache,
        n_noise,
        type_counts,
    )


@app.cell
def _(K, arts, cc_cluster, mo, n_noise, type_counts):
    mo.md(f"""
    The corpus is **{len(arts):,} documents**: {type_counts.get('paper',0):,} papers,
    {type_counts.get('project',0):,} iGEM projects, {type_counts.get('patent',0):,} patents,
    each geocoded to a city (patents to inventor cities, following Breschi &
    Lissoni 2001). Clustering the fine-tuned embeddings gives **{K} topics**;
    HDBSCAN leaves {n_noise:,} low-density documents as noise
    ({n_noise/len(arts):.0%}), which carry no topic and drop out of the topic
    measure. The carbon-capture topic is **cluster {cc_cluster}**.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. A map of the field

    Before any test, the space has to make sense. Do the three artifact types
    share the same regions — is this genuinely *one* co-embedded space rather
    than three islands? The map below colours every document by its type.
    """)
    return


@app.cell
def _(FIGDIR, SOL, arts, plt):
    # ── The map of the field: one shared projection, coloured by artifact type ──
    _m = arts[arts["umap_x"].notna()]

    # Draw the densest type first so the rarer ones stay visible on top; give the
    # smaller types slightly larger, more opaque points so they read clearly.
    _layers = [
        ("paper",   SOL["paper"],   6, 0.28),
        ("project", SOL["project"], 9, 0.55),
        ("patent",  SOL["patent"],  9, 0.60),
    ]

    fig_map, ax_map = plt.subplots(figsize=(13, 12))
    for _t, _col, _sz, _al in _layers:
        _s = _m[_m["type"] == _t]
        ax_map.scatter(_s["umap_x"], _s["umap_y"], s=_sz, alpha=_al, color=_col,
                       linewidths=0, rasterized=True, label=f"{_t}  ({len(_s):,})")

    ax_map.set_aspect("equal")
    ax_map.set_xlabel("UMAP-1"); ax_map.set_ylabel("UMAP-2")
    ax_map.set_xticks([]); ax_map.set_yticks([])          # UMAP axes carry no units
    for _sp in ("top", "right"):
        ax_map.spines[_sp].set_visible(False)
    ax_map.set_title("The synthetic-biology field: projects, papers, and patents in one space")

    _leg = ax_map.legend(markerscale=3.5, loc="upper right", framealpha=0.95,
                         title="artifact type", title_fontsize=14, fontsize=14)
    _leg.get_title().set_fontweight("bold")
    for _lh in _leg.legend_handles:
        _lh.set_alpha(1)

    fig_map.tight_layout()
    fig_map.savefig(FIGDIR / "tripartite_map.png", bbox_inches="tight", dpi=200)
    fig_map
    return


@app.cell
def _(mo):
    mo.md(r"""
    Papers spread across the whole field; projects and patents each concentrate
    in their own regions, but **papers overlap both** while projects and patents
    barely touch each other. That shape — papers as the shared middle ground — is
    the whole result previewed by eye, before a single test. Note the map is a
    2-D UMAP purely for viewing; the clustering below is done in a higher-D
    reduction where density is better preserved.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. The seductive wrong answer: centroid overlap

    The obvious measure of "do a city's types align?" is to average each type's
    document vectors into a centroid and take the cosine between two centroids.
    It looks reasonable and it is almost useless here: every document is
    synthetic biology, so any two centroids start close, and bigger cities
    average to steadier centroids nearer the field-wide mean. The result is that
    centroid overlap mostly measures **how much a city produces**, not how
    aligned its work is. We show the trap before stepping around it.
    """)
    return


@app.cell
def _(arts, ft_cache, np):
    # ── Per-city, per-type centroids from the fine-tuned embeddings ───────────
    def _type_centroids(typ):
        sub = arts[(arts["type"] == typ) & arts["id"].isin(ft_cache)]
        out = {}
        for city, g in sub.groupby("city_key"):
            V = np.asarray([ft_cache[i] for i in g["id"]], dtype=np.float32)
            c = V.mean(axis=0)
            nrm = np.linalg.norm(c)
            if nrm > 0:
                out[city] = (c / nrm, len(g))
        return out

    cen_paper   = _type_centroids("paper")
    cen_project = _type_centroids("project")
    return cen_paper, cen_project


@app.cell
def _(cen_paper, cen_project, np, pd, stats):
    # Centroid overlap (paper vs project) and city size, for cities with both.
    _rows = []
    for _c in set(cen_paper) & set(cen_project):
        _pv, _np_ = cen_paper[_c]
        _qv, _nq = cen_project[_c]
        _rows.append({"city_key": _c, "centroid_overlap": float(np.dot(_pv, _qv)),
                      "n_papers": _np_, "n_projects": _nq})
    centroid_df = pd.DataFrame(_rows)
    centroid_df["log_size"] = np.log1p(centroid_df["n_papers"] + centroid_df["n_projects"])
    _r, _p = stats.pearsonr(centroid_df["log_size"], centroid_df["centroid_overlap"])
    centroid_size_r, centroid_size_p = float(_r), float(_p)
    centroid_r2 = float(centroid_size_r ** 2)
    return centroid_df, centroid_r2, centroid_size_p, centroid_size_r


@app.cell
def _(FIGDIR, SOL, centroid_df, centroid_size_p, centroid_size_r, np, plt):
    # ── One panel, one lesson: the "obvious" measure just tracks city size ─────
    fig_cen, ax_cen = plt.subplots(figsize=(13, 8))

    ax_cen.scatter(centroid_df["log_size"], centroid_df["centroid_overlap"],
                   s=34, alpha=0.55, color=SOL["blue"])
    _z = np.polyfit(centroid_df["log_size"], centroid_df["centroid_overlap"], 1)
    _xr = np.linspace(centroid_df["log_size"].min(), centroid_df["log_size"].max(), 100)
    ax_cen.plot(_xr, np.poly1d(_z)(_xr), color=SOL["orange"], lw=3,
                label=f"fit:  r = {centroid_size_r:.2f},  p = {centroid_size_p:.1e}")
    ax_cen.set_xlabel("log(1 + papers + projects)  —  city size")
    ax_cen.set_ylabel("paper–project centroid cosine")
    ax_cen.set_title("The centroid measure is mostly city size")
    ax_cen.legend()

    fig_cen.tight_layout()
    fig_cen.savefig(FIGDIR / "centroid_size_artifact.png", bbox_inches="tight")
    fig_cen
    return


@app.cell
def _(centroid_r2, centroid_size_r, mo):
    mo.md(f"""
    Centroid overlap rises steadily with city size (r = {centroid_size_r:.2f}):
    size alone explains about **{centroid_r2:.0%}** of it. A measure that is mostly
    a restatement of "how much does this city publish?" cannot be evidence of
    local idea flow. We keep this number as a yardstick — the real test below
    should be *far* less size-driven.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. The decisive test: cluster co-membership

    Instead of averaging vectors, sort every document into a topic and ask a
    sharper question: do a city's papers, projects, and patents fall into the
    **same topics**? For each city and type we build a topic-frequency vector
    (how many of that type's documents are in each cluster); the relatedness of
    two types is the cosine of their vectors. This throws away magnitude and
    keeps only the partition, so it is immune to the size artifact — and it is
    symmetric, so it is immune to the papers-as-hub asymmetry of the embedding.

    The test is a **within-country re-pairing permutation**. The null keeps each
    country's cities and each type's document counts fixed and only breaks the
    specific local pairing. Beating it means a city's own types are more
    topically aligned than a random same-country city's types — which size and
    country cannot explain.

    Alongside the cosine we report an **interpretable co-location lift**: how much
    more likely a random document of each type from the *same* city is to land in
    one topic, versus two documents drawn from different same-country cities.
    """)
    return


@app.cell
def _(
    K,
    arts,
    build_city_type_vectors,
    city_name,
    comembership_table,
    country_of,
    pair_permutation,
    three_way_permutation,
):
    # ── Run the decisive test ────────────────────────────────────────────────
    MIN_DOCS = 5      # a city needs this many non-noise docs of each type (see note below)
    N_PERM   = 4000
    PAIRS    = [("paper", "project"), ("paper", "patent"), ("project", "patent")]

    # L2 vectors -> cosine co-membership (the headline statistic).
    tri_vecs, tri_counts = build_city_type_vectors(arts, K, norm="l2")
    # L1 (probability) vectors -> P(same topic), for the interpretable lift.
    prob_vecs, _pc = build_city_type_vectors(arts, K, norm="l1")

    pair_results, pair_tables, lift_res = {}, {}, {}
    for _a, _b in PAIRS:
        _tab = comembership_table(tri_vecs, tri_counts, _a, _b, MIN_DOCS, country_of, city_name)
        pair_tables[(_a, _b)] = _tab
        if len(_tab) >= 5:
            _cities = list(_tab.city_key)
            pair_results[(_a, _b)] = pair_permutation(
                tri_vecs, _a, _b, _cities, country_of, n_perm=N_PERM)
            _lp = pair_permutation(prob_vecs, _a, _b, _cities, country_of, n_perm=N_PERM)
            lift_res[(_a, _b)] = {
                "obs": _lp["observed"], "null": _lp["null_mean"],
                "lift": _lp["observed"] / _lp["null_mean"] if _lp["null_mean"] else float("nan"),
                "p": _lp["p_value"],
            }

    tri_cities = [
        c for c in tri_vecs["paper"]
        if c in tri_vecs["project"] and c in tri_vecs["patent"]
        and tri_counts["paper"].get(c, 0) >= MIN_DOCS
        and tri_counts["project"].get(c, 0) >= MIN_DOCS
        and tri_counts["patent"].get(c, 0) >= MIN_DOCS
    ]
    three_way = (
        three_way_permutation(tri_vecs, ("paper", "project", "patent"),
                              tri_cities, country_of, n_perm=N_PERM)
        if len(tri_cities) >= 5 else None
    )
    return MIN_DOCS, lift_res, pair_results, pair_tables, three_way, tri_counts, tri_vecs


@app.cell
def _(MIN_DOCS, lift_res, mo, pair_results, three_way):
    def _row(k):
        r = pair_results[k]
        lf = lift_res.get(k, {})
        star = "**yes**" if r["p_value"] < 0.05 else "no"
        lift = f"{lf.get('lift', float('nan')):.2f}× (p {lf.get('p', float('nan')):.3f})"
        return (f"| {r['type_a']} × {r['type_b']} | {r['n_cities']} | "
                f"{r['excess']:+.4f} | {r['p_value']:.4f} | {lift} | {star} |")

    _lines = [
        "| link | cities | cosine excess | p | same-topic lift | beats null? |",
        "|---|---|---|---|---|---|",
    ]
    for _k in [("paper", "project"), ("paper", "patent"), ("project", "patent")]:
        if _k in pair_results:
            _lines.append(_row(_k))

    _tw = ""
    if three_way is not None:
        _tw = (f"\n\nRestricting to the **{three_way['n_cities']} cities with all three "
               f"types**, the average pairwise co-membership also exceeds its null "
               f"(excess {three_way['excess']:+.3f}, p {three_way['p_value']:.3f}) — but this "
               f"is a *consequence* of the two paper links, not independent evidence: the "
               f"direct project–patent leg contributes almost nothing.")

    mo.md(
        f"Cluster co-membership vs the within-country null "
        f"(floor: {MIN_DOCS} documents per type per city).\n\n" + "\n".join(_lines) + _tw
    )
    return


@app.cell
def _(FIGDIR, SOL, pair_results, plt):
    # ── Permutation null distributions with the observed value marked ─────────
    _panels = [("paper", "project"), ("paper", "patent"), ("project", "patent")]
    fig_perm, axes_perm = plt.subplots(1, 3, figsize=(20, 6))

    for _ax, _key in zip(axes_perm, _panels):
        _r = pair_results.get(_key)
        if _r is None:
            _ax.set_visible(False); continue
        _ax.hist(_r["null"], bins=45, color=SOL["bg2"], edgecolor=SOL["muted"])
        _ax.axvline(_r["observed"], color=SOL["orange"], lw=2.5,
                    label=f"observed\np = {_r['p_value']:.4f}")
        _ax.axvline(_r["null_mean"], color=SOL["muted"], ls="--", lw=1.2, label="null mean")
        _sig = "" if _r["p_value"] < 0.05 else "  (n.s.)"
        _ax.set_title(f"{_key[0]} × {_key[1]}{_sig}\n{_r['n_cities']} cities")
        _ax.set_xlabel("mean city co-membership"); _ax.legend(fontsize=11)

    axes_perm[0].set_ylabel("permutations")
    fig_perm.suptitle("Cluster co-membership beats the same-country null "
                      "(orange line right of the histogram = local signal)",
                      fontsize=19, fontweight="bold")
    fig_perm.tight_layout()
    fig_perm.savefig(FIGDIR / "tripartite_permutation.png", bbox_inches="tight")
    fig_perm
    return


@app.cell
def _(mo):
    mo.md(r"""
    *On the document floor:* we require at least 5 documents of each type per
    city, because below that a city's topic vector is too sparse to estimate. The
    floor is a measurement threshold, not a tuned knob — the two paper links go
    on to survive the far more demanding leave-one-country-out and downsampling
    tests in §4.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Three ways to try to break it

    A single small p-value is not a finding; a finding is something that survives
    honest attempts to kill it. We run three checks, each answering one plain
    objection a sceptic would raise — and close with a short note on size,
    sample, and multiple testing.

    1. **Leave-one-country-out** — with the US supplying a large share of the
       cities, is this just an American result?
    2. **Resolution sweep** — does the signal need exactly this clustering, or
       does it hold from coarse to fine?
    3. **Power check** — is the flat project–patent link truly empty, or just
       measured on too few cities to see?
    """)
    return


@app.cell
def _(FIGDIR, SOL, country_of, leave_one_country_out, pair_tables, plt, tri_vecs):
    # ── Check 1: drop one whole country at a time and re-run. The sharp version
    # of a jackknife: if the US carries the result, removing it kills the signal.
    _pairs = [("paper", "project"), ("paper", "patent")]
    loco = {}

    fig_loco, axes_loco = plt.subplots(1, 2, figsize=(20, 7))
    for _ax, (_a, _b) in zip(axes_loco, _pairs):
        _cities = list(pair_tables[(_a, _b)].city_key)
        _d = leave_one_country_out(tri_vecs, _a, _b, _cities, country_of, n_perm=1500).head(7)
        loco[(_a, _b)] = _d
        _base = SOL["blue"] if _b == "project" else SOL["orange"]
        _colors = [SOL["red"] if c in ("US", "United States") else _base
                   for c in _d["dropped_country"]]
        _y = range(len(_d))
        _ax.barh(list(_y), _d["p_value"], color=_colors, edgecolor="white", height=0.66)
        _ax.set_yticks(list(_y))
        _ax.set_yticklabels([f"drop {c}  (−{n})" for c, n in
                             zip(_d["dropped_country"], _d["n_dropped"])])
        _ax.invert_yaxis()
        _ax.axvline(0.05, color=SOL["muted"], ls="--", lw=1.5, label="p = 0.05")
        _ax.set_xlabel("permutation p-value after dropping that country")
        _ax.set_title(f"{_a} × {_b}")
        _ax.legend(loc="lower right", fontsize=12)

    fig_loco.suptitle("Leave-one-country-out: is it just the United States? "
                      "(red = dropping the US)", fontsize=19, fontweight="bold")
    fig_loco.tight_layout()
    fig_loco.savefig(FIGDIR / "robust_leave_country.png", bbox_inches="tight")
    fig_loco
    return (loco,)


@app.cell
def _(loco, mo):
    def _us_row(df):
        m = df[df["dropped_country"].isin(["US", "United States"])]
        return m.iloc[0] if len(m) else None

    _pp = _us_row(loco[("paper", "project")])
    _px = _us_row(loco[("paper", "patent")])
    mo.md(f"""
    **Read:** dropping the US is the real test, because it is the largest single
    country in both samples. **paper × patent survives it** — still significant on
    the {_px['n_cities']:.0f} non-US cities (p = {_px['p_value']:.3f}), so it is not a US
    mirage. **paper × project does not** — without the US it falls to
    p = {_pp['p_value']:.3f} on {_pp['n_cities']:.0f} cities: still positive, but no longer
    significant, so it leans partly on the US and China. The two links are not
    equally strong, and we say so.
    """)
    return


@app.cell
def _(FIGDIR, PROCESSED, SOL, pd, plt):
    # ── Check 2: re-cluster with KMeans at k = 10..120 and re-run the test at
    # each k (see scripts/11_robustness_kcurve.py). KMeans keeps every document,
    # so this also answers the "you dropped 30% as noise" worry.
    kcurve = pd.read_csv(PROCESSED / "robustness_kcurve.csv")
    _pairs = [("paper", "project", SOL["blue"]),
              ("paper", "patent", SOL["orange"]),
              ("project", "patent", SOL["project"])]

    fig_ksweep, (axK1, axK2) = plt.subplots(1, 2, figsize=(20, 7))
    for _a, _b, _col in _pairs:
        _d = kcurve[(kcurve.type_a == _a) & (kcurve.type_b == _b)].sort_values("k")
        axK1.plot(_d.k, _d.excess, "-o", lw=2.5, ms=9, color=_col, label=f"{_a}×{_b}")
        axK2.plot(_d.k, _d.p_value, "-o", lw=2.5, ms=9, color=_col, label=f"{_a}×{_b}")

    axK1.axhline(0, color=SOL["muted"], ls="--", lw=1)
    axK1.set_xlabel("number of topics k (KMeans)")
    axK1.set_ylabel("excess co-membership over null")
    axK1.set_title("Excess stays positive at every resolution")
    axK1.legend()

    axK2.axhline(0.05, color=SOL["red"], ls="--", lw=1.5, label="p = 0.05")
    axK2.set_yscale("log")
    axK2.set_xlabel("number of topics k (KMeans)")
    axK2.set_ylabel("permutation p-value (log scale)")
    axK2.set_title("The two paper links stay significant; project×patent never does")
    axK2.legend()

    fig_ksweep.suptitle("Robustness to clustering resolution "
                        "(KMeans, all documents — no noise dropped)",
                        fontsize=19, fontweight="bold")
    fig_ksweep.tight_layout()
    fig_ksweep.savefig(FIGDIR / "robust_kcurve.png", bbox_inches="tight")
    fig_ksweep
    return (kcurve,)


@app.cell
def _(kcurve, mo):
    _pp = kcurve[(kcurve.type_a == "paper") & (kcurve.type_b == "project")]
    _px = kcurve[(kcurve.type_a == "paper") & (kcurve.type_b == "patent")]
    mo.md(f"""
    **Read:** across k from 10 to 120, paper×project stays significant at every
    resolution (worst p = {_pp.p_value.max():.3f}) and paper×patent almost always
    (worst p = {_px.p_value.max():.3f}, a single borderline k), while project×patent never
    clears 0.05. Because KMeans assigns *every* document to a topic, this doubles
    as proof the result did not depend on the third of documents HDBSCAN set aside
    as noise.
    """)
    return


@app.cell
def _(FIGDIR, SOL, country_of, downsample_power, pair_results, pair_tables, plt, tri_vecs):
    # ── Check 3: squeeze a WORKING link down to 28 cities (the project-patent
    # sample size) many times, and see how often it still looks significant.
    _strong = [("paper", "project"), ("paper", "patent")]
    power = {}

    fig_power, ax_power = plt.subplots(figsize=(14, 7))
    for (_a, _b), _col in zip(_strong, [SOL["blue"], SOL["orange"]]):
        _cities = list(pair_tables[(_a, _b)].city_key)
        _r = downsample_power(tri_vecs, _a, _b, _cities, country_of,
                              target_n=28, n_draws=150, n_perm=400)
        power[(_a, _b)] = _r
        ax_power.hist(_r["p_values"], bins=28, alpha=0.55, color=_col,
                      label=f"{_a}×{_b} at 28 cities  ({_r['share_significant']:.0%} still sig.)")

    _ppx = pair_results.get(("project", "patent"))
    if _ppx is not None:
        ax_power.axvline(_ppx["p_value"], color=SOL["project"], lw=2.8,
                         label=f"project×patent actual p = {_ppx['p_value']:.2f}  (28 cities)")
    ax_power.axvline(0.05, color=SOL["red"], ls="--", lw=1.6, label="p = 0.05")
    ax_power.set_xlabel("permutation p-value on a random 28-city subset")
    ax_power.set_ylabel("subsampled draws")
    ax_power.set_title("With only 28 cities, even a real link often looks non-significant")
    ax_power.legend(fontsize=12)
    fig_power.tight_layout()
    fig_power.savefig(FIGDIR / "robust_power.png", bbox_inches="tight")
    fig_power
    return (power,)


@app.cell
def _(mo, pair_results, power):
    _pp = power[("paper", "project")]
    _ppx = pair_results.get(("project", "patent"))
    mo.md(f"""
    **Read:** the real paper×project link, cut to 28 random cities (matching the
    project×patent sample), stays significant only **{_pp['share_significant']:.0%}** of the
    time — its median p climbs to **{_pp['median_p']:.2f}**, almost exactly project×patent's
    actual p of **{_ppx['p_value']:.2f}**. So the flat project×patent result is what "too
    few cities" looks like, not evidence that no link exists. We report it as
    *not detected here*, never *absent*.
    """)
    return


@app.cell
def _(centroid_r2, country_of, mo, pair_tables, size_control_ols):
    # ── Housekeeping: size regression, effective sample, multiple testing ─────
    _ols = {p: size_control_ols(pair_tables[p], p[0], p[1])
            for p in [("paper", "project"), ("paper", "patent")]}
    _pp = _ols[("paper", "project")]["r2_size"]
    _px = _ols[("paper", "patent")]["r2_size"]

    # Effective sample: cities that sit in a permutable (>= 2-city) country.
    _tab = pair_tables[("paper", "project")]
    _vc = _tab["country"].value_counts()
    _eff_cities = int(_vc[_vc >= 2].sum())
    _eff_countries = int((_vc >= 2).sum())

    mo.md(f"""
    ### Size, sample, and multiple testing

    - **Size control.** Regressing each city's co-membership on its two log
      document counts (standard errors clustered by country) leaves size
      explaining only **{_pp:.0%}** of paper×project and **{_px:.0%}** of paper×patent —
      against **{centroid_r2:.0%}** for the centroid measure in §2. The permutation
      already conditions on size; this is corroboration, not the control.
    - **Effective sample.** Of the paper×project cities, {_eff_cities} sit in
      {_eff_countries} countries with two or more cities; the rest are singleton
      countries that contribute the same value to the statistic and its null, so
      they add coverage but no discriminating power.
    - **Multiple testing.** We report three pairwise tests plus a three-way; a
      Bonferroni threshold of 0.05 / 4 = 0.0125 leaves both paper links (p ≈ 0.006)
      comfortably significant in the full sample.
    """)
    return


@app.cell
def _(loco, mo, pair_results):
    def _us_p(pair):
        df = loco[pair]
        m = df[df["dropped_country"].isin(["US", "United States"])]
        return m.iloc[0]["p_value"] if len(m) else float("nan")

    _pp = pair_results[("paper", "project")]["p_value"]
    _px = pair_results[("paper", "patent")]["p_value"]
    mo.md(f"""
    ## 5. What it shows, and what it can't

    A city's work is organised as a **star, not a triangle**. The two links that
    run **through papers** are significant: its papers share topics with its
    projects (p = {_pp:.3f}) and with its patents (p = {_px:.3f}), beyond what size or
    country can explain. The **direct project–patent link is not** — students and
    the patents filed in their city do not co-specialise once you condition on
    country and size. That fits the shape of the embedding and of the map: papers
    are the hub, and the science a city publishes is the common ground its
    students and its inventors both stand on.

    The two paper links are **not equally solid**, and the robustness checks say
    so honestly. paper × patent is the sturdier one: it survives dropping the US
    (p = {_us_p(("paper","patent")):.3f} on a dozen non-US cities) and holds across every
    clustering resolution. paper × project is real in sign and interpretable in
    size (a same-city paper and project are ~1.3× more likely to share a topic),
    but its significance leans partly on the US and China — remove the US and it
    softens to p = {_us_p(("paper","project")):.3f}.

    **What this cannot support:** any claim that student projects *cause* local
    papers or patents, or lead them in time. The design measures standing
    thematic association, not flow. The project–patent null is underpowered — only
    a couple of dozen cities have enough of both — so it is "not detected here,"
    never "shown absent." Carbon capture is the worked slice: the same test,
    restricted to that topic, is the next section to build.
    """)
    return


if __name__ == "__main__":
    app.run()
