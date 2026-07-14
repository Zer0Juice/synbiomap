# Paragraph Plan — *Patents, Papers, Parts, and Planet*

Worked using the 5-step "How to write essays" procedure. This file covers **Step 1
(the math)** and **Step 2 (generate one topic per paragraph)**. Steps 3–5 (5 data
points per paragraph → English → opening/closing/spellcheck) come later.

---

## Step 1 — The Math

**Requirement:** ~70-page thesis, of which roughly **50 pages are body text** (front
matter ≈5 pp, appendices ≈5 pp, and figures/tables/references absorb the rest up to 70).

The procedure's conversion constants:

| Conversion | Constant | Result |
|---|---|---|
| Pages → paragraphs | 5 paragraphs / page | 50 × 5 = **250 body paragraphs** |
| Paragraphs → sentences | 5 sentences / paragraph | 250 × 5 = **1,250 sentences** |
| Sentences → data points (Step 3) | 1 fact / sentence | **1,250 supporting facts / citations / figure call-outs** |
| Pages → words | ~300 words / page | 50 × 300 ≈ **15,000 words of body text** |

So the whole job reduces to: **invent 250 paragraph topics** (Step 2, below), then hang
**5 data points** on each (Step 3, later).

> **Note on the procedure's "minus 2 paragraphs" rule.** For a single essay you subtract
> the opening + closing paragraph. A multi-chapter thesis instead carries that overhead
> *per chapter* — most chapters open with a roadmap paragraph and close with a synthesis
> paragraph. Those are already counted inside each chapter's budget below, so the total
> still lands at 250.

### Two reconciliations the math forced

1. **Budget vs. chapter estimates.** The page estimates in `THESIS_OUTLINE.md` sum to
   ~64 text pages (≈320 paragraphs)

### Per-chapter paragraph budget (sums to 250)

| Ch | Title | Paragraphs |
|---|---|---|
| 1 | Introduction | 20 |
| 2 | Background & Related Work | 22 |
| 3 | Data & Corpus Construction | 30 |
| 4 | Methods | 30 |
| 5 | Results: City-Level Semantic Analysis *(core)* | 46 |
| 6 | Results: BioBrick Parts & Cross-Modal Validation | 30 |
| 7 | Dual-Space Alignment *(reinstated — confirm)* | 12 |
| 8 | Case Study: Carbon Capture | 14 |
| 9 | Reproducibility & Deliverables | 10 |
| 10 | Discussion | 16 |
| 11 | Limitations | 8 |
| 12 | Conclusion & Future Work | 12 |
| | **Total** | **250** |

---

## Step 2 — Paragraph Topics (one line = one paragraph)

Each line is the single topic for one paragraph. Reorder freely; this is the raw idea
list, already arranged into a logical sequence per the procedure.

### Chapter 1 — Introduction (20)



### Chapter 2 — Background & Related Work (22)

### Chapter 3 — Data & Corpus Construction (30)

43. Why a shared schema: comparing heterogeneous artifacts requires common fields.
44. The schema fields enumerated (id, type, title, text, year, city, country, lat, lon, theme_primary/secondary, case_study_flag/confidence, retrieval_reason).
45. Where the schema lives (`src/utils/schema.py`) and why it's enforced centrally.
46. Papers source: OpenAlex, and why (open, comprehensive, structured metadata).
47. The three-layer retrieval design overview.
48. Layer 1: core keywords ("synthetic biology / genomics / genome").
49. Layer 2: subfield keywords (BioBrick, repressilator, minimal genome, …).
50. Layer 3: citation expansion (backward + forward snowballing from Layer 1).
51. Why citation expansion: captures method/seminal papers keywords miss; the p-hacking concern noted honestly.
52. Final paper count (10,319) and the pre-2000 drop decision (commit `0a026cf`) with rationale.
53. iGEM projects source: the Registry / Teams API.
54. Project count (4,606) and year span (2009–2025).
55. Team rosters fetched (`03c`) and what they enable downstream.
56. What a project "text" is: the wiki abstract, treated like a paper abstract.
57. iGEM parts source: Registry API; ~89,060 BioBrick parts.
58. The `biobrick_part_type` taxonomy (cds, composite, regulatory, reporter, rbs, terminator, device, generator, primer, dna).
59. Basic vs. composite parts; composite parts create a part→part citation network.
60. 55% of parts list an academic publication as "source" — the part→paper link.
61. The link tables built (`part_source_papers`, `paper_mentions_part`, `biobrick_papers`, `papers_from_parts`).
62. Team→part linkage: projects as bundles of parts.
63. The geocoding problem: institution → city is hard (acronyms, multi-institution teams).
64. Nominatim first attempt and its limited success.
65. OpenAlex Institutions API + ROR for structured geographic data.
66. LLM-assisted geocoding (Qwen first pass on team names, Claude Haiku for hard cases) + caches.
67. The LLM comparison experiment (`compare_geocoding_llms.py`).
68. Limitation: first listed affiliation only; multi-city collaborations not captured (Munich TUM+LMU example).
69. CC tagging fields (`case_study_flag`, `case_study_confidence`, `retrieval_reason`) and why it's traceable, not an informal filter.
70. CC subset counts: 294 papers, 141 projects flagged.
71. Normalization (`src/ingest/normalize.py`) and city-name keying (strip + lowercase).
72. Section synthesis: the final corpus shape and the multilayer network (projects↔parts↔papers).

