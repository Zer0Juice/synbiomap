---
source: 2022_What_Can_the_Millions_of_Random_Treatments_in_Nonexperimental_Data_Reveal_A.pdf
pages: 36
extractor: pdftext
tokens_raw: 24832
tokens_compressed: 14765
compression: 41%
---

What can the millions of random treatments [...] reveal about causes?

What can the millions of random treatments in
nonexperimental data reveal about causes?

Andre F. Ribeiro andre ribeiro@hks.harvard.edu
Harvard University

79 John F. Kennedy Street, Cambridge, MA USA 02138

Frank Neffke frank neffke@hks.harvard.edu
Harvard University

arXiv:2105.01152v2 [stat.ME] 6 Nov 2022

79 John F. Kennedy Street, Cambridge, MA USA 02138

Ricardo Hausmann ricardo hausmann@hks.harvard.edu
Harvard University

79 John F. Kennedy Street, Cambridge, MA USA 02138

Editor: -

Abstract
We propose a new method to estimate causal effects from nonexperimental data. Each
pair of sample units is first associated with a stochastic ’treatment’ - differences in factors
between units - and an effect - a resultant outcome difference. It is then proposed that
all such pairs can be combined to provide more accurate estimates of causal effects in
observational data, provided a statistical model connecting combinatorial properties of
treatments to the accuracy and unbiasedness of their effects. The article introduces one
such model and a Bayesian approach to combine the O(n
) pairwise observations typically
available in nonexperimnetal data. This also leads to an interpretation of nonexperimental
datasets as incomplete, or noisy, versions of ideal factorial experimental designs.

This approach to causal effect estimation has several advantages: (1) it expands the
number of observations, converting thousands of individuals into millions of observational
treatments; (2) starting with treatments closest to the experimental ideal, it identifies
noncausal variables that can be ignored in the future, making estimation easier in each
subsequent iteration while departing minimally from experiment-like conditions; (3) it recovers
individual causal effects in heterogeneous populations. We evaluate the method in
simulations and the National Supported Work (NSW) program, an intensively studied program
whose effects are known from randomized field experiments. We demonstrate that the
proposed approach recovers causal effects in common NSW samples, as well as in arbitrary
subpopulations and an order-of-magnitude larger supersample with the entire national program
data, outperforming Statistical, Econometrics and Machine Learning estimators in
all cases. As a tool, the approach also allows researchers to represent and visualize possible
causes, and heterogeneous subpopulations, in their samples.

Keywords: Causal Effect Estimation, Experimental Design, Signal Processing, Effect
heterogeneity

1. Introduction

Most questions of interest in the social, behavioral and life sciences – What makes economies
grow? What explains criminal behavior? What can prevent or cure a disease? – are ul1
Ribeiro, Neffke and Hausmann

timately questions about what causes an outcome of interest. Data used to answer such
questions typically have no shortage of correlational patterns, but correlations are often
poor guides to the causal process that produced them. The central methodological difficulty
in scientific inquiry remains that of estimating the causal effect of a treatment, or
independent variable, on an outcome. Compared to the tremendous success of Machine
Learning algorithms in prediction and pattern recognition tasks in correlation-rich data,
such as in face recognition and textual topic modelling, Machine Learning approaches are
still of limited use when estimating causal effects (Pearl, 2019; Athey, 2017). This has led to
a paradoxical situation: in the midst of the big-data revolution, many prominent scientists
have declared randomized field experiments - with often just hundreds of participants - as
the sole standard for empirical research (Imbens, 2010; Duflo et al., 2008). Experiments
are attractive because, once individuals have been randomly divided into treated and nontreated
subgroups, it suffices to compare their average outcomes to estimate causal effects.
Yet, randomized trials have many drawbacks: they are expensive, slow and sometimes impossible
or unethical to carry out and they elucidate only if treatments work, rather than
why they work (Deaton, 2010; Imbens, 2010; Heckman and Smith, 1995). Furthermore,
a focus on average effects creates problems when different individuals experience different
effects. Indeed, Xie (Xie, 2013) (2016, p. 6263) considers this a fundamental conundrum:
’the ubiquitous presence of individual-level variability [in social phenomena] makes it impossible
to study individual-level causal effects. To draw a causal inference, it is necessary
to pool information from different members in a population into aggregates’. As we will
demonstrate, effect heterogeneity affects the accuracy of current observational methods even
in datasets of moderate size. While discourse about causes are often dominated by all-ornothing
hypothesis testing in the Sciences, there is great practical need for tools that can
introduce causal insights into the earlier phases of scientific discovery or provide insights
from larger data. Here, we study a problem representation and method that facilitates the
use of recent Machine Learning and high-dimensional techniques to that end.

1.1 Model Summary

In particular, we consider the problem of estimating Average Treatment Effects (ATE) or

Individual Treatment Effects (ITE) of a given treatment on an outcome, y ∈ R. The problem
of estimating the effect of a treatment-of-interest nonexperimentally have been studied
extensively, in particular from comparisons between treated and non-treated subjects’ outcomes
(Morgan, 2007; Stuart, 2010; Colson et al., 2016). Although for nonexperimental
estimation, these approaches often draw on Experimental Design concepts and have received
attention, especially, in Econometrics and Applied Statistics.

The central goal of the present work is to better understand and exploit the heterogeneity
of statistical conditions between pairs of individuals in everyday datasets, as they relate to

causality. Consider a nonexperimental dataset with n observations and m variables, from
a variable set X
m. An observed difference in outcome yij = yi − yj between any two
individuals, 0 < i, j ≤ n, can carry both a lot or very little information about a variable, or

variable subset, v ⊂ X m. When individuals differ only by a single variable v = {a}, strict
claims can be made for the effect of a, as the pairing characterizes an ideal counterfactual

(given conditions reviewed below). More commonly, however, pairwise conditions are in a

What can the millions of random treatments [...] reveal about causes?

spectrum of usefulness for each variable and individual. Imagine the existence of a prior
stochastic process that can describe how individual pairwise conditions translate to the

validity of pairwise observations, yij , for each variable subset v. Such model would allow us
to use all pairs, and the full range of experiments ’run by nature’, to help estimate causal
effects.

An obvious analogy is to Signal Processing and Fusion (MacKay, 2003; Hall et al., 2008),
where the use of millions of (noisy) observations often outperform any individual
observation by orders of magnitude – provided a suitable prior statistical model
for measurements. We characterize all population pairwise conditions by considering all
their possible combinations of differences and intersections. The model then connects such

combinatorial conditions to the validity of pairwise estimates. The effect f(v) of variables
v is first described as f(v) ∼ N (yij , σij (v)), which carries the assumption of Gaussian

