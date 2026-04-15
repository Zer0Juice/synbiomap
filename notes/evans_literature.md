# Evans Literature — Connections to This Project

This note records how James Evans' research connects to the core questions of
this project, and includes an extended section on mixed-artifact knowledge
ecosystems and how to model them with embeddings.

---

## Relevant Papers (with verified Zotero citation details)

### 1. Wu, Wang & Evans (2019) — Team size and disruption

> Wu, L., Wang, D., & Evans, J.A. (2019). Large teams develop and small teams
> disrupt science and technology. *Nature*, 566(7744), 378–382.
> DOI: 10.1038/s41586-019-0941-9
> Zotero key: SXJE34V6

**Key finding.** Analysing 65 million papers, patents, and software products
(1954–2014), Wu et al. show that large teams tend to *develop* existing ideas
(citing recent, popular work; low CD index) while small teams *disrupt* —
searching more deeply into the past, introducing novel combinations that
redirect a field away from prior work (high CD index). The effect is not
explained by topic or design differences alone; it operates at the level of
the individual as people move between team sizes.

**Connection to this project.**

- iGEM teams are small by construction (typically 5–15 undergraduate
  students). This project has direct access to team-level metadata through
  the iGEM Registry (team name, year, institution, project description).
- The disruption/development distinction maps naturally onto the innovation
  dynamics question: are iGEM projects acting as disruptors that open new
  semantic directions, or consolidators that develop existing subfields?
- The CD index (Funk & Owen-Smith 2017) requires a citation network. iGEM
  projects do not have traditional citations, but see the embedding section
  below for proxy approaches.
- Carbon capture: is carbon capture in iGEM associated with small, disruptive
  teams introducing novel biological routes, or with larger teams consolidating
  known metabolic engineering strategies?

---

### 2. Hao, Xu, Li & Evans (2026) — AI tools and scientific focus

> Hao, Q., Xu, F., Li, Y., & Evans, J. (2026). Artificial intelligence tools
> expand scientists' impact but contract science's focus. *Nature*, 649(8099),
> 1237–1243. DOI: 10.1038/s41586-025-09922-y
> Zotero key: UJZ38ZCG

**Key finding.** Using a pre-trained LM classifier on 41.3 million papers,
Hao et al. find that AI-augmented researchers publish 3× more, receive 4.8×
more citations, and reach leadership positions 1.4 years earlier — but AI
adoption shrinks the collective volume of scientific topics studied by 4.6%
and reduces researcher-to-researcher engagement by 22%. AI tools move science
collectively toward data-rich, already-established areas. "AI tools seem to
automate established fields rather than explore new ones."

**Connection to this project.**

- Synthetic biology has enthusiastically adopted computational tools:
  AlphaFold for protein structure, Benchling and SnapGene for DNA design,
  and increasingly LLMs for sequence design and literature synthesis.
- Testable prediction in this corpus: if the Hao et al. finding holds in
  synbio, cluster diversity should decrease post-2020 — the variance of UMAP
  coordinates across all artifact types should shrink, and the carbon capture
  subset should become more semantically concentrated.
- The local-trajectory implication: if AI narrows focus globally, does it
  also erode city-level specialisation? Or is it path-dependent, pushing each
  city deeper into its existing strengths?

---

### 3. Evans & Duede (2025) — After science

> Evans, J., & Duede, E. (2025). After science. *Science*, 390(6774),
> eaec7650. DOI: 10.1126/science.aec7650
> Zotero key: 775BHZE4

**Key finding.** A broad empirical-philosophical argument that science is
entering a phase where formal knowledge production is increasingly entangled
with — and in some respects displaced by — a wider ecosystem of data, models,
infrastructure, and non-academic actors. The traditional linear model
(discovery → publication → application) no longer captures how knowledge
moves. Institutional boundaries between "basic science," "applied research,"
and "commercial development" are eroding.

**Connection to this project.**

- Provides the theoretical vocabulary for treating iGEM projects, papers, and
  patents as co-constituting a single knowledge ecosystem rather than as
  separate pipelines. This is the key framing move in the Introduction.
