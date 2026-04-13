# James Evans — Connections to This Project

Notes on relevant work by James Evans (Knowledge Lab, University of Chicago) and how it intersects with the "Patents, Papers, Parts & Planet" thesis project.

---

## Key Papers

### 1. Wu, Wang & Evans (2019) — Team size and disruption

**Citation:** Wu, L., Wang, D., & Evans, J. A. (2019). Large teams develop and small teams disrupt science and technology. *Nature*, 566, 378–382. https://doi.org/10.1038/s41586-019-0941-9

**Core finding:** Across millions of papers and patents, small teams are disproportionately likely to *disrupt* existing knowledge (high CD index — citing papers that stop citing the prior art), while large teams tend to *develop* and consolidate established directions. This pattern holds across science, technology, and social science over decades.

**Connection to this project:**
- iGEM teams are small (typically 5–15 students), operate on short timelines, and produce conceptual proof-of-concept work — the profile of a disruptive actor in Evans' framework.
- Large institutional and corporate patent applicants in the same semantic space likely occupy the "develop" end of the spectrum.
- A testable implication: iGEM projects in carbon-capture synthetic biology may cluster near the frontier of semantic space (introducing new directions), while patents cluster in regions of consolidated, applied work. The UMAP + HDBSCAN projection can be used to explore this spatially.
- Team size data is available through the iGEM Registry (team member counts per year), enabling a direct operationalization of the disruption-development axis within the iGEM layer.

---

### 2. Hao, Xu, Li & Evans (2026) — AI tools and science focus

**Citation:** Hao, J., Xu, F., Li, W., & Evans, J. A. (2026). AI tools expand scientists' impact but contract science's focus. *(forthcoming / preprint)*

**Core finding:** Scientists who adopt AI tools (including language models and computational biology tools) publish more and garner more citations, but their work becomes more similar to the existing literature — AI tools amplify productivity while narrowing the diversity of questions being asked.

**Connection to this project:**
- Synthetic biology is a computationally intensive field. Tools like Benchling, Geneious, and increasingly LLM-assisted design are becoming standard.
- If AI tools contract the focus of science, the semantic clusters we observe in synbio carbon capture may partly reflect tool-induced convergence rather than genuine intellectual community formation. Clusters that look "tight" in embedding space might be tight because the underlying text was produced with similar AI assistance rather than because the researchers were in genuine dialogue.
- This is a methodological caveat worth noting in the manuscript's limitations section: embedding-based similarity cannot distinguish intellectual proximity from tool-induced vocabulary homogeneity.
- It also raises a positive framing: iGEM student projects, written mostly without AI assistance (at least through ~2022), may provide a cleaner signal of genuine semantic community than AI-assisted papers and patents.

---

### 3. Evans & Duede (2025) — After science

**Citation:** Evans, J. A., & Duede, E. (2025). After science. *(working title — check for published version)*

**Core finding / framing:** A philosophical argument about the epistemic transformation of science in the era of big data, AI, and algorithmic knowledge production. Science is shifting from hypothesis-driven discovery toward pattern extraction at scale, raising questions about what counts as explanation, understanding, and knowledge.

**Connection to this project:**
- This project is itself an example of "after science" methodology: we use embedding models and clustering algorithms to detect semantic structure across thousands of artifacts, without hypothesis-driven inspection of any individual item.
- The philosophical framing is useful for the manuscript's introduction and limitations: what do we claim to *know* when we find that iGEM projects and patents cluster together in UMAP space? Is semantic proximity a proxy for intellectual influence, shared community, or just shared vocabulary?
- Evans & Duede's framing suggests being careful about the difference between *detecting patterns* (what this project does) and *explaining mechanisms* (what requires additional theoretical and empirical work).

---

## Bridge Paper

### Santolini et al. (2023) — iGEM as a model system for team science

**Citation:** Santolini, M., Barabási, A.-L., Bhatt, D. L., Bhattacharya, J., Bhattacharyya, S., & Evans, J. A. (2023). iGEM: a model system for team science and innovation. *eLife* (or similar venue — confirm citation).

