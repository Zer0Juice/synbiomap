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

    return (
        FIGDIR,
        FT_CACHE,
        PROCESSED,
        build_city_type_vectors,
        comembership_table,
        load_cache,
        mpl,
        np,
        own_vs_other,
        pair_permutation,
        pd,
        plt,
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
    return MIN_DOCS, pair_results, three_way, tri_counts, tri_vecs


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
    ## 4. What it shows, and what it can't

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
