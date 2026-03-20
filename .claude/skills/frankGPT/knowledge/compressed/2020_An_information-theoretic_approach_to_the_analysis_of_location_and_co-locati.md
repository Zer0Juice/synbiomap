---
source: 2020_An_information-theoretic_approach_to_the_analysis_of_location_and_co-locati.pdf
pages: 13
extractor: pdftext
tokens_raw: 14127
tokens_compressed: 11727
compression: 17%
---

An information-theoretic approach to the analysis of location and co-location patterns

Alje van Dam1,2,∗
, Andres Gomez-Lievano3

, Frank Neffke3

, Koen Frenken1

Abstract

We propose a statistical framework to quantify location and co-location associations of economic activities using informationtheoretic
measures. We relate the resulting measures to existing measures of revealed comparative advantage, localization and
specialization and show that they can all be seen as part of the same framework. Using a Bayesian approach, we provide measures
of uncertainty of the estimated quantities. Furthermore, the information-theoretic approach can be readily extended to move beyond

pairwise co-locations and instead capture multivariate associations. To illustrate the framework, we apply our measures to the colocation
of occupations in US cities, showing the associations between different groups of occupations.

arXiv:2004.10548v1 [stat.AP] 22 Apr 2020

Keywords: pointwise mutual information, Kullback-Leibler divergence, revealed comparative advantage (RCA), specialization,
localization, co-agglomeration

1. Introduction

pair of people from the same city, how much information does
the occupation of one of them provide about the likely occupation
of the other?

The recognition of differential specialization patterns lies at
the heart of economics since the works of Adam Smith and
David Ricardo. Economists studying task assignments (Roy,
1951, Sattinger, 1993), urban economies (Ellison and Glaeser,
1997, Ellison et al., 2010), or international trade (Balassa, 1965,

The information-theoretic basis that underlies the PMI ensures
that the framework is explicit about the null models, priors
and data-generating processes we assume. This puts the measurement
of location and co-location on a rigorous statistical
footing. Furthermore, we show how the PMI can be estimated
from data on the counts of activities across locations. To do
so, we use a Bayesian framework that assumes that the data
on the presence of units of economic activities across locations
are generated from a multinomial distribution. This Bayesian
estimation framework resolves some well-known measurement
issues and provides a measure of uncertainty for the estimated
quantities.

Krugman, 1991), all stress the fact that different economic entities
specialize in different activities. Scholars in each of these

fields have relied on indices that quantify, for example, the revealed
comparative advantage of exports, the specialization of
regions, and the extent of localization and (co-)agglomeration
of industries. However, these indices are often used ad hoc and
lack a clear statistical foundation. In this paper, we propose
a statistical framework from which such measures can be derived.
Although the methodology generalizes immediately to
other contexts, to fix ideas, we focus on economic geography
and derive measures of (co-)location, specialization and localization
from a single statistical framework, revealing the internal
connections between these concepts.

Metrics based on Information Theory such as the PMI have
found various applications in economics (Theil, 1967), and are
uniquely derived from axioms about how information can be
gained from probability distributions (Shannon, 1948, Cover
and Thomas, 2005). One of their key properties is that they
can be aggregated and decomposed to form well-defined measures
that have an interpretation in terms of information, by taking
expectations. This allows the use of the PMI as a building
block of information-theoretic measures that describe properties
at the location, activity, or even system level.

We treat (co-)location as the realizations of two categorical
random variables: the location and the type of an economic
activity. We use the Pointwise Mutual Information (PMI) to
express the association between a location and the type of an
activity in terms of the information that the type of a unit of
activity (e.g. a person’s occupation) gives about the unit’s location
(e.g. the city where that person works). Next, we show
how the PMI can be used to quantify the association between
two activity types in terms of how much information observing
a particular activity type in a location gives about observing another
activity type in the same location. That is: if we observe a

We show how the resulting measures can be related to wellknown
existing indices of localization and specialization. In
particular, at the level of location-activity pairs – as exemplified
in country-product or city-industry data – our metric of association,
the PMI, is conceptually similar to the logarithm of the
widely used index of revealed comparative advantage (RCA)

(Balassa, 1965).4 This provides an information-theoretic motivation
for considering the logarithm of the RCA index, which

∗Corresponding author

Email address: A.vanDam@uu.nl (Alje van Dam )
1Copernicus Institute of Sustainable Development, Utrecht University
2Center for Complex Systems Studies, Utrecht University

4The RCA is also known as the Location Quotient in the regional science
literature (Isard, 1960).

3Growth Lab, Center for International Development, Harvard University
has the practical advantage that it overcomes the RCA index’s
problem of distributional skew. Moreover, the Bayesian estimation
procedure ensures that the measure always attains finite
values, and suggests a natural measure of uncertainty for the
estimates.

of people employed in a particular occupation i in a city c, the
number of establishments of industry i in region c or the number
of dollars of product i exported by country c. The total amount
of activity of type i and the total activity in location c are given
by the row sums qc =
P
i qci and column sums qi =
P
c qci,
respectively. Total economic activity is given by q =
P
c,i qci.
We will consider the prevalence matrix Q to be the outcome

