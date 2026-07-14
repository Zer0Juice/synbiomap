# Notebooks

Walkthroughs and the case study. Reusable logic lives in `src/`; these notebooks
narrate and inspect the results.

| Notebook | Kind | What it does |
|----------|------|--------------|
| `pipeline.ipynb` | Jupyter | Orchestrator. Runs the ingest → embed → cluster → export scripts in order with a step-by-step status table. Start here to build the datasets. |
| `02_tripartite_city_analysis.py` | [marimo](https://marimo.io) | The main analysis. Places iGEM projects, papers, and patents in one fine-tuned SPECTER2 semantic space and tests whether a city's three artifact types share topics more than chance. |
| `03_carbon_capture.py` | marimo | The carbon-capture case study. Which cities lead carbon-capture work, and who sits at the centre of the citation network. |

## Running the marimo notebooks

```bash
pip install marimo          # already in requirements.txt
marimo edit notebooks/02_tripartite_city_analysis.py   # interactive
marimo run  notebooks/02_tripartite_city_analysis.py   # read-only app
```

Rendered HTML exports of the two marimo notebooks live in `outputs/`
(`notebook_02.html`, `notebook_03.html`) and are embedded in the website.

## Numbering

The `02_`/`03_` prefixes are kept to match the committed HTML exports. Earlier
`01_city_level_analysis.ipynb` and `02_dual_space_alignment.ipynb` notebooks
covered a two-artifact (projects vs. papers) study that the tripartite analysis
above supersedes; they were removed during cleanup and remain in git history.
