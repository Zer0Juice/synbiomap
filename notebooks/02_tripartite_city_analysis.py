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
    synthetic biology work on the same specific topics? This notebook is the
    core test of the thesis. It embeds all three artifact types in one
    fine-tuned semantic space, sorts them into topics, and asks whether a
    city's three kinds of work fall into the *same* topics more than chance —
    and more than city size can explain.

    The story runs in four moves:

    1. a sane map of the field,
    2. the seductive wrong answer (centroid overlap, which just measures size),
    3. the decisive test (cluster co-membership, with a permutation null),
    4. what it means, and what it can't.

    Embeddings come from SPECTER2 with our fine-tuned adapter; clusters come
    from `scripts/10_cluster_tripartite.py`. We speak of semantic relatedness
    and association throughout, never cause.
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
        own_vs_other, pair_permutation, three_way_permutation,
    )
    from src.analyze.robustness import (
        size_control_ols, leave_one_city_out, downsample_power,
    )

    return (
        FIGDIR,
        FT_CACHE,
        PROCESSED,
        build_city_type_vectors,
        comembership_table,
        downsample_power,
        leave_one_city_out,
        load_cache,
        mpl,
        np,
        own_vs_other,
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
    ## The data
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
    ## 1. A sane map of the field

    Before any test, the space has to be believable. Two things to see: the
    three artifact types share the same regions (they are genuinely
    co-embedded, not three separate islands), and the topics are coherent —
    the carbon-capture cluster sits where carbon-capture work should.
    """)
    return


@app.cell
def _(FIGDIR, SOL, arts, cc_cluster, plt):
    # ── The map: by artifact type (left) and by topic with carbon capture (right)
    m = arts[arts["umap_x"].notna()].copy()

    fig_map, (axL, axR) = plt.subplots(1, 2, figsize=(20, 9))

    # Left: colour by artifact type
    for t, col in [("paper", SOL["paper"]), ("patent", SOL["patent"]), ("project", SOL["project"])]:
        s = m[m["type"] == t]
        axL.scatter(s["umap_x"], s["umap_y"], s=5, alpha=0.35, color=col, label=f"{t} ({len(s):,})")
    axL.set_title("The three artifact types share the space")
    axL.set_xlabel("UMAP-1"); axL.set_ylabel("UMAP-2")
    leg = axL.legend(markerscale=3, loc="upper right", framealpha=0.9)
    for lh in leg.legend_handles:
        lh.set_alpha(1)

    # Right: colour by topic, carbon capture highlighted
    clu = m[m["cluster_label"] >= 0]
    axR.scatter(m[m["cluster_label"] < 0]["umap_x"], m[m["cluster_label"] < 0]["umap_y"],
                s=4, alpha=0.15, color=SOL["muted"])
    axR.scatter(clu["umap_x"], clu["umap_y"], s=5, alpha=0.4,
                c=clu["cluster_label"], cmap="twilight")
    cc = m[m["cluster_label"] == cc_cluster]
    axR.scatter(cc["umap_x"], cc["umap_y"], s=22, color=SOL["orange"],
                edgecolor="white", linewidth=0.3, label=f"carbon capture (cluster {cc_cluster})")
    axR.annotate("carbon capture", (cc["umap_x"].mean(), cc["umap_y"].mean()),
                 fontsize=15, fontweight="bold", color=SOL["orange"],
                 ha="center", va="center",
                 bbox=dict(boxstyle="round,pad=0.3", fc=SOL["bg"], ec=SOL["orange"]))
    axR.set_title("80 topics; the carbon-capture cluster in context")
    axR.set_xlabel("UMAP-1"); axR.set_ylabel("UMAP-2")
    axR.legend(markerscale=1.5, loc="upper right", framealpha=0.9)

    fig_map.tight_layout()
    fig_map.savefig(FIGDIR / "tripartite_map.png", bbox_inches="tight")
    fig_map
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. The seductive wrong answer: centroid overlap

    The obvious measure of "do a city's types align?" is to average each
    type's document vectors into a centroid and take the cosine between two
    centroids. It looks reasonable and it is almost useless here: every
    document is synthetic biology, so any two centroids start close, and
    bigger cities average to steadier centroids nearer the field-wide mean.
    The result is that centroid overlap mostly measures **how much a city
    produces**, not how aligned its work is. We show the trap before
    stepping around it.
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
    return centroid_df, centroid_size_p, centroid_size_r


@app.cell
def _(FIGDIR, SOL, centroid_df, centroid_size_p, centroid_size_r, np, plt):
    fig_cen, (axA, axB) = plt.subplots(1, 2, figsize=(18, 7))

    axA.hist(centroid_df["centroid_overlap"], bins=30, color=SOL["blue"], edgecolor="white")
    axA.axvline(centroid_df["centroid_overlap"].median(), color=SOL["orange"], lw=2,
                label=f"median = {centroid_df['centroid_overlap'].median():.3f}")
    axA.set_title("Centroid overlap is pinned near 1.0")
    axA.set_xlabel("paper–project centroid cosine"); axA.set_ylabel("cities")
    axA.legend()

    axB.scatter(centroid_df["log_size"], centroid_df["centroid_overlap"],
                s=28, alpha=0.5, color=SOL["blue"])
    _z = np.polyfit(centroid_df["log_size"], centroid_df["centroid_overlap"], 1)
    _xr = np.linspace(centroid_df["log_size"].min(), centroid_df["log_size"].max(), 100)
    axB.plot(_xr, np.poly1d(_z)(_xr), color=SOL["orange"], lw=2.5)
    axB.set_title(f"...and it just tracks city size  (r = {centroid_size_r:.2f}, p = {centroid_size_p:.1e})")
    axB.set_xlabel("log(1 + papers + projects)"); axB.set_ylabel("paper–project centroid cosine")

    fig_cen.tight_layout()
    fig_cen.savefig(FIGDIR / "centroid_size_artifact.png", bbox_inches="tight")
    fig_cen
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. The decisive test: cluster co-membership

    Instead of averaging vectors, sort every document into a topic and ask a
    sharper question: do a city's papers, projects, and patents fall into the
    **same topics**? For each city and type we build a topic-frequency vector
    (how many of that type's documents are in each cluster, L2-normalised);
    the relatedness of two types is the cosine of their vectors. This throws
    away magnitude and keeps only the partition, so it is immune to the size
    artifact — and it is symmetric, so it is immune to the papers-as-hub
    asymmetry of the embedding.

    The test is a **within-country re-pairing permutation**. The null keeps
    each country's cities and each type's document counts fixed and only
    breaks the specific local pairing. Beating it means a city's own types are
    more topically aligned than a random same-country city's types — which
    size and country cannot explain.
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
    MIN_DOCS = 5      # a city needs this many non-noise docs of each type (see floor curve)
    N_PERM   = 5000

    tri_vecs, tri_counts = build_city_type_vectors(arts, K)

    pair_results = {}
    pair_tables  = {}
    for _a, _b in [("paper", "project"), ("paper", "patent"), ("project", "patent")]:
        _tab = comembership_table(tri_vecs, tri_counts, _a, _b, MIN_DOCS, country_of, city_name)
        pair_tables[(_a, _b)] = _tab
        if len(_tab) >= 5:
            pair_results[(_a, _b)] = pair_permutation(
                tri_vecs, _a, _b, list(_tab.city_key), country_of, n_perm=N_PERM)

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
    return MIN_DOCS, pair_results, pair_tables, three_way, tri_counts, tri_vecs


@app.cell
def _(MIN_DOCS, mo, pair_results, three_way):
    def _fmt(r):
        star = "**significant**" if r["p_value"] < 0.05 else "not significant"
        return (f"| {r['type_a']} × {r['type_b']} | {r['n_cities']} | "
                f"{r['observed']:.4f} | {r['null_mean']:.4f} | {r['excess']:+.4f} | "
                f"{r['p_value']:.4f} | {star} |")

    _lines = [
        "| link | cities | observed | null | excess | p | |",
        "|---|---|---|---|---|---|---|",
    ]
    for _k in [("paper", "project"), ("paper", "patent"), ("project", "patent")]:
        if _k in pair_results:
            _lines.append(_fmt(pair_results[_k]))
    if three_way is not None:
        _t = three_way
        _star = "**significant**" if _t["p_value"] < 0.05 else "not significant"
        _lines.append(
            f"| three-way | {_t['n_cities']} | {_t['observed']:.4f} | {_t['null_mean']:.4f} | "
            f"{_t['excess']:+.4f} | {_t['p_value']:.4f} | {_star} |"
        )

    mo.md(
        f"Cluster co-membership vs the within-country null "
        f"(floor: {MIN_DOCS} documents per type per city).\n\n" + "\n".join(_lines)
    )
    return


@app.cell
def _(FIGDIR, SOL, pair_results, plt, three_way):
    # ── Permutation null distributions with the observed value marked ─────────
    _panels = [("paper", "project"), ("paper", "patent"), ("project", "patent")]
    fig_perm, axes_perm = plt.subplots(1, 4, figsize=(22, 5.5))

    for _ax, _key in zip(axes_perm[:3], _panels):
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

    _ax = axes_perm[3]
    if three_way is not None:
        _ax.hist(three_way["null"], bins=45, color=SOL["bg2"], edgecolor=SOL["muted"])
        _ax.axvline(three_way["observed"], color=SOL["orange"], lw=2.5,
                    label=f"observed\np = {three_way['p_value']:.4f}")
        _ax.axvline(three_way["null_mean"], color=SOL["muted"], ls="--", lw=1.2, label="null mean")
        _ax.set_title(f"three-way (exploratory)\n{three_way['n_cities']} cities")
        _ax.set_xlabel("mean city co-membership"); _ax.legend(fontsize=11)
    else:
        _ax.set_visible(False)

    axes_perm[0].set_ylabel("permutations")
    fig_perm.suptitle("Cluster co-membership beats the same-country null "
                      "(orange line right of the histogram = local signal)",
                      fontsize=19, fontweight="bold")
    fig_perm.tight_layout()
    fig_perm.savefig(FIGDIR / "tripartite_permutation.png", bbox_inches="tight")
    fig_perm
    return


@app.cell
def _(
    FIGDIR,
    SOL,
    city_name,
    comembership_table,
    country_of,
    own_vs_other,
    plt,
    tri_counts,
    tri_vecs,
):
    # ── Measurement-floor robustness: does the signal need dense cities? ──────
    fig_floor, ax_floor = plt.subplots(figsize=(14, 7))

    for _a, _b, _col in [("paper", "project", SOL["blue"]),
                         ("paper", "patent", SOL["orange"]),
                         ("project", "patent", SOL["project"])]:
        _mins, _fracs = [], []
        for _MIN in (3, 5, 8, 12, 20):
            _tab = comembership_table(tri_vecs, tri_counts, _a, _b, _MIN, country_of, city_name)
            if len(_tab) < 6:
                continue
            _d = own_vs_other(tri_vecs, _a, _b, list(_tab.city_key))
            _mins.append(_MIN); _fracs.append(float((_d > 0).mean()))
        ax_floor.plot(_mins, _fracs, "-o", lw=2.5, ms=9, color=_col, label=f"{_a} × {_b}")

    ax_floor.axhline(0.5, color=SOL["muted"], ls="--", lw=1)
    ax_floor.set_ylim(0, 1)
    ax_floor.set_xlabel("minimum documents per type per city")
    ax_floor.set_ylabel("share of cities: own > other")
    ax_floor.set_title("Local signal strengthens once cities are dense enough to measure")
    ax_floor.legend()
    fig_floor.tight_layout()
    fig_floor.savefig(FIGDIR / "tripartite_floor.png", bbox_inches="tight")
    fig_floor
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Four ways to try to break it

    A single small p-value is not a finding; a finding is something that
    survives honest attempts to kill it. We run four checks, each answering one
    plain-English objection a sceptic would raise:

    1. **Size control** — is co-membership just city size again, the way the
       centroid measure was?
    2. **Resolution sweep** — does the signal need exactly this clustering, or
       does it hold across many?
    3. **Leave-one-city-out** — is one big city (Boston, say) secretly carrying
       the whole result?
    4. **Power check** — is the flat project–patent link truly empty, or just
       measured on too few cities to see?
    """)
    return


