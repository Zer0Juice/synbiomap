# Thesis Outline — *Proteins, Papers, Parts, and Planet*

**Target length:** ~70 pages (±10% → 63–77 pp)

**Scope note:** Structural outline of *what was actually done*, anchored mainly to
the notebooks (`notebooks/01_city_level_analysis.ipynb`, `notebooks/02_dual_space_alignment.ipynb`,
`notebooks/pipeline.ipynb`) and the supporting `scripts/` and `src/` modules. Figure filenames
refer to files in `outputs/figures/`. Numbers are the current corpus counts.

**Realized corpus (current `data/processed/`):**
- `papers.csv` — 10,319 papers, 2000–2026, 294 carbon-capture flagged
- `projects.csv` — 4,606 iGEM projects, 2009–2025, 141 carbon-capture flagged
- `parts.csv` — 89,060 BioBrick parts, 2003–2025
- `all_artifacts.csv` — 13,335 combined rows
- `city_level.csv` — 387 cities (have BOTH papers and projects = analysis sample)
- `city_level_carbon_capture.csv` — 7 carbon-capture cities

The realized analysis covers **papers + projects + parts**

---

## Front Matter (~5 pp)

- Title page — *Patents, Papers, Parts, and Planet*
- Abstract — research question, data, method, headline result (semantic overlap is
  dominated by field-level similarity; permutation tests show the cross-sectional
  result is a centroid-stability artifact; one narrow genuine paper-volume signal)
- Acknowledgements
- Table of contents
- List of figures (index of the ~30 figures in `outputs/figures/`)
- List of tables
- Note on non-causal language (relatedness / association / co-location, not causation)

---

## Chapter 1 — Introduction (~5 pp)

- 1.1 Research question — *Do cities where iGEM student projects are active also produce
  academic papers in semantically related areas of synthetic biology?* (from notebook 01, cell 0)
- 1.2 Motivation — innovation as a possible local path: student projects → academic
  publications (downstream patents left to future work, Ch. 12)
- 1.3 The three realized artifact types (projects, papers, parts); "Planet" = the
  carbon-capture / sustainability lens. Patents are the planned fourth strand, not yet analysed
- 1.4 Unit of analysis: the city (aggregated across years)
- 1.5 The carbon-capture case study as the worked example
- 1.6 What this thesis does NOT claim — descriptive/correlational only; shared confounders
  (research infrastructure, university quality, mentor coupling)
- 1.7 Contributions (a shared-schema multi-artifact corpus; an embedding-based city
  relatedness measure; a battery of falsification/permutation tests; a reproducible
  pipeline + website)
- 1.8 Thesis roadmap

---

## Chapter 2 — Background and Related Work (~6 pp)
*(mirrors `manuscript/main.tex` §2)*

- 2.1 Synthetic biology as a fast-moving, self-named field
- 2.2 Economic geography of innovation and **relatedness** — product space and skill
  relatedness applied to *text* rather than product/occupation co-occurrence
  - Hidalgo et al. (2007), *The Product Space*; Neffke & Henning (2013), *Skill Relatedness*
- 2.3 iGEM and the "student engineer" — informal, interdisciplinary project wikis
- 2.4 Measuring a field that keeps moving — keyword vs. citation-based corpus construction
- 2.5 A common representation for heterogeneous artifacts — document embeddings
  - SPECTER / SPECTER2 (Cohan et al. 2020; allenai/specter2), citation-informed contrastive training
- 2.6 BioBrick parts as a physical, text-independent fingerprint of what teams did

---

## Chapter 3 — Data and Corpus Construction (~8 pp)
*(from `notebooks/pipeline.ipynb` + `scripts/01, 03` + `src/ingest/`)*

- 3.1 Shared schema across datasets (`src/utils/schema.py`)
  - `id, type, title, text, year, city, country, lat, lon, theme_primary,
    theme_secondary, case_study_flag, case_study_confidence, retrieval_reason`
- 3.2 Papers — OpenAlex (`scripts/01_ingest_papers.py`, `src/ingest/openalex.py`)
  - Three-layer retrieval: (1) core keywords ("synthetic biology/genomics/genome"),
    (2) subfield keywords (BioBrick, repressilator, minimal genome, …),
    (3) citation expansion (backward + forward snowballing from Layer 1)
  - 10,319 papers; pre-2000 papers dropped (commit `0a026cf`)
- 3.3 iGEM projects — Registry (`scripts/03_ingest_projects.py`, `src/ingest/igem.py`)
  - 4,606 projects, 2009–2025; team rosters (`03c_fetch_team_rosters.py`)