Building on the location-activity PMI, we can furthermore
derive a measure for the localization of economic activities, that
is, for the degree to which economic activities are spatially constrained.
We do so by calculating an activity’s expected PMI
(i.e., the expected association of the activity with a given location)
over all locations. This yields the Kullback-Leibler divergence,
which has been proposed as a measure of localization
before (Mori et al., 2005). Likewise, we can calculate the
expected location-activity PMI of a particular location across
all activity types. This average association of a location with
given activities provides a measure of specialization that is conceptually
similar to Krugman’s specialization index (Krugman,
1991).

of a sampling process from the underlying distribution p with
probabilities

pci = P(X = i,C = c) (1)
that a randomly sampled unit (i.e. an employee, an establishment,
a dollar) is part of activity i in location c. Here,
the categorical random variables X and C denote the activity
and location of a randomly sampled unit, respectively. Their
marginal probabilities are given by pi =
P
c pci = P(X = i) and
pc =
P
i pci = P(C = c).

The location-activity probabilities pci will be the main object
of interest as they hold information on the associations between
locations and activities (Section 2.2). From these probabilities
it is also possible to construct the probabilities pi j that a pair
of economic activities i and j are present in the same location,
which is used to analyze the co-location association (Section
2.3). Both pci and pi j are estimated from Q using a Bayesian
framework as described in Section 3.

Finally, we apply the PMI to the distribution of co-located
pairs of economic activity, which gives the probabilities that
pairs of activities are located in the same geographic unit. This
provides a measure of spatial association between economic
activities. Such measures may reveal positive or negative colocation
forces, and are conceptually similar to widely used (co-
)agglomeration measures (Ellison and Glaeser, 1997, Ellison
et al., 2010). Here we derive such measures from first principles,
which clarifies their underlying assumptions and statistical
properties.

2.2. Location association

As noted, we will use the dependencies hidden in the joint
probabilities pci to measure the association between an activity
and a location. Information theory provides a framework in
which these associations can be quantified explicitly in units of
information. The association between the two events X = i and
C = c is given by their pointwise mutual information PMI(pci)
(Fano, 1961). Intuitively, it answers the question ‘how much
information does observing c provide about the presence of
i?’ PMI has been used in several fields, including economics
(Theil, 1967), administrative sciences (Theil, 1972), and linguistics
(Church and Hanks, 1990). Here, we use it in the
context of economic geography to measure the association between
economic activities and locations (location association)
and within pairs of economic activities (co-location association).As
in the case of location-activity pairs, marginalizing the
PMIs of co-located activity-activity pairs yields meaningful aggregate
quantities. Accordingly, the expected spatial association
of an activity with all other activities gives a measure of
the spatial ‘co-dependence’ of an activity. This measure reveals
how ‘picky’ activities are in their tendencies to co-locate with
other activities. This spatial co-dependence is low for activities
that locate independently of other activities, whereas codependence
is high for activities that are preferentially found
in the presence of specific other activities. As an empirical illustration,
we calculate the associations between pairs of occupations
groups, along with the aggregate spatial co-dependence
of each occupation group, using US city-occupation employment
data. The associations between occupation groups reveal
three clear clusters. The first consists of occupations related
to knowledge intensive services, the second to occupations related
to non-traded services and the third to occupations related
to manufacturing.

The PMI measures the association between two outcomes by
assessing the information content of the realization (C = c, X =
i) given the information content in case of a null model in which
c and i are independent, i.e. pci = pc pi
. This is given by the
logarithm of ratio of both probabilities:5

2. Information-theoretic measures of (co-)location

PMI(pci) = log

!

pci
pcpi

. (2)

2.1. Notation

Consider data on the location of economic activities in the
form of an Nc × Ni dimensional matrix Q, where Nc and Ni are
the number of locations and economic activities in the classifications
of the data, respectively. We call Q the ‘prevalence
matrix’ as its entries qci denote the number of occurrences of
activity i in location c. This can be for example the number

In information theory, the information content or ’surprise’ of an outcome
i is defined as log( 1
pi
). Observing an event that occurs with small probability
leads to a high information content or surprise, whereas highly likely events
contain little information. The difference between the information contents of

pci and pc pi gives a measure of the surprise of observing pci while expecting
pc pi
. Depending on the base of the logarithm, PMI measures association in
units of bits (base 2) or nats (natural logarithm).
PMI(pci) will be positive when it is more likely to observe c and
i together than expected under independence, i.e. pci > pc pi
,
whereas PMI(pci) takes negative values when c and i are less
likely to occur together than expected under the null model of
independence, i.e. pci < pcpi
. PMI(pci) = 0 if and only if
pci = pc pi
, indicating that c and i are independent (i.e., the

expected under independence will have a positive association,
whereas activities that are less likely to occur together than expected
under independence will have a negative association.7
The PMI(pi j) is inherently symmetric, since pi j = pji. Computing
this measure for all pairs of activity types thus leads to
a symmetric, square matrix that has as entries the co-location
association PMI(pi j).

incidence of an activity is independent of the place). The maximum
value of PMI(pci) is given by max{log
pi

, log
pc

} =
log
pci
, which is attained either when activity i always occurs
in location c, or when activity i is the only activity in location
c.
6 PMI(pci) is not bounded from below, as it tends to −∞ as
the joint probability pci tends to 0.

