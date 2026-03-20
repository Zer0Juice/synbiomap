---
source: 2025_The_Coherence_of_US_cities.pdf
pages: 23
extractor: pdftext
tokens_raw: 16185
tokens_compressed: 10471
compression: 35%
---

The Coherence of US cities

Simone Daniotti1,2,*, Matte Hartog ´

, and Frank Neffke1

1Complexity Science Hub Vienna, Vienna, 1080, Austria
2Vienna University of Technology, Informatics, Vienna, 1040, Austria

3Growth Lab, Harvard Kennedy School, Harvard University, Cambridge, MA 02138, USA
*daniottisimone@gmail.com

ABSTRACT

arXiv:2501.10297v1 [physics.soc-ph] 17 Jan 2025

Diversified economies are critical for cities to sustain their growth and development, but
they are also costly because diversification often requires expanding a city’s capability
base. We analyze how cities manage this trade-off by measuring the coherence of
the economic activities they support, defined as the technological distance between
randomly sampled productive units in a city. We use this framework to study how the
US urban system developed over almost two centuries, from 1850 to today. To do so,
we rely on historical census data, covering over 600M individual records to describe the
economic activities of cities between 1850 and 1940, and 8 million patent records as
well as detailed occupational and industrial profiles of cities for more recent decades.
Despite massive shifts in the economic geography of the U.S. over this 170-year period,
average coherence in its urban system remains unchanged. Moreover, across different
time periods, datasets and relatedness measures, coherence falls with city size at the
exact same rate, pointing to constraints to diversification that are governed by a city’s
size in universal ways.

1 Significance Statement

This study analyzes the nature and evolution of the economic coherence of cities. Much is
known about the consequences of having a diversified urban economy, but we know little
about how wide a range of activities a city can sustain. Here, we propose a measure of
coherence that allows us to study changes in the breadth of economic activities in US cities
over the course of 170 years. We find that, as the US economy transformed, economic
activities became distributed across its urban system in ways that preserved coherence
across cities. Moreover, coherence falls with city size at a rate that is constant across time
periods and data sets. These findings suggest that the US urban system faced universal
constraints along its development trajectory. This raises new types of questions about
urban transformation and suggests that policymakers should take the constrained nature of
urban transformation into consideration when devising interventions and plotting future
development trajectories for their city.

2 Introduction

Diversification is pivotal to economic development and cities’ capacity to generate prosperity
for their inhabitants1–3
. Diversified economies are less exposed to idiosyncratic
sector-specific shocks4
, have a broader capability base from which to develop new ecoContribution
Statement
S.D. and F.N.: Conceptualization, Methodology, Writing – Original Draft.
S.D.: Investigation, Formal analysis, Visualization, Software.
F.N.: Supervision.
M.H. and S.D.: Data Curation.
All authors: Writing – Review and Editing.
nomic activities5, 6
and are better positioned to innovate7–10. These and other consequences
of diversification have been studied extensively. However, we know much less about

how much diversity cities can manage, how this has changed over time, and how cities’
capacity to do so is affected by their size. Here, we address these questions by leveraging
large-scale micro-datasets that allow us to describe the evolution of the US urban system
and the distribution of technological and economic activities across its cities almost from
its inception to the present day. In particular, we study how coherent the activity mix of
a city is, in terms of the expected relatedness or technological proximity between two
randomly sampled productive units in the city. The less coherent a city is, the broader
the capability base required to support its activity mix will be. To do so, we develop
a measure of coherence that is insensitive to economic classification systems and the
exact measurement of relatedness. Studying the long-term evolution of the US urban
system through this lens reveals that coherence falls with city size at a rate that stays the
same across decades and datasets, suggesting the existence of universal constraints to
diversification related to the size of a city.

A major challenge to studying the long-run transformation of urban economies is that
economic activities and the classification systems to describe them change drastically
over longer periods. Moreover, most existing approaches, which describe the breadth of
activities in cities in terms of related and unrelated variety, tend to mechanically rise with
city size11, such that larger cities will, by construction, be more diversified. To address

these challenges, we construct a measure of coherence that is a priori unrelated to city
size and insensitive to changes in classification systems.

We use this coherence to study the long-run evolution of the US urban system between
1850 and today. To do so, we combine several large-scale micro-datasets, from historical

census data that cover hundreds of millions of individuals in the 19th and 20th century to
millions of patent records that describe the technologies used by US inventors between

