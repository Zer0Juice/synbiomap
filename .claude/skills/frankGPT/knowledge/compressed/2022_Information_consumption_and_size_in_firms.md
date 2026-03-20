---
source: 2022_Information_consumption_and_size_in_firms.pdf
pages: 12
extractor: pdftext
tokens_raw: 16414
tokens_compressed: 16296
compression: 1%
---

Information consumption and size in firms

Edward D. Leea

, Alan P. Kwanb

, Rudolf Hanela

, Anjali Bhattc

, and Frank Neffkea

aComplexity Science Hub Vienna, Vienna, Austria; bHong Kong University, Hong Kong, China; cHarvard Business School, Boston, USA

This manuscript was compiled on December 19, 2023

flow. Yet, an obstacle specific to the business firm is that the
information flow and its contents are largely unseen. Here, we
are able to peer into one part of it, news consumption. By
relating scaling trends in the data to one another, we take a
step towards quantitatively modeling the volume and variety
of information in organizations and establish quantitative measures
that can help connect them to principles that mediate
or shape collective behavior more broadly.

Social and biological collectives need to exchange information to persist
and to function. This happens across internal networks, whose
structure represents static channels through which information flows.
Less studied is the quantity and variety of information transmitted.
We characterize a part of the information flow, the information going
into organizations, primarily business firms. We measure what firms
read using a data set of hundreds of millions of records of news
articles accessed by employees across millions of firms. We measure
and relate quantitatively three essential aspects: reading volume,
reading variety, and firm size. First we compare volume with firm size,
showing that firms grow sublinearly with the volume of their reading.
The scaling means that inequality in information volume exaggerates
the classic Zipf’s law inequality in firm size, pointing to an economy
of scale in information consumption. Then, by connecting variety and
volume, we show that the firms vary in their reading habits to a limited
degree. Firms above a certain size become repetitive readers, consistent
with the sudden onset of a coordination cost between teams, not
individual employees. Finally, we relate information variety to size to
show that large firms tend to increase investments in existing areas
of interest instead of divesting from them to move to new areas. We
argue that this reflects structural constraints in growth. The results
indicate how information consumption reflects the role of internal
structure, beyond individual employees, analogous to information
processing in other social and biological systems.

arXiv:2210.07418v3 [physics.soc-ph] 17 Dec 2023

We look into the prodigious information consumption of
millions of organizations globally, the vast majority of which
are business firms. To do so, we analyze an extensive data set
of “intent data” aimed at gauging customer interest (25, 26).
The data consists of hundreds of millions of records of content
accessed by firm employees within a large universe of publishers
including The Wall Street Journal, Bloomberg, Forbes,
Business Insider, and CBSi, along with more specialized groups
of sites such as 1105Media, ITCentral Station, and Questex.
Most are anonymous but span technology, marketing, legal,
biotech, manufacturing, and a wide range of business services
(25). We focus on a two-week period between the dates of June

DRAFT

10 and June 23, 2018, which we expect is generally representative
of the data set as we detail further in Appendix ?? in the
Supplementary Information. The limited time window also
ensures that proprietary preprocessing steps used to generate
the data remain consistent. In principle, the data would allow
us to determine which news article an anonymized employee at
a firm accessed and when. For each article, we have up to ten
associated topics that have been identified with a proprietary
topic modeling algorithm (more details in reference 25). These
different properties permit us to analyze employee reading at
different scales of resolution from the individual articles, which

firms | information | scaling | reading

I
nformation exchange facilitates collective behavior including
coordination in schools of fish or flocks of birds (1–4), conflict
levels in primate society (5), team performance (6), and
organizational function (7, 8). In each of these cases, the transmission
of information is structured by cognitive constraints
(9), social strategy and relationships (10), or simply distance
(11). One particularly compelling example is the business firm.
Individuals throughout the firm hierarchy acquire and process
information to make decisions and retransmit information to
different parts of the organization (12, 13). Importantly, social
structure such as bridges or weak ties (14, 15) mediate the
flow of information, a perspective that has inspired the statistical
physics (16, 17) and computational social science (18) of
social networks. Pioneering work has gone into characterizing
the structural properties of the networks. As one mapping
in the study of collective knowledge, the properties of nodes

Significance Statement

Organisms exchange and use information to function. Social
organizations like firms do too, but they are hard to measure
quantitatively. We use a database with unprecedented resolution
and breadth to analyze how firms consume information
through reading of online news. We find that aspects of reading
reveal telltale signs of organizational structure from an economy
of scale (information is cheaper the more firms read), that
large firms face a coordination problem because teams are redundant
and repetitive readers, to that firms hold onto previous
interests (larger firms have cumulatively more interests). The
trends relate information consumption and firm size to establish
a baseline for characterizing firms with information targets and
raise questions about analogous biological structure.

include tacit knowledge, worker skills, and social skills (19).
Edges represent coworker complementarities (20). Structural
properties may reflect organization and hierarchy (21). On
the other end, others focus on the output of the computation
done by the networks such as how patents reflect combinatorial
innovation (22–24). In a related vein, the management
literature has investigated how firms absorb (13), process, and
use information such through investment on R&D and internal
communications (8). To connect internal structure to a firm’s
output, we need to determine the dynamics of information

E.D.L. designed the project. E.D.L., A.P.K., and A.B. participated in initial discussions. E.D.L., F.H,
and R.H. discussed the results. A.P.K. and E.D.L. processed the data. E.D.L. did the analysis, wrote
the code, and initially drafted the manuscript. E.D.L., F.N., A.P.K., and R.H. edited the manuscript.
The authors declare no other competing interests.

2To whom correspondence should be addressed. E-mail: edlee@csh.ac.at

December 19, 2023 | vol. XXX | no. XX | 1–7
then belong to sets of content pages or “sources,” and that
may overlap in broader “topics” as diagrammed in Figure ??
in the Supplementary Information (27, 28). Importantly, the
comprehensive nature of the data set allows us to obtain a
multiscale portrait of how firms seek out information down to
the individual acts of information acquisition.

a

s

s

e

t

s

(

U

S

D

)

(a) P
P

E

(

U

S

D

)

We focus on large-scale, population-wide aspects and establish
trends between the volume of information consumption,
its variety, and measures of firm size. In the first part of the
paper, we relate reading volume with firm size. We find that
firm size scales sublinearly with volume, leading to an inequality
of information consumption that exaggerates the Zipf’s law
inequality in firm size (29). This suggests that reading volume
reflects a different organizational structure than that reflected
in the usual size metrics. Then, we relate volume with variety
to find that large firms tend to be redundant readers. We
relate the limited variety of reading to coordination limits in
firms, and we propose that the scaling of teams of employees
is a crucial part of predicting how diversely large firms
read. Finally, by exploring the relation between variety and
firm size, we predict two qualitative extremes of firm reading
strategies, where either firms’ asset-to-topic ratio increases
or the ratio decreases. We predict that nearly all firms tend
to the former. Generally, the quantitative model aligns with
conventional wisdom for how firms focus on core competencies
(30, 31). Interestingly, the increasing concentration of assets
per topic is in contrast with the economy of scale for reading
volume, or elementary bits of information, suggesting that
the way that firms use information at the scale of employee
is fundamentally different from its use at the scale of the
organization. This echoes our main finding that the use of
information consumption reflects properties of the firm as an
information processing machine that leaves quantitative traces
of organizational structure.