- 3.4 iGEM parts — Registry API (`scripts/03b_fetch_parts.py`)
  - 89,060 BioBrick parts; `biobrick_part_type` taxonomy (cds, composite, regulatory,
    reporter, rbs, terminator, device, generator, primer, dna)
  - Team→part linkage; part→paper and paper→part link tables
    (`part_source_papers.csv`, `paper_mentions_part.csv`, `biobrick_papers.csv`,
    `papers_from_parts.csv`)
- 3.5 Geocoding (`src/geo/geocode.py`, `scripts/geocode_igem_teams.py`)
  - Institution → city; LLM-assisted geocoding + caches
    (`geocoding_cache.json`, `openalex_institution_cache.json`, `igem_geocoding_cache.json`)
  - LLM comparison experiment (`scripts/compare_geocoding_llms.py`)
  - Limitation: first listed affiliation only (multi-city collaborations not captured)
- 3.6 Carbon-capture tagging — `case_study_flag`, `case_study_confidence`, `retrieval_reason`
  - 294 papers, 141 projects flagged; traceable analytical slice (not an informal filter)
- 3.7 Normalization (`src/ingest/normalize.py`) and city-name keying (strip + lowercase)

---

## Chapter 4 — Methods (~8 pp)
*(from `notebooks/pipeline.ipynb`, `src/embed/`, `src/cluster/`, and the stats used in notebook 01/02)*

- 4.1 Embeddings (`src/embed/embeddings.py`, `scripts/04_embed.py`)
  - SPECTER2 base + **proximity adapter**, 768-d; "title [SEP] abstract" input
  - Why scientific-text + citation supervision over general BERT
  - Disk cache; checkpoint every 64/256 docs; restartable; Apple-Silicon optimized
    (~30 min / 15k embeddings on M1, 8 GB)
- 4.2 Dimensionality reduction — UMAP, two-stage pipeline (Grootendorst 2022, BERTopic)
- 4.3 Clustering — HDBSCAN; noise label = −1; clusters papers/projects, not parts
  (`scripts/05_cluster.py`, `src/cluster/cluster.py`)
- 4.4 Cluster labeling — Claude Haiku on 20 nearest-centroid titles, batched, cached
  (`scripts/05b_label_clusters.py` → `cluster_labels.json`)
- 4.5 City-level aggregation — embedding **centroids**, L2-normalized
  - Centroid cosine ≡ mean pairwise cosine when vectors are unit-norm (Turney & Pantel 2010)
- 4.6 Statistical toolkit used across results
  - OLS with HC3 heteroskedasticity-robust SE; country fixed effects
  - Permutation / randomization tests (within-country label shuffles)
  - Bootstrap 95% CIs (1,000 resamples)
  - Mann-Whitney U + Bonferroni correction
  - Mantel test (Spearman rank corr. of two pairwise-similarity matrices + permutation null)
  - Difference-in-differences (Angrist & Pischke 2009, Ch. 5)
  - Lead-lag / cross-correlation framing (Granger 1969)
  - Shannon entropy of part-type proportions
- 4.7 Dual-space alignment method (detailed in Ch. 7) — OLS map W (384→768), optional MLP adapter

---

## Chapter 5 — Results: City-Level Semantic Analysis (~12 pp)
*(core chapter — `notebooks/01_city_level_analysis.ipynb`)*

- 5.1 Coverage and the analysis sample (cells 4–7)
  - Papers vs projects coverage; cities with papers-only / projects-only / **both** (387)
  - Activity by year → `activity_by_year.png`
- 5.2 The semantic-overlap measure and its distribution (cells 11–15, 20–22)
  - Per-city `paper_centroid`, `project_centroid`, `semantic_overlap` = cosine of centroids
  - Saved to `city_level.csv`
  - Distribution: mean 0.946, median 0.960, left-skew; histogram + QQ →
    `overlap_distribution.png`; skewness/kurtosis reported
- 5.3 Top / bottom cities (cell 23)
  - Top: Cambridge (US), Shanghai, Tianjin, Berkeley, Beijing (major synbio universities)
  - Bottom: Tampa, West Point, Orléans, Kfar Saba, Boca Raton (1–2 docs each)
- 5.4 Overlap vs. city size (cell 24) → `overlap_vs_size.png`
  - Diversity-vs-relatedness tension; Pearson r on log(1+n)
