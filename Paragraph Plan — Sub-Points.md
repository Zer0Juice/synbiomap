## Abstract

**1. DNA-as-code hook**

- programmable DNA
- cells as factories
- standardized parts
- new innovation mode
- thesis motivation

**2. Research question**

- the question
- iGEM
- related papers
- semantic relatedness
- city level

**3. Why it matters**

- uneven innovation
- city clustering
- student→research path
- novel angle
- unstudied link

**4. Roadmap**

- corpus
- embeddings
- city centroids
- relatedness tests
- negative result

## Introduction

**5. SynBio defined**

- engineering biology
- genetic circuits
- DNA language
- standardized parts
- industrial cells

**6. SynBio importance**

- emergent field
- fast-moving
- economic stakes
- innovation relevance
- worth measuring

**7. iGEM intro**

- student competition
- year-long teams
- "lego" genetics
- worldwide
- project wikis

**8. iGEM significance**

- career launchpad
- sets norms
- open science
- "heart of synbio"
- industry impact

**9. Logical chain**

- synbio → innovation
- igem → synbio
- study igem
- learn innovation
- syllogism

**10. Core claim**

- topical relatedness
- local research
- projects↔papers
- claim to establish
- testable

**11. Artifacts differ**

- papers = scholarship
- patents = commerce
- projects = students
- different signals
- shared capability

**12. Realized artifacts**

- projects
- papers
- parts
- patents (planned)
- scope note

**13. "Planet" lens**

- carbon capture
- sustainability
- title motif
- case-study thread
- interpretive frame

**14. City unit**

- innovation in cities
- infrastructure needs
- agglomeration
- chosen unit
- justification

**15. Capability clustering**

- specialization
- branching
- relatedness preview
- path dependence
- adjacent tech

**16. Year aggregation**

- pool documents
- city-level
- not per-project
- enough depth
- rationale

**17. CC worked example**

- runs throughout
- demonstration
- interpretive case
- traceable slice
- preview

**18. Non-claims**

- correlational only
- no causation
- confounders
- infrastructure
- mentor coupling

**19. Contributions**

- shared-schema corpus
- relatedness measure
- falsification tests
- reproducible pipeline
- website

**20. Outcomes preview**

- centroids
- field-level baseline
- niche-level relatedness real
- co-membership
- cross-modal corroboration

## Background / Related Work

**21. Ch roadmap**

- econ geography
- relatedness
- embeddings
- iGEM
- positioning

**22. SynBio hard to define**

- fast-moving
- vocab overlap
- molecular biology
- Oldham & Hall
- delimitation

**23. Moving-field measurement**

- keyword drift
- interdisciplinary
- nomenclature
- boundary problem
- why hard

**24. Econ geography**

- spatial clustering
- agglomeration
- spillovers
- innovation geography
- foundation

**25. Relatedness principle**

- diversify nearby
- existing capabilities
- branching
- core idea
- regions

**26. Product Space**

- Hidalgo 2007
- co-occurrence
- capability proxy
- network
- relatedness

**27. Skill relatedness**

- Neffke & Henning 2013
- labor flows
- industry relatedness
- revealed
- precedent

**28. Text twist**

- embeddings
- not co-occurrence
- text relatedness
- novel application
- contribution

**29. Boschma 2014**

- scientific relatedness
- biotech
- city level
- knowledge dynamics
- methodological base

**30. Trajectories**

- path dependence
- branching paths
- city trajectories
- evolution
- framing

**31. Student engineer**

- iGEM wikis
- informal
- interdisciplinary
- data source
- novelty

**32. Santolini 2023**

- iGEM dataset
- team dynamics
- innovation
- structured data
- precedent

**33. Open-science norms**

- documentation
- registry
- standardization
- culture
- data richness

**34. BioBrick standard**

- Tom Knight
- MIT
- interoperable
- basic/composite
- modularity

**35. Parts knowledge graph**

