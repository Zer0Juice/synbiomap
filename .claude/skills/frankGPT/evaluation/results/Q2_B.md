# Q2 — Condition B (baseline, no KB)

*FrankGPT — A Neffke-inspired agent*

---

Good. This is a question worth answering carefully, because the two frameworks are often lumped together as "relatedness" when they are doing quite different theoretical work.

---

## The key mechanism in Neffke's relatedness framework

Neffke's core claim is that regions diversify along lines of **skill relatedness** — the degree to which two industries draw on overlapping bundles of worker competencies. The mechanism is explicitly about **labor mobility**: when workers move between industries, they carry tacit, industry-specific skills with them. If those skills are transferable, the receiving industry benefits. If they are not, the worker is mismatched and either underperforms or leaves.

The measure of skill relatedness is therefore operationalized through **revealed labor flows**: two industries are related to the extent that workers actually move between them, over and above what a random mobility baseline would predict. This is not a theoretical construct imposed from outside — it is inferred from observed economic behavior.

The empirical payoff: regions whose existing industry portfolio is relatedly dense around a candidate new industry are more likely to enter that industry. The density variable — the average relatedness of existing specializations to the candidate — is the central predictive tool.

The microfoundation matters here. It is not just "proximity" in some abstract space. It is a claim about **human capital redeployment**: the productive capabilities embedded in workers can be moved across industry boundaries at lower cost when industries are skill-related. Structural change happens at the margin where capability reuse is possible.

Neffke, Henning & Boschma (2011) `[training]` is the canonical empirical anchor for this, using Swedish plant-level data over several decades. The finding that regions enter industries related to their existing portfolio, and exit unrelated ones, is reasonably well established `[unverified]`.

---

## How this differs from Hidalgo's product space

Hidalgo, Klinger, Barabási & Hausmann (2007) `[training]` build their relatedness measure on a completely different inferential logic: **co-export proximity**. Two products are related if countries that export one tend to export the other — revealed through trade flows rather than labor flows.

The underlying theoretical story in Hidalgo and Hausmann's broader complexity program is about **capabilities** in an abstract sense — the productive know-how, institutions, and infrastructure required to produce a good. Countries diversify by moving to nearby products in the product space because they can redeploy their existing (unspecified) capability bundle.

Here is where the frameworks diverge sharply:

| Dimension | Neffke (skill relatedness) | Hidalgo/Hausmann (product space) |
|---|---|---|
| Unit of relatedness | Industry pairs | Product pairs |
| Measure | Revealed labor flows | Revealed co-export patterns |
| Microfoundation | Worker skills, tacit knowledge | Abstract "capabilities" |
| Mechanism | Human capital redeployment | Unspecified capability reuse |
| Level of analysis | Region → industry | Country → product |
| Data requirement | Linked employer-employee records | International trade data |

The critical theoretical difference is **specificity of mechanism**. Hidalgo's "capabilities" are doing a lot of work without being precisely defined. They could be labor, institutions, infrastructure, trust — any of it. The product space is a powerful descriptive device, but the mechanism generating the relatedness structure is left underspecified. Neffke is more austere in scope but more precise: he gives you a specific, identifiable channel (worker mobility) and a specific empirical proxy (labor flow data). The tradeoff is that you need much richer microdata, which limits geographic coverage to countries with good administrative records like Sweden or Germany.

---

## What this means for your thesis

If you are analyzing city-level diversification in synthetic biology, the Neffke framework gives you a crisper causal story: cities enter new synbio subfields because the existing workforce has transferable skills. The Hidalgo product space framework gives you a more tractable empirical tool — co-specialization patterns are easy to compute from publication data — but at the cost of a vague mechanism.

The honest answer is that most applied work ends up using Hidalgo-style co-occurrence measures while invoking Neffke-style capability language. That is not necessarily wrong, but you should be clear about the gap. The density score you compute from concept co-specialization is closer to Hidalgo in operationalization, even if the theoretical motivation sounds more like Neffke.

If a referee asks "why does density predict entry?" you need an answer beyond "because relatedness." Either commit to the labor-mobility mechanism and defend why it applies to academic knowledge production, or reframe around a mechanism more defensible given your data — shared training pipelines, methodological proximity, equipment co-use. That is the work the theory section needs to do.

---

*All empirical claims above are tagged `[training]` or `[unverified]`. For exact coefficients, check the primary sources directly.*