- 5.5 Own-city vs. other-city project alignment (cells 16–17)
  - `MIN_CITY_PAPERS = 3`; vectorized project×city similarity matrix
  - `delta = sim_own − sim_random`; mean delta + hypothesis test
  - Figures: `project_level_alignment.png`, `alignment_similarity_distribution.png`
- 5.6 Difference-in-differences test (cells 18–19) → `did_alignment.png`
  - Separates stable city specialisation from contemporaneous local spillover
  - `MIN_ANNUAL_PAPERS = 2`; four DiD cells (AA, BA, AB, BB) over all city-year centroids
- 5.7 OLS regression — predictors of overlap
  - DV `semantic_overlap` on `log_n_papers`, `log_n_projects`, country FE, CC shares
  - Model 1→3: R² 0.625 → 0.661 → 0.662; β log_n_papers +0.016***, β log_n_projects +0.019***;
    CC shares add nothing (p = 0.55, 0.78)
  - Figures: `coef_plot_model3.png`, `coef_plot_extended.png`, `correlation_matrix.png`,
    `regression_diagnostics.png`
- 5.8 Permutation test — within-country shuffle (key negative result)
  - Observed R² (0.6252) *below* permuted mean (0.6297), perm-p = 0.684 → R² is a
    **centroid-stability artifact**
  - β log_n_projects indistinguishable from null (perm-p = 0.456)
  - β log_n_papers barely clears 95th pct (perm-p = 0.026; excess ≈ 0.0008) → one narrow genuine signal
  - Figures: `permutation_cluster_overlap.png`, `geographic_permutation_test.png`
- 5.9 Temporal lead-lag analysis (cells 25–29)
  - Project centroid at (city, t) vs paper centroid at (city, t+k), `LAGS = −3..+3`,
    `MIN_ANNUAL_DOCS = 1`, bootstrap CIs (1,000)
  - Profile nearly flat (0.895–0.900); nominal peak k=+3 (Δ 0.001) → inconclusive
  - Permutation test on profile *shape* (slope + directional contrast); null = shuffle paper
    years within city → `lead_lag_profile.png`, `lead_lag_permutation.png`
- 5.10 Cluster co-membership ("Section 8" / `co_df`)
  - Fraction of a city's projects and papers falling in the *same* HDBSCAN cluster
    (`cluster_overlap`, `cluster_freq_vector`)
  - OLS on `log_n_cl_papers`, `log_n_cl_projects`; figures `cluster_onset.png`,
    `overlap_overall_vs_cs.png`
- 5.11 Section synthesis — why centroid similarity is dominated by field-level baseline;
  asymmetry "papers define the environment, projects follow"

---

## Chapter 6 — Results: BioBrick Parts and Cross-Modal Validation (~8 pp)
*(`notebooks/01_city_level_analysis.ipynb` §9, cells 30–41)*

- 6.1 What a BioBrick part is; part-type taxonomy; parts as a text-independent fingerprint (cell 30)
- 6.2 Assigning parts to cities (cells 31–32)
  - parts have `team_id` but no city → join to `projects` team→city lookup; coverage reported
- 6.3 City part-type profiles + specialisation (cells 33–37)
  - `MIN_PARTS = 10`; city×part-type count → proportion (simplex) → Shannon entropy
  - Distribution of entropy; heatmap of top-30 cities by total parts
  - Figures: `part_type_composition.png`, `part_type_cc_comparison.png`
- 6.4 Cross-modal alignment — **Mantel test** (cells 38–39)
  - Part-type space vs. semantic cluster space; cosine sims → upper triangle →
    Spearman r; 999-permutation null (seed 42)
  - Tests whether the embedding clusters and the physical parts tell the same story
  - Figure: `mantel_test_parts_vs_cluster.png`
- 6.5 OLS extension — does part-type entropy predict cluster co-membership? (cell 39)
  - Models P1 (base) / P2 (+entropy) / P3 (+share_cds, share_composite, share_reporter),
    HC3 SE → `part_entropy_vs_cluster_overlap.png`
- 6.6 Carbon-capture part-type signature (cells 40–41)
  - CC city = ≥1 CC-flagged team; CC vs non-CC mean part-type shares
  - Mann-Whitney U per part type with Bonferroni correction
  - Figures: `cc_cities_part_type_scatter.png`, `part_type_cc_comparison.png`,
    `part_entropy_vs_cluster_overlap.png`

---


## Chapter 8 — Case Study: Carbon Capture (~4 pp)
*(integrates `Carbon Capture Case Study.md` + CC slices throughout the notebooks)*

