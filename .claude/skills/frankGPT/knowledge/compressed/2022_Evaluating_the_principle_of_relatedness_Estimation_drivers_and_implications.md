---
source: 2022_Evaluating_the_principle_of_relatedness_Estimation_drivers_and_implications.pdf
pages: 55
extractor: pdftext
tokens_raw: 32857
tokens_compressed: 20016
compression: 39%
---

Evaluating the principle of relatedness: Estimation,

drivers and implications for policy

Yang Li1,* and Frank Neffke2,1,**

arXiv:2205.02942v2 [physics.soc-ph] 29 Mar 2023

1Center for International Development, Harvard University - 79 JFK street, 02138 Cambridge MA, USA
2Complexity Science Hub Vienna - Josefstädter Straße 39, 1080 Vienna, Austria
*Yang_Li@hks.harvard.edu
**Frank_Neffke@hks.harvard.edu

March 30, 2023

Abstract

A growing body of research documents that the size and growth of an industry in a place
depends on how much related activity is found there. This fact is commonly referred to as the
“principle of relatedness”. However, there is no consensus on why we observe the principle of
relatedness, how best to determine which industries are related or how this empirical regularity
can help inform local industrial policy. We perform a structured search over tens of thousands
of specifications to identify robust – in terms of out-of-sample predictions – ways to determine
how well industries fit the local economies of US cities. To do so, we use data that allow us to
derive relatedness from observing which industries co-occur in the portfolios of establishments,
firms, cities and countries. Different portfolios yield different relatedness matrices, each of
which help predict the size and growth of local industries. However, our specification search not
only identifies ways to improve the performance of such predictions, but also reveals new facts
about the principle of relatedness and important trade-offs between predictive performance
and interpretability of relatedness patterns. We use these insights to deepen our theoretical
understanding of what underlies path-dependent development in cities and expand existing
policy frameworks that rely on inter-industry relatedness analysis.

Funding