### Chapter 4 — Methods (30)

73. The goal: a common semantic space to compare text artifacts empirically.
74. What an embedding is: text → 768-d vector capturing meaning, not keyword overlap.
75. Why not keywords (synbio vocabulary-overlap problem) and why not citations alone.
76. Model choice: SPECTER2 base + proximity adapter; trained to predict citation links.
77. Input format: "title [SEP] abstract."
78. Why scientific-text + citation supervision beats general BERT.
79. Cosine similarity as the relatedness measure between two vectors.
80. Engineering: disk cache, checkpoint every 64/256 docs, restartable, Apple-Silicon optimized (~30 min / 15k on M1).
81. The curse of dimensionality: 768-d is too sparse to cluster directly.
82. UMAP reduction to ~60 dims; two-stage pipeline (Grootendorst 2022, BERTopic).
83. Why UMAP over PCA / t-SNE (manifold structure, neighbor preservation).
84. HDBSCAN clustering: density-based; noise label = −1.
85. What gets clustered (papers/projects) vs. what doesn't (parts).
86. Cluster labeling: Claude Haiku on the 20 nearest-centroid titles, batched, cached → `cluster_labels.json`.
87. City-level aggregation via embedding centroids, L2-normalized.
88. Centroid cosine ≡ mean pairwise cosine when vectors are unit-norm (Turney & Pantel 2010).
89. Coarse-grained (centroid) vs. fine-grained (cluster co-membership) city representations.
90. Panel / temporal framing: city-year centroids.
91. OLS with HC3 heteroskedasticity-robust SE; country fixed effects.
92. Permutation / randomization tests (within-country label shuffles) — the core falsification tool.
93. Bootstrap 95% CIs (1,000 resamples).
94. Mann-Whitney U + Bonferroni correction.
95. Mantel test (Spearman rank corr. of two pairwise-similarity matrices + permutation null).
96. Difference-in-differences (Angrist & Pischke 2009, Ch. 5).
97. Lead-lag / cross-correlation framing (Granger 1969) and its exploratory, non-causal stance.
98. Shannon entropy of part-type proportions as a specialization measure.
99. The three escalating claims structure (internal validity → co-specialization → temporal precedence).
100. Operational definitions of "relatedness," "success," and "prominence" for this study.
101. Dual-space alignment method preview (OLS map W 384→768, optional MLP adapter) — detailed in Ch. 7.
102. Section synthesis: how the pieces combine into the analysis pipeline.

### Chapter 5 — Results: City-Level Semantic Analysis (46) *(core)*

