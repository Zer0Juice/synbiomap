# Patents, Papers, Parts & Planet

**Do student iGEM projects, academic papers, and patents in synthetic biology form semantically related local innovation trajectories at the city level?**

This repository contains the full research pipeline and documentation website for a CSH thesis project studying synthetic biology innovation across three types of knowledge artifact: student projects, academic publications, and patents. The primary case study is **carbon capture in synthetic biology**.

## Project website

[GitHub Pages site](https://zer0juice.github.io/synbio-diversification) — the main public-facing home for this project.

## Quick start

```bash
# 1. Clone
git clone https://github.com/Zer0Juice/synbio-diversification
cd synbio-diversification

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Edit .env and add your OPENALEX_EMAIL and LENS_API_TOKEN

# 4. Run the pipeline notebooks in order
jupyter notebook notebooks/
```

## Repository structure

```
├── config/                  # settings.yaml — all pipeline parameters
├── data/
│   ├── raw/                 # downloaded raw data (not committed)
│   └── processed/           # normalized CSVs (committed)
│       ├── papers.csv
│       ├── patents.csv
│       ├── projects.csv
│       └── parts.csv
├── src/                     # reusable Python modules
│   ├── ingest/              # data fetching: openalex.py, lens.py, igem.py
│   ├── embed/               # embedding generation with caching
│   ├── cluster/             # UMAP + HDBSCAN
│   ├── geo/                 # geocoding with caching
│   └── utils/               # shared schema and config loading
├── notebooks/               # step-by-step pipeline notebooks
│   ├── 01_ingest_papers.ipynb
│   ├── 02_ingest_patents.ipynb
│   ├── 03_ingest_projects.ipynb
│   ├── 04_embed.ipynb
│   ├── 05_cluster.ipynb
│   ├── 06_visualize.ipynb
│   └── walkthrough_carbon_capture.ipynb   ← main case study walkthrough
├── website/                 # Quarto documentation website
├── manuscript/              # LaTeX manuscript
└── slides/                  # LaTeX Beamer slides
```

## Data sources

| Source | What it provides | Access |
|--------|-----------------|--------|
| [OpenAlex](https://openalex.org) | Academic papers | Free REST API |
| [Lens.org](https://www.lens.org) | Patents | Free API (token required) |
| [iGEM Registry](https://igem.org) | Student projects and parts | CSV download |

## Configuration

All pipeline parameters — keywords, model name, year range, clustering settings — are in [`config/settings.yaml`](config/settings.yaml). Edit that file to change behaviour.

## Methods summary

1. **Corpus construction** — keyword search in OpenAlex and Lens.org; iGEM data loaded from CSV
2. **Case study tagging** — carbon-capture keywords matched against title + abstract
3. **Embeddings** — `all-MiniLM-L6-v2` sentence-transformer (384-dim vectors)
4. **Dimensionality reduction** — UMAP (2D, cosine metric)
5. **Clustering** — HDBSCAN
6. **Geocoding** — Nominatim (OpenStreetMap), cached locally

## License

[To be determined]