The diagonal entries of this matrix hold ‘self-associations’
PMI(pii). Self-association is high when observing an activity
of type i in a particular region increases the likelihood that a
second randomly sampled unit in that location is also of type i.
This is the case when the probability of observing i is above average
in a few locations, and below average in others. The selfassociation
can thus be interpreted as a measure of geographical
concentration. Note that the self-association is always positive,
i.e. PMI(pii) ≥ 0, since observing a unit of activity of type i can
never lower the probability of finding another unit of activity of
type i (we sample with replacement). The matrix of co-location
associations thus provides a joint estimate of geographic concentration
and co-location.

2.3. Co-location association

We can also use this information-theoretic framework to obtain
a measure of association between pairs of economic activities.
To do so, we expand (1) to include two units of activity:

pci j = P(X1 = i, X2 = j,C = c), (3)

where X1 and X2 describe randomly sampled units of activity
from the same location C.

3. Bayesian estimation

The measure of co-location will come from integrating
across places to get the joint distribution of economic activities

In order to compute the quantities above, an estimate of the
probabilities pci is needed. A straightforward way to estimate
these probabilities is to consider the share of every locationactivity
pair, corresponding to the maximum likelihood estimate
ˆpci =
qci
q
. Here we estimate pci using a Bayesian framework,
which has two major advantages over the maximum likelihood
approach. First, the Bayesian approach always returns
nonzero probability estimates, so that computing the PMI will
always return finite values. Second, the Bayesian framework
yields a full posterior distribution for the estimated probabilities
as opposed to a point estimate. The posterior distribution
provides a natural description of the uncertainty in the estimated
parameter values, which can be used to construct a Bayesian error
bar for the information-theoretic quantities based on those
estimates (Wolpert and Wolf, 1995).

pi j = P(X1 = i, X2 = j). (4)

The probability pi j thus represents the joint probability that two
units of economic activity that are randomly picked from the
same (random) location are of type i and j. It can be obtained
by exploiting the fact that, conditional on knowing the location
c, the occurrence of types i and j are independent, i.e.
pi j|c = pi|c pj|c, since the full distribution of economic activities
for every location is known. By the law of total probability,
one then obtains

pi j =
X
c

pi|c pj|cpc. (5)

This defines the probability that two randomly sampled units
from the same (random) location have activity types i and j.
As with the location-activity associations, the association between
activity types can be quantified with the PMI. The association
between two activities is then defined as

Assuming that Q is generated by an independent sampling
process, the probability of its realization is given by a multinomial
distribution

Γ(q + 1)
Q
c,i Γ(qci + 1)

Y
c,i
p
qci
ci ,

P(Q|p) =

PMI(pi j) = log

pi j
pipj
!

, (6)

P
c,i pci = 1.
Applying Bayes’ rule, the posterior distribution for the matrix
of probabilities p is then given by

where p is the matrix containing probabilities pci,

where pipj
is the null model that describes a situation where
i and j are distributed independently of each other. What
PMI(pi j) captures is that the presence of some activities may
increase or decrease the probability that other activities are
present in the same location. Hence, observing a particular
type of economic activity holds information about the likelihood
of observing other types of activities in the same location.
Economic activities that are more likely to occur together than

P(p|Q) ∝ P(Q|p)P(p),

7Another way of seeing this, is by noting that PMI(pi j) is positive when
observing type i increases the probability of observing type j when sampling
units of activity from the same location, i.e. pj|i > pj
. Likewise, negative
associations indicate that conditional on observing i, the probability of sampling
a unit of activity j in the same location decreases.

6Notice that then pci = pi or pci = pc respectively.
where P(p) represents the prior distribution. A conjugate prior
for the multinomial distribution is the Dirichlet distribution

the data in the same way across activities and locations, so that
the relative uncertainty of estimates ˆpci is independent of the
units of Q.
One could use the estimate ˆpci = E[pci] directly to compute
PMI( ˆpci) and PMI( ˆpi j). However, this will induce a systematic
bias which comes from Jensen’s inequality E[PMI(pci)] Q
PMI(E[pci]) depending on whether PMI(pci) is concave or
convex.10 One needs instead an estimate of PMI(pci), which
in itself is a random variable whose distribution is determined
by the posterior distribution of pci. Thus, we use the uncertainty
for the estimates ˆpci to determine the uncertainty of estimates
for PMI(pci) and PMI(pi j).

Γ(α)
Q
c,i Γ(αci)

Y
c,i
p
αci−1
ci ,

P(p|α) ∼ Dir(α) =

P
c,i αci. This gives the distribution of p given hyperparameter
α. The posterior distribution for p given the data
Q and hyperparameter α is then given by