Frank Neffke acknowledges financial support from the Austrian Research Agency [FFG, project
#873927: ESSENCSE].

1 Introduction

The field of human geography has uncovered a number of striking empirical regularities, such as
Zipf’s law for city-size distributions (Auerbach, 1913; Zipf, 1946), the law of gravity for social
interactions (Tinbergen, 1962), Tobler’s first law of geography for spatial dependence (Tobler,
1970) and the urban wage and productivity premiums for the exceptional role that cities play in
the economy (Bettencourt et al., 2007; Rosenthal and Strange, 2004). Recently, a new regularity

has been proposed: the principle of relatedness (Hidalgo et al., 2018). According to this principle,
the rate of growth of an activity in a location can be predicted from the prevalence of related
activities in that same location. The principle of relatedness has not only received ample attention
in scholarly work, but also plays an important role in economic policy frameworks that provide
the basis for large-scale place-based development programs (Balland et al., 2019; Boschma et al.,
2022; Hidalgo, 2022; Rigby et al., 2022), such as the EU’s smart specialization policy (Foray et al.,
2009). However, important aspects of the principle of relatedness remain poorly understood. First,

when researchers examine the principle of relatedness, they face a large number of ad hoc choices
for how to construct and then use relatedness measures. Second, we know little about when and why
we observe the principle of relatedness. Third, most existing policy frameworks that leverage the
principle of relatedness do not incorporate this methodological and conceptual uncertainty in their
policy recommendations. In this paper, we perform a structured search over tens of thousands of
specifications of models that aim at quantifying the strength of the principle of relatedness. Doing
so, we (1) provide practical guidance for empirical research, (2) uncover a number of substantive
insights into the principle of relatedness and the forces giving rise to it; and (3) complement existing
policy frameworks by highlighting existing blind spots and proposing an alternative way to use the
principle of relatedness in policy that focuses on the identification, not of growth opportunities, but
of developmental bottlenecks.

The principle of relatedness traces its intellectual roots to debates on how local economies
reinvent themselves (e.g., Glaeser, 2005; Grabher, 1993; Jacobs, 1969; Martin and Sunley, 2006).
For cities to stay relevant in a world where technologies and competitive forces constantly change,
their economies need to find new growth paths. In this context, Jacobs (1969) differentiated between
economic growth and economic development. The former refers to increases in efficiency: as cities
become better at utilizing their existing resources, their productivity grows. The latter refers to
economic renewal and diversification. According to Jacobs, cities that only raise their efficiency risk
deep crises when technological paradigms change or competitive forces shift. Canonical examples
can be found in the developmental histories of Detroit in the U.S., Manchester in the U.K. and the
Ruhr area in Germany. The lack of renewal in such regions would later give rise to an extensive
literature on path dependence and regional lock-in (e.g. Grabher, 1993; Martin and Sunley, 2006).

An important conclusion of this research is that, to avoid decline, the successful regions of past
epochs need to diversify into new activities. However, such new growth paths do not arise out of
thin air. Instead, as Jacobs put it, cities grow by “adding new work to old” (Jacobs, 1969): new
economic activities are often related to what a city already knows how to do.

Although the idea that local economies develop by branching into activities related to their
current strengths (e.g. Frenken and Boschma, 2007) has immediate intuitive appeal, empirically
validating this hypothesis initially ran into a serious obstacle: how do we decide which activities
are related? It would take several decades before this issue had been resolved and Jacobs’ claims
backed by quantitative evidence.

A breakthrough emerged with the insight that important information can be gained from studying
the portfolios of activities in which economic entities choose to be active. Accordingly, certain

combinations of economic activities give rise to economies of scope: there are advantages to engage
in them simultaneously. When myriad economic agents make micro-level portfolio decisions aimed
at exploiting these economies of scope, such advantages leave a trace in the activity mix of economic
entities. In other words, relatedness reveals itself in the tendency of activities to co-occur in
productive portfolios.1 Exploiting this insight allowed accumulating evidence in support of Jacobs’
claims across a wide variety of datasets and contexts, successfully connecting the growth of an
industry (Delgado et al., 2014; Essletzbichler, 2012; Florida et al., 2012; Neffke et al., 2011; Porter,
2003), export category (Zhu et al., 2017), occupation (Muneepeerakul et al., 2013), technology
(Boschma et al., 2015; Petralia et al., 2017) or academic field (Guevara et al., 2016) to the local
prevalence of related activities.2

These empirical studies typically proceed in three steps. First, they determine the relatedness
among economic activities. Next, for each activity in a region, they calculate how prevalent related
activities are in that region. Finally, they regress the growth rates of an activity on the prevalence
of related activities.

Although this procedure seems straightforward, its implementation involves several ad hoc
choices. In this paper, we undertake a structured exploration of tens of thousands of candidate
specifications that aim to replicate the principle of relatedness. To do so, we create a specification
grid on which we vary several aspects of the empirical model design. First, economic activities
can be observed in different types of economic entities, each of which can be used to count
co-occurrences. For instance, Hidalgo et al. (2007) study the co-occurrence of traded product
categories in the export mix of countries, Porter (2003) and Delgado et al. (2010) of industries
in regions, Teece et al. (1994) and Bryce and Winter (2009) of industries in firms, and Neffke
et al. (2011) of products in manufacturing plants. Second, information on productive portfolios
can be turned into relatedness matrices in different ways. Third, given a relatedness matrix, there
are many ways to quantify how related one activity is to the local economy as a whole. For each
of these design aspects, we explore dozens of choices, yielding tens of thousands of candidate
specifications.

Our empirical analysis relies on Dun and Bradstreet’s World Base (henceforth, “D&B data”).
This dataset reports for over 100 million establishments worldwide the number of employees,
geographical coordinates, headquarter-subsidiary relations and up to six economic activities. We
choose this dataset, because it allows us to observe co-occurrences of economic activities at four
different levels of aggregation: the establishment, the firm, the city and the country. To test
which candidate specification in our specification grid best captures the principle of relatedness,
we focus on the economies of US cities and aggregate the D&B data to the level of city-industry
combinations. Next, we repeatedly divide the data into train and test samples and generate out-ofsample
predictions for city-industry employment and employment growth patterns. This allows us
to rank all candidate specifications by their out-of-sample predictive performance.

Overall, we find broad support for the principle of relatedness: many specifications corroborate
the positive association between the presence of related economic activity and an industry’s local

1This insight was first leveraged by scholars in scientometrics (Engelsman et al., 1991) and strategic management
(Teece et al., 1994).
2For a recent overview, see Hidalgo et al. (2018).

size and growth rate. However, many specifications perform poorly, with about 10% - 20% of
specifications failing to outperform benchmarks that use random relatedness matrices. Moreover,
which specification to use depends to some extent on the productive unit in which we observe
industry co-occurrences and different units give rise to different relatedness matrices. To support
future research in this area, we provide a number of guidelines in terms of specification choices
that should be avoided, as well as our preferred specifications.

Apart from these specification recommendations, our analysis reveals a number of stylized facts
about the principle relatedness. First, the principle of relatedness is often regarded as an expression

of which capabilities a city has. Accordingly, moving into related activities is cheaper, because
it limits the number of new capabilities that the city needs to acquire (see, e.g., Balland et al.,
2019). Therefore, many authors exclude from their analysis industries whose location decisions
are not primarily driven by access to local capabilities, such as extractive industries, industries in
the public sector and non-traded services. However, the principle of relatedness also turns out to
be predictive in these sectors. This suggests that the principle of relatedness exists for reasons
that go beyond the common explanation that inter-industry relatedness reflects commonalities in
capability requirements. Second, we find that constructing relatedness matrices in different types
of productive units reveal different types of economies of scope. For instance, labor-sharing
rationales are an important factor explaining co-occurrences in establishments and firms, but much
less so in cities or countries. Yet, the co-occurrence patterns in cities contain information for
predicting location and growth patterns beyond what is expressed in establishment and firm level
co-occurrences. Finally, good predictive performance does not not guarantee a clear understanding
of why some local industries thrive in a city: some of the best performing specifications yield
cluttered inter-industry relatedness networks that make it hard to disentangle clusters of related
industries.

Finally, when it comes to policy implications, an important finding is that the principle of
relatedness is much better at predicting where industries are located than where they grow. As a
result, if we were to prioritize industries by their predicted growth potential, we would often pick
industries that won’t exhibit growth spurts and miss industries that will. Moreover, even if we could
identify promising growth candidates, the principle of relatedness offers little guidance for how to

promote their growth. In fact, one may ask: if these industries fit the local economy so well, why
haven’t they grown yet? We will argue that this type of question can complement current policy

frameworks by using the principle of relatedness, not to prioritize industries, but as an anomaly

detection tool. Accordingly, the principle of relatedness can help policy makers diagnose their
economy, by prompting them to ask why specific industries are surprisingly small or large in their

city. We conclude our paper by proposing to use this type of analysis to identify binding constraints
to economic development in a city, integrating the principle of relatedness into the wider policy
framework of Growth Diagnostics (Hausmann et al., 2008b).

2 Data

The D&B data are provided by Dun and Bradstreet, a business analytics firm. They contain
information on over 100 million establishments across the world and offer an almost complete
census of economic establishments in the U.S.. For each establishment, the dataset records an

variable counts mean std
# employees 165,987,254
# establishments 26,374,079
# establishment (>1 SIC 3-digit industry) 1,688,984
# firms 363,620
# firm (>1 primary SIC 3-digit industry) 83,548
# cities 927
# countries 100
# industries 415

# industries per establishment 1.08 0.34
# industries per multi-industry establishment 2.25 0.59
# industries per firm 1.66 2.20
# industries per multi-industry firm 3.14 3.42
# industries per city 288.37 56.11
# industries per country 316.11 78.72
# employees per city-industry 620.93 4,714.69
log(# employees per city-industry) 3.94 2.14
Δ log() -0.08 0.79

Table 1: Summary statistics

Multi-industry establishments are establishments with at least two distinct 3-digit SIC codes. Multi-industry
firms are firms that list establishments with at least two distinct primary 3-digit SIC codes. Δ log( ) refers
to employment growth between 2011 and 2019.

identifier (the so-called D.U.N.S.3 number). This D.U.N.S. number is unique to the establishment
and remains unchanged throughout its existence, regardless of changes in ownership. Furthermore,
the dataset offers for each establishment the number of employees,4 geographical coordinates, and
the D.U.N.S. number of the parent establishment if the establishment is part of a larger corporation.
The latter allows us to reconstruct corporate hierarchies that express these ownership linkages.
Finally, each establishment can list up to six different industries. These industries are ordered by
their importance, with the primary codes identifying the establishment’s main industry. Industry
codes are recorded in the SIC or NAICS classifications. In this paper, we rely on the 2011 and
2019 waves of the D&B data, the first and last waves available to us at the time of the analysis.
Because our 2011 wave only contains SIC codes, our analysis is based on 3-digit industries of this
classification system.5 Table 1 provides some general statistics for the dataset.

The D&B data are highly representative of the US economy (a comparison with US County
Business Patterns data is listed in Appendix A.2), but not necessarily of other economies. Therefore,
we will mainly work with US data, limiting the sample to US establishments and defining firms
as sets of US establishments that report to the same domestic (US-based) parent. However, to
3D.U.N.S is a recursive acronym for D.U.N.S. Universal Numbering System.
4Outside the U.S., most employment figures are based on estimates by D&B.
5At this level, there are over 400 industry codes, distinguishing, for instance, between the construction industries of
“Masonry, stonework, tile setting, and plastering” and “Plumbing, heating and air-conditioning” or the manufacturing
industries of “Computer and office equipment” and “Household appliances”.

examine the industrial portfolios of countries, we aggregate information for a number of national
economies that are reasonably well represented by the D&B data (see Appendix A.1). This
reduced representivity compared to the US will result in some uncertainty about the accuracy of
country-level relatedness matrices.

Another drawback of using D&B data is that, although they provide a fairly accurate account
of the level of economic activity in a particular year, observed changes in economic activity tend
to be quite noisy due to the fact that the information in the database is not updated in a uniform
way (Crane and Decker, 2019; Neumark et al., 2007). To limit such concerns, we will calculate
growth rates over the longest possible time period. In spite of these shortcomings, the micro-level
character of the data, the record of ownership ties and the fact that industry classifications do not
change over time or across geography make the dataset uniquely suited for our purposes.

3 Specification search

3.1 Setting up the search grid

Researchers need to make a number of choices when analyzing the principle of relatedness. We
summarize these choices in Fig. 1. First, we need to choose the type of productive unit in which
industries can coincide. That is, we need to determine at which level of aggregation we capture
economies of scope.

The D&B data allow us to identify the industrial portfolios of four types of productive units:
establishments, firms, regions and countries.6 As a regional unit, we use US Core-Based Statistical
Areas (CBSAs, i.e., metropolitan and micropolitan areas, henceforth “cities”).

As we move from establishments to firms, cities and countries, industrial portfolios start
reflecting a widening range of economies of scope. As a consequence, the notion of relatedness
changes. For instance, establishments are likely to combine activities that share similar inputs,
technologies or skills (Neffke et al., 2011). Firms can harness additional economies of scope across
their establishments, by pooling managerial, marketing, sales or other organizational processes
(Teece et al., 1994). At the level of cities, industries may coagglomerate to share pools of specialized
labor and suppliers, or physical and institutional infrastructure (see, e.g., Diodato et al., 2018; Ellison
et al., 2010). In countries, the potential sources of economies of scope widen further to include
climatic conditions and macro-level institutions such as intellectual property rights regimes or
sophisticated financial markets (Rajan and Zingales, 1998).

However, moving to higher level productive units is not costless: it increases the number of
spurious and indirect relations between industries. For instance, ski-resorts exhibit few economies
of scope with hydroelectric power plants. That is why we do not observe firms that specialize in
both activities, let alone that combine them in one and the same economic establishment. Yet,
these industries do often colocate in the same regions. Such combinations, which are more likely
to be found in the industrial portfolios of higher-order productive units, confound relatedness as an
estimate of economies-of-scope. We will study these issues in more depth in section 5.1.

6When we construct the industrial portfolios of firms, we do not use all industries listed by their establishments,
but only establishments’ primary industry codes (see Appendix B.1). This way, we avoid that industries that coincide
in establishments by construction also do so in firms.

Once we have picked a type of productive unit, we need to construct three interrelated quantities.
The prevalence of an economic activity (step 1 of Fig. 1), the relatedness of pairs of industries (step
2) and the density of related activity around an industry in a local economy (step 3). To facilitate
calculations, we collect our data into matrices at the bottom of Fig. 1.
Prevalence, , expresses how strongly represented an industry  is in productive unit . The
simplest way to capture this is by the amount of employment unit  has in industry . A more
commonly used metric is the unit’s revealed comparative advantage (RCA) in the industry (e.g.
Hidalgo et al., 2007). In appendix B, we list a number of plausible alternatives that mainly differ in
the benchmark against which they assess how large an industry’s presence in a productive unit is.

When it comes to measuring relatedness between industries, our grid relies on a class of socalled
outcome-based relatedness metrics. These metrics focus on the imprint that relatedness
leaves on the behavior of economic actors.7

Outcome-based measures have been justified by reference to the survivor principle (Teece
et al., 1994). Accordingly, the fact that we observe that two industries often coincide in the same
productive units means that this combination is economically viable. Outcome-based measures
have two advantages. First, there are many ways in which activities may be related. For instance,
industries may share the same human capital requirements, use similar resources or be part of the
same value chains. Outcome-based measures summarize all these linkages in a single metric that
implicitly puts most weight on the linkages that matter most in the portfolio decisions of economic
actors. Second, outcome-based measures can be derived from the same data that are used to study
industrial growth or diversification. For instance, in economic geography, they can be derived
from data that describe the industry mix of cities. As a consequence, outcome-based relatedness
measures are by far the most common in the literature.

Most outcome-based relatedness matrices are based on counts of how often two industries
co-occur in the same productive units. These counts are typically normalized to account for how
often we would expect the industries to co-occur merely by chance. We explore several metrics
that differ mainly in these normalizations: correlations, cosine distances, conditional probabilities,
and RCA-like transformations. We explain the differences and similarities between these methods
from a mathematical and conceptual point of view in Appendix B.2. In addition, we distinguish
between approaches that use continuous prevalence information and those that binarize prevalence
information. The latter consider that an industry is present in a productive unit whenever its
prevalence exceeds some threshold value.

Furthermore, some authors (e.g., Muneepeerakul et al., 2013) have argued that positive relatedness
(industries that appear together more often than by chance) is qualitatively different from
negative relatedness (industries that coincide less than by chance). We explore this by using not
only the full relatedness matrices, but also versions in which all negative elements are set to zero.

Finally, in step 3, we need to assess not just the relatedness between two industries, but also
how related an industry is to a city’s entire portfolio of industries. To do so, we use a measure that
Hidalgo et al. (2007) dubbed an industry’s “density” in the city. The density of industry  in city ,
, is defined as the average prevalence of all other industries, , in , weighted by their relatedness
to :

7Neffke and Henning (2013) distinguish between resource-based and outcome-based relatedness measures.
Resource-based measures define relatedness as the extent to which industries utilize the same resources or inputs.
Examples are relatedness measures based on input-output tables (e.g., Fan and Lang, 2000), occupational employment
vectors (e.g., Farjoun, 1994) or labor flows (Neffke and Henning, 2013).

Binarize?

Overrepresentation

νir

Fixed eects

Random
Regression
level
log(level+1)
RCA
RCA*
PMI

cities

Size of city

Poisson

φik

d

N

r

N

i

OLS

φij

d

N

i

industries

k

d11 · · ·

d

N

r

k

Nearest neighbors? {0, 50, 100, 200, 300, } all

Step 3: Density -

=

˜Φ

V

=

D

Figure 1: Constructing the specification grid.

.

}

1, ...,

Positive only?

φij

.

,

.

Step 2: Relatedness -

industries

κ
 ∈ {

φ

N

i

N

i

φ

N

i

industries

φ12 · · ·

Cond. prob.

RC
A

Correlation
Cosine

Correlation
Cosine

Continuous

φ21 φNi

Binarized

Φ =

yes

no

Binarize?

νiu

productive units

Step 1: Prevalence -

Size in productive unit

ν

N

u

N

i

Overrepresentation

ν

N

i

industries

Fixed eects

Random
Regression
level
log(level+1)
RCA
RCA*
PMI

ν11 · · ·

ν

N

u

Poisson

OLS

=

V

Í
≠∈

 =
∑︁
≠∈

. (1)

where
is the set of  most closely related “neighboring” industries to industry ,   the relatedness
between industry  and  and  industry ’s prevalence in city .8 Once again, we can either use
continuous prevalence information as weights or binary information on whether or not an industry
is present in a city.

This procedure leads to various ways to quantify prevalence, relatedness and density. Combining
all alternatives of each step in Fig. 1, we arrive at 32,480 different specifications.

3.2 Estimation

To evaluate each specification, we study its performance in two prediction tasks: out-of-sample
prediction of employment levels and out-of-sample prediction of employment growth. For the first
task, we estimate the following regression model:

log  =  + 1 log  + 2 log  + , (2)

where  represents the density of industry  in city  at time ,9  the employment of industry
 in city  at time ,  the employment in industry  at time  and  the employment in city  at
time .  is a residual.

For the second task, we estimate the following growth model:

Δ log  =  log  +  + 1 log  + 2 log  +  if  > 0, + > 0; (3)

where  is the time-horizon over which growth is measured and  captures mean reversion effects.10
Accounting for the latter is crucial, because  and  are typically strongly and
positively correlated. Therefore, failing to account for (negative) mean reversion effects will lead
to an underestimation of the (typically positive) effect of density.11 Note that we only evaluate
performance for growth at the intensive margin. That is, we only look at growth rates for local
industries that exist in both 2011 and 2019. This simplifies the analysis because it avoids values of
log(0) in the dependent variable and mean reversion term.

8If density is used to predict employment levels, the contribution of the industry itself to the sum in eq. (1) would
render the regression analysis of section 3.2 circular. When instead predicting growth, we will capture the industry’s
own contribution by adding a mean-reversion term. Therefore, we exclude industry  from its own neighborhood in eq.
(1).
9Because   can have a highly skewed distribution, we log-transform density in specifications where an industry’s
prevalence in a city is based on RCAs or on raw employment counts.
10These effects – which quantify the influence of the size of an industry in the base year – have sometimes been
interpreted as local competition effects (e.g. Delgado et al., 2014). However, negative mean reversion effects also
arise as statistical artefacts if   is measured with noise or has an idiosyncratic element.
11Different studies add different control variables. Apart from controls for the overall size of the region and of the
industry, some studies add aggregate growth rates of regions and industries – what Hausmann et al. (2021) call radial
growth. Another common specification adds industry and region dummies. Note, however, that both sets of control
variables assume information that is not available in a forecasting exercise: radial growth explicitly assumes that
aggregate future growth rates are available and region and industry fixed effects make the same assumption implicitly.

Employment levels

Employment growth

R
 w/o density term 0
 50 100 150 200 250

R
 w/o density term 0
 200 400 600 800 1000

candidate specifications
benchmark

candidate specifications
benchmark

.6 .65 .7 .75
Out-of-sample R2

.055 .06 .065 .07
Out-of-sample R2

Figure 2: Kernel density plots of out-of-sample
.
Left: prediction of employment levels; right: prediction of employment growth. Vertical gray lines:
2 of
specifications of eqs (2) and (3) without density ( ) term. Candidate specifications shows the distribution
of the
in the specification grid. Benchmark shows the distribution for runs in which density terms are
based on random proximity matrices.

To evaluate the models of eqs (2) and (3), we first divide the dataset into a train and a test
sample. The train sample is used to construct density and control variables, as well as to fit the
model’s parameters. To make it computational feasible to run millions of regression analyses, we
fit these models using Ordinary Least Squares (OLS). Next, predictive performance is evaluated
on the test sample. We repeat this procedure 100 times to arrive at an average model fit for each
candidate specification, expressed as the model’s out-of-sample
, as well as confidence bands

around this average. Finally, as a benchmark, we estimate models without density terms and with
density terms that are based on (symmetric) relatedness matrices whose elements are drawn at
random from a uniform distribution.

4 Results

4.1 Grid search

Fig. 2 shows distributions of model performance across specifications. The benchmark specification
without density term is marked by vertical lines and dashed curves show benchmark performance
distributions for specifications with random relatedness matrices.
The majority of specifications corroborate the principle of relatedness: 88% of candidate
specifications outperform the median random benchmark in predicting employment levels and 78%

prediction task baseline
log(emp.) Δ log(emp.)
Relatedness
entity City City n.a.
prevalence resid. (OLS) RCA n.a.
binarized no yes n.a.
metric cosine dist. RCA* n.a.
 n.a. n.a. n.a.
truncation yes yes n.a.
Density
prevalence resid. (OLS) RCA n.a.
binarized yes yes n.a.
# neighbors 300 100 n.a.
Out-of-sample

log(emp.) 0.770 0.710 0.666
Δ log(emp.) 0.063 0.076 0.060

Table 2: Top specifications.
Specifications with the highest out-of-sample

for employment levels (first column), for employment
growth regressions (second column) and without density term (third column).

in predicting employment growth. However, there is substantial heterogeneity across specifications.
For specifications in the 99th performance percentile, adding a density term raises the
2 by about

10% when predicting employment levels and by about 16% when predicting employment growth.
In the median specification, the density term raises the
2 of these models only by between 2 and
3%.

Appendix C.1 describes which specification elements matter most for a model’s performance.
The most important aspect of the specification grid turns out to be how we define density and, in
particular, how we define the prevalence of an industry in a city. Also the choice of the productive
unit has a large impact on the quality of growth predictions. Of least importance is how many
neighbors are used when calculating density variables.

Table 2 shows the two top specifications in terms of predictive validity. The first column uses
the prediction of employment levels as a criterion, the second the prediction of employment growth.
Apart from relying on the same productive unit for relatedness calculations, the selected specifications
have little in common. Moreover, their performance is not very robust: the specification
that predicts employment levels best, fails to do well in predicting employment growth, and vice
versa. This suggests that the performance criteria are too noisy to confidently select an optimal
specification from our grid.

4.2 Robust performance

To draw reliable conclusions, we explore which specification choices are robustly associated with
good performance. We will call a specification robust if it ranks among the best 10% of specifica11
tions in both prediction tasks. Next, we count how often each choice is used in this set of robust
specifications.

Tables 3 and 4 report the results of this exercise. They display for each specification characteristic
the share of specifications that yield robust performance. These shares can be interpreted as the
likelihood that a randomly chosen specification that uses a given characteristic preforms robustly.
Columns correspond to the types of productive units that were used to measure inter-industry
relatedness. Furthermore, the tables are split into two parts, one using binary (presence) information
and one using continuous (prevalence) information to construct relatedness matrices (Table 3) or
density variables (Table 4).

The overall shares of robust specifications are provided in bold. The likelihood that a random
specification is robust is quite low: 2.0% for specifications with binary (co-occurrence-based)
relatedness matrices and 1.2% for specifications with continuous (co-prevalence-based) relatedness
matrices.

Preferred specifications. In appendix C.2, we provide recommendations for how to avoid poor
predictive performance, listing a number of general lessons about how not to construct relatedness
and density metrics. Here, instead, we analyze two specifications that, in light of Tables 3 and 4,

are a priori expected to work particularly well. The first specification uses a relatedness matrix
based on city-level binarized co-occurrence information. The second uses a relatedness matrix
based on firm-level continuous co-prevalence information. As points of reference, we also consider
the specification in Hidalgo et al. (2007), once based on country-level co-occurrences as used in
Hidalgo et al.’s original study and once based on city-level co-occurrences. The latter are frequently
used in the economic geography literature (Boschma et al., 2013; Montresor and Quatraro, 2017;
Zhu et al., 2017).

Table 5 shows that both preferred specifications work remarkably well, ranking among the top
5% of specifications in terms of predicting employment and employment growth. Hidalgo et al.’s
specification performs only marginally worse, as long as it uses city colocation information to
calculate relatedness.

5 Inside the principle of relatedness

A core aspect of each empirical specification is its relatedness matrix. These matrices depend
somewhat on technical details, such as normalizations and proximity metrics (see Fig. F.1 of
Appendix F), but the most pronounced differences are due to differences in the productive units in
which industry co-occurrences are recorded. Studying these differences offers an opportunity to
learn more about the inner workings of the principle of relatedness. To do so, we focus on three
aspects: (1) the degree to which matrices yield well-delineated clusters of industries, (2) the drivers
of relatedness, and (3) their performance in predicting future growth.

5.1 Industry spaces

Relatedness matrices are often visualized as networks, or industry spaces (e.g., Hidalgo et al.,
2007). These networks can be used to identify clusters of related industries and how to do so is an
active field of research (Delgado et al., 2016; O’Clery and Kinsella, 2022). Here, we explore how

(BINARY) PRESENCES
PREVALENCE Cntry City Firm Estab. Total
RCA/RCA*/PMI 0.0% 3.0% 0.6% 0.1% 0.9%
resid. (POI) 0.0% 3.0% 0.6% 0.0% 0.9%
emp./log(emp.) 0.0% 0.0% 0.6% 0.1% 0.2%
Total 0.0% 5.9% 1.9% 0.2% 2.0%
METRIC Cntry City Firm Estab. Total
RCA* 0.0% 1.7% 0.0% 0.0% 0.4%
Pearson corr. 0.0% 1.3% 0.1% 0.0% 0.3%
cosine dist. 0.0% 0.0% 0.3% 0.2% 0.1%

 = 0.0 0.0% 1.2% 0.3% 0.0% 0.4%
... 0.1 0.0% 0.9% 0.3% 0.0% 0.3%
... 0.2 0.0% 0.5% 0.3% 0.0% 0.2%
... 0.3 0.0% 0.2% 0.2% 0.0% 0.1%
... 0.4 0.0% 0.0% 0.2% 0.0% 0.1%
... 0.5 0.0% 0.0% 0.2% 0.0% 0.0%
Total 0.0% 5.9% 1.9% 0.2% 2.0%

(CONTINUOUS) PREVALENCES
PREVALENCE Cntry City Firm Estab. Total
RCA* 0.0% 2.0% 0.2% 0.2% 0.6%
resid. (OLS) 0.0% 0.2% 1.3% 0.1% 0.4%
PMI 0.0% 0.4% 0.0% 0.0% 0.1%
emp. 0.0% 0.0% 0.0% 0.1% 0.0%
resid. (POI) 0.0% 0.1% 0.0% 0.0% 0.0%
RCA 0.0% 0.0% 0.0% 0.1% 0.0%
log(emp.) 0.0% 0.0% 0.0% 0.1% 0.0%
Total 0.0% 2.8% 1.4% 0.6% 1.2%
METRIC Cntry City Firm Estab. Total
Pearson corr. 0.0% 2.7% 0.6% 0.0% 0.8%
cosine dist. 0.0% 0.1% 0.8% 0.6% 0.4%
Total 0.0% 2.8% 1.4% 0.6% 1.2%

Table 3: Definition of relatedness.

(BINARY) PRESENCES
PREVALENCE Cntry City Firm Estab. Total
RCA/RCA*/PMI 0.0% 2.1% 0.1% 0.4% 0.7%
resid. (POI) 0.0% 2.1% 0.1% 0.4% 0.7%
resid. (OLS) 0.0% 0.0% 0.4% 0.0% 0.1%
Total 0.0% 4.3% 0.7% 0.8% 1.4%
TRUNCATION Cntry City Firm Estab. Total
positive 0.0% 1.7% 0.3% 0.0% 0.5%
all 0.0% 0.9% 0.3% 0.8% 0.5%
n.a. 0.0% 1.6% 0.1% 0.0% 0.4%
Total 0.0% 4.3% 0.7% 0.8% 1.4%
# NEIGHBORS Cntry City Firm Estab. Total
50 0.0% 1.3% 0.3% 0.5% 0.5%
100 0.0% 1.2% 0.1% 0.3% 0.4%
200 0.0% 0.8% 0.1% 0.0% 0.2%
300 0.0% 0.5% 0.1% 0.0% 0.1%
415 0.0% 0.5% 0.1% 0.0% 0.1%
Total 0.0% 4.3% 0.7% 0.8% 1.4%

(CONTINUOUS) PREVALENCES
PREVALENCE Cntry City Firm Estab. Total
resid. (OLS) 0.0% 1.3% 2.3% 0.0% 0.9%
RCA* 0.0% 1.1% 0.1% 0.0% 0.3%
resid. (POI) 0.0% 0.9% 0.0% 0.0% 0.2%
PMI 0.0% 0.9% 0.0% 0.0% 0.2%
log(emp.) 0.0% 0.7% 0.1% 0.0% 0.2%
emp. 0.0% 0.6% 0.0% 0.0% 0.2%
Total 0.0% 5.5% 2.5% 0.0% 2.0%
TRUNCATION Cntry City Firm Estab. Total
positive 0.0% 2.4% 0.4% 0.0% 0.7%
all 0.0% 0.9% 0.2% 0.0% 0.3%
n.a. 0.0% 2.3% 1.8% 0.0% 1.0%
Total 0.0% 5.5% 2.5% 0.0% 2.0%
# NEIGHBORS Cntry City Firm Estab. Total
100 0.0% 1.4% 0.5% 0.0% 0.5%
50 0.0% 1.3% 0.4% 0.0% 0.4%
200 0.0% 1.1% 0.6% 0.0% 0.4%
415 0.0% 0.9% 0.5% 0.0% 0.3%
300 0.0% 0.8% 0.5% 0.0% 0.3%
Total 0.0% 5.5% 2.5% 0.0% 2.0%

Table 4: Definition of density.

Preferred specifications Hidalgo et al. (2007)
binary continuous country city
Relatedness

entity city Firm Country city
prevalence RCA resid. (OLS) RCA RCA
binarized yes no yes yes
metric RCA* cosine dist. cond. prob. cond. prob.
 n.a. n.a. 0.0 0.0
truncation yes yes n.a. n.a.
Density

prevalence resid. (OLS) resid. (OLS) RCA RCA
binarized no no yes yes
# neighbors 100 100 415 415
Out-of-sample performance

- levels 0.707 (0.950) 0.730 (0.989) 0.685 (0.623) 0.704 (0.929)

- growth 0.069 (0.974) 0.068 (0.955) 0.062 (0.508) 0.067 (0.926)

Table 5: Preferred specification.

Left panel: specifications with binary and continuous prevalence used to construct relatedness matrices.
Right panel: specifications in Hidalgo et al. (2007) using industry combinations observed within countries
and cities. The bottom rows show the specification’s performance in terms of out-of-sample
, with the
corresponding percentile rank position in parentheses.

well different matrices lend themselves for this task, focusing on the relatedness matrices in our
preferred specifications.

Delineating clusters of industries

Appendix I displays two industry spaces for each productive unit, one for our preferred binary and
one for our preferred continuous specification. Some industry spaces exhibit more structure than
others. Although deciding how “structured” a network is is somewhat subjective, we can quantify
an aspect of this by determining how easy it is to identify communities in the network.

To do so, we calculate the modularity and the effective number of communities for each industry
space. Modularity quantifies to what extent a network consists of easily separable communities. It
is defined as the fraction of ties that form between industries belonging to the same community,
minus the fraction of such ties that we would have expected, had links formed at random. A
high modularity score thus means that most links form between industries in the same community,
as opposed to across communities, i.e., that the industry space is composed of distinct, welldelineated
clusters.12 The effective number of communities is a so-called Hill number (Hill, 1973).
It is calculated as
, where  represents the entropy of the communities’ size distribution. It

12Because relatedness matrices are too dense for network analysis, we use the truncated networks of Figs I.1 and
I.2, not of the full relatedness matrices. To calculate modularity, we rely on the Louvain algorithm (Blondel et al.,
2008) to compute the best community division and then calculate the corresponding modularity scores. The random
benchmark used in these calculations preserves node degrees, but randomly rewires connections.

Binary

Continuous

.4 .5 .6 .7 .8
modularity

.4 .5 .6 .7 .8
modularity

Establishment
Firm
City
Country

Establishment
Firm
City
Country

6 8 10 12 14 16
effective # communities

6 8 10 12 14 16
effective # communities

Figure 3: Modularity and effective number of communities.

The vertical axis depicts the modularity and the horizontal axis the effective number of communities – defined
as
 , where  denotes the entropy of the size distribution of the communities – for different relatedness
matrices. Left panel uses our preferred specification for binary presence data to construct the relatedness
matrices, right panel for continuous prevalence data.

reflects how many communities of equal size would be needed to arrive at the same observed
entropy.

Results are shown in Fig. 3. Industry spaces based on firm-level portfolios exhibit the clearest
community structures, combining a modest number of distinct communities with a high degree of
modularity. In contrast, cities give rise to the most cluttered industry spaces with only few not very
well-delineated communities. The industry spaces for establishments and countries are somewhere
in between these two extremes.

Conformance to sectoral classification

Do industries that belong to the same higher-level sectors tend to be more related? To study this, we
define the SIC relatedness between two industries as the number of leading digits their SIC codes
shares. Given that we work with 3-digit industries, SIC relatedness can be 0, 1 or 2. If relatedness
is particularly high between industries in the same sector but not across sectors, we will say that the
relatedness matrix conforms closely to the classification system’s sectoral boundaries. Because of
our familiarity with classical sector designations, such matrices tend to be more intuitive.

Fig. 4 plots the average relatedness for industry pairs at different levels of SIC relatedness.
The binary and continuous specifications conform about equally closely to the higher-level sectorboundaries.
However, there are pronounced differences between productive units. The closest
agreement with the classification system is achieved by relatedness matrices based on the industrial
portfolios of establishments. The next closest agreement relies on firm portfolios. In contrast,
industrial portfolios of cities and countries yield relatedness matrices that align much less with the
sectoral classification. As a consequence, the establishment- and firm-level relatedness matrices
yield quite intuitive clusters. In contrast, relatedness based on city- or country-level colocation

Binary

Continuous

 1 2 3 4 5
normalized relatedness

 1 2 3 4 5
normalized relatedness

establishment firm
city country

establishment firm
city country

0 1 2
SIC proximity

0 1 2
SIC proximity

Figure 4: Agreement with the industrial classification system.

The vertical axis depicts the average relatedness and its 95% confidence interval between two industries
based on our preferred binary (left) or continuous (right) specification. To ensure comparability, links are
normalized by the sum total of elements in each relatedness matrix, multiplied by 100,000 for graphical
convenience. The horizontal axis depicts industries’ SIC relatedness, where 0 means that the industries
belong to different sectors.

patterns often cuts across sector boundaries, suggesting connections that are more surprising at
best and puzzling at worst.

Drivers of relatedness

In section 3.1, we speculated that different types of productive units harness different types of
economies of scope. To explore this, we regress the number of co-occurrences between industries
on measures of the strength of value chain linkages and human capital similarities. To quantify
value-chain linkages, we cast US input-output tables (Ingwersen et al., 2022) into the SIC 3-digit
classification. Next, we symmetrize these tables by using the maximum of the input coefficients
between industries  and ,   , in either direction:

  = max(  ,  )

To quantify human capital similarities, we rely on the US Bureau of Labor Statistics’ Occupational
Employment and Wage Statistics for 2011.13 We again transform industry codes into 3-digit
SIC industries. The human capital similarity between industry  and  is now calculated as:

13Retrieved from www.bls.gov/oes.

(1) (2) (3) (4)
Establishment Firm City Country

ℎ 7.344*** 2.424*** 1.036*** 1.114***
(1.07) (0.24) (0.00) (0.01)

 1.056** 1.044*** 1.012*** 1.014***
(0.02) (0.01) (0.00) (0.00)

 85,464 85,029 85,903 85,903
pseudo-
2 0.784 0.749 0.860 0.453

Table 6: Drivers of co-occurrences of industries.
Standard errors (two-way clustered by industry) in parentheses, *:  < 0.05, **:  < 0.01, ***:  < 0.001.
The table reports incidence rate ratios from a Poisson pseudo-maximum-likelihood regression of the number
of co-occurrences of two industries in a productive unit on human capital similarity and value-chain linkages
between the industries, controlling for two-way industry fixed effects. Coefficients are standardized by each
variable’s standard deviation. Co-occurrence counts refer to the number of times that two industries exhibit
  > 1 in the same productive unit. Columns label the type of productive unit in which co-occurrences
are observed.

 =

/
/
> 1

,

  =   ,
   =

,

   + 1

ℎ
  =

where (.) is an indicator function that evaluates to 1 if its argument is true and to 0 otherwise,
is the employment of occupation  in industry ,  and
the employment of occupation  and
industry  in the US and  the overall employment in the US. In words, we first determine which
occupations are overrepresented in which industries. Next, we count how many occupations are
overrepresented in industry  and . Finally, we normalize these occupational co-occurrences using
an RCA-style metric, that we cast between 0 and 1 to reduce skew, mimicking the steps described
in eqs (B.1), (B.2) and (B.15):

Next, we regress co-occurrence counts on value chain and human capital linkages between
industries. We standardize explanatory variables by mean-centering them and dividing them by
their standard deviations. As a result, the reported incidence rate ratios (IRRs) express by which
factor co-occurrences go up for a one-standard-deviation increase in human capital similarities or
value-chain linkages. Table 6 reports results for Poisson pseudo-maximum-likelihood estimation
with two-way industry fixed effects.

The main driver of co-occurrence patterns is human capital similarities. Although this holds
across all models, effects are particularly salient for co-occurrences in establishments and firms,
where a one-standard-deviation increase in human capital similarity is associated with an over

7-fold increase in co-occurrences in establishments and an over 2-fold increase in firms. In cities
and countries, the link between co-occurrence patterns and labor linkages is much weaker, lifting
co-occurrences by just 4% and 11%. This suggests that human-capital based economies of scope
are core to how industries are combined in establishments and firms, but labor market externalities
are much less important for how industries co-agglomerate in cities and countries. Finally, although
value-chain linkages are always statistically significant, they explain comparatively little of which
industries co-occur in all productive units.

How much information does a productive unit add?

Regardless of the productive unit in which we measure relatedness, density always has a positive
and significant effect on the sizes and growth rates of local industries in our preferred specifications.
But do different productive units offer redundant or complementary perspectives on relatedness?

To analyze this, we run our performance regressions with pairs of density variables, juxtaposing
the relatedness matrices associated with two different productive units. We then ask in which
pairings one of the two density variables turns statistically insignificant. When this happens, the
juxtaposed relatedness matrices contain redundant information.

Table 7 shows results. To economize on space, we only display coefficients for the density
variables, omitting control variables. Although firms and establishments give rise to different
relatedness matrices, the information in establishments that is relevant for our predictions is largely
the same as in firms. In contrast, city-level co-occurrences offer information that is not captured
in the establishment or firm level relatedness matrices. This suggests that the industrial portfolios
of firms (or establishments) and of cities provide complementing views on the predicted growth
trajectories of cities.14

Prediction versus interpretation

Our results so far suggest an interesting tension between interpretability and predictive validity.
City-level relatedness matrices tend to be top performers when it comes to out-of-sample prediction
and they contain information that is not present in other relatedness matrices. Yet, city-level industry
spaces are less intuitive and interpretable than firm- or establishment-level ones: they neither closely
follow the delineations between traditional sectors, nor strongly reflect human capital or value-chain
links.

5.2 Sector-specific estimations

So far, we have studied the principle of relatedness in the economy as a whole. However, industries
differ in how much their location and growth patterns will be determined by local capabilities. In
some industries, capabilities are only of secondary concern. For instance, industries that rely on
natural resources can only locate where those resources are found: fishing requires access to bodies
of water and, regardless of which capabilities a city has, mining activities cannot emerge without

14The country level also offers new information, however, only when it comes to predicting employment levels, not
employment growth. Because country-level relatedness provides only weak information about growth opportunities,
we discount this evidence. These findings are corroborated when density variables are constructed with our preferred
continuous instead of binary specifications (see Appendix G).

productive unit (1) (2) (3) (4) (5) (6)
Effect of density on employment levels
establishment 0.511*** 0.318*** 0.439***
(0.0364) (0.0397) (0.0373)
firm 0.0580 0.199*** 0.306***
(0.0367) (0.0426) (0.0328)
city 0.378*** 0.462*** 0.463***
(0.0436) (0.0461) (0.0473)

country 0.186*** 0.289*** 0.237***
(0.0534) (0.0467) (0.0565)
 384,705 384,705 384,705 384,705 384,705 384,705

2 0.720 0.732 0.727 0.723 0.714 0.729
Effect of density on employment growth
establishment 0.00345* 0.00275 0.00755***
(0.00174) (0.00149) (0.00138)
firm 0.00576*** 0.00357* 0.00803***
(0.00170) (0.00149) (0.00124)
city 0.00937*** 0.00891*** 0.0105***
(0.00152) (0.00155) (0.00133)
country 0.000895 0.000832 0.00118

(0.00151) (0.00139) (0.00138)
 245,395 245,395 245,395 245,395 245,395 245,395

2 0.068 0.072 0.072 0.067 0.068 0.072

Table 7: Redundancy and complementarity in pairs of density variables.
Standard errors in parentheses, *:  < 0.05, **:  < 0.01, ***:  < 0.001. Upper panel: regression
analysis of employment levels, controlling for industry and city size. Lower panel: regression analysis of
employment growth, controlling for mean reversion effects, industry and city size. The coefficients reflect
the effects of density measured using the productive units listed in the first column. All density measures are
based on our preferred binarized specification. For results based on our preferred continuous specifications,
see Table G.1 in Appendix G.

mineral deposits. Similarly, many nontraded services, such as restaurants and shops, require easy
access to large markets, and the presence and size of public services, such as health care and
education, are determined by government policies. Many authors therefore restrict their analysis
to industries in the private sector that produce tradable products and that are not based on natural
resources.

But how relevant are these restrictions? To answer this question, we reanalyze our specification
grid for four (mutually exclusive) sectors: public-sector industries, resource-based industries, nontraded
services, and all remaining industries, to which we will refer as traded industries. The exact
definition of each sector is provided in Appendix D.

Figs 5a and 5b show scatter plots of the out-of-sample performance in each sector against the
out-of-sample performance in the overall economy. Predictive performance is highly correlated
across sectors: specifications that perform well in the overall sample also tend to do so within
each sector. This consistency is reassuring: it suggests that our analysis is robust, yielding similar

preferred specifications in different subsamples.

Furthermore, whenever observations lie above the 45 degree line, specifications perform better
in the corresponding sector than in the overall economy. This often happens in the traded sector, but
rarely in nontraded services. However, in all four sectors, the principle of relatedness has at least
some predictive validity. Moreover, predictive performance is not particularly poor in public sector
activities or resource-based industries, suggesting that restricting the sample to traded industries
may be helpful, but not necessary.

There are plausible explanations for why predictability is high also outside non-resource based,
private-sector, traded industries. For instance, different resource-based activities may be attracted
by the same geological conditions or their presence may be betrayed by the presence of downstream
industries. Similarly government services will locate in predictable locations such as regional
capitals or following central place theory (Christaller, 1933). However, such explanations align
poorly with the leading explanation for the principle of relatedness, namely, that the reason why we
observe related diversification is that related industries share similar capability requirements. The
principle of relatedness would instead reflect also other forces than capabilities. Alternatively, we
could stretch the concept of capabilities beyond its common meaning. However, this would make
the term less discerning: we typically think of a capability as something that a city can develop
through investments and learning, not as something that is predetermined by its location.

5.3 Related variety or relatedness?

A particularly important specification choice turns out to be whether to base density on continuous
information on industries’ prevalence in a city as opposed to binary information on their presence.
This finding is more than a mere technicality. It has important implications for our understanding
of the principle of relatedness. To see this, note that, if in eq. (1) we use continuous prevalence
information, density quantifies the size or mass of related industries in the city, reminiscent of
Marshallian externalities (Rosenthal and Strange, 2004). In contrast, if we use binarized (presence)
information, density becomes a proximity-weighted count of related industries. This emphasizes
the diversity of activities in a city, reminiscent of Jacobs externalities and related variety benefits
(Frenken et al., 2007).

Now, does the principle of relatedness reflect benefits of related variety or of related mass? To
analyze this, we construct two versions of our density measures that only differ in whether they use
continuous prevalence or binarized presence information. Because performance also depends on
the relatedness matrix used, we run separate regressions for each type of productive unit used to
calculate relatedness.

Results in Table 8 offer a surprisingly clear verdict. Regardless of whether we predict employment
levels or growth rates, only the density that uses continuous information on the prevalence of
an industry in a city is positively and significantly associated with employment and employment
growth.15 This finding may explain why the positive effects of related variety on economic development
in Frenken et al. (2007) have sometimes proved hard to replicate. For instance, seven out
of thirteen studies reviewed by Content and Frenken (2016) report mixed support for the related
variety hypothesis. Although a full analysis of this is beyond the scope of this paper, our analysis

15Table G.2 of Appendix G corroborates this finding, using our preferred continuous specification, where “continuous”
refers to the way in which we calculate relatedness, not density.

(a) employment levels

(b) employment growth

Figure 5: Out-of-sample performance by sector.
Plots show
−

, with

the out-of-sample
2 of specification  and

of the baseline specification. Each
observation in the scatterplots represents a specification in our specification grid, with its performance in
the overall sample on the horizontal axis and in a specific subsample on the vertical axis. Panel 5a refers to
performance in predicting employment levels, panel 5b in employment growth.

suggests that previously reported related variety effect may, in fact, be due to omitted-variable bias:
because related variety studies don’t control for related mass effects, they may erroneously have
attributed the effect of relatedness to related variety.16

6 Policy implications

Because the principle of relatedness helps identify promising diversification paths, it has started
to play an important role in regional development policy frameworks (e.g., Balland et al., 2019;
Boschma et al., 2022; Hidalgo, 2022; Rigby et al., 2022), with the European Union’s Smart
Specialization policy as a leading example. These frameworks often use industry space networks
to help policy makers prioritize certain industries over others. For instance, Balland et al. (2019)
argue that relatedness proxies how costly it would be for a region to develop a specific industry.
They submit that, because related industries (presumably) share many capabilities, moving into
industries that are closely related to a region’s existing industries economizes on the number of new

16Note that related variety studies typically estimate effects at the aggregate level of cities, not industries within
cities. Controlling for relatedness would therefore require measures of industrial coherence as in Teece et al. (1994).

Establishment Firm City Country
Employment levels
density 0.574*** 0.533*** 0.650*** 0.518***
(0.0278) (0.0332) (0.0469) (0.0382)
density -0.0863* -0.171*** -0.105 -0.0518

(0.0382) (0.0501) (0.0633) (0.0425)
 384705 384705 384705 384705

2 0.721 0.711 0.724 0.706
Employment growth
density 0.00748*** 0.00893*** 0.0104*** 0.00301

(0.00121) (0.00130) (0.00172) (0.00154)
density 0.00371* -0.00109 0.000989 0.00391

(0.00188) (0.00168) (0.00218) (0.00201)
 245395 245395 245395 245395

2 0.068 0.068 0.072 0.065

Table 8: Related variety versus mass of related activity.
Standard errors in parentheses, *:  < 0.05, **:  < 0.01, ***:  < 0.001. Upper panel: regression analysis
of employment levels, controlling for industry and city size effects. Lower panel: regression analysis of
employment growth, controlling for mean reversion, industry and city size effects. The coefficients reflect
the effects of density based on relatedness measured in the productive units listed in the columns, where
density uses continuous information on an industry’s prevalence in a city, and density binarized
information on whether or not an industry is significantly present in the city. For results based on our
preferred continuous specifications, see Table G.2 in Appendix G.

capabilities the region needs to develop.

Our results in section 4 support such an interpretation. However, just because it is easy to
develop an industry does not mean that it is attractive to do so. Therefore, most authors complement
information about inter-industry relatedness with information that captures how attractive an
industry is. For this purpose, different alternatives have been proposed. For instance, Balland et al.
(2019) and Rigby et al. (2022) suggest that regions should try to move into nearby industries that
are complex. Complex industries require many capabilities and are therefore somewhat shielded
from competition from other regions. By developing closely related complex industries, regions
can economize on capabilities, while benefiting from the barriers to entry that characterize these
industries.

However, this approach has several drawbacks. First, because most capabilities are hard to
observe, determining the complexity of an industry is not straightforward. Balland et al. (2019) and
Rigby et al. (2022) rely on the so-called economic complexity index (ECI, Hidalgo and Hausmann,
2009), which infers complexity from which cities host which industries. Under certain assumptions,
the ECI ranks industries by the technological sophistication they require (Schetter, 2019; Yildirim,
2021). However, Mealy et al. (2019) show that, more generally, the ECI can be interpreted as
the best one-dimensional representation of a “location space”, a network that links locations that
host related industries. This means that, by construction, low complexity regions will be close
to low complexity industries, and high complexity regions to high complexity industries. As a

consequence, the two axes on which the policy framework in Balland et al. (2019) is based –
relatedness and complexity – are not independent. Finally, McNerney et al. (2021) show that the
ECI can also be regarded as a city’s position along a long-run direction of transformation that is
consistent with the short-run diversification patterns described by the principle of relatedness. This
debate shows that the interpretation of complexity as a measure of desirability needs to be qualified.
One solution is to not overly rely on the ECI when determining the desirability of industries.

For instance, Hidalgo (2022) argues that the desirability of an industry depends on policy priorities.
Although these priorities may include productivity and employment growth – which are related
to complexity – they may also reflect other objectives, such as reducing inequality or a region’s
carbon footprint. Furthermore, Hausmann and Klinger (2009) propose combining the ECI with
information on an economy’s productivity to determine whether this productivity fully reflects the
complexity of the economy’s industrial base. If productivity falls short of what would be expected
based on the economy’s ECI, there should be scope for raising productivity without diversifying into
new activities. In this case, policy should focus on increasing the efficiency with which capabilities
are deployed. Only once productivity exceeds the levels implied by the city’s industry mix does
further diversification become necessary.

Another solution is to change how the principle of relatedness is used to support policy making.
Such an approach would also help overcome three other drawbacks of extant policy frameworks that
emerged from our specification search. First, as shown in section 5.2, the principle of relatedness is
unlikely to be exclusively driven by capabilities. Most authors acknowledge this either implicitly or
explicitly and list a variety of issues that should be considered in smart specialization policies, such
as institutions (Grillitsch, 2016) and entrepreneurship (Coffano and Foray, 2014; Hausmann and
Rodrik, 2003). Second, as noted in section 5.1 about the lack of interpretability of predictions, even
if capabilities were its main driving force, the principle of relatedness still does not provide insights

into which capabilities hold back a city’s development. Third, as shown in Table 5), the principle
of relatedness is much better at predicting how large an industry should be in a city today than how
much it will grow or shrink in the future: the out-of-sample
in predictions of employment levels

is about a factor ten higher than in predictions of employment growth. To further illustrate these
points, we examine how the principle of relatedness could be used to prioritize candidate industries
in practice.

Selecting industries for growth spurts

To make matters concrete, we assume that policy makers are particularly interested in identifying
industries that are likely to undergo growth spurts, where we define growth spurts as industries
with   < 0.25 in a city in 2011 that jump to   > 1 in 2019. To identify likely candidates for
such growth spurts, we rely on the principle of relatedness to predict industries’ local employment
in 2011, using our preferred binary specification, with city-based relatedness. The residual of
this regression tells us for each city-industry combination by how much employment exceeds the
predictions of the principle of relatedness. Positive residuals suggest that the industry is “too big”,
negative residuals that it is “too small”. As a consequence, the smaller (more negative) the residual
is, the greater a local industry’s presumed growth potential will be.

Figure 6 evaluates how accurate the guesses that we provided to our imaginary policy makers
were. The horizontal axis bins all city-industry observations by their estimated residuals. The
vertical axis shows which share of local industries in each of these bins undergo growth spurts.

Deep Sea Foreign Transportation Of Freight in
Tucson, AZ (-3.23) and Albuquerque, NM (-2.91);
Gold and silver ores in Pittsburgh, PA (-4.99)

entry probabilty

residual (more negative = higher expected growth rate)

Figure 6: Identifying candidates for growth spurts.

Share of city-industry combinations that undergo a growth spurt. The horizontal axis bins observations
based on the residual of a regression that predicts the size of an industry in a city. The more negative this
residual is, the more the principle of relatedness would predict the industry to grow.

Results are somewhat mixed. Our advice would certainly have helped policy makers avoid
industries with abysmal growth potential: very few industries with large positive residuals exhibited
growth spurts. However, if the goal was to pick winners, Fig. 6 offers a cautionary tale: even in
local industries with very large negative residuals, the likelihood of growth spurts is just marginally
above average (3.36% against 2.68%).

Why may this have happened? A possible explanation is that the very fact that industries are
small in spite of being closely related to the wider local economy signals that these industry face
some (unobserved) hurdles. After all: why, if it were so easy to develop the industry, has the
city not done so yet? This suggests leveraging the principle of relatedness for something other
than predicting future development paths. Instead, the principle of relatedness may help detect
anomalies – industries that are active in a region that according to the principle of relatedness
shouldn’t be and industries that are not active, while the principle of relatedness predicts they
should be.

Anomaly detection and Growth Diagnostics

A policy framework that illustrates the value of anomaly detection is Growth Diagnostics (GD,
Hausmann et al., 2008b). GD starts from the position that for economic development to happen,
many things need to be in place. Applied to industrial development in cities, this means that for an
industry to be productive in a city, it needs access to a large number of complementary factors. For
instance, to flourish, industries need a highly skilled and diversified workforce, but also functioning
infrastructure and utilities, effective institutions, risk-taking entrepreneurs and so on. If one of

these factors is in low supply, expanding any of the other factors is unlikely to lead to growth until
the initial bottleneck is resolved. To find these bottlenecks, Hausmann et al. (2008a) propose a set
of diagnostics tools that aim to identify binding constraints to growth.17

We propose that industry spaces can be a useful addition to this toolbox: although the principle
of relatedness may not very accurately identify growth candidates, it reliably pinpoints which
industries are surprisingly small or large. Instead of assuming that industries that are too small
need to be kick-started by policy prioritization, a more prudent approach would first scrutinize the
anomalies that the principle of relatedness detects in a city.

To illustrate this, we added some examples in Fig. 6 of city-industry combinations with –
apparently – high growth potential. These examples were not picked at random. On the contrary,
it is quite obvious that Phoenix (AZ) and Albuquerque (NM) are unlikely to develop deep-sea
transportation activities, and that opening gold mines in Pittsburgh is probably no promising
proposition either. Instead, these high-growth candidates are better understood as anomalies that
point to binding constraints to development. In Phoenix and Albuquerque, a prominent constraint is
lack of coastal access, in Pittsburgh, lack of gold deposits would explain the city’s poor performance
in gold mining.

On the other hand, some industries that are deemed far too large for a city are still unlikely to
shrink. For instance, the over 15,000 employees in Research, development and testing in Knoxville
(TN) represent a very large, positive, anomaly. However, this anomaly is solidly anchored in the
city by the presence of the Oak Ridge National Laboratory (ORNL). This research institute has deep
roots in the region and is financed by the federal government as part of Department of Energy’s
system of national research labs. It is therefore unlikely to leave the city. As a consequence, the
fact that Research, development and testing is too large according to the principle of relatedness
should not be interpreted as a risk for Knoxville, but rather as an opportunity: the city is likely
to be able to attract related industries that are synergistic with ORNL’s work, some of which are
already present, such as Laboratory apparatus and analytical, optical, measuring, and controlling
instruments and Engineering, architectural and surveying services.

The voice of absent industries

Most anomalies will be harder to explain than the examples listed above. Instead, they require
further investigation. The aim of such investigations is to understand which constraints hold back
industries’ growth in a city. This may involve further statistical analysis, surveys or interviews with
private sector representatives. However, the most binding constraints are often those that prevent
an industry from locating in a city altogether. Precisely here is where policy makers struggle most
to learn about how to lift such constraints: the industries that are absent typically have no “voice”
in the city, nor do they generate any data (e.g., requests for permits, vacancies, profitability reports)
in local administrative records. By highlighting anomalies, the principle of relatedness identifies
which absent industries merit further analysis. Policy makers can then invest in targeted analysis,
such as approaching firms in these industries outside the city to ask what prevents them from
moving to the policy maker’s city.

17These diagnostic tools try to infer missing factors by observing the behavior of economic actors. In particular, if
certain factors are absent, firms and other economic actors will try to find workarounds. Observing these workarounds
provides important clues for policy makers about development bottlenecks in their economies.

By focusing less on which activities to support and which not, anomaly detection circumvents
the risks associated with picking winners. More importantly, however, using the principle of
relatedness as a diagnostic tool can help understand what kind of capabilities are missing in a city.
Using several relatedness matrices – each focusing on a different type of economies of scope – can
help further triangulate these missing capabilities.

At the same time, the principle of relatedness remains useful in policy prioritization. After all,
given that the principle of relatedness predicts quite well which industries will not exhibit growth

spurts, it may still help prioritize (or, better, deprioritize) growth candidates. For instance, the
rankings of industries derived from the principle of relatedness are apolitical and objective. This
can be used to put a check on the power of well-funded lobbies and vested interests. Anomaly
detection should therefore be considered as a refinement, not replacement, of existing policy
frameworks.

7 Discussion and conclusion

The principle of relatedness posits that diversification and growth trajectories of cities are predictable:
cities typically grow by developing and expanding industries that are closely related to
their current portfolio of industries. We have shown that the principle of relatedness is robust across
a wide set of specifications, although there are substantial differences in predictive performance
and interpretability across these specifications. Beyond performance differences, different specifications
can be seen as testing different “flavors” of the principle of relatedness. As a result, our
specification search also yields insights into the mechanisms behind the principle of relatedness.

First, different types of productive units combine different industries, resulting in different types
of relatedness. For instance, establishment and firm portfolios exhibit relatedness patterns that
conform closer to the sectoral classification system than city and country portfolios. Furthermore,
co-occurrences of industries in establishments and firms are strongly shaped by how similar the
mix of occupations of different industries is. In comparison, value-chain linkages seem much
less important drivers of co-occurrences. Moreover, co-occurrence patterns in cities and countries
follow neither human capital nor value chain links very closely. As a consequence, industry spaces
– and the industry clusters derived from them – are typically more intuitive and readily interpretable
when based on establishment or firm portfolios compared to city or country portfolios. At the same
time, both city-level and firm-level relatedness matrices perform well in predicting a city’s growth
trajectory. This suggests that the best compromise between interpretability and predictiveness is
provided by firm-based relatedness matrices.

Second, when it comes to measuring density, we show that measures that are based on the mass
of related industries in a city outperform measures that are based on the variety of related industries.
This suggests that the principle of relatedness is closer related to Marshallian (i.e., specialization)
than Jacobs (i.e., related variety) externalities.

Third, the leading explanation for the principle of relatedness is that, by moving along trajectories
of related diversification, cities can limit the number of new capabilities they need to acquire.
However, this raises a puzzle: why is the principle of relatedness also predictive in sectors where
capabilities play no primary role in location decisions, such as public services, resource-based
industries and nontraded services? A capability-based explanation of the principle of relatedness
can only be salvaged if we were to expand the notion of capability far beyond its common meaning.

For instance, capabilities would have to include aspects that are hard to change, such as a city’s
geological conditions or population size. Related to this, we find that the principle of relatedness
does not always provide plausible predictions of which industries will grow in a city. In fact, the
principle of relatedness seems better suited to identify industries that are least likely to grow than
those that are most likely to do so.

Although none of this invalidates the principle of relatedness, it suggests that relatedness
patterns should be interpreted with caution: inter-industry relatedness does not necessarily reflect

shared capabilities. Indeed, understanding why industries colocate is an important emerging area
of research (e.g., Diodato et al., 2018; Ellison et al., 2010). In light of this, using the principle of
relatedness to prioritize industries in industrial policy may be useful, but not without risks. A more
conservative approach uses the principle of relatedness to detect anomalies in a city’s industrial
portfolio. In some cases, these anomalies will be due to missing capabilities, in other cases, they
may point to other reasons that hold back a city’s development. In either case, these anomalies
reveal binding constraints to growth. We have proposed that such anomaly detection is best used
as a component of a broader diagnostics approach. Such an approach would complement existing
frameworks that help policy makers navigate the trade-off between feasibility and desirability of
future development trajectories by focusing on which capabilities a city is lacking and what kind
of public policy would help overcome existing development bottlenecks.

Limitations and future research

Some limitations of our study stand out. First, we have focused on the principle of relatedness
in economic geography. That is, we studied its performance in predicting the presence and
growth of industries in cities. This choice may explain the exceptional performance of city-level
colocation-based relatedness matrices. Future research could analyze specifications and predictive
performance of the principle of relatedness applied to growth and diversification in establishments,
firms and countries.

Second, in spite of covering many important elements, specifications can be improved in
other ways. For instance, we did not consider set-based distance metrics, such as the Jaccard
distance. Similarly, when residualizing industry-unit size data, we only considered industry and
unit size, leaving aside other characteristics, such as diversity or productivity. Finally, to keep
our estimation framework computationally feasible and allow for millions of repeated analyses, we
only explored OLS regressions. Future research could analyze the statistical implementation of our
model specifications.

Third, our results rely on a single database that was not originally intended to offer a representative
depiction of the world economy, although it reliably describes the US economy. Further
analysis in countries other than the U.S., using, for instance, administrative datasets – many of
which record establishments, firms, industries and locations – could help corroborate or falsify the
findings in this study.

Finally, our analysis focused on industrial development and growth in cities. However, it can
be readily extended to technological and scientific development using patent data or scientific
publication data. In both datasets, co-occurrences of technologies or academic fields can be studied
at different levels of aggregation: from patents or journal articles to individuals, organizations,
cities and countries. It would be particularly interesting to learn how these spheres interact by
studying co-occurrences across domains. This would shed light on how diversification dynamics

interact across science, technology and the economy.
