# Q6 — Condition B (baseline, no KB)

*FrankGPT — A Neffke-inspired agent*

---

## The short answer

They are **related but distinct** frameworks that share a common empirical ancestor (relatedness/proximity) but differ fundamentally in their theoretical logics, units of analysis, and causal mechanisms. Conflating them is a common mistake. Understanding where they overlap and where they diverge will sharpen your thesis considerably.

---

## 1. Evolutionary Economic Geography (EEG) — Boschma, Neffke, and colleagues

**Core theoretical logic:** Regions and firms diversify into new activities through **recombination of existing capabilities**. The mechanism is explicitly evolutionary: variation (entry into new sectors/technologies), selection (survival of new activities), and retention (capability lock-in). Relatedness is the transmission belt — related diversification is more likely because it reuses existing know-how, labor pools, and organizational routines.

**Unit of analysis:** The **region** (or firm), understood as a historically-constituted bundle of capabilities. Geography matters because capabilities are embodied in people and institutions that do not move freely.

**Key mechanisms:**
- **Labor mobility** — workers carry tacit knowledge across firms and sectors (Neffke & Henning, 2013 `[training]`)
- **Spin-offs** — new firms inherit capability profiles from parent firms
- **Skill relatedness** — industries are related if they share occupational structures, not just input-output linkages
- **Path dependence** — current specialization constrains future trajectories; diversification is locally bounded

**What it predicts:** A region will enter activity B if it already has activity A, and A and B are related (share capabilities). Entry is probabilistic, path-dependent, and bounded by the existing portfolio. Exit from unrelated activities is also more likely.

**Empirical tradition:** Detailed microdata — establishment-level employment, matched employer-employee records, patent data at inventor level. The work is often causal or quasi-causal in ambition.

---

## 2. Economic Complexity (ECI) — Hidalgo, Hausmann, and colleagues

**Core theoretical logic:** The **product space** (or technology space) reflects the distribution of **capabilities** across countries (or regions), but ECI does not directly model capability transmission. Instead, it infers the structure of capability requirements from co-occurrence patterns in export (or patent) data. Complexity is an emergent property of the system — countries with diverse, exclusive baskets of products are inferred to hold rare capability combinations.

**Unit of analysis:** Primarily the **country** (originally), extended to regions and cities. The country/region is treated as a revealed capability bundle, but the internal firm/worker mechanisms are largely a black box.

**Key mechanisms:**
- **Ubiquity and diversity** as proxies for capability rarity and richness
- **Proximity/relatedness** (density) as a constraint on diversification — but derived from co-occurrence, not from labor flows or organizational genealogy
- The mechanism linking density to entry is **implicit**: regions enter nearby products because they already hold the required capabilities, but *how* capabilities are acquired or transferred is not specified

**What it predicts:** A country/region with high density in a product's neighborhood will be more likely to export that product in the future. High-complexity economies grow faster. But the framework is better at describing the *structure* of the capability space than explaining the *process* of capability formation.

**Empirical tradition:** Aggregate trade data (Comtrade), patent data (PATSTAT). Typically observational and correlational.

---

## 3. Comparison table

| Dimension | EEG (Boschma/Neffke) | Economic Complexity (Hidalgo/Hausmann) |
|---|---|---|
| **Primary unit** | Region / firm / worker | Country / region (aggregate) |
| **Core mechanism** | Capability recombination via labor mobility, spin-offs | Revealed capability inference from co-occurrence |
| **Relatedness definition** | Skill overlap, labor flow, technological co-occurrence | Co-export/co-patent probability (proximity) |
| **Mechanism specified?** | Yes — labor, organizational genealogy | No — black box between density and entry |
| **Causal ambition** | Often quasi-causal (DiD, IV) | Primarily correlational / predictive |
| **Data requirements** | Microdata (firm, worker, inventor) | Aggregate (country/region-product matrices) |
| **Theoretical tradition** | Evolutionary economics, institutional economics | Information theory, complexity science |
| **Key construct** | Skill relatedness, capability proximity | Product space, ECI, density |

---

## 4. Where they make different predictions

**On relatedness measurement:** EEG says two technologies are related if workers can move between them — skill relatedness based on labor flows `[training]`. ECI-style frameworks say they are related if they co-occur in the same regional portfolio more than expected by chance. These measures are correlated but not identical.

**On diversification into distant technologies:** EEG allows for capability-building through deliberate policy, education, or FDI that shifts the regional trajectory. ECI offers less traction here: if a region has low density everywhere, the framework predicts stagnation but does not specify how to escape it.

**On the role of firms vs. places:** EEG, particularly through Neffke's work, can disaggregate to the firm and worker level — explaining which specific firms enter new sectors and why. ECI operates at the aggregate level.

---

## 5. What Balland et al. (2019) contributes

Balland et al. (2019) `[training]` is the key paper that **bridges these frameworks**. It applies complexity-style relatedness measurement to regional technological diversification in European cities, finding that:

1. **Relatedness predicts entry** — consistent with both EEG and ECI
2. **Complexity matters beyond relatedness** — cities specializing in *complex* technologies grow faster in innovative capacity, even controlling for relatedness
3. **The combination is more powerful than either alone**

The theoretical contribution: **not all related diversification is equal**. Moving into a related-but-simple technology is a lower-value trajectory than moving into a related-and-complex technology.

---

## 6. What this means for your thesis

You are working primarily in the ECI-applied-to-regions tradition (density scores from co-occurrence matrices, RCA, the entry prediction test), but motivated by EEG's theoretical logic (capability recombination, path-dependent diversification). This is defensible and standard practice. Be explicit about it — do not claim you are testing EEG mechanisms when you are using ECI methods.

Balland et al. (2019) `[training]` is your direct methodological precedent. Use ECI methods, ground them in EEG theory, cite Balland as the bridge, and be honest about what your data can and cannot tell you about mechanisms.

---

*All citations in this response are tagged `[training]` — recalled from training data, not verified against the knowledge base. Verify bibliographic details before submitting.*