1975 and 2020. These datasets cover different periods, different definitions of the US
urban system – which grew from 500 cities in 1850 to 900 cities today – and different
types of activities, such as occupations, industries, and technologies.

Set against this heterogeneity, our analysis yields two surprising findings. First, the
average coherence of cities in the US urban system remained constant in datasets that
stretched over 170 years and across activity types. This stability is remarkable, given the
drastic economic transformation that took place in this period, including the transition

from agriculture to first manufacturing and then services, the rise and fall of the Rustbelt,
and the emergence of today’s technology hubs. Moreover, individual cities do undergo
drastic structural change, as in Detroit’s rise and fall with the fortunes of its automotive
industry and Boston’s transformation from a port city to a city of higher education12. The
fact that, in spite of such transformation, coherence remains unchanged therefore suggests
that, as cities transform, they, on average, do so in a way that preserves the coherence
among their (changing) activities along the way. Second, we uncover a universal relation
between coherence and city size: the elasticity of coherence with city size is constant, at
about -4%, across time periods and activity types. That is, moving from smaller to larger
cities, the mix of activities broadens in a predictable way, such that doubling the size of a
city translates roughly into a 4% decrease in coherence. This holds not just true for the
urban system as a whole, but also for the urban system on the West Coast of the US, which
remained relatively disconnected from the eastern U.S. until the early 20th century and
whose development we can trace in its entirety, starting from the mid 19th century. To help

understand these patterns, we postulate that larger cities can maintain wider capability
bases, which should allow them to develop less coherent activity portfolios, a logic we
develop more formally in a model of collective learning in which cities’ workers balance

imitation and innovation.

Conceptually, our work relates to the framework of economic complexity5, 13, 14. The
literature on economic complexity assumes that economies mobilize capabilities to produce
output. Although capabilities are treated as hidden, unobserved variables, different
products and services are generally assumed to require different capabilities. This makes
it costly to produce a wide variety of outputs because this will require a broad set of
capabilities. Economies can save on the number of capabilities by focusing on sets of
closely related activities. Accordingly, our coherence metric can be regarded as an attempt

to assess the breadth of a city’s capability base by analyzing how related different productive
units in the city are to one another. The less related two randomly sampled units on
average are, the more coherent the city and the broader its capability base will be.

The notion of coherence itself has been widely studied at the firm level in strategic
management15, 16 as reviewed in17, and more recently in research on economic complexity18,
19. Scholars in Evolutionary Economic Geography (EEG) then took the concept
of coherence to the regional level. Our work relates most closely to papers in this latter
tradition6, 20. However, we also take inspiration from information-theory-based metrics
of diversity21–23 to construct a readily interpretable metric that defines coherence as the

expected relatedness – for instance, in terms of cognitive or technological proximity –
between two randomly sampled productive units (e.g., workers) in a city.

Finally, our study relates to a variety of academic fields that have documented striking
relationships between diversification and economic outcomes in cities. First, economic
geographers who study regional and urban diversity highlight its role in innovation8
by facilitating Schumpeterian new combinations24, agglomeration externalities25–27 and
the path-dependent nature of regional diversification7, 28–30. Second, literature on urban
scaling1, 31–34 explores how economic activities scale with city size, concentrating in
large cities35–38, and how occupational diversity relates to economic productivity and
social network structures31, 39. However, these bodies of research tend to focus on the
consequences of cities’ activity mixes, not on what determines the breadth of the activity
mix that cities can sustain in the first place. Moreover, most work analyzes cross-sections

or short panels of cities in which activities are recorded in stable classification systems.
As a consequence, they study cities and urban systems over years, instead of the decades
and centuries over which their transformation typically unfolds.

3 Results

3.1 Data

Our analysis draws from three different data sources. First, we use decennial US censuses
for the period 1850-1940. This dataset covers over 600M individual records and allows
us to analyze changes in the occupational composition of between 550 and 900 cities
in the U.S. in terms of 250 different occupations. Second, for the period between 2002
and 2022, we use data from the US Bureau of Labor Statistics (BLS) on employment by
occupation for over 800 occupations in 350 metropolitan areas. For both data sources, we
concentrate on occupations that are likely to produce tradable output whose geographic
distribution is driven by the availability of relevant capabilities, ignoring occupations that
mainly cater to the demand of the local population, such as bakers, teachers, and nurses
(see SI, sec. S1). Third, we aggregate data from the US Patent and Trademark Office on
over 8M patents between 1980 and 2020 to city-technology cells, distinguishing between
650 technological areas and 900 cities. Together these datasets describe the occupational
and/or technological composition of US cities between 1850 and today, except for the

