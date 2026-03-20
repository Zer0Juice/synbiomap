# Q4 — Condition B (baseline, no KB)

*FrankGPT — A Neffke-inspired agent*

---

## Diagnosis

This is a well-posed empirical question — possibly the best-posed one you can ask in this literature. The dependent variable is clear (entry into a technology class), the treatment variable is theoretically grounded (density), the panel structure is appropriate, and the estimand is actually interesting. You have made it further than most students before asking about identification.

That said, "best identification strategy" depends entirely on what threat you are most worried about.

---

## The core identification problem

Density is a function of the city's existing capability portfolio. Entry into a new technology class is also a function of the city's existing capability portfolio. Both are downstream of the same latent variable: accumulated local knowledge stock. OLS on a cross-section is nearly useless. Even in a panel, you need to think carefully about what variation is doing the work.

---

## Identification strategies, ranked by credibility

**1. Two-way fixed effects with lagged density (TWFE)** — City FE, technology-class FE, year FE. Necessary but not sufficient. Controls for time-invariant heterogeneity but cannot eliminate correlation between lagged density and prior capability shocks that independently predict entry. Your main specification. Interpret it conservatively.

**2. Shift-share / Bartik-style instrument** — Instrument for city density using national-level growth in the technology class interacted with pre-period exposure. Goldsmith-Pinkham, Sorkin & Swift (2020) `[training]` and Borusyak, Hull & Jaravel (2022) `[training]` clarify that Bartik validity rests on exogeneity of either shares or shocks — both are questionable here. Useful as a robustness check; do not oversell the causal claim.

**3. Plausibly exogenous relatedness shocks** — Find external events that shift relatedness between existing capabilities and the target class for reasons orthogonal to the city's trajectory. Rare and hard to measure. Best paper would do this. Probably too ambitious for a thesis chapter without a very clean natural experiment.

**4. RD on density thresholds** — No theoretical basis for a hard threshold. Do not do this.

---

## Threats to validity

**Simultaneity:** Entry mechanically raises density in adjacent classes in subsequent periods. Use density lagged at least one period. Test sensitivity to lag length.

**Omitted capability shocks:** A skilled-worker inflow raises density and entry probability simultaneously. Include time-varying city controls (R&D, inventor population, grants) and test whether density survives.

**Endogenous relatedness measure:** If relatedness is computed from the same panel used for entry regressions, it is not independent. Fix: compute relatedness from a different country, time window, or dataset (e.g. US patent co-classification applied to European entry). `[unverified]` — verify the specific procedure in the Neffke et al. papers.

**Rare events and binary outcome bias:** Conditional logit for fixed-effects binary models, or Mundlak correction. Be explicit about the choice.

**Spatial autocorrelation:** Cities are not independent. Standard errors clustered only by city are too optimistic. Consider Conley spatial standard errors `[training]`.

**Technology class definition artifacts:** Test robustness to aggregation level. If density only predicts entry at one level of taxonomy, it is probably an artifact.

---

## Recommended specification

Primary: TWFE LPM with city FE, technology-class FE, year FE, lagged density, lagged city size, lagged technology-class growth rate. Cluster by city.

Robustness: conditional logit; varying lag lengths; out-of-sample relatedness; Bartik IV with Olea-Pflueger F; placebo test using density in unrelated classes (should predict nothing).

---

## Biggest remaining risk

After all of this, you are not identifying a clean causal effect. You are identifying a strong conditional correlation consistent with the relatedness-capability mechanism and inconsistent with the main alternatives you have tested. That is what this literature does. It is respectable science. Be honest about what you have and have not demonstrated. The worst outcome is claiming causal identification you do not have and having a reviewer dismantle it.

---

*All `[unverified]` claims should be checked against primary sources before citing. Citations tagged `[training]` are recalled from training data — verify details before use.*
