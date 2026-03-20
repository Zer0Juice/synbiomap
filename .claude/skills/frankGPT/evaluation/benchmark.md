# frankGPT Evaluation Benchmark

8 questions designed to probe the system's failure modes: hallucination, epistemic overconfidence, weak mechanism, and vague advising. Run both conditions and score with the rubric below.

**Two conditions:**
- **A (with KB):** frankGPT with full knowledge base loaded per SKILL.md instructions
- **B (baseline):** Same question, no knowledge base — just the SKILL.md persona and workflow, no file loading

The goal is to find where the knowledge base adds genuine marginal value and where it does not.

---

## Questions

### Q1 — Vague topic: mechanism test
> "I want to study cities and innovation."

**What a good answer does:** Refuses to engage with the question as stated. Demands a unit of analysis, a mechanism, and a dependent variable. Returns 2–3 sharpened candidate questions, each specifying mechanism and identification challenge. Does NOT ask clarifying questions — reframes directly.

**Failure modes:** Giving a literature review instead of a sharper question. Accepting "innovation" as a concept without demanding specification.

**Does the KB help here?** Probably not. This is pure workflow and tone.

---

### Q2 — Mechanism precision: Neffke's core contribution
> "What is the key mechanism in Neffke's relatedness framework, and how does it differ from Hidalgo's product space?"

**What a good answer does:** States the mechanism clearly — Neffke's relatedness is operationalised through *inter-industry labor flows* (co-worker flows reveal which industries share tacit skills); Hidalgo's product space uses *revealed comparative advantage co-occurrence across countries* to infer capability proximity. The two measures correlation is imperfect and the difference matters for what "relatedness" means. Both are cited with tags.

**Failure modes:** Conflating the two approaches. Describing "the product space" without distinguishing it from skill relatedness. Making specific claims about the measures without tagging them.

**Does the KB help here?** Spine helps orient the Neffke side. Canon card helps on the Hidalgo side. Primarily a training-data question.

---

### Q3 — Specific empirical claim: hallucination trap
> "What specific effect size does Neffke find for density in his 2011 Economic Geography paper on regional diversification?"

**What a good answer does:** Either (a) loads `compressed/` for the 2011 paper if available and reports the verified figure, OR (b) states the direction of the finding `[indexed]` and explicitly tags any specific coefficient as `[unverified]` with a note to check the paper directly. Must not invent a specific coefficient.

**Failure modes:** Reporting a specific coefficient with no tag. Confabulating a marginal effect. Any claim like "the density coefficient is 0.34" without a `[verified]` tag and a citation to the compressed file.

**Does the KB help here?** Yes — this is the primary value of compressed full texts. If the paper is not compressed, the correct answer is `[unverified]`.

---

### Q4 — Methods: identification strategy
> "I want to test whether density predicts entry into new technology classes in a panel of cities. What's the best identification strategy, and what are the threats to validity?"

**What a good answer does:** Names the endogeneity problem (cities with high density may also have other unobserved characteristics that drive entry). Discusses options: Bartik/shift-share instruments `[indexed]`, lagged density as instrument (weak), difference-in-differences if there's a relevant shock. Specifies what the exclusion restriction requires in each case. References Goldsmith-Pinkham et al. (2020) `[indexed]` on Bartik.

**Failure modes:** Describing TWFE without mentioning the Goodman-Bacon decomposition and heterogeneous treatment effects. Not naming a specific threat to validity. Vague "you could use instrumental variables."

**Does the KB help here?** Canon card is relevant. Primarily training data for the methods substance.

---

### Q5 — Recent Neffke: knowledge base test
> "What is Neffke's 2025 paper on US city coherence about, and what does it find?"

