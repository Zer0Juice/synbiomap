# Canonical Reference Card

~20 foundational papers across the literatures frankGPT draws on.
Load this file when you need to verify a specific citation or confirm a paper exists.
For conceptual knowledge of these literatures, rely on training data — this card is for bibliographic precision, not orientation.

Each entry states **what the paper actually contributes** to the theoretical conversation, not just what it is about.

---

## Evolutionary Economic Geography & Relatedness

**Boschma, R. (2005). Proximity and Innovation: A Critical Assessment.**
*Regional Studies*, 39(1). **5,746 citations.**
DOI: 10.1080/0034340052000320887
Distinguishes five dimensions of proximity (cognitive, organisational, social, institutional, geographical) and argues that cognitive proximity is the key mechanism for knowledge spillovers, with too much closeness as harmful as too little. The canonical framing of *why* relatedness matters.

**Frenken, K., Van Oort, F., & Verburg, T. (2007). Related Variety, Unrelated Variety and Regional Economic Growth.**
*Regional Studies*, 41(5). **2,337 citations.**
DOI: 10.1080/00343400601120296
Decomposes regional diversification into related and unrelated variety; shows empirically that related variety drives employment growth while unrelated variety reduces unemployment. The foundational empirical paper for the related-variety hypothesis.

**Boschma, R., Heimeriks, G., & Balland, P.-A. (2014). Scientific knowledge dynamics and relatedness in biotech cities.**
*Research Policy*, 43(1). ~160 citations.
DOI: 10.1016/j.respol.2013.06.004
Applies the relatedness-density framework to scientific bibliometric data at the city level in biotechnology — the closest methodological template for city-level synbio/carbon-capture studies. Uses co-specialization across cities to derive relatedness, not embedding geometry.

**Balland, P.-A., Boschma, R., Crespo, J., & Rigby, D. (2019). Smart specialization policy in the EU: Relatedness, knowledge complexity and regional diversification.**
*Regional Studies*, 53(9). ~750 citations.
DOI: 10.1080/00343404.2018.1437900
Operationalises smart specialisation using relatedness and complexity; shows regions diversify into complex technologies only when they have sufficient related capabilities. Key paper for connecting relatedness to industrial policy and green transition.

**Rigby, D. (2015). Technological relatedness and knowledge space: Entry and exit of US cities from patent classes.**
*Regional Studies*, 49(11). ~345 citations.
DOI: 10.1080/00343404.2015.1060481
Uses USPTO patent classes to construct city-technology portfolios and tests whether density (relatedness to existing portfolio) predicts technology entry and exit across US cities. The direct patent-class analogue of what synbio diversification studies do.

**Hidalgo, C., Klinger, B., Barabási, A.-L., & Hausmann, R. (2007). The Product Space Conditions the Development of Nations.**
*Science*, 317(5837). **2,751 citations.**
DOI: 10.1126/science.1144581
Constructs a product space from revealed comparative advantage co-occurrences across countries and shows that countries diversify along relatedness gradients. The seminal paper for operationalising relatedness as co-occurrence rather than categorical similarity.

**Neffke, F., Henning, M., & Boschma, R. (2011). How Do Regions Diversify over Time? Industry Relatedness and the Development of New Growth Paths in Regions.**
*Economic Geography*, 87(3). **140 citations.**
DOI: 10.1111/j.1944-8287.2011.01121.x
Shows Swedish regions are most likely to branch into industries technologically related to their existing portfolio. The primary empirical demonstration of the density-entry mechanism at regional level using industry data.

---

## Economic Complexity

**Hidalgo, C., & Hausmann, R. (2009). The building blocks of economic complexity.**
*PNAS*, 106(26). ~3,084 citations.
DOI: 10.1073/pnas.0900943106
Introduces the Economic Complexity Index (ECI) via the Method of Reflections; treats country-product bipartite network as a signal of underlying capability stocks. Foundational for treating economic diversity as evidence of hidden capabilities.

**Hausmann, R., & Hidalgo, C. (2011). The network structure of economic output.**
*Journal of Economic Growth*, 16(4). ~800 citations.
DOI: 10.1007/s10887-011-9071-4
Formalises the fitness-complexity algorithm; argues that economic complexity is the best predictor of future income growth, outperforming standard capital or human capital measures.

---

## Agglomeration & Urban Economics