(b)

s

ale
s

(

U

S

D

)

data
fit

employees

(c)
Utilities
Services

(d)

0 10
3 10
records

0 10
3 10
records

Fig. 1. Scaling of firm size measures (a) assets, (b) plants, property, equipment
(PPE), (c) employees, and (d) sales with record count. NAICS sectors Utilities
(orange), Professional, Scientific, and Technical Services (red), and all other (gray)
firms. Black line shows a power law fit to Eq 1 with exponents (a) β = 0.68 ± 0.02,
(b) β = 0.79 ± 0.02, (c) β = 0.76 ± 0.01, and (d) β = 0.77 ± 0.01 using one
standard deviation from bootstrapped fits as error bars. Fitting range R ≥ 160 given
by the fit to the distribution in Figure 2e.

DRAFT

firms in Utilities (orange points falling above the fit line). They
are not as clearly differentiated employees, but the estimate
of the number of employees in COMPUSTAT is known to be
poor. While the services category includes a broad swathe of
industries and thus displays wide variation along the vertical,
the trend is consistent with the notion that firms in the service
sector are on the whole more knowledge-intensive compared
to utilities.

Economy of scale in information
As a first step to characterizing how firms seek out information,
we consider the relationship between the volume of information
acquisition, the number of times a firm is recorded in
the database, or “records,” and conventional measures of firm
capital. In Figure 1, we plot for public firms in the COMPUSTAT
database the value of firm assets, PPE (plants, property,
equipment), the number of employees, and sales against the
number of records. Building on previous work on scaling
in firms (32), we consider a power law relationship between
economic measure Y and records R,

A record, however, is a rather rudimentary measure of
information flow. Within any given record, we are also given
the article that was accessed, the page on which it published or
“source,” and the topics that were relevant to the article, the
latter a derivative measure obtained from proprietary topic
modeling (see Appendix ?? for more details). Since these
constitute progressively larger groupings of individual records,
we might anticipate the economic size to scale differently with
the information measures at coarser granularity. As we show
in Figure 2, we find that sales grow faster with the number
of articles (β = 0.82 ± 0.02), with sources (β = 0.97 ± 0.02),
and with topics (β = 0.95 ± 0.03), respectively, using a leastsquares
fit on logarithmic axes. The sublinearity with records
indicates that the typical increase in elementary counts of
information access grows faster than the increase in sales such
that the effective cost of accessing new information decreases
with reading volume or articles, but this is not the case for
sources and topics.

Y = ARβ

, [1]

for some positive constant A and positive exponent β. This is
equivalent to a regression on a logarithmic scale, where the
slope is β and the y-intercept log A when Eq 1 is transformed
to log Y = β log R + log A. Importantly, the exponent β is
independent of the units of X and Y , the conversion between
which is separately captured in A. We find that all economic
measures scale sublinearly with the number of records with
scaling exponents of about β ≈ 3/4 except for assets which
scale somewhat slower as β = 0.68 ± 0.02 (Table ??). Furthermore,
it tends to be the case that a category of service firms (as
indicated by North American Industrial Classification System
codes, or NAICS, red points falling below the fit line) have
more records per unit of economic measure as compared to

Importantly, the scaling between economic and information
measures is consistent with the heavy-tailed distributions of
information search. This would mean that our results extracted
for a small subset of public firms in COMPUSTAT
are consistent with the distribution from the millions of firms
in the reading data. We check this by using the observation
that the distribution of firm receipts, here given by sales
Y , follows a Zipf’s law such that p(Y ) ∼ Y
−2
(29). Then,

2 | Lee et al.
s

ale
s

(

U

S

D

)

utilities
services
other
median

(a) (b) (c) (d)

(e)

(f)

(g)

(h)

pdf

0 10
3 10
records

0 10
3 10
articles

0 10
3 10
sources

0 10
3 10
topics

Fig. 2. (a-d) Scaling of sales with information variables. Mining (green), service (red), and all other (gray) firms. Black line is the scaling fit. Scaling exponents are
β = 0.77 ± 0.01, β = 0.82 ± 0.02, β = 0.97 ± 0.02, and β = 0.95 ± 0.03 (not shown) using bootstrapped error bars. Fits are only to data points above the lower cutoff
given by the fit to the distributions in the panel directly below except for topics, where the lower cutoff can be set a priori because the topic relevancy vector is of size 10. (e-h)
Distribution of the number of records α = 1.88, articles α = 1.92, sources α = 1.97, and topics α = 1.80 per firm shows power law scaling in the tails. A standard fitting
procedure involving maximum likelihood for the exponent α with the Kolmogorov-Smirnov statistic for the lower bounds returns xmin = 160, xmin = 69, and xmin = 61
(33). For topics, the lower bound is fixed at xmin = 10, and our simplified scaling model does not capture the curvature in panel d. See Table ?? for further exponents.

DRAFT

if it is the case that the distribution of information quantity
X obeys p(X) ∼ X
−α
, we can use the transformation
p(S)dS = p(X)dX and the scaling relation Y = ARβ
to
obtain the exponent relation

strong inequality in how firms read. In contrast, firm size
distributions have an exponent α = 2. This means that along
elementary measures of information, but not the aggregated
measures of sources or topics, we find that the largest firms
have a disproportionately larger information footprint compared
to the disparity in economic size.

α = β + 1. [2]

Using the values of β found above, we obtain the predictions
αˆ = 1.77 ± 0.01, αˆ = 1.82 ± 0.02, αˆ = 1.97 ± 0.02, and
αˆ = 1.95 ± 0.03.
Next, we fit the probability distributions by the number
of records, articles, and topics in Figure 2 using a standard
method (33), which gives us a direct estimate of α instead of
from using the right hand side of Eq 2. From this method,
we obtain α = 1.88 ± 0.00, α = 1.92 ± 0.00, α = 1.97 ± 0.01,
and α = 1.80 ± 0.00 for records, articles, sources, topics,
respectively. We note that the fit to topics provides a negative
check because it should fail. After all, the fit to topics is
statistically distinguishable from a power law, is limited in its
range, and the estimate of β from panel d does not account
for the curvature in the median sales by topic. Accordingly,
we find that the exponent scaling relation in Eq 2 is least well
satisfied for topics with error of ∆ ≡ αˆ−α = 0.15±0.03, but is
better satisfied for the remaining quantities ∆ = −0.11 ± 0.01,
∆ = −0.10±0.02, and ∆ = 0.00±0.02 for records, articles, and
sources, respectively. While one has to be careful with startups
and the smallest firms which show much more variability in
information and economic behavior (32), our scaling models
establish a basis for comparison relative to an expected trend.
Indeed, that the exponents are close to satisfying the exponent
relation Eq 2 — despite β having been extracted for a small
subset of public firms in COMPUSTAT and α from all firms in
the reading data — indicates that our scaling approximation
is reasonably self-consistent.

Limits to information variety