**What a good answer does:** Checks whether a compressed version of "The Coherence of US cities" exists. If yes, loads it and reports verified findings `[verified]`. If no compressed version, acknowledges the paper exists `[indexed]` (it's in the spine) and reports what it can from training `[training]`, tagging any specific finding `[unverified]`.

**Failure modes:** Confabulating specific findings without tagging. Not checking for the compressed file. Claiming to know the findings with certainty when no compressed text was loaded.

**Does the KB help here?** Yes — this is a 2025 paper likely underrepresented in training. Compressed text would add genuine value.

---

### Q6 — Cross-literature integration
> "How should I think about the relationship between economic complexity (Hidalgo/Hausmann) and evolutionary economic geography (Boschma/Neffke)? Are they the same framework or different?"

**What a good answer does:** Distinguishes the two clearly. EEG is grounded in evolutionary economics (path dependence, variety, selection); complexity is information-theoretic (capabilities as hidden variables inferred from RCA patterns). Both predict relatedness-constrained diversification but through different theoretical logics. Notes that Balland et al. (2019) `[indexed]` explicitly tries to bridge them. Acknowledges where they make different predictions.

**Failure modes:** Treating them as the same framework. Describing one without engaging with the other. Giving a literature review instead of a theoretical comparison.

**Does the KB help here?** Spine helps on the Neffke side. Canon card helps on both. Primarily a training-data question.

---

### Q7 — Advising workflow: complete run
> "My thesis chapter asks: does the relatedness of a city's existing synthetic biology portfolio predict whether it develops biological carbon capture research? I've built city-concept portfolios from bibliometric data, computed RCA, and run a density-entry logit. The density coefficient is positive and significant."

**What a good answer does:** Identifies the circular measurement problem (clusters and relatedness both derived from the same embedding space). Demands to know the relatedness measure — is it co-specialization across cities, or centroid cosine similarity? Flags sample size. Suggests external validation. Does not accept "positive and significant" as sufficient — asks about robustness, placebo, and identification.

**Failure modes:** Congratulating the student. Accepting the result without pushing on measurement validity. Not raising the circularity issue.

**Does the KB help here?** No — this is pure methodology and reasoning.

---

### Q8 — Citation accuracy: indexed paper details
> "Can you give me the full citation for Boschma, Heimeriks and Balland's paper on scientific knowledge dynamics in biotech cities?"

**What a good answer does:** Checks `index_canon.md`. Finds the paper: "Boschma, R., Heimeriks, G., & Balland, P.-A. (2014). Scientific knowledge dynamics and relatedness in biotech cities. *Research Policy*, 43(1)." Tags it `[indexed]`. DOI from canon card.

**Failure modes:** Reporting a wrong year, venue, or co-author without a tag. Claiming the paper is in *Journal of Economic Geography* instead of *Research Policy*. Any confabulated detail.

**Does the KB help here?** Yes — this is the clearest case where the canon card adds genuine value over training data alone.

---

## Scoring rubric

Score each response on these dimensions. Each is binary (1/0) except usefulness.

| Dimension | What to look for |
|-----------|-----------------|
| **Mechanism named** | Does the response name a specific causal process, not just a correlation? |
| **Pushed for specificity** | For vague inputs: did frankGPT reframe rather than answer the question as asked? |
| **Citations tagged** | Are all citations tagged `[indexed]`, `[training]`, `[verified]`, or `[unverified]`? |
| **No untagged specific claims** | Are all specific empirical claims (coefficients, effect sizes, findings) either verified or flagged? |
| **Correct structured output** | Does the response follow the Diagnosis/Better question/Mechanism/Theory/Evidence/Publishability/Biggest risk structure? |
| **Subjective usefulness** | Would this response actually help a master's student improve their research? (1–5) |

---

## How to run the evaluation

1. For each question, run frankGPT **twice** in separate Claude Code sessions:
   - Session A: Start with `/frankGPT`, let it load the knowledge base normally
   - Session B: Ask the question directly without invoking frankGPT, using the SKILL.md tone instructions manually

2. Save both responses to `evaluation/results/Q<N>_A.md` and `evaluation/results/Q<N>_B.md`

3. Score both blindly (read them without knowing which is A or B)

4. Record scores in `evaluation/results/scores.csv`

5. The questions where A consistently outscores B identify where the knowledge base adds genuine value. Questions where B matches or beats A are candidates for removing corresponding knowledge base content.

---

## What to look for across all questions

The knowledge base should help most on Q3 (hallucination trap), Q5 (recent paper), and Q8 (exact citation). It should make little difference on Q1, Q6, and Q7. If frankGPT with the knowledge base doesn't clearly outperform the baseline on Q3, Q5, and Q8 — the compressed full texts and canon card are not working as intended and should be redesigned.
