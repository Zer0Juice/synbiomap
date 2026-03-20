---
source: 2021_Bridging_the_short-term_and_long-term_dynamics_of_economic_structuraln_chan.pdf
pages: 29
extractor: pdftext
tokens_raw: 28830
tokens_compressed: 27894
compression: 3%
---

Bridging the short-term and long-term dynamics of economic structural change

James McNerney,1, 2, ∗ Yang Li,1 Andres Gomez-Lievano,1, 3 and Frank Neffke1, 2
1Center for International Development, Kennedy School of Government,
Harvard University, Cambridge MA 02139, USA
2Complexity Science Hub Vienna, Vienna, Austria
3Analysis Group, Inc., Boston MA 02199, USA

Economic transformation – change in what an economy produces – is foundational to development
and rising standards of living. Our understanding of this process has been propelled recently by two
branches of work in the field of economic complexity, one studying how economies diversify, the other
how the complexity of an economy is expressed in the makeup of its output. However, the connection
between these branches is not well understood, nor how they relate to a classic understanding of
structural transformation. Here, we present a simple dynamical modeling framework that unifies
these areas of work, based on the widespread observation that economies diversify preferentially into
activities that are related to ones they do already. We show how stylized facts of long-run structural
change, as well as complexity metrics, can both emerge naturally from this one observation. However,
complexity metrics take on new meanings, as descriptions of the long-term changes an economy
experiences rather than measures of complexity per se. This suggests relatedness and complexity
metrics are connected, in a hitherto overlooked way: Both describe structural change, on different
time scales. Whereas relatedness probes transformation on short time scales, complexity metrics
capture long-term change.

arXiv:2110.09673v2 [physics.soc-ph] 24 Mar 2023

include the Economic Complexity Metric (ECI)18 and
country Fitness19, and others have been proposed in their
wake23,24,26,27,29,30
, such as GENEPY.

I. INTRODUCTION

The prosperity of an economy is tied to the economic
activities it can develop1
. Whereas places like Silicon Valley,
the city of London, and the country of Japan pursue
diverse and profitable activities, other places struggle to
shift out of a narrow range of activities with low economic
returns. Working to understand why, the emerging field of

While both branches of investigation have found success,
the connection between them is not well understood,
potentially limiting the development of this research
agenda and its interpretability for scholarly and

policy work. Here, we present a simple modeling framework
that links these branches, and suggests they describe
the same dynamical process of development, at different
time scales and granularity. Our framework begins by
making explicit the dynamics that are implicitly used
in the first branch to describe economic diversification
under the Principle of Relatedness (PoR). We then follow
a standard approach, analyzing these models with the
workhorse method of eigenmode decomposition. PoR

economic complexity has emphasized two branches of research.
In the first, researchers have asked how economies
(e.g. countries, regions, cities) develop into new sectors of

activity. One finding that repeatedly emerges is that economic
diversification typically entails shifts into activities
that are related to ones that are already in place. This
tendency has been corroborated in research on the growth
of industry clusters2,3, and on related diversification by
individuals4,5, firms6–8, regions9–13, and countries14–16
.
Recently these tendencies have together been referred to
as the Principle of Relatedness17
.

models describe economic structural change on short (e.g.
year-to-year) time scales. We work out the implications
of these short-run descriptions for economic evolution
over the long run. We show that the PoR implies the
importance of at least two kinds of long-run changes in an
economy’s basket of activities. One involves changes in
the diversity of activities (such as the number of product

A second stream of research has investigated the concept
of complexity, a term that refers to the sophistication
and diversity of the input needs of products, or of the

productive endowments of places – product complexity
and place complexity, respectively. More complex
economies are expected to make more complex and more

categories in which an economy competitively exports).
The other involves changes in their relative mix or composition.
These changes are tracked by a pair of coordinates,
one associated with diversity, the other with a particular
pattern of shifts in an economy’s activity basket.

profitable products by providing a richer basis of productive
capabilities. A key objective of this stream of
work has been to develop methods to infer the complexity
of products and places from data18–30. This literature
puts forward metrics to estimate complexity from the

We then show (1) how these coordinates re-express a
classic understanding of structural change, and (2) how
they relate to complexity metrics. The two coordinates
that emerge from the PoR resonate surprisingly well with

structure of a bipartite network that describes which locations
produce which products in quantities suggesting

a location has the needed capabilities to engage competitively
in the product. Well-known complexity metrics

how economists have long described economic development
in work stretching back decades. It is well known
that countries diversify as they rise through lower and
middle stages of income31,32, and undergo compositional
changes that include shifting out of labor-intensive forms

∗ james mcnerney@hks.harvard.edu

of agriculture and into other sectors33,34. Motivated by
this, we examine the coordinates that emerge from our
framework in data on global production patterns, asking
whether their movements capture these known stylized

produce. Complexity metrics are typically seen as competing
methodologies, each offering a potential solution
to a challenging inference problem – extracting country
and product complexities from observable patterns of
production. But our results suggest the two main contending
classes of metrics are not competing measures
but give useful, complementary information about an
economy’s development. Nevertheless, our results do not
associate complexity metrics with complexity necessarily,
and raise the question how well these metrics infer complexity
per se versus summarizing long-run changes in an
economy’s basket of activities, becoming principled ways
to restate and quantify classic statements of structural
change. Other more technical differences also arise from
basing complexity metrics on the PoR, which we discuss
in depth. Our paper also represents an effort to quantify
structural change in economies, and thus it both joins
recent literature, such as work focusing on regional and
city development9–13 or using new methods from machine
learning35, and provides continuity with classic literature
in economics31,33,34
.

facts. We use the coordinates generated by the framework
to describe 56 years of change in the export baskets
of about 250 countries and regions. What we find is that
the dominant movements of these coordinates are intuitive
and consistent with classic observations of economic
development. We see simultaneous movements along the
diversity and composition coordinates that correspond
to a well-documented pattern of development: Countries
diversify into making a greater number of products, while
simultaneously shifting out of agricultural products toward
manufactured goods (e.g.31,35). This demonstrates
the empirical relevance of our coordinates, and supports
an interpretation of them as summary measures of the
diversity and compositional changes associated with structural
change. This is also noteworthy because it shows
that transient, year-to-year dynamics contain a great deal
of information about the long-term, permanent development
of economies.

We then observe a close correspondence between the
coordinates implied by the PoR and complexity metrics.
Nearly all complexity metrics fall in one of two groups, as
shown in Fig. 1. This is surprising given the variety of theoretical
arguments that have been put forward to arrive
at different metrics, and the emphasis on these arguments
to justify one metric over another. One group contains
metrics that strongly correlate with an economy’s diversity,
and includes the country Fitness metric. The other
group captures compositional information about an economy,
and includes the ECI. These groups of complexity
metrics correspond numerically and theoretically to the
coordinates generated by our framework. That is, complexity
metrics come in two main types, and these types
are ones that should be expected to describe long-run
changes to an economy’s basket of activities if short-run
changes are accurately described by the PoR. Given this,
we propose a simple connection between the two main
branches of work in economic complexity: Complexity
metrics describe the long-term changes to an economy’s
basket of activities that are implied by the Principle of
Relatedness. In particular, the PoR delivers quantities
that track an economy’s diversity and composition.

II. RESULTS

A. The PoR as a dynamical model

A widespread finding about the geography of economic
activity is that particular activities tend to coincide in
the same places. These patterns are often intuitive; a
city, region, or country that makes cloth garments, for
example, is also likely to make other textiles (e.g. knitted
garments). These co-occurrences are assumed to indicate
that two activities are related (i.e. they depend on similar
underlying capabilities) and based on this various
measures have been developed to infer the relatedness of
different activities. For concreteness, we focus on relatedness
between exported products as inferred from their
co-occurrences within country export baskets. Exports
are often analyzed because harmonized data is available
across countries of very different levels of development,
and because exporting competitively represents an indicator
of reaching an important level of production ability.
Studies typically measure activity in an export using
the Balassa index of revealed comparative advantage
(RCA)39
, Rcp = θcp/θp, where θcp is the share of country
c’s exports devoted to product p, and θp is the share of
p in world exports. RCAs are often treated as measures
of inferred ability in exported products40,41, and these
quantities have also been used to characterize ability
in activities besides exports (where the meanings of θcp
and θp are adjusted appropriately). Here we follow suit,
though it is not an intrinsic requirement of our model to
measure ability this way.

In all, our modeling framework represents an approach
to economic structural change that exploits dynamical
systems methods, and in which the PoR and complexity
metrics, as well as classic findings of structural change,
are mutually reconciled. Besides the potential for using
this framework as a starting point for further studies,
many of our immediate findings relate to the understanding
of complexity metrics that have become widely used
in recent years36. We discuss these points in depth in
section II D. Briefly, our framework grounds these metrics
conceptually and mathematically on the PoR, a different
basis from the heuristic arguments that have motivated
these metrics, which ask how the complexity of a sector
or economy can be inferred from data on what economies

The relatedness, also called proximity, of products
p and p
is then computed by a measure of similarity
between the p and p
columns of the matrix R = [Rcp].
This means that p and p
0 are taken to be closely related
if high ability in p co-occurs with high ability in p
0 across

0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9

Diversity-like

ECI

Composition-like

FIG. 1. Spearman rank correlations among complexity metrics and the coordinates that emerge from our dynamical modeling
framework. Diversity here is the count of activities in which a place has a revealed comparative advantage above 1, a common
measure of the number of activities that a place performs competitively18,19, and often taken to have a close association with
an economy’s underlying complexity. Proposed complexity metrics include the Economic Complexity Index (ECI)18, country
Fitness19, Production Ability26, GENEPY27, Collective knowhow30, and the entropic measure of Teza, Caraglio, and Stella24
(here labelled TCS entropic). X1 and X2 are the first and second components of the GENEPY metric27
. A, A
M, and A
C are
different variations of the first coordinate that emerges from our dynamical framework, based on different literature approaches
for estimating proximity between activities, and b, b
M, b
C are the corresponding variations of the second coordinate that
emerges from our framework. All complexity metrics and other quantities were computed for the year 2016 using UN Comtrade
data37
.

locations. As one example, Hidalgo et al. (2007)15 say
a country has significant ability in a product if its RCA
in the product exceeds 1, and compute the conditional
probability Qpp0 that country c has an RCA greater than
1 in good p given that it also satisfies this condition for p
.
The proximity Φpp0 between products p and p
is taken to
be the lesser of Qpp0 and Qp0p: ΦM
pp0 ≡ min(Qpp0 , Qp0p).
The structure of proximities between products is often
visualized using network representations (Fig. 2a).

two such regressions analytically will also lead to an
expression of the form of Eq. (1). These types of analyses
overwhelmingly find a robust, positive statistical
association between density and future growth and diversification,
bolstering the idea that relatedness measures
capture underlying similarities in activities that make
some transitions easier to achieve than others, influencing
the direction in which an economy develops.

In general, the PoR treats diversification as a process
of spreading on a network of economic activities. One
such example is the network of products in Fig. 2. The
relatedness network is typically taken to be fixed for the
purpose of predicting this process. Using Eq. (1) we can
make make more explicit the dynamical model the PoR
implies. The results that follow use network concepts (see
e.g.44) and the dynamical systems method of eigenmode
decomposition (see e.g.45). A given economy has various
levels of ability in different activities, which are given by
elements of a vector R(t). We call this the economy’s
activity basket. These abilities evolve as the economy
improves or shifts into new parts of the network. Using
Eq. (1) as a guide, a simple model of the diversification
process is

Crucially, changes in an economy’s activities are predicted
by the structure of proximities. Empirical studies
show that the development of high ability in an exported
product tends to be preceded by high ability in nearby
products15. A typical regression modeling setup11,13,42,43
to explore this effect takes future ability in a product p
to be a function of the density around it, defined as the
average ability that an economy has in other products,
weighted by proximity to p:

Φpp0
P
p00 Φpp00

X
p0

Rp(t + 1) = b1Rp(t) + b2

Rp0 (t) + εp(t).

(1)

An alternate setup16 contains two steps, with ability in
product p first regressed on density in the same time period,
establishing the existence of systematic correlations
in which economic activities co-occur. Residuals from
this regression are then used to forecast appearances of
comparative advantage in future periods. Combining

τ

R˙ (t) = γ(t)R(t) −

LΦR(t), (2)

where γ(t) is an arbitrary growth rate, LΦ is a graph
Laplacian, and τ is a time scale. The two terms on the
right capture two kinds of changes. An economy’s abilities

a

b

c