More reading does not necessarily imply new information for
the firm. As we show in the Heaps’ plot in Figure 3, we
compare the number of unique articles A, sources S, or topics
T with the total number of times the firm accessed content, or
left a record R (34). For a given logarithmic bin for records
R, we plot the average number of items read by firms (blue
markers) below the maximum (orange). Both data points grow
sublinearly with R in every panel. This is sensible because
we know that a single employee might read the same article
several times or share it with colleagues such that this plot
would at maximum trace the black, dashed, one-to-one line.
Furthermore, the three Heaps’ plots all show qualitatively
similar patterns of two distinct regimes: the least read (small
R) firms saturate the variety of articles and the most read
(large R) firms fail to saturate this curve. This means that
small firms with the most diverse reading tendencies saturate
the maximum number of articles they could read per record
but that at a larger size, the most diverse readers peel away
from linear growth, indicating that the same articles A, sources
S, and topics T are reread.

We model how such a transition may occur with a simplified
picture of how firms process information and extract benefits
as in Figure 4. We picture each record to be a point in a
high-dimensional information space as indicated by the arrows.
Each employee has some expertise, corresponding to a volume
in the same space; this can be represented as a “ball” with a

The exponents α < 2 for records and articles indicates
heavy-tailed distributions of firm information search and thus

Lee et al. December 19, 2023 | vol. XXX | no. XX | 3
R
*

mean
max
mean fit
max fit
linear

ticle
s

A

a

r

(a)

s

o

u

r

c

e

s

S

R
*

Fig. 4. Diagram of information processing model. Firm consists of organizational
units, each with a range of expertise in a high-dimensional space of information,
here projected onto two dimensions. If an article falls into the range of expertise
of a unit, the firm can realize a benefit (Eq 3). In small firms below the percolation
point, teams hardly fill the space, and in large firms above the percolation point teams
overlap substantially. The percolation point is the point at which the majority of units
begin to touch. Below it, organizational units generally do not overlap, and above it
organizational units generally do. Our formulation is general and allows for a wide
range of interpretations that are consistent with the probabilistic formulation such as
variations of goal-directed search, random realization of the economic benefit, biased
distribution of information and teams in the space, information that is passed around
the firm to find an expert, amongst others.

(b)

R
*

t

o

pic
s

T

DRAFT

(c)

0 10
3 10

records R

to a firm with no organizational grouping. Simultaneously,
firms are limited in the total amount of incoming information
they can process regardless of overlap with expertise, a quantity
that we model as a scaling with the number of employees
of N
a
. As before, the typical number of successful intersections
between an information piece and an organizational unit
yields a total economic benefit B. Assuming that cost of new
information is proportional to its frequency (i.e. it pays for
itself),∗ we would expect that B is proportional to the total
new information

Fig. 3. Diversity of information collected by firms as Heaps’ plots for firm reading.
Growth of (a) articles A, (b) sources S, and (c) topics T with number of records R
along with fits of information-overlap model as lines. For a given logarithmic bin R, we
show the firms with maximal variety in reading (orange markers) and firms with mean
reading variety (blue markers). While the total number of articles (A ∼ 40 million)
and sources (S ∼ 800,000) is much greater than what any single firm accesses in
the subsample, the number of topics is bounded at T = 4,338. To avoid overfitting
to the cutoff, we scan over a range of values and only take fit values that are of
sufficiently low error and do not violate physical limits (more details in Appendix ??).
Estimated team size scaling exponents are b ≈ 3/10 for both mean and max curves
for articles. For sources, b ≈ 1/3 and b ≈ 2/5 for mean and max, respectively. For
topics, b ≈ 1/2 and b ≈ 2/3. Points R
∗
at which the maximal curves fall below
90% of the 1:1 line are indicated with arrows R = 1,645 records for articles, R = 41
records for sources, and R = 18 records for topics.

a
h

Nb
i

Itot ∼ B ∼ N

1 − (1 − p)

. [3]

Eq 3 predicts three regimes. First, there is a regime in
which each additional organizational unit contributes more or
less independently to the expertise of the firm, maximizing
the benefit of each organizational addition. Then, there is a
relatively sharp, exponential turning point at which the organizational
units suddenly saturate the space of information and
when every new piece of information almost always intersects
with some unit’s expertise. Thereafter, benefits from filling
the space are marginal, but the rate of new information is only
determined by a universal rate N
a
at which organizations read.
Since this is also the regime in which organizational units overlap
in expertise, this is compatible with the observation that
for large firms the dominant limit is not cumulative expertise
but the fact that units must coordinate. Thus, Eq 3 presents a
testable prediction for how the way that firms fill the space of
information and the onset of a coordination problem manifest
in the cost of reading.

characteristic radius r. Then, we assume that firms extract
some economic benefit B from each piece of information if
there is overlap between the expertise of an employee and
the information content of a record. The chance that the
record intersects with the expertise of the employee is the
ratio of the size of the ball to the volume of the space, or the
fraction p. Considering a firm with N employees in a large
information space, the probability that the piece intersects
with the expertise of at least one employee is 1 − (1 − p)
N .
The result is exponential convergence to full coverage with
employee number, or the prediction of a sudden turning point
as a firm goes from a small size with a sparse covering to a
large one with a dense covering of the information space.

The level at which useful information is extracted, however,
is typically not relegated to a single employee but an organizational
unit (e.g. teams, branches, etc.), which may serve as
a collection of expertise relatively independent of other units.
Then, it is more accurate to consider a scaling relation of
the organizational unit with the number of employees N
b
for
a positive and sublinear exponent b, which implies that the
probability of finding at least one unit with the right expertise
is 1 − (1 − p)
Nb
, where b = 1 as considered above corresponds

To fit the model to the data, we minimize the least-squares
error on a logarithmic scale. While we have a sufficiently wide
range of data to simply fit articles and sources, we are limited
in the number of topics, which leads the curve to flatline at
about R ∼ 103
. A natural solution seems to be to fit to the
∗
If it were to pay more than for itself, we would anticipate that more information would be consumed
and if it paid for less than the amount would be reduced. In other words, the marginal benefit should
equal the marginal cost.

4 | Lee et al.
part of the curve that comes before the flatline, but this leads
to the problem of choosing the maximum values Rmax below
which to fit. Since there is no definitive point to which to
restrict ourselves, we instead vary the cutoff Rcutoff a wide
range. Helpfully, we find the errors to be large when we restrict
ourselves to fit a range 102 ≲ R ≲ 103
records, but they
suddenly drop at larger R. There, we find a range in which
the exponent a that determines the extrapolated region stays
within a narrow range. Finally, we find beyond 103 ≲ R ≲ 104
that the exponent for the mean curve a exceeds that for the
maximum curve, which is physically impossible and a indication
that the curves overfit the flatline (see Appendix ?? for
more details). Thus, we find a natural fitting regime in which
the extrapolation remains consistent while not overfitting the
data cutoff.

a

s

s

e

t

s

A

data
mean
max

1 10
3 10
5 10

topics T

Remarkably, our model matches closely the curves in Figure
3. Using the scaling relation between records R and
employees N to replace N with R, we fit the prediction in
Eq 3 to the Heaps’ plots in Figure 3. The data agree extraordinarily
well with the mean and maximum curves predicted from
the emergence of a coordination problem shown in the blue
and orange curves, respectively. Importantly, our estimate
for the exponent b, how team size scales with the nmber of
employees, are all sublinear. For the mean curves, we find for
articles, sources, and topics, b ≈ 3/10, b ≈ 1/3, and b ≈ 1/2,
respectively. For maximally diverse reading, we find b ≈ 3/10,
b ≈ 2/5, and b ≈ 2/3. Sensibly, the increasing values indicate
that bigger collections of employees map onto larger aggregates
of information.

