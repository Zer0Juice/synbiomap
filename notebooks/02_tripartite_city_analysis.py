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

    Synthetic biology is the point where biology stops only reading life and
    starts writing it: students, academics, and companies now compose new
    biology from shared, standardized parts. This notebook asks one small,
    testable question about that shift. When a city's iGEM students, its academic
    labs, and its patent-filing inventors all work in synthetic biology, are they
    working on the same topics, or only in the same field?

    We place all three kinds of document in one semantic space with a fine-tuned
    SPECTER2 model, sort them into topics, and measure how often a city's three
    artifact types land in the same topics, against what chance alone would give.

    The argument runs in five steps:

    1. a map, so we trust the space before we test on it;
    2. the obvious measure, and why it only tracks city size;
    3. the real test: do a city's types share topics more than chance?
    4. three attempts to break that result;
    5. what it shows, and what it can't.

    Throughout we speak of relatedness and association, never cause.
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
        comembership_regression,
    )
    from src.analyze.crossmodal import city_part_type_props, mantel_test

    return (
        FIGDIR,
        FT_CACHE,
        PROCESSED,
        build_city_type_vectors,
        city_part_type_props,
        comembership_regression,
        comembership_table,
        downsample_power,
        leave_one_country_out,
        load_cache,
        mantel_test,
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
    # ── Publication-ready white theme ────────────────────────────────────────
    from matplotlib.colors import LinearSegmentedColormap

    SOL = {
        "bg": "#ffffff", "bg2": "#f0f0f0", "muted": "#888888", "text": "#222222",
        "paper": "#268bd2", "project": "#2aa198", "patent": "#cb4b16",
        "blue": "#268bd2", "cyan": "#2aa198", "orange": "#cb4b16",
        "yellow": "#b58900", "red": "#dc322f", "violet": "#6c71c4", "green": "#859900",
    }
    sol_div = LinearSegmentedColormap.from_list("sol_div", [SOL["orange"], "#ffffff", SOL["blue"]])

    mpl.rcParams.update({
        "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff",
        "axes.edgecolor": SOL["muted"], "axes.labelcolor": SOL["text"],
        "xtick.color": SOL["text"], "ytick.color": SOL["text"], "text.color": SOL["text"],
        "grid.color": "#dddddd", "grid.linestyle": "--", "grid.alpha": 0.8,
        "savefig.facecolor": "#ffffff", "savefig.dpi": 200,
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
def _(PROCESSED, pd):
    # ── The human-reviewed topic labels (scripts/12_label_clusters.py) ────────
    labels_df = pd.read_csv(PROCESSED / "cluster_labels.csv")
    label_of = dict(zip(labels_df["cluster"].astype(int), labels_df["label"].astype(str)))
    return label_of, labels_df


@app.cell
def _(K, arts, cc_cluster, label_of, mo, n_noise, type_counts):
    mo.md(f"""
    The corpus is {len(arts):,} documents: {type_counts.get('paper',0):,} papers,
    {type_counts.get('project',0):,} iGEM projects, and {type_counts.get('patent',0):,}
    patents, each geocoded to a city. Patents go to the cities of their inventors,
    not their owners, following Breschi and Lissoni (2001).

    Clustering the fine-tuned embeddings sorts the documents into {K} topics.
    HDBSCAN, the clustering method, leaves {n_noise:,} low-density documents
    ({n_noise/len(arts):.0%}) unassigned; they carry no topic and sit out the topic
    measure. The carbon-capture case study lives in cluster {cc_cluster},
    "{label_of.get(cc_cluster, '')}".
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. A map of the field

    Before any test, look at the space. Every document is a point, placed by a
    fine-tuned SPECTER2 model that reads its title and abstract and turns the text
    into 768 numbers. Documents about similar work end up with similar numbers,
    and so land near each other. To draw that 768-dimensional space on a page,
    UMAP flattens it to two dimensions while trying to keep near things near. The
    axes carry no units; only closeness means anything.

    Two things to check by eye. Do the three artifact types share the same
    regions, so this is one space and not three islands? And do the neighbourhoods
    hold together as real topics?
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
    Papers spread across the whole field. Projects and patents each gather in
    their own areas, and here is the shape the rest of the notebook keeps meeting:
    the papers sit inside both the project regions and the patent regions, while
    projects and patents rarely touch. The papers are the shared ground. We will
    test that impression, but you can already see it.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### The neighbourhoods have names

    The same map, now with the topics labelled. We clustered the documents into
    topics, then named each topic from its most central papers and its most
    distinctive words (`scripts/12_label_clusters.py`), and a human checked the
    result. The largest topics are written at their centres; carbon capture is in
    orange.
    """)
    return


@app.cell
def _(FIGDIR, SOL, arts, cc_cluster, label_of, plt):
    # ── The topic map: same UMAP, coloured by cluster, largest topics named ────
    _m = arts[arts["umap_x"].notna() & (arts["cluster_label"] >= 0)]
    _noise = arts[arts["umap_x"].notna() & (arts["cluster_label"] < 0)]

    fig_topics, ax_top = plt.subplots(figsize=(16, 14))
    ax_top.scatter(_noise["umap_x"], _noise["umap_y"], s=4, alpha=0.05,
                   color=SOL["muted"], rasterized=True)
    ax_top.scatter(_m["umap_x"], _m["umap_y"], s=5, alpha=0.30,
                   c=_m["cluster_label"], cmap="twilight", rasterized=True)
    _cc = _m[_m["cluster_label"] == cc_cluster]
    ax_top.scatter(_cc["umap_x"], _cc["umap_y"], s=11, alpha=0.75,
                   color=SOL["orange"], rasterized=True)

    # Name the 20 largest topics, plus carbon capture, at each topic's median point.
    _to_label = list(_m["cluster_label"].value_counts().head(20).index)
    if cc_cluster not in _to_label:
        _to_label.append(cc_cluster)
    for _c in _to_label:
        _g = _m[_m["cluster_label"] == _c]
        _is_cc = _c == cc_cluster
        ax_top.annotate(
            label_of.get(_c, str(_c)), (_g["umap_x"].median(), _g["umap_y"].median()),
            fontsize=12 if _is_cc else 10.5, fontweight="bold", ha="center", va="center",
            color=SOL["orange"] if _is_cc else SOL["text"],
            bbox=dict(boxstyle="round,pad=0.25", fc=SOL["bg"],
                      ec=SOL["orange"] if _is_cc else SOL["muted"], alpha=0.85),
        )

    ax_top.set_aspect("equal")
    ax_top.set_xlabel("UMAP-1"); ax_top.set_ylabel("UMAP-2")
    ax_top.set_xticks([]); ax_top.set_yticks([])
    for _sp in ("top", "right"):
        ax_top.spines[_sp].set_visible(False)
    ax_top.set_title("The topics of synthetic biology (largest topics named; carbon capture in orange)")

    fig_topics.tight_layout()
    fig_topics.savefig(FIGDIR / "tripartite_topic_map.png", bbox_inches="tight", dpi=200)
    fig_topics
    return


@app.cell
def _(mo):
    mo.md(r"""
    The map reads like a field guide. Genome editing, metabolic engineering,
    biosensors, gene circuits, and plant engineering each hold their own
    territory. The carbon-capture patch is cyanobacterial chassis work:
    photosynthetic microbes engineered to fix carbon. For this project that patch
    is the point of the whole exercise, the proof that the same tools which
    reshaped the planet by accident might be turned, on purpose, to repair it.
    """)
    return


@app.cell
def _(labels_df, mo):
    # ── The topics as a table, largest first, split by artifact type ──────────
    _d = labels_df.sort_values("n_docs", ascending=False).head(18)
    _lines = ["| topic | papers | projects | patents | total |",
              "|---|--:|--:|--:|--:|"]
    for _, _r in _d.iterrows():
        _star = " (cc)" if str(_r["is_carbon_capture"]).lower() in ("true", "1") else ""
        _lines.append(f"| {_r['label']}{_star} | {int(_r['n_paper'])} | "
                      f"{int(_r['n_project'])} | {int(_r['n_patent'])} | {int(_r['n_docs'])} |")
    mo.md(
        "Read down the type columns and the shape returns. Some topics are almost "
        "all papers, the academic core of the field. Some are mostly student "
        "projects. A few are patent-heavy. No large topic is a single type, and "
        "the paper column is never empty. Here are the 18 largest topics; (cc) "
        "marks carbon capture.\n\n" + "\n".join(_lines)
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. The obvious measure, and why it fails

    Start with the natural idea. To ask whether a city's papers and projects are
    alike, average each type into one vector and compare the two averages.

    Take every paper in a city and average their 768-number embeddings into a
    single centroid, the city's "average paper". Do the same for its projects.
    Scale both to length one and take the cosine of the angle between them: near
    1 if they point the same way, near 0 if they are unrelated.

    ```
    similarity = cosine(average paper vector, average project vector)
    ```

    It sounds reasonable. It barely works, for a reason worth seeing. Averaging
    many vectors pulls the result toward the middle of the whole field: the more
    documents you average, the more their differences cancel, and the closer the
    centroid sits to the field-wide mean. A city with 500 papers has a paper
    centroid near that global average, and its project centroid sits there too, so
    the two look alike whatever the city actually works on. The similarity ends up
    measuring how much a city produces, not what it produces.
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
    The plot bears it out. Across cities the centroid similarity climbs with size,
    with a Pearson correlation of r = {centroid_size_r:.2f}, and size alone accounts
    for about {centroid_r2:.0%} of it. (The correlation coefficient r runs from -1 to
    1; squaring it gives the share of the up-and-down variation that a straight line
    on size explains.) A measure that mostly restates "this city is large" cannot be
    evidence that a city's students and academics work on the same things. We keep
    the number as a yardstick and build a better test.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. The real test: shared topics

    The fix is to throw away magnitude and keep only topic. Do not average the
    vectors. Count the topics.

    Sort every document into one of the topics. For a city and an artifact type,
    count how many of that type's documents fall in each topic. That gives a list
    of counts, one per topic: the city's topic profile for its papers, and another
    for its projects. Scale each list to length one, so a large city and a small
    city are compared on the shape of their work, not its amount.

    The relatedness of two types in a city is the cosine of their two topic
    profiles, which after scaling is just the sum, over topics, of the two shares
    multiplied together:

    ```
    overlap = sum over topics of (paper share in topic) x (project share in topic)
    ```

    It is large when both types put their weight on the same topics and small when
    they favour different ones. Because it uses only the profile of topics and not
    how many documents made it, city size drops out. And because the cosine of A
    with B equals the cosine of B with A, it treats papers and projects
    symmetrically. That matters here, since the fine-tuning pulls patents and
    projects toward the papers they cite, and a one-sided measure would inherit
    that pull.

    One number on its own says nothing. A city's paper and project profiles might
    overlap simply because every document here is synthetic biology. So we compare
    the real overlap against a null: the same world with the local pairing broken.

    For every city we take its real overlap, then average across cities to get the
    observed value. Then, inside each country, we shuffle which project profile is
    matched to which paper profile, and average again. Shuffling within a country
    holds every country's set of cities and every document count exactly as they
    were; it breaks only the tie between a city's own papers and its own projects.
    Repeat the shuffle thousands of times to trace the range of overlaps that
    chance produces. The p-value is the share of shuffles that match or beat the
    real average.

    ```
    observed = average over cities of overlap(city)
    null     = the same average, after re-pairing papers and projects within each country
    p        = fraction of nulls at least as high as observed
    ```

    Beating that null means a city's own types share topics more than a random
    same-country city's types would, which neither size nor country can explain.

    Cosine is the right statistic but a hard one to feel, so we also read it as a
    probability. Scale each topic profile to sum to one instead of to length one,
    and it becomes a distribution: the chance a random document of that type lands
    in each topic. The dot product of two such distributions is then the chance
    that a random paper and a random project from the city fall in the same topic.
    Dividing the same-city chance by the shuffled chance gives a lift, how many
    times more likely two artifacts from one city are to meet in a topic than two
    drawn from different cities in the same country.
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
        beats = "yes" if r["p_value"] < 0.05 else "no"
        lift = f"{lf.get('lift', float('nan')):.2f}x (p {lf.get('p', float('nan')):.3f})"
        return (f"| {r['type_a']} × {r['type_b']} | {r['n_cities']} | "
                f"{r['excess']:+.4f} | {r['p_value']:.4f} | {lift} | {beats} |")

    _lines = [
        "| link | cities | cosine excess | p | same-topic lift | beats null? |",
        "|---|---|---|---|---|---|",
    ]
    for _k in [("paper", "project"), ("paper", "patent"), ("project", "patent")]:
        if _k in pair_results:
            _lines.append(_row(_k))

    _tw = ""
    if three_way is not None:
        _tw = (f"\n\nWith all three types present, on the {three_way['n_cities']} cities "
               f"that have enough of each, the average pairwise overlap also beats its null "
               f"(excess {three_way['excess']:+.3f}, p {three_way['p_value']:.3f}). This follows "
               f"from the two paper links rather than adding to them: the direct project–patent "
               f"leg carries almost none of it.")

    mo.md(
        f"Each row is one type pair. The excess is the observed average overlap minus "
        f"its within-country null; the lift reads the same effect as a probability. "
        f"A city needs at least {MIN_DOCS} documents of each type to enter a row.\n\n"
        + "\n".join(_lines) + _tw
    )
    return


@app.cell
def _(FIGDIR, SOL, pair_results, plt):
    # ── Permutation null distributions with the observed value marked ─────────
    _panels = [("paper", "project"), ("paper", "patent"), ("project", "patent")]
    fig_perm, axes_perm = plt.subplots(3, 1, figsize=(10, 15))

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
        _ax.set_xlabel("mean city co-membership")
        _ax.set_ylabel("permutations")
        _ax.legend(fontsize=11)

    fig_perm.suptitle("Real overlap against the same-country null "
                      "(orange line right of the grey histogram is local signal)",
                      fontsize=19, fontweight="bold")
    fig_perm.tight_layout()
    fig_perm.savefig(FIGDIR / "tripartite_permutation.png", bbox_inches="tight")
    fig_perm
    return


@app.cell
def _(mo):
    mo.md(r"""
    Each grey histogram is the range of overlaps the shuffle produces; the orange
    line is what the real pairing gives. For paper–project and paper–patent the
    real value sits to the right of almost every shuffle. For project–patent it
    sits in the middle of the pile, indistinguishable from chance.

    A note on the floor. A city enters a pair only if it has at least five
    documents of each type, because below that its topic profile is a handful of
    counts and too noisy to trust. This is a measurement threshold, not a dial we
    tuned for a result; the two paper links go on to survive the harder tests in
    section 4.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Three ways to try to break it

    A small p-value is a start, not a finding. A finding survives attempts to
    knock it down. Here are three, each aimed at a specific way the result could
    be an artifact rather than a real pattern.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Drop a whole country

    The within-country null already holds country fixed. But if one country
    supplies most of the cities, the shuffle mostly happens inside that country,
    and the result could be a story about one place wearing a global coat. The
    United States is the largest single source of cities here. So we remove one
    whole country at a time and run the test again on the rest. If the signal is
    real and spread out, no single removal should break it.
    """)
    return


@app.cell
def _(FIGDIR, SOL, country_of, leave_one_country_out, pair_tables, plt, tri_vecs):
    # ── Check 1: drop one whole country at a time and re-run. The sharp version
    # of a jackknife: if the US carries the result, removing it kills the signal.
    _pairs = [("paper", "project"), ("paper", "patent")]
    loco = {}

    fig_loco, axes_loco = plt.subplots(2, 1, figsize=(10, 12))
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
                      "(red bar is dropping the US)", fontsize=19, fontweight="bold")
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
    Dropping the US is the real test, since it is the largest single country in
    both samples. Paper–patent survives it: still significant on the {_px['n_cities']:.0f}
    non-US cities, at p = {_px['p_value']:.3f}. So that link is not an American mirage.
    Paper–project does not survive: without the US it falls to p = {_pp['p_value']:.3f} on
    {_pp['n_cities']:.0f} cities. It stays positive, but it leans partly on the US and
    China. The two links are not equally strong, and the notebook says so.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Change the number of topics

    The topics came from one clustering, at one setting. Maybe the result only
    holds there. So we redo the topics with a different method, KMeans, at sizes
    from 10 topics to 120, and run the whole test again at each size. KMeans also
    assigns every document to a topic, with none left out as noise, so this check
    does a second job: it shows the result does not depend on the third of
    documents HDBSCAN set aside.
    """)
    return


@app.cell
def _(FIGDIR, PROCESSED, SOL, pd, plt):
    # ── Check 2: re-cluster with KMeans at k = 10..120 and re-run the test at
    # each k (see scripts/11_robustness_kcurve.py).
    kcurve = pd.read_csv(PROCESSED / "robustness_kcurve.csv")
    _pairs = [("paper", "project", SOL["blue"]),
              ("paper", "patent", SOL["orange"]),
              ("project", "patent", SOL["project"])]

    fig_ksweep, (axK1, axK2) = plt.subplots(2, 1, figsize=(10, 12))
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

    fig_ksweep.suptitle("Robustness to the number of topics (KMeans, all documents kept)",
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
    From 10 topics to 120, paper–project stays significant at every size (its worst
    p is {_pp.p_value.max():.3f}), and paper–patent stays significant at all but one
    borderline size (worst p {_px.p_value.max():.3f}). Project–patent never clears 0.05.
    The result does not hinge on the one clustering we chose, and dropping no
    documents as noise changes nothing.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Starve the sample

    The direct project–patent link is measured on only 28 cities, and it came out
    null. Is there really nothing there, or are 28 cities too few to see it? To
    find out, take a link that does work, paper–project, and cut it down to 28
    random cities, again and again. If the working link also goes quiet at 28
    cities, then 28 cities simply cannot resolve an effect this size, and the
    project–patent null means "too little data", not "no link".
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
    The real paper–project link, cut to 28 random cities to match the
    project–patent sample, stays significant only {_pp['share_significant']:.0%} of the
    time. Its median p climbs to {_pp['median_p']:.2f}, almost exactly project–patent's
    actual p of {_ppx['p_value']:.2f}. So the flat project–patent result is what too few
    cities looks like, not proof that no link exists. We record it as undetected
    here, and leave it open.
    """)
    return


@app.cell
def _(centroid_r2, country_of, mo, pair_results, pair_tables, size_control_ols):
    # ── Housekeeping: size regression, effective sample, multiple testing ─────
    _ols = {p: size_control_ols(pair_tables[p], p[0], p[1])
            for p in [("paper", "project"), ("paper", "patent")]}
    _rp = _ols[("paper", "project")]["r2_size"]
    _rx = _ols[("paper", "patent")]["r2_size"]
    _pp = pair_results[("paper", "project")]["p_value"]
    _px = pair_results[("paper", "patent")]["p_value"]

    _tab = pair_tables[("paper", "project")]
    _vc = _tab["country"].value_counts()
    _eff_cities = int(_vc[_vc >= 2].sum())
    _eff_countries = int((_vc >= 2).sum())

    mo.md(f"""
    ### Size, sample, and multiple testing

    Three loose ends, stated plainly. First, size again. If we predict a city's
    overlap from its two document counts with a straight-line regression, and
    cluster the standard errors by country, size explains {_rp:.0%} of the
    paper–project overlap and {_rx:.0%} of the paper–patent overlap, against
    {centroid_r2:.0%} for the centroid measure in section 2. The permutation already
    holds size fixed; this is a second check, not the main one, and it agrees.

    Second, the real sample size. Of the paper–project cities, {_eff_cities} sit in
    {_eff_countries} countries that have two or more cities. The rest are lone
    cities in their country, which contribute the same value to the observed and
    the null, so they add coverage but no power to tell the two apart.

    Third, multiple tests. We ran three pairwise tests and a three-way one. A
    Bonferroni threshold, 0.05 divided by 4, is 0.0125; both paper links, at
    p = {_pp:.4f} and p = {_px:.4f}, clear it in the full sample.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### The same test as a regression

    The permutation is one way to ask the question. A regression is another, and if the
    two disagree that is worth knowing. So we lay the same numbers out as a table with
    one row per city pair: a city's own paper vector against every same-country city's
    project vector, its own against its own, and so on. The thing we regress on is a
    single indicator, same-city, one when the two vectors come from the same place and
    zero otherwise.

    Its coefficient is the local signal in plain sight. It says how much higher a city's
    own two types overlap than the mismatched same-country pairings, in the same cosine
    units the permutation reports as excess. Size on each side and country fixed effects
    ride along as controls, and the errors are clustered by city, since one city's vector
    turns up in many pairs. If that coefficient is positive and holds up, a city's own
    registers really do share topics more than the neighbours' do — the permutation's
    answer, reached by a road that breaks in different places.
    """)
    return


@app.cell
def _(FIGDIR, SOL, comembership_regression, country_of, pair_results,
      pair_tables, plt, tri_counts, tri_vecs):
    # ── The decisive test re-run as a regression ─────────────────────────────
    # One row per ordered city dyad (same country); DV = cosine co-membership,
    # key regressor = same-city dummy. See src/analyze/robustness.py.
    _pairs = [("paper", "project"), ("paper", "patent"), ("project", "patent")]
    reg_res = {}
    for _a, _b in _pairs:
        _tab = pair_tables[(_a, _b)]
        if len(_tab) >= 5:
            reg_res[(_a, _b)] = comembership_regression(
                tri_vecs, tri_counts, _a, _b, list(_tab.city_key), country_of)

    # ── Forest plot: same-city coefficient (95% CI); tick marks the perm excess ─
    _keys = [k for k in _pairs if k in reg_res]
    _cols = {("paper", "project"): SOL["blue"], ("paper", "patent"): SOL["cyan"],
             ("project", "patent"): SOL["orange"]}
    fig_reg, ax_reg = plt.subplots(figsize=(11, 5))
    for _i, _k in enumerate(_keys):
        _r = reg_res[_k]
        ax_reg.errorbar(_r["beta_same_city"], _i, xerr=1.96 * _r["se_same_city"],
                        fmt="o", ms=13, lw=2.5, color=_cols[_k],
                        ecolor=SOL["muted"], mec=SOL["text"], capsize=5, zorder=5)
        ax_reg.plot(pair_results[_k]["excess"], _i, marker="|", ms=24, mew=3,
                    color=SOL["text"], zorder=6)
    ax_reg.axvline(0, color=SOL["muted"], ls="--", lw=1.2)
    ax_reg.set_yticks(range(len(_keys)))
    ax_reg.set_yticklabels([f"{_a} × {_b}" for _a, _b in _keys])
    ax_reg.set_xlabel("same-city coefficient on cluster co-membership (95% CI); "
                      "tick = permutation excess")
    ax_reg.set_title("The same-city regression agrees with the permutation")
    ax_reg.invert_yaxis()
    fig_reg.tight_layout()
    fig_reg.savefig(FIGDIR / "tripartite_samecity_reg.png", bbox_inches="tight")
    fig_reg
    return (reg_res,)


@app.cell
def _(mo, pair_results, reg_res):
    _pairs = [("paper", "project"), ("paper", "patent"), ("project", "patent")]
    _lines = ["| link | cities | dyads | perm excess (p) | same-city β (p) |",
              "|---|---|---|---|---|"]
    for _k in _pairs:
        if _k not in reg_res:
            continue
        _r = reg_res[_k]
        _pm = pair_results[_k]
        _lines.append(f"| {_k[0]} × {_k[1]} | {_r['n_cities']} | {_r['n_dyads']} | "
                      f"{_pm['excess']:+.4f} ({_pm['p_value']:.4f}) | "
                      f"{_r['beta_same_city']:+.4f} ({_r['p_same_city']:.4f}) |")

    _pj = reg_res[("paper", "project")]
    _px = reg_res[("paper", "patent")]
    mo.md(
        "Each row is one type pair. The permutation excess and the same-city coefficient "
        "sit in the same cosine units and measure one thing two ways: how much more a "
        "city's own types overlap than the mismatched pairings.\n\n"
        + "\n".join(_lines) + "\n\n"
        f"The two agree. Both paper links stay positive and significant once the test "
        f"becomes a regression carrying size controls and country fixed effects "
        f"(same-city β {_pj['beta_same_city']:+.3f}, p {_pj['p_same_city']:.3f} for "
        f"paper × project; β {_px['beta_same_city']:+.3f}, p {_px['p_same_city']:.3f} for "
        f"paper × patent). The regression is the more cautious of the two, since its "
        f"standard errors lean on a few dozen city clusters rather than four thousand "
        f"shuffles, and the local signal survives anyway. The direct project × patent "
        f"link stays null under both, as it should. One honest limit: clustering by city "
        f"handles the dependence on one side of each pair, not both, so the permutation, "
        f"which respects it fully, stays the decisive test. This is a second opinion that "
        f"happens to agree."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Beyond the text: do the BioBrick parts agree?

    Every measure so far reads text. SPECTER2 sees titles and abstracts, and a
    fair worry is that we are testing the writing, not the work. BioBrick parts
    let us check from another angle. Each iGEM team registers physical DNA parts,
    and each part carries a functional type: a promoter, a coding sequence, a
    terminator, and so on. Those type labels come from the registry, not from any
    text the model read.

    A Mantel test asks whether two ways of measuring distance between the same
    cities agree. From the semantic side, build a city-by-city table of how far
    apart two cities' project topic profiles are. From the parts side, build
    another table of how far apart their part-type mixes are. The statistic is the
    correlation between the two tables, taken over every pair of cities.

    ```
    r = correlation( topic distances, part-type distances )   over all city pairs
    ```

    City-pair distances are not independent, so a plain p-value would lie. The
    Mantel test shuffles the city labels of one table, recomputes the correlation,
    and repeats, to see how often chance alone reaches the real value. If the parts
    and the topics line up beyond that shuffle, the semantic space has caught
    something the parts confirm from outside the text.
    """)
    return


@app.cell
def _(K, PROCESSED, arts, city_part_type_props, mantel_test, np, pd):
    # ── Part-type profiles vs project topic profiles, per city ────────────────
    _parts = pd.read_csv(PROCESSED / "parts.csv", low_memory=False)
    _proj = pd.read_csv(PROCESSED / "projects.csv", low_memory=False)
    _proj["city_key"] = _proj["city"].astype(str).str.strip().str.lower()
    _team_city = (_proj.dropna(subset=["team_id"]).drop_duplicates("team_id")
                  .set_index("team_id")["city_key"].to_dict())
    part_props = city_part_type_props(_parts, _team_city, min_parts=10)

    # Project topic proportions per city (>= 5 project documents).
    _pdoc = arts[(arts["type"] == "project") & (arts["cluster_label"] >= 0)]
    topic_props = {}
    for _c, _g in _pdoc.groupby("city_key"):
        if len(_g) >= 5:
            _v = np.zeros(K)
            for _k, _n in _g["cluster_label"].value_counts().items():
                _v[int(_k)] = _n
            topic_props[_c] = _v / _v.sum()

    mantel_cities = sorted(set(topic_props) & set(part_props.index))
    _part_vecs = {c: part_props.loc[c].to_numpy() for c in mantel_cities}
    mantel = mantel_test(topic_props, _part_vecs, mantel_cities, n_perm=2000)
    return (mantel,)


@app.cell
def _(FIGDIR, SOL, mantel, np, plt):
    # ── Left: the two distances rise together. Right: beats the shuffle null ──
    fig_mantel, (axM1, axM2) = plt.subplots(2, 1, figsize=(10, 12))

    axM1.hexbin(mantel["part_dist"], mantel["sem_dist"], gridsize=32,
                cmap="YlGnBu", mincnt=1)
    _z = np.polyfit(mantel["part_dist"], mantel["sem_dist"], 1)
    _xr = np.linspace(mantel["part_dist"].min(), mantel["part_dist"].max(), 100)
    axM1.plot(_xr, np.poly1d(_z)(_xr), color=SOL["orange"], lw=3,
              label=f"r = {mantel['r']:.3f}")
    axM1.set_xlabel("part-type distance between two cities")
    axM1.set_ylabel("project topic distance between two cities")
    axM1.set_title("Every dot is a pair of cities")
    axM1.legend()

    axM2.hist(mantel["null"], bins=40, color=SOL["bg2"], edgecolor=SOL["muted"])
    axM2.axvline(mantel["r"], color=SOL["orange"], lw=2.5,
                 label=f"observed r = {mantel['r']:.3f}\np = {mantel['p_value']:.4f}")
    axM2.axvline(mantel["null_mean"], color=SOL["muted"], ls="--", lw=1.2, label="null mean")
    axM2.set_xlabel("Mantel correlation under label shuffling")
    axM2.set_ylabel("permutations")
    axM2.set_title("The agreement beats the shuffle")
    axM2.legend(fontsize=12)

    fig_mantel.suptitle("Do the BioBrick parts agree with the semantic space?",
                        fontsize=19, fontweight="bold")
    fig_mantel.tight_layout()
    fig_mantel.savefig(FIGDIR / "mantel_parts_vs_topics.png", bbox_inches="tight")
    fig_mantel
    return


@app.cell
def _(mantel, mo):
    mo.md(f"""
    Over {mantel['n_cities']} cities the two distance tables correlate at
    r = {mantel['r']:.3f}, and the shuffle reaches that value only {mantel['p_value']:.4f}
    of the time. The agreement is modest but real: cities that build similar kinds
    of parts sit closer in the topic space too. The part types are functional
    labels the model never read, so this is a second signal, from outside the
    text, pointing the same way as the topics.
    """)
    return


@app.cell
def _(lift_res, loco, mo, pair_results):
    def _us_p(pair):
        df = loco[pair]
        m = df[df["dropped_country"].isin(["US", "United States"])]
        return m.iloc[0]["p_value"] if len(m) else float("nan")

    _pp = pair_results[("paper", "project")]["p_value"]
    _px = pair_results[("paper", "patent")]["p_value"]
    _lift = lift_res[("paper", "project")]["lift"]
    mo.md(f"""
    ## 6. What it shows, and what it can't

    A city's work is shaped like a star, not a triangle. The two links that run
    through papers are real: a city's papers share topics with its projects
    (p = {_pp:.3f}) and with its patents (p = {_px:.3f}), beyond what size or country
    can explain. The direct project–patent link is not: students and the patents
    filed in their city do not settle on the same topics once country and size are
    held fixed. This matches the map and the embedding. Papers are the hub, and
    the science a city publishes is the common ground its students and its
    inventors both stand on.

    The two paper links are not equally solid, and the checks say so. Paper–patent
    is the sturdier one: it survives dropping the US, on a dozen non-US cities
    (p = {_us_p(("paper","patent")):.3f}), and holds across every number of topics.
    Paper–project is real in sign and easy to read in size, a same-city paper and
    project are about {_lift:.1f} times more likely to share a topic than a
    same-country pair from different cities, but its significance leans on the US
    and China; remove the US and it softens to p = {_us_p(("paper","project")):.3f}.

    What this cannot show is direction. Nothing here says student projects cause a
    city's papers or patents, or come first in time. The test measures standing
    thematic overlap, not flow. The project–patent link stays undetected rather
    than shown absent, on only a couple of dozen cities. And carbon capture, the
    cyanobacterial-chassis topic where this project's hope lives, is the worked
    example the next section builds: the same test, narrowed to that one topic.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. Dynamic coupling: difference-in-differences and lead-lag

    Sections 1–6 measured standing topical overlap — do a city's three artifact
    types land in the same clusters across the full corpus? That is the structural
    question. Here we ask the temporal one: does activity in one type at time $t$
    co-move with activity in another type at time $t + k$, within the same city and
    the same topic?

    Two tests. First, a difference-in-differences panel regression using five-year
    period bins: for each pair (upstream, downstream), we regress the downstream
    type's cluster-share on the upstream type's cluster-share, absorbing city fixed
    effects and topic × period fixed effects by within-group demeaning
    (Frisch-Waugh). Standard errors are clustered by city. The coefficient $\beta$
    captures within-city, within-topic co-movement after removing each city's
    standing specialization and each topic's global trend.

    Second, a lead-lag profile: for each lag $k \in [-3, +3]$ years, we compare
    a city's annual cluster-frequency vector for the upstream type at year $t$ with
    the downstream type's vector at year $t + k$. A positive $k$ means the
    downstream artifact comes after the upstream one. Bootstrap 95% confidence
    intervals across city-year pairs. A permutation test (500 shuffles of project
    year labels within each city) checks whether any asymmetry in the profile is
    real.
    """)
    return


@app.cell
def _(arts, K, np, pd):
    # ── Section 7 data: annual cluster-frequency vectors ─────────────────────
    # One L2-normalised K-dimensional vector per (city_key, year, type).
    # Requires at least MIN_ANNUAL_DOCS non-noise documents of that type in that
    # city-year; below that threshold the vector is too sparse to be informative.
    MIN_ANNUAL_DOCS = 2

    _a = arts[arts["cluster_label"] >= 0].copy()

    def make_annual_vecs(df, type_name, min_docs=MIN_ANNUAL_DOCS):
        sub = df[df["type"] == type_name]
        out = {}
        for (ck, yr), grp in sub.groupby(["city_key", "year"]):
            if len(grp) < min_docs:
                continue
            counts = np.zeros(K)
            for lab, cnt in grp["cluster_label"].value_counts().items():
                counts[int(lab)] = cnt
            norm = np.linalg.norm(counts)
            if norm > 0:
                out[(ck, int(yr))] = counts / norm
        return out

    annual_vecs = {t: make_annual_vecs(_a, t) for t in ["project", "paper", "patent"]}

    # ── Five-year period cluster-share table (for DiD regression) ─────────────
    PERIOD_BINS   = [2003, 2008, 2013, 2018, 2024]
    PERIOD_LABELS = ["2004-08", "2009-13", "2014-18", "2019-24"]
    _a["period"] = pd.cut(_a["year"], bins=PERIOD_BINS, labels=PERIOD_LABELS)
    _a = _a.dropna(subset=["period"])

    def cluster_shares_long(df, type_name):
        sub = df[df["type"] == type_name]
        cnt = (sub.groupby(["city_key", "period", "cluster_label"])
                   .size().reset_index(name="count"))
        tot = cnt.groupby(["city_key", "period"])["count"].sum().reset_index(name="total")
        cnt = cnt.merge(tot, on=["city_key", "period"])
        cnt["share"] = cnt["count"] / cnt["total"]
        return cnt[["city_key", "period", "cluster_label", "share"]]

    shares = {t: cluster_shares_long(_a, t) for t in ["project", "paper", "patent"]}

    return annual_vecs, cluster_shares_long, shares


@app.cell
def _(shares, np, pd):
    import statsmodels.formula.api as smf

    # ── Tripartite DiD: cluster-share panel regression ────────────────────────
    # Y = downstream cluster share in city c, topic k, period t
    # X = upstream cluster share in same city, topic, period
    # FE: city (c) + topic × period (k,t) — absorbed by double demeaning
    # SE: clustered by city

    def run_did_pair(shares_a, shares_b):
        m = (shares_a.rename(columns={"share": "share_a"})
             .merge(shares_b.rename(columns={"share": "share_b"}),
                    on=["city_key", "period", "cluster_label"]))
        m["topic_period"] = (m["cluster_label"].astype(str) + "_"
                             + m["period"].astype(str))
        for col in ["share_a", "share_b"]:
            m[col] = m[col] - m.groupby("city_key")[col].transform("mean")
            m[col] = m[col] - m.groupby("topic_period")[col].transform("mean")
        m = m.dropna(subset=["share_a", "share_b"])
        mod = smf.ols("share_b ~ share_a", data=m).fit(
            cov_type="cluster", cov_kwds={"groups": m["city_key"]})
        return mod, m["city_key"].nunique(), len(m)

    _pairs = [
        ("project", "paper",   "project → paper"),
        ("paper",   "patent",  "paper → patent"),
        ("project", "patent",  "project → patent"),
    ]

    did_results = {}
    for _ta, _tb, _lbl in _pairs:
        _mod, _nc, _n = run_did_pair(shares[_ta], shares[_tb])
        did_results[(_ta, _tb)] = {
            "label": _lbl, "model": _mod,
            "beta": _mod.params["share_a"],
            "se":   _mod.bse["share_a"],
            "t":    _mod.tvalues["share_a"],
            "p":    _mod.pvalues["share_a"],
            "n_cities": _nc, "n_obs": _n,
        }
        _stars = ("***" if _mod.pvalues["share_a"] < 0.001 else
                  "**"  if _mod.pvalues["share_a"] < 0.01  else
                  "*"   if _mod.pvalues["share_a"] < 0.05  else "")
        print(f"{_lbl:25s}  β={_mod.params['share_a']:+.5f}  "
              f"t={_mod.tvalues['share_a']:+.2f}  "
              f"p={_mod.pvalues['share_a']:.4f}{_stars}  "
              f"N={_nc} cities")

    return (did_results,)


@app.cell
def _(FIGDIR, SOL, did_results, np, plt):
    # ── DiD coefficient plot ──────────────────────────────────────────────────
    _pair_order = [("project","paper"), ("paper","patent"), ("project","patent")]
    _colors = [SOL["project"], SOL["paper"], SOL["muted"]]
    _betas  = [did_results[p]["beta"]     for p in _pair_order]
    _ses    = [did_results[p]["se"]       for p in _pair_order]
    _pvals  = [did_results[p]["p"]        for p in _pair_order]
    _labels = [did_results[p]["label"]    for p in _pair_order]
    _ncity  = [did_results[p]["n_cities"] for p in _pair_order]

    fig_did, ax_did = plt.subplots(figsize=(10, 5))
    _y = np.arange(len(_pair_order))
    ax_did.barh(_y, _betas, xerr=_ses, color=_colors, capsize=8, height=0.5,
                edgecolor="white", error_kw={"linewidth": 2})
    ax_did.axvline(0, color=SOL["muted"], ls="--", lw=1.5)
    ax_did.set_yticks(_y)
    ax_did.set_yticklabels([f"{l}  (N={n})" for l, n in zip(_labels, _ncity)])
    for yi, (b, se, p) in enumerate(zip(_betas, _ses, _pvals)):
        stars = ("***" if p < 0.001 else "**" if p < 0.01 else
                 "*"   if p < 0.05  else f"p={p:.2f}")
        ax_did.text(b + se * 1.15, yi, stars, va="center", fontsize=14)
    ax_did.set_xlabel("β  (cluster-share DiD coefficient, city-clustered SE)")
    ax_did.set_title("Tripartite DiD: within-city, within-topic co-movement across five-year periods")
    fig_did.tight_layout()
    fig_did.savefig(FIGDIR / "tripartite_did.png", bbox_inches="tight")
    fig_did
    return (fig_did,)


@app.cell
def _(did_results, mo):
    _pp = did_results[("project","paper")]
    _px = did_results[("paper","patent")]
    _pt = did_results[("project","patent")]
    mo.md(f"""
    Within a city and topic, when project activity in a five-year period rises
    above that city's own baseline, academic output in the same topic also rises
    (β = {_pp['beta']:+.4f}, t = {_pp['t']:.2f}, p = {_pp['p']:.4f},
    {_pp['n_cities']} cities). The paper–patent link shows the same pattern
    (β = {_px['beta']:+.4f}, t = {_px['t']:.2f}, p = {_px['p']:.4f},
    {_px['n_cities']} cities). The direct project–patent co-movement is
    {'significant' if _pt['p'] < 0.05 else 'not significant'}
    (β = {_pt['beta']:+.4f}, p = {_pt['p']:.4f}), consistent with the
    permutation test result that papers carry the middle link.

    The city and topic×period fixed effects absorb each city's standing
    specialization and each topic's global trend. What β captures is the
    residual co-movement: when a city pushes into a topic in one period beyond
    its own norm and beyond the field's global trend in that topic, the other
    artifact type follows.
    """)
    return


@app.cell
def _(annual_vecs, np, pd):
    # ── Lead-lag: annual cluster-vector cosine similarity at lags -3 to +3 ───
    LAGS   = range(-3, 4)
    N_BOOT = 500
    _rng   = np.random.default_rng(42)

    def lead_lag_profile(vecs_a, vecs_b):
        lag_sims = {k: [] for k in LAGS}
        for (city, yr), va in vecs_a.items():
            for k in LAGS:
                vb = vecs_b.get((city, yr + k))
                if vb is not None:
                    lag_sims[k].append(float(np.dot(va, vb)))
        rows = []
        for k, vals in lag_sims.items():
            if not vals:
                continue
            arr = np.array(vals)
            boot = [_rng.choice(arr, len(arr), replace=True).mean()
                    for _ in range(N_BOOT)]
            rows.append({"lag": k, "n_pairs": len(vals), "mean_sim": arr.mean(),
                         "ci_lo": np.percentile(boot, 2.5),
                         "ci_hi": np.percentile(boot, 97.5)})
        return pd.DataFrame(rows).sort_values("lag").reset_index(drop=True)

    ll_pp = lead_lag_profile(annual_vecs["project"], annual_vecs["paper"])
    ll_px = lead_lag_profile(annual_vecs["paper"],   annual_vecs["patent"])

    return LAGS, ll_pp, ll_px, lead_lag_profile, N_BOOT


@app.cell
def _(FIGDIR, LAGS, SOL, ll_pp, ll_px, plt):
    # ── Lead-lag figure: two pairs stacked vertically ─────────────────────────
    _data   = [ll_pp,             ll_px]
    _titles = ["Project activity (year t) vs paper activity (year t+k)",
               "Paper activity (year t) vs patent activity (year t+k)"]
    _colors = [SOL["project"], SOL["paper"]]

    fig_ll, axes_ll = plt.subplots(2, 1, figsize=(10, 10))
    for _ax_ll, _df_ll, _title_ll, _col_ll in zip(axes_ll, _data, _titles, _colors):
        _ax_ll.errorbar(_df_ll.lag, _df_ll.mean_sim,
                    yerr=[_df_ll.mean_sim - _df_ll.ci_lo, _df_ll.ci_hi - _df_ll.mean_sim],
                    fmt="o-", color=_col_ll, ecolor=_col_ll, capsize=5, linewidth=2.5, ms=8)
        _ax_ll.axvline(0, color=SOL["text"], ls="--", lw=1, label="k = 0")
        _ax_ll.axvspan(0.1, max(LAGS) + 0.4,  alpha=0.06, color=SOL["cyan"],   label="upstream leads")
        _ax_ll.axvspan(min(LAGS) - 0.4, -0.1, alpha=0.06, color=SOL["orange"], label="upstream lags")
        _ax_ll.set_xlabel("Lag k  (positive k → downstream artifact comes after upstream)")
        _ax_ll.set_ylabel("Mean cosine similarity (cluster vectors)")
        _ax_ll.set_title(_title_ll)
        _ax_ll.set_xticks(list(LAGS))
        _ax_ll.legend(fontsize=11)
        _ax_ll.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.3f}"))

    fig_ll.suptitle("Lead-lag structure: does upstream activity precede downstream activity?",
                    fontsize=16, fontweight="bold")
    fig_ll.tight_layout()
    fig_ll.savefig(FIGDIR / "tripartite_lead_lag.png", bbox_inches="tight")
    fig_ll
    return (fig_ll,)


@app.cell
def _(annual_vecs, LAGS, N_BOOT, ll_pp, ll_px, np):
    # ── Permutation test: is the lead-lag asymmetry real? ────────────────────
    # Shuffle year labels for the upstream type within each city 500 times.
    # Test statistics: (1) slope of a linear fit to the profile,
    #                  (2) mean(k>0) - mean(k<0).
    _N_PERM_LL = 500
    _rng2  = np.random.default_rng(99)

    def perm_profile(vecs_a, vecs_b):
        cities = list({c for c, _ in vecs_a})
        shuffled = {}
        for city in cities:
            yrs = [yr for (c, yr) in vecs_a if c == city]
            perm = _rng2.permutation(yrs)
            for orig, new in zip(yrs, perm):
                shuffled[(city, orig)] = vecs_a[(city, new)]
        means = {}
        for k in LAGS:
            sims = [float(np.dot(shuffled[(c,y)], vecs_b[(c, y+k)]))
                    for (c, y) in shuffled if (c, y+k) in vecs_b]
            means[k] = float(np.mean(sims)) if sims else float("nan")
        return means

    def perm_stats(obs_df, vecs_a, vecs_b):
        lags_arr  = np.array(obs_df.lag)
        sims_arr  = np.array(obs_df.mean_sim)
        obs_slope    = float(np.polyfit(lags_arr, sims_arr, 1)[0])
        obs_contrast = (obs_df[obs_df.lag > 0].mean_sim.mean()
                        - obs_df[obs_df.lag < 0].mean_sim.mean())
        null_slopes, null_contrasts = [], []
        for _ in range(_N_PERM_LL):
            pm = perm_profile(vecs_a, vecs_b)
            valid = [(k, v) for k, v in pm.items() if not np.isnan(v)]
            if len(valid) < 5:
                continue
            ls, ss = zip(*valid)
            null_slopes.append(float(np.polyfit(ls, ss, 1)[0]))
            null_contrasts.append(
                np.mean([s for l, s in valid if l > 0])
                - np.mean([s for l, s in valid if l < 0]))
        p_slope    = (sum(s >= obs_slope    for s in null_slopes)    + 1) / (len(null_slopes)    + 1)
        p_contrast = (sum(s >= obs_contrast for s in null_contrasts) + 1) / (len(null_contrasts) + 1)
        return {"obs_slope": obs_slope, "null_slopes": np.array(null_slopes),
                "obs_contrast": obs_contrast, "null_contrasts": np.array(null_contrasts),
                "p_slope": p_slope, "p_contrast": p_contrast}

    perm_pp = perm_stats(ll_pp, annual_vecs["project"], annual_vecs["paper"])
    perm_px = perm_stats(ll_px, annual_vecs["paper"],   annual_vecs["patent"])

    for lbl, r in [("project→paper", perm_pp), ("paper→patent", perm_px)]:
        print(f"{lbl}: slope p={r['p_slope']:.4f}  contrast p={r['p_contrast']:.4f}")

    return (perm_pp, perm_px)


@app.cell
def _(FIGDIR, SOL, perm_pp, perm_px, plt):
    # ── Permutation figure: two pairs × two statistics (2×2, vertically led) ──
    _rows = [(perm_pp, "project → paper"), (perm_px, "paper → patent")]
    _col_pairs = [SOL["project"], SOL["paper"]]

    fig_perm_ll, axes_pll = plt.subplots(2, 2, figsize=(14, 10))

    for _ri, (_r_perm, _lbl_perm) in enumerate(_rows):
        _c_perm = _col_pairs[_ri]

        # Left column: slope distribution
        _axL = axes_pll[_ri, 0]
        _axL.hist(_r_perm["null_slopes"], bins=40, color=SOL["bg2"], edgecolor=SOL["muted"])
        _axL.axvline(_r_perm["obs_slope"], color=_c_perm, lw=2.5,
                   label=f"observed = {_r_perm['obs_slope']:.5f}\np = {_r_perm['p_slope']:.4f}")
        _axL.set_xlabel("slope of lead-lag profile (null)"); _axL.set_ylabel("permutations")
        _axL.set_title(f"{_lbl_perm}: slope test")
        _axL.legend(fontsize=11)

        # Right column: contrast distribution
        _axR = axes_pll[_ri, 1]
        _axR.hist(_r_perm["null_contrasts"], bins=40, color=SOL["bg2"], edgecolor=SOL["muted"])
        _axR.axvline(_r_perm["obs_contrast"], color=_c_perm, lw=2.5,
                   label=f"observed = {_r_perm['obs_contrast']:.5f}\np = {_r_perm['p_contrast']:.4f}")
        _axR.set_xlabel("mean(k>0) − mean(k<0) (null)"); _axR.set_ylabel("permutations")
        _axR.set_title(f"{_lbl_perm}: contrast test")
        _axR.legend(fontsize=11)

    fig_perm_ll.suptitle("Lead-lag permutation tests (500 within-city year shuffles)",
                         fontsize=16, fontweight="bold")
    fig_perm_ll.tight_layout()
    fig_perm_ll.savefig(FIGDIR / "tripartite_lead_lag_perm.png", bbox_inches="tight")
    fig_perm_ll
    return (fig_perm_ll,)


@app.cell
def _(mo, perm_pp, perm_px):
    mo.md(f"""
    The lead-lag permutation tests check whether the profile shape—specifically
    whether similarity is higher when the downstream artifact comes *after* the
    upstream one—is real or a chance feature of the corpus timing.

    For project → paper: slope p = {perm_pp['p_slope']:.4f},
    contrast p = {perm_pp['p_contrast']:.4f}.
    For paper → patent: slope p = {perm_px['p_slope']:.4f},
    contrast p = {perm_px['p_contrast']:.4f}.

    A p-value below 0.05 means the observed asymmetry—where similarity is higher
    at positive lags than at negative ones—exceeds what year-shuffled cities
    produce. The direction of the asymmetry, when it appears, is consistent with
    projects feeding into papers and papers feeding into patents, but the test
    establishes only that the temporal pattern is non-random, not that the flow
    is causal.
    """)
    return


if __name__ == "__main__":
    app.run()
