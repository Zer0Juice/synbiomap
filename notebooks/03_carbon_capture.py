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
    # Carbon capture: the case study

    Humanity reshaped the planet's carbon by accident. The same power, aimed on
    purpose, could pull some of it back. In synthetic biology the biological ways
    to do that gather in three topics from the main analysis: engineering
    cyanobacteria to fix carbon by photosynthesis (clusters 7 and 8), and
    fermenting waste gases into fuels and chemicals (cluster 62). This notebook
    treats those three as one carbon-capture family and asks two questions the
    main notebook set up but did not answer.

    Which cities do the most carbon-capture work? And in the papers, who sits at
    the centre of the citation conversation?

    This is the worked example, not a new test. We name real cities and real
    papers, and we keep to description.
    """)
    return


@app.cell
def _():
    # ── Setup ─────────────────────────────────────────────────────────────────
    import sys
    from pathlib import Path
    from collections import Counter

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import networkx as nx
    from matplotlib.lines import Line2D

    ROOT = Path.cwd()
    if not (ROOT / "src").exists() and (ROOT.parent / "src").exists():
        ROOT = ROOT.parent
    sys.path.insert(0, str(ROOT))

    PROCESSED = ROOT / "data" / "processed"
    FIGDIR    = ROOT / "outputs" / "figures"
    FIGDIR.mkdir(parents=True, exist_ok=True)

    from src.analyze.network import citation_graph, pagerank_centrality

    return (
        Counter, FIGDIR, Line2D, PROCESSED, citation_graph, mpl, np, nx,
        pagerank_centrality, pd, plt,
    )


@app.cell
def _(mpl):
    # ── Publication-ready white theme ────────────────────────────────────────
    SOL = {
        "bg": "#ffffff", "bg2": "#f0f0f0", "muted": "#888888", "text": "#222222",
        "paper": "#268bd2", "project": "#2aa198", "patent": "#cb4b16",
        "blue": "#268bd2", "cyan": "#2aa198", "orange": "#cb4b16",
        "yellow": "#b58900", "red": "#dc322f", "violet": "#6c71c4", "green": "#859900",
    }
    mpl.rcParams.update({
        "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff",
        "axes.edgecolor": SOL["muted"], "axes.labelcolor": SOL["text"],
        "xtick.color": SOL["text"], "ytick.color": SOL["text"], "text.color": SOL["text"],
        "grid.color": "#dddddd", "grid.linestyle": "--", "grid.alpha": 0.8,
        "savefig.facecolor": "#ffffff", "savefig.dpi": 200, "figure.dpi": 120,
        "font.size": 15, "axes.titlesize": 20, "axes.titleweight": "bold",
        "axes.labelsize": 16, "legend.fontsize": 13,
        "xtick.labelsize": 13, "ytick.labelsize": 13,
    })
    return (SOL,)


@app.cell
def _(mo):
    mo.md(r"""
    ## The carbon-capture family

    We pull the three topics out of the clustered corpus and attach citation lists
    to the papers from `papers.csv`.
    """)
    return


@app.cell
def _(PROCESSED, pd):
    # ── Load the family (clusters 7, 8, 62) and the topic labels ──────────────
    FAM = (7, 8, 62)

    arts = pd.read_csv(PROCESSED / "artifacts_tripartite_clustered.csv", low_memory=False)
    labels_df = pd.read_csv(PROCESSED / "cluster_labels.csv")
    label_of = dict(zip(labels_df["cluster"].astype(int), labels_df["label"].astype(str)))

    family = arts[arts["cluster_label"].isin(FAM)].copy()

    # Papers need their citation lists, which live in papers.csv, not the corpus.
    _cited = pd.read_csv(PROCESSED / "papers.csv", low_memory=False,
                         usecols=["id", "cited_works"])
    fam_papers = (family[family["type"] == "paper"]
                  .merge(_cited, on="id", how="left"))

    return FAM, fam_papers, family, label_of


@app.cell
def _(FAM, family, label_of, mo):
    _counts = family["type"].value_counts()
    _fams = ", ".join(f"cluster {c} ({label_of.get(c,'')})" for c in FAM)
    mo.md(f"""
    The family is {len(family):,} artifacts: {_counts.get('paper',0)} papers,
    {_counts.get('project',0)} student projects, and {_counts.get('patent',0)} patents,
    drawn from {_fams}. Patents outnumber papers here, which already says something:
    carbon capture is close enough to application that firms file for it.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Which cities do the most carbon-capture work?

    Count each city's carbon-capture artifacts, split by kind. "Most" is not one
    thing: a patent is applied output, a paper is research output, a student
    project is a first attempt. So we keep the three apart rather than sum them
    into a single ranking.
    """)
    return


@app.cell
def _(FIGDIR, SOL, family, np, plt):
    # ── Leaderboard: top cities by carbon-family artifacts, split by kind ──────
    lead = (family.groupby("city")
            .agg(total=("id", "size"),
                 paper=("type", lambda s: int((s == "paper").sum())),
                 project=("type", lambda s: int((s == "project").sum())),
                 patent=("type", lambda s: int((s == "patent").sum())))
            .sort_values("total", ascending=False))
    _top = lead.head(15).iloc[::-1]      # reverse so the biggest is on top in barh

    fig_lead, ax_lead = plt.subplots(figsize=(14, 9))
    _y = np.arange(len(_top))
    _left = np.zeros(len(_top))
    for _k, _col in [("paper", SOL["paper"]), ("project", SOL["project"]), ("patent", SOL["patent"])]:
        ax_lead.barh(_y, _top[_k], left=_left, color=_col, label=_k, edgecolor="white")
        _left = _left + _top[_k].to_numpy()
    ax_lead.set_yticks(_y); ax_lead.set_yticklabels(_top.index)
    ax_lead.set_xlabel("carbon-capture artifacts")
    ax_lead.set_title("Where carbon-capture synthetic biology happens")
    ax_lead.legend(loc="lower right")
    fig_lead.tight_layout()
    fig_lead.savefig(FIGDIR / "cc_city_leaderboard.png", bbox_inches="tight")
    fig_lead
    return (lead,)


@app.cell
def _(lead, mo):
    _t = lead.head(6)
    _rows = "\n".join(
        f"| {_c} | {int(_r.paper)} | {int(_r.project)} | {int(_r.patent)} | {int(_r.total)} |"
        for _c, _r in _t.iterrows()
    )
    _lead_city = lead.index[0]
    _paper_city = lead.sort_values("paper", ascending=False).index[0]
    mo.md(f"""
    | city | papers | projects | patents | total |
    |---|--:|--:|--:|--:|
    {_rows}

    {_lead_city} leads by volume, and mostly through patents. {_paper_city} leads on
    papers instead, the research end rather than the filing end. The same field
    looks like invention in one city and publication in another, which is the split
    the main analysis kept finding: a city's carbon-capture work leans academic or
    applied depending on who is doing it.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. The citation conversation

    Among the carbon-capture papers, who does the work build on? Each paper cites
    others; keep the citations that point to another paper in the family and you
    get a directed graph, one arrow per citation. PageRank then scores each paper:
    a paper is central when it is cited by papers that are themselves cited, so the
    score rewards sitting at the middle of the conversation, not merely being cited
    often. In the drawing, bigger dots are more central and the largest are
    labelled by city.
    """)
    return


@app.cell
def _(Counter, FIGDIR, Line2D, SOL, citation_graph, fam_papers, np, nx,
      pagerank_centrality, plt):
    # ── Build the family citation graph and score it ──────────────────────────
    G, meta = citation_graph(fam_papers)
    pr = pagerank_centrality(G)

    _top_cities = [c for c, _ in Counter(meta["city"].dropna()).most_common(6)]
    _palette = [SOL[k] for k in ("blue", "cyan", "orange", "violet", "green", "yellow")]
    _city_color = {c: _palette[i] for i, c in enumerate(_top_cities)}

    _pos = nx.spring_layout(G, seed=42, k=0.5)
    _nodes = list(G.nodes)
    _sizes = [30 + 9000 * pr[w] for w in _nodes]
    _colors = [_city_color.get(meta.loc[w, "city"], SOL["muted"]) for w in _nodes]

    fig_net, ax_net = plt.subplots(figsize=(15, 13))
    nx.draw_networkx_edges(G, _pos, ax=ax_net, alpha=0.08, edge_color=SOL["muted"],
                           arrows=False, width=0.7)
    nx.draw_networkx_nodes(G, _pos, ax=ax_net, nodelist=_nodes, node_size=_sizes,
                           node_color=_colors, linewidths=0.4, edgecolors="white")
    for _w in sorted(pr, key=pr.get, reverse=True)[:10]:
        ax_net.annotate(str(meta.loc[_w, "city"]), _pos[_w], fontsize=11,
                        fontweight="bold", ha="center", va="center", color=SOL["text"])
    _handles = [Line2D([0], [0], marker="o", ls="", mfc=_city_color[c],
                       mec="white", ms=12, label=c) for c in _top_cities]
    ax_net.legend(handles=_handles, title="most-present cities", loc="upper left",
                  framealpha=0.9)
    ax_net.set_title(f"The carbon-capture citation network "
                     f"({G.number_of_nodes()} papers, {G.number_of_edges()} citations)")
    ax_net.axis("off")
    fig_net.tight_layout()
    fig_net.savefig(FIGDIR / "cc_citation_network.png", bbox_inches="tight")
    fig_net
    return G, meta, pr


@app.cell
def _(G, meta, mo, pr):
    _top = sorted(pr, key=pr.get, reverse=True)[:8]
    _rows = "\n".join(
        f"| {pr[w]:.3f} | {G.in_degree(w)} | {str(meta.loc[w,'city'])} | "
        f"{str(meta.loc[w,'title'])[:70]} |"
        for w in _top
    )
    mo.md(f"""
    The most central carbon-capture papers, by PageRank, with their in-family
    citation count and city:

    | PageRank | cited by | city | title |
    |--:|--:|---|---|
    {_rows}
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Which cities anchor the conversation?

    PageRank scores sum to one across all the papers, so adding up a city's papers
    gives that city's share of the whole carbon-capture conversation. This is a
    different question from volume: a city can file many patents yet sit at the
    edge of the citation graph, or publish a few well-placed papers and sit near
    its centre.
    """)
    return


@app.cell
def _(FIGDIR, SOL, meta, mo, np, pr, plt):
    # ── City share of citation centrality ─────────────────────────────────────
    _by_city = {}
    for _w, _s in pr.items():
        _c = meta.loc[_w, "city"]
        if _c and str(_c) != "nan":
            _by_city[_c] = _by_city.get(_c, 0.0) + _s
    city_pr = dict(sorted(_by_city.items(), key=lambda kv: -kv[1]))

    _top = list(city_pr.items())[:12][::-1]
    fig_citypr, ax_cpr = plt.subplots(figsize=(13, 8))
    _y = np.arange(len(_top))
    ax_cpr.barh(_y, [v for _, v in _top], color=SOL["blue"], edgecolor="white")
    ax_cpr.set_yticks(_y); ax_cpr.set_yticklabels([c for c, _ in _top])
    ax_cpr.set_xlabel("share of carbon-capture citation centrality (summed PageRank)")
    ax_cpr.set_title("Which cities anchor the carbon-capture conversation")
    fig_citypr.tight_layout()
    fig_citypr.savefig(FIGDIR / "cc_city_centrality.png", bbox_inches="tight")
    fig_citypr
    return (city_pr,)


@app.cell
def _(city_pr, lead, mo):
    _anchor = list(city_pr)[0]
    _anchor_share = city_pr[_anchor]
    _vol_leader = lead.index[0]
    _same = _anchor == _vol_leader
    mo.md(f"""
    {_anchor} holds the largest share of citation centrality, about
    {_anchor_share:.0%} of the total. { "It also leads by volume, so here the busiest city is also the most central." if _same else f"That is not the same as {_vol_leader}, the busiest city by count: volume and centrality can part ways, one city filing patents at the edge of the conversation while another publishes at its centre." }
    Read the two together: the leaderboard shows where the work is done, the
    network shows whose work the rest is built on.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## What this adds

    The main notebook showed that a city's carbon-capture papers, projects, and
    patents tend to share topics. This one puts names to it. A short list of
    cities does most of the work, some as inventors and some as researchers, and a
    smaller set of papers anchors what the rest cites. None of this is a causal
    claim; it is a portrait of where one corner of synthetic biology, the corner
    aimed at the planet's carbon, is being written.
    """)
    return


if __name__ == "__main__":
    app.run()