Fig. 5. Predicted asset growth with topics from combining the information processing
model from Figure 3 and the scaling between assets and records (Table ??). Gray
points indicate public firms. A superlinear curve in the tail indicates increasing assets
per topic read, whereas a sublinear curve decreasing assets per topic read, or an
intensive vs. extensive strategy, respectively. Linear scaling indicates proportional
growth in assets with topic variety such as if investments were split equally across
them. Best estimates for scaling in the tail are approximately A ∼ T
for the mean
and A ∼ T
for the max, which both correspond to intensive strategies. Shaded
regions indicate 95% confidence intervals as defined in Appendix ??. Bottomost error
bars extend to sublinear scaling, or roughly as A ∼ T
.

DRAFT

to be older (32), the ratio of A/T may reflect as aspect of
strategy that we distinguish as either “intensive” (superlinear)
or “extensive” (sublinear).

The observation that larger groups matter for larger aggregations
of information also manifests in the place at which
the maximum variety curves peel away from the one-to-one
line. When the inflection point is defined as the number of
records at which the quantity in question first reaches 90%
of linear growth, it occurs at R = 1,645 records for articles,
R = 41 records for sources, and R = 18 records for topics.
Using our measured scaling relations, the points correspond
to publicly listed assets and annual sales of typically $900
million and $100 million, $80 million and $6 million, and $40
million and $3 million, respectively. That the variation of the
inflection point maps to firms of different sizes suggests that
firms may pass through critical sizes at which the amount of
new information of a certain granularity cannot be processed
in the same way.

To determine γ, we must rely on the previous relations for
assets A as a function of records R from Figure 1, which was
approximately A ∼ R
, and the predicted relation between
topics T and R given by exponent a measured in Figure 3.
For firms of mean reading variety, we found a ≈ 1/4 and
for firms of maximal variety we found a ≈ 1/2. Putting the
relations together, we estimate for large firms the relations
A ∼ T
and A ∼ T
, respectively. Confidence intervals of
95% on the values of a range from [0.05, 0.34] and [0.28, 0.78]
correspond to γ ranging from [0.07, 0.50] and [0.41, 1.15]; thus,
they remain mostly confined to the superlinear regime, if not
entirely. Overall, this is consistent with the picture of a firm
that retains a fixed set of interests into which it reinvests
assets, although they also allow for rare instances of alternative
“silo” and extensive strategies. Taken together with our
other findings, this observation indicates how the information
dimension may reflect elements of organizational structure.

Information intensive vs. extensive growth
As the final comparison, we consider how firm size relates to
topic variety. As a start, we might anticipate three qualitatively
different scenarios relating size such as assets A with
topic variety T, or the relation A ∼ T
γ
for positive exponent γ.
If firms were to focus on core competencies, we might expect
superlinear scaling of γ > 1 since that means firms tend to
reinvest topics that they already read. Then, we would expect
that the ratio of assets per topic A/T ∼ T
γ−1
increases. In
the linear case γ = 1, we would find that a fixed unit of asset
growth corresponds to the addition of a topic, or a siloed portrait
of a firms such as might be expected from the separate
acquisitions of a conglomerate that remain unintegrated. The
final, sublinear case γ < 1 would be unusual because it would
suggest that assets are being divested from existing interests
while more go into an enlargened set. Since larger firms tend

Discussion

How groups of biological organisms exchange information to
coordinate individual components has been major area of interest
in the study of collective behavior (3, 5, 35). Yet, it
is difficult to query the cognitive state of the individual, and
a sophisticated experimental apparatus is crucial to control
and track the information that individuals are receiving and
generating (3, 36–39). In organizations, much transmitted
information is recorded and its content understandable; instead,
the scale and complexity of the information is little
understood quantitatively. Thus, the firm presents a complementary
opportunity to study information flows. We leverage
such information at a wide scale to study on the amount of

Lee et al. December 19, 2023 | vol. XXX | no. XX | 5
information that organizations, primarily firms, consume and
focus on how such information is connected to firm size.

three types of firm strategy that would correspond to each
one. The differences are summarized in the ratio of assets to
topics A/T that either grows, stays constant, or shrinks with
firm size. We find that nearly the entire range compatible
with the fit to data corresponds to an increasing ratio, or an
intensive strategy, consistent with other measures (43). This is

We first show a sublinear relationship between the size and
the information footprint of a firm in Figures 1 and 2. The
main implication of the sublinear scaling is that the effective
cost of an additional unit of information shrinks, signaling an
“economy of scale.” This observation aligns with the intuition
that the tools of the knowledge economy such as information
technology use enhance firm productivity (40, 41). As part of
this, the typical large firm accesses more records and consumes
more articles per employee, which implies that its employees
on the whole are more productive at processing elementary
information. The sublinear scaling leads to an information
consumption inequality that is an exaggerated version of the
economic inequality between firms given by the classic finding
of Zipf’s law in US Census data (29). We validate this by
measuring the exponents of power-law tails in the distributions
of firm information consumption α, finding an exaggerated
tail for records and articles of α < 2. Sources, in contrast,
show nearly linear scaling, and we confirm that the power
law tail is Zipfian, or α = 2. Flipping the axes around by
taking information as the driver, the inverse perspective is

in contrast with the economy of scale for records and articles.
The difference may reflect the fact that expanding the interests
of a firm is not as simple as reading another article, but it
may involve a structural cost (e.g. hiring the right employees
and setting up management structures) reflected in processing
higher levels of information.

In each of these macroscopic trends, we find indications that
organizational units, not the individual employees, play a role
in information consumption. These echo the classic ideas that
organizational structures are crucial for the “absorptive capacity”
of a firm (13), the way knowledge is stored or exploited
(44), and the role of teams (45) and organizational structure
(46) on performance. Here, we provide another piece of the
puzzle by measuring aspects of information consumption that
elucidate the information behavior of employees. Information
use by individuals follows a parallel line of work in biological
collectives, where we have begun to connect individual-level
information exposure and cognition to group-level capabilities
(47–50). How information consumption captures the capacity

DRAFT

of a superlinear increase in information required to “power”
unit economic growth, or one of diminishing returns. The
two perspectives, while compatible with the same scaling laws,
correspond to different causal mechanisms for the drivers of
productivity in firms.

or interaction-structure in firms remains an open question.
As a start, how firms vary in such organization as would be
reflected in information use suggests one way to distinguish
systems from one another or to highlight unusual ones. Large
deviations from patterns extracted over many millions of firms
are likely to represent surprising activity that demands further
attention. In this sense, our work suggests a way forward for
understanding why and how firms use information and the
principles that organize information processing in social and
biological systems.