- 8.1 Why a subfield slice — removing the shared field-level baseline that dominates Ch. 5
- 8.2 The CC subset — 294 papers, 141 projects, 7 CC cities (`city_level_carbon_capture.csv`)
- 8.3 CC city-level overlap vs. the full sample
- 8.4 CC part-type signature (expected more cds/composite/device, fewer reporter)
  - Candidate enzymes/themes: RuBisCO, carbonic anhydrase, PEP carboxylase
- 8.5 CC timeline (`outputs/figures/fig4_cc_timeline.html`, `fig2_umap_cc.html`)
- 8.6 What the case study can and cannot show at n = 7 cities

---

## Chapter 9 — Reproducibility and Deliverables (~4 pp)

- 9.1 The pipeline notebook (`pipeline.ipynb`) — one cell per script, restartable, cache-aware
  - Steps 1–6: ingest papers/projects/parts → embed → UMAP+HDBSCAN → label → export
    (the pipeline also has a patent-ingest step, excluded from the realized analysis)
- 9.2 Code organisation — `src/` modules (ingest, embed, cluster, geo, utils) vs. notebooks
- 9.3 Config and secrets — `config/settings.yaml`, `.env` / `.env.example`
- 9.4 Quarto website (`website/`) — Home, Paper, Methods, Results, Case Study, Explorer,
  Reproducibility, Slides; Solarized-Light theme matched to slides
- 9.5 Interactive views (static GitHub Pages: precomputed JSON + client-side render)
  - Semantic Space Explorer (UMAP, filter by type / CC); Geographic city view
  - Export: `scripts/06_visualize.py` → `artifacts.json`, `projections.json`, `cities.json`
- 9.6 Manuscript (`manuscript/main.tex`, pdflatex) and Beamer slides (`outputs/slides/frank_talk.pdf`)
- 9.7 Repo + site: github.com/Zer0Juice/synbiomap · zer0juice.github.io/synbiomap

---

## Chapter 10 — Discussion (~5 pp)

- 10.1 What centroid similarity actually measures — field-level vs. local-niche similarity
- 10.2 The permutation evidence — cross-sectional R² is a stability artifact, not local alignment
- 10.3 The asymmetry as a mechanism hint — paper volume carries the only genuine signal;
  faculty publications set the niche, iGEM teams (mentored by the same faculty) track it
- 10.4 Cross-modal coherence (Mantel) as independent validation that clusters are real biology
- 10.5 Placement in the relatedness / economic-geography literature
- 10.6 Methodological lessons for embedding-based relatedness within a single field

---

## Chapter 11 — Limitations (~2 pp)
*(from notebook 01 summary, cell 42)*

- 11.1 Centroid-stability artifact (single-field corpus)
- 11.2 Temporal resolution — annual city-year centroids often built from one document
- 11.3 Single-institution geocoding
- 11.4 Omitted variables — mentor–student coupling, university prestige, cluster presence, policy
- 11.5 Carbon-capture sample small (7 cities)

---

## Chapter 12 — Conclusion and Future Work (~2 pp)
*(next-steps from notebook 01 cell 42 + `Write-Up.md` open questions)*

- 12.1 Deviation vectors — subtract global synbio centroid before comparing
- 12.2 Cluster co-membership as the primary measure
- 12.3 Subfield-focused designs where field-level similarity no longer dominates
- 12.4 Institution-/PI-level data to test the mentor-coupling mechanism
- 12.5 **Patents — the planned fourth artifact strand (the "what's next" headline).**
  Ingest script already exists (`scripts/02_ingest_patents.py`, Lens.org; combined IPC +
  keyword strategy following van Doren, Koenigstein & Reiss 2013; synbio patents spread
  across C12N/C12P/C12Q/C12S/C40B with no dedicated code). Next step: geocode, embed in the
  shared SPECTER2 space, and add patents as the downstream "translation" layer in the
  city-level analysis (student projects → papers → patents)
- 12.6 Restated answer to the research question

---

## Appendices (~5 pp)

- A. Full shared schema and field definitions (`src/utils/schema.py`)
- B. Corpus retrieval terms — paper keyword layers (core + subfield) and citation-expansion settings
- C. Embedding, UMAP, and HDBSCAN parameter settings
- D. Sample of Claude-Haiku cluster labels (`cluster_labels.json`)
- E. Figure index — all `outputs/figures/*.png` / `*.html` with generating cell
- F. Repository structure and reproduction instructions