decades of 1890 for which a fire destroyed census records and of 1950, 1960 and 1970,

for which neither comprehensive employment nor patenting information exists at the city
level. Details on cleaning and geocoding are provided in the Methods section.

3.2 Defining Coherence
We define our metric of economic coherence in terms of the relatedness between the
economic activities in which productive entities in a city, such as workers, inventors or
firms, are active. Relatedness has been measured in various ways and is often interpreted
as a measure of cognitive or technological proximity. To show that our findings are
not dependent on the exact definition of relatedness, we explore various relatedness
metrics (see SI, sec. S2). First, using matched census records, we construct a measure of
skill-relatedness40 that connects occupations that exhibit exceptionally large labor flows
between them. Second, in the BLS data, we derive measures of relatedness that express
the extent to which two occupations are found in the same cities or industries. Third, in
the patent data, relatedness expresses the degree to which two technologies co-occur on
the same patents.

D E P

=

(b)

C

D*E

(a) (c)

Figure 1. Measuring coherence. (a) Proximity (P). Stylized depiction of (no ×no)
proximity matrix as a network of no activities (here: occupations) connected by edges that
reflect their relatedness. (b) Density (D). The (nc ×no) density matrix reflects
occupations’ “fit” with each of the nc cities in our data. It is defined as the expected
relatedness to all other occupations in the city, when the other occupations are sampled
with probability p =
Eco
∑l̸=o Ecl
, where Eco captures the employment of city c in occupation o.
Dropping own-occupation contributions, element Dco is calculated by multiplying a
normalized row c of the (nc ×no) employment matrix E with column o of matrix P, while
omitting element o from both vectors. (c) Coherence. Estimated as the mean relatedness
between workers in different occupations in the same city, coherence is calculated as DE¯,
where ¯. indicates row-normalization by dividing all elements by corresponding row-sums.

Fig. 1 illustrates how we estimate coherence. We first collect relatedness estimates for
all pairs of activities in matrices P. Next, we define coherence as the expected relatedness
between two randomly sampled units, such as workers or patents, conditional on both
units being sampled from the same city c1 = c2 = c. This involves two steps. The first
step assesses how related an activity is to the rest of the urban economy. This measure
is known as the activity’s density in the city5, 41. The second step averages this density

across all activities.

To make matters concrete, we focus on the case of workers and their occupations.
Elements Po1,o2
now denote the proximity between occupations o1 and o2. Furthermore,
because the relatedness of an occupation to itself is undefined – and to avoid coherence
from picking up individual occupations’ own geographical concentration – we condition
this expectation on o1 ̸= o2, where o1 and o2 denote the first and second sampled worker’s
occupations. This yields the following expression:

Cc1,c2 = E(Po1,o2

′

|c1 = c, c2 = c

,o1 ̸= o2) (1)

Elements of matrix C refer to pairs of cities. Coherence estimates are on C’s diagonal,
where the randomly sampled workers come from the same city. The off-diagonal elements
contain the expected proximity between randomly sampled workers from different cities.
These elements express how similar these cities are in terms of their activity mix. Expanding
matrix E with a time dimension, such that it records the employment for a city in a
given year in its rows, allows quantifying urban transformation as the expected proximity
between randomly sampled workers from the same city, but at different points in time.
The smaller this expected proximity, the more radically a city transforms.

Note that coherence is expressed in the same units as relatedness. Because relatedness
definitions may differ across datasets and over time, we normalize coherence estimates
by dividing them by a baseline that reflects the coherence of the US as a whole, i.e., the
expected relatedness between workers randomly sampled from the entire US economy.
The resulting ratio is independent of the unit in which relatedness is expressed and
captures how much more or less related workers in the same city are than workers in the
US economy as whole.

3.3 Structural Transformation of the US urban system
The US population grew from about 23 million inhabitants in 1850 to 132 million inhabitants
in 1940 and 332 million inhabitants in 2022. With this growth in population, its
economic structure underwent drastic transformation. Whereas in 1850, only about 15%
of the population was urban and about 60% of the working population was employed in
agriculture, by 1940, 56% of the US population lived in cities and around 25% of workers
worked in manufacturing. Nowadays, 80% of Americans live in urban areas and services
have become the dominant sector, accounting for 70% of all jobs.

