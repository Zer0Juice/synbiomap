# Patents, Papers, Parts & Planet

**Do student iGEM projects, academic papers, and patents in synthetic biology form semantically related local innovation trajectories at the city level?**

This repository contains the full research pipeline and documentation website for a CSH thesis project studying synthetic biology innovation across three types of knowledge artifact: student projects, academic publications, and patents. The primary case study is **carbon capture in synthetic biology**.

## Project website

[GitHub Pages site](https://zer0juice.github.io/synbiomap) — the main public-facing home for this project.

## Quick start

```bash
# 1. Clone
git clone https://github.com/Zer0Juice/synbiomap
cd synbiomap

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Edit .env — add OPENALEX_EMAIL and OPENALEX_API_KEY
# No credentials needed for patent data (PatentsView is open)

# 4. Place iGEM data files
#    data/raw/projects/igem_projects.csv
#    data/raw/parts/igem_parts.csv

# 5. Run the pipeline (choose one):

# Option A — run all steps at once in the notebook
jupyter notebook notebooks/pipeline.ipynb

# Option B — run individual steps from the terminal
python scripts/01_ingest_papers.py
python scripts/02_ingest_patents.py
python scripts/03_ingest_projects.py
python scripts/04_embed.py
python scripts/05_cluster.py
python scripts/06_visualize.py
```

## Repository structure

```
├── config/
│   └── settings.yaml          # all pipeline parameters — edit this to change behaviour
│
├── data/
│   ├── raw/                   # downloaded raw files (not committed — too large)
│   │   ├── projects/          # igem_projects.csv goes here
│   │   └── parts/             # igem_parts.csv goes here
│   ├── processed/             # normalized CSVs (output of steps 01–03, 05)
│   │   ├── papers.csv
│   │   ├── patents.csv
│   │   ├── projects.csv
│   │   ├── parts.csv
│   │   └── all_artifacts.csv  # combined, with UMAP coords and cluster labels
│   ├── embeddings/            # embedding cache and projections (not committed)
│   │   ├── embeddings.json
│   │   └── projections.json
│   └── geo/                   # geocoding cache
│       └── geocoding_cache.json
│
├── scripts/                   # pipeline steps — runnable individually or via notebook
│   ├── 01_ingest_papers.py    # fetch papers from OpenAlex (3-layer keyword strategy)
│   ├── 02_ingest_patents.py   # fetch patents from PatentsView/USPTO (no key needed)
│   ├── 03_ingest_projects.py  # load iGEM projects and parts from CSV
│   ├── 04_embed.py            # generate sentence embeddings (cached)
│   ├── 05_cluster.py          # UMAP projection + HDBSCAN clustering
│   └── 06_visualize.py        # export JSON files for the website
│
├── notebooks/
│   └── pipeline.ipynb         # single notebook that runs all scripts + case study walkthrough
│
├── src/                       # reusable Python modules (imported by scripts/)
│   ├── ingest/
│   │   ├── openalex.py        # OpenAlex API client
│   │   ├── patentsview.py     # PatentsView (USPTO) patent API client
│   │   ├── igem.py            # iGEM CSV loader
│   │   └── normalize.py       # converts raw records to shared schema
│   ├── embed/
│   │   └── embeddings.py      # sentence-transformer model + caching
│   ├── cluster/
│   │   └── cluster.py         # UMAP + HDBSCAN + result export
│   ├── geo/
│   │   └── geocode.py         # Nominatim geocoding with JSON cache
│   └── utils/
│       ├── schema.py           # shared column schema and dataclass
│       └── config.py           # loads settings.yaml + .env
│
├── notes/                     # research notes and literature connections
├── website/                   # Quarto documentation site (GitHub Pages)
├── manuscript/                # LaTeX manuscript
│   └── references.bib
└── slides/                    # LaTeX Beamer slides
```

## Data sources

| Source | What it provides | Access |
|--------|-----------------|--------|
| [OpenAlex](https://openalex.org) | Academic papers | Free REST API; optional API key for higher rate limits |
| [PatentsView](https://patentsview.org) | US patents (USPTO, 1976–present) | Free, open-government API — no key required |
| [iGEM Registry](https://igem.org) | Student projects and parts | CSV download |

**Patent scope note:** PatentsView covers US-granted patents only. International filings (EPO, JPO, etc.) are not included. The US is the largest single jurisdiction for synthetic biology patents (Oldham & Hall, 2018), and the tradeoff in coverage is offset by the API's openness and reproducibility — no credentials, no rate-limit negotiations, stable schema.

## Corpus construction strategy

**Papers** follow Shapira, Kwon & Youtie (2017, *Scientometrics*): a two-layer keyword approach where Layer 1 uses core self-identifying terms (`"synthetic biology"`, `"synthetic genomics"`) and Layer 2 uses subfield terms (`"BioBrick"`, `"repressilator"`, `"minimal genome"`, etc.). Broad terms like `"metabolic engineering"` are intentionally excluded from retrieval — they would swamp the corpus with unrelated work.

**Patents** follow van Doren, Koenigstein & Reiss (2013, *Systems and Synthetic Biology*): the same layered keyword approach is applied to patent titles and abstracts. IPC classification codes (C12N, C12P, etc.) are returned with each patent and available for downstream analysis, but are not used as query filters — pure IPC filtering misses synbio patents filed under broad biotechnology classes.

All parameters are in `config/settings.yaml`.

## Methods summary

| Step | Method | Key parameter |
|------|--------|---------------|
| Corpus construction | Layered keyword search | `config/settings.yaml` → `corpus` |
| Case study tagging | Keyword match on title + abstract | `carbon_capture_keywords` |
| Embeddings | `allenai-specter` (384-dim) | Cohan et al. (2020) |
| Dimensionality reduction | UMAP, cosine metric | McInnes et al. (2018) |
| Clustering | HDBSCAN | Campello et al. (2013) |
| Geocoding | Nominatim (OpenStreetMap), cached | `data/geo/geocoding_cache.json` |

## License

To be determined.
