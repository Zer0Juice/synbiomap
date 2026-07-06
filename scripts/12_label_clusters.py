"""
Step 12 — Draft human-readable topic labels, then let a human verify them.

HDBSCAN gives us 80 numbered topics; numbers are useless on a map or in a table.
This script produces a *review sheet* — draft labels plus all the evidence a
human needs to check and correct them in one place. The final labels that ship
are whatever a person leaves in the CSV; the LLM only removes the blank page.

Why contrastive labelling?
  Labelling each cluster in isolation produced collisions (two cyanobacteria
  clusters both came out "Cyanobacterial Synthetic Biology") even though the
  clusters are genuinely different — one is student iGEM projects, the other
  academic chassis toolkits. So we label each cluster *against its nearest
  neighbours*: Claude sees the neighbouring clusters' labels and must give this
  one a label that is distinct and specific. A final repair pass breaks any ties.

Evidence assembled locally per cluster:
  - representative titles: documents closest to the cluster centroid;
  - distinctive terms: light c-TF-IDF (Grootendorst 2022, BERTopic);
  - nearest sibling clusters by centroid cosine (also flags likely over-splits).

Auth: reads ANTHROPIC_API_KEY (or CLAUDE_API_KEY) from .env — never hard-coded.

Output (the review sheet — edit `label` / `description` in place, then it ships):
  data/processed/cluster_labels.csv
    cluster, label, description, review_note, n_docs, n_paper, n_project,
    n_patent, dominant_type, is_carbon_capture, top_terms, nearest_siblings,
    representative_titles

Usage
-----
  python scripts/12_label_clusters.py
  python scripts/12_label_clusters.py --model claude-sonnet-4-6 --n-siblings 5
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.embed.embeddings import _load_cache

PROCESSED = REPO_ROOT / "data" / "processed"
CORPUS    = PROCESSED / "artifacts_tripartite_clustered.csv"
CACHE     = REPO_ROOT / "data" / "embeddings" / "finetuned" / "embeddings.json"
OUT       = PROCESSED / "cluster_labels.csv"

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MERGE_FLAG    = 0.90   # centroid cosine above which two clusters may be over-splits

CONTRASTIVE_SYSTEM = (
    "You label topic clusters from a synthetic-biology corpus that mixes academic "
    "papers, student iGEM project pages, and patents. You are given ONE cluster's "
    "representative titles and distinctive terms, plus the labels of its NEAREST "
    "neighbour clusters. Give THIS cluster a label that is specific to synthetic "
    "biology (name the technique, system, organism, or application) AND clearly "
    "distinct from every neighbour label shown. If the cluster is dominated by "
    "student projects rather than papers, or vice versa, reflect that register only "
    "when it is what distinguishes it. Respond with ONLY JSON: "
    '{"label": "...", "description": "..."} — label 2-5 words Title Case, '
    "description one sentence of at most 20 words."
)

REPAIR_SYSTEM = (
    "Several synthetic-biology topic clusters received the SAME label. Give each a "
    "distinct, specific label that separates it from the others, using its terms and "
    "titles. Respond with ONLY a JSON object mapping each cluster id (as a string) to "
    '{"label": "...", "description": "..."}.'
)


def representative_titles(df_c, cache, n):
    """Titles of the n documents closest to the cluster centroid (most typical)."""
    ids = [i for i in df_c["id"] if i in cache]
    if not ids:
        return df_c["title"].dropna().astype(str).head(n).tolist()
    X = np.asarray([cache[i] for i in ids], dtype=np.float32)
    Xn = X / np.clip(np.linalg.norm(X, axis=1, keepdims=True), 1e-8, None)
    centroid = Xn.mean(axis=0); centroid /= np.clip(np.linalg.norm(centroid), 1e-8, None)
    order = np.argsort(-(Xn @ centroid))
    title_by_id = dict(zip(df_c["id"], df_c["title"].astype(str)))
    seen, out = set(), []
    for j in order:
        t = title_by_id.get(ids[j], "").strip()
        if t and t.lower() not in seen:
            seen.add(t.lower()); out.append(t[:150])
        if len(out) >= n:
            break
    return out


def distinctive_terms(labels, texts, k_clusters, top):
    """c-TF-IDF: pool each cluster's text into one document, score distinctive terms."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    pooled = ["" for _ in range(k_clusters)]
    for lab, txt in zip(labels, texts):
        if lab >= 0:
            pooled[lab] += " " + str(txt)
    vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english",
                          min_df=2, max_features=20000, sublinear_tf=True)
    M = vec.fit_transform(pooled)
    vocab = np.array(vec.get_feature_names_out())
    return {c: vocab[np.argsort(-M[c].toarray().ravel())[:top]].tolist() for c in range(k_clusters)}


def cluster_centroids(clustered, cache, k_clusters):
    """Unit-norm mean embedding per cluster, and the centroid cosine matrix."""
    cent = np.zeros((k_clusters, 768), dtype=np.float64)
    for c, g in clustered.groupby("cluster_label"):
        V = np.asarray([cache[i] for i in g["id"] if i in cache], dtype=np.float32)
        Vn = V / np.clip(np.linalg.norm(V, axis=1, keepdims=True), 1e-8, None)
        m = Vn.mean(0); cent[int(c)] = m / np.clip(np.linalg.norm(m), 1e-8, None)
    S = cent @ cent.T
    np.fill_diagonal(S, -1.0)
    return S


def _parse_json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(raw)