- basic from literature
- composite from parts
- citation network
- links
- structure

**36. Corpus construction**

- keyword approach
- citation approach
- trade-offs
- coverage vs precision
- choice

**37. Embeddings as bridge**

- common representation
- heterogeneous artifacts
- vectors
- comparability
- why embeddings

**38. SPECTER2**

- Cohan 2020
- citation contrastive
- scientific text
- model choice
- foundation

**39. Shared-space precedent**

- Pat-SPECTER
- PatentSBERTa
- papers+patents
- justification
- prior work

**40. Parts fingerprint**

- physical artifact
- text-independent
- what teams did
- validation tool
- complement

**41. The gap**

- no prior link
- projects+papers+parts
- shared space
- city level
- contribution

**42. Synthesis**

- toolkit assembled
- relatedness
- embeddings
- iGEM
- transition

## Data & Corpus Construction

**43. Why shared schema**

- heterogeneous artifacts
- common fields
- comparability
- normalization
- rationale

**44. Schema fields**

- id/type/title/text
- year/city/country
- lat/lon
- theme fields
- CC flags

**45. Schema in code**

- schema.py
- central enforcement
- reproducibility
- single source
- discipline

**46. OpenAlex**

- papers source
- open access
- comprehensive
- structured metadata
- why chosen

**47. Three-layer retrieval**

- overview
- layered design
- recall+precision
- structure
- preview

**48. Layer 1 keywords**

- "synthetic biology"
- core terms
- genomics/genome
- seed
- broad net

**49. Layer 2 subfield**

- BioBrick
- repressilator
- minimal genome
- targeted terms
- depth

**50. Layer 3 citations**

- snowballing
- backward+forward
- from Layer 1
- expansion
- network

**51. Why citation expansion**

- method papers
- seminal work
- keyword gaps
- p-hacking concern
- honesty

**52. Paper count**

- 10,319 papers
- pre-2000 dropped
- commit 0a026cf
- rationale
- cleaning

**53. iGEM Registry**

- Teams API
- projects source
- official
- open data
- ingestion

**54. Project count**

- 4,606 projects
- 2009–2025
- year span
- coverage
- scale

**55. Team rosters**

- 03c script
- member lists
- downstream use
- network
- enrichment

**56. Project text**

- wiki abstract
- like paper abstract
- the "document"
- input unit
- treatment

**57. Parts source**

- Registry API
- 89,060 parts
- BioBricks
- scale
- ingestion

**58. Part-type taxonomy**

- cds/composite
- regulatory/reporter
- rbs/terminator
- device/generator
- primer/dna

**59. Basic vs composite**

- basic = new code
- composite = combos
- part→part network
- citation
- structure

**60. Part→paper link**

- 55% sourced
- publication source
- literature link
- provenance
- bridge

**61. Link tables**

- part_source_papers
- paper_mentions_part
- biobrick_papers
- papers_from_parts
- joins

**62. Team→part**

- linkage
- projects = bundles
- ownership
- city inheritance
- network

**63. Geocoding problem**

- institution→city
- acronyms
- multi-institution
- hard
- motivation

**64. Nominatim**

- first attempt
- open-access
- limited success
- mismatches
- pivot

**65. OpenAlex+ROR**

- Institutions API
- ROR coverage
- structured geo
- 100k+ institutions
- accuracy

**66. LLM geocoding**

- Qwen first pass
- Claude Haiku
- hard cases
- caches
- hybrid

**67. LLM comparison**

- compare script
- model bake-off
- accuracy test
- methodology
- validation

**68. Geocoding limit**

- first affiliation only
- multi-city missed
- Munich example
- caveat
- scope

**69. CC tagging**

- case_study_flag
- confidence
- retrieval_reason
- traceable
- not informal

**70. CC counts**

- 294 papers
- 141 projects
- flagged
- subset size
- preview

**71. Normalization**

- normalize.py
- city keying
- strip+lowercase
- consistency
- joins