**Core finding:** iGEM provides a unique natural experiment for studying team science: teams are comparably structured, compete on the same timeline, and produce public artifacts (wiki pages, parts, presentations) that enable large-scale bibliometric analysis. The paper uses iGEM to test and extend findings from team-size research, including Evans' disruption-development framework.

**Connection to this project:**
- This is the most direct bridge between Evans' team-science work and the iGEM data layer in this project.
- Santolini et al. validate that iGEM wikis and project descriptions are usable as research artifacts — supporting our use of iGEM project text as the "student projects" corpus.
- Their finding that iGEM teams behave like disruptive small teams in Evans' framework provides prior support for the hypothesis that iGEM carbon-capture projects will occupy semantically novel (frontier) regions of the shared embedding space.
- The paper also suggests iGEM as a natural experiment for *geographic* team science, which has not been fully explored. This project can contribute that geographic layer.

---

## Questions for James Evans

These questions target the intersection of Evans' work with the specific methodological and empirical choices in this project.

---

**1. Does the disruption-development axis map across knowledge layers?**

Your 2019 Nature paper shows that small teams disrupt and large teams develop *within* a single knowledge layer (papers or patents). This project treats iGEM projects, papers, and patents as three distinct layers of the same innovation ecosystem. Do you expect the disruption-development gradient to manifest *across* layers — i.e., student iGEM projects acting as the "disruptive" input that gets consolidated into papers and then into patents? Or is the axis layer-specific, and cross-layer comparison introduces too many confounds (e.g., different citation practices, different timescales)?

---

**2. Geography, semantic relatedness, and the mechanism question**

This project asks whether iGEM projects, papers, and patents in the same city share semantic relatedness in synthetic biology carbon capture. If we find city-level clustering, what would you take as the strongest plausible mechanism — shared institutions (universities, incubators), labor mobility, or informal knowledge spillovers? And does your work on the role of geographic proximity in knowledge networks suggest any empirical test that could help distinguish these mechanisms, given only the artifact text and metadata we have?

---

**3. AI-induced semantic convergence as a confound**

Your 2026 paper finds AI tools contract science's focus. If computational tools narrow the vocabulary and question framing of scientists, then our embedding-based similarity measures might be inflated — artifacts look semantically close partly because they were produced with similar AI assistance rather than because the people involved were in genuine intellectual dialogue. How serious is this confound for projects that use embedding similarity as a proxy for intellectual relatedness? Is there a way to estimate or bound its magnitude?

---

**4. Cross-layer citation networks and the limits of co-citation analysis**

Your network-of-science work typically operates within a single artifact type (e.g., paper-to-paper citation networks). This project wants to measure relatedness across artifact types — patents cite papers, papers describe iGEM parts, but the citation practices are completely different. What methodological frameworks would you recommend for measuring "intellectual relatedness" between artifact types that don't share a common citation graph? Is embedding similarity a reasonable substitute for co-citation in this setting, or does it collapse too much of the signal?

---

**5. Sample sizes and geographic inference for carbon capture**

The carbon-capture subset in synthetic biology is relatively small — a few hundred iGEM projects at most, and a comparable number of patents and papers. Santolini et al. (2023) have the full iGEM corpus; we have a topical slice. At what point does the corpus become too small for reliable geographic inference — e.g., to say that "City X has a coherent local trajectory in carbon capture"? Are there nonparametric or permutation-based approaches from your work on knowledge networks that handle small-N geographic inference gracefully?

---

## Notes for Follow-up

- Check whether Evans has published work on *patent* disruption (the 2019 paper covers both papers and patents, but the patent analysis may be less developed).
- The Santolini et al. (2023) citation needs to be verified — confirm venue and co-authors before citing in the manuscript.
- Evans & Duede (2025) "After science" — confirm whether this is a published article, book chapter, or working paper; look for a stable DOI before citing.
- Consider whether any of the five questions above could be posed as a mini-analysis within the thesis (e.g., computing a CD-like disruption index for iGEM projects using semantic novelty rather than citation-based forward citation patterns).