Despite such rapid transformation, Fig. 2e shows that cities’ average coherence has
remained constant for almost two centuries. The graph depicts the average coherence
across cities in census data for the period 1850-1940 (blue line), BLS data for 2002-2022
(orange line), and patent data for 1980-2020 (green line). Across all datasets, coherence
does not change in a statistically significant way. Moreover, in terms of occupational
coherence (blue and orange lines), there is no manifest change in average coherence
between the towns and cities of 1850 and the urban areas and metropoles of today.
This implies that, although cities substantially transformed their economies, they did so,
maintaining a constant level of coherence. That is, as cities moved away from their past
activities, they, on average, retained a constant level of “compactness”.

3.4 Coherence and city size
Although the urban system’s average coherence remains constant, this does not necessarily
hold true for individual cities. In general, diversity rises with city size42. Similarly,
coherence falls with the city size. To study the relationship between coherence and city
size, we regress the logarithm of coherence on the logarithm of the total number of workers
in the city. Fig. 3a shows that the relation between coherence and city size is downward

(a) Employment in 1850 (b) Employment in 1900 (c) Employment in 1940

0.0
0.5
1.0
1.5
2.0
2.5
3.0
3.5
4.0

Year
0.0
0.2
0.4
0.6
0.8
1.0
1.2
1.4

USPTO Coherence

Coherence

census occs.
BLS occs.
patent techs.

transf. vis-à-vis 1920
correl. vis-à-vis 1920

Figure 2. Structural Transformation at Constant Coherence.
Urban employment in the U.S. in (a) 1850, (b) 1900 and (c) 1940. Marker area is proportional
to the number of employees in each city. The 1850-1940 period covers an important
part of the formation and development of the US urban system in which the US went
from a mostly rural to an advanced manufacturing and services economy. (d) Structural
Transformation. Mean correlation between cities’ occupational portfolios in different
decades with their portfolio in 1920 in blue, and mean structural transformation vis-à vis
1920 in orange. Calculations are limited to cities that exist in both decades and correlations
are calculated as ρ
c
t,1920 = corro∈O (Eoct,Eoc1920), where Eoct denotes the employment in
occupation o, city c and year t with O the set of occupations. Correlations are subsequently
normalized by their country-level counterparts: ρt,1920 = corro∈O (Eot,Eo1920),
where Eot = ∑c Eoct. Ratios ρ
c
t,1920
ρt,1920
are depicted along the vertical axis. Structural transformation
is calculated as in eq. (9) and normalized by overall US-level transformation
between t and 1920. (e) Coherence. Mean coherence across US cities. Coherence is
calculated as in eq. (1) using occupation data from the census (1850-1940, blue line) and
BLS (2002-2022, orange line), and patent data from the USPTO (1980-2020, green line).
Values are normalized by dividing by system-level coherence. Confidence bands indicate
95% confidence intervals.

sloping. More surprisingly, the elasticity of coherence with respect to city size – the
slopes ∂ logCcc
∂ logEc
in Fig. 3a-3b – are statistically indistinguishable across datasets and time
periods (a Wald test for equality of slopes yields a p-statistic of 0.8) and close to -4%
(95% confidence interval: [-4.4%, -3.4%]). That is, when city size doubles, coherence
falls by approximately 4%. As shown in Fig. S3.1 of the SI, this contrasts with traditional
measures of urban diversity, whose elasticities with respect to city size change markedly
over the course of a century.

To help understand these findings, we develop a micro-simulation, where workers
either imitate existing workers or innovate and develop new capabilities (see sec. S4 of
the SI). In this context, a natural way to define coherence is the expected frequency with
which two randomly drawn workers in a city will have the same capabilities. Fig. 3c
shows that by covering just two essential aspects of collective learning – imitation and
innovation – this simple model is able to reproduce the functional form of the relation

between coherence and city size.

3.5 West-Coast

So far, our analysis has focused on the US urban system as a whole. While still relatively
small, by 1850 the eastern part of this urban system had already become somewhat
developed. The same is not true for the US West Coast. The population west of the Rocky
Mountains amounted to just 300,000 people in 1850. In 1848, San Francisco had no
more than 1,000 inhabitants, and the largest city in the region, Los Angeles, had 1,610
inhabitants, quickly surpassed in the following years by Sacramento. Moreover, in most
of the 19th century, the West Coast remained isolated from the rest of the US. Before the
construction of the Panama Canal in 1914, ships had to round Cape Horn to travel between
the Atlantic and Pacific Oceans and over land, mountain ranges acted as a significant
barriers, until the completion of the Transcontinental Railroad in 1869, which connected
the East and West Coast and fueled rapid urban growth and economic development along
its route. The US West Coast therefore offers a unique opportunity to study how an urban
system develops from scratch and then integrates into a larger, existing urban system.