**72. Corpus synthesis**

- final shape
- multilayer network
- projects↔parts↔papers
- ready
- transition

## Methods

**73. Embedding goal**

- common space
- empirical comparison
- text artifacts
- relatedness
- foundation

**74. What's an embedding**

- text→vector
- 768-d
- meaning capture
- not keywords
- intuition

**75. Why not keywords**

- vocab overlap
- synbio problem
- not citations alone
- limitations
- motivation

**76. SPECTER2 choice**

- base + adapter
- proximity adapter
- citation-trained
- model
- justification

**77. Input format**

- title [SEP] abstract
- concatenation
- standard
- consistency
- preprocessing

**78. Why SPECTER2**

- scientific text
- citation supervision
- beats general BERT
- domain fit
- rationale

**79. Cosine similarity**

- relatedness metric
- vector angle
- bounded
- interpretable
- choice

**80. Embedding engineering**

- disk cache
- checkpointing
- restartable
- M1 optimized
- ~30 min/15k

**81. Curse of dimensionality**

- 768-d sparse
- noisy
- clustering fails
- motivation
- reduction needed

**82. UMAP**

- ~60 dims
- two-stage
- Grootendorst 2022
- BERTopic
- manifold

**83. Why UMAP**

- vs PCA
- vs t-SNE
- neighbor preservation
- manifold structure
- justification

**84. HDBSCAN**

- density-based
- noise = −1
- variable clusters
- no k needed
- choice

**85. What's clustered**

- papers+projects
- not parts
- text artifacts
- scope
- rationale

**86. Cluster labeling**

- Claude Haiku
- 20 nearest titles
- batched/cached
- cluster_labels.json
- interpretability

**87. City centroids**

- mean embedding
- L2-normalized
- per type
- representation
- aggregation

**88. Centroid identity**

- centroid cosine
- ≡ mean pairwise
- unit-norm
- Turney & Pantel 2010
- justification

**89. Two representations**

- coarse centroid (foil)
- fine co-membership (headline)
- niche vs average
- granularity matters
- preview

**90. Panel framing**

- city-year centroids
- temporal
- depth caveat
- structure
- setup

**91. OLS+HC3**

- robust SE
- country FE
- regression base
- specification
- toolkit

**92. Permutation tests**

- within-country shuffle
- core falsification
- null distribution
- key tool
- rigor

**93. Bootstrap CIs**

- 1,000 resamples
- 95% intervals
- uncertainty
- nonparametric
- toolkit

**94. Mann-Whitney**

- nonparametric
- group compare
- Bonferroni
- multiple testing
- toolkit

**95. Mantel test**

- two matrices
- Spearman
- permutation null
- cross-modal
- toolkit

**96. DiD**

- Angrist & Pischke
- Ch. 5
- treatment framing
- toolkit
- preview

**97. Lead-lag**

- Granger 1969
- cross-correlation
- exploratory
- non-causal
- framing

**98. Shannon entropy**

- part-type proportions
- specialization
- diversity
- information
- toolkit

**99. Three claims**

- internal validity
- co-specialization
- temporal precedence
- escalating
- structure

**100. Operational definitions**

- relatedness
- success
- prominence
- explicit
- rigor

**101. Dual-space preview**

- OLS map W
- 384→768
- MLP adapter
- Ch. 7
- forward ref

**102. Methods synthesis**

- pipeline combine
- pieces
- flow
- transition
- recap

## Results: City-Level Semantic Analysis

**103. Ch roadmap**

- two measures
- foil → real signal
- what's tested
- structure
- preview

**104. Coverage**

- papers vs projects
- per city
- cells 4–7
- distribution
- sample

**105. Overlap sets**

- papers-only
- projects-only
- both (387)
- Venn
- analysis set

**106. Activity by year**

- time profile
- activity_by_year.png
- growth
- coverage
- trend

**107. Sample definition**

- thresholds
- inclusion rules
- analysis sample
- filtering
- setup