@app.cell
def _(FIGDIR, SOL, centroid_size_r, pair_tables, plt, size_control_ols):
    # ── Check 1: is co-membership just size? Regress overlap on log doc counts.
    # If size explained it (as it did the centroid), R² is high; we want it low.
    _pairs = [("paper", "project"), ("paper", "patent"), ("project", "patent")]
    ols_res = {p: size_control_ols(pair_tables[p], p[0], p[1])
               for p in _pairs if len(pair_tables[p]) >= 8}
    centroid_r2 = float(centroid_size_r ** 2)

    _labels = ["centroid\noverlap"] + [f"{a}×{b}\nco-membership" for a, b in ols_res]
    _r2 = [centroid_r2] + [ols_res[p]["r2_size"] for p in ols_res]
    _cols = [SOL["red"]] + [SOL["blue"], SOL["orange"], SOL["project"]][:len(ols_res)]

    fig_size, ax_size = plt.subplots(figsize=(14, 7))
    _bars = ax_size.bar(_labels, _r2, color=_cols, edgecolor="white", width=0.62)
    for _bar, _v in zip(_bars, _r2):
        ax_size.text(_bar.get_x() + _bar.get_width() / 2, _v + 0.012, f"{_v:.0%}",
                     ha="center", va="bottom", fontsize=15, fontweight="bold")
    ax_size.axhline(0.15, color=SOL["muted"], ls="--", lw=1.3, label="15% reference")
    ax_size.set_ylim(0, max(0.72, max(_r2) + 0.1))
    ax_size.set_ylabel("share of variance explained by city size  (R²)")
    ax_size.set_title("Size explained the centroid measure — but barely touches co-membership")
    ax_size.legend()
    fig_size.tight_layout()
    fig_size.savefig(FIGDIR / "robust_size_control.png", bbox_inches="tight")
    fig_size
    return centroid_r2, ols_res