The change in the scaling from sublinear to linear as we
change information granularity is curious. This is summarized
in the scaling exponents β in Figure 2, which indicate the
strongest economy of scale for records and articles and the
weakest for topics. One possible reason for the variation is
that processing diverse information at larger scales is more
complicated. Gaining something out of a whole new topic
may require restructuring of the firm such as adding a division
or changing the corporate mission, whereas reading a new
article on the same topic is trivial. This would mean that firm
growth in information space at the coarsest levels is more tied
to economic growth, echoing the role of intangible aspects in
determining firm costs (42). The observations suggest two
different ways in which information costs may reflect firm
growth, either through an increasing economy of scale or
reflecting the demands of diversification.

Acknowledgements
We thank the Complexity Science Hub Theory Group including
Tuan Pham, Jan Korbel, and Stefan Thurner and others
including Ernesto Ortega, Chris Kempes, and Geoffrey West
for useful discussions. We thank Maria del Rio-Chanona for
comments on a previous draft. E.D.L. acknowledges funding
from BMBWF, HRSM 2016 (Complexity Science Hub Vienna)
and the Austrian Science Fund under grant number ESP 127-
N. F.N. acknowledges financial support from the Austrian
Research Agency (FFG), project #873927 (ESSENCSE).

As a second observation, we show that the volume of firm
online reading is limited in its variety because the number of

read articles, sources, and topics scales sublinearly with volume
in the Heaps’ plots of Figure 3. Even the most diversely
read firms are redundant readers above a critical size, and the

Data availability
Anonymized code for analysis can be made available upon
request, but data presented are proprietary, and we must
consider requests for data access for reproducibility on a caseby-case
basis.

critical size depends on information granularity. By considering
how the expertise of organizational units in a firm tile
the space of information (Figure 4), we predict the emergence
of a transition when the organizational units in a firm begin
to overlap in expertise. Overlap means the point at which
coordination or conflict between units becomes an issue. This
model yields a prediction that fits the data remarkably well,
indicating that organizational constraints may leave traces in
the information footprint.

1. Couzin ID, Krause J, Franks NR, Levin SA (2005) Effective leadership and decision-making in
animal groups on the move. Nature 433(7025):513–516.

2. Ballerini M, et al. (2008) Interaction ruling animal collective behavior depends on topological

rather than metric distance: Evidence from a field study. Proc Natl Acad Sci USA 105(4):1233–
1237.

Finally, we connect reading variety to firm size by using
the scaling relations found in the previous analyses Figure 5.
Inspired by the qualitative differences that could emerge for
the scaling relations relating the two properties, we predict

3. Rosenthal SB, Twomey CR, Hartnett AT, Wu HS, Couzin ID (2015) Revealing the hidden

networks of interaction in mobile animal groups allows prediction of complex behavioral
contagion. Proc. Natl. Acad. Sci. U.S.A. 112(15):4690–4695.

4. Hartnett AT, Schertzer E, Levin SA, Couzin ID (2016) Heterogeneous Preference and Local
Nonlinearity in Consensus Decision Making. Phys. Rev. Lett. 116(3):038701.

6 | Lee et al.
5. Brush ER, Krakauer DC, Flack JC (2013) A Family of Algorithms for Computing Consensus
about Node State from Network Data. PLoS Comput Biol 9(7):e1003109.
6. Wuchty S, Jones BF, Uzzi B (2007) The increasing dominance of teams in production of
knowledge. Science 316(5827):1036–1039.
7. Nonaka I, Takeuchi H (1995) The Knowledge-creating Company: How the Japanese Companies
Create the Dynamics of Innovation. (Oxford University Press).
8. Bhatt AM, Goldberg A, Srivastava SB (2022) A Language-Based Method for Assessing
Symbolic Boundary Maintenance between Social Groups. Sociol. Methods Res. 51(4):1681–
1720.

50. Shishkov O, Peleg O (2022) Social insects and beyond: The physics of soft, dense invertebrate
aggregations. Collective Intelligence 1(2):263391372211237.

9. Simon HA (1979) Information Processing Models of Cognition. Ann. Rev. Psychol. 30:363–96.
10. Katz R, Allen TJ (1982) Investigating the Not Invented Here (NIH) syndrome: A look at
the performance, tenure, and communication patterns of 50 R & D Project Groups. R & D
Management 12(1):7–20.
11. Katz Y, Tunstrøm K, Ioannou CC, Huepe C, Couzin ID (2011) Inferring the structure and
dynamics of interactions in schooling fish. Proc. Natl. Acad. Sci. U.S.A. 108(46):18720–18725.
12. Simon HA (1962) New Developments in the Theory of the Firm. The American Economic
Review 52(2):1–15.

13. Cohen WM, Levinthal DA (1990) Absorptive Capacity: A New Perspective on Learning and
Innovation. ASQ 35(1):128–152.
14. Granovetter MS (1973) The Strength of Weak Ties. AJS 78(6):1360–1380.
15. Burt RS (2004) Structural Holes and Good Ideas. Am. J. Sociol. 110(2):349–399.
16. Strogatz SH (2001) Exploring complex networks. Nature 410(6825):268–276.
17. Albert R, Barabási AL (2002) Statistical mechanics of complex networks. Rev. Mod. Phys.
74(1):47–97.

18. Watts DJ, Strogatz SH (1998) Collective dynamics of ‘small-world’ networks. Nature 393:440–
442.

19. Deming DJ (2017) The growing importance of social skills in the labor market. The Quarterly
Journal of Economics 132(4):1593–1640.
20. Neffke FM (2019) The value of complementary co-workers. Science advances 5(12):eaax3370.
21. Girvan M, Newman MEJ (2002) Community structure in social and biological networks. Proc.
Natl. Acad. Sci. U.S.A. 99(12):7821–7826.
22. Hall BH, Harhoff D (2012) Recent Research on the Economics of Patents. Annu. Rev. Econ.
4(1):541–565.

DRAFT

23. Jaffe A, Trajtenberg M, Fogarty M (2000) The Meaning of Patent Citations: Report on the
NBER/Case-Western Reserve Survey of Patentees, (National Bureau of Economic Research,
Cambridge, MA), Technical Report w7631.
24. Youn H, Strumsky D, Bettencourt LMA, Lobo J (2015) Invention as a combinatorial process:
Evidence from US patents. J. R. Soc. Interface 12(106):20150272.
25. Kwan A, Zhu C (2019) Does Internet Research Activity by Sophisticated Investors Lead to
Heightened Adverse Selection? SSRN Journal.
26. Kwan A, Liu Y, Matthies B (2022) Institutional Investor Attention.
27. Hoberg G, Phillips G (2018) Conglomerate Industry Choice and Product Language. Management
Science 64(8):3735–3755.
28. Hoberg G, Phillips G (2016) Text-Based Network Industries and Endogenous Product Differentiation.
Journal of Political Economy 124(5).
29. Axtell RL (2001) Zipf Distribution of U.S. Firm Sizes. Science 293(5536):1818–1820.
30. Teece DJ, Rumelt R, Dosi G, Winter S (1994) Understanding corporate coherence. Journal of
Economic Behavior & Organization 23(1):1–30.
31. Hidalgo CA (2021) Economic complexity theory and applications. Nat Rev Phys 3(2):92–113.
32. Zhang J, Kempes CP, Hamilton MJ, West GB (2021) Scaling laws and a general theory for the
growth of companies. arXiv:2109.10379 [physics].
33. Clauset A, Shalizi CR, Newman MEJ (2009) Power-Law Distributions in Empirical Data. SIAM
Rev. 51(4):661–703.