**108. Centroids built**

- paper_centroid
- project_centroid
- per city
- construction
- inputs

**109. Overlap measure**

- cosine of centroids
- semantic_overlap
- city_level.csv
- definition
- saved

**110. Overlap distribution**

- mean 0.946
- median 0.960
- left-skew
- shape
- summary

**111. Distribution plots**

- histogram
- QQ plot
- overlap_distribution.png
- skew/kurtosis
- diagnostics

**112. Interpreting 0.946**

- very high
- baseline similarity
- field-dominance hint
- red flag
- foreshadow

**113. Top cities**

- Cambridge US
- Shanghai/Tianjin
- Berkeley/Beijing
- synbio hubs
- pattern

**114. Bottom cities**

- Tampa/West Point
- Orléans/Kfar Saba
- Boca Raton
- 1–2 docs
- thin data

**115. Top vs bottom**

- depth difference
- not real relatedness
- artifact warning
- interpretation
- caution

**116. Overlap vs size**

- overlap_vs_size.png
- Pearson r
- log(1+n)
- relationship
- scaling

**117. Diversity tension**

- big cities
- more topics
- relatedness effect
- trade-off
- discussion

**118. Alignment setup**

- MIN_CITY_PAPERS=3
- project-level
- own vs other
- design
- threshold

**119. Similarity matrix**

- project×city
- vectorized
- efficient
- computation
- method

**120. Delta measure**

- sim_own − sim_random
- mean delta
- hypothesis test
- statistic
- definition

**121. Alignment result**

- result
- project_level_alignment.png
- similarity_distribution
- figures
- finding

**122. Alignment interpretation**

- weak own-city
- projects↔local papers
- modest signal
- reading
- caveat

**123. DiD motivation**

- stable vs spillover
- separate effects
- specialization
- contemporaneous
- why DiD

**124. DiD setup**

- MIN_ANNUAL_PAPERS=2
- AA/BA/AB/BB
- city-year centroids
- four cells
- design

**125. DiD result**

- did_alignment.png
- estimate
- figure
- finding
- reading

**126. DiD limits**

- can't rule out
- confounders
- caveat
- scope
- honesty

**127. Regression design**

- DV overlap
- log_n_papers/projects
- country FE
- CC shares
- specification

**128. Model progression**

- M1→M3
- R² 0.625→0.661→0.662
- nested
- improvement
- table

**129. Coefficients**

- β papers +0.016***
- β projects +0.019***
- significant
- signs
- magnitude

**130. CC shares null**

- p=0.55
- p=0.78
- nothing added
- non-significant
- finding

**131. Regression figures**

- coef_plot_model3
- coef_plot_extended
- correlation_matrix
- regression_diagnostics
- visuals

**132. Reading regression**

- stars look fine (***)
- counts predict overlap
- suspicious
- permutation needed
- not yet a finding

**133. Why permute**

- within-country null
- real relatedness?
- falsification
- rationale
- key move

**134. Observed vs null**

- R² 0.6252
- permuted 0.6297
- below mean!
- perm-p 0.684
- result

**135. Artifact conclusion**

- centroid-stability
- document-count artifact
- stars unmasked
- foil, not finding
- motivates niche measure

**136. Projects null**

- β projects
- perm-p 0.456
- indistinguishable
- no signal
- finding

**137. Papers signal**

- β papers
- perm-p 0.026
- barely clears
- marginal
- secondary, not headline

**138. Marginal paper signal**

- paper volume
- weak
- survives barely
- minor note
- not the headline

**139. Permutation figures**

- permutation_cluster_overlap
- geographic_permutation_test
- visuals
- nulls
- evidence

**140. Lead-lag setup**

- project(t) vs paper(t+k)
- LAGS −3..+3
- temporal
- design
- centroids

**141. Lead-lag stats**

- bootstrap CIs
- 1,000
- MIN_ANNUAL_DOCS=1
- uncertainty
- thresholds