measurements having a common mean, for each v, but distinct standard deviations σij across
pairs. In datasets below, there are in the order of 50-200M such pairs. Here, variables yij and
v are assumed observable. We relate the unobservables, f(v) and σij (v), to the asymmetric
differences of pairs under its two commutations – corresponding to the effect of ’treatments’
and their observed confounders. We also show these have straight-forward interpretations
as vector angles in covariate space. Since each pair is seen as a deviation from an ideal
factorial experimental run, it becomes useful to characterize a nonexperimental dataset,
overall, as a noisy version of an ideal Factorial Experimental Design.

Using the proposed combinatorial population model, we also derive other sources of
measurement ’noise’ from the causal effect estimation literature. The way we formulate
such added deviations is purposively standard, allowing us to later benchmark the proposed
approach (using all pairs) to alternatives selecting pairs or other popular estimators. It
would be easy to add more intricate conditions, that can be formulated combinatorically,
but we show that simple conditions outperform more complex estimators. This is the case,
for example, of estimators designed to account for unobservables and endogeneity, when
replicating the outcome of the studied Randomized Experiments.

A popular recent strategy (Louizos et al., 2017; Wang and Blei, 2020; Abadie et al.,
2015) is to stipulate prior models assuming a proxy confounding variable (either observed
or unobserved) in the data. Latent-Confounder approaches require assuming and training
complex functional models to infer the latent variable, then adjusting effect estimates accordingly.
In practice, pairs of individuals vary in how they differ, and consequently in
what variables can confound estimates in each case. Instead of requiring a single variable to
account for this potentially complex and contingent relationship, a prior statistical model
for pairwise conditions allow estimates to be considered in a pair-by-pair case - simply
penalizing pairs, or observations yij , that are ruled unfit in some fundamental way.

This article’s main contribution is therefore to demonstrate the practical benefits of
modeling and combining large numbers of disparate pairwise observations. Beyond practical
usefulness, understanding how population combinatorial patterns relate to causality is also
of great importance to population-based research, such as the study of genetic variation
in the Medical Sciences and demographics in the Social Sciences. We discuss implications
of concepts developed here to the study of genetic population variation, and Genome-wide
Association studies, in (Ribeiro, 2020).

Ribeiro, Neffke and Hausmann

observational
treatment, match, confounders

Ο(n2) observational pairs
x1Θx2 x1∩x2 x2Θx1
xi
Θxj xi
∩xj xj
Θxi

(1,2)
(1,3)
(1,4)
(i,j)
(n,n)
... yij
xi
 xj
xj xi
a
b c

-

-

a)

b)

+a

{+a,+b,+c}
{+a,-b,-c}

{+a,+b,-c}

e) multivariate
treatment
d) univariate
treatment

a
b

{+a,-b,+c}

-b
-c

f(a)

+b

{-a,-b,+c}
{-a,-b,-c} {-a,+b,-c}

f(c)

xi

{-a,+b,+c}

f) treatment with g) no treatment
obs. confounding
risk

-a

c) f(b)

3 = {a, b, c}, where xi ⊂ X 3
is a subset
describing individual i (resp. j) and 	 is set difference, illustration for the sample
balance condition xi	xj ⊥ y | xj	xi for a pairwise difference xi	xj = {a}
(’treatment’) between two individuals (ij), with xj	xi = {b, c}, (b) for a n-sized
nonexperimental sample and m factors, decomposition of the sample n(n − 1)/2
pairs into the same number of treatments (xi	xj ), matches (xi ∩xj ) and possible
confounders (xj	xi), (c) Factorial cube C
3 with factors X
3 = {a, b, c} which can
assume high and low (Boolean) values, notated +a and -a, C’s vertices correspond
to all possible factorial experimental runs and edges to treatments, vectors
(gray) depict 8 individuals’ positions according to a 8×3 standardized observation
matrix X, f(a) is the causal effect of variable a (resp. b, c) in the proposed representation;
(d-g) representative individual pairings and their implied factorial
treatments.

Figure 1: (a) for a set of population attributes X

What can the millions of random treatments [...] reveal about causes?

1.2 Sample Balance and Treatment-Assignment Ignorability Conditions

The previous discussion leads to a simple but also very conservative model, where the risk of
(observed) confounding increases with extraneous variables between pairs. We also extend
the model to account for common, more specific, conditions from the literature, such as
reduced noise for pairs satisfying treatment-covariate sample independence conditions and

with small treatments. Let xi ⊂ X m be a set of attributes describing an individual i (resp.
j) and 	 indicate (asymmetric) set-difference. The former condition, xi	xj ⊥ y | xj	xi
,
is illustrated in Fig.1(a). In the previous model, variables xj	xi were assumed capable of
confounding pairwise estimates, affecting both the treatment and outcome at the same time.
With this added assumption, the pairs where treatment-outcome variables are independent,
conditional on non-treated variation, are now also deemed useful. Each such assumption
thus further scales the number of useful pairs. This condition is, abstractly, ’the most
developed and popular strategy for causal analysis in observational studies’ (Pearl, 2010;
King and Nielsen, 2019). It is used by a wide range of methods across disciplines. It
requires, however, a further ’ignorable treatment assignment’ assumption (Rubin, 1974;
Angrist and Krueger, 2001; Louizos et al., 2017). Namely, it requires that, conditional on
the observed variables, there are no unobserved differences between treatment and control
groups. The common way to satisfy this assumption is to include in X
m any variable that
affect either outcomes or treatments. This is because, theoretically at least, for any variable
set satisfying ignorability, any superset will too (VanderWeele and Shpitser, 2011). Due
to the centrality of this condition in the causal effect estimation literature, and its further
required assumptions, we briefly review them.

In randomized experiments, randomization enables unbiased estimation of treatment
effects across local population groups. For each observed variable, randomization implies,
as a simple application of the law of large numbers, that any treatment-subgroups will be,
what is often called, ’balanced’ on average. Unfortunately, the assignment of treatments to
subjects is typically not random in observational datasets. Most causal effect estimator in
use today attempt to reduce the treatment assignment bias, and mimic randomization, by
increasing a balance score between treatment and control units in use. The idea is to create
a subsample of sample units that received the treatment that is comparable on all observed
covariates to units that did not receive the treatment.

A balancing score b(X) is a function of the observed covariates X such that the conditional
distribution of X given b(X) is the same for treated and control units - thus reflecting
the previous assumption. There are three general approaches to derive such functions. The

first and most trivial function is b(X) = X, which is the case of exact matching (we review
these methods in detail below). A second approach, which broadly underlie popular Propensity
Score and Latent-Confounder estimators, is to use dimensionality reduction techniques
to define a simpler function π(X). With this function, it is easier to balance samples,
[v ⊥ y | X] ≈ [v ⊥ y | π(X)]. On the other hand, the approach requires not only the added
assumption, but also more complex models, both statistically and computationally. With
ignorability, it has been shown analytically (Rosenbaum and Rubin, 1983) that Propensity