FIG. 2. Network visualizations of relatedeness between tradable products. a To construct the network above we use an
approach similar to Hidalgo et al. (2007)15. Using UN Comtrade data37 we compute the revealed compared advantages (RCAs)
of each country in each product p, and obtain the conditional probability across countries Qpp0 that a country has an RCA
greater than 1 in good p given that it also meets this condition for p
. We then compute relatedness between products p and
p
as ΦM
pp0 ≡ min(Qpp0 , Qp0p). For other approaches to constructing the network see e.g. Ref.16,38
. b-c The first two right
eigenvectors of the row-normalized proximity matrix Φ˜
pp0 = Φpp0/
P
p00 Φpp00 . The first eigenvector is simply a uniform vector.
For the second eigenvector red nodes are positive entries while blue nodes are negative entries.

average ability in activities around p (
P
p0 Φ˜
pp0Rp0 (t))
exceeds that in p itself (Rp(t)), ability in p rises. The last
term in Eq. (3) can also be negative, corresponding to a
decline in ability. In addition, abilities have the freedom
to rise or fall as a whole because of the term γ(t)Rp(t).
Integrating Eq. (2) over time leads to

can rise or fall as a whole, and they can shift according
to the Laplacian term to weight activities differently,
changing which ones receive the most emphasis.
The Laplacian term reflects an implicit choice of empirical
specifications of the PoR as instances of consensus
dynamics (e.g.45). The Laplacian LΦ captures the structure
of the network and governs shifts between activities,
taking the form LΦ = I−Φ˜ where Φ˜ is a proximity matrix
with rows normalized to sum to 1, Φ˜
pp0 = Φpp0/
P
p00 Φpp00 .
With this assumption, a discrete-time approximation of
Eq. (2) in index form reads

R(t) = A(t)P(t)R(0), (4)

where the dynamics are now captured by the scalar A(t)
and the matrix P(t). The prefactor A(t) ≡ e
R t
γ(s) ds is a
shift factor that captures accumulated growth in overall
ability up to time t, scaling the R vector up or down
as a whole. The matrix P(t) = e
−LΦ(t/τ)
is a stochastic
matrix that transforms R, changing the relative emphasis
on different activities over time.

Rp(t + ∆t) − Rp(t)
∆t

≈

X
p0
Φ˜
pp0Rp0 (t) − Rp(t)

 . (3)

γ(t)Rp(t) + 1
τ

Implementing this model involves some practical
considerations. First, RCAs are commonly transformed
non-linearly to weaken the influence of extreme
values16,35,46,47. When we use RCAs as a measure of
ability, we will do so as well, but note that this does
not change the model in any fundamental way. Second,

In this form the dynamical model is easily compared with
regression setups that test for the PoR in the literature.
Ability in activity p changes between periods in a way
that depends on ability in nearby products. When the

we need to choose how to operationalize the network of
relatedness Φpp0 between activities. Studies have used
a variety of measures of proximity. We consider several
options, finding similar outcomes, as we discuss later.

patterns of deviation decays with time at the rate set by
τµ, the characteristic time scale of the µth eigenmode.
If the pre-factor A(t) were fixed and equal to 1, then a
region would be destined to have ability c1(0) in every
product. Letting A(t) change over time, the final level of
ability in products can be arbitrarily high or low.

B. A PoR-derived coordinate system to describe
an economy’s activity basket

To better understand the implications of the PoR for
economic change over the long term, we focus on the
two modes of change associated with dynamics on the
longest time scales. Absorbing the coefficient c1(0) into
A(t), and defining the coefficient b(t) ≡ c2(0)e
−t/τ2
, the
longest-lived dynamics of R(t) are described by the two
leading terms of Eq. (5):

Dynamical models are frequently analyzed in terms
of their dynamical modes, called eigenmodes in linear
models. Applying eigenmode decomposition to the model
above leads to a coordinate system that can be used to
describe the evolution of an economy’s activity basket.
Let vµ be the µth right eigenvector of LΦ and let κµ be its
eigenvalue. Ordering eigenvalues from least to greatest,
the first right eigenvector has κ1 = 0 and is a uniform
vector of real positive numbers. It can be taken to be a
vector of 1s, v1 = 1. Higher-order eigenvectors (v2 and
up) have κµ > 0, and contain a mix of elements with
positive and negative real parts.1 The right eigenvectors
of LΦ form a basis for the vector space of activity baskets
R(t), and as a result, one can write any such vector as a
linear combination R(t) = P
µ
cµ(t)vµ. Letting wµ be

R(t) ∼ A(t)1 + A(t)b(t)v2. (6)

The coefficients A(t) and b(t) have simple interpretations.
A shift in A(t) corresponds to a region realizing a uniform
change in abilities across activities. A shift in b(t)
corresponds to a compositional shift. Some activities rise
in ability and others fall, as determined by the signs and
magnitudes of entries in v2. Together, these coordinates
situate the activity basket R(t) in a 2D space.

To further interpret the A(t) coordinate, let π = w1
denote the first left eigenvector of LΦ, normalized so that
its elements sum to 1, and note that R¯(t) = π
T R(t)

the µth left eigenvector of LΦ, the coefficients cµ(t) may
be computed by exploiting the biorthogonality of left and
right eigenvectors, w†
µvν = δµν, giving cµ(t) = w†
µR(t).
Following the usual steps of eigenmode decomposition,
one can decompose R(t) to separate different
modes of change according to their time scales. Plugging
R(0) = P
µ
cµ(0)vµ into Eq. (4) gives R(t) =
A(t)
P
µ
cµ(0)e
−κµt/τvµ. The first term contains the
first eigenvector v1 = 1 and corresponds to the fixed
point of the simpler model R(t) = P(t)R(0) (i.e. the
model with the factor A(t) fixed at 1). Separating the
first term from other terms of the sum we have

defines a weighted average of the abilities of a region.
By again exploiting the biorthogonality of left and right
eigenvectors, it can be shown (see Methods, Eq. (17))
that A(t) equals this average:

A(t) = R¯(t) ≡ π

T R(t). (7)

For this reason, we refer to A(t) as the average ability
coordinate.

To further interpret the b(t) coordinate, note that the
activity basket R(t) conveys two types of information: the
relative mix or composition of activities, as well as ability
levels. Factoring out an economy’s average ability A(t)
from R(t) gives a normalized vector, r(t) ≡ R(t)/A(t),
that characterizes only the composition of activities. In
particular, dividing Eq. (6) by A(t) we see that r(t) ∼
1 + b(t)v2, showing that b(t) characterizes the deviation
of the compositional vector r(t) from uniformity.

X

−t/τµ vµ

R(t) = A(t)

c1(0)1 +

cµ(0)e

 , (5)

µ≥2

where we defined τµ ≡ τ /κµ.
Eq. (5) describes the following behavior. First, neglecting
the effect of the shift factor A(t), the activity basket
of a region converges over time to a uniform vector c1(0)1.
In this state, the region has equal ability in all products.
On its way to this state, the basket shows higher ability
in some products and lower ability in others, and each
eigenvector vµ describes a different pattern of deviations
from the long-term steady state in which all activities
are equally important. Because each eigenvector vµ (for
µ ≥ 2) satisfies w
†
1vµ = 0, where w1 has only positive
elements, each such eigenvector has some elements that
are positive and others that are negative. Each of these

C. Diversity and composition of exports baskets
over time

The PoR thus delivers coordinates that theoretically
could be used to characterize the activity basket of an
economy. We now examine these coordinates empirically,
asking whether their movements corroborate known facts
of economic development. We focus on international
trade data from UN Comtrade37, which are frequently
used in research on economic complexity, because they
offer a detailed description of what economies export
over long periods of time. This allows us to construct our
coordinates to describe the evolution of countries’ export
baskets from 249 countries over the 57-year period 1962 -

1 Depending on the proximity matrix used, some eigenvectors
could contain imaginary parts, but this would pose no special
difficulties in interpreting modes; see Supplementary Note S1.

a GDP per capita (2010 US$ PPP)

Diversity

1.0

b

c

1.0

1.0

Composition coordinate b (ECI*)

Composition coordinate b (ECI*)

Composition coordinate b (ECI*)

0.5

$30000

0.5

0.5

20000
30000

10 20 30 60 100

0.0

$10000

10000
20000

0.0

0.0

-0.5

$3000

-0.5

-0.5

OECD

$1000

-1.0

developing
tax havens

-1.0

-1.0

resource-rich

$300

0 0.2 0.4 0.6 0.8 1
Average ability coordinate A
-1.5

0 0.2 0.4 0.6 0.8 1
Average ability coordinate A
-1.5

0 0.2 0.4 0.6 0.8 1
Average ability coordinate A
-1.5

d e

Region 2
Region 3

Region 2
Region 3

Composition coordinate b (ECI*)

0.5

100 years

60 years

-0.5

30 years

20 years

-1

10 years

Region 1

Region 1

0 years

0 0.2 0.4 0.6 0.8 1
Average ability coordinate A
-1.5

0 0.2 0.4 0.6 0.8 1
Average ability coordinate A

FIG. 3. Country export baskets plotted according to average ability (A coordinate) and composition (b coordinate), based on
Comtrade data37 for 249 countries and regions over the period 1962 - 2018 (11,544 observations). We analyze these data at the
3-digit SITC product level (235 product categories). a-b We form bins in the 2D plane to collect country-year observations, and
compute average GDP per capita and average diversity d within each bin. White lines are contours of a LOWESS-smoothed
surface fit to bin averages. c Positions of export baskets in 2018 of four categories of economies. ‘Developing’ refers to economies
on the UN’s least developed economies list48, ‘tax havens’ to non-OECD and non-developing countries appearing in Hines
(2010)49, and ‘resource-rich’ to economies not elsewhere categorized whose natural resource rent50 exceeded 5% of GDP in 2018.
d Number of country-year observations in each bin. e Quiver and streamline plots for the average directional change over 20
years for countries beginning at different starting points in the plane. Red dots in the right panel follow one streamline and
roughly convey the average pace of movement, though no streamline should be taken as a typical country trajectory; individual
countries display wide variation in both direction and speed of change. To construct the quiver plot, we divided the plane into
10 equal-size bins horizontally and 12 equal-size bins vertically (120 bins total). For each bin we obtain the horizontal and
vertical components of movement by computing the average horizontal change ∆A and average vertical change ∆b over the
next 20 years using all observations starting in the bin. We used the MATLAB quiver function to render a vector field and the
streamslice function to render a streamline plot.

2018. This exercise summarizes country development by
two simple statistics.

per capita (Fig. 3a). For example, holding A fixed at 0.5,
an increase in b from -0.5 to +0.5 is associated with an
increase from about $1500 to $30,000 (2010 US dollars
PPP). In contrast, the association between a country’s
average ability A and its income when holding the value
of b fixed is weak at best.

RCAs are commonly transformed to mitigate the influence
of extreme values, and here we transform the heavytailed
RCAs with the function g(R) ∼ log(1 + R/R0).
We tune the parameter R0 such that it maximizes the
variance that the b coordinate can explain across time and
countries (Methods section, “Transformation of RCAs”).
We then calculate for each country c and time t the RCA
vector Rc(t) on this transformed scale and use these
vectors to compute the A and b coordinates.

The situation is roughly opposite when we examine
countries’ economic diversity in these coordinates (Fig.
3b). The diversity of a country’s economic activity has
been quantified with a number of measures, such as the
Gini coefficient and Herfindahl-Hirschmann index (e.g.31),
or the count of products dc in which a region c has an
RCA greater than 1. Higher values of the average ability
coordinate A are closely associated with greater diversity
in a country’s export basket. Holding b fixed at 0, an
increase in A from 0.1 to 0.9 is associated with an over
10-fold rise in the number of products with RCA above 1.
In contrast, when holding A fixed, a compositional shift
towards higher levels of b is only weakly associated with
higher export diversity.

Figs. 3a-b depict country income and export diversity
as functions of A and b. For reasons that will become
clear in the next section, we also refer to b as ECI* in
these graphs. Plotting income and diversity this way
allows us to ask how each of these variables vary as a
function of one coordinate while holding the other fixed.

Income increases with b, diversity with A. A higher
value of the compositional coordinate b for a country’s
export basket is associated with significantly higher GDP

Different types of countries inhabit different regions
of this coordinate system (Fig. 3c). The industrialized
countries of the OECD are predominantly located in the
right of the plot with relatively high values of both A
and b, corresponding to diverse, high-income, developed
economies. In the lower left we find a set of undiversified
developing economies as defined by the UN’s least developed
economies classification. In contrast, in the upper
left, we find countries that are also undiversified, yet
frequently have high-income. Many of these are resourcerich
economies or are often considered tax havens49
.