- "After science" implies that the artifact boundaries we use (paper vs.
  patent vs. student project) are analytically constructed, not natural
  divisions. The embedding approach operationalises this: if these artifact
  types genuinely share semantic space, the embedding model should place
  related items near each other regardless of type.
- The project's core finding — if confirmed — would be an empirical
  instantiation of Evans & Duede's claim: knowledge artifacts from different
  institutional registers do form coherent local trajectories.
- Use in the Introduction and Discussion, especially when justifying the
  mixed-corpus design.

---

### 4. Santolini et al. (2023) — iGEM as a model system for team science

> Santolini, M., Blondel, L., Palmer, M.J., Ward, R.N., Jeyaram, R.,
> Brink, K.R., Krishna, A., & Barabasi, A.-L. (2023). iGEM: a model system
> for team science and innovation. arXiv:2310.19858.
> DOI: 10.48550/arXiv.2310.19858
> Zotero key: TTR9W6ZY

**Key finding.** Combines digital lab notebooks with performance data from
2,406 iGEM teams to reveal "shared dynamical and organizational patterns
across teams" and identify features associated with success. Treats iGEM as
a natural experiment: teams form annually under roughly comparable conditions,
generating unusually comparable observational data. Makes visible
organizational behaviour that is typically hidden (who does what, when,
in what sequence).

**Connection to this project.**

- Direct methodological bridge between the Wu/Wang/Evans team science
  literature and the iGEM data we use.
- Validates the use of iGEM as a research site for innovation dynamics.
- Provides team-level metadata (size, inter-institutional collaboration,
  sequence of activities) that could be joined to the project corpus.
- Citable when introducing the iGEM data source and justifying why iGEM
  projects are a meaningful unit of analysis.

---

### 5. Boschma, Heimeriks & Balland (2014) — Relatedness in biotech cities

> Boschma, R., Heimeriks, G., & Balland, P.-A. (2014). Scientific knowledge
> dynamics and relatedness in biotech cities. *Research Policy*, 43(1),
> 107–114. DOI: 10.1016/j.respol.2013.07.009
> Zotero key: 6JTXZPYM

**Key finding.** New scientific topics tend to emerge in cities where
cognitively related topics already exist (measured by co-occurrence of title
words across journal articles). Existing topics disappear faster when weakly
related to a city's existing portfolio. Strong evidence for the "relatedness
principle" in biotech knowledge dynamics, across 276 cities, 1989–2008.

**Connection to this project.**

- This is the closest existing precedent for what this project attempts:
  city-level relatedness analysis in a life-sciences field using
  scientometric data.
- Boschma et al. use co-occurrence of words across publications as their
  relatedness measure. This project uses embedding-based cosine similarity —
  a more semantically rich measure that should capture relatedness across
  artifact types that don't share a common bibliographic database.
