# Q1 — Baseline (B): No knowledge base loaded

**Condition:** SKILL.md persona and workflow only. No knowledge base files loaded.
**Question asked:** "I want to study cities and innovation."

---

## Diagnosis

That is not a research question. It is a theme — and a large one. "Cities" is a unit of analysis. "Innovation" is an outcome, a process, a dependent variable, an independent variable, and a literature, depending on who you ask. At the moment you have neither a puzzle nor a mechanism. You have a postcard.

The question as stated could absorb an entire research institute for thirty years. That is not a compliment. It means nothing in this form is falsifiable, nothing is theoretically committed, and nothing rules anything out.

Before this can become a research question, three things need to exist:

1. A **unit of analysis**: cities (fine), but cities as measured how, over what time period, at what spatial aggregation?
2. A **dependent variable**: what specific outcome are you calling "innovation"? Patent counts? New product introductions? Entry into new technology classes? Knowledge spillovers as measured by citation flows? Each of these implies a different mechanism and a different dataset.
3. A **mechanism**: why would anything about a city — its size, its density, its industrial composition, its labor market structure — cause more or less of that outcome? Through what process? For which firms or workers?

Without these three things, no amount of data will produce an argument. You will produce a description.

---

## Better question

Here are three candidate questions that are at least arguable:

**Candidate 1 — Relatedness and technological entry**
> Does the relatedness of a city's existing technology portfolio predict whether it enters new technological domains, and does this effect operate through co-located labor mobility or through knowledge spillovers among firms?

- Unit of analysis: city × technology class × year
- Mechanism: capability redeployment — workers and firms that are already good at adjacent things lower the cost of entry
- Outcome: probability of entry into a new technology class (measured by patent class or publication field)
- Data: USPTO patents by inventor location, or OpenAlex publications by author city
- Identification challenge: cities that enter new domains may already have unobserved growth trajectories — density is endogenous

**Candidate 2 — Agglomeration and innovation quality**
> Do larger cities produce higher-quality innovations (measured by forward citations) controlling for quantity, and does this effect diminish as a field matures?

- Unit of analysis: city × technology field × time period
- Mechanism: knowledge recombination — denser labor markets increase the probability of non-redundant idea collisions
- Outcome: mean forward citations per patent, normalized within field and year
- Data: patent data with citation links and inventor location (PATSTAT, USPTO)
- Identification challenge: larger cities attract better inventors; the city effect is confounded with selection

**Candidate 3 — Labor mobility and knowledge transfer**
> When skilled workers move from high-innovation to low-innovation cities, do they transfer measurable knowledge to their destination firms, and under what conditions does this transfer persist?

- Unit of analysis: worker × job transition × city pair
- Mechanism: embodied knowledge transfer — skilled workers carry tacit know-how across firm and city boundaries
- Outcome: citation behavior and patent output of receiving firms post-hire
- Data: matched employer-employee records (if available), or LinkedIn-style career data linked to patent records
- Identification challenge: workers who move are not random — selection into mobility and selection of destination city are both endogenous

---

## Mechanism

All three candidates share a common underlying mechanism: **knowledge spillovers are not frictionless**. They require proximity — either spatial, industrial, or occupational — to operate. The theoretical question is which form of proximity matters most and why. Spatial proximity (Marshall, Jacobs) gives you agglomeration. Technological proximity gives you relatedness (Neffke, Boschma). Occupational proximity gives you labor-flow-based knowledge transfer (Neffke's skill-relatedness work `[training]`).

The mechanism must be stated before the data are collected. Otherwise you are measuring a correlation and calling it an explanation.

---

## Theory

This sits at the intersection of three conversations:

- **Evolutionary economic geography** (Boschma, Frenken, Neffke): regions diversify into related activities because relatedness lowers capability costs. The theoretical core is path dependence — what you can do next depends on what you can already do.
- **Agglomeration economics** (Duranton, Puga, Glaeser): cities generate productivity and innovation gains through density. The debate is whether this is a matching effect, a learning effect, or a sharing effect.
- **Innovation systems and knowledge spillovers** (Jaffe, Audretsch, Feldman): knowledge does not flow freely; it is localized, embodied in people and organizations, and shaped by industrial structure.

Your argument needs to position itself relative to at least one of these. "Cities and innovation" is a topic. Adding a mechanism that builds on one of these frameworks makes it a contribution.

---

## Evidence

The best currently available datasets for this class of question:

- **Patent data**: USPTO, PATSTAT, or Google Patents — give technology class, inventor location, citation links. Good for measuring output and relatedness. Weak on measuring the mechanism (you can see what was produced but not how).
- **Publication data**: OpenAlex, Web of Science — similar logic, better for academic science, increasingly usable for applied research fields.
- **Matched employer-employee records**: available in some European countries (Sweden, Denmark, Germany, Netherlands) via administrative data. These are the gold standard for the labor mobility mechanism because you can observe actual worker movements.
- **Economic complexity / RCA-based approaches**: compute revealed comparative advantage from patent or publication portfolios, then compute relatedness as co-specialization across cities. This is the Hidalgo-Hausmann / Neffke toolkit `[training]`.

The identification challenge in every version of this question is endogeneity: the city characteristics that drive innovation may also be the city characteristics that attract the kind of workers and firms that innovate. You need either a plausible instrument, an event study, or a very clear argument about selection.

---

## Publishability

The question "do cities matter for innovation?" has been answered. The answer is yes. Papers published on that question in 2025 need a more specific claim: *which* cities, *which* kinds of innovation, *through which* mechanism, and *for whom*. The three candidate questions above each have this specificity. A paper on Candidate 1 (relatedness and technological entry) could speak to the technology diversification literature directly. A paper on Candidate 3 (labor mobility and knowledge transfer) could speak to the labor economics and geography of innovation literatures simultaneously.

The theoretical contribution depends on which mechanism you identify. If the labor mobility channel is quantitatively more important than the agglomeration channel for entry into frontier technologies, that is a finding that matters for both theory and policy.

---

## Biggest risk

You will spend eighteen months collecting and cleaning data, run a series of regressions, find a positive and significant coefficient on some measure of city-level connectivity, and be unable to say *why* it is positive. The mechanism will remain unidentified. The result will be interesting to you and boring to everyone else.

The antidote is to commit to a mechanism *before* the data collection and design the empirical strategy around testing that mechanism rather than documenting a correlation. A panel regression showing that innovative cities produce more patents is not a paper. A research design that isolates the labor-mobility channel from the agglomeration channel — using a shock that separates the two — is a paper.

The biggest single risk is that you never commit to one of the candidate questions and instead write a chapter that tries to address all of them loosely. Pick one.

---

*FrankGPT — A Neffke-inspired agent. No knowledge base loaded (Condition B). All citations marked `[training]` are recalled from training data and should be verified before use.*