long-lived shift in their export baskets away from agricultural
products and towards manufactured products.
This shift is consistent with the long-observed tendency
for economies to move from agriculture to manufacturing
(and then on to services, a move that largely eludes trade
statistics) as they develop33,34
.

If a country traverses the length of the diagonal band in
Region 1 it will arrive in Region 2, where countries have
high-income, diverse, developed economies. Within this
region, the average speed of movement is much lower than
in Region 1. This in part owes to the fact that export
baskets here evolve in a greater variety of directions, with
an average directional change near zero. Broadly though,
countries in Region 2 tend to sustain a high b, somewhat
above zero, and move within a range of relatively high
A values. On reaching Region 2, a number of countries
move toward lower values of A. This transformation path
is consistent with a phenomenon in which countries see a
fall in diversity in late stages of development31,32
.

Note that, although countries often diversify as they
rise in income31, the observations above do not directly
associate higher income with higher diversity of exported
products. Rather, they suggest that what matters more
for a country’s GDP per capita is the composition of
exports1
. We next explore the dynamics of countries in
this space and probe this distinction further.

Country development. Export baskets occupy a triangular
region of the A-b phase plane. A particularly
densely occupied portion of this plane is a diagonal band
that stretches from low A and low b, to high A and
above-average b (Fig. 3d). We start by focusing on the
movement of countries whose export baskets lie in this
band. Countries show diverse trajectories (see Supplementary
Note S2). To nevertheless characterize broad
tendencies over long periods, we group country-year observations
into bins in the A-b plane. We examine the
average direction and speed of movement over the next 20
years for observations that start within a given bin. For
expositional convenience, we summarize our results by
referring to three regions of the plane, labelled Regions
1, 2, and 3 (Fig. 3e).

Finally, countries in Region 3 tend to have high income
and low diversity. Many of these countries are abundant
in natural resources (particularly oil) or function as tax
havens. In this region, countries tend to move quickly
toward lower levels of b, converging near zero. We are
not aware of any prior observations that this movement
corresponds to. Evidently it is difficult for these countries
to sustain a high degree of specialization in products that
load positively on v2 for long periods of time.

Together, these observations show an end-to-end agreement
of our framework between short-term and long-term
changes in economic development. The Principle of Relatedness
describes structural change on short time-scales,
and fine-grained levels of sectoral resolution. When we
analyze network models that operationalize this principle,
using the standard technique of eigenmode decomposition,
we arrive at coordinates that should capture activity
changes over long time-scales, and higher levels of aggregation.
As one would hope, observed movements of
export baskets in these coordinates yield long-term and
coarse-grained descriptions of structural change that are
consistent with well-documented stylized facts.

Countries beginning in the lower part of the main diagonal
band – i.e. in Region 1 – trend over decadal time
scales in a lower-left-to-upper-right direction. Given how
the coordinates A and b are defined, a simultaneous increase
in both directions corresponds to an export basket
that simultaneously realizes two kinds of changes: (1)
a general improvement in ability across products; (2) a
shift in composition towards products with positive values
in the vector v2. These two components of movement
are associated with different effects. The shift in the
composition of exports captured by increasing b is (empirically)
most directly associated with increased GDP
per capita (Fig. 3a). In contrast, the increase in A is
more associated with a rise in export diversity (Fig. 3b).
These patterns are consistent with the idea that higher
income is associated with exporting particular products,
rather than diversification per se. Nevertheless, in practice,
countries in the lower part of the main diagonal
band that succeed in reaching such products tend do so
while simultaneously diversifying into a broad range of

Before moving on, we note that higher-order eigenvectors
beyond the second are of interest because in principle
they could describe other important modes of transformation.
However, the proximity matrices in the literature
only show strong agreement in the structure of the first
two eigenvectors, and do not straightforwardly resolve
how many eigenvectors matter (see Supplementary Note
S3).

D. Comparing our structural change coordinates
with complexity metrics

goods, including ones not associated with higher income.
What products are involved in the vertical shifts that

We see that the PoR leads naturally to coordinates
that track the process of structural change. We now
show that the resulting coordinates closely resemble complexity
metrics that have been proposed in recent years,
even though the latter have been motivated along very

increase b? Manufacturing products very often have positive
elements in v2, and agricultural products very often
have negative elements. As a result, countries in Region 1
that traverse the length of the diagonal band see a broad,

different lines than the coordinates we derive here. Complexity
metrics have been put forward as practical tools to
draw inferences about the number of distinct production
capabilities that different economies possess, based on observations
about which activities are performed in which
places. Among the metrics that have been proposed
are the Economic Complexity Index (ECI)18, country
Fitness19,23, the entropic measure of Teza, Caraglio, and
Stella24,29, Production Ability26, GENEPY27, and collective
knowhow30. We first describe the relationships
between these metrics and our coordinates and then comment
on their significance afterwards.

Different complexity metrics are set apart by many
differences in motivating narrative and implementation.
Despite this, empirically, complexity metrics fall into
two main groups that emphasize different kinds of information
(Fig. 1). These groups have a straightforward
correspondence with the coordinates generated from the
PoR. The first group contains diversity-like quantities.
This includes diversity dc itself, the A coordinate of our
framework, country Fitness, Production Ability, and the
entropic measure of Teza, Caraglio, and Stella. The other
group contains quantities that capture a particular type
of compositional information about an economy; roughly,
the agriculture-to-manufacturing axis noted earlier. This
group includes the ECI, and the b coordinate of our framework
(ECI*). The GENEPY metric by design combines
information associated with both groups, and itself does
not fall clearly in either one, but its first component X1
by construction is related to Fitness and is associated
with the first group, while its second component X2 by
construction is related to the ECI and is associated with
the second group (see also Supplementary Note S4 for
further discussion of complexity metric correlations).

FIG. 4. The b coordinate (ECI*) versus ECI for 249 countries
and regions and 57 years computed from Comtrade data37
.

tion with the vector PCI in general. To distinguish the
conventional PCI vector and the second eigenvector of
the dynamical model, we will call the latter PCI∗ ≡ v2.
In general, PCI∗
and PCI are strongly correlated, and
in the special case Φ = ΦP they are identical.

The coordinate b(t), which tracks where a country
lies on the axis of economic change described by the
eigenvector v2 = PCI∗
, is in turn closely related to the

ECI. We define an ECI-like quantity in our framework,
ECI∗
(t) ≡ b(t). To see that this coordinate is closely
related to the ECI, note that a country’s ECI is equal
to the average PCI of the products in which the country
has an RCA greater than 1:53,54

!

Mcp
p0 Mcp0

These correlations can be anticipated on theoretical
grounds. The diversity-like quantity A =
P
p Rcpπp we
derive is a sum over the activities that a country performs
at significant ability levels, weighted by the all-positive elements
πp. Similarly, the Fitness metric Fc =
P
p McpQp
is a sum over the activities that a country performs at
significant levels with weights given by the all-positive
product Qualities Qp. Not surprisingly, these quantities
strongly correlate both with each other and with the
count of products in which a country has an RCA greater
than 1, dc =
P
p Mcp, a standard measure of diversity.

X
p

ECIc =

PCIp. (8)

P

We can compare this with the ECI*, which can be computed
by observing that b(t) = c2(t)/c1(t) and calculating
the eigen-expansion coefficients c2 and c1. The resulting
calculation (see Methods, “The b coordinate (ECI*)”)
yields

!

Rcpπp
p0 Rcp0πp0

X
p

ECI∗
c =

PCI∗
p

. (9)

P

Similarly, the b(t) coordinate has a close theoretical
connection to the ECI and its counterpart metric, the PCI.
The PCI and ECI were proposed by Hidalgo and Hausmann
(2009)18, and can be computed with an eigenvector
computation as noted by Caldarelli et al. (2012)51,52
.
When proximities are measured as ΦP
pp0 ≡
P
c
McpMcp0
Dc
,
the second vector v2 of the dynamical model and the
vector of PCIs (PCI) solve the same eigenvector equation
(see Methods section, “The eigenvector v2 (PCI*)”),
and are therefore identical up to a normalizing constant.
There is ambiguity about which proximity measure one
should use to construct the network of activities, yet we
find that the second eigenvector is not sensitive to this
choice (see Methods, Fig. 7) and has very high correlaThe
ECI and b(t) are simply different averages of PCIs
or PCI*s. The conventional ECI gives equal weight to
activities in which the country has an RCA greater than
1, and zero weight to other activities. The ECI* weights
activities by their RCA, adjusted by the elements of the
first left eigenvector π = w1. Not surprisingly, these
averages are strongly correlated (Fig. 4), and this holds
for any proximity matrices we consider (see Methods, Fig.
7).

Interpretation. What do we make of these close numerical
and theoretical connections between complexity
metrics and the PoR-derived structural change coordinates?
Table I summarizes differences between the usual

a

b

c

region 1

v2
(PCI*)

b1(t)
(ECI* 1)

v2
(PCI*)

b2(t)
(ECI* 2)

region 2

FIG. 5. The order in which key quantities are computed in our framework. a A relatedness network is first defined, on which
various patterns of transitions can be described, such as b the compositional mode of change described by the elements of v2
(PCI∗
). Negative values (blue) correspond to economic activities that are vacated in relative terms, while positive values (red)

correspond to activities that are reached. c A region’s coordinate projection onto this mode determines its value of b (ECI*).

view of complexity metrics and the dynamical systems
view we present here based on the PoR. First, these connections
demonstrate (echoing and expanding on Ref.53)
that quantities very similar to complexity metrics can
be motivated through arguments that have little per se
to do with ‘complexity’. The relevance of A(t) and b(t)
is not tied to considerations of how to infer complexity
from data, but to how aptly they characterize long-lived
patterns of change in economies.

the arithmetic average complexity of the products that
a place exports competitively (i.e. with an RCA greater
than 1), and G to be the arithmetic average complexity of
the countries that competitively export a given product.
Alternatively, one obtains Fitness by replacing G with a
harmonic average. But the structure of the framework
here differs fundamentally. There is no co-determination
but a two-step sequence (Fig. 5a-c): According to the
PoR, there is a diversification process shaped by a relatedness
network, whose eigenvectors capture different
directions of change across activities, onto which any
given region’s coordinate projections can be computed.
This difference in frameworks is related to another – several
product complexity metrics18,27 are derived from a
similarity matrix between products, while country metrics
are derived from a similarity matrix between countries.
But the approach here uses just one of these matrices –
between products. Under the mindset we adopt to derive
our results, this matrix is the fundamental one, capturing
technological relationships between products. The
country similarity matrix is incidental, capturing current
similarities between countries depending on where they
happen to be in their development.

Second, our results suggest that debates between the
main contending metrics could be pointless. Complexity
metrics are typically viewed as being in competition
with one another, since they each represent alternative
methods to estimate the same underlying quantity (complexity).
But clearly we would not view the coordinates
A(t) and b(t) this way; these coordinates just summarize
different, complementary information about economic
activity baskets, focusing either on their diversity (A(t))
or composition (b(t)). The results here affirm the empirical
relevance of complexity metrics, while raising the
question whether they infer complexity, or essentially
summarize major changes in an economy’s basket of activities
that are associated with development, effectively
becoming principled ways to recapitulate and quantify
classic statements of structural change. In the latter
case, different metrics emphasize different aspects of development,
related either to changes in the diversity or
composition of activities. But as Fig. 3 illustrated, and
classic and recent literature supports31,33–35, both types
of changes are general features of economic development.
Third, the mathematical frameworks used by some

Fourth, our results would help make sense of conundrums
that so far have been swept under the rug. For
example, oil production is ranked near the bottom of
complexity by both the PCI and product Quality measures
– yet oil production is clearly a complex activity,
requiring knowledge of several fields of engineering, geology,
chemistry, physics, transportation and logistics,
business operations, and other areas. At the other end of
the spectrum, pottery and works-of-art are ranked highly
by these metrics, yet are clearly low-complexity goods.
But these cases are not mysterious if these metrics are
not taken as methods to infer complexity, but as measures
that track the trajectory of structural change. Then
these rankings would reflect the fact that oil is a difficult
product for an economy to diversify away from,2 and that

complexity metrics could be unnecessary. Several approaches
adopt a framework in which country and product
complexity metrics are co-determined by a system of
equations18,19,27, i.e.

country complexity = F(product complexities)
product complexity = G(country complexities).

This approach is seen as a way to constrain the metrics
and give them reasonable properties, with different metrics
arising from different choices for functions F and
G. For example, one obtains the ECI by taking F to be

2 Explanations for the “resource curse” have long been debated,
see e.g.55
.

Complexity inference view Dynamical systems / PoR view