**142. Flat profile**

- 0.895–0.900
- peak k=+3
- Δ 0.001
- inconclusive
- result

**143. Profile permutation**

- shape test
- slope+contrast
- shuffle years
- null
- rigor

**144. Lead-lag figures**

- lead_lag_profile
- lead_lag_permutation
- non-causal caveat
- visuals
- reading

**145. Co-membership measure**

- §8 / co_df
- same specific clusters
- cluster-freq vectors
- discards field baseline
- niche-level instrument

**146. Co-membership robustness**

- ≥8 docs/type (~60 cities)
- not explained by size
- threshold sweep 3/5/8/12/20
- sparsity floor
- monotone strengthening

**147. Co-membership result (HEADLINE)**

- perm p≈0.0005
- ~50% above null
- genuine local relatedness
- robust to size
- the thesis's finding

**148. Ch synthesis**

- relatedness real at niche level
- centroid was the foil
- mentor-coupling mechanism
- papers lead, projects follow
- qualified yes

## Results: BioBrick Parts & Cross-Modal Validation

**149. Ch roadmap**

- parts validation
- text-free
- independent
- structure
- preview

**150. BioBrick recap**

- part definition
- taxonomy
- cell 30
- reminder
- setup

**151. Parts as fingerprint**

- text-independent
- what teams did
- physical
- complement
- rationale

**152. Parts→cities**

- team_id only
- no city
- join via projects
- lookup
- method

**153. Join coverage**

- coverage %
- matched parts
- reported
- completeness
- caveat

**154. City profiles**

- MIN_PARTS=10
- threshold
- profile build
- filtering
- setup

**155. Simplex**

- city×part-type
- counts→proportions
- normalized
- vector
- representation

**156. Entropy measure**

- Shannon
- part-type proportions
- specialization
- diversity
- statistic

**157. Entropy distribution**

- across cities
- spread
- specialization range
- histogram
- summary

**158. Parts heatmap**

- top-30 cities
- part_type_composition.png
- visual
- composition
- pattern

**159. Profiles reveal**

- city specialization
- different part types
- heterogeneity
- finding
- interpretation

**160. Cross-modal question**

- parts vs embeddings
- same story?
- validation
- motivation
- key test

**161. Mantel setup**

- part-type space
- cluster space
- two matrices
- design
- method

**162. Mantel stats**

- cosine sims
- upper triangle
- Spearman r
- 999 perms
- seed 42

**163. Mantel result**

- mantel figure
- correlation
- significance
- finding
- reading

**164. Mantel interpretation**

- independent validation
- real biology
- clusters confirmed
- credibility
- reading

**165. Entropy→co-membership**

- OLS extension
- predictor test
- specialization
- question
- design

**166. Part models**

- P1 base
- P2 +entropy
- P3 +shares
- HC3
- nested

**167. Part results**

- part_entropy figure
- coefficients
- finding
- reading
- assessment

**168. Entropy added value**

- over counts
- incremental
- or not
- assessment
- honesty

**169. CC signature setup**

- CC city
- ≥1 CC team
- definition
- subset
- design

**170. CC vs non-CC**

- mean shares
- comparison
- part types
- contrast
- finding

**171. CC stats**

- Mann-Whitney
- per part type
- Bonferroni
- multiple testing
- rigor

**172. Expected signature**

- more cds/composite/device
- fewer reporter
- hypothesis
- mechanism
- prediction

**173. CC part figures**

- cc_cities_scatter
- part_type_cc_comparison
- visuals
- comparison
- evidence

**174. Small-n caveat**

- holds?
- 7 cities
- power
- caution
- honesty

**175. Biobrick-citing papers**

- 671 papers
- PubMedCentral
- direct citations
- cross-modal link
- result

**176. Search caveats**

- underscores
- open-access only
- PMC-only
- undercount
- limitation

**177. Validation value**

- credibility
- triangulation
- independent
- strengthens
- argument