scores are the ’coarsest’ balancing function taking the multidimensional X into one dimension.
It uses a logistic regression to calculate the probability of a unit being assigned to a
particular treatment, given X. A third approach is to use explicit, or non-parametric, bal5
Ribeiro, Neffke and Hausmann

ance functions. The simplest such function is a difference-of-means (i.e., between covariate
means across treated and nontreated samples). There are additional analytic advantages to
this approach (King and Nielsen, 2019) - such as, concurrently, decreasing model dependence.
Due to the focus on large numbers of pairwise observations, we favor this alternative.
That is, for a large number of pairs, it is undesirable to run a large number of regressions1
.
The assumption of ignorability that often accompanies observational methods has been
challenged recently, such as when not all relevant variables can be included (Wang and Blei,

2020; Athey et al., 2020; Louizos et al., 2017). While sometimes calling confounders
’unobserved’, these parametric estimators assume partially-observed confounding
variables (whose correlations with observed variables can be exploited when training a
proxy). Beyond analytical discussions, there is however a more practical problem underlying
ignorability. Popular ATE estimation methods such as Propensity Scores are often sensitive

to inclusion of non-causal variables (A. and E., 2005; Zhao, 2008; Iacus et al., 2012). These
opposing constraints (to include as many variables as possible versus not including noncauses)
create practical difficulties for researchers and threaten the validity of observational
estimates - especially in datasets with many variables. Addressing selection bias is essential
to identify extraneous effects of other causes on the treatment-of-interest, but does not address
the second problem. Conducting model selection and effect estimation in a common
framework is a promising direction to rule out non-causes (Chernozhukov et al., 2015).

Because of the use of pairwise outcome differences, yij , we argue it is natural to translate
these two problems into distance metric learning problems. The approach leads, as a result,
to a data representation that is more easily interpretable by researchers, reflecting Factorial
Experimental Designs. Other immediate advantages of the approach are discussed below.

1.3 Reproducing Effect Estimates from Large Randomized Experiments

We assess the proposed method’s performance in simulations and a seminal real-world example,
comparing it to current Statistics, Econometrics and Machine Learning estimators. We
demonstrate that the proposed approach also remain accurate in heterogeneous and diverse
samples. The simulations introduce confounders and heterogeneous subpopulations into
synthetic data, demonstrating that observational methods generally become biased or inaccurate,
unlike the proposed. As real-world application, we consider the National Supported
Work (NSW) program. Starting with a seminal contribution by Lalonde (Lalonde, 1986),
studies have used this Randomized Control Trial to benchmark nonexperimental techniques
- including an historical ’face-off between regression and propensity-score matching’ (Angrist,
2009). Observational methods generally fail to recover the experimental causal effect
estimate, except in a smaller handpicked NSW subsample (A. and E., 2005; Dehejia and
Wahba, 1999; Zhao, 2006; Colson et al., 2016). This literature exemplify a typical scenario
across disciplines: estimating causal effects nonexperimentally require several (hard
to justify) population and variable selection assumptions (in this case, expert selection of
samples and variables with desirable economic characteristics). We demonstrate, however,
that the proposed approach can recover the NSW experimental effects not only in Lalonde’s

1. We would also mention that we experimented with other alternatives, such as HSIC tests and Distance
Correlations (Sejdinovic et al., 2013), while results with these alternatives are comparable to those used
in reported results, we favor explicit balance scores due to their computational efficiency and very natural
interpretation in the geometrical framework formulated below.

What can the millions of random treatments [...] reveal about causes?

original unsolved challenge (with 740 participants and 6 variables) but also in the full NSW
data with over 10000 participants and 1000 variables, without ex ante assumptions from
researchers.

We compare the approach to a range of previous solutions, including those making typical
ignorability assumptions, as well as approaches relaxing other assumptions, such as missing
variables and endogeneity. We show that the previous simple model outperform these
solutions, when trying to reproduce the results of the previous Randomized Experiment.
Our initial goal was to address the common case of large datasets with many variables.
Perhaps surprisingly, however, this is also the case for samples with very few variables,
where Instrument-based and Latent-Confounder approaches should be most relevant.

2. Stochastic Factorial Estimation (SFE)

We first introduce the proposed approach, then review the related literature in
further detail. Randomized Controlled Trials (RCTs), and the observational estimators
they have inspired (Rubin, 1974), often focus on the causal effect of a single treatment or
intervention. However, observed outcomes are often the result of many interacting causes.
This limitation of RCTs had already been noted by Fisher in 1926: ’No aphorism is more
frequently repeated in connection with field trials, than that we must ask Nature few questions,
or, ideally, one question, at a time.’ (Fisher, 1927) (1926, p. 503) Instead, he
proposed submitting Nature ’logical and carefully thought out questionnaire[s]’, leading to
factorial experimental designs. Factorial designs have since been mostly studied for the
design or analysis of experiments (Dasgupta et al., 2015).

A factorial experiment is a complex experiment consisting of many runs. It is designed
to estimate the causal effect of m factors on an outcome of interest y. When factors are
binary, the design contains 2m factorial runs, or, possible factor combinations. Fig.1(c)
depicts geometrically a 3-factor design with a cube C : {-1, +1}
. We call the set of factors

in which two runs differ a factorial treatment. A factorial run corresponds to C’s vertices and
treatments to edges. We consider all individuals in a nonexperimental dataset as stochastic
factorial runs and the entire dataset as an incomplete random factorial design. Critically,
the full set of observed factorial treatments express necessary combinatorial patterns of
variable variation and fixation necessary to make claims about each variable’s piecewise
effects on y.

We consider this geometric representation for the nonexperimental causal effect estimation
problem next, then discuss a Bayesian procedure that combine effect estimates from
each pair of individuals, given how strongly they depart from ideal factorial treatments. We
call the resulting method Stochastic Factorial Estimation (SFE).

2.1 Geometric Representation

Consider a Factorial Experiment studying the effects of a set of factors X
m = {a, b, c, ...}.
The experiment’s runs are the vertices of the cube C(X )
m : {-1, +1}
m. Factorial treatments
are pairs of runs that differ on a set of factors (the ’treatment’), while having all other
factors in common. Namely, let xi
, xj ∈ Cm be runs and their corresponding treatment

be the set of factors run i has exclusively, xi	xj . In addition, we let the size of C’s edges

Ribeiro, Neffke and Hausmann