103. Chapter roadmap: what each measure tests and how they escalate.
104. Coverage of papers vs. projects across cities (cells 4–7).
105. Cities with papers-only / projects-only / both (387 with both).
106. Activity by year (`activity_by_year.png`) and what the time profile shows.
107. The analysis-sample definition and thresholds.
108. Constructing per-city `paper_centroid` and `project_centroid`.
109. `semantic_overlap` = cosine of the two centroids; saved to `city_level.csv`.
110. The overlap distribution: mean 0.946, median 0.960, left-skew.
111. Histogram + QQ plot (`overlap_distribution.png`); skewness / kurtosis reported.
112. Interpreting a mean of 0.946: very high baseline similarity — the first hint of field-level dominance.
113. Top cities: Cambridge (US), Shanghai, Tianjin, Berkeley, Beijing — major synbio universities.
114. Bottom cities: Tampa, West Point, Orléans, Kfar Saba, Boca Raton — 1–2 docs each.
115. What actually separates top from bottom: document depth, not necessarily real relatedness.
116. Overlap vs. city size (`overlap_vs_size.png`); Pearson r on log(1+n).
117. The diversity-vs-relatedness tension: more topics in big cities, and what that does to overlap.
118. The project-level alignment test setup (`MIN_CITY_PAPERS = 3`).
119. The vectorized project × city similarity matrix.
120. `delta = sim_own − sim_random`; mean delta and the hypothesis test.
121. Result and figures (`project_level_alignment.png`, `alignment_similarity_distribution.png`).
122. Interpretation: projects are (weakly) more like their own city's papers than a random city's.
123. The DiD motivation: separate stable city specialization from contemporaneous local spillover.
124. DiD setup (`MIN_ANNUAL_PAPERS = 2`; four cells AA/BA/AB/BB over city-year centroids).
125. DiD result and figure (`did_alignment.png`).
126. What DiD can and cannot rule out here.
127. The regression design: DV `semantic_overlap` on `log_n_papers`, `log_n_projects`, country FE, CC shares.
128. Model 1→3 progression; R² 0.625 → 0.661 → 0.662.
129. Coefficients: β `log_n_papers` +0.016***, β `log_n_projects` +0.019***.
130. CC shares add nothing (p = 0.55, 0.78).
131. Regression figures (`coef_plot_model3`, `coef_plot_extended`, `correlation_matrix`, `regression_diagnostics`).
132. Reading the regression: document counts predict overlap — a warning sign, not yet a finding.
133. Why permute: the within-country shuffle as the null for "is this real relatedness?"
134. Observed R² (0.6252) *below* permuted mean (0.6297); perm-p = 0.684.
135. Conclusion: the cross-sectional R² is a centroid-stability artifact, not local alignment.
136. β `log_n_projects` indistinguishable from null (perm-p = 0.456).
137. β `log_n_papers` barely clears the 95th pct (perm-p = 0.026; excess ≈ 0.0008).
138. The one narrow genuine signal: paper volume.
139. Permutation figures (`permutation_cluster_overlap`, `geographic_permutation_test`).
140. Lead-lag setup: project centroid (city, t) vs. paper centroid (city, t+k), `LAGS −3..+3`.
141. Bootstrap CIs (1,000); `MIN_ANNUAL_DOCS = 1`.
142. The flat profile (0.895–0.900); nominal peak k=+3 (Δ 0.001) → inconclusive.
143. Permutation test on profile *shape* (slope + directional contrast); null = shuffle paper years within city.
144. Lead-lag figures (`lead_lag_profile`, `lead_lag_permutation`) and the non-causal caveat.
145. The cluster co-membership measure (§8 / `co_df`): fraction of a city's projects and papers in the *same* HDBSCAN cluster.
146. `cluster_overlap` and `cluster_freq_vector` construction.
147. OLS on `log_n_cl_papers`, `log_n_cl_projects`; figures (`cluster_onset`, `overlap_overall_vs_cs`); the **positive** permutation result (p ≈ 0.0005).
148. Section synthesis: why centroid similarity is dominated by the field-level baseline; the asymmetry "papers define the environment, projects follow."

### Chapter 6 — Results: BioBrick Parts & Cross-Modal Validation (30)