where α =

Y
ci
p
qci+αci−1
ci .

P(p|Q, α) ∼ Dir(Q + α) ∝

The hyperparameter α can be interpreted as a matrix of
‘pseudocounts’, giving the assumed number of observed units
of activity for every c, i pair prior to seeing the data Q. The
total number of pseudocounts α determines the strength of the
prior relative to the data. An estimate for the parameters pci is
then given by the expectation of the marginals of the posterior
distribution, so that

3.1. Estimation of the posterior mean and variance of
PMI(pc,i)
Here, we approximate the mean and variance of the posterior
distribution of PMI(pci), which will serve as estimates
of the posterior distribution of the location-activity association.
Our approach is based on Wolpert and Wolf (1995) and Hutter
and Zaffalon (2005), in which the estimation of informationtheoretic
quantities using a Bayesian approach is discussed in
depth.

qci + αci
q + α

=
q˜ci
q˜
,

pˆci = E[pci|Q, α] =

where we write ˜qci = qci + αci and ˜q = α + q. When the pseudocounts
αci are nonzero for all c, i, then ˆpci > 0 will also be
nonzero. This has the practical advantage that it prevents difficulties
when computing logarithms of the estimated probabilities,
as when calculating PMI(pci).8

To obtain an approximation for the posterior distribution of
PMI(pci), we compute its Taylor expansion around the mean
pˆci. Writing ∆ci = pci − pˆci, and noting the fact that |∆ci| < 1,
this gives

A measure for the uncertainty of the estimate ˆpci is given
by the variance of the marginals of the posterior distribution,
leading to

PMI(pci) = PMI( ˆpci) + ∆ci

pˆci
−
pˆc
−
pˆi
!

+
∆
ci

−
pˆ
ci
+
pˆ
c
+
pˆ
i

+ O(∆
ci).

q˜ci( ˜q − q˜ci)
q˜
( ˜q + 1)

Var[pci|Q, α] =

Note that E[∆ci] = 0 and thus E[∆
ci] = Var[pci], where expectations
are taken with respect to the posterior distribution of pci.
It follows that

q˜ci/q˜(1 − q˜ci/q˜)
q˜ + 1
.
Note that this implies that the variance is dependent on the granularity
of the data in Q. To see this, suppose we alter the units
leading to a new matrix Q0 = kQ, so that for large q

=

−
pˆ
ci
+
pˆ
c
+
pˆ
i

 . (7)

Var[pci]

E[PMI(pci)] ≈ PMI( ˆpci) +

kq˜ci/kq˜(1 − kq˜ci/kq˜)
kq˜ + 1

The second term accounts for systematic bias in the estimate of
PMI(pci), in which the sign of the factor multiplying the variance
is indicative of whether PMI(pci) is concave or convex,
and thus determines whether the bias is positive or negative.
Using the Delta method, we then obtain for the variance of
PMI(pci):

, α] =