correspond to the causal effect, f(xi	xj ), of their associated treatment. We discuss an
extension to the continuous variables case in Appendix B.
Consider now an observational matrix X with variables X
m. Fig.1(c) depicts an example
with n=8 individuals and m=3 variables, where values have been normalized to the unit
interval, X : [-1, +1]m. The O(n
) pairs of individuals are in a myriad of configurations.
As a result, different pairs are useful for estimating effects of different variables. Fig.1(d)
illustrates a pair corresponding to a factorial treatment with {a} as treatment. The pair
captures the main intuition behind factorial designs: a single variable, a, differs between
individuals while all other variables are fixed. Fig.1(e) depicts another factorial treatment.
Here, however, the treatment is multivariate, {a, b}. Because the treatment consists of
two potential causes, it is impossible to infer their separate effects from the pair alone.
However, we can still learn about their combined effect. Fig.1(f) shows an imperfect factorial
treatment. There, the outcome difference is not necessarily due to variables in the treatment
and may reflect extraneous variation from other variables. Although not fixed within the
pair, these nontreated variables could coincide in expectation across treated and non-treated
individuals - i.e., they could be ’balanced’ in the sample. We can also learn from pairs in
this case. Finally, Fig.1(g) illustrates a pair without treatment. We disregard such cases in
the estimation.

We will use observed factorial treatments like the ones depicted in Fig.1(d-g) to iteratively
transform X, such that distances between individuals come to represent expected
treatment effects on y,

Ty(Xm) =

xi ∈ R
m : |xi − xj |
2 = py(xi

, (1)

, xj )f(xi	xj ), ∀ 0 < i, j ≤ n.

where Ty(X) is a map [-1, +1]m → R
m, xi (in bold) is the transformed position for
individual i, py(xi
, xj ) is the probability that the pairing of i and j reproduces the factorial
treatment v=xi	xj , and, f(v) is the treatment’s effect. The use of factorial treatments leads
to an estimator for outcome differences yij as distances in Ty(Xm). We discuss py(xi
, xj )
and the resulting stochastic model next.

2.2 Stochastic Model and Assumptions

Let 0 < i, j ≤ n be any two individuals and g(x), h(x) be two functionals over x. We do not
postulate a model that relates an individual’s characteristics to her outcomes, yi = g(xi)+.
Instead, we interpret yij = yi−yj as a noisy observation of the true causal effect of observed
factor differences, xi	xj . Noise increases as xi	xj departs from factorial, balanced and
univariate treatments. Such departure is described by a distribution py(xi
, xj ). That is, we
interpret differences in characteristics between a pair of individuals, xi	xj , as ‘treatment’
differences that cause differences in outcomes yij = yi−yj ,

yij ∼ g(xi	xj ) + ij ,

(2)

ij ∼ N (0, h(xj	xi)),

What can the millions of random treatments [...] reveal about causes?

where ij is a Gaussian noise with mean 0 and variance σ
2 = h(xj	xi). Eq. (2) postulates
that ij reflects distortions in observed effects yij due to variables that individual
j, alone, has. We will say that, when ij = 0, pairwise observations correspond to factorial
treatments: pairwise observations with little risk of observed confounding. Or, similarly,
that each observational pair, xi	xj , in the sample represents a factorial treatment,
v=xi	xj , with probability py(xi
, xj ).

A first way to estimate effects f(v) is to focus on pairs that approximate a given factorial
treatment v with near certainty: py(v) → 1. The defining characteristic for this type of
pair is that, when estimating the effect for an individual i, the other individual j has no observed
extraneous factors that could confound the effect yij , xj	xi = ∅. This is the first key
condition behind Factorial experimentation. In this first condition, the experimenter keeps
all relevant conditions fixed, except for a treatment. Since factors can, however, be beyond
the experimenter’s control, a second condition is popular: randomize treatment assignment
such that subpopulations are balanced in expectation in the treated and nontreated subsamples.
Nonexperimental methods using balancing scores are often seen as attempting
to reproduce randomized conditions from nonexperimental data (Rosenbaum and Rubin,
1983; King and Nielsen, 2019).

Randomization is essentially a mechanism to address selection bias. For a treatment
indicator d ∈ {−1, +1}, selection biases appear when the treatment d is not independent
either of other factors, X, or the outcome, y. In Econometrics (Heckman, 1979),
when p(d|X, y) = p(d) it is said, under ignorability, that the sample is not subject to selection
bias. Computational approaches sometimes make a distinction between covariate,
p(d|X) = p(d), and outcome, p(d|y) = p(d), induced bias. These distinctions are discussed
in detail in (Zadrozny, 2004; Fan and Davidson, 2007). In Propensity scores or LatentConfounders
based approaches, treated and untreated individuals with the same π(X) are
expected to have similar distributions across any observed baseline covariates - reproducing
a randomization experimental procedure. This is often used as diagnostic for their outputs.
The former approach is mature and has been studied extensively, both theoretically and
practically. There are serious questions as to whether the previous goal can typically be
achieved in practice, and whether these methods’ assumptions, in fact, hold (King and
Nielsen, 2019; A. and E., 2005). Instead of estimating a parametric model π(X) for a given
treatment, we calculate explicit balance scores for all O(n
) pairwise treatments (univariate
or multivariate), with simple matrix operations. The calculation is repeated thousands of
times in a Bayesian optimization procedure that progressively estimate treatment effects.
The approach thus uses ’weak’ but numerous balancing scores. This reflects its alternative
Signal Processing perspective, as opposed to the more typical, based on Model Inference.
In the present framework, the notion of sample balance thus leads to an observational pair’s
balance, φ
bl
ij = p(xi	xj ) − p(xi	xj |xj	xi). We let p[φ
bl
ij = 0] denote the probability that
the observational pair (ij) is not subject to covariate induced bias, in which case it can also
be used to estimate effects. This is given a simple geometrical interpretation below.

The implicit goal of causal effect estimation is to devise effect estimates with high
external validity. It is worth considering the impact of multivariate treatments on external
validity. Multivariate treatment effects estimate the simultaneous effects of all variables in
the treatment, xi	xj . Effects need not generalize to the 2|xi	xj | different instantiations of
the treated variables. Under multivariate treatment conditions, it is impossible to attribute

Ribeiro, Neffke and Hausmann

effects to any single cause. As a consequence, the cardinality of a treatment, |xi	xj |, is
inversely related to the external validity of the derived effect estimates. The notion leads to
the pairs’ treatment size, φ
cx
ij = |xi	xj |. We let p[φ
cx
ij = 1] denote the probability that the
the observational pair (ij) has a univariate treatment, indicating the propensity for higher
external validity.

2.3 Optimization

cx
ij = 1] and p[φ
bl
ij = 0] are fulfilled