34. Heaps HS (1978) Information Retrieval, Computational and Theoretical Aspects. (Academic
Press).

35. Couzin ID, Krause J (2003) Self-Organization and Collective Behavior in Vertebrates in
Advances in the Study of Behavior. (Elsevier) Vol. 32, pp. 1–75.
36. Noy L, Dekel E, Alon U (2011) The mirror game as a paradigm for studying the dynamics of
two people improvising motion together. PNAS 108(52):20947–20952.
37. Minderer M, Harvey CD, Donato F, Moser EI (2016) Neuroscience: Virtual reality explored.
Nature 533(7603):324–325.
38. Stowers JR, et al. (2017) Virtual reality for freely moving animals. Nat Meth 14(10):995–1002.
39. Lee ED, Esposito E, Cohen I (2019) Audio cues enhance mirroring of arm motion when visual
cues are scarce. J. R. Soc. Interface 16(154):20180903.
40. Stiroh KJ (2002) Information Technology and the U.S. Productivity Revival: What Do the
Industry Data Say? The American Economic Review 92(5):1559–1576.
41. Black SE, Lynch LM (2004) What’s Driving the New Economy? The Benefits of Workplace
Innovation. The Economic Journal p. 20.
42. Black SE, Lynch LM (2001) How to Compete: The Impact of Workplace Practices and
Information Technology on Productivity. The Review of Economics and Statistics 83(3):434–
445.

43. Hoberg G, Phillips GM (2023) Scope, Scale and Concentration: The 21st Century Firm.
44. Kogut B, Zander U (1992) Knowledge of the Firm, Combinative Capabilities, and the Replication
of Technology. Organ. Sci. 3(3):383–397.
45. Wu L, Wang D, Evans JA (2019) Large teams develop and small teams disrupt science and
technology. Nature 566(7744):378–382.
46. Stanley MHR, et al. (1996) Scaling behaviour in the growth of companies. Nature
379(6568):804–806.

47. DeDeo S, Krakauer DC, Flack JC (2010) Inductive Game Theory and the Dynamics of Animal
Conflict. PLoS Comput Biol 6(5):e1000782.
48. Kao AB, Miller N, Torney C, Hartnett A, Couzin ID (2014) Collective Learning and Optimal
Consensus Decisions in Social Animal Groups. PLoS Comput Biol 10(8):e1003762.
49. Lee ED, Daniels BC, Krakauer DC, Flack JC (2017) Collective memory in primate conflict
implied by temporal scaling collapse. J. R. Soc. Interface 14(134):20170223.

Lee et al. December 19, 2023 | vol. XXX | no. XX | 7
Appendices to “Information consumption and size

in firms”

Edward D. Leea

, Alan P. Kwanb

, Rudolf Hanela

, Anjali Bhattc

, and Frank Neffkea

aComplexity Science Hub Vienna, Vienna, Austria; bHong Kong University, Hong Kong, China; cHarvard Business School, Boston, USA

This manuscript was compiled on December 19, 2023

A. Data preprocessing
The data set consists of access records of news content that is
within the universe of publishers monitored by a firm specializing
in “intent” data, hereafter called the “Data Partner.” As
we specify in reference (? ),

relevant to business, trained on a set of articles from sports,
adult, and entertainment websites versus a set of articles from
well-known business publishers. After filtering the content
which is likely to discuss business-relevant content, the Data
Partner runs a multi-label model which calculates the article’s
topic relevancy to the current taxonomy of topics, which during
our sample period was around 4,000 topics (not all are
commercially sold). The intersection of content which can
be mapped to a firm, and content which can be mapped to
a business, is about 10-15% of the total content observed by
the Data Partner (consisting of over one billion article read
events per day). Thus, although it is not clear that all information
consumed by the organization is done so for productive
purposes, the filters applied toward the content and visitors
suggests that information consumption events observed in this
study contain the subset of observations most likely to come
from work-related visitors and work-related content.

arXiv:2210.07418v3 [physics.soc-ph] 17 Dec 2023

‘Intent’ refers to a recent strain of data analytics
aiming to gauge a prospective business customer’s
buying interest based on patterns of reading on the
internet. If a given business customer’s reading on
a particular topic increases at a rate relative to a
baseline, one might presume the business customer
has a greater ‘intention’ of transacting in a related
service as this increase in reading is indicative of the
research that occurs prior to a purchase.

DRAFT

Each record, in principle, does not identify who is accessing
the content, only the origin of the request, or the IP address,
as well as metadata associated with the visitor, known as
a “cookie.” Cookies allow a user to be observed through
different visitor sessions. Using methods standard in the digital
marketing industry, the Data Partner links various website
visits to a given firm. The Data Partner analyzes the textual
content and uses proprietary topic model implementation
to extract a set of hand-labeled, customer-relevant topics
associated with each page of content. Thus, we have a database
of which devices are accessing what and information about
the content in question.

To provide some context, here we provide a breakdown
of articles by publisher type in terms of their IAB category
(a common taxonomy for content developed by the Interactive
Advertising Bureau, https://iabtechlab.com/standards/
content-taxonomy/) as well as the AlexaRank. While imperfect,
these are two popular classifications applicable to all websites
across the Internet. They suggest that the plurality of the
information observed in this study come from major news and
business publishers but the content altogether is diverse.

The data is proprietary and the analyses are run on big
data sets, so we cannot feasibly rerun our own preprocessing.
However, we can take some steps to mitigate potential
limitations of the data set.

For the topic model, the Data Partner runs a binary classification
model which seeks to filter out content which is not

1. One consideration is that the topic list is updated over
time to account for changing data sources and customer
interests. To limit this time-varying effect, we focus on
a two-week period between June 10, 2018 and June 23,
2018 in the time zone GMT, for which we do not have any
reason to believe is unusual relative to other points in the
data set, which represents a large number of labeled topics,
and that does not have changes in topic preprocessing.
Within this time frame, the preprocessed data consists of
4,338 unique topics with more than 3.5 million firms as
identified by their domains, and day-to-day statistics are
similar.

2. Some of the extracted topics may not describe well the

content at hand, so we impose a lower threshold on the

Fig. S1. Information falls across multiple layers of resolution from articles (gray circles)
provided by on different pages at a publisher’s website, or sources (blue circles), which
can be related by topic (dashed circles). Articles form the most unstructured view of
the data and each article can belong to multiple sources or topics that form different
scales for analysis. Here, we consider a copy of the same article on a different content
provider as a separate article.

E.D.L. designed the project. E.D.L., A.P.K., and A.B. participated in initial discussions. E.D.L., F.H,
and R.H. discussed the results. A.P.K. and E.D.L. processed the data. E.D.L. did the analysis, wrote
the code, and initially drafted the manuscript. E.D.L., F.N., A.P.K., and R.H. edited the manuscript.
The authors declare no other competing interests.

2To whom correspondence should be addressed. E-mail: edlee@csh.ac.at

Table S1. IAB classifications of the top-level domains (provided by
Data Partner) breaking down the percentages of articles across the
publisher types and publisher web traffic rank, per AlexaRank, from
the year 2019.

