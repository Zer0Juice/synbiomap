# Evans Literature — Connections to This Project

This note records how James Evans' research connects to the core questions of
this project, and lists candidate questions to discuss with him.

---

## Relevant Papers

### 1. Wu, Wang & Evans (2019) — Team size and disruption

> Wu, L., Wang, D., & Evans, J.A. (2019). Large teams develop and small teams
> disrupt science and technology. *Nature*, 566, 378–382.
> DOI: 10.1038/s41586-019-0941-9

**Key finding.** Using 65 million papers and 3.9 million patents, Wu et al.
show that large teams tend to *develop* existing ideas (high citation to
recent work, low CD index) while small teams are more likely to *disrupt* —
introducing novel combinations that redirect a field away from prior work
(high CD index, atypical citation patterns).

**Connection to this project.**

- iGEM teams are small by construction (typically 5–15 undergraduate
  students). This project has direct access to team-level metadata through
  the iGEM Registry (team name, year, institution, project description).
- The disruption/development distinction maps naturally onto the innovation
  dynamics question: are iGEM projects acting as disruptors that open new
  semantic directions, or consolidators that develop existing subfields?
- The CD index (Funk & Owen-Smith 2017) measures whether a work's citers
  also cite its references (consolidation) or abandon those references
  (disruption). Because iGEM projects do not have traditional citation
  networks, we cannot compute CD index directly — but *semantic novelty*
  in the embedding space (distance from centroid of contemporaneous work)
  may serve as a structural proxy.
- Carbon capture: is carbon capture in iGEM associated with small, disruptive
  teams introducing novel biological approaches, or with larger teams
  consolidating known metabolic engineering strategies?

---

### 2. Hao, Xu, Li & Evans (2026) — AI tools and scientific focus

> Hao, Y., Xu, F., Li, W., & Evans, J.A. (2026). Artificial intelligence
> tools expand scientists' impact but contract science's focus.
> *[Journal TBC — check Zotero for final publication details]*

**Key finding.** Adoption of AI tools by scientists increases individual
productivity and impact but narrows the collective focus of science — AI
users tend to work on more central, already-popular topics, leaving the
periphery of knowledge less explored.

**Connection to this project.**

- Synthetic biology is a field that has enthusiastically adopted
  computational tools: DNA design software (Benchling, SnapGene),
  protein structure prediction (AlphaFold), and increasingly large
  language models for sequence design.
- If the Evans/Hao finding generalises to synbio, we would expect:
  (a) increasing semantic convergence in the patent and paper corpus
      over time, and
  (b) a narrowing of iGEM project themes in the years after major AI
      tools became widely available (roughly 2020–present).
- This can be tested in this project by examining temporal trends in
  cluster diversity: does the variance of UMAP coordinates shrink
  post-2020? Do carbon capture projects cluster more tightly than
  before?
- Implication for the local trajectory argument: if AI tools narrow
  focus globally, do they also homogenise across cities, or do they
  allow some cities to diverge by specialising in AI-enabled approaches?

---

### 3. Evans & Duede (2025) — After science

> Evans, J.A., & Duede, E. (2025). After science. *[Check Zotero for
> full citation details]*

**Key finding.** Broad philosophical and empirical argument about how
science is changing — the relationship between formal scientific knowledge
and broader knowledge ecosystems (data, models, institutions).

**Connection to this project.**

- Provides framing for understanding iGEM projects as a *different kind*
  of knowledge artifact from papers and patents — student projects sit
  closer to the "commons" end of the knowledge production spectrum.
- The mixed artifact corpus (projects + papers + patents) in this project
  is itself an instance of the broader knowledge ecosystem Evans & Duede
  describe. The project asks whether these different artifact types form
  coherent local innovation trajectories, which is a specific empirical
  test of the claim that knowledge artifacts from different institutional
  contexts are meaningfully connected.
- Use as theoretical framing in the Introduction and Discussion.

---

### 4. Santolini et al. (2023) — iGEM as a model system for team science

> Santolini, M., Mäkinen, M., Yammine, S., Isalan, M., Tanaka, R.J.,
> Breitling, R., … & Grozinger, C. (2023). iGEM: a model system for team
> science and innovation. *iScience*, 26(1), 105927.
> DOI: 10.1016/j.isci.2022.105927
> Zotero key: TTR9W6ZY

**Key finding.** Treats iGEM as a natural experiment for studying how team
composition, collaboration structure, and institutional environment shape
innovation outcomes. Finds systematic patterns linking team diversity,
inter-institutional collaboration, and project quality/impact.

**Connection to this project.**

- This paper is the methodological bridge between the Wu/Wang/Evans team
  science literature and the iGEM data we actually use.
- It validates the use of iGEM as a research site for studying innovation
  dynamics — a claim we would otherwise need to defend from scratch.
- It provides specific metadata about iGEM teams (size, composition,
  collaboration networks) that could be joined to the project corpus.
- Directly citable when introducing the iGEM data source and justifying
  why iGEM projects are a meaningful unit of analysis for studying
  local synthetic biology innovation.

---

## Candidate Questions for James Evans

These questions connect this project's specific empirical setup to Evans'
research agenda. They are intended for a meeting or email conversation.

---

**1. Measuring disruption without citation networks**

The CD index relies on citation behaviour to classify patents and papers as
disruptors or developers. iGEM student projects don't have formal citation
networks. What would you recommend as a proxy measure of disruption for
artifacts that lack citations? Is semantic distance from contemporaneous
work in an embedding space a plausible structural proxy, and has your group
explored this?

---

**2. Does the small-team disruption effect hold for student teams?**

Your 2019 Nature paper shows small teams disrupt across science and patents.
iGEM teams are structurally small, but they are student teams operating
under a competition format with standardised parts and annual themes. Does
the disruption mechanism (fewer constraints from prior work, different
information environment) apply in this context? Or does the competition
structure actually pull teams toward consolidation?

---

**3. Do AI tools narrow local knowledge trajectories as well as global ones?**

If AI adoption narrows the collective focus of science globally, does it
also erode the distinctiveness of *local* innovation trajectories — the
city-level specialisation that this project is trying to map? Or could AI
tools be path-dependent, amplifying local strengths (e.g. a synthetic
biology cluster in Boston is already focused on metabolic engineering, so
AI tools help them go deeper rather than redirecting them)?

---

**4. iGEM as a leading indicator — methodological validity**

This project frames iGEM projects as potentially *upstream* of papers and
patents in a local innovation trajectory. The logic is: student projects
introduce early-stage ideas, papers develop them, patents commercialise
them. Is there existing empirical support for student competitions acting
as leading indicators of later commercial or academic activity? And how
should we handle the reverse possibility — that iGEM teams are actually
*responding* to what's already happening in local industry?

---

**5. Relatedness and the synthetic biology product space**

The economic complexity framing (Hidalgo & Hausmann, Product Space) treats
diversification as following paths of relatedness. In this project,
relatedness is measured through semantic similarity of artifacts. Does
your group see semantic relatedness as a plausible operationalisation of
the Hidalgo/Hausmann concept of capability overlap? Are there known pitfalls
when applying economic complexity frameworks to science rather than to
exports?