Var[pci|Q

≈
k

Var[pci|Q, α].

The variance thus decreases as the counts become more finegrained.
The reason is that the data generating process is assumed
to create the data at the level of the counts, so that morefine
grained units represent more observations. The variance of
the estimates is thus directly related to the units in which the
underlying data generating process is assumed to generate the
data.9 However, the variance is affected by the granularity of

∂PMI(pci)
∂pci

Var[PMI(pci)] ≈ Var[pci]

|pˆci

pˆci
−
pˆc
−
pˆi
!2

= Var[pci]

. (8)

This is a measure for the uncertainty around the point estimate
E[PMI(pci)]. In particular, it can be used to determine whether
the estimate for PMI(pci) is significantly nonzero, i.e. if there
is a significant association between i and c.

In the context of information retrieval in text analysis, adding the pseudocounts
αci to categorical data is known as ‘Laplace smoothing’ or ‘additive
smoothing’ (Manning et al., 2008).
In the context of (co-)agglomeration of industries for example, the relevant
unit of analysis is the one at which location decisions are made, which could be
be assumed to be the plant level, suggesting an analysis of data containing the
counts of plants of a specific industry for a given location.

10PMI(pci) is concave when ∂
2PMI(pci)/∂p
ci = −1/p
ci + 1/p
c + 1/p
i
< 0,
and convex when ∂
2PMI(pci)/∂p
ci > 0.
3.2. Estimation of posterior mean and variance of PMI(pi j)

showing that conceptually the PMI is equal to the logarithm of
the RCA index.

Approximations of E[PMI(pi j)] and Var[pi j] are obtained in
a similar fashion, replacing pci with pi j in equations (7) and
(8), although the computation of Var[pi j] is more involved. Appendix
A provides a discussion of how Var[pi j] is obtained.
Appendix B provides comparisons to numerical simulations to
justify the approximations made.

Our approach stands therefore as a generalization of the RCA
index. This shows that there is an information-theoretic notion
of association underlying the RCA. Seen in this light, the
practical problem of having to take the logarithm of zero when
qci = 0 is in fact a problem related to miss-estimating pci. In our
Bayesian approach, the estimates of probabilities pci are always
strictly positive.

4. Location and co-location

4.2. Measures of localization

4.1. Revealed Comparative Advantage

One of the most commonly used indices to study location
patterns of economic activities originates from the trade literature,
where it is known as Balassa’s index of Revealed Comparative
Advantage (RCA) (Balassa, 1965). The RCA of a
location-activity pair is given by the ratio of the share of activity
i within location c compared to the share of activity i in
the overall economy:

Many questions are better answered at more aggregate levels
of analysis than the level of location-activity pairs. Typical
questions at these levels of aggregations rely on quantifying
which activities are most localized in space, or which locations
are most specialized in terms of their economic activities.

Localization of an activity can be defined as the degree of
dissimilarity between the activity’s own geographical distribution
and the distribution of the population or of total economic
activity across all locations (Hoover, 1936, Mori et al., 2005).
Highly localized activities will be distributed across locations
in a very different way than what one would expect from locations’
sizes. Activities with a low degree of localization will
be distributed proportionally to the relative (population) size of
locations. This can be quantified by comparing how much, on
average, the probability that a unit of activity of type i is located
in a location differs from the probability that any unit of activity
is located there.

qci
qc

/
qi
q

RCA(c, i) =

. (9)

It compares the observed share of activity i within location c in
the numerator to the total share of i as given by the denominator.
Since qi and qc are exchangeable in (9), RCA(c, i) can be interpreted
in two ways: as a measure of ‘localization’ of activity i
in location c, or as a measure of ‘specialization’ of location c in
activity i. The neutral value is given by RCA(c, i) = 1, where
the share of activity i in location c is equal to the total share of
activity i over all locations.

Let pc|i = pci/pi be the probability that a unit of activity
is located in c given that its activity type is i, and recall that
the probability that a unit of economic activity is located in c
regardless of its type is given by pc. Considering the average
deviations between pc|i and pc leads to a measure of localization
that is given by

A theoretical derivation of the RCA index is given by Kunimoto
(1977), who uses a probabilistic approach that comes
close to the approach presented in this paper. Properties of the
RCA and related indices have since been discussed extensively
(Yeats, 1985, Ballance et al., 1987, Vollrath, 1991), some of
which are problematic when applying the index in empirical
analysis. One of the issues of the RCA index is that it is heavily
skewed and asymmetric around its neutral value. A possible
solution that has been presented is taking the logarithm of the
index, making it symmetric around a neutral value of 0 (Vollrath,
1991). This, however, leads to the problem that the index
becomes undefined in the cases where qci = 0, since the logarithm
of zero is undefined.

X
c

|pc) =