**Krugman, P. (1991). Increasing Returns and Economic Geography.**
*Journal of Political Economy*, 99(3). ~836 citations.
DOI: 10.1086/261763
The core-periphery model showing how transport costs, economies of scale, and factor mobility combine to generate spatial concentration. The canonical theoretical entry point for new economic geography.

**Glaeser, E., Kallal, H., Scheinkman, J., & Shleifer, A. (1992). Growth in Cities.**
*Journal of Political Economy*, 100(6). **4,530 citations.**
DOI: 10.1086/261856
Tests MAR (specialisation), Porter (competition), and Jacobs (diversity) externalities using US city-industry employment data; finds Jacobs diversity externalities dominate. The canonical empirical paper for distinguishing sources of agglomeration.

**Duranton, G., & Puga, D. (2004). Micro-foundations of urban agglomeration economies.**
*Handbook of Regional and Urban Economics*, Vol. 4. ~2,000 citations.
DOI: 10.1016/S1574-0080(04)80005-1
Surveys and unifies the three Marshallian externalities (sharing, matching, learning) as micro-foundations of agglomeration. The reference for anyone making claims about *why* firms or researchers cluster.

**Ellison, G., & Glaeser, E. (1999). The Geographic Concentration of Industry: Does Natural Advantage Explain Agglomeration?**
*American Economic Review*, 89(2). ~999 citations.
DOI: 10.1257/aer.89.2.311
Decomposes geographic concentration into natural advantage and spillover components using the Ellison-Glaeser index. Canonical for measuring the non-random component of industry clustering.

---

## Econometrics & Identification

**Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik Instruments: What, When, Why, and How.**
*American Economic Review*, 110(8). ~1,979 citations.**
DOI: 10.1257/aer.20181047
Shows Bartik shift-share instruments are equivalent to a weighted combination of industry-share instruments; validity requires industry shares to be exogenous, not national industry growth rates. Essential for any regional study using Bartik IVs.

**Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-Experimental Shift-Share Research Designs.**
*Review of Economic Studies*, 89(1). ~135 citations.
DOI: 10.1093/restud/rdab030
Proposes a complementary identification strategy where the shock (national growth) is quasi-randomly assigned across industries; validity requirements and standard errors differ from Goldsmith-Pinkham et al. Read alongside the above.

**Callaway, B., & Sant'Anna, P. (2021). Difference-in-Differences with multiple time periods.**
*Journal of Econometrics*, 225(2). **1,413 citations.**
DOI: 10.1016/j.jeconom.2020.12.001
Develops group-time ATT estimators for staggered DiD designs; shows conventional two-way FE estimators are biased when treatment effects are heterogeneous across cohorts. The go-to reference for modern DiD in panel settings.

**Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing.**
*Journal of Econometrics*, 225(2). **6,474 citations.**
DOI: 10.1016/j.jeconom.2021.03.014
Decomposes the TWFE estimator into a weighted average of all 2×2 DiD comparisons; shows that late-treated units acting as controls for early-treated units is the source of negative-weight problems. Canonical for understanding why TWFE fails with staggered treatment.

**Angrist, J., & Pischke, J.-S. (2009). Mostly Harmless Econometrics.**
*Princeton University Press*. **8,538 citations.**
DOI: 10.1515/9781400829828
The standard reference for applied causal inference: regression anatomy, IV, DiD, RD. If you are asking what identifies what, the answer is probably in here.

---

## Synthesis / Frontier

**Neffke, F., Henning, M., Boschma, R., Lundquist, K.-J., & Olander, L.-O. (2010). The Dynamics of Agglomeration Externalities along the Life Cycle of Industries.**
*Regional Studies*, 45(1). **265 citations.**
DOI: 10.1080/00343401003596307
Shows agglomeration externalities vary systematically with industry age and technological relatedness of co-located industries — connecting the relatedness and agglomeration literatures.

**Neffke, F., Hartog, M., Boschma, R., & Henning, M. (2017). Agents of Structural Change: The Role of Firms and Entrepreneurs in Regional Diversification.**
*Economic Geography*, 94(1). **358 citations.**
DOI: 10.1080/00130095.2017.1391691
Distinguishes the contributions of incumbent firms vs. entrepreneurs vs. local vs. non-local founders to regional branching; shows that non-local entrants introduce most novelty. Key for understanding *who* drives diversification, not just *what* knowledge enables it.