1.0

0.8

0.6

IAB % Total IAB name
IAB12 21.77 News

CDF

0.4

IAB3 8.81 Business
IAB13 8.41 Personal Finance

data
cutoff

0.2

IAB19 7.79 Technology, Computing
IAB9 6.37 Hobbies, Interests

0.000 0.025 0.050 0.075 0.100
mean relevancy by firm
0.0

IAB25 5.48 Non-Standard Content
IAB1 5.27 Arts, Entertainment
IAB5 4.22 Education
IAB22 4.07 Shopping
IAB17 3.68 Sports
IAB15 3.39 Science

Fig. S2. Cumulative distribution function (CDF) over firms of the firm-averaged
relevancy scores. We use a 95th percentile threshold to remove firms whose reading
habits are not well captured by the topic modeling (dashed black line).

IAB7 3.08 Health/Fitness
IAB8 2.45 Food / Drink

IAB11 2.37 Law, Gov’t, Politics
IAB20 1.88 Travel

2.8 million domains, only 8,477 were US government affiliated.
In terms of records, they constitute less than 4% of the data.
As for academic institutions, we consider them to be firms
for the purposes of our analysis, but domains with a .edu
suffix (either alone or followed by country-specific domain)
also constitute about 9,152 and about 13% of the records.
Thus, the vast majority of the data we analyze corresponds
to non-government, non-educational entities, and there is little
indication that government agencies are unusual in our
analyses.

AlexaRank % Total Reading
[1 − 1000] 27.87
[1000 − 10000] 17.59
[25000 − 50000] 7.32
[50000 − 500000] 5.56
[500000 − 106] 15.91
> 106 25.75

DRAFT

topic relevance value. We first calculate the typical relevancy
over the set of all topics for each firm for a given
day. When firm average relevancy falls in the bottom 5th
percentile, we remove it from consideration as we show in
Figure S2. This allows us, in our cross-firm comparison,
to only consider firms that are well-represented within
our given, bounded universe of topics.

B. Fitting size scaling with reading volume

In Figure ??, we compare various measures of firm size Y
with the amount that firms read in terms of records R in the
data set to establish a sublinear relationship. It is natural,
however, to consider the converse relationship of how reading
volume scales with measures of firm size. This presents two
different ways of considering fitting the data to obtain a scaling
relationship, where the “independent” variable is either firm
size or reading volume. It is not in general expected that the
fits resolve the same scaling relationship. In other words, it
is not necessarily the case that our finding Y = ARb when fit
with the reversed axes returns R = (Y /A)
1/b with the same fit
parameters A and b as would be the case under an invertible
scaling relation.

3. We exclude Amazon because it is a clear outlier by over

an order of magnitude in terms of records, which most
likely indicates that customer behavior was incorrectly
flagged as employee behavior such as through Amazon
Web Services. This is also a possible source of error in
other cloud or internet service provider firms like Comcast
and Microsoft, but there is no clear indication that they
are outliers as is the case with Amazon.

One solution is to use a symmetric cost function that accounts
for logarithmic errors along both the x and y axes
simultaneously, guaranteeing an invertible relationship. A
more sophisticated technique would be total factor correlation,
which accounts for the principle dimension through which the
data passes (). We do not rely on either of the two techniques
because there is clear asymmetry in the fit error distributions
that is attributable to known biases in the reading data
and we do not have a good model of the corresponding error
distribution.

Once the above steps have been taken, we have a selection of
firms with some basic statistics plotted in Figure S3. Thus, we
are considering roughly 106 firms per day and the distribution
of unique topics accessed by any given firm displays a power
law tail.

Besides businesses, the data set contains government agencies,
non-governmental organizations, academic institutions,
and entities registered with a domain. While we could filter
out some of the organizations, it is unclear if such pruning can
be done in a consistent way across all countries especially when
considering that firms in many countries are closely tied to
the government such as Saudi Arabia’s Aramco and Russia’s
Gazprom, to name a couple. As a check of how large an effect
government organizations might have on the data set, we took
an extensive list of 9,225 US government and governmentaffiliated
URLs from https://github.com/GSA/govt-urls in addition
to top-level “.gov” and “.mil” domains to find that of over

As an example of what happens when we use firm measures
as the independent variable is shown in Figure S4. Whereas the
regression that we show in the main text — using logarithmic
least-squares along the y-axis — cuts right through the median
data, a regression along the other axis does not. This reflects
the fact that the reading coverage is uneven over firms, so
there are many firms large and small for which coverage is
sparse (see Figure S5). This means that once we condition

2 | Lee et al.
on firm size, and especially for large firms where we have few
data points, skewed observations matter inordinately for the
mean (note that conditioning on firm size is separate from
averaging over firms with a large number of records as we
do in our later analysis). In contrast, firm size measures
from COMPUSTAT are complete and public firms must abide
by the standardized accounting and disclosure regulations
in place. Reflecting the comprehensive nature of firm sizes
measures, we recover error distributions that are much closer to
normal and pass through the median data points for firm size
distributions, indicating that a logarithmic least-squares fit is
tenable. Thus, we perform our fits to the relationship between
firm size and reading only considering the errors for which we
can be reasonably confident as being well-characterized with
a simple fitting cost.

(a)

no. of firms

2018-06-10
2018-06-11
2018-06-12
2018-06-13
2018-06-14
2018-06-15
2018-06-16
2018-06-17
2018-06-18
2018-06-19
2018-06-20
2018-06-21
2018-06-22
2018-06-23

C. Heaps model specification

no. of firms

As a hypothesis for how firms process the incoming flow of
information, we picture a shared information space in which
articles and organizational units in the firm live. The assumptions
are that the intersection of an article (a point in the
high-dimensional information space) with the radius of expertise
of an organizational unit leads to a benefit for the firm.
The prediction made by this model is summarized in the main
text in Eq ??.

(b)

DRAFT

day
2018-06-10
2018-06-11

1 10

In order to fit our model to the data, we minimize the
squared logarithmic distance to the data points that are shown
in Figure ??. For articles and sources, the procedure is straightforward
because we are unconcerned about saturating the full
number of articles or sources in the data set under the period
of study, so we fit to the variety count at each logarithmic
bin in Figure ?? as long as there are at least five observed
firms and the firm with the minimum number of reads has
more than one record (an indication of undersampling). For
topics, however, fitting to the full range of records would mean
that we are also fitting to the point where the finite number
of observed topics caps the relationship between records and
topics.

no. of topics

Fig. S3. (a) Number of firms in database per day beforing filtering out firms with low
mean topic-relevancy and subsampling. (b) Distribution of firms by number of topics
across all queries on June 10, 2018 appears to be a scaled version of June 11.

a

s

s

e

t

s

(

U

S

D

)

(a) P
P

E

(

U

S

D

)