We consider that py(xi

, xj ) → 1 when conditions p[φ

by stipulating Bayesian priors for: sizes of factorial treatments, xi	xj , and balance of
non-factorial variations, xj	xi
. This Bayesian formulation leads to an objective function
Γ(xi) over individual positions xi that we later minimize. The overall procedure transforms
pairwise distances |xi−xj | in X to reflect observed outcome differences, yij , according to the
smallest and most balanced factorial treatments. Appendix A contains a detailed derivation
of Γ(xi) from eq.(2), similar to those underlying LASSO and Ridge-Regressions (Hastie,
2001). The objective has the form

Γ(xi) = min
xi
Xn
j=1
(1 + φ
cx
ij )[hxi
, xj i + |yij |]
2 + φ
bl
ij hxi
, xj i
,

φˆcx
ij =
|xi + xj |
m
,
φˆbl
ij = |
n
Xn
k=0
hxk, xi + xj i|,

(3)

where h., .i is the dot-product, φ
cx
ij and φ
bl
ij are treatment size and balance estimates.
When both φij terms are zero and hxi
, xj i is negative, the pair corresponds to a factorial
treatment, Fig.1(d-g), and the residual hxi
, xj i + |yij | is minimized. Term φ
bl
ij penalizes
unbalanced non-factorial treatments, Fig.1(f), and the consequent risk of confounded estimates
(given the discussed assumptions). Term φ
cx
ij penalizes multivariate treatments,
Fig.1(e), and the consequent risk of low external validity. The estimators used in the Experimental
section, φˆcx
ij and φˆbl
ij , are simple treatment size and balance estimators derived
directly from the previous geometrical representation (Appendix A).
In the output space, Ty(X), the ATE of any factor a can be calculated simply as the
difference in coordinates a between the mean position of all individuals with factor a, x¯
+a
,
and those without, x¯
-a
,

ATE(a) =p
|x¯
+a − x¯

-a|(a), (4)

for any a and where x¯ ∈ Ty(X). That is, in Ty(X) coordinate differences correspond
to treatment effects and distances to outcome differences (the squared-sum of treatment
effects). Since each factor a with non-zero effects divides a population in two subpopulations,
(+a, -a), the method’s output also gives researchers means to represent and visualize relevant
subpopulations in their samples.

What can the millions of random treatments [...] reveal about causes?

2.4 Related Work

In the Sciences, problems of integrating noisy diagnostic measurements are sometimes called
‘Inverse problems’. Tikhonov regularization approaches, such as Ridge and LASSO regressions,
are popular solutions to inverse problems. They perform both variable selection and
regularization in order to enhance the prediction accuracy and interpretability of the statistical
models they put forward to explain observations. Regularized inverse problems can
be seen as special cases of Bayesian inference (Tarantola, 2005). We devise a solution on
this framework, using well-known Bayesian interpretations of the previous solutions.
Different disciplines can differ in how they approach causality, with the two most popular
frameworks (Morgan, 2007) identified as the Pearl (Pearl, 2000) and Rubin (Rubin, 1974)
frameworks. Due to focus on Experimental Design concepts and pairwise comparisons,
we review Rubin’s framework, also known as the counterfactual (or potential outcomes)
formulation. We do not wish to disregard, however, the critical contributions of other
frameworks, and the solutions developed under them.

Consider a treatment indicator variable d ∈ {-1, +1} and that a treated individual i has
observed outcome y
+d
i ∈ R. The individual treatment effect of d, ITEi(d), is defined as the
counterfactual outcome difference,

ITEi(d) = y
+d
i −y
-d
i

. (5)

According to the counterfactual framework, it is impossible to observe the outcome that
individual i would have had in the counterfactual situation where she would not have been
treated, y
-d
i
. A Randomized Controlled Trial (RCT) solves this problem with the help of an
homogeneity assumption: since the treatment is administered at random, the nontreated
subpopulation’s outcome serves, in expectation, as a counterfactual outcome for the treated
subpopulation. The manipulation allows researchers to calculate average treatment effects
easily,

ATE(d) = E[y
+d
]−E[y
-d

]. (6)

Nonexperimental approaches, in contrast, often require researchers to specify a data
generating process (DGP) for the observed data. A DGP specifies at least:

- a causal model describing how the treatment affects the outcome variable, as well as
how other potential causes may confound the treatment’s effect;

- a population in which this model holds.

This approach puts, however, ’the cart before the horse’: most research is undertaken
because the DGP is poorly understood. We address this problem by combining insights
from nonexperimental causal effect estimation and model selection.

Experimental Designs (ED) prescribe conditions, to be verified, or manipulated, by
researchers, under which outcome differences, yij=yi−yj , are true causal effects. We considered
two commonplace ED conditions. In the first, the experimenter keeps all relevant
conditions fixed, except for a treatment. This is the distinguishing strategy of Factorial
experimentation. In the second, researchers try to maintain population representativeness

Ribeiro, Neffke and Hausmann

in their samples. This is the central strategy underlying Randomized experimentation.
These two conditions inspired the development of exact (Imai et al., 2008) and balancebased
matching estimators (Heckman, 1979; Rubin, 1974; Diamond and Sekhon, 2012) in
observational analysis,

ATE(d) = E[yi−yj ], iff xi	xj={d} (exact)
ATE(d) = E[yi−yj ], iff xi	xj={d} & y ⊥ {d} | X −d (balance−based)

(7)

These estimators try to find pairs fulfilling the previous conditions for a treatment-ofinterest,
typically, a variable d. They have been used across disciplines (Stuart, 2010;
Colson et al., 2016) such as statistics (Rubin and Stuart, 2006), epidemiology (Brookhart
et al., 2006), sociology (Morgan and Harding, 2006), economics (Abadie and Imbens, 2006)
and political science (Ho et al., 2007).

We defined a combinatorial-based model for random treatments, eq.(2), which can be
used to combine large numbers of pairwise observations. Using pairwise comparisons, SFE
is related to matching estimators (Rubin, 1974; Stuart, 2010) but different in two important
ways. Factorial treatments, eq.(2), are more specific statistical entities than matches. The
approach articulates statistical roles for all possible combinatorial conditions appearing in
pairings, such as when there are extraneous varying variables, xj	xi
, as well as multivariate
treatments, xi	xj . The formulation of a random treatment model enables the use of all
available treatments and treatment types (such as multivariate treatments) in datasets.
To that end, we decomposed all sample pairs into three components: xi	xj (treatment),
xi ∩ xj (match), xj	xi (possible confounders). Fig.1(b) illustrates the decomposition. The
decomposition leads to a simple geometrical interpretation of observational pairs and a
density py(xi
, xj ) that indicates pairs’ departure from ideal factorial treatments: univariate
treatments with no observed confounders (Appendix A discusses this geometric connection
in further detail, as well as density versions for categorical and continuous variables).

This leads to a second important difference. The decomposition allows the method to
autonomously reduce the input data dimensionality. A Bayesian procedure first estimates
the effects of treatments xi	xj with largest py(xi
, xj ), which simplifies the estimation of
effects for the remaining treatments, and repeats. Estimation is progressively simplified
because variables without any significant effect on y can be ignored in each step, relaxing
the conditions-to-be-fulfilled for the remaining variables (such as the penalties, φij , for
sample balance and treatment sizes). This is an effective strategy because, contrary to
matching assumptions, treatments in nonexperimental data are overwhelmingly multivariate
or have negligible effects on outcomes. While not directly about the treatment-of-interest,
each observational treatment provides some information about which variables have any
significant effect on y and which do not. In the Experimental section, we consider both
traditional and iterative extensions to balance-based matching methods (Colson et al.,
2016; van Der Laan J. et al., 2007; Diamond and Sekhon, 2012), as well as other recent
Econometrics (Chernozhukov et al., 2015) and Machine Learning methods (Louizos et al.,
2017; van Der Laan J. et al., 2007).

Whereas matching estimators typically focus on the causal effect of a single variable,
this considers that, somewhat counter-intuitively, the problem of estimating the effect of
one causal variable can become easier once we try to estimate the effect of all causes.

What can the millions of random treatments [...] reveal about causes?

This is due to the curse of dimensionality from which matching estimators suffer. Initially
estimating the effects only of (sets of) variables that are closest to experimental conditions,
allows us to ignore variables estimated as having negligible effects in future iterations,
progressively lowering the dimensionality of the matching process. The output of this
process, Ty(X), represents effects analogously to factorial designs. The previous model,
eq.(2), and objective, eq.(3), combine effect estimation and model selection within
the standard framework of sparcity-based model selection (e.g., LASSO, UnbiasedLASSO,
Ridge regressions) (Appendix A).

Notice that because differences yij are estimated (as opposed to a functional for y conditional
on X), eq. (2), the approach does not require i.i.d. assumptions on subjects.
The assumption of i.i.d. observations, although common in Machine Learning, can bias
estimates for models that stipulate a functional relationship between factors and output,
y ∼ g(X). This is because, if any two groups are misrepresented in a sample, average
outcome differences (i..e., effects) will consequently reflect such biases in selection. Optimization
is, instead, used here to combine pairwise observations under a simple Bayesian
rationale and learn distances, eq. (1). This is a central advantage of pairwise observational
estimators (Stuart, 2010). The approach can, on the other hand, be potentially sensitive to
unobserved pairwise differences, leading, in the present interpretation, to incomplete factorial
designs. This is however ameliorated by learning from multi-variate treatments, which
are overwhelmingly common in everyday datasets. We consider next how practical the
presented approach can be in common conditions, compared to pairwise and non-pairwise
solutions.

3. Results

3.1 Simulation

We first test SFE in synthetic datasets. The design is similar to previous studies (A. and
E., 2005; Athey and Imbens, 2016). In the first simulations, the treatment effect is homogeneous.
Each of 3 subpopulations are, however, randomly underrepresented in the treatment.
Fig.2(a) shows the DGP in graphical-model notation and Fig.2(b) Average Treatment Effects
(ATE) and their Mean Squared Errors (MSE) from several popular methods, which
includes all methods in (Colson et al., 2016) plus 5 methods making use of Machine Learning
(super-learner,genetic,latent,instrument,sfe), Distance Metric Learning (genetic,latent,sfe)
and high-dimensional Econometric (instrument) techniques2
. The counterfactual outcomes
y
+treat and y
-treat for each individual and ITEi(treat) = y
+treat−y
-treat are known. In this
setting, all methods recover the ground-truth (dashed line) with little bias. SFE has, however,
the smallest MSE, even below the ground-truth’s MSE, illustrating the advantage of
using many pairs.

In the next simulations, we assume that subpopulations respond differently to the treatment.
Subpopulation b observes double the expected effect, whereas c is immune. The
resulting heterogeneity introduces significant biases in most estimates, Fig.2(c). Whereas
most estimators become increasingly inaccurate as populations become more diverse, SFE
continues to provide accurate and unbiased ATE estimates.

2. see (Colson et al., 2016) for further algorithmic details.

Ribeiro, Neffke and Hausmann

b
a

treat y | treat=1 ~ Gaussian(0.5, 0.5)
treat | type ~ 0.5 - Uniform(0,0.3 | type) {

plot
(b)
plot
(c)

y | treat=0 ~ Gaussian(0, 0.5)

1 14

10 2-7
8,9

y | a=1, treat=1 ~ Gaussian(0.5, 0.5)
y | b=1, treat=1 ~ Gaussian(1, 0.5)
y | c=1, treat=1 ~ Gaussian(0, 0.5)

c y

0.90

a)

ATE

1.00

0.85

0.75

ATE

0.80

0.01 0.05 0.1 0.15 0.2 0.25 0.3 0.35 0.4 0.45
incompleteness, γ / 210

0.50

d)