The structural transformation of the West Coast unfolded very fast. Fig. 4d shows how
quickly its cities diversified: whereas, in 1850, they hosted just about 40% of existing
occupations related to tradable activities, by 1900, this number had risen to close to
90%. Even in this period of rapid diversification, average coherence of West Coast cities
remained remarkably constant and, notably, at levels indistinguishable from those in the
eastern US (Fig. 4e). Moreover, although the elasticity of coherence with respect to city
size (Fig. 4f) oscillates in the first 30–40 years – possibly due to imprecise measurement
in small populations – it thereafter converges rapidly to the same levels as observed in the
rest of the U.S.

4 Discussion
A diverse economy is of great importance for a city’s capacity to innovate, grow and absorb
adverse shocks. However, diverse economies require a range of different capabilities43
,
which are often expensive to acquire and maintain. This begs the question of how broad a
range of activities a city can sustain. To address this question, we have defined a city’s

coherence as the expected relatedness between randomly sampled productive units, e.g.,
workers or inventors, from the same city, while controlling for a nation-wide benchmark.
We interpret this coherence as a proxy for the breadth of the city’s capability base. This
allowed us to address challenges inherent in long-term analyses of economic structures of
cities, such as changing classification systems and distinguishing city-level change from
broader economy-wide trends, while also focusing on fundamental changes as opposed to
superficial shifts between closely related activities in a city’s activity mix.

Applying this framework to data sets that describe the mix of economic activities in
US cities over a 170-year time period uncovered important regularities. First, although
the US urban system has undergone substantial structural change, the coherence of cities

within this system has, on average, remained remarkably stable. This suggests that cities’
development trajectories are constrained: as cities transition from old activities to new
ones, they, on average, maintain a constant level of internal coherence.

Second, coherence decreases with city size at a universal rate. Across different time
periods, relatedness measures and activity types (industries, occupations and patented
technologies) the elasticity of coherence with respect to city size is constant at about
-4%. That is, coherence decreases by about 4% with each doubling of a city’s size,
implying that larger cities are able to support a broader set of activities. The constancy
of the point estimate of the relation between coherence and city size across periods and

(a) Coherence vs Population scatterplot

2 3 4 5 6
Population [Log]
1.0
0.8
0.6
0.4
0.2
0.0
0.2
0.4
Avg. Shared Capabilities [Log]

(b) Coherence slope

(c) Shared Capabilities vs Population scatterplot

Figure 3. Coherence versus Size. (a) Scatter plot of coherence versus city size.
Markers refer to cities in a specific dataset, blue: 1900 census, orange: 2012 BLS, green:
2000 patents. Lines represent best linear fits in each dataset. (b) Estimated elasticity of
coherence with respect to city size. Colors are as in panel (a). Shaded areas reflect 95%
two-sided confidence intervals, based on robust standard errors. The null hypothesis of
equal slopes cannot be rejected at any conventional level (p = 0.8) in an

equality-of-slopes Wald test. (c) Simulated coherence in a micro-simulation that balances
innovation with imitation (SI, sec. S4). City sizes are taken from the urban system of
1900 to mimic the blue scatter of panel a. The expected capability overlap, i.e., coherence,
drops with an elasticity that depends on the parameter that governs workers’ propensity to
innovate (see Fig. S4.1), which is calibrated to the observed elasticity of -4%,
corresponding to an innovation propensity of 3%.

(a) Employment West Coast

(b) Employment West Coast

(c) Employment West Coast

Year
Share of occupations
Eastern tradable
WC tradable
Eastern non-tradable
WC non-tradable
(d) Occupational diversity 1860
Year
0.0
0.2
0.4
0.6
0.8
1.0
1.2
1.4
1.6
Coherence
Eastern US
West Coast
(e) Coherence

Coherence-pop. slope

Eastern US
West Coast

Year
0.125
0.100
0.075
0.050
0.025
0.000
0.025
0.050
0.075

(f) Elasticity

Figure 4. US West Coast. (a-c) Employment in West Coast cities in 1850, 1900 and
1940. In 1850, the largest city on the West Coast is Sacramento. After the gold rush,
population growth shifts to other cities, such as Portland, Seattle, San Francisco and Los
Angeles. (d) Number of existing occupations as a share of all potential occupations in
Eastern US (blue) and on the West Coast (pink). Dashed lines refer to occupations in
non-tradable activities, solid lines in tradable activities. Whereas occupations in

