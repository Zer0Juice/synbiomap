# Q2 — Condition A (with KB)

*FrankGPT — A Neffke-inspired agent*

---

## Short answer

Both frameworks assert that proximity in some latent capability space predicts diversification. The difference is not cosmetic — it is a disagreement about *what the latent capabilities are*, how to measure them, and therefore what the mechanism actually is.

---

## The key mechanism in Neffke's framework

Neffke's central claim is that **skill relatedness** — operationalised through inter-industry labor flows — captures the degree to which two industries draw on overlapping human capital. When workers move from industry A to industry B in unusually large numbers, that is treated as evidence that the two industries share a common capability base in the labor market.

The mechanism, stated plainly: **capabilities reside in workers, not just in products**. Firms can enter a related industry because they can redeploy existing workers (or hire workers released by related firms) without incurring prohibitive retraining costs. The friction is skill specificity. When skill specificity is high across industries, diversification is path-dependent; when it is low, it is not.

This generates the operational variable that matters for your work: **density**. For a given industry *i* in region *r*, density measures the share of industries already present in *r* that are skill-related to *i*, weighted by the strength of the region's presence in those industries. Density predicts entry and exit.

Key papers:
- Neffke, Henning & Boschma (2011) `[indexed]` — entry and exit of Swedish industries predicted by relatedness to existing regional portfolio.
- Neffke & Henning (2013) `[training]` — skill-relatedness measured from German Social Security labor flow data.
- Neffke, Hartog, Boschma & Henning (2017) `[indexed]` — who introduces new industries into regions: incumbent firms vs. entrepreneurs, locals vs. outsiders.
- "The Principle of Relatedness" (2018) `[indexed]` — the finding generalises across spatial scales, activity types, and countries.

---

## Hidalgo's product space — the contrast

Hidalgo & Hausmann (2009) `[training]` operationalise relatedness through **co-export patterns**: two products are related if countries with comparative advantage in one tend to have it in the other. The latent construct is productive capabilities, but they are never directly observed — they are inferred from the structure of the export basket. The mechanism is capability overlap, but the framework does not commit to what those capabilities are: they could be labor skills, infrastructure, institutions, or technical knowledge embedded in firms.

| Dimension | Neffke | Hidalgo |
|---|---|---|
| Unit of capability | Human capital / skills | Unspecified productive capabilities |
| Measurement | Observed labor flows between industries | RCA co-occurrence in trade data |
| Geographic unit | Regions (subnational) | Countries |
| Activity unit | Industries | Products |
| Mechanism specificity | High — workers carry skills across industries | Low — "capabilities" not directly observable |
| Data requirement | Matched employer-employee records | Standard trade statistics |
| Main weakness | Data-intensive; not globally available | Mechanism is a black box |

The core critique from the Neffke tradition: the product space is a **reduced-form** description of what places are good at, without a clear mechanism for why the structure looks as it does or how it changes. Neffke's approach is harder on data but more interpretable — you have a specific testable channel (labor redeployment) that can in principle be checked independently of the diversification outcome.

---

## Relevance for your project

For city-level diversification in synthetic biology using publication data, you are applying the product-space logic (relatedness from co-occurrence of topics or concepts). You are recovering a real relatedness signal but the mechanism remains ambiguous. To operate fully in the Neffke tradition you would want to identify a capability-flow channel — for instance, researcher mobility between topics or cities. That is harder, but the density-predicts-entry test you are running is squarely in both traditions.

---

## Epistemic self-audit

- Neffke, Henning & Boschma (2011): `[indexed]` — title and venue confirmed. Specific density coefficient `[unverified]`.
- Neffke & Henning (2013): `[training]` — verify exact title via `index_canon.md` before citing.
- Hidalgo & Hausmann (2009): `[training]` — widely cited; verify venue before submitting.
- Qualitative finding that density predicts entry: robust and well-documented `[unverified]` at the level of specific effect sizes.