Goal Solve an inference problem: Estimate country and product
complexities.
Characterize activity baskets: Describe baskets of economic
activities in low-order terms using particular coordinates.
Competitors or complements?Different
metrics are in competition. They offer different
methods for solving the inference problem above.
Metrics belonging to different classes in Fig. 1 are largely
complementary. They summarize different information (diversity,
composition) about an economy.
Derivation Motivated by a data challenge: Infer complexity from data
about what goods are produced where.
Derived from a model: Coordinates emerge from a dynamical
model of economic diversification.
Role for Principle of
Relatedness?
None in particular. Yes - the PoR implies the relevance of particular coordinates.

Product and
country metrics...

...have similar interpretations: Both measure complexity.
In some setups these metrics solve a set of simultaneous
equations.

...have different interpretations: Product metrics collectively
describe a direction of economic change, country metrics individually
show where a country lies along this axis. Product
metrics are computed first, and country metrics follow.

TABLE I. Comparing the usual view of complexity metrics and the dynamical systems view here based on the Principle of
Relatedness.

pottery and artwork are activities that are most readily
supported in economies that are rich and developed.

decaying ones, a well-known outcome of the interaction
of structure and dynamics in networks45,56. (See also
Supplementary Note S5 for an expanded discussion.)

Our results invite us to ask whether complexity metrics
essentially summarize structural change, rather than act
as inference methods that recover hidden information
about complexity. Nevertheless, we cannot rule out the
possibility that these metrics play both roles at the same
time. Some recent works explore this by making assumptions
about the structure of capabilities and how they
are acquired through the process of development25,30
.
The close correspondence between complexity metrics
and long-term change would then reflect the fact that
economies become more complex over time, though why
and how they do this is not entirely clear. (Presumably,
raising productivity or well-being is the goal of development,
not complexity per se.)

Mealy et al. (2019)53 point out that the conventional
ECI can be seen as a dimensionality-reduction tool, equivalent
to a spectral clustering algorithm that orders regions
along an axis that scores the similarity in their baskets
of activities. Our results are consistent with this view
and extend it, showing that the ECI is not just a similarity
score but also tracks a classic, long-lived pattern of
compositional change. Our results also relate to other,
diversity-like complexity metrics, showing how these relate
to the dynamics of the PoR. Sciarra et al. (2020)27
put forward a complexity index (GENEPY) that reduces
the dimensionality of economic activity data in a different
way, combining information from two eigenvectors of a
country similarity graph. In one sense, this is related to
what we do here, because we also exploit a 2-dimensional
picture of country development. The difference is both
technical and conceptual – the two components that underly
GENEPY are taken directly from the elements of
the first two eigenvectors of a country-country similarity
graph, while the model on which our framework is based
takes similarities between economic activities to be fundamental,
giving rise to eigenvectors that characterize
directions of change, and then our coordinates result from
projecting countries’ export baskets onto these vectors.
Finally, Brummitt et al. (2020)35 apply machine learning
methods to historical export data to extract dimensions
that characterize variation in export baskets across countries
and time, finding axes that strongly correlate with
the PCIs. This is also closely related to the work here,
because the first principal component in Brummitt et al.
captures a simultaneous increase in export diversity and
a compositional shift, precisely the two kinds of changes
that our analytically-derived coordinates separate.

Dimensionality reduction and related works. We
are in a position now to discuss several recent works
that approach economic complexity from the perspective
of dimensionality reduction. While we emphasized
the dynamical meaning of A(t) and b(t), one could also
think about these quantities in a dimensionality-reduction
framework.

First, note our method of analysis (eigenmode decomposition)
is also a dimensionality-reduction technique –
it returns axes (the eigenvectors vµ) in which one can
describe high-dimensional data (the matrix of activity
baskets R(t)) along with the coordinate projections of observations
onto these axes (coefficients cµ(t)). Differences
arise in how directions in the vector space are determined
and interpreted, as dimensionality-reduction techniques
typically aim to identify directions that capture high
amounts of variation in data, while eigenmodes characterize
coherent patterns in dynamics. In fact, an eigenmode
decomposition not only generates a representation of
data in a low-dimensional vector space, but shows that
the model predicts that countries’ activity baskets will
converge to such a subspace (i.e. corresponding to the directions
with the largest time scales). Differences between
countries shrink first among quickly-decaying dimensions,
leaving activity baskets scattered primarily along slowlyIII.
DISCUSSION

There are two broad ways to view the results here.
First, our work represents a dynamical modeling frame-

work to bridge between short-term and long-term descriptions
of economic structural change. The Principle of
Relatedness and its empirical implementations describe
structural change on short, year-to-year time scales, and
across fine-grained sectors of activities. In contrast, classic
observations of structural change33,34 emphasize the
slow transition of economies over decades across broad
economic sectors, along with changes in an economy’s
diversity31. As one would hope, a dynamical framework
based on short-term observations is consistent with and
bridges into classic observations of long-term change. In
this way our paper elaborates on a long-standing goal of
research, dating back at least to Kuznets34, to understand
the trajectories of economic transformations.

METHODS

Below we first describe theory results that serve as the basis
for our analysis, and then describe our data sources and
empirical methods.

Relationship between left and right eigenvectors. Analyzing
our dynamical model involves manipulations of the
left and right eigenvectors of LΦ. Here we derive a relationship
between these eigenvectors (Eq. (10)) that we use to
help determine our normalization convention for these vectors
(next section), as well as to help derive our ECI-like expression
for the b coordinate, Eq. (9) (see section “The b-coordinate
(ECI*)” below).

First, note that LΦ = I − Φ˜ and Φ˜ share the same eigenvectors.
The matrix Φ˜ = D
−1Φ with D = Diag(Φ1) is a

Second, our results tie together two areas of work in the
rapidly growing field of economic complexity. The field’s
major branches – studies of relatedness, and complexity
metrics – share concepts and motivating questions, but
are linked more in spirit than in math. The framework
here connects these branches, suggesting that they refer
to short-term and long-term consequences of the same
assumptions about economic development.

row-normalized stochastic matrix, and so its principal right
eigenvector may be taken to be a vector of 1s, v1 = 1. Its
principal left eigenvector can be understood as a vector of
stationary probabilities π for the Markov chain described by
Φ, ˜ w1 = π.

Define Π = Diag(π). If Φ is symmetric, then the left and
right eigenvectors of Φ are related by ˜

Our findings highlight that different complexity metrics
emphasize different aspects of economic development.
Because of this, our emphasis differs significantly from
the bulk of discussions surrounding complexity metrics,
which have focused on identifying the correct way to infer
‘complexity’18–30 from data. Our results neither directly
support nor contradict the interpretation of complexity
metrics as inference methods. Our difference in emphasis
partly reflects our strategy, which diverges fundamentally
from prior work. Most work on complexity metrics develops
heuristic arguments for using metrics with particular
functional forms, but our paper shows how such metrics
can be directly derived from an underlying economic
model.

Πvµ = αwµ (10)

where α is a constant that depends on the normalization of
the eigenvectors.
Proof: By definition the right eigenvectors of Φ˜ satisfy
Φ˜vµ = λµvµ, which can be rearranged as

−1/2ΦD

−1/2

)(D

(D

vµ) = λµ(D

vµ).

The vector D
1/2vµ is thus a right eigenvector of the symmetric
matrix Q ≡ D
−1/2ΦD
−1/2 = D
1/2Φ˜D
−1/2
. Similarly, the left
eigenvectors of Φ˜ satisfy w†
µΦ˜ = λµw†
µ, which can rearranged
as

−1/2

−1/2ΦD

−1/2

−1/2
),