1 2 3 4 5 6 7 8 9 10 11 12 13 14

treat

y | treat = 0 ~ Gaussian(0, 0.5)
y | treat = 1 ~ Gaussian(0.5, 0.5)
treat | type ~ 0.5 - Uniform(0,0.3 | type)

b
a
c

0.25

b)

y | b=1, treat = 1 ~ Gaussian(1, 0.5)
y | c=1, treat = 1 ~ Gaussian(0, 0.5)
ut
 ~ corr(y, ut
) = 1-1/t
u
t

1.00

y

e)

0.75

ATE

0.8

7 12 13

 2 3 4 5 6 8 9 10 11

0.50

ATE

0.6

8,11
3-6

genetic
mahab−1:1
mahab−1:2
mahab−1:3
mahab−1:4
ols
optimal
ps
ps−iptw
super−lea
rner
sfe (this*)
c)

0.25

ground-truth

latent
instrumental

0.4

2,10

f)
ground-truth
mahab−1:1 genetic
mahab−1:2
mahab−1:3
ols mahab−1:4
optimal
ps
ps−iptw
super−learner sfe (this*)
instrumental

latent

1 2 3 4 5 6 7 8 9 10
t

Figure 2: Montecarlo simulations. (a) A priori Data-Generating Process (DGP) in
graphical-model notation (gray variables are observed), population of 1000 individuals
with 3 disjoint subpopulations type = {a, b, c} with sizes 600, 300, and
100, treat is a treatment indicator and y an outcome; (b) Average treatment effect
(ATE) and Mean Squared Error (MSE, error bars) estimates from 1,000 simulations
under observational conditions using several methods (columns), groundtruth
is dotted, effects drawn from a Gaussian with mean and standard deviation
0.5 for all subpopulations, treatment propensities for each subpopulation drawn
from a uniform distribution over [0.2, 0.5], methods are: propensity-score matching
(ps), propensity-score with inverse probability of treatment weighting (psiptw),
mahalanobis covariate matching (mahab) with 1-4 neighbor matchings,
optimal matching (optimal), ordinary least-squares (ols), genetic balance optimization
(genetic) (Diamond and Sekhon, 2012), SuperLearner ensembles (superlearner
) (van Der Laan J. et al., 2007; Colson et al., 2016), high-dimensional
instrument selection (instrument) (Chernozhukov et al., 2015; Belloni et al.,
2014), latent causal variables deep-learning (latent) (Louizos et al., 2017) and
stochastic factorial estimation (sfe), using eq.(4); (c) simulations under heterogeneous
conditions, effects drawn from Gaussians with mean 1.0 for subpopulation
b and 0 for c (both with standard deviation 0.5); (d) avg. factor ATE for simulations
with 10 subpopulations (unitary effects) and increasingly complete samples
γ/2
10 in respect to pairwise differences (γ is the number of random sampled C

edges, horizontal axis), (e) DGP with added ut variables (plate) that are increasingly
correlated with y; (f) ATE estimates for simulations under confounding,
heterogeneous and endogenous conditions, 1 ≤ t ≤ 10.
What can the millions of random treatments [...] reveal about causes?