**178. Ch synthesis**

- parts corroborate
- clusters real
- same depth limits
- takeaway
- transition

## Dual-Space Alignment _(confirm source)_

**179. Why Ch 7**

- referenced §4.7
- not written
- dual-space
- gap
- purpose

**180. The problem**

- 384-d space
- 768-d SPECTER2
- alignment
- mismatch
- motivation

**181. OLS map**

- W matrix
- 384→768
- linear
- fit
- method

**182. MLP adapter**

- nonlinear
- alternative
- neural
- option
- method

**183. Train/val split**

- fitting
- validation
- overfitting
- protocol
- rigor

**184. Eval metric**

- alignment quality
- measure
- benchmark
- definition
- setup

**185. Linear results**

- OLS map
- performance
- numbers
- finding
- reading

**186. MLP results**

- adapter performance
- vs linear
- comparison
- finding
- choice

**187. What it enables**

- cross-model compare
- artifact bridging
- use case
- value
- purpose

**188. Alignment limits**

- caveats
- error
- assumptions
- limitation
- honesty

**189. When it matters**

- vs single-space
- necessity
- trade-off
- decision
- scope

**190. Ch synthesis**

- used or not
- decision
- main analysis
- takeaway
- transition

## Case Study: Carbon Capture

**191. Why subfield slice**

- remove baseline
- field dominance
- isolate niche
- motivation
- key move

**192. "Planet" framing**

- carbon capture
- sustainability
- chosen example
- relevance
- narrative

**193. CC subset**

- 294 papers
- 141 projects
- 7 CC cities
- cc csv
- scope

**194. CC tagging recap**

- case_study_flag
- pipeline
- how tagged
- traceable
- reminder

**195. CC overlap**

- vs full sample
- comparison
- overlap measure
- finding
- contrast

**196. Baseline removed?**

- relatedness picture
- changes?
- subfield effect
- assessment
- key question

**197. CC part signature**

- more cds/composite/device
- fewer reporter
- composition
- finding
- mechanism

**198. Candidate enzymes**

- RuBisCO
- carbonic anhydrase
- PEP carboxylase
- themes
- biology

**199. Project deep dive**

- one project
- its biobricks
- cited literature
- citing literature
- worked example

**200. CC timeline**

- fig4_cc_timeline
- fig2_umap_cc
- temporal
- visual
- narrative

**201. CC cities**

- 7 named
- characterized
- profiles
- geography
- detail

**202. What it shows**

- n=7
- illustrative
- mechanism hints
- value
- scope

**203. What it can't show**

- power
- generalization
- limits
- caution
- honesty

**204. Ch synthesis**

- interpretable lens
- field-dominated signal
- CC value
- takeaway
- transition

## Reproducibility & Deliverables

**205. Pipeline notebook**

- pipeline.ipynb
- one cell/script
- restartable
- cache-aware
- reproducibility

**206. Pipeline steps**

- ingest→embed
- UMAP+HDBSCAN
- label→export
- steps 1–6
- patents excluded

**207. Code organization**

- src/ modules
- ingest/embed/cluster
- geo/utils
- vs notebooks
- structure

**208. Config & secrets**

- settings.yaml
- .env
- .env.example
- no secrets committed
- safety

**209. Quarto site**

- Home/Paper/Methods
- Results/Case Study
- Explorer/Repro/Slides
- navigation
- product

**210. Static interactivity**

- precomputed JSON
- client-side render
- GitHub Pages
- constraint
- approach

**211. Semantic Explorer**

- UMAP view
- filter by type
- filter CC
- interactive
- feature

**212. Geographic view**

- city map
- selection
- composition
- interactive
- feature

**213. Export artifacts**

- 06_visualize.py
- artifacts.json
- projections.json
- cities.json + manuscript/Beamer

**214. Repo & repro**

- repo link
- site link
- end-to-end
- instructions
- access

## Discussion