(w
†
µD

)(D

) = λµ(w

†
µD

Recent work has harnessed new ways of thinking
and new analytical methods to study economic development.
Many avenues for further study remain. We
explored our results in the setting of country exports,
but similar analyses could be carried out in networks of
occupations57, industries16,58,59, technology classes60, research
publications5
, or in networks of related locations61
,
where the roles of locations and activities could be reversed
by projecting the bipartite network of locations
and activities onto location nodes instead of activities.
Complexity metrics have been justified in part by their
empirical connection to economic growth, though our
results suggest these connections may have less to do
with complexity per se than with long-term development
processes more generally that shape the trajectory of
structural change. All told, our results call for further
investigations to improve the dynamical description of
structural change62. We suggest an approach like the
one here can be a step toward models that describe these
processes with ever-greater fidelity, while being closely
tied with empirical metrics, helping shed light on the
determinants of growth and development.

showing that D
−1/2wµ is a left eigenvector of the same matrix
Q. Finally, since Q is symmetric, any right eigenvector is also
a left eigenvector, and thus

D

vµ = αD−1/2wµ

for some constant α. We therefore have Dvµ = αwµ. In
particular, the first left and right eigenvectors of Φ˜ are v1 ∝ 1
and w1 ∝ π, and so we have D1 ∝ π. Since D is diagonal,
in index form this reads Dpp ∝ πp, i.e. D is a matrix that is
proportional to Π, giving us Eq. (10).

Normalization of eigenvectors. Our convention for normalizing
eigenvectors helps determine the numerical scales
of the A and b coordinates (and in principle other coordinate
projections). In general left and right eigenvectors are
biorthogonal, obeying WT V = Ψ for some diagonal matrix
Ψ. It simplifies many calculations to require that Ψ = I so
that left and right eigenvectors obey

w
†
νvµ = δνµ. (11)

This condition does not determine a normalization for the wµ
and vµ eigenvectors, since these can be rescaled as vµ → cvµ
and wµ → 1
c wµ while preserving Eq. (11). However, we can
pin down a normalization for the eigenvectors by requiring
that they also satisfy Eq. (10) with proportionality constant

α = 1. One way to accomplish this is to normalize left
eigenvectors such that the weighted 2-norm

Review of conventional PCI and ECI To aids our discussion
of the PCI* and ECI* next we review the calculations
that generate the conventional PCI and ECI. The PCI and
the ECI were proposed by Hidalgo and Hausmann (2009)18
,
and can be computed with an eigenvector computation as
noted by Caldarelli et al. (2012)51,52. Let nc be the number
of countries and np the number of products. Let R be the
nc × np matrix R of RCAs, and let M be a binarized version
of this matrix, with elements Mcp = 1 wherever Rcp ≥ 1 and
0 otherwise. M may be viewed as an adjacency matrix for a
bipartite network connecting countries to products that they
export at a significant ability level. Define the diversity of
country c’s activity basket as the cth row sum of this matrix,
denoted as dc ≡
P
p Mcp. Similarly, define the ubiquity of
activity p as the pth column sum, denoted as up ≡
P
c Mcp.
Let D and U be the diagonal matrices formed from countries’
diversities and products’ ubiquities, respectively. One may
use the products of D
−1M and U
−1MT
, in different orders,

||w|| ≡ √

wT Π−1w (12)

is 1 for each left eigenvector, and to normalize right eigenvectors
such that the weighted 2-norm

||v|| ≡ √

vT Πv (13)

is 1 for each right eigenvector. In addition to satisfying Eq.
(10) with α = 1, this normalization convention has the nice
side effect that the first right eigenvector v1 = 1 is a vector
of 1s, and the elements of the first left eigenvector w1 = π
sum to 1.3

The A coordinate. The A(t) factor in Eq. (4) can be
understood as a weighted average of elements of R(t). To
see this, first consider the simpler model R(t) = P(t)R(0) in
which A(t) is fixed at 1. Left-multiplying this model by the
first left eigenvector w1 = π, and exploiting the fact that π is
the stationary state of the matrix P(t) = e
−LΦ(t/τ)
, we have

to define two square matrices that eliminate either the country
nodes or the product nodes from the bipartite network.
Multiplying these matrices in one order collapses the country
dimension, leading to the np × np row-normalized stochastic
matrix

R¯(t) = π

T R(0) = R¯(0). (15)

T R(t) = π

The left and right sides are weighted averages of elements of
R with weights given by the elements of π. This calculation
shows that this particular average is unaffected by the multiplication
of R(0) by P(t), a well-known aspect of consensus
dynamics models, which R(t) = P(t)R(0) is an instance of:
The dynamics preserves the average value R¯(0) = π
T R(0) of
the initial condition R(0) (e.g.45).

P ≡ U
−1
(MT D

−1M). (18)

The second right eigenvector of P defines the unstandardized
PCIs, PCI. Similarly, collapsing the product dimension leads
to the nc × nc row-normalized stochastic matrix

C ≡ D
−1
(MU −1MT

). (19)

Next, allowing A(t) to vary in Eq. (4), it is clear that
the average of the elements of R will change by whatever
factor A(t) changes. Left-multiplying Eq. (4) by π, after
rearrangement we have

The second right eigenvector of C defines the unstandardized
ECIs, ECI. Often the PCIs and ECIs are standardized to have
zero mean and unit variance across products or countries63
,
but here we work with the unstandardized vectors, and indeed
our theory implies that standardizing removes information
(see Supplementary Note S6).

A(t) = π
T R(t)
πT R(0) =
R¯(t)
R¯(0), (16)

showing that A(t) is the factor by which the average of R
has changed from time 0 to time t. The time t = 0 is just a
reference period, with no special significance, and R¯(0) is just
a reference value. Taking this value to be 1 we have simply

The eigenvector v2 (PCI*). The second eigenvector of
the Laplacian matrix of the dynamical model, v2, is of special
interest because it captures the pattern of compositional
change with the longest time scale. Activities that take an
especially long time to shift out of have negative elements in
this eigenvector, and activities that take an especially long
time to reach have positive elements. This mode of change
represents a shift in emphasis from some activities to others, as
determined by the signs of elements of the second eigenvector
v2, thus giving this vector a meaning as a pattern of economic
transformation. We now discuss further how the elements of
v2 are closely related to the complexity metrics known as the
Product Complexity Indices. To highlight its relation to the
PCIs, we refer to this eigenvector as PCI∗
:

T R(t) = R¯(t). (17)

A(t) = π

The same result can also be obtained from the eigen-expansion
Eq. (5). Left-multiplying by w1 = π1, and exploiting
the biorthogonality of left and right eigenvectors, we have
π
T R(t) = A(t)c1(0)π
T 1 = A(t)c1(0), where π
T 1 = 1 because
the elements of π sum to 1. The c1(0) coefficient plays
a redundant role with A(t); setting it to 1 leaves us with Eq.
(17).

PCI∗ ≡ v2. (20)

3 We note in passing that Eqs. (12) and (13) are dual norms. If
||v|| is a norm for vector v, the dual norm of w is the least
upper bound of wT v for all v such that ||v|| ≤ 1. To see
that these are dual norms, recall the Cauchy-Schwarz inequality
|a
T b| ≤ ||a||2||b||2. Making the replacements a = Π−1/2w and
b = Π1/2v lets us write this in terms of the norms Eqs. (12)-(13):

To see that elements of v2 are related to PCIs, first note
that the eigenvectors of our dynamical model depend on
how we construct the matrix of proximities between activities.
Prior work has generated a variety of proximity matrices, each
finding empirical support when used to forecast transitions in
economic activities. It is not clear what proximity measure
describes the network of transitions best, and our goal here
is not to resolve this. Instead, we show that the structure
of the second eigenvector is not sensitive to this choice, and
that across a variety of empirically-supported measures of

1/2v||2 =
√
wT Π−1w
√

|wT v| ≤ ||Π

−1/2w||2 ||Π

vT Πv = ||w|| ||v||.
(14)

As |wT v| reaches its largest value when ||v|| = 1, the least upper
bound of |wT v| is √
wT Π−1w, which is Eq. (12).

proximity (Fig. 7), the second eigenvectors are quite similar
to one another, and to the vector of the conventional PCIs.
First, there is a particular choice of proximity matrix for
which v2 = PCI∗
and the vector of conventional PCIs, PCI,
are identical up to an irrelevant factor. This happens when
the proximities are taken to be

Next we use three results to express the b coordinate in a
different form. First, in the denominator, we use the fact that
the first left eigenvector equals π, wp1 = πp. Second, in the
numerator, we use the relationship derived earlier between
left and right eigenvectors (Eq. (10)), wp2 = πpvp2. These
changes yield

bc(t) =
P
p Rcp(t)πpvp2
P
p Rcp(t)πp

McpMcp0
Dc

Φ
P
pp0 ≡
X
c

, (21)

. (27)

or in matrix form ΦP = MT D
−1M. If the proximities used
in the dynamical model are given by Φ = ΦP
, then PCI∗
and
PCI will be the second eigenvectors of the same eigenvector
equation. To see this, note that PCI∗
is by definition an
eigenvector of LΦ = I − Φ˜, and consequently an eigenvector
of Φ˜. Finally, Φ˜ ≡ Diag(Φ1)
−1Φ equals the matrix P, whose
second eigenvector defines the conventional PCIs:

Finally, we insert the definition of PCI*, PCI∗
p ≡ vp2. The
resulting expression has a structure that closely resembles
that of Eq. (8): Taking ECI∗
c (t) ≡ bc(t), we have

P
Rcp(t)πp
p0 Rcp0 (t)πp0

!
PCI∗
p. (28)

ECI∗
c (t) = X
p

Like the conventional ECI, Eq. (8), the ECI* is an average of
PCI*s. The conventional ECI uses uniform weights for all of
the nonzero elements in the binarized matrix M. The ECI*,
in contrast, uses non-uniform weights based on the elements
of the unbinarized matrix R, and adjusted by the ergodic
probabilities π. (See SI Note S7 for an interpretation and
potential benefits of these weights.)

Φ˜ ≡ Diag(ΦP
1)
−1Φ
P

= Diag(MT D
−1M1)
−1MT D
−1M
= Diag(MT D
−1d)
−1MT D
−1M
= Diag(MT
1)
−1MT D
−1M

= Diag(u)
−1MT D
−1M

We tie the definition of PCI* and ECI* to the Laplacian
LΦ that governs the dynamics in our diversification model.
This Laplacian could be constructed using different practical
measures of proximity, such as ΦP
(Eq. (21)), for example,
or ΦM
pp0 ≡ min{(MTMU −1
)pp0 ,(U
−1MTM)pp0}, the proximity
matrix introduced in Ref.15 to define the Product Space.
These different proximity measures represent different guesses
for how to infer underlying relationships between products,
and the propensity for particular product transitions to take
place. Proximity measures yielding better predictions of these
transitions could therefore, in principle, produce better calculations
of PCI∗
and ECI* that are more informative of
countries’ development pathways, offering a path for refinement
of these quantities.

= U
−1MT D
−1M

= P. (22)

Further, a close numerical relation between PCI∗
and
PCI carries over beyond this special case; see “Comparing
PCI*/PCI and ECI*/ECI across proximity measures” and
Fig. 7 below.

The b coordinate (ECI*). The b coordinate is associated
with the projection of a country’s ability vector onto the
second eigenvector v2. This coordinate can be written in
the form of Eq. (9), showing that it closely resembles the
conventional ECI. To derive this expression, first note that the
coefficients of the eigen-expansion can be obtained by exploiting
the biorthogonality of the left eigenvectors wµ with the
right eigenvectors vµ. Left-multiplying R(t) = P
µ
cµ(t)vµ
by w†
µ, we have cµ(t) = w†
µR(t). Examining Eq. (5), the first
coefficient satisfies (since we have set c1(0) to 1)

Description of data. We use cleaned UN Comtrade data37
publicly available at Harvard Dataverse64. Trade data are
reported twice: once as exports by the exporting country and
once as imports by the importing country. The data cleaning
corrects trade flows to increase the consistency between
importer and exporter records of the same flow, and further
corrects reported values using an index of reliability based
on the consistency of reported values over time. The data
provides total export volumes of products for 249 countries
over the period 1962 - 2018 (11,544 export baskets observed
across all regions and years). We analyze these data at the
3-digit SITC product level (235 product categories).

A(t) = c1(t) = w
†
1R(t), (23)

and the second coefficient satisfies

†
2R(t). (24)

A(t)b(t) = c2(t) = w

It follows that the coordinate b(t) is the ratio of these coefficients:b(t)
= c2(t)
c1(t)
=
w
†
2R(t)
w
†
1R(t)

Calculation of relatedness network and eigenvectors.
To obtain our results for country evolution in Fig. 3 we
first compute a matrix of relatedness between products using
Eq. (21). We fix Φ in the initial year of our data (1962) in
accordance with the idea, inherent in the PoR, that economies
diversify across a fixed (or at least slow-moving) space of
related activities. From Φ we compute the row-normalized
version of this matrix Φ˜
pp0 = Φpp0/
P
p00 Φpp00 as described
in the text, whose right (vµ) and left (wµ) eigenvectors are
the basis for the remainder of the analysis. We normalize
these eigenvectors with the weighted L2-norms Eqs. (12)-
(13), though this choice of norms is just a convention and is
not consequential, as different choices will simply rescale the
coordinates projected onto the eigenvectors.

. (25)

The coordinate b(t) and the activity basket R(t) vary across
countries. We now account for this in our notation, which
will help us compare b(t) to the ECI. Let bc be the coordinate
associated with country c, and we now expand the vector R
into the nc × np matrix of abilities R = [Rcp] across countries
and products. In index form, bc(t) is then

bc(t) = [R(t)w2]c
[R(t)w1]c

=
P
p Rcp(t)wp2
P
p Rcp(t)wp1

. (26)

a

and time t the RCA vector Rc(t) on this transformed scale
and use these vectors to compute the A and b coordinates.
The A coordinate for country c and time t is computed as
Ac(t) = π
T Rc(t), where π = w1 is the first left eigenvector.
The b coordinate is computed as bc(t) = wT
2 Rc(t)/wT
1 Rc(t),
which is equivalent to Eq. (9).

0 0.5 1 1.5 2 2.5
Bin count
R0
 = 0.001
0 2 4 6
R0
 = 0.115

Transformation of RCAs. As noted above, we transform
raw RCAs with the function g(R
) = log(1 + R
/R0)/ log(1 +
1/R0). The parameter R0 sets the transition between the
linear and log regimes of the transformation, and modulates
the expression of extreme values. High values of R0 allow
large RCAs more expression, while low values of R0 suppress
them (Fig. 6a). A given value of R0 leads to a given activity
vector R(t; R0) and a normalized activity vector r(t; R0) ≡
R(t; R0)/A(t), which has the following representation in the
eigenvector basis:

0 5 10 15
Transformed RCA g(R)
Bin count
R0
 = 1
0 500 1000 1500 2000 2500
Transformed RCA g(R)
R0
 = 1000

r(t; R0) = X
µ

X

bµ(t; R0)vµ = 1 +

bµ(t; R0)vµ. (29)

b

µ≥2

We choose R0 to maximize the variance explained across
countries and time by the directional vector v2 = PCI∗
,
or equivalently, the variance explained by the coordinate
b2(t; R0) = b(t) = ECI∗
(t). Our procedure is related to principal
component analysis. The difference is that a PCA uncovers
a set of variance-maximizing directions in data, while here,
the directions are given to us beforehand (the eigenvectors of
the Laplacian LΦ). Otherwise, we still ask how much variance
is explained by data along the particular direction v2 = PCI∗
for different values of R0 and, like PCA, select a value that
maximizes data variability described by this direction.
Let ri be an observation of a normalized activity basket, and
let X = [ri] be the np × N data matrix of these observations
across countries and years i ∈ 1 . . . N. The eigendecomposition
Eq. (29) corresponds to the matrix factorization

FIG. 6. a Distribution of transformed RCAs g(R
) for different
values of R0. Small values of R0 weaken the expression of
the largest RCAs; large values of R0 do the opposite. (To
make the transformation easier to interpret, we divide the
transformation function g(R
) by the constant log (1 + 1/R0)
so that a raw RCA R
0 = 1 consistently maps to a transformed

X(R0) = V B(R0), (30)

where V is the np × np matrix whose columns are LΦ’s right
eigenvectors vµ and B is the np ×N matrix whose ith column
gives the coordinates of the ith observation in the eigenvector
basis. The variances and covariances of the data in the
directions of each vector in V can be computed as follows.
Let Xc = XΘ be the centered (i.e. de-meaned) data where
Θ ≡ IN −
N
1N 1
T
N is a centering matrix. The data covariance
matrix is

RCA R = 1 for all values of R0.) b Ratio of variance described
by variation in the ECI* (Eq. (34)) to total data variability.

Calculation of ability vectors R and (A, b) coordinates.
For each country c, product p, and year we computed the
Balassa index of revealed comparative advantage (RCA)
R
cp = (Xcp/
P
p0 Xcp0 )/(
P
c
0 Xc
0p/
P
c
,p0 Xc
0p0 ) where Xcp
is the value of c’s exports in product p. RCAs are heavy
tailed and are commonly transformed to weaken the effect
of extreme values (e.g.16,35,46,47). Here, we transform them
using the function R = g(R
) = α log(1 + R
/R0). The
constant α = [log(1 + 1/R0)]−1
is included for convenience so

C(R0) = 1
N

T

Xc(R0)Xc(R0)

=
N

X(R0)ΘΘT X(R0)

T

=
N

V B(R0)ΘΘT B(R0)

T
V
T

=
N

T
V
T

V Bc(R0)Bc(R0)

that an RCA of 1 is mapped to 1 on the transformed scale.
This function behaves linearly for small values of R
and
logarithmically for large values, and thus achieves the goal of
weakening the effect of very large RCAs while also handling
RCAs that are identically zero (i.e. which occurs in the
many instances where a country has no exports of a product).
The parameter R0 (which sets the transition between the
linear and logarithmic regimes) is tuned to maximize the
amount of variance in export baskets that the b coordinate
explains across time and countries, as we discuss in the next
section. Our results can be reproduced using our obtained
value R0 = 0.115. We then calculate for each country c

= V C˜(R0)V
T

, (31)

where Bc = BΘ is the matrix of centered data coordinates
in the V basis. The matrix C˜ =
N BcB
T
c is the covariance
matrix of the data in the coordinate system given by the
eigenvectors of the dynamical model.4

4 As further comparison with PCA, recall that in PCA the data is

a

P

b

M c

C

1.5
1.0
0.5
0.0
0.5
1.0
1.5
2.0

Pearson:0.947
Spearman:0.950

Pearson:1.000
Spearman:1.000

Pearson:0.872
Spearman:0.916

1.0

0.10 0.05 0.00 0.05 0.10
PCI
2.0
1.5
1.0
0.5
0.0
0.5
1.0
1.5

0.0

-1.0

PCI*

PCI*

PCI*

-2.0

-3.0

-4.0

0.10 0.05 0.00 0.05 0.10
PCI

0.10 0.05 0.00 0.05 0.10
PCI

d e f

FIG. 7. Comparison of PCI* with PCI (a-c) and ECI* with ECI (d-f) for the proximity matrices ΦP

, ΦM, and ΦC .

Let W be the np × np matrix whose columns are LΦ’s left
eigenvectors wµ. Exploiting the biorthogonality of left and
right eigenvectors W†V = I, Eq. (31) can be solved for C˜
(the covariances in the V basis) as

Thus, the data variance in the direction v2 = PCI∗
can be
written as a weighted sum of the variances of the principal
components, with each principal component weighted by its
projection (ˆwT
2 za(R0)) onto v2 in the non-orthogonal basis
V . We score the variance that the coordinate b = ECI∗
explains using the ratio of Eq.
P
(34) to the total data variability
a
σ
a(R0). We calculate this ratio for various values of R0,
finding a peak near R0 = 0.115 (Fig 6b).

C˜(R0) = W†C(R0)W. (32)

In particular, the variance of activity baskets in the direction
v2 = PCI∗
is

Comparing PCI*/PCI and ECI*/ECI across proximity
measures. To see whether the PCI* and ECI* not only
resemble the conventional PCI and ECI theoretically, but also
numerically, we compute these quantities with our data and
directly compare them. The PCI* is defined by the second
eigenvector v2 of the Laplacian matrix LΦ and, in general,
this and other eigenvectors of our model will vary depending
on exactly how the proximity matrix Φ between activities is
constructed. This matrix has been implemented in a variety
of ways that all find empirical support. Here, we show that
the general structure of the second eigenvector is not sensitive
to this choice, and that it resembles the vector of conventional
PCIs across a range of proximity matrices. We similarly show
that the ECI* numerically resembles the conventional ECI,
which is plausible because the ECI* depends on the PCI*.
We consider three proximity matrices. The first is ΦP
(Eq.
(21)). We also consider the minimum conditional probabilitybased15
proximity measure ΦM noted in the main text:

; R0) = C˜22(R0)