def label_contrastive(client, model, terms, titles, neighbours):
    nb = "\n".join(f"- {lab}: {', '.join(t[:6])}" for lab, t in neighbours)
    user = (
        "THIS cluster distinctive terms: " + ", ".join(terms) + "\n\n"
        "THIS cluster representative titles:\n" + "\n".join(f"- {t}" for t in titles) +
        "\n\nNEAREST neighbour clusters (make THIS label distinct from these):\n" + nb
    )
    msg = client.messages.create(model=model, max_tokens=220, temperature=0,
                                 system=CONTRASTIVE_SYSTEM,
                                 messages=[{"role": "user", "content": user}])
    obj = _parse_json(msg.content[0].text)
    return str(obj["label"]).strip(), str(obj["description"]).strip()


def repair_collisions(client, model, groups, evidence):
    """groups: {label: [cluster ids]} with >1 member. Returns {cluster: (label, desc)}."""
    fixed = {}
    for _, ids in groups.items():
        blocks = []
        for c in ids:
            terms, titles = evidence[c]
            blocks.append(f"Cluster {c}\n  terms: {', '.join(terms[:8])}\n  titles: "
                          + " | ".join(titles[:5]))
        user = "\n\n".join(blocks)
        msg = client.messages.create(model=model, max_tokens=400, temperature=0,
                                      system=REPAIR_SYSTEM,
                                      messages=[{"role": "user", "content": user}])
        obj = _parse_json(msg.content[0].text)
        for c in ids:
            o = obj.get(str(c)) or obj.get(int(c)) or {}
            if o:
                fixed[c] = (str(o["label"]).strip(), str(o["description"]).strip())
    return fixed


def run(args):
    from dotenv import load_dotenv
    import anthropic

    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
    if not key:
        sys.exit("No ANTHROPIC_API_KEY / CLAUDE_API_KEY found in .env or environment.")
    client = anthropic.Anthropic(api_key=key)

    df = pd.read_csv(CORPUS, low_memory=False)
    cache = _load_cache(CACHE)
    df["is_cc"] = df["case_study_flag"].astype(str).str.lower().isin(["true", "1", "1.0"])
    clustered = df[df["cluster_label"] >= 0].copy()
    K = int(clustered["cluster_label"].max()) + 1

    print("Assembling evidence (terms, titles, centroids)...")
    terms = distinctive_terms(df["cluster_label"].to_numpy(),
                              df["text"].fillna(df["title"]).astype(str).tolist(),
                              K, top=args.top_terms)
    titles = {c: representative_titles(clustered[clustered.cluster_label == c], cache, 10)
              for c in range(K)}
    S = cluster_centroids(clustered, cache, K)
    siblings = {c: list(np.argsort(-S[c])[:args.n_siblings]) for c in range(K)}

    cc_share = clustered.groupby("cluster_label")["is_cc"].mean()
    cc_cluster = int(cc_share.idxmax())

    # Provisional labels for neighbour context: reuse an existing sheet if present.
    prov = {}
    if OUT.exists() and not args.force:
        old = pd.read_csv(OUT)
        prov = dict(zip(old["cluster"].astype(int), old["label"].astype(str)))
        print(f"Reusing {len(prov)} provisional labels as neighbour context.")

    print("Contrastive labelling...")
    lab, desc = {}, {}
    for c in range(K):
        nbrs = [(prov.get(s, f"cluster {s}"), terms[s]) for s in siblings[c]]
        try:
            lab[c], desc[c] = label_contrastive(client, args.model, terms[c], titles[c], nbrs)
        except Exception as e:
            print(f"  cluster {c}: FAILED ({e})"); lab[c], desc[c] = prov.get(c, ""), ""
        print(f"  c{c:>2} ({len(clustered[clustered.cluster_label==c]):>4}): {lab[c]}")

    # Repair any remaining duplicate labels.
    vc = pd.Series(lab).value_counts()
    dups = {L: [c for c in lab if lab[c] == L] for L in vc[vc > 1].index}
    if dups:
        print(f"Repairing {sum(len(v) for v in dups.values())} clusters in "
              f"{len(dups)} collision group(s)...")
        for c, (L, D) in repair_collisions(client, args.model, dups,
                                           {c: (terms[c], titles[c]) for c in range(K)}).items():
            lab[c], desc[c] = L, D

    # Build the review sheet.
    rows = []
    for c in range(K):
        g = clustered[clustered.cluster_label == c]
        vcnt = g["type"].value_counts()
        best_sib = siblings[c][0]
        note = (f"possible merge with c{best_sib} (cos {S[c][best_sib]:.2f})"
                if S[c][best_sib] >= MERGE_FLAG else "")
        rows.append({
            "cluster": c, "label": lab[c], "description": desc[c], "review_note": note,
            "n_docs": len(g), "n_paper": int(vcnt.get("paper", 0)),
            "n_project": int(vcnt.get("project", 0)), "n_patent": int(vcnt.get("patent", 0)),
            "dominant_type": vcnt.idxmax() if len(vcnt) else "",
            "is_carbon_capture": (c == cc_cluster),
            "top_terms": ", ".join(terms[c][:8]),
            "nearest_siblings": " | ".join(f"c{s}:{lab[s]}({S[c][s]:.2f})" for s in siblings[c]),
            "representative_titles": " | ".join(titles[c]),
        })
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\nReview sheet -> {OUT.relative_to(REPO_ROOT)}  "
          f"({sum(1 for r in rows if r['review_note'])} merge flags). "
          f"Edit label/description in place; the notebook ships whatever you leave.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Draft + review topic-cluster labels with Claude.")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--n-siblings", type=int, default=5, help="neighbour clusters for contrast")
    p.add_argument("--top-terms", type=int, default=12)
    p.add_argument("--force", action="store_true", help="ignore any existing sheet")
    run(p.parse_args())
