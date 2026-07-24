"""
Step 18 — Export website data assets for the *tripartite* corpus.

This replaces the older bipartite export (scripts/06_visualize.py), which only
knew about papers and projects. The website's interactive Explorer and
geographic map read the five JSON files written here.

We read from the finished tripartite corpus so nothing heavy has to re-run:
    data/processed/artifacts_tripartite_clustered.csv   (all 3 artifact types,
        with UMAP coordinates and cluster assignments already attached)
    data/processed/cluster_labels.csv                   (human-checked topic
        names, one row per HDBSCAN cluster)

Only the Python standard library is used (csv + json), so this runs in any
Python 3 without pandas installed.

Usage:
    python3 scripts/18_export_website_assets.py

Output (written to website/assets/data/):
    artifacts.json      one lightweight record per artifact (no abstract text)
    projections.json    2-D UMAP coordinates keyed by artifact id
    abstracts.json      id -> abstract text (large; loaded lazily in the browser)
    cities.json         per-city counts by artifact type
    cluster_labels.json cluster id -> topic name
"""

import csv
import json
import math
from pathlib import Path

# The `text` column holds full abstracts, which can exceed the default CSV
# field-size limit. Raise it so the parser doesn't choke on long entries.
csv.field_size_limit(10 ** 7)

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED = REPO_ROOT / "data" / "processed"
WEB_DATA = REPO_ROOT / "website" / "assets" / "data"

ARTIFACTS_CSV = PROCESSED / "artifacts_tripartite_clustered.csv"
LABELS_CSV = PROCESSED / "cluster_labels.csv"


def to_float(value):
    """Parse a CSV string to float, returning None for blanks/NaN.

    Browsers reject the literal NaN in JSON, so empty or missing numbers must
    become null (None), never NaN.
    """
    if value is None:
        return None
    value = str(value).strip()
    if value == "" or value.lower() in ("nan", "none"):
        return None
    try:
        f = float(value)
        return None if math.isnan(f) else f
    except ValueError:
        return None


def to_int(value):
    """Parse a CSV string to int, returning None for blanks (e.g. a year)."""
    f = to_float(value)
    return int(f) if f is not None else None


def to_bool(value):
    """Parse the case-study flag, which appears as True/False/1/0 text."""
    return str(value).strip().lower() in ("true", "1", "1.0", "yes")


def load_cluster_labels():
    """Return {cluster_id (int): topic label} from the reviewed labels file."""
    labels = {}
    with open(LABELS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cid = to_int(row.get("cluster"))
            if cid is not None:
                labels[cid] = (row.get("label") or "").strip()
    return labels


def run():
    print("=== Step 18: Export tripartite website assets ===\n")
    WEB_DATA.mkdir(parents=True, exist_ok=True)

    cluster_labels = load_cluster_labels()
    print(f"Loaded {len(cluster_labels)} cluster labels")

    artifacts = []      # lightweight metadata for every artifact
    projections = []    # UMAP coordinates for the scatter plot
    abstracts = {}      # id -> abstract text (fetched on demand in the browser)
    cities = {}         # (city, country) -> running counts
    type_counts = {}

    with open(ARTIFACTS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            aid = row["id"]
            atype = row["type"]
            type_counts[atype] = type_counts.get(atype, 0) + 1

            title = (row.get("title") or "").strip()
            year = to_int(row.get("year"))
            city = (row.get("city") or "").strip()
            country = (row.get("country") or "").strip()
            lat = to_float(row.get("lat"))
            lon = to_float(row.get("lon"))
            cc_flag = to_bool(row.get("case_study_flag"))

            cid = to_int(row.get("cluster_label"))
            if cid is None:
                cid = -1
            cluster_name = cluster_labels.get(cid, "") if cid >= 0 else ""

            # --- artifacts.json record (no abstract text — kept small) ---
            artifacts.append({
                "id": aid,
                "type": atype,
                "title": title,
                "year": year,
                "city": city or None,
                "country": country or None,
                "lat": lat,
                "lon": lon,
                "case_study_flag": cc_flag,
                "cluster_label": cid,
                "cluster_name": cluster_name,
            })

            # --- projections.json record ---
            projections.append({
                "id": aid,
                "x": to_float(row.get("umap_x")),
                "y": to_float(row.get("umap_y")),
                "cluster": cid,
                "label": cluster_name,
            })

            # --- abstracts.json entry (strip the title prefix from `text`) ---
            text = (row.get("text") or "").strip()
            abstract = text
            if title and text.startswith(title):
                abstract = text[len(title):].lstrip(". ").strip()
            if abstract:
                abstracts[aid] = abstract

            # --- cities.json aggregation ---
            if city and lat is not None and lon is not None:
                key = (city, country)
                rec = cities.get(key)
                if rec is None:
                    rec = {
                        "city": city, "country": country,
                        "lat": lat, "lon": lon,
                        "count_papers": 0, "count_patents": 0,
                        "count_projects": 0, "count_carbon_capture": 0,
                    }
                    cities[key] = rec
                if atype == "paper":
                    rec["count_papers"] += 1
                elif atype == "patent":
                    rec["count_patents"] += 1
                elif atype == "project":
                    rec["count_projects"] += 1
                if cc_flag:
                    rec["count_carbon_capture"] += 1

    # --- write everything out ---
    (WEB_DATA / "artifacts.json").write_text(json.dumps(artifacts))
    print(f"Wrote artifacts.json ({len(artifacts)} records)")

    (WEB_DATA / "projections.json").write_text(json.dumps(projections))
    print(f"Wrote projections.json ({len(projections)} records)")

    (WEB_DATA / "abstracts.json").write_text(json.dumps(abstracts))
    print(f"Wrote abstracts.json ({len(abstracts)} entries)")

    city_list = sorted(
        cities.values(),
        key=lambda c: (c["count_papers"] + c["count_patents"] + c["count_projects"]),
        reverse=True,
    )
    (WEB_DATA / "cities.json").write_text(json.dumps(city_list))
    print(f"Wrote cities.json ({len(city_list)} cities)")

    (WEB_DATA / "cluster_labels.json").write_text(
        json.dumps({str(cid): name for cid, name in sorted(cluster_labels.items())})
    )
    print(f"Wrote cluster_labels.json ({len(cluster_labels)} clusters)")

    print("\nArtifact type counts:")
    for t, n in sorted(type_counts.items()):
        print(f"  {t:8s} {n}")
    print(f"  {'TOTAL':8s} {sum(type_counts.values())}")
    print(f"\nAll files written to {WEB_DATA.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    run()