KL(pc|i

pc|i

log(pc|i/pc)

X
c

=

pc|iPMI(pci),

where we used that pc|i/pc = pci/pc pi
. Here, KL denotes the
Kullback-Leibler divergence (Kullback and Leibler, 1951), and
measures the deviation between the distribution across all locations
of a specific activity, given by probabilities pc|i
, and the
overall distribution of locations, given by the probabilities pc.
Hence, the proposed information-theoretic framework naturally
suggests a localization measure by aggregating PMI(pci) to the
activity level. The resulting metric can be interpreted as the
activity type’s expected locational dependence.

The approach presented in the current paper provides an
information-theoretic derivation of the logarithm of the RCA
index. Consider the maximum likelihood estimate for the multinomial
probabilities ˆpci =
qci
q
.
11 We then have that

PMI(pci) = log

!

pˆci
pˆc pˆi

This measure has the exact same functional form as the measure
of industrial localization put forward by Mori et al. (2005),
although the null model implicit in their metric is based on a
location’s area. That is, they take the probability pc to be proportional
to the area of that location as opposed to its population
size.12 Here we show that their measure can be retrieved as the

= log

q˜ci
q˜c

q˜i
q˜
!

= log(RCA(c, i)),

11Note that here we write qci and not ˜qci = qci +αci, since the maximum likelihood
estimate uses directly the observed counts, without adding the pseudocounts
that where a consequence of incorporating a prior distribution of counts
in the Bayesian estimate.

12Furthermore, they obtain an error bar for this statistic based on a normal

unit of analysis measure formula
location-activity association PMI(pci)
activity localization KL(pc|i
|pc) = Epc|i[PMI(pci)]
location specialization KL(pi|c|pi) = Epi|c[PMI(pci)]
system overall specialization MI(C, X) = Epci[PMI(pci)]
Table 1

expected PMI values of a particular industry.13 Ignoring differences
in how these distributions are estimated, the functional
of this measure is equal to Epc|i
[log(RCA(c, i))], showing that it
can be understood as the expected value of the logarithm of the
RCA of an activity over all locations it occurs in.

4.3. Measures of specialization

Similarly, the aggregate level of specialization of a location
as a whole can be analyzed by quantifying the difference of the
distribution of activities within the location, pi|c, to the overall
distribution of activities pi
. Such a measure of specialization

economic activity is distributed proportionally to location size,
or equivalently that every location has an identical distribution
of activities. In this situation, there is no specialization in the
system in the sense that all locations are identical. The maximum
value of MI(C, X) is reached when each location has its
own unique activity, so that each location is maximally specialized
and each activity is maximally localized. In the current
context, the mutual information is a system-level measure of
overall specialization that can be used to compare across different
systems (e.g. comparing the degree of overall specialization
across countries), or to track the changes over time (e.g. comparing
the degree of overall specialization before and after the
establishment of a trade union). Table 1 summarizes each of the
measures derived thus far and the relation between them.

is obtained by aggregating the PMI(pci) to the location level,
thus considering the expected association of the activity with
particular locations, leading to

X
c

KL(pi|c|pi) =

pi|cPMI(pci).

Again, this can be interpreted as the expected value of the logarithm
of the RCA, but now over industries within a given location:
Epi|c
[log(RCA(c, i))]. The measure is akin to Krugman’s
specialization index (Krugman, 1991).14 However, in
our framework, the localization of activities and specialization
of locations are essentially the same measures, defined for different
units of analysis.

5. Co-location

5.1. Co-location association

4.4. Overall specialization

So far, we have studied the matrix Q, which summarizes location
patterns of economic activity. Our framework can however
readily be extended to study more complex patterns. Here
we will discuss co-location patterns of pairs of activities, i.e.,
of the dependencies between activities that are located in the
same region. Such co-location patterns have received increasing
attention in studies on international trade (Hidalgo et al.,
2007) and urban economies (Ellison et al., 2010). In the latter
field, authors have used co-location patterns to test theories on
Marshallian externalities (Marshall, 1920). In this literature, the
co-agglomeration index of Ellison et al. (2010) has become a de
facto standard (Faggio et al., 2017, Diodato et al., 2018). Here,
we show how information theory can be used to derive an alternative
measure based on the co-location association, PMI(pi j).
Before presenting our co-location metrics in detail, it is useful
to first discuss how Ellison et al. (2010) construct their coagglomeration
index. These authors present a location choice
model for profit-maximizing plants (Ellison and Glaeser, 1997,
Ellison et al., 2010) in which the (combined) effects of natural
advantage and spillovers between activity types determine coagglomeration
patterns. They propose the following pairwise
co-agglomeration index:15

Aggregating even further, a measure for the overall specialization
at the system level can be obtained by taking the expectation
over both locations and activities, leading to the expected
association of a location-activity pair, or equivalently as either
the expected localization of an activity or the expected specialization
of a location. The resulting quantity is known as the
Mutual Information (MI) (Cover and Thomas, 2005) and quantifies
the dependence between two random variables. In this
case, it measures the dependence between the random variables
X and C, which describe the type and location of a randomly
sampled unit of activity. It is given by

X

MI(C, X) =

pciPMI(pci) (10)

c,i

X
i

|pc) (11)

=