@app.cell
def _(centroid_r2, mo, ols_res):
    _pp = ols_res.get(("paper", "project"))
    _px = ols_res.get(("paper", "patent"))
    _rx = ols_res.get(("project", "patent"))
    mo.md(f"""
    **Read:** city size explains **{centroid_r2:.0%}** of the centroid measure — that measure
    really was mostly size. It explains only **{_pp['r2_size']:.0%}** of paper×project and
    **{_px['r2_size']:.0%}** of paper×patent co-membership, so the two significant links are about
    *which* topics a city shares, not *how much* it produces. Tellingly, size explains
    **{_rx['r2_size']:.0%}** of the (non-significant) project×patent overlap: what little there is,
    is mostly size — the opposite of a hidden real link.
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
    **Read:** across k from 10 to 120, paper×project stays significant at every resolution
    (worst p = {_pp.p_value.max():.3f}) and paper×patent almost always (worst p = {_px.p_value.max():.3f},
    a single borderline k), while project×patent never clears 0.05. Because KMeans assigns *every*
    document to a topic, this doubles as proof the result did not depend on the third of documents
    HDBSCAN set aside as noise.
    """)
    return


@app.cell
def _(FIGDIR, SOL, country_of, leave_one_city_out, np, pair_results,
      pair_tables, plt, tri_vecs):
    # ── Check 3: drop each city once and re-run. If no single city carries the
    # result, every leave-one-out p-value stays below 0.05.
    _pairs = [("paper", "project"), ("paper", "patent")]
    jack = {}
    _rng = np.random.default_rng(0)

    fig_jack, ax_jack = plt.subplots(figsize=(14, 7))
    for _i, (_a, _b) in enumerate(_pairs):
        _col = SOL["blue"] if _b == "project" else SOL["orange"]
        _cities = list(pair_tables[(_a, _b)].city_key)
        _j = leave_one_city_out(tri_vecs, _a, _b, _cities, country_of, n_perm=1000)
        jack[(_a, _b)] = _j
        _y = _i + (_rng.random(len(_j)) - 0.5) * 0.32
        ax_jack.scatter(_j.p_value, _y, s=45, alpha=0.55, color=_col)
        ax_jack.scatter([pair_results[(_a, _b)]["p_value"]], [_i], s=240, marker="D",
                        color=_col, edgecolor="white", linewidth=1.5, zorder=5,
                        label=f"{_a}×{_b}: full-sample p = {pair_results[(_a, _b)]['p_value']:.3f}")

    ax_jack.axvline(0.05, color=SOL["red"], ls="--", lw=1.6, label="p = 0.05")
    ax_jack.set_yticks([0, 1]); ax_jack.set_yticklabels(["paper×project", "paper×patent"])
    ax_jack.set_ylim(-0.5, 1.5)
    ax_jack.set_xlabel("permutation p-value with that one city removed")
    ax_jack.set_title("No single city carries the result: every leave-one-out stays significant")
    ax_jack.legend(loc="lower right", fontsize=12)
    fig_jack.tight_layout()
    fig_jack.savefig(FIGDIR / "robust_jackknife.png", bbox_inches="tight")
    fig_jack
    return (jack,)