**215. What centroid measures**

- field-level
- vs local-niche
- similarity meaning
- interpretation
- core

**216. 0.946 = baseline**

- field baseline
- not finding
- high floor
- interpretation
- key

**217. Permutation evidence**

- centroid R² artifact
- conventional stars unmasked
- foil
- motivates niche measure
- not the headline

**218. Why counts drive it**

- averaging washes niche
- centroid → global centroid
- n → stability
- mechanical inflation
- artifact source

**219. Marginal paper signal**

- paper volume
- β log_n_papers
- marginal
- secondary
- not the headline

**220. Asymmetry hint**

- papers set niche
- projects track
- mechanism
- directionality
- interpretation

**221. Mentor coupling**

- faculty publish niche X
- mentor teams in X
- microfoundation
- explains co-membership
- centroid can't see it

**222. Co-membership headline**

- genuine positive result
- niche-level relatedness
- p≈0.0005, robust
- the answer: qualified yes
- better instrument

**223. Mantel coherence**

- cross-modal
- independent
- validation
- credibility
- support

**224. Lit placement**

- relatedness lit
- econ geography
- positioning
- contribution
- context

**225. Boschma comparison**

- 2014 biotech
- city level
- contrast
- agreement?
- positioning

**226. Methodological lesson**

- single-field
- baseline subtraction
- needed
- generalizable
- contribution

**227. Naive cosine misleading**

- narrow corpora
- field baseline dominates
- conventional stars mislead
- permutation catches it
- methodological lesson

**228. iGEM as indicator**

- innovation proxy
- usefulness
- caveats
- implications
- assessment

**229. Answering the hypothesis**

- qualified yes
- niche-level not average
- not a negative result
- measure-dependent
- interpretation

**230. Ch synthesis**

- relatedness real (niche)
- measurement contribution
- foil + headline arc
- qualified yes
- transition

## Limitations

**231. Centroid artifact**

- single-field
- stability
- main limitation
- caveat
- honesty

**232. Temporal resolution**

- city-year
- one document
- noisy
- limitation
- caveat

**233. Single-institution**

- first affiliation
- multi-city missed
- geocoding limit
- caveat
- scope

**234. Omitted variables**

- mentor coupling
- prestige
- cluster presence
- policy
- confounders

**235. CC small n**

- 7 cities
- power
- generalization
- limitation
- caveat

**236. SPECTER2 transfer**

- not trained patents
- not trained projects
- assumption
- limitation
- caveat

**237. Search limits**

- PMC-only
- open-access
- underscore issue
- undercount
- caveat

**238. Ch synthesis**

- what to trust
- what to hedge
- honest bounds
- takeaway
- transition

## Conclusion & Future Work

**239. Restated question**

- the question
- qualified-yes answer
- recap
- closing
- frame

**240. Headline**

- niche-level relatedness real
- co-membership p≈0.0005
- centroid = foil
- measurement lesson
- qualified yes

**241. Deviation vectors**

- subtract global centroid
- isolate niche
- future method
- fix
- direction

**242. Co-membership primary**

- better measure
- go-forward
- positive result
- recommendation
- direction

**243. Subfield designs**

- field similarity gone
- focused corpus
- better test
- future
- direction

**244. PI-level data**

- institution
- mentor coupling
- mechanism test
- future
- direction

**245. Patents strand**

- fourth artifact
- "what's next"
- translation layer
- headline future
- direction

**246. Patent script**

- 02_ingest_patents.py
- Lens.org
- IPC+keyword
- van Doren 2013
- exists

**247. Patent next step**

- geocode
- embed shared space
- downstream layer
- projects→papers→patents
- plan

**248. Wiki DOI scraping**

- in-progress
- 263 teams
- citation network
- dataset
- direction

**249. Other directions**

- Revelio hiring
- PatSeq matching
- author matching
- future
- breadth

**250. Closing**

- careful negative
- reproducible pipeline
- value
- contribution
- end