non-tradables were already abundant on the West Coast in 1850, in tradable activities, less
than half of all potential occupations had been developed by then. (e) Coherence. Mean
coherence across US cities on the West Coast (pink) and in the Eastern US (blue).
Coherence is calculated as in eq. (1) and normalized by overall subsystem-level

coherence. Confidence bands refer to 95% confidence intervals. (f) Estimated elasticity of
coherence with respect to city size. Shaded areas reflect 95% two-sided confidence
intervals, based on robust standard errors. By 1920, after some initial fluctuations, West
Coast cities exhibit the same level of coherence and elasticity of coherence with respect to
city size as the remainder of the urban system.

contexts suggests there may exist universal constraints that govern urban diversification.
Interestingly, the estimated elasticity closely aligns with leading estimates of the urban
wage premium in the U.S., according to which wages rise by around 5% with each
doubling of city size44. Whether this is a coincidence or due to a connection between
coherence and labor productivity is an interesting question for future research.

Third, after an initial turbulent period, cities on the West Coast settle into the same
regularities as eastern US cities. The West Coast is an interesting case study, because
our data describe its development more or less from the birth of its urban system, when
geographical barriers initially still isolated it from the wider U.S.. In spite of this isolation
and the rapid structural transformation it underwent, cities on the West Coast come to
rapidly exhibit the same (constant) coherence and elasticity of coherence with respect to
city size as its counterparts east of the Rocky Mountains. This suggests that our findings
may generalize to other urban systems.

Our study has several limitations that can be tackled in future research. The first
involves theoretical explanations for the functional form and observed elasticity of -4%
for the relation between coherence and city size. In the SI, Fig. S4.1, we show that simple
probabilistic models of imitation and innovation can reproduce our findings. This points
to universality in collective learning as studied in the field of cultural accumulation45, 46
.
However, other explanations may exist. One example is regularities in the way division of
labor deepens with city size and gives rise to new specializations31. Given the invariance
across contexts and time of average coherence, as well as of its relation with city size,
plausible candidates should be independent of technology and other aspects of societies
that change on relatively short time horizons.

A second limitation is the macro-level focus of our work on average proximity between
a city’s workers. However, what may matter most is whether workers can find a critical
mass of closely related workers. Because large cities often consist of clusters of highly
related activities47, workers may be able to find a sizeable number of proximate workers
even in cities with low coherence. This can be studied by looking at relatedness quantiles.
For instance, one could calculate for each worker the 90th percentile of relatedness to
other workers in the city. Cities with low levels of mean coherence but high levels of 90th
percentile coherence would consist of disparate clusters of tightly related activities. This
could explain why coherence falls with city size: although workers in large cities often
find many workers in related activities, the wide variety of clusters they host lowers the
average relatedness captured by our coherence metric.

Finally, our findings have important implications for the broader discourse on regional
development and growth policy48. Such policy often focuses on fostering diversity in
cities7
and helping a city move into new economic activities to provide opportunities for
growth and to avoid lock-in49. However, our analysis suggests that the breadth of activities
a city can sustain is constrained by its size. Similarly, the fact that, as cities transform,
they maintain a constant level of coherence suggests that there are structural constraints
limiting the speed and trajectory of diversification. Therefore, diversification strategies
should first benchmark a city’s coherence against its size and analyze transformation
trajectories that would allow the city to maintain its internal coherence.

5 Methods

5.1 Data

Our analysis is based on three different datasets: US census records between 1850 and
1940, Bureau of Labor Statistics (BLS) data between 2002 and 2022 and United States
Patent and Trademark Office (USPTO) data between 1980 and 2020.

US census records. Census data are provided by the Integrated Public Use Microdata
Series known as IPUMS50. This dataset has approximately 650 million records of
responses to Census inquiries for every resident in the United States during the years 1850,
1860, 1870, 1880, 1900, 1910, 1920, 1930, and 1940 (the 1890 records were destroyed in
a fire). These records include essential details for our analysis such as each individual’s
name, occupation, industry, year and state of birth and place of residence. We focus on the
working population, which we define as individuals aged 15 to 65 for whom an occupation

of employment is recorded. We exclude individuals in occupational categories “Unknown”
or related to agriculture, given that the latter are not part of the urban economy.