149. Chapter roadmap: parts as independent, text-free validation of the embedding story.
150. What a BioBrick part is, recapped; the part-type taxonomy (cell 30).
151. Parts as a text-independent fingerprint of what teams did.
152. Assigning parts to cities: parts carry `team_id` but no city → join via the projects team→city lookup.
153. Coverage of the part→city join reported.
154. Building city part-type profiles (`MIN_PARTS = 10`).
155. City × part-type count → proportion (simplex representation).
156. Shannon entropy of part-type proportions as a specialization measure.
157. Distribution of entropy across cities.
158. Heatmap of the top-30 cities by total parts (`part_type_composition.png`).
159. What the profiles reveal: cities specialize in different part types.
160. The cross-modal question: do parts and embeddings tell the same story?
161. Mantel test setup: part-type space vs. semantic cluster space.
162. Cosine sims → upper triangle → Spearman r; 999-permutation null (seed 42).
163. Mantel result and figure (`mantel_test_parts_vs_cluster.png`).
164. Interpreting the Mantel result: independent validation that the clusters are real biology.
165. OLS extension: does part-type entropy predict cluster co-membership?
166. Models P1 (base) / P2 (+entropy) / P3 (+share_cds, share_composite, share_reporter), HC3 SE.
167. Results and figure (`part_entropy_vs_cluster_overlap.png`).
168. What part entropy adds (or doesn't) over raw document counts.
169. Carbon-capture part-type signature setup: a CC city = ≥1 CC-flagged team.
170. CC vs. non-CC mean part-type shares.
171. Mann-Whitney U per part type with Bonferroni correction.
172. The expected CC signature: more cds/composite/device, fewer reporter.
173. CC part-type figures (`cc_cities_part_type_scatter`, `part_type_cc_comparison`).
174. Whether the CC signature holds at small n.
175. The 671 papers citing biobricks from PubMedCentral — a cross-modal link result.
176. Caveats of full-text biobrick search (underscores, open-access only, PMC-only).
177. What the parts validation does for the thesis's overall credibility.
178. Section synthesis: parts corroborate the embedding clusters but inherit the same depth limits.


### Chapter 8 — Case Study: Carbon Capture (14)

191. Why a subfield slice: removing the shared field-level baseline that dominates Ch. 5.
192. The "Planet" framing and why carbon capture is the chosen worked example.
193. The CC subset: 294 papers, 141 projects, 7 CC cities (`city_level_carbon_capture.csv`).
194. How CC artifacts were tagged (recap of the `case_study_flag` pipeline).
195. CC city-level overlap vs. the full sample.
196. Whether removing the field baseline changes the relatedness picture.
197. The CC part-type signature (more cds/composite/device, fewer reporter).
198. Candidate enzymes / themes: RuBisCO, carbonic anhydrase, PEP carboxylase.
199. A worked single-project deep dive: its biobricks, the literature they cite, and the literature that cites them.
200. The CC timeline (`fig4_cc_timeline.html`, `fig2_umap_cc.html`).
201. The 7 CC cities named and characterized.
202. What the case study *can* show at n = 7 cities.
203. What it *cannot* show (statistical power, generalization).
204. Section synthesis: CC as the interpretable lens on an otherwise field-dominated signal.

### Chapter 9 — Reproducibility & Deliverables (10)

205. The pipeline notebook (`pipeline.ipynb`): one cell per script, restartable, cache-aware.
206. Steps 1–6: ingest → embed → UMAP+HDBSCAN → label → export (the patent-ingest step is excluded from the realized analysis).
207. Code organization: `src/` modules (ingest, embed, cluster, geo, utils) vs. notebooks.
208. Config and secrets: `config/settings.yaml`, `.env` / `.env.example`, never commit secrets.
209. The Quarto website structure (Home, Paper, Methods, Results, Case Study, Explorer, Reproducibility, Slides).
210. Interactive views on static hosting: precomputed JSON + client-side rendering.
211. The Semantic Space Explorer (UMAP, filter by type / CC).
212. The Geographic city view.
213. Export artifacts (`06_visualize.py` → `artifacts.json`, `projections.json`, `cities.json`); manuscript + Beamer outputs.
214. Repo + site links and how to reproduce end-to-end.

### Chapter 10 — Discussion (16)

215. What centroid similarity actually measures: field-level vs. local-niche similarity.
216. Why a 0.946 mean overlap is the field baseline, not a finding.
217. The permutation evidence: the cross-sectional R² is a stability artifact.
218. Why document count drives the apparent signal (centroids stabilize as n grows).
219. The one surviving signal: paper volume (β `log_n_papers`).
220. The asymmetry as a mechanism hint: papers set the niche, projects track it.
221. The mentor-coupling interpretation: faculty publish *and* mentor the same teams.
222. Cluster co-membership as the more honest measure (the positive permutation result).
223. Cross-modal coherence (Mantel) as independent validation.
224. Placement in the relatedness / economic-geography literature.
225. Comparison with Boschma et al. (2014) biotech findings.
226. Methodological lesson: embedding-based relatedness within a single field needs baseline subtraction.
227. Why naive centroid cosine is misleading in narrow corpora generally.
228. Implications for using iGEM as an innovation indicator.
229. What a positive vs. negative result means for the original hypothesis.
230. Section synthesis: an honest read of what we learned.

### Chapter 11 — Limitations (8)

231. Centroid-stability artifact in a single-field corpus.
232. Temporal resolution: annual city-year centroids often built from a single document.
233. Single-institution geocoding.
234. Omitted variables: mentor–student coupling, university prestige, cluster presence, policy.
235. Carbon-capture sample small (7 cities).
236. SPECTER2 not trained on patents or student projects (the transfer assumption).
237. Full-text biobrick-search limits (PMC-only, open-access, the underscore issue).
238. Section synthesis: what to trust and what to hedge.

### Chapter 12 — Conclusion & Future Work (12)

---

## What's next (Steps 3–5, not done here)

- **Step 3:** 5 data points per paragraph = 1,250 facts/citations/figure call-outs.
- **Step 4:** convert each paragraph's 5 points into readable English.
- **Step 5:** opening + closing paragraphs per chapter, citations, spellcheck.