{-b,+c,+treat} {+b,+c,+treat}
{+b,-c,+treat}

{-b,+treat} {+b,+treat}

treated
no
yes
0.00
0.25
0.50
0.75
1.00
y
ATE

treat

{-b,-c,+treat}

−0.5
0.0
0.5

(kl)

−0.8 −0.6 −0.4 −0.2 0.0 0.2 0.4 0.6 0.8

-b
-b

δkl

+b
+b

treat

δij

(ij)

{+b,+c,-treat}

{-b,+c,-treat}

−0.8
−0.6
−0.4
−0.2
 0.0
 0.2
 0.4
 0.6

−0.5 0.0 0.5
type b

{+b,-treat} {-b,-treat}

{+b,-c,-treat}
type c
type b

−0.8 −0.6 −0.4 −0.2 0.0 0.2 0.4 0.6 0.8

a) b)

{-b,-c,-treat}

Figure 3: (a) Factorial subspace {b, c, treat} of Ty(X) for the simulations in Fig.2(b), pluses
(+) show the (average) positions of treated and nontreated subpopulations, the
AT E corresponds to coordinate differences between these subpopulations on the
treat axis; (b) subspace {b, treat}, treated individuals in green, nontreated in
red, diagonal axis indicates the variables’ combined effect, the ATE is an aggregation
of individual effects, distances (solid lines) and their projections, δij and
δkl, illustrate individual treatment effects for two example pairs: pair (ij) with
both individuals in subpopulation b, with +b and distinct treat, and (kl) with
individuals not in b, with −b and distinct treat.

Ribeiro, Neffke and Hausmann

Fig.2(d) shows simulations with 10 subpopulations and samples that are decreasingly
incomplete (i.e., approaching a Factorial Design). At each instant, a number γ of the 210
hypercube edges C
10 is sampled uniformly without replacement. Treatment propensities

are as before and effects are unitary. The figure shows mean AT E estimates across factors
(vertical axis) with increasing γ/2
10 (horizontal axis). The figure demonstrates that while
the central assumption in the present work is factorial incompleteness, the assumption, in
fact, impact other methods more severely. Making such assumptions explicit is, we
believe, one of the proposed representation’s strengths.

Fig.3(a) illustrates SFE’s factorial representation. It shows a 3D subspace of the estimated
space Ty(X). Dots show individuals’ positions and their outcomes (colors). Spatial
differences in Ty(X) reflect differences in outcomes y. The AT E corresponds to differences
in the treat coordinate between treated and nontreated subpopulations, eq.(4). Results
demonstrate that SFE achieves lower MSE in homogeneous synthetic samples and can recover
unbiased individual effects under heterogeneity.

3.2 National Supported Work (NSW) Program

We now consider a real-world application: the NSW employment program (details in the
Appendix B), where eligible applicants were randomized into treatment and control groups.
In his seminal article (Lalonde, 1986), Lalonde selected a subsample of the NSW participants
and replaced its nontreated subgroup with samples from national surveys, leading
to 6 distinct datasets. By doing so, he ’unbalanced’ the NSW data (i.e., subpopulations’
treatment propensities) - previously balanced by the NSW’s experimental design. Lalonde
then showed that observational methods failed to recover the experimental effect, a finding
corroborated by later authors (Zhao, 2006; A. and E., 2005). Subsequent research
(Dehejia and Wahba, 2002, 1999; Zhao, 2006) showed, however, that in a more restricted
sample (henceforth the ’DW’ subsample) covariate matching and other methods recover
the experimental effect. This small sample continues to be used to this day (Colson et al.,
2016).

Fig.4(a) shows ATE estimates calculated by different methods (columns), using Lalonde’s
variables and sample restrictions, as well as the experimental (dashed line). Each dot is an
estimate in one Lalonde sample. As in Lalonde’s study, methods struggle to recover the
NSW effect. In contrast, SFE estimates are consistently close to the experimental effect -
within U$37, well inside the experimental 95% confidence interval.

ATEs neglect that the NSW effect may differ across subpopulations. Fig.4(b) shows
experimental effects for several subpopulations. Far from homogeneous, the program’s effect
was particularly large for older, married and relatively educated workers. Fig.4(c) shows
that, unlike other methods, SFE estimates these heterogeneous effects with negligible bias
in all subsamples.

3.2.1 Unknown or Unconsidered causes

Both Lalonde and Dehejia and Whaba restricted the sample population and model variables.
Fig.5(a) shows results in 4 nested subsamples: DW, Lalonde, all males in the NSW and,
finally, the full NSW dataset. This figure uses variables Lalonde picked based on his expert
judgment. All methods perform well in the DW sample. However, their performance

What can the millions of random treatments [...] reveal about causes?

−2000

−2000

ols

mahab−1:4

−2000

−2000

ATE ($)

ps

optimal

−2000

−2000

ps−iptw

super−learner

−2000

−2000

−500

mahab−1:1

rimental

genetic
mahab−1:1
mahab−1:2
mahab−1:3
mahab−1:4
ols
optimal
ps
ps−iptw
super−lea
rner

instrumental

latent

sfe (this*)

genetic

−2000

−2000

(a)

expe

mahab−1:2

instrumental

−2000

−2000

−500

ATE ($)

latent

mahab−1:3

sfe (this*)

difference to
experimental ($)

−2000

age<24
(n= 408 )
age>=24
(n= 314 )
african-am.
(n= 578 )
degree
(n= 159 )
education<10
(n= 368 )
education>=10
(n= 354 )
hispanic
(n= 76 )
married
(n= 117 )
not african-am.
(n= 144 )
no degree
(n= 563 )
not hispanic
(n= 646 )

not married
(n= 605 )

(b) (c)

age<24
(n= 408 )
age>=24
(n= 314 )
african-am.
(n= 578 )
degree
(n= 159 )
education<10
(n= 368 )
education>=10
(n= 354 )
hispanic
(n= 76 )
married
(n= 117 )
not african-am.
(n= 144 )
no degree
(n= 563 )
not hispanic
(n= 646 )
not married
(n= 605 )

Figure 4: (a) Lalonde (Lalonde, 1986) reproduction, estimated AT E for the National Supported
Work (NSW) program with different methods (columns) over the 6 control

