"""
network.py — the citation graph for the carbon-capture case study.

Papers carry a cited_works field: a list of the OpenAlex ids they cite. That
turns a set of papers into a directed graph, one arrow per citation. Here we
build that graph among a chosen set of papers (the carbon-capture family) and
score how central each paper is with PageRank, so we can ask which papers, and
which cities, sit at the middle of the conversation.

Only papers carry citations in this corpus, so the graph is paper-to-paper.
Patents and student projects join the case study through the leaderboard, not
this graph.
"""

from __future__ import annotations

import re

import networkx as nx
import pandas as pd


def _bare_id(url: str) -> str | None:
    """OpenAlex ids look like https://openalex.org/W2085204013; keep the W-number."""
    m = re.search(r"(W\d+)$", str(url))
    return m.group(1) if m else None


def citation_graph(
    papers: pd.DataFrame,
    id_col: str = "id",
    cited_col: str = "cited_works",
) -> tuple[nx.DiGraph, pd.DataFrame]:
    """
    Directed citation graph among the given papers. An arrow runs from a paper to
    each paper it cites that is also in the set (cited_works is a ';'-separated
    list of bare W-ids). Returns the graph and a metadata frame indexed by W-id.
    """
    df = papers.copy()
    df["_w"] = df[id_col].map(_bare_id)
    df = df.dropna(subset=["_w"]).drop_duplicates("_w")
    nodes = set(df["_w"])

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for w, cited in zip(df["_w"], df[cited_col].fillna("")):
        for c in str(cited).split(";"):
            c = c.strip()
            if c in nodes and c != w:
                G.add_edge(w, c)          # w cites c
    return G, df.set_index("_w")


def pagerank_centrality(G: nx.DiGraph) -> dict:
    """
    PageRank on the citation graph. A paper scores high when it is cited by papers
    that are themselves cited, so it rewards being central to the conversation, not
    just being cited often. Scores sum to one across papers. With no edges every
    paper is equally (un)central.
    """
    if G.number_of_edges() == 0:
        n = G.number_of_nodes()
        return {v: 1.0 / n for v in G} if n else {}
    return nx.pagerank(G)
