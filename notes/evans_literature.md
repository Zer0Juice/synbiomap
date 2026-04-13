# Connections to James Evans' Research

This file documents how key papers by James Evans connect to this project,
and prepares questions for a potential conversation with him.

---

## Relevant Papers

### 1. Wu, Wang & Evans (2019) — "Large teams develop and small teams disrupt science and technology"
*Nature 566, 378–382. DOI: 10.1038/s41586-019-0941-9*

**Core finding:** Small teams tend to produce disruptive work (papers and
patents that redirect the field away from prior work), while large teams tend
to develop existing knowledge (high-citation incremental advances). This
pattern holds across science, technology, and social science over decades.
Operationalized using the CD index (Funk & Owen-Smith, 2017): a measure of
whether citing papers *abandon* prior work cited by the focal paper (disruptive)
or *continue* to cite it alongside the focal paper (developmental).

**Connection to this project:**
- iGEM teams vary in size from 2 to 30+ members. The Wu et al. finding predicts
  that smaller iGEM teams should produce more disruptive synthetic biology
  projects — opening new directions rather than executing well-established ones.
- We can test this within the iGEM corpus: does team size predict semantic
  distinctiveness (distance from existing cluster centroids) or temporal novelty
  (first to occupy a region of semantic space)?
- The patent corpus is also relevant: small-entity patents in synbio may show
  different disruption dynamics than large assignee (corporate) patents.
- If iGEM student projects really are early signals of innovation trajectories,
  they may function like the "small team" node in a local knowledge graph —
  opening directions later developed by larger academic and corporate teams.

---

### 2. Hao, Xu, Li & Evans (2026) — "Artificial intelligence tools expand scientists' impact but contract science's focus"
*Nature (forthcoming / preprint). Reference year from Zotero: 2026.*

**Core finding:** AI-assisted research dramatically increases individual
productivity and citation impact, but the papers produced tend to converge on
popular topics. AI tools amplify existing trends rather than opening new ones —
the *focus* of the field narrows even as output expands.

**Connection to this project:**
- Synthetic biology is increasingly computational: CRISPR design, part
  optimization, protein structure prediction (AlphaFold), and metabolic
  modeling all use AI tools heavily. The 2015–2025 period in the corpus likely
  captures the transition from wet-lab-first to AI-augmented practice.
- If we observe increasing semantic clustering in the later part of the corpus
  (papers, patents, and iGEM projects converging on fewer themes), this could
  be partly explained by AI-tool adoption — consistent with the Hao et al. finding.
- The carbon capture case study is relevant: as an applied area, it may have
  attracted AI-augmented design workflows earlier than other synbio subfields,
  potentially showing earlier convergence in semantic space.
- This paper also contextualizes the team-size finding: if AI tools amplify
  individual/small-team output, do they simultaneously reduce the disruptive
  potential of small teams (because AI tools guide researchers toward popular
  directions)?

---

### 3. Evans & Duede (2025) — "After science"
*Reference from Zotero. Full citation TBD.*

**Core finding / framing:** A philosophical and empirical examination of how
the institution of science is changing — how knowledge production, validation,
and the social organization of research are being restructured by computational
tools, big data, and changing incentive structures.

**Connection to this project:**
- Provides the broader intellectual frame for asking whether student iGEM
  projects, academic papers, and patents still represent meaningfully distinct
  epistemic communities, or whether these categories are blurring.
- The "local innovation trajectory" framing in this project implicitly assumes
  that the three artifact types have different relationships to knowledge
  creation. Evans & Duede (2025) gives language and legitimacy to interrogating
  that assumption.
- Useful for the manuscript's discussion section: what does it mean that a
  student project is semantically proximate to a patent in the same city?
  Is that proximity meaningful knowledge flow, or an artifact of shared
  vocabulary in an era where all science is increasingly legible as technology?

---

### 4. Santolini et al. (2023) — "iGEM: a model system for team science and innovation"
*Zotero key: TTR9W6ZY. DOI to be added from Zotero record.*

**Core finding:** iGEM provides a large-scale natural experiment for studying
team science. Santolini et al. analyze how team composition, collaboration
networks, and institutional resources predict project quality and innovation.
The iGEM Registry's open, annual, multi-team structure makes it uniquely suited
for large-n studies of team dynamics in science.

**Connection to this project:**
- Provides methodological legitimacy for using iGEM data as a proxy for student
  innovation activity. This paper should be cited prominently in the data
  sources section of the manuscript.
- The team science framing bridges Wu et al. (team size → disruption) to the
  iGEM context: Santolini et al. confirm that iGEM teams are meaningfully
  comparable units of analysis, not just noise.
- Santolini et al. also analyze geographic and institutional network effects —
  directly relevant to the city-level analysis in this project.
- Their finding that collaboration network position predicts project quality
  suggests that the city-level semantic clusters in this project may partly
  reflect network structure (cities with dense iGEM-academia-industry ties
  produce more coherent innovation trajectories).

---

## Questions for James Evans

Given this project maps the global synthetic biology innovation network
(patents, papers, iGEM projects) and uses economic complexity frameworks
(Product Space, relatedness) to study local knowledge trajectories in
carbon capture:

### 1. Disruption in iGEM: can we measure it without citation data?
iGEM projects don't accumulate citations the way papers do. The CD index
requires citation links. Is there an analogous measure of disruption that
works for semantic embeddings or for registry-style data (parts that get
reused vs. abandoned)? Or is the right approach to use downstream citation
of papers that reference the iGEM project or its parts?

### 2. Does local co-location amplify or dampen disruption?
The Wu et al. finding operates at the paper/patent level. At the city level,
do places where small teams *and* large teams co-locate (high diversity of
team sizes) produce more innovative trajectories than places dominated by one
type? What's the unit of analysis for "disruption" in a local innovation system?

### 3. AI tools and the convergence of student projects
If AI tools are contracting the focus of science (Hao et al.), do iGEM
projects post-2018 (after the AlphaFold-era tools became available) cluster
more tightly in semantic space than pre-2018 projects? Is that a testable
prediction within this corpus?

### 4. The sequence from project → paper → patent: is there evidence of actual flow?
This project proposes a temporal sequence in local innovation (student project
→ academic paper → patent). Is there evidence in the literature — or in
your work — that this sequencing reflects actual knowledge transfer, or is it
more likely that all three respond to a common exogenous signal (e.g. a
technology breakthrough, a policy shift)? How would you distinguish flow from
common cause using the kind of observational data available here?

### 5. Carbon capture as a "mission-driven" case: does it behave differently?
Mission-driven research areas (climate, health) may attract different team
composition than curiosity-driven ones. Does the disruption/development dynamic
from Wu et al. hold in explicitly applied subfields, or do external pressures
(funding mandates, policy timelines) push even small teams toward developmental
work? Is synthetic biology carbon capture a useful test case for this question?

---

## Notes on Integration

- Cite Wu et al. (2019) in the manuscript's **Introduction** and **Discussion**
  when framing the student-project → paper → patent sequence as a disruption
  narrative.
- Cite Hao et al. (2026) in the **Discussion** when interpreting temporal
  trends in semantic clustering (especially if post-2018 convergence is visible).
- Cite Evans & Duede (2025) in the **Discussion** for broader framing of what
  it means to study knowledge flow across artifact types.
- Cite Santolini et al. (2023) in the **Data Sources** section to validate
  iGEM data as a research object, and in **Related Work** to situate the
  team-science framing.
- The questions above are candidates for a meeting agenda or email to Evans.
  Questions 1 and 4 are the most directly actionable for the dissertation.