surrogates drawn by Lalonde (dots), the dotted line shows the experimental estimate,
variables as in (Lalonde, 1986): y is the worker’s real post-program annual

earnings (in 1981 dollars), X variables are workers’ age, years of schooling, wage

before entering the program, treatment status, race indicators (African-American,

Hispanic) and whether the worker holds a high-school degree; (b) experimental

effects of subpopulations (columns) in blocked samples (and their resulting sample
sizes n); (c) estimated effects (difference from experimental, in dollars) for

subpopulations (columns) according to each method, note that existing methods
require 12 separate estimations, SFE represents subpopulations explicitly,

making subpopulation-specific effects available from Ty(X), eq.(4), without reestimation;
SFE estimates are closer to the ground-truth in both the Lalonde

sample population and blocked subsamples.

Ribeiro, Neffke and Hausmann

Dehejia and Wahba (DW)

Lalonde

All-males

NSW

Dehejia and Wahba (DW)

Lalonde

All-males

NSW

dierence from experimental ($)

3-9

1,14
3,4,9
5-8,10,

11,14

0 500 1000 1500 2000
n. treated

0 500 1000 1500 2000
n. treated

a) b)

optimal
super−learner
genetic
instrumental

ground-truth
ols

ps
ps−iptw

mahab−1:1
mahab−1:2

mahab−1:3
mahab−1:4

latent
sfe (this*)

Figure 5: (a) ATE difference from experimental groundtruth (in dollars) using Lalonde’s
expert DGP and progressively fewer ex ante assumptions from previous studies
(Lalonde, 1986; Dehejia and Wahba, 1999; Zhao, 2006; Colson et al., 2016), leading
to the full NSW dataset (rightmost) with 1231 variables, 1923 treated and
8001 non-treated individuals; estimates become progressively harder for most
approaches as sample restrictions are loosened with the exception of SFE; (b)
ATE estimates with an automatically devised DGP (Appendix B details the
procedure), yielding a DGP with variables: worker’s work-ethic, race (AfricanAmerican),
previous school attendance, previous work, alcoholic drink consumption
and location (New York city); all methods perform well throughout all samples
using the DGP devised with SFE.

What can the millions of random treatments [...] reveal about causes?

DW NSW subsample
National survey (Panel Study of
Income Dynamics 1975)

0.0 0.2 0.4 0.6 0.8 1.0

0.0 0.2 0.4 0.6 0.8 1.0
−1.0
−0.5
 0.0
 0.5
 1.0
y

b)

−1.0 −0.5 0.0 0.5 1.0

y

NSW sample
Full
Lalonde
DW

−1.0
−0.5
 0.0
 0.5
 1.0

count

college
ranking

−0.8 −0.6 −0.4 −0.2 0.0 0.2 0.4 0.6 0.8

0e+00 1e+08 2e+08 3e+08 4e+08
(δi - δ)

a)

c)

work ethics

Figure 6: (a) Subspace of Ty(X) consisting of two variables (ranking of attended college and

work-ethics) versus outcome y (wages), variables selected after running SFE on
a matched NSW-National survey (Appendix B describes the procedure, dataset
has 441 variables, 8001 individuals), survey respondents are blue and individuals
in the Dehejia and Wahba (DW) sample are red; (b) illustration of diminishing
exponential returns across subpopulations and the area of concentration of the
DW sample (small cube); (c) (δi − ¯δ)
2 histogram for treated individuals in DW,

Lalonde and the full NSW experimental samples, δi are before-after individual
outcome differences, 0 < i ≤ n, and ¯δ their mean in each sample; results illustrate
how the DW sample contains a highly homogeneous subpopulation.

degrades as sample restrictions are relaxed. Fig.5(a) and Fig.4(c) suggest that SFE, in
contrast, can estimate effects in heterogeneous populations, relieving the need for population
selection. Can SFE also help determine which variables to include as causes? Fig.5(b)
show estimates with variables selected by SFE from the 1232 NSW variables (selection
procedure details in the Appendix B). Using this alternative set of 5 variables improves SFE
performance. More surprisingly, it also improves other estimators. Using these variables,
all observational methods approach the ground-truth (matching methods, in particular),
even as sample restrictions are removed. This suggests that the autonomously identified
DGP approximates the true DGP more closely than the one derived from expert judgment.

But why did all observational methods perform well in the DW sample? To explain
this, Fig.6(a) plots individuals’ coordinates on the two variables with the highest ATEs in a
NSW-National Survey matched dataset: work-ethics and college ranking. It illustrates how
wages increase exponentially with college ranking, while, at the same time, this relation
varies with individuals’ work-ethic. The figure shows in red the matched DW subsample.
This suggests that the reason why observational methods recover effects in the DW sample
with apparent ease is that this subsample consist of individuals with high effect homogeneity.

Ribeiro, Neffke and Hausmann

3.3 Discussion

Which DGP was selected by SFE? Table 1 in the Appendix B lists the 20 variables with the
largest effects against 20 selected by a traditional model-selection algorithm, a regularized
(LASSO) regression. The two lists are very different. Among the variables selected by
a LASSO are alimony money received, unemployment in past two years, money received
from training, money from social security. Several of these reflect consequences, or just
components, of an individual’s income. In contrast, the top variables selected by SFE are
work-ethics, race (African-American), NSW treatment, recent school attendance and recent
employment. All these variables are arguably connected to causes of income differences such
as education, work attitudes and discrimination.

These results suggest that SFE may also shed light on the direction of causation. To explore
this further, we revisit the earlier simulations, adding variables that are consequences,
not causes, of the outcome variable. We progressively add 10 variables ut
, 0 < t ≤ 10,
which are increasingly correlated with y, with expected Pearson correlations 1−
t
. Fig.2(e)
shows the expanded graphical-model and Fig.2(f) ATE estimates. For most methods, even
a small numbers of consequences significantly biases estimates. In contrast, SFE estimates
remain unbiased.

We introduced SFE in this article, a computational tool for nonexperimental causal
effect estimation which we compared to several estimators from the Statistics and Machine
Learning literature. SFE allows researchers to represent nonexperimental data as incomplete
factorial designs, eq.(1). We have shown that, as result, it can recover the ground-truth in
synthetic data and in Lalonde’s seminal setting - estimating causal effects with less bias and
error than alternatives. We have also shown effect estimates at the individual level and in
the entire nationwide NSW program, not relying on ex ante model and population selection
criteria, outperforming estimates that used expert specifications. A more abstract goal was
to demonstrate that the troves of data on pairwise treatments and confounders in common
nonexperimental data can be very useful when estimating causal effects. Many fields, from
Medicine to the Social Sciences, face new realities where historical data is increasingly
accessible and new data is constantly accumulating. The tool could enable new uses for
such data in scientific investigation.