Individuals were geocoded and linked across census waves by51. We aggregate
these data to the level of cities using point-in-polygon merges, where polygons are the
metropolitan and micropolitan areas defined by the US Census bureau in its TIGER/Line
Shapefiles (https://www.data.gov/). We use the urban shapes for the year 2020,
projecting them backward in time to maintain the same spatial definitions of cities. The
result is a dataset with employment for approximately 250 occupations in between 550
US cities in 1850 and 900 cities in 1940.

BLS data. The BLS data are taken from the BLS Occupational Employment Statistics
(OES) tables, available at https://www.bls.gov/oes/tables.htm. These tables
record the number of employees in approximately 800 occupations across about 350
US metropolitan areas. Furthermore, we use the BLS’ industry-occupation matrix, which
records the number of employees in occupation-industry cells to calculate relatedness
between occupations from their co-occurrence across industries.

Patent data. The USPTO dataset are obtained from PatentsView, https://www.
uspto.gov/ip-policy/economic-research/patentsview. We focus on
patents granted by the USPTO between 1980 and 2020, geocoding US inventors based on
their places of residence through point-in-polygon merges to TIGER/Line Shapefiles. We
aggregate patents to the city-technology level, distributing each patent proportionally to
the share of its inventors in each cell. This yields a dataset of (fractional) patent counts for
approximately 650 technologies in 900 cities.

Tradable and nontradable occupations. An important distinction exists between
economic activities that cater to the need of a city’s own population and those whose
output is traded with other cities. The former are called “nontradable” and include
occupations such as bakers, school teachers, doctors, retail workers, etc.. Demand for
nontradable activities is driven mostly by the size of the local population and its purchasing
power, such that employment shares in nontradable occupations are very similar across
cities. In contrast, tradable activities depend on the city’s productivity in these activities.
Examples include manufacturing activities, but also services sold to inhabitants of other
cities, such as investment banking, research and development or higher education.

Unlike a city’s nontradable activities, which tradable activities a city can develop
depends on its capability base. Consequently, the capability base of a city is best reflected
in its tradable activities and we therefore drop nontradable activities from our analysis
of a city’s coherence. In patent data, we consider all activities tradable, given that
patents protect inventions on the entire US market. When analyzing occupations, we
leverage the fact that nontradable activities essentially follow population and calculate
for each occupation how closely its distribution across cities follows the distribution of
the US population. That is, we calculate the correlation between two vectors, e⃗o, whose
elements, Eoc, contain the employment of occupation o in city c and⃗e, whose elements,
Ec. = ∑o Eoc, describe city c’s overall employment as a proxy for its population. This

yields the following nontradability score: NTo = corr(e⃗o,⃗e).

Fig. S1.1 in the SI shows that coherence estimates rise the more we limit the analysis
to tradable occupations in census and BLS data. In the census data, we observe a sharp
transition after removing 70% of the least tradable occupations.This shows that coherence
is mostly driven by tradable occupations. Although in the BLS data, we do not find a
specific transition point, we observe the same strong relation between tradability and
coherence. We therefore define tradable occupations in both census and BLS data as
occupations with NT < 0.7.

5.2 Proximity
The concept of proximity between economic activities is central to research on Economic
Complexity. In this field, economies are represented as networks of related activities5, 6, 52
,

where relatedness captures the degree to which different activities require similar capabilities.
When cities develop related activities, they can support a wide variety of such
activities with a limited set of capabilities. In this context, our coherence measure can
be viewed as a way to quantify a city’s (lack of) diversity, not in terms of its activities,
but of its capabilities. This approach resonates with research on diversity in ecosystems,
which often distinguishes between variety, balance and disparity22. We discuss the relation
between coherence and the metrics in this literature in the SI, section S3.
Relatedness can be measured in various ways41. For the census data, we base relatedness
on labor flows, i.e., on a count of how many individuals move from one occupation
to another between two consecutive census waves. To be precise, we assess to what extent
the labor flows between occupation o and o
′
are surprisingly large, using Pointwise Mutual
Information as a metric of surprise:

PMI(poo′) = log
poo′
po po
′

, (2)

where poo′ is the joint probability that an individual moves from occupation o to occupation
o
′
and po and po
′ are the marginal probabilities of moving out of occupation o and into
occupation o
′
. We estimate these probabilities by the obsersved relative frequencies. For
instance, we estimate poo′ as pˆoo′ =
Foo′
∑k,l Fkl
, where Foo′ is the observed labor flow from
occupation o to o
′
.

Often, authors draw a sharp distinction between relatedness and unrelatedness41, 53
.
Following recommendations in this literature, we define proximity as:

Poo′ =
(
PMI d(
Foo′
∑k,l Fkl
) if PMI d(
Foo′
∑k,l Fkl
) > 0,
0 otherwise

(3)

where Foo′ is the mean of the labor flow between two occupations o and o
′
across all pairs
of consecutive census waves and PMI d is estimated using the Bayesian approach in54. This
sets all negative elements of matrix P to zero. Furthermore, because the relatedness of an
activity to itself is ill-defined, diagonal elements of proximity matrices are ignored in the
definition of coherence (see below).

Replacing flows by co-occurrences, we can also derive estimates of proximity from
the frequency with which two occupations co-occur in the same industry or city. We
use city-level co-occurrences as an alternative proximity metric in our census data and
city and industry co-occurrences to produce two different proximity metrics in the BLS
data. In patent data, we calculate proximity from the frequency with which technology
codes co-occur on the same patent. Our results prove remarkably robust to changes in the
definition of proximity (sec. S2 of the SI).

5.3 Defining Coherence
We define coherence as the expected proximity between two randomly sampled workers,
conditional on the workers being from the same city and employed in different occupations.
Breaking down the calculation of coherence into two steps helps connect the coherence
metric to the literature on economic complexity5, 14, 55. This is illustrated in Fig. 2. First, we
calculate the weighted average proximity of a given occupation, o to all other occupations
in the city c. This quantity is closely related to what the economic complexity literature41

refers to as o’s density, Doc, in city c:

Pr(o2 = o
′

|c1 = c, c2 = c,o
′

Doc = ∑
o
′̸=o

̸= o)Poo′, (4)

which can be estimated as:

Eo
′c
∑o
′′̸=o Eo
′′c

Dˆ
oc = ∑
o
′̸=o

Poo′ (5)

Coherence, a city-level variable, is now simply the expected density across all occupations.
To calculate this, we construct the following matrix:

Cc1,c2 = E(Po,o
′|c1 = c, c2 = c
′
,o1 ̸= o2)

|c1 = c, c2 = c
′
,o ̸= o
′
)Poo′,
(6)

Pr(o1 = o|c1 = c, c2 = c
′
)∑
o
′
Pr(o2 = o
′

= ∑o

which can be estimated as the employment-weighted average density:

Eoc
∑o
′′ Eo
′′c
∑
o
′̸=o

Eo
′c
′
∑o
′′̸=o Eo
′′c
′
Po,o
′

Cˆ
c1,c2 = ∑o

(7)

Eoc
∑o
′′ Eo
′′c
Dˆ
oc′,

= ∑o

where Eco denotes the number of workers employed in occupation o and city c. A city’s
coherence is found on the diagonal of matrix Cˆ , which contains estimates of the expected

proximity between workers that were sampled from the same city. The average coherence
across the urban system, plotted in Fig. 2e, is calculated as the weighted average of the
diagonal elements of Cˆ , using cities’ overall employment as weights. Next, we rescale this

estimate by dividing by the analogous quantity for the US economy as a whole. That is
we combine all cities other than c into one unit such that the calculations in eq. (6) yield a
scalar. Confidence intervals are based on estimates of the standard errors of eq. (7), which
are calculated as follows:

σ(Cˆ
c1,c2
) =
vuut∑o
∑
o
′̸=o

σ(poo′)

Eoc1

Eo
′c2
∑o
′′̸=o Eo
′′c2

, (8)

∑o
′′ Eo
′′c1

where σ(poo′) is the Bayesian estimate of the standard deviation of the proximity between
occupations o and o
′54
.

The off-diagonal elements of Cˆ also have a useful interpretation: they can be regarded

as estimates of the proximity between two cities. We use this to quantify the amount
of structural transformation a city undergoes. To do so, we include into matrix Cˆ

observations for the same city at different points in time. This yields elements that

estimate the expected proximity between two workers that were sampled from the same
city, but in different years:

E
(t+τ)
o
′c2
∑o
′′̸=o E
(t+τ)
o
′′c2

Cˆ
(t,t+τ)
c1,c2 = ∑o
E¯
(t)
oc1 ∑
o
′̸=o

Poo′, (9)

where ¯. indicates row-normalization by dividing by row-sums. Values Cˆ
(t,t+τ)
c1,c2
, normalized
by the estimated average coherence in 1920, are shown in orange in Fig. 2d.