piKL(pc|i

X
c

=

pcKL(pi|c|pi). (12)

When MI(C, X) = 0, the location of a randomly sampled
unit is independent of its activity type, which implies that all

(pc|i − pc)(pc| j − pc)
1 −
P
c p
c

P
c

approximation. In the Bayesian framework, an estimate for the standard deviation
of the KL can be obtained in a similar way as for the PMI, as shown in
Appendix C.

γi j =

. (13)

13This holds regardless of the ’null model’ considered. Hence, one could
follow Mori et al. (2005) and use their area based null model to define a measure
on the location-activity level that is analogous to the RCA index.
14The Krugman specialization index is given by K(c) =
P
i
|pi|c − pi
|. Like
KL(pc|i
|pi), it considers an ’average deviation’ of pi|c to pi
, where the measure
of deviation is taken to be the absolute difference.

and qc
q
are replaced by probabilities
pc|i and pc. This makes specific that we regard the former shares as
maximum likelihood estimates of the latter probabilities. For now, however, we
leave the issue of estimating these probabilities open.

15Note that, in our notation, activity shares qci
qi
The co-agglomeration of all pairs can be collected in a matrix
with entries γi j, completely analogous to the PMI(pi j) in
Section 2.3. The diagonal entries γii contain the agglomeration
index of a single activity (Ellison and Glaeser, 1997), when neglecting
effects of the plant size distribution.16

a measure of the average association of activity i with all other
activities, given by

X
j

KL(pj|i

|pj) =

pj|iPMI(pi j). (14)

Comparing the co-agglomeration index given in Eq. (13) to
our co-location association metric rewritten as

We call this measure the co-dependence of a particular activity.
It quantifies the deviation of the distribution of activity types
conditional on having observed activity type i, pj|i
, with respect
to the unconditional distribution of probabilities pj
. When activity
type i has, on average, strong associations with other activity
types it co-locates with, this deviation will be large. In
other words, activity i ‘cares’ about the type of activity it colocates
with. A low value of KL(pj|i
|pj) on the other hand

PMI(pi j) = log P

c pi|c pj|c pc
pipj

!

X
c

!
pc

.

pc|i
pc

! pc| j
pc

= log

clarifies the conceptual similarity between the two. Both capture
how different activities co-vary in space. In either case, the
intensity of spatial co-location may be generated by a location
choice model akin to the one by Ellison and Glaeser (1997).

implies that the distribution of probabilities pj|i does not differ
much from the distribution of pj
, meaning that activity i is
uninformative for the type of activities it co-locates with. This
implies that activity i co-locates with the ’average’ distribution
of activity types, suggesting it is indifferent of the other activities
in the same location.

The difference lies, however, in the functional form used
to measure the deviation from the reference distribution. The
co-location association compares probabilities by taking ratios
pi|c/pc, whereas the co-agglomeration index considers differences
pi|c−pc. Furthermore, the co-location association weights
each of the differences by pc.

Note that activities that are heavily concentrated geographically,
have by definition a high co-dependence, as PMI(pii) is
part of the sum in (14). In that case, activity of type i typically
co-locates with other activity of type i.

Although the co-agglomeration index is derived from an economic
model, the measure of concentration that lies at its heart
enters the derivation as an assumption. Our framework provides
a principled way to quantify these deviations, by leveraging
information theory. The advantage of such an approach is
that it gives insight into the underlying assumptions on the data
generating process, the used reference distribution17, and the
estimation procedure with its corresponding uncertainties. Furthermore,
as before, our statistical framework allows constructing
measures of co-dependence at higher levels of aggregation,
such as at the level of the activity or of the economic system as
a whole.

5.3. Overall pairwise dependence

Taking the expectation of the co-dependence over all activity
types, or equivalently taking the expectation of the co-location
association over all activity pairs leads to the mutual informationXiMI(X1,
X2) =

piKL(pj|i

|pj)

X
i j

=

pi jPMI(pi j).

This is a measure of dependence between the random variables
X1 and X2, which each describe the activity type of a randomly
sampled unit of activity, both sampled from the same
location (see (4)). The overall co-dependence is thus a systemlevel
variable that describes how much two units of activity are
on average (spatially) associated. This may, for instance, help
understand how the overall strength of co-agglomeration externalities
differs across economies or changes over time. Table 2
gives a summary of the measures that follow from analysis of
the co-location distribution pi j. Both Tables 1 and 2 construct
similar sets of measures. Both sets of measures take averages
across rows, columns, or both, of a matrix that summarizes associations
between two variables. However, whereas the measures
in Table 1 are based on the location-activity information
of a matrix that collects elements PMI(pci), the measures in Table
2 are based on the spatial co-location information collected
in a matrix with elements PMI(pi j).

5.2. Co-dependence

As in Section 4.2, the co-location associations can be aggregated
by taking the expectation across all activities j, leading to

16Mori et al. (2005) show that the agglomeration index of (Ellison and
Glaeser, 1997) can be written as γi = aiGi − bi ≈
P
c
(pc|i−pc)
1−
P
c p
c
. This approximation
is valid when plants are reasonably uniformly distributed, in which
case the plant size effect is negligible. The plant size distribution determines
the size of the chunks in which the counts are generated in the data generating
process. Quantifying the dependencies that arise from such a data generating
process is an interesting direction for future research, but for now we focus
on the simpler case in which information on the chunk sizes (e.g. the plant
size distribution) is unavailable. Further note that unlike Mori et al. (2005), we
compare the agglomeration index to the self-association PMI(pii) as opposed
to the localization KL(pc|i
|pc).
17In fact, the literature is not entirely consistent in the choice of the reference
distribution that is used in the (co-)agglomeration indices. In some work the
reference distribution is taken to be the share of total employment in location c,
which we denote by pc (Ellison and Glaeser, 1997, 1999, Faggio et al., 2017).
In other work, the reference distribution is given by the average share of employment
in industry i in a location, given by ˆpc|i =
Ni
P
i pc|i (Ellison et al.,
2010, Diodato et al., 2018).

6. Empirical example

As an example, we apply the PMI to show the co-location
associations of occupation groups in US employment data in

unit of analysis measure formula
activity-activity co-location association PMI(pi j)
activity-activity geographic concentration PMI(pii)
activity co-dependence KL(pj|i
|pj) = Epj|i
[PMI(pi j)]
system overall co-dependence MI(X1, X2) = Epi j[PMI(pi j)]
Table 2

7. Discussion

Information theory offers a unified way to estimate location
and co-location associations using PMI. This yields measures
that are similar to the well-known RCA index Balassa (1965)
and the co-agglomeration index (Ellison et al., 2010). However,
our metrics based in information theory have important
advantages over these existing measures.

2016 provided by the Bureau of Labor Statistics.18 The data
consists of a matrix Q that gives for every city c the number of
employees qci in a particular occupation group i. In this examFirst,
by deriving these metrics from a unified framework, we
were able to show the intrinsic connections between hitherto
disparate measures. This is not only satisfying from a methodological
point of view, but allows exploring the relations between
concepts like revealed comparative advantage, specialization,
localization, concentration and co-location.

ple, we choose a uniform prior, setting αci = 1 for all c, i. This
represents a single observation for every location-activity pair.

Since the total number of pseudocounts α = NrNc << q, the
resulting estimates will be determined much more by the data
than by than the prior.

Second, the proposed measures are derived from a formal
framework (information theory) in a way that is explicit in the
assumed data generating process, the chosen null models and
the estimation procedures. Different choices for these assumpThe
inferred PMI(i, j) matrix is shown in Figure 1, showing
the co-location associations between the occupation groups.
The right hand side shows the co-dependence of each occupation
group with respect to all other groups, corresponding to the
expected value of a row in the PMI matrix. The error bars show
one standard deviation in the posterior distribution, as derived
in Appendix C. Red indicates positive associations, and blue
negative ones.

tions leads to different results. However, the afforded transparency
allows to construct arguments against and in favor of
such alternatives that take into consideration aspects of the specific
context at hand. Such a discussion can be framed in terms
of an underlying model, rather than of ad hoc specificities of
a particular index. For instance, we used a null model based
on the assumption that neutral associations imply a distribution
of location-activity pairs that is proportional to the sizes of locations
and activities (Hoover, 1936). Alternative null models
could follow from the assumption that activities are distributed
proportional to the area of a location (Mori et al., 2005). Another
possibility is to determine the expected number of (co-
)occurrences on the basis of external factors that could drive
the distribution of activities over locations, using for instance
a regression model (Neffke et al., 2011, Jara-Figueroa et al.,
2018).

The matrix delineates three clusters of occupations groups.
The upper left block shows a cluster of positively associated
occupations that seem to be related to knowledge-intensive services.
The positive associations lead to a relatively high codependence
for these occupations, suggesting that the presence
of these occupations depends largely on which other occupations
are present in the same city.

The lower right block of the matrix shows a smaller cluster
of occupations related to production, transportation and repair.
These occupations have a negative association with the
knowledge-intensive occupations, and thus typically co-locate
with a different set of occupations. The ‘Production’ occupations
group also has a high co-dependence, which is mostly
driven by a high self-association.

Third, the framework provides uncertainty estimates for all
the information-theoretic quantities involved. Most currently
used indices are applied without any notion of uncertainty. Using
these uncertainties in practice however may present some
challenges. For instance, the Bayesian estimation procedure
leaves room for the selection of different priors. Here, for
reasons of practicality, we applied a simple uniform prior.
However, in some contexts, alternative priors may be natural
choices. Many of these priors would still result in Dirichlet
priors, but with different uniform values for αci to adapt the
strength of the prior to the data at hand (Hutter and Zaffalon,
2005). In other contexts, non-uniform priors, such as the maximum
entropy prior (Wolpert and Wolf, 1995), may be preferable.
Furthermore, the absolute magnitude of the uncertainty
will depend on the granularity of the data. This simply reiterates
that inferences should always be made with an underlying
data generating process in mind. In spite of this, we can still
make statements about the relative magnitudes of uncertainties,
which are independent of the granularity of the data generating
process.

The ’Farming, fishing and forestry’ group is highly isolated,
with mostly negative associations with other groups. The diagonal
entry in the matrix shows the self-association is very high,
which is also reflected in a high co-dependence, which is orders
of magnitude larger than that of the other occupations (note the
broken axis).

In the middle band of the matrix, occupation groups have
a neutral association with most other occupations, and have a
low co-dependence. These groups seem to be related to nontraded
services, including ’Protective service’, ’Food preparation
and serving’ and ’Personal care and service’. The low codependence
implies that these occupations are distributed approximately
proportional to the total population, independently
of which other occupation groups are present in a city.

Fourth and finally, it is important to note that the informationtheoretic
approach can be readily extended to move beyond the
analysis of pairwise co-locations, as it also allows analyzing

18These data are available at https://www.bls.gov/oes/special.
requests/oesm16ma.zip

Figure 1: Values of the estimated PMI(pi j) for major occupations groups. Red indicates positive associations, blue indicates negative associations, and grey
indicates neutral (PMI(i j) = 0) associations. All pairwise associations are between −0.5 and 0.5 with the exception of the self-association of the ’Farming, fishing
and forestry’ occupations, which has a value of 3.15. The right hand side shows the co-dependence KL(pj|i
|pj) of every occupation group, given by the expected
value of a row of the PMI matrix. The error bars depict one standard deviation of the posterior distribution as a measure of uncertainty for the estimate. Note the
broken axis, showing the extreme dependence of the ’Farming, fishing and forestry’ occupations.

multivariate associations. For instance, one could analyze associations
between multiple variables (e.g. occupations, cities and
industries) or multi-way co-locations (such as the co-location
of triplets instead of pairs of activities).19 Such higher-order
associations could be further analyzed using the informationtheoretic
concepts of redundancy and synergy (Finn and Lizier,
2018). This may help disentangle different types of associations,
capturing different economic interactions. The association
between a pair of economic activities could be conditional
on the presence of (a specific combination of) other activities,
or be driven by the mutual dependence on a (combination of)
other economic activities or on some external variable such as
the presence of a natural resource. Further development of this
analytical framework could reveal such higher-order relations
among economic activities.