Var(ECI∗

= w
T
2 C(R0)w2. (33)

The left eigenvectors were normalized with the modified 2-
norm Eq. (12), while principal components are typically
normalized with a standard 2-norm. To remove the scale effect
this creates we factor out the standard 2-norm from the left
eigenvectors, computing the variance with ˆw2 ≡ w2/||w2||2:

; R0) = ˆw
T
2 C(R0)ˆw2. (34)

Var(ECI d ∗

For intuition, we could write Var d(ECI∗
; R0) in terms of the
variances explained by principal components. Let Z be the
np × np matrix whose columns are principal components.
Inserting I = ZZT
above leads to

ˆw
T
2 za(R0)
σ
a(R0). (35)

; R0) = X
a

Var(ECI d ∗

Φ
M
pp0 ≡ min{(MTMU −1

−1MTM)pp0}. (36)

)pp0 ,(U

We also consider a correlation-based proximity measure16 Φ
C ,

expressed in a basis V that diagonalizes the covariance matrix.
In such a basis C˜ would be diagonal. Here, we are expressing
the data in a pre-determined basis given by the eigenvectors of
LΦ, and C˜ will have non-zero off-diagonal elements (non-zero
covariances in the new coordinates).

Φ
C
pp0 ≡

(1 + ρpp0 ), (37)

where ρpp0 is the Pearson correlation of the RCAs for products
p and p
across locations c. Fig. 7 compares PCI*s to PCIs

and ECI*s to ECIs for each proximity matrix. Pearson and
Spearman correlations are shown for each comparison, all
with high values between 0.83 and 1. Panels (a) and (d) show
the comparison in the special case Φ = ΦP discussed above.
As noted already, when proximities are constructed using Eq.
(21), PCI∗
is equal to PCI up to a constant overall factor.
Fig. 7d is the comparison of ECI* with ECI in this case, and
displays the same results as Fig. 4. While the PCI∗
and PCI
coincide in one special case (Φ = ΦP
), the same is never true
of the ECI* and ECI. Differences between these quantities
will always remain because of the different averaging weights
used in Eqs. (8) and (9). In the closest approach, where
Φ = ΦP
, the Pearson correlation between the ECI* and the
ECI is 0.919, and the Spearman rank correlation is 0.902 (Fig.
4). In SI Note S6 we discuss why the weights used to calculate
ECI* may have certain desirable properties.

than on arguments about how best to infer complexity.

ACKNOWLEDGEMENTS

We thank Ulrich Schetter, R. Maria del Rio Chanona, Ricardo
Hausmann, Vito Servedio, Fran¸cois Lafond, Muhammed
Yildirim, Stefan Thurner, Doyne Farmer, and three anonymous
referees for valuable feedback. Frank Neffke acknowledges
financial support from the Austrian Research Agency
(FFG), project #873927 (ESSENCSE).

DATA AVAILABILITY

The datasets analyzed during the current study
are available in the Harvard Dataverse, https:
//dataverse.harvard.edu/dataset.xhtml?persistentId=
doi:10.7910/DVN/H8SFD2&version=4.0

Although the closest approach of the b(t) coordinate to the
conventional ECI occurs when the proximity matrix is taken
to be ΦP
, we note that there is no inherent reason in the
dynamical modeling approach presented here to assume this
particular proximity matrix. Proximities between activities
could be quantified with other existing matrices, or entirely
new ones to be developed, and could be selected based on the
quality of forecasts of future transitions in activities, rather

CODE AVAILABILITY

The code used for the study is available at https://github.
com/complexly/por-structuralchange.

[1] Hausmann, R., Hwang, J. & Rodrik, D. What you export
matters. J. Econ. Growth 12, 1–25 (2007).
[2] Porter, M. The economic performance of regions. Regional
Studies 37, 549–578 (2003).

geography 89, 29–51 (2013).
[12] Essletzbichler, J. Relatedness, industrial branching and
technological cohesion in US metropolitan areas. Regional
Studies 49, 752–766 (2015).

[3] Delgado, M., Porter, M. E. & Stern, S. Clusters, convergence,
and economic performance. Research Policy 43,
1785–1799 (2014).

[13] Zhu, S., He, C. & Zhou, Y. How to jump further and
catch up? Path-breaking in an uneven industry space.
Journal of Economic Geography 17, 521–545 (2017).
[14] Hausmann, R. & Klinger, B. The structure of the product
space and the evolution of comparative advantage. CID
Working Paper Series (2007).

[4] Gathmann, C. & Sch¨onberg, U. How general is human
capital? a task-based approach. Journal of Labor Economics
28, 1–49 (2010).

[5] Guevara, M. R., Hartmann, D., Aristar´an, M., Mendoza,
M. & Hidalgo, C. A. The research space: using career
paths to predict the evolution of the research output
of individuals, institutions, and nations. Scientometrics
109, 1695–1709 (2016).

[15] Hidalgo, C. A., Klinger, B., Barab´asi, A.-L. & Hausmann,
R. The product space conditions the development of
nations. Science 317 (2007).

[16] Hausmann, R., Stock, D. P. & Yıldırım, M. A. Implied
comparative advantage. Research Policy 104143 (2021).
[17] Hidalgo, C. A. et al. The principle of relatedness. In
International conference on complex systems, 451–457
(Springer, 2018).

[6] Farjoun, M. Beyond industry boundaries: Human expertise,
diversification and resource-related industry groups.
Organization Science 5, 185–199 (1994).
[7] Lien, L. B. & Klein, P. G. Using competition to measure
relatedness. Journal of Management 35, 1078–1107
(2009).

[18] Hidalgo, C. A. & Hausmann, R. The building blocks
of economic complexity. Proceedings of the National
Academy of Sciences 106, 10570 – 10575 (2009).
[19] Tacchella, A., Cristelli, M., Caldarelli, G., Gabrielli, A.
& Pietronero, L. A new metrics for countries’ fitness and
products’ complexity. Scientific Reports 2, 1–7 (2012).
[20] Kemp-Benedict, E. An interpretation and critique of the
method of reflections. Munich Personal RePEc Archive
(MPRA) (2014).

[8] Neffke, F. & Henning, M. Skill relatedness and firm
diversification. Strategic Management Journal 34, 297–
316 (2013).

[9] Neffke, F., Henning, M. & Boschma, R. How do regions
diversify over time? Industry relatedness and the development
of new growth paths in regions. Economic
Geography 87 (2011).

[21] Mariani, M. S., Vidmer, A., Medo, M. & Zhang, Y.-
C. Measuring economic complexity of countries and
products: which metric to use? The European Physical
Journal B 88, 1–9 (2015).

[10] Boschma, R., Minondo, A. & Navarro, M. Related variety
and regional growth in Spain. Papers in Regional Science
91 (2012).

[11] Boschma, R., Minondo, A. & Navarro, M. The emergence
of new industries at the regional level in Spain: A proximity
approach based on product relatedness. Economic

[22] Morrison, G. et al. On economic complexity and the
fitness of nations. Scientific Reports 7, 1–11 (2017).

[23] Servedio, V. D., Butt`a, P., Mazzilli, D., Tacchella, A. &
Pietronero, L. A new and stable estimation method of
country economic fitness and product complexity. Entropy
20, 783 (2018).

technological knowledge in us metropolitan areas from
1981 to 2010. Industrial and Corporate Change 24, 223–
250 (2015).

[43] Petralia, S., Balland, P.-A. & Morrison, A. Climbing the
ladder of technological development. Research Policy 46,
956–969 (2017).

[24] Teza, G., Caraglio, M. & Stella, A. L. Growth dynamics
and complexity of national economies in the global trade
network. Scientific reports 8, 1–8 (2018).
[25] Schetter, U. A structural ranking of economic complexity.
CID Research Fellow & Graduate Student Working Paper
(2019).

[44] Newman, M. E. J. Networks: An Introduction (Oxford
University Press, 2010).

[45] Schaub, M. T., Delvenne, J.-C., Lambiotte, R. & Barahona,
M. Structured networks and coarse-grained descriptions:
A dynamical perspective. Advances in Network
Clustering and Blockmodeling 333–361 (2019).
[46] Hoen, A. R. & Oosterhaven, J. On the measurement of
comparative advantage. The Annals of Regional Science
40, 677–691 (2006).

[26] Bustos, S. & Yıldırım, M. A. Production ability and
economic growth. Research Policy 104153 (2020).
[27] Sciarra, C., Chiarotti, G., Ridolfi, L. & Laio, F. Reconciling
contrasting views on economic complexity. Nature
Communications 11, 1–10 (2020).

[28] Ivanova, I., Smorodinskaya, N. & Leydesdorff, L. On
measuring complexity in a post-industrial economy: The
ecosystem’s approach. Quality & Quantity 54, 197–212
(2020).

[47] Elekes, Z., Boschma, R. & Lengyel, B. Foreign-owned
firms as agents of structural change in regions. Regional
Studies 53, 1603–1613 (2019).

[48] United Nations. Un list of least developed
countries. URL https://unctad.org/topic/
least-developed-countries/list.

[29] Teza, G., Caraglio, M. & Stella, A. L. Entropic measure
unveils country competitiveness and product specialization
in the world trade web. Scientific reports 11, 1–11
(2021).

[49] Hines Jr, J. R. Treasure islands. Journal of Economic
Perspectives 24, 103–26 (2010).

[30] Gomez-Lievano, A. & Patterson-Lomba, O. Estimating
the drivers of urban economic complexity and their connection
to economic performance. Royal Society open
science 8, 210670 (2021).

[50] The World Bank. World Bank Development Indicators
(2018). URL http://data.worldbank.org/.
[51] Caldarelli, G. et al. A network analysis of countries’
export flows: Firm grounds for the building blocks of the
economy. PloS one 7, e47278 (2012).

[31] Imbs, J. & Wacziarg, R. Stages of diversification. American
Economic Review 93, 63–86 (2003).
[32] Cadot, O., Carr`ere, C. & Strauss-Kahn, V. Export
diversification: What’s behind the hump? Review of
Economics and Statistics 93, 590–605 (2011).
[33] Clark, C. The conditions of economic progress. (London:
Oxford, 1967).

[52] Cristelli, M., Gabrielli, A., Tacchella, A., Caldarelli, G.
& Pietronero, L. Measuring the intangibles: A metrics
for the economic complexity of countries and products.
PloS one 8, e70726 (2013).

[53] Mealy, P., Farmer, J. D. & Teytelboym, A. Interpreting
economic complexity. Science Advances 5, eaau1705
(2019).

[34] Kuznets, S. Quantitative aspects of the economic growth
of nations: II. Industrial distribution of national product
and labor force. Econ. Dev. Cult. Change 5, 1–111 (1957).
[35] Brummitt, C. D., G´omez-Li´evano, A., Hausmann, R. &
Bonds, M. H. Machine-learned patterns suggest that
diversification drives economic development. Journal of
the Royal Society Interface 17, 20190283 (2020).
[36] Balland, P.-A. et al. Reprint of the new paradigm
of economic complexity. Research Policy 51,
104568 (2022). URL https://www.sciencedirect.com/
science/article/pii/S0048733322000919. Special Issue
on Economic Complexity.

[54] Hill, M. O. Reciprocal averaging: An eigenvector method
of ordination. The Journal of Ecology 237–249 (1973).
[55] Ross, M. L. What have we learned about the resource
curse? Annual review of political science 18, 239–259
(2015).

[56] Simon, H. A. & Ando, A. Aggregation of variables in
dynamic systems. Econometrica: Journal of the Econometric
Society 111–138 (1961).

[57] Muneepeerakul, R., Lobo, J., Shutters, S. T., Gom´ezLi´evano,
A. & Qubbaj, M. R. Urban economies and
occupation space: Can they get “there” from “here”?
PloS one 8, e73676 (2013).

[37] United Nations. UN Comtrade International Trade Statistics
Database. URL https://comtrade.un.org/.
[38] van Dam, A., Gomez-Lievano, A., Neffke, F. & Frenken,
K. An information-theoretic approach to the analysis of
location and colocation patterns. Journal of Regional
Science 63, 173–213 (2023).

[58] Neffke, F., Henning, M. & Boschma, R. How do regions
diversify over time? industry relatedness and the development
of new growth paths in regions. Economic
geography 87, 237–265 (2011).

[59] O’Clery, N., Curiel, R. P. & Lora, E. Commuting times
and the mobilisation of skills in emergent cities. Applied
Network Science 4, 1–27 (2019).

[39] Balassa, B. Trade liberalisation and “revealed” comparative
advantage 1. The Manchester School 33, 99–123
(1965).

[60] Kogler, D. F., Rigby, D. L. & Tucker, I. Mapping knowledge
space and technological relatedness in us cities. European
Planning Studies 21, 1374–1391 (2013).
[61] Bahar, D., Hausmann, R. & Hidalgo, C. A. Neighbors and
the evolution of the comparative advantage of nations:
Evidence of international knowledge diffusion? Journal
of International Economics 92, 111–123 (2014).
[62] Coniglio, N. D., Lagravinese, R., Vurchio, D. & Armenise,
M. The pattern of structural change: testing the product
space framework. Industrial and Corporate Change 27,
763–785 (2018).

[40] Hillman, A. L. Observations on the relation between
“revealed comparative advantage” and comparative advantage
as indicated by pre-trade relative prices. Review
of World Economics 116, 315–321 (1980).
[41] Hinloopen, J. & van Marrewijk, C. Empirical relevance
of the hillman condition for revealed comparative advantage:
10 stylized facts. Applied Economics 40, 2313–2328
(2008).

[42] Boschma, R., Balland, P.-A. & Kogler, D. F. Relatedness
and technological change in cities: The rise and fall of

[63] Hausmann, R., Hidalgo, C. A., Bustos, S., Coscia, M. &
Simoes, A. The atlas of economic complexity: Mapping
paths to prosperity (MIT Press, 2014).
[64] The Growth Lab at Harvard University. International
trade data (SITC, Rev. 2) v4.0 (2019). URL

https://dataverse.harvard.edu/dataset.xhtml?
persistentId=doi:10.7910/DVN/H8SFD2&version=4.0.
Bridging the short-term and long-term dynamics of economic structural change
(Supplementary Information)
James McNerney, Yang Li, Andr´es G´omez-Li´evano, Frank Neffke

arXiv:2110.09673v2 [physics.soc-ph] 24 Mar 2023

S1 Supplementary note: Cancellation of imaginary components in complex conjugate pairs 2
S2 Supplementary note: Individual country trajectories 2
S3 Supplementary note: Higher-order eigenvectors and eigenvalues 3
S4 Supplementary note: Correlations of coordinates with complexity metrics 4
S5 Supplementary note: Dimensionality reduction 6
S6 Supplementary note: Benefits of seeing complexity metrics as coordinates of structural

change 7
S7 Supplementary note: On the ECI* weights when Φ = ΦP 8

S1 Supplementary note: Cancellation of imaginary components
in complex conjugate pairs

Typically the matrix Φ that maps the relatedness of different economic activities is constructed to be
symmetric, which results in eigenvalues and eigenvectors of LΦ that are real-valued. However, a symmetric Φ
is not a requirement of our dynamical theory; here we discuss how complex eigenvalues and eigenvectors can
be handled without any special difficulties in interpreting the eigenmodes. The eigenvalues and eigenvectors
of real matrices occur in complex conjugate pairs and real-valued modes can be constructed with a standard
trick by combining both components of the pair. As noted in the main text, the projection of region c onto
the µth eigenmode is given by cµ(t) = w†
µR(t). If the elements of wµ = aµ + ibµ contain imaginary parts,
then it has a paired eigenvector wµ0 = w∗
µ = aµ − ibµ, and wherever this is the case one may combine the
eigenvectors and consider the coefficients in pairs, i.e.

†
µ0R(t) = w†µ
+ (w†
µ
)
∗

cµ(t) + cµ0 (t) = w†
µR(t) + w

R(t) (S1)

for which the summed vector w†
µ+(w†
µ
)
∗
(and therefore the combined projection onto both modes, cµ(t)+cµ0 (t))
is manifestly real.

S2 Supplementary note: Individual country trajectories

End point in:

Region 1

Region 3

Angola

Albania

Region 2

Brazil

Burundi

0.5

Egypt
Ethiopia
Indonesia

Region 2

Composition coordinate b (ECI*)

Austria

Belgium

China
Germany

Japan

Korea, Republic of
Thailand
United States

Switzerland

-0.5

Region 3

Anguilla

Bangladesh

Virgin Islands (U.S.)

-1

Region 1

0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1
Average ability coordinate A
-1.5

Figure S1: Trajectories of selected countries in the A-b phase plane. The labels Region 1, Region 2, and
Region 3 refer to the same parts of the plane as in Figure 4e of the main paper. Round markers identify the
end point of each trajectory.

Fig. S1 shows the individual trajectories of countries in our data from which the average directional
movement depicted in Fig. 3e of the main text was derived. In some parts of this plane only a few countries
have been observed, and in these sparse areas individual countries can dominate the behavior of directional
lines in Fig. 3e. An instance of this small-numbers effect is seen in Japan’s movements in Region 2.

S3 Supplementary note: Higher-order eigenvectors and eigenvaluesHere
we examine the empirical structure of the right eigenvectors and eigenvalues of Φ˜ for the three choices
of proximity matrix Φ describe in the Methods (ΦP , ΦM, and ΦC ). Higher-order eigenvectors (i.e. those
beyond the second eigenvalue) are of interest because in principle they could describe other modes of economic
transformation besides the particular diversity and compositional changes that we study in the main text.
However, we find that the proximity matrices in the literature only have strong agreement in the structure
of the first two eigenvectors, and do not straightforwardly resolve how many eigenvectors matter. We rownormalize
each proximity matrix to obtain the matrices Φ˜ P , Φ˜M, and Φ˜ C and examine the eigenvectors of the
resulting graph Laplacian LΦ (i.e. LΦ = I − Φ˜ P , LΦ = I − Φ˜M, or LΦ = I − Φ˜ C ). We put their eigenvectors
in ascending order by eigenvalue κµ, and use the eigenvectors of Φ˜ P as a reference point, computing the
correlation of the µth eigenvector of I − Φ˜ P with the µth eigenvector of LΦ = I − Φ˜M or LΦ = I − Φ˜ C
(Fig. S2a). The first eigenvectors have a correlation ρ = 1 since Φ˜ P , Φ˜M, and Φ˜ C share the same first right
eigenvector, v1 = 1. The first two eigenvectors have very high correlations, but the correlations fall off beyond
this (with a notable spike for the 4th eigenvector). We see related issues when we consider the eigenvalues
(Fig. S2b). The spectra derived from different proximity matrices differ not only in their values but also in
the number of eigenvalues that appear significantly different from others.

Resolving the structure of higher-order eigenvectors and estimating how many eigenvectors appear relevant
for long-term structural transformation means addressing the question of what the right proximity matrix is.
Future work could, for example, investigate which proximity matrices show the highest predictive ability [6].
Alternatively, one could avoid directly constructing the proximity matrix Φ and adopt an agnostic approach
such as Dynamical Mode Decomposition, which involves estimating the best-fitting linear operator that
advances a system forward in time.

a

(vP
,vC
)
(vP
,vM)

Pearson correlation
of eigenvectors

0.8

0.6

0.4

0.2

2 4 6 8 10
Eigenvector index

b

Laplacian eigenvalue

0.8

0.6

0.4

C
M
P

0.2

2 4 6 8 10
Eigenvector index

Figure S2: a Pearson correlations showing how eigenvectors of different proximity matrices become less similar
to one another as one moves to higher-order eigenvectors. The series labeled ρ(v
P , v
C ) gives correlations
between eigenvectors of Φ˜ P and Φ˜ C , and the series labeled ρ(v
P , vM) gives correlations betweens eigenvector
of Φ˜ P and Φ˜M. b Variation of the first 10 eigenvalues of the graph Laplacian LΦ for the proximity metrics
Φ
P , ΦM, and ΦC .

S4 Supplementary note: Correlations of coordinates with complexity
metrics

Here we further discuss connections of the A and b coordinates with complexity metrics. As emphasized
in the main text, nearly all complexity metrics fall into two groups (Fig. S3) that correspond to the two
coordinates A and b in our dynamical theory. The main text discusses theoretical and empirical similarities
of the A coordinate with country Fitness [7] and of the b coordinate with the ECI [8]. Two other metrics,
Production Ability [9] and the entropic measure of Teza, Caraglio, and Stella [10, 11], are also strongly
correlated with the A coordinate. A recently introduced hybrid metric known as GENEPY [12] contains
aspects of both the ECI and country Fitness. GENEPY is computed by first obtaining the two eigenvectors
with the largest eigenvalues of a country-to-country similarity matrix. Letting Xc,1 and Xc,2 denote the
elements of these eigenvectors, and letting λ1 and λ2 denote the eigenvalues, the GENEPY of country c
is GENEPYc =
P2
i=1 λiX2
c,i2
+ 2P2
i=1 λ
i X2
c,i. By design, Xc,1 is closely related to Fitness and Xc,2 is
closely related to the ECI. Sciarra et al. (2020) show that, for example, when the country-country proximity
matrix is Ncc0 ≡
P
p
McpMc0p
dcdc0 (k0
p
)
2 where k
p =
P
c Mcp/kc, then Xc,1dc = Fc, and Xc,2/
√
dc is strongly correlated
with ECIc. We find empirically that the Xc,1 and Xc,2 components underlying GENEPY also have similar
relationships to the A and b coordinates, i.e. Xc,1dc is highly correlated to A, and Xc,2/
√
dc is highly
correlated to ECI∗
. Of the metrics we examine, only collective knowhow [13] shows no similarly strong
empirical relationship to the A and b coordinates. The existence of these two groups emphasizes that, when
viewed through the analytical lens of our dynamical modeling framework, most existing complexity metrics
emphasize different aspects of the same development process: either changes in economic diversity, or a

particular pattern of compositional shifts in activities. However, as Fig. 2 in the main paper illustrated, both
aspects of change are important characteristics of economic development.

Further comments are in order regarding the GENEPY metric. Sciarra et al. highlight that GENEPY
merges information about countries from coordinates on two axes. Interestingly, we also arrived at a
representation of country development on a 2D plane, using a very different starting point for our calculations.
GENEPY is motivated by the goal of reconciling different methods for inferring complexity from data within
a consistent linear algebra and networks framework. In contrast, our 2D plane arose from our analysis of a
dynamical model based on the Principle of Relatedness. We note three differences in the resulting planes that
define each of our approaches. First, as noted already above, our A and b coordinates correspond most closely
to Xc,1dc and Xc,2/
√
dc rather than Sciarra et al.’s Xc,1 and Xc,2 themselves. Second, a fundamental input
in the method of Sciarra et al. is a country-country proximity matrix Ncc0 . The elements of the eigenvectors
of this matrix then directly give countries’ coordinates in the plane. In contrast, the fundamental input
in the framework here is a product-product proximity matrix Φpp0 . Our approach comes with a two-step
process: Eigenvectors derived from Φ first define directions of movement, and then country coordinates
are obtained from projections onto these axes. Third, Sciarra et al. interpret their coordinates in terms of
their relationship to Fitness and the ECI. Here, we exploit the fact that, by analyzing the changes in the
world economy captured by movement in the directions v1 and v2, we can give economic meaning to the
coordinates A and b (ECI*) that define our 2D plane, as capturing changes in average ability or shifts in
activity composition.

Correlations within the two groups of diversity-like and composition-like metrics were high across time
(Fig. S4a). In addition, we note that correlations across these two groups are high in early years of our data,
where regions overwhelmingly lie in a diagonal band (Fig. S4b) such that a region’s A coordinate is strongly
related to its b coordinate. We are mainly interested in correlations within each group of metrics, and do not
determine the extent to which these changes in cross-group correlations derive from aspects of our data (e.g.
new countries becoming available in our dataset over time) or from changes in the nature of development.
An exception to the high within-group correlations is X2/
√
d, which in early years is weakly correlated with
other compositional quantities. GENEPY was originally studied on data in the years 1995 - 2017, and thus
we are examining this quantity in a period well outside the one in which it was tested.

a

b

0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9

0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9

Diversity-like

Diversity-like

ECI

ECI

Composition-like

Composition-like

Figure S3: Correlations among our A and b (ECI*) coordinates, several proposed measures of complexity
(ECI, Fitness, Production Ability, the entropic measure of Teza, Caraglio, and Stella, and GENEPY), and

related quantities. a Pearson correlations. b Spearman rank correlations (identical to Fig. 5 in the main text).
The coordinate A is our average ability coordinate used throughout the text, defined using the proximity
matrix ΦP , while AM and AC refer to the same coordinate obtained from using the proximity matrices ΦM
and ΦC respectively. All quantities were computed for the year 2016 using UN Comtrade data.

a 1966

1976 1986 1996 2006 2016

Diversity-like

0.5

ECI

Composition-like

b

Composition coordinate b (ECI*)

Composition coordinate b (ECI*)

Region 2
Region 3

Region 2
Region 3

0.5

0.5

-0.5

-0.5

-1

-1

Region 1

Region 1

0 0.2 0.4 0.6 0.8 1
Average ability coordinate A
-1.5

0 0.2 0.4 0.6 0.8 1
Average ability coordinate A
-1.5

Figure S4: a Correlations over time among our A and b (ECI*) coordinates, complexity metrics, and related
quantities. b Scatter of regions in the A-b plane in 1966 and 2016.

S5 Supplementary note: Dimensionality reduction

We can relate the theory here to recent works that study the geography of economic activity and complexity
metrics through the lens of dimensionality reduction. For instance, Mealy et al. (2019) [17] point out that the
conventional ECI can be seen as a dimensionality reduction tool, equivalent to a spectral clustering algorithm
that orders countries along an axis in a way that tries to preserve the proximities between baskets of activities.
Similarly, Sciarra et al. (2020) [12] put forward a complexity index that reduces the dimensionality of
economic activity data by combining information from two eigenvectors of a country-country similarity graph.
Brummitt et al. (2020) [4], in turn, apply machine learning methods to extract dimensions that characterize
variation in historical export baskets across countries and time, finding axes that strongly correlate with
the PCIs. In the works above, dimensionality reduction involves strategies to summarize complex data.
In contrast, in exploring our dynamical model, we used the tool of eigenmode decomposition. Eigenmode
decomposition is not focused on discovering structure in data per se, but on describing a dynamical process.
Nevertheless, it is well understood that these approaches are related, and here we briefly summarize the
relationship.

First, the outcome of eigenmode decomposition is very similar to dimensionality reduction techniques:
It returns dimensions (the eigenvectors vµ) in which one can describe high-dimensional data (the matrix
of activity baskets R(t)), along with the coordinate projections of each data point onto these axes (the
coefficients cµ(t)). The two approaches differ in how directions in the vector space are determined and
interpreted. Typically, dimensionality reduction techniques aim to identify directions that capture large
amounts of variation in data, while eigenmodes characterize coherent dynamical patterns. This difference
is closely related to the distinction between proper orthogonal decomposition (POD) and dynamical mode
decomposition (DMD) in applications of machine learning to dynamical systems (e.g. [19]): Whereas POD
modes optimally reconstruct a data set of snapshots of a system over time, DMD modes identify coherent
structures in the dynamics.

The eigenmode decomposition not only generates a representation of data in a vector space, but shows
that the model predicts that countries’ activity baskets will converge to a lower-dimensional subspace that
corresponds to the modes with the largest time scales. This is a well-known outcome of the interaction
of structure and dynamics in networks [20, 1]. Heterogeneity in the time scales of different eigenmodes
leads countries’ activity baskets to collapse onto a low-dimensional subspace of possible activity baskets
as differences between countries shrink first among quickly-decaying dimensions, leaving activity baskets

3rd eigenvector v

ECI* < 0
c
 > 0

ECI* > 0
c
 > 0

2nd eigenvector v2

ECI* < 0
c
 < 0

ECI* > 0
c
 < 0

Figure S5: An illustration of the model dynamics. We display the phase portrait in the 2D plane corresponding
to the 2nd and 3rd eigenmodes in a case where τ2/τ3 = 4. Different points in the plane correspond to different
coordinate projections for an activity basket R(t) onto the 2nd and 3rd eigenvectors v2 and v3. We present
a skewed coordinate system as a reminder that these vectors in general are non-orthogonal, v2 · v3 = 0. The 6
four quadrants are labelled by whether the projection onto each eigenvector is positive or negative. Blue lines
show the paths of a country that obeys the model depending on its starting position. The model has a stable
fixed point where the projections onto both eigenvectors are zero. Because the speed of convergence is much
faster along the 3rd eigenvector, however, variation along this direction quickly shrinks, while variation along
the 2nd eigenvector is sustained for a longer time.

scattered primarily along slowly-decaying dimensions. A simple example is given in Fig. S5, which depicts
the phase portrait of the model if we assume that the characteristic time scale of the 2nd eigenmode is four
times that of the 3rd, τ2/τ3 = 4. Phase lines show the path of a country that obeys the model, and show that
variation along the 3rd eigenvector shrinks much more quickly than variation along the 2nd eigenvector. This
illustrates how the theory here can be viewed through a dimensionality reduction lens, and indeed encourages
such a perspective.

S6 Supplementary note: Benefits of seeing complexity metrics as

coordinates of structural change

In discussing our dynamical modeling framework, we emphasized that quantities very similar to complexity
metrics (the A and b coordinates) can be motivated using standard arguments of dynamical systems theory.
These arguments lead to measures that have little to do with ‘complexity’ per se, calling into question the
usual interpretation of complexity metrics. However, we could also ask what benefits or opportunities are
suggested by the framework here, which invites us to see complexity metrics as quantities that track the path
of structural change by summarizing an economy’s basket of activities in interpretable, low-order terms. We
describe four possible benefits below.

First, a theory like the one here can potentially give interpretations to the signs and magnitudes of some
complexity metrics. For example, the conventional PCI and ECI are usually standardized to have zero mean
and unit variance, implying that only the way they rank products and countries matters. Yet our theory
assigns clear meaning to signs and magnitudes: Elements of v2 (PCI∗
) convey which products are vacated or

reached, and how large the change in these products is as structural change occurs. Similarly, b(t) (ECI*)
conveys more than just rank information – its magnitude conveys how far a country has progressed in a
particular direction of change.1

Second, interpreting complexity metrics as coordinates raises the possibility of tracking countries’ structural
1As a caveat, we note that there are still numerical and sign differences among these metrics and our coordinates, due to
differences in how each one is constructed, including choices about the product proximity matrix selected; the use of RCAs as
measures of ability; and how RCAs are transformed.

change in absolute terms. A longstanding concern of research on economic growth is whether countries are
converging in income. A related question is whether countries are converging in industrial composition. It
is clearly not possible to track such a convergence if complexity metrics can only provide rank information
about countries. But it is possible to do this using the A and b coordinates, or any complexity metric, if one
can justify that the cardinal values of these metrics are meaningful, so that different countries can potentially
reach similar coordinate values over time.

Third, by deriving these coordinate measures from a dynamical model of the process of development,
improving the description of this process – e.g. developing better proximity matrices Φ, or improving on the
dynamical model presented in the main text – can feed into better summary measures of structural change,
offering a path for refinement of these measures.

Finally, because our coordinates depend on the network of products Φ, our results raise the question of
what happens as this network changes. While it is conventional to assume that Φ is fixed for the purposes
of predicting product transitions, proximities between different products can evolve [21] as the technologies
underpinning these products change, which in turn could shift the directional tendency of structural change.
While in the past countries have undergone well-documented patterns of development (e.g. the shift out of
agricultural products toward manufactured goods [22, 4]) this canonical trajectory could change. A framework
like the one here can account for such shifts in a similar way that index numbers do in other settings. Change
in a region’s b(t) coordinate (for example) would be split into two components – one due to changes in a
country’s weights on the elements of v2, and one due to changes in the elements of v2 themselves. This
would allow one to decompose movements of a country into sum of a long-term movement along the direction
of development, and shifts in the direction of development itself, whereby the relative sequence of different
products can rise and fall over time. This would also be one way for studies to evaluate the quality of the
approximation that Φ is fixed in time, as this would be reflected in the rate of change of v2.

S7 Supplementary note: On the ECI* weights when Φ = ΦP

As discussed in the Methods, the special case Φ = ΦP is noteworthy because PCI∗
coincides with PCI.
There are also reasons why this special case is interesting for the ECI*. First, note that in this case LΦ’s first
left eigenvector w1 = π is proportional to the vector of product ubiquities:

π ∝ u. (S2)

To see this, observe that LΦ = I − Φ˜ and Φ˜ have the same eigenvectors, and that u is a left eigenvector of
Φ˜ P = U
−1MT D−1M with eigenvalue 1:

TP = u

TU
−1

(MT D−1M) = 1

TMT D−1M = d

T D−1M = 1
TM = u

T

u

. (S3)

Taking π ∝ u, the ECI* (Eq. (9) of the main text) becomes

P

!

Rcp(t)up
p0 Rcp0 (t)up0

(t) = X
p

ECI∗
c

PCIp. (S4)

Thus, in this special case, the weights used by the ECI* are ubiquity-adjusted RCAs. These weights emerge
as a by-product of using the proximity matrix Φ = ΦP , and do not represent an intentional choice about
how different products in the export basket should be weighted. However, such a ubiquity adjustment could
nevertheless be beneficial from a measurement standpoint, because it puts more weight on products for which
high RCAs are harder to achieve and are therefore more exceptional. For example, many countries in the
world produce textiles, but only a few produce ostrich eggs. As a result, almost all ostrich egg-producers
have high RCAs in this product. In contrast, to achieve a high RCA in a high-ubiquity product such as
textiles, a country must outcompete many others. In general, achieving high RCAs will be more difficult in
ubiquitous products than in nonubiquitous ones, and it would be reasonable to regard high values of Rcp
as more impressive the more ubiquitous product p is. The conventional ECI not only thresholds RCAs in
weighting products in a country’s activity basket, but it also makes no adjustment for how competitive each
product’s export market is. In contrast, the ECI* uses unthresholded RCAs, and in the special case Φ = ΦP ,

it emphasizes the RCAs of ubiquitous products. We do not offer a more general interpretation of the ergodic
weights πp that applies outside the special case Φ = ΦP , but exploring such issues could reveal interesting
aspects of measurement in those contexts as well.