To minimize the impact of the cutoff, we fit only to a limited
regime far before the curve flattens out at large R for topics.
The limited regime also means, however, that the fit is much
more sensitive to small aberrations in the data at the end
of small firms, which are noisier and would be more strongly
affected by bots. We solve this problem in two steps. First, we
do not fit to the entire curve but consider a principled upper
cutoff at the turning point that we identify earlier 90% of the
1:1 one, or R ≤ 178. As a result, however, the fit jumps to
fractional values for small values of R, which is not physically
possible. To solve this problem, we increment the lower cutoff
until we recover a fit that goes through the data points and
remains greater than unity. We find that for the mean curve
(blue), we are limited to the range 11 ≤ R ≤ 178 and for
the maxima (orange) 1 ≤ R ≤ 178. Note that the curvature
of the data in the Heaps’ plots are different from that of a
null model where firms are randomly sampling from the set
of articles, sources, and topics that we have in the data R
times. In the latter case, the mean reading variety curves run
almost completely along the 1:1 line. The fact that firms are
systematically re-reading items is reflected in the nontrivial
exponents that we find for team-size scaling b and the limits
to large-firm reading a. Thus, the fits to the Heaps’ curves

(b)

s

ale
s

(

U

S

D

)

data
fit

employees

(c)
Utilities
Services

(d)

0 10
3 10
records

0 10
3 10
records

Fig. S4. Relationship between firm size measures and reading volume R. Logarithmic
regressions using least-squares but with errors along the x-axis are shown as black
lines. Medians along the measures of firm size are shown as black x’s.

Lee et al. December 19, 2023 | vol. XXX | no. XX | 3
Table S2. Scaling exponents for economic against information footprint.
Error bars represent one standard deviation over bootstrapped
fits.

assets PPE employees sales
records 0.68 ± 0.02 0.79 ± 0.02 0.76 ± 0.01 0.77 ± 0.02
articles 0.73 ± 0.02 0.85 ± 0.02 0.82 ± 0.01 0.82 ± 0.02
sources 0.85 ± 0.02 1.01 ± 0.03 0.97 ± 0.02 0.97 ± 0.02
topics 0.95 ± 0.03 0.97 ± 0.03 0.95 ± 0.03 0.95 ± 0.03

devices

2. The function does not exceed the 1:1 line, since it is by
definition impossible to read with higher variety than the
number of items read.

0 10
2 10
4 10

3. The exponent a for the max must be strictly greater than
or equal to the exponent a for the mean; otherwise, the
mean can be greater than the maximum for large R.

employees

Fig. S5. Number of devices per employee estimates from COMPUSTAT for the quarter
ending on 2018-07-01. Black line indicates 1:1. There is a cloud of devices that
follow a linear scaling, indicating that the number of devices, for a majority of firms, is
proportional to the number of employees.

For the fits to articles and sources, the fits are straightforward
because we have a wide range of observations, and no
single firm saturates the number of unique articles or sources.
We fit the function using logarithmic least-squares and implement
the listed conditions using numerical constraints in
NumPy.

DRAFT

for articles and sources indicate that our simple model agrees
closely with the data and extrapolates the scaling of topic
variety to large firms, where the data are inadequate.

For topic scaling, we must worry about the hard, artifical
cutoff in the number of topics that we observe, so it does not
make sense to fit the entire curve; i.e. we need a maximum
cutoff Rmax. We will also have a lower cutoff because many
firms that have an appearance of R = 1 are both poorly
observed and are set with an artificial lower bound: articles
are labeled with typically T = 10. To be systematic about
the fit, we scan over a combination of lower and upper cutoffs
and calculate the fit error as we show in Figure S7c and d.
The fits separate into two bands, on the left corresponding to
larger a and larger errors for the fit, whereas on the right side
we have smaller a and better fits.

D. Sector-by-sector fits
We fit the scaling relations between firm size measures and
records for each NAICS sector that we have represented in the
database. We have taken the primary NAICS classification
code for each firm as shown in Figure S6. While there is
variation across the sectors, we find that the scaling exponents
in panel a are consistently sublinear. In the few cases where
they are not, the bootstrapped error bars indicate that we
cannot be sure of the precise value.

To identify “reasonably good” fits, we apply two criteria:
first, we leverage condition 3, assuming that sufficiently informative
regions of the curve will ensure compliance; we then
take fits that satisfy it. The second criterion we obtain from
inspecting the distribution of errors for the fit of the mean
curve across the range of lower and upper cutoffs shown in
Figure S7. The distribution is strongly bimodal as the colors
indicate, with a set of fits with normalized errors around 1/20
and below and another set with normalized errors of about 1/5
and above. Putting the two criteria together, we obtain a band
of good fits that we highlight in Figure S8. These constitute
the pairs of lower and upper limits that we consider for obtaining
the median (best fit) and the 90% confidence intervals
that we show in the main text. As we show in Figure ??, the
fits hew closely to the data below the cutoff and do not overfit,
deviating from it at large T. Most importantly, the exponent
that we focus on in the main text a, shows a distribution
that is strongly confined to a < 2/3, which corresponds to the
conservative strategy that we discuss in the main text.

E. Information space model
The information-space model that we propose in the main text
in Eq ?? has four parameters that we must fit; namely, the
exponent for information intake a, team size scaling exponent
b, the combination of fractional team size and team scaling
units C log(1 − p), and the units D. To connect it with the
data that we have on reading, we also take a scaling relation to
convert the number of employees N to the number of records R,
or N = R0R
β
. We rewrite the equation with the substitution
below,

aβ h

−CRb
0Rbβ i

Idiv = DRa
0R

1 − e

. [1]

Thus, we need only fit the parameter combinations aβ, bβ,
CRb
0, and DRa
0 . We iwll do this for the three mappings of

information variety Idiv to articles, sources, and topics. For
each of these cases, we must find a different set of parameters
that describe how team expertise overlaps in the respective
units.

We fit the parameters by numerical optimization, but logarithmic
least-squares does not ensure that the resulting functional
form satisfies physical limits. There are several criteria
that must be observed for the fits to be physically sensible:

1. The parameters must all be positive, which also ensures
that the function is positively valued in the region R ≥ 1.

4 | Lee et al.
0.0
0.5
1.0
1.5
scaling exp.
(a) assets
PPE
emp
sales

log intercept

(b)

Information
Retail Trade
Finance, Insurance
Utilities
Educational Services
Manufacturing
Professional, Scientific
Mining, Quarrying
Transportation, Warehousing Wholesale Trade
Administrative, Support
Real Estate
Health Care
Construction
Agriculture, Forestry
Arts, Entertainment
Accommodation, Food
Nonclassifiable
Other Services

DRAFT

Fig. S6. Scaling model (Eq ??) fits to each NAICS sector separately for (a) exponents and (b) intercepts. For each sector, we show the first two words of the sector name along
the x-axis. In panel a, we show a black, dashed line at linearity, and a gray, dashed line at an exponent value of 0.68, the value measured when fitting over all firms at once.

1.0

1.0

error for mean

error for max

lower limit

0.5

0.5

accept
reject

lower limit

0.0

0.0

1.0

1.0

lower limit

a

f

o

r

m

e

a

n

a

f

o

r

m

a

x

upper limit (log10)
Fig. S7. Variation in fit for exponent a in information space model. On the left, the
normalized logarithmic errors below 1/20 and fits that have errors of about 1/5 and
above. 2 4
upper limit
(log10)

0.5

0.5

Fig. S8. Region of lower and upper cutoffs for topic Heaps plot fit.

0.0

0.0

2 4

2 4

Lee et al. December 19, 2023 | vol. XXX | no. XX | 5