- Directly relevant when justifying the geographic analysis and the
  relatedness framework. Their finding ("new topics emerge where related
  topics already exist") is exactly the pattern we would expect to see if
  local innovation trajectories are real.
- Key methodological difference to flag: Boschma et al. use a single artifact
  type (publications). This project extends to three types, which requires
  the shared embedding approach described below.

---

### 6. Raimbault, Cointet & Joly (2016) — Mapping the emergence of synthetic biology

> Raimbault, B., Cointet, J.-P., & Joly, P.-B. (2016). Mapping the emergence
> of synthetic biology. *PLOS ONE*, 11(9), e0161522.
> DOI: 10.1371/journal.pone.0161522
> Zotero key: 9JGIUBMB

**Key finding.** Scientometric analysis of the WoS synbio corpus identifies
four structural approaches within the field: biobrick engineering (central),
genome engineering, protocell creation, and metabolic engineering. Notes that
synthetic biology functions as an "umbrella term" that mobilises resources
across these clusters. Central scientists act as "boundary spanners" bridging
academic and non-academic spheres.

**Connection to this project.**

- Confirms that the synthetic biology corpus has genuine cluster structure —
  it is not a homogeneous cloud of papers, and HDBSCAN should recover
  meaningful groupings.
- The "umbrella term" observation explains why broad keyword retrieval works:
  the term "synthetic biology" is genuinely used across all four clusters,
  not just one.
- The boundary spanner finding connects to this project's multi-artifact
  design: if scientists who span academic and commercial spheres are central
  to synbio, then the paper/patent boundary in our corpus corresponds to
  a structural feature of the field itself.

---

## Mixed-Artifact Knowledge Ecosystems: Theory and Embedding Models

This section develops the theoretical framing for treating projects, papers,
and patents as a single mixed-artifact corpus, and describes the main
approaches for modelling such a corpus with embeddings.

---

### What is a mixed-artifact knowledge ecosystem?

The standard bibliometric approach treats each artifact type separately:
papers in citation databases, patents in patent databases, projects (if at
all) in project databases. Analysis is done within each type, and linkages
across types are established through named-entity matching (same institution,
same inventor/author, same cited patent) or co-invention networks.

Evans & Duede (2025) argue that this separation is increasingly artificial.
Knowledge in contemporary science does not flow neatly from basic research
(papers) to applied research (patents) to products. It circulates: patents
are cited in papers, papers are produced by teams with commercial affiliations,
student projects introduce ideas that loop back into the academic literature.
The artifact types are **co-constituted** — their meaning, value, and
trajectory are shaped by the ecosystem in which they appear.

The key claim of this project, following this framing:

> If projects, papers, and patents in synthetic biology form a shared
> knowledge ecosystem, then their *content* should be semantically related —
> and that relatedness should be visible in a shared embedding space.

Critically, the semantic relatedness hypothesis can be tested empirically.
The artifact types can be embedded into a shared vector space and their
positions compared. If the hypothesis is wrong, the three artifact types
will form three isolated islands in the embedding space with no systematic
overlap.

---

### Why embeddings are the right tool for mixed-artifact corpora

Co-citation and co-authorship networks only work within artifact types that
share a citation convention. iGEM projects, academic papers, and patents
do not cite each other in machine-readable ways. Three alternatives exist:

**1. Keyword/co-occurrence matrices (Boschma et al. approach)**
Measure relatedness between two artifacts by the overlap in their title words
or abstract terms. Easy to compute, interpretable, but loses word sense
(synonym problem: "carbon sequestration" and "CO₂ fixation" score zero
overlap) and doesn't scale well to cross-type comparisons.

**2. Topic models (LDA, NMF)**
Fit a shared topic model to the full corpus and represent each artifact as
a distribution over topics. Topics are interpretable; temporal dynamics can
be tracked by re-fitting or by using dynamic topic models (Blei & Lafferty
2006). Main limitation: topics are bag-of-words, so phrase structure and
domain-specific terminology are underweighted.

**3. Pre-trained sentence embeddings (current approach)**
Encode each artifact's title + abstract into a dense vector using a model
that has learned the statistical structure of scientific language. Cosine
similarity in this space captures semantic relatedness even when surface
vocabulary differs. This is the approach used in this project (SPECTER).

The embedding approach is preferred here because:
- It handles synonym variation naturally (no manual keyword curation needed
  after the corpus is built).
- It produces a single shared space that all artifact types inhabit without
  ad-hoc normalisation.
- It enables the visual exploration (UMAP + HDBSCAN) that is the main output
  of the project.

---

### The key modelling choice: shared vs. type-specific spaces

**Shared embedding space (current design)**
All artifact types are embedded using the same model, with no type-specific
fine-tuning. A single UMAP projection and HDBSCAN clustering is applied to
the full mixed corpus.

*Advantage:* Clusters that contain a mix of artifact types are direct evidence
of shared thematic space. The position of iGEM projects relative to papers
and patents is directly readable.

*Risk:* The three artifact types may have different surface language
conventions (patents use legal boilerplate, iGEM wikis use informal
language). A shared model might place artifacts near each other for surface
reasons (shared boilerplate) rather than shared concepts. This can be
partially checked by examining which non-carbon-capture patents cluster near
the carbon capture iGEM projects.

**Type-specific embedding (alternative)**
Train or fine-tune separate models for each artifact type, then align the
resulting spaces (e.g. via a Procrustes rotation learned from known
cross-type pairs). This is the approach used in cross-lingual embedding
alignment (Mikolov et al. 2013).

*Advantage:* Each model captures the language conventions of its artifact
type; the alignment step explicitly learns the cross-type relationship.

*Risk:* We don't have known cross-type alignment pairs. And for a thesis
project, this adds substantial complexity with uncertain benefit.

**Recommended approach:** Start with the shared SPECTER space (current
design) and use it as the primary result. Add a robustness check: compute
within-type and between-type average cosine similarities for the carbon
capture subset. If carbon capture iGEM projects are closer to carbon capture
papers and patents than to random iGEM projects, this validates the shared
space.

---

### Modelling the temporal dimension: semantic trajectories

The most interesting question is not whether the artifact types share space
at a single point in time, but whether ideas *move* from one type to another
over time within a city. This is a trajectory question.

**Approach 1: Centroid drift**
For each city and each year, compute the centroid (mean embedding vector)
of all artifacts in that city from that year. Track how the centroid moves
over time. Cities where the centroid trajectory of iGEM projects precedes
and predicts the centroid trajectory of patents are evidence for the
leading-indicator hypothesis.

*Limitation:* Centroids wash out within-city diversity. A city with two
unrelated clusters will have a centroid between them that doesn't represent
either cluster.

**Approach 2: Cluster membership transition**
Assign all artifacts to clusters (via HDBSCAN). For each cluster and each
city, compute the fraction of artifacts of each type over time. If iGEM
projects enter a cluster in year T, and papers and patents follow in years
T+3 and T+7, this is a local trajectory pattern. Compare across cities to
estimate whether the pattern is systematic or idiosyncratic.

*Advantage:* Robust to multi-modal city distributions; each cluster has a
clear thematic interpretation.

*Limitation:* Requires non-trivial cluster stability across years; HDBSCAN
clusters fitted on the full corpus may not be stable if refit on annual
subsets.

**Approach 3: Semantic novelty score**
For each artifact, compute its distance from the centroid of all artifacts
published *before* it in the same field. High distance = high semantic
novelty. This is the embedding proxy for the CD disruption index that can
be applied to iGEM projects (which have no citation network).

Formally: for artifact *i* published in year *t*, compute

    novelty(i) = 1 − cosine_similarity(embed(i), mean_embed(corpus_{t-1}))

This is a local measure of how far an artifact departs from the accumulated
knowledge base at the time of its publication. It can be computed separately
for each city to test whether local novelty in iGEM precedes local novelty
in patents (the disruption-propagation hypothesis).

**Approach 4: Cross-type alignment offset**
Project the embeddings of all papers into 2D UMAP space. Then, separately,
project all patents into the *same* 2D space (hold the UMAP fit fixed, apply
the transform to patents). Compare the centroid of patents to the centroid
of papers in each cluster. A systematic offset between patent and paper
centroids could indicate that patents operate in a slightly different
semantic register (more application-oriented) even within the same thematic
area.

*This is exploratory:* the interpretation of offset direction is not obvious
without careful qualitative validation against known patent families.

---

### What SPECTER captures and what it misses

The current model is `allenai-specter` (Cohan et al. 2020), trained on
scientific papers using citation-informed contrastive learning: papers that
cite each other are pulled together in the embedding space relative to
random pairs. This makes SPECTER well-suited for scientific abstracts but
introduces two potential biases for a mixed-artifact corpus:

1. **Patent language.** Patents use a different register from papers: claims
   language, legal boilerplate, hedged descriptions of prior art. SPECTER
   was not trained on patent text. The consequence is that patent embeddings
   may cluster together for linguistic reasons (shared patent-register
   vocabulary) rather than thematic ones. Mitigation: abstract-only embedding
   (strip the claims), which is closer to paper language.

2. **iGEM wiki language.** iGEM project wikis are written by undergraduates,
   are often informal, and mix experimental description with motivational
   framing. SPECTER may place wikis at the periphery of the scientific
   vocabulary distribution. Mitigation: use only the project abstract or
   summary paragraph if available, rather than the full wiki.

3. **No temporal structure.** SPECTER has a fixed vocabulary from its
   training data (papers up to ~2020). Terms coined after that date (e.g.
   new gene editing terminology) will be handled by the model's
   approximation to nearby vocabulary. This is unlikely to be a major issue
   for the 2000–2024 synbio corpus, but worth noting.

An alternative model is `allenai/scibert_scivocab_uncased` (Beltagy et al.
2019), which was trained on a broader scientific corpus (papers from
Semantic Scholar, not citation-aware). SciBERT may generalise better to
patent and wiki text because it was not optimised specifically for the
paper-cites-paper relationship. Testing both models and comparing cluster
stability would strengthen the Methods section.

---

### Practical validation checks

Before presenting results, the following checks should be run and reported:

1. **Type separation test.** Fit a simple logistic regression classifier
   on the embeddings predicting artifact type (project/paper/patent). If
   accuracy is ~33% (chance), types are fully mixed in the embedding space.
   If accuracy is 90%+, the types are nearly separated — the shared space
   interpretation is weak. Ideally, accuracy should be meaningfully above
   chance (showing structure) but well below perfect (showing genuine
   thematic overlap).

2. **Carbon capture coherence test.** Compute average cosine similarity
   between: (a) carbon capture papers and carbon capture patents; (b) carbon
   capture papers and non-carbon-capture papers; (c) random patent pairs.
   If (a) > (b) ≈ (c), the shared embedding space successfully captures
   the cross-type thematic relationship.

3. **Temporal consistency check.** For cities with at least 5 artifacts of
   each type, test whether the rank correlation between iGEM project themes
   and patent themes (in the following 5 years) is positive. A positive
   correlation would support the leading-indicator interpretation; a near-zero
   correlation would suggest the artifact types are thematically independent
   even within cities.

4. **SPECTER vs. SciBERT comparison.** Re-run steps 04–06 with SciBERT and
   compare: number of coherent clusters, carbon capture coherence score, and
   type-separation classifier accuracy. Report in a methods robustness
   appendix.

---

## Candidate Questions for James Evans

**1. Measuring disruption without citation networks**

The CD index requires citation behaviour. iGEM student projects don't have
formal citations. What do you recommend as a proxy? Is the semantic novelty
score (distance from prior-corpus centroid) a plausible structural proxy, and
has your group explored this direction?

---

**2. Does the small-team disruption effect hold for student competitions?**

iGEM teams are structurally small but operate under a competition format with
standardised parts and annual themes. Does the disruption mechanism (less
constrained by prior work, deeper search into the past) apply here, or does
the competition structure pull teams toward consolidation? Has your group
looked at innovation competitions as a specific context?

---

**3. Do AI tools narrow local knowledge trajectories as well as global ones?**

Your 2026 paper shows AI adoption narrows global scientific focus. Does the
same effect homogenise *local* innovation trajectories — the city-level
specialisation this project maps — or could AI be path-dependent, amplifying
what each city already does well?

---

**4. iGEM as a leading indicator — methodological validity**

This project frames iGEM projects as potentially upstream of papers and
patents in a local trajectory. Is there existing empirical support for student
competitions acting as leading indicators of commercial or academic activity?
How should we handle the reverse: iGEM teams responding to local industry
context rather than leading it?

---

**5. Semantic relatedness as a Product Space proxy**

This project measures relatedness via embedding cosine similarity rather than
export co-occurrence (Hidalgo & Hausmann). Does your group see this as a
valid operationalisation of the capability-overlap concept? Are there known
failure modes when applying economic complexity frameworks to science rather
than exports?

---

**6. Mixed-artifact corpora and the shared embedding assumption**

When you map cross-type knowledge relationships (papers + patents in the 2019
Nature study), do you embed them in a shared space or align separate spaces?
What was the most important modelling choice that made cross-type comparison
valid, and what was the biggest assumption you had to make?