@app.cell
def _(city_name, jack, mo):
    _lines = []
    for (_a, _b), _j in jack.items():
        _worst = _j.iloc[0]
        _lines.append(f"- **{_a}×{_b}:** worst case is dropping "
                      f"*{city_name.get(_worst['dropped'], _worst['dropped'])}* → p = "
                      f"{_worst['p_value']:.3f} (still significant).")
    mo.md("**Read:** removing any single city leaves both paper links significant.\n\n"
          + "\n".join(_lines))
    return


@app.cell
def _(FIGDIR, SOL, country_of, downsample_power, pair_results, pair_tables,
      plt, tri_vecs):
    # ── Check 4: squeeze a WORKING link down to 28 cities (the project-patent
    # sample size) many times, and see how often it still looks significant.
    _strong = [("paper", "project"), ("paper", "patent")]
    power = {}

    fig_power, ax_power = plt.subplots(figsize=(14, 7))
    for (_a, _b), _col in zip(_strong, [SOL["blue"], SOL["orange"]]):
        _cities = list(pair_tables[(_a, _b)].city_key)
        _r = downsample_power(tri_vecs, _a, _b, _cities, country_of,
                              target_n=28, n_draws=150, n_perm=500)
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
    **Read:** the real paper×project link, cut to 28 random cities (matching the project×patent
    sample), stays significant only **{_pp['share_significant']:.0%}** of the time — its median p
    climbs to **{_pp['median_p']:.2f}**, almost exactly project×patent's actual p of
    **{_ppx['p_value']:.2f}**. So the flat project×patent result is what "too few cities" looks like,
    not evidence that no link exists. We report it as *not detected here*, never *absent*.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. What it shows, and what it can't

    The two links that run **through papers** are significant: a city's papers
    and its projects share topics beyond chance, and so do its papers and its
    patents. The **direct project–patent link is not** — students and the
    patents filed in their city do not co-specialise once you condition on
    country and size. That fits the shape of the embedding: papers are the
    hub, and the science a city publishes is the common ground its students
    and its inventors both stand on. The three-way test, on the cities mature
    enough to have all three, is positive, but it leans on the two paper links
    rather than a genuine student–patent tie.

    What this cannot support: any claim that student projects *cause* local
    papers or patents, or lead them in time. The design measures standing
    thematic association, not flow. The project–patent null is also
    underpowered — only a couple of dozen cities have enough of both — so read
    it as "not detected here," not "shown absent." Carbon capture is the worked
    slice: the same test, restricted to that topic, is the next section to
    build.
    """)
    return


if __name__ == "__main__":
    app.run()
