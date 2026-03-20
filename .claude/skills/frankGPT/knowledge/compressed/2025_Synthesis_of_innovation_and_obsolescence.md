---
source: 2025_Synthesis_of_innovation_and_obsolescence.pdf
pages: 14
extractor: pdftext
tokens_raw: 15742
tokens_compressed: 10691
compression: 32%
---

Synthesis of innovation and obsolescence

Edward D. Lee1,*, Christopher P. Kempes2
, Manfred D. Laubichler2,3, Marcus J.
Hamilton2,4,5, Jeffrey W. Lockhart6
, Frank Neffke1
, Hyejin Youn2,7, Jose Ignacio Arroyo ´
,
Vito D. P. Servedio1
, Dashun Wang8
, Jessika Trancik9
, James Evans2,10, Vicky Chuqiao
Yang9
, Veronica R. Cappelli11, Ernesto Ortega1
, Yian Yin12, and Geoffrey B. West2

1Complexity Science Hub, Vienna, Austria
2Santa Fe Institute, Santa Fe, USA

3School of Complex Adaptive Systems, Arizona State University, Tempe, USA
4Department of Anthropology, University of Texas at San Antonio, San Antonio, TX, USA
5School of Data Science, University of Texas at San Antonio, San Antonio, TX, USA
6University of California, Berkeley, USA
7Seoul National University, Korea

arXiv:2505.05182v1 [physics.soc-ph] 8 May 2025

8Kellogg School of Management, Northwestern University, Evanston, USA
9Massachusetts Institute of Technology, Cambridge MA, USA
10University of Chicago, Chicago, USA
11IESE Business School, Barcelona, Spain

12Department of Information Science, Cornell University, Ithaca, USA
*e-mail: edlee@csh.ac.at

ABSTRACT

Innovation and obsolescence describe the dynamics of ever-churning social and biological systems, from the development of
economic markets to scientific and technological progress to biological evolution. They have been widely discussed, but in
isolation, leading to fragmented modeling of their dynamics. This poses a problem for connecting and building on what we know
about their shared mechanisms. Here we collectively propose a conceptual and mathematical framework to transcend field
boundaries and to explore unifying theoretical frameworks and open challenges. We ring an optimistic note for weaving together
disparate threads with key ideas from the wide and largely disconnected literature by focusing on the duality of innovation and
obsolescence and by proposing a mathematical framework to unify the metaphors between constitutive elements.

Over the last 3.4 million years1
, we have experienced monumental
changes in the quality2
and pace3 of life due to rapid

to the biosphere whose consequences for biodiversity and
human societies remain uncertain.

innovation and its consequences. These include technological
changes like the rise of modern medicine, the transistor, the
Internet, and most recently the AI revolution, besides social
changes like universal suffrage and the resurgence of antiliberalism.
These have gone hand-in-hand with the demise
of vacuum tubes, 1990s fashion, and, more profoundly, the
destruction of biomes on an unprecedented scale4
, including
the large-scale disappearance of coral reefs, melting of
the cryosphere, and massive deforestation. We live in a dynamic
world, one that is constantly upturned and reshaped by
the inseparable forces of innovation and obsolescence. Yet,
our scientific understanding of this dynamic duality is still
nascent. Obsolescence, in particular, is largely overlooked
compared to the celebrated and promoted narrative of innovation,
creating conceptual gaps, ambiguity, and a lack of formal
approaches with testable hypotheses. This theoretical imbalance
is especially concerning, given several poorly understood
yet increasingly apparent trends. These include a slowdown
in economic productivity that underpins global growth5, 6
; a
decline in rates of scientific and technological progress7
, disruptiveness8,
and canonical progress9
; reduced innovation

The world we inhabit lies in between the frontiers of innovation
and obsolescence. Key to advancing the scientific
understanding of the dual forces is to recognize how they are
both deeply interwoven into nearly every field of inquiry11
.
Schumpeter interlinked them in the concept of “creative destruction,”
the process of firm birth with death12. Similarly,
Kuhn’s notion of paradigm shift centers at the conditions for
innovation and obsolescence within the dynamics of science13
.
Darwin introduced the idea of incremental changes leading to
the vast diversity of life, complemented by Kauffman’s ideas
about the “adjacent possible” to describe the set of novelties
that are one step away from what is now possible14. Meanwhile,
the science of science brings to the table both universal
and domain-specific features, mechanisms, and structures in
the process of scientific discovery15, 16. The list could go on,
but, unfortunately, the very breadth of the topic, the study of
innovation and obsolescence, is a veritable kaleidoscope.
Research remains fragmented, with different disciplines
operating in silos, each using distinct methods and definitions.
For example, minimal physics models may explain
exponents for scaling relations of novelty production17, but
how these are related to how teams generate novelty remains

within the legal system10; and accelerating ecological changes
unclear18. Similarly, the connection between biological evolution
and economic innovation19 remains elusive. In both
cases, the quality and quantity of measurements hinder intellectual
progress; the fossil record is sparse and incomplete20
,
and measures for a proper “phylogeny” of ideas are debated21
.
Although innovation is undoubtedly a fundamental element
of biological and social dynamics, there are seemingly insurmountable
disciplinary chasms that need to be bridged.

Box 1

Note on conceptual ambiguity

There is no single, agreed-upon definition of either
innovation or obsolescence. The lack of consensus
underscores the need for formal, mathematical, and
testable definitions, which require an iterative dialogue
between ontology—defining what we aim to study—
and empirical research that captures these concepts.
But there are key aspects that recur. Innovations, in
contrast to “inventions,” have wide impact economically12
or ecologically24. Naturally, this raises the
question of what one means by either criterion, and for
this, there is no standard quantitative definition, and
there is much plastic use of the term. Innovations can
also take many forms, including an improved physical
form of a tool, the reuse of an existing tool for a new
use, or exaptation (e.g., evolution of feathers from thermal
regulators to flight enablers25), and the expansion
of ecological niches26. As a corollary, the meaning
of “one step away” into the adjacent possible remains
debated. Obsolescence faces an analogous quandary.
Most simply put, obsolescence refers to the complement
of innovation, or to have negligible impact on
the dynamics of innovation and the wider ecology of
the system. Extinction is one avenue, but commonplace
items like nails may have negligible impact on
innovation, despite their omnipresence. Again, this is
not a unique specification: in social systems, obsolescence,
like innovation, can happen in multiple ways. It
can be voluntary or involuntary, the former resulting
from strategic or policy decisions to maintain limited
resources and to drive innovation and productivity (we
discuss this idea further in “Fundamental variations”).
Additionally, ideas or technologies can be permanently
forgotten or become unpopular. Some examples may
be irreversible (e.g., Roman cement or Damascus steel)
while others are reversible23 (e.g., vinyl records).

A major difficulty is the challenge of crossing the bridge
from a conceptual understanding to predictive mathematical
theories. Despite foundational work clarifying conceptual
elements and proposed models, the notion of what it means to
innovate, the precise point at which novelties become innovations,
and the multitude of different processes that one might
plausibly call obsolescence leads to a flexibility in the mappings
that render cumulative progress on the problem difficult
(Box 1). Instead, bringing the three together—the conceptual
debate, formal mathematical theories, and a diverse range of
data sets—will help triangulate exactly what it means to “innovate”
or to go “obsolete.” Such a combination goes beyond
individual disciplines and requires extensive familiarity with
various literature, mathematical fluency, and technical rigor.
This calls for a new way of forging ahead by bringing together
people into a coherent field of study instead of dispersing
them across disciplines.

In the face of this challenge22, 23, we ring an optimistic note
in light of a working group held at the Complexity Science
Hub (CSH) in December 2022. By bringing together a range
of fields under the guise of complexity science, we were able
to find common conceptual ground that hopefully serves as
a starting point for reorganizing our efforts, not as an evershifting
kaleidoscope, but as elements of a shared puzzle.

We bring together key concepts from various disciplines
to develop a shared framework, with the five key constitutive
components detailed in Box 2. These are inspired by recent
work that touches on two aspects that deserve more attention
in the context of innovation27. One is a foundational aspect
that reemerges many times in the literature, but is neither fully
understood nor always incorporated into models: the relationship
between innovation and obsolescence, including the role
of obsolescence in promoting innovation and vice versa. The
other is the importance of mathematical and quantitatively
testable predictions, which includes engaging with the difficulty
of mapping proxies of innovation onto the dynamics
thereof. By connecting these aspects in an accessible way
(and skimming over some of the finer points of debate in the
literature), we pose some open problems around which the
emerging field can coalesce.

constraints, and metrics.

The realized space of the possible is the set of widespread
technologies, mutations, or scientific theories, represented
as a graph or hypergraph that connects related innovations.
The space leads towards the “adjacent possible,”14, 28 and
it disintegrates at the “adjacent obsolescent” (the set of all
things one step away from obsolescence27). Naturally, the
composition of the space is field-dependent. In economics,
for example, the space could be manufacturing techniques29
,

Five-part framework
We propose a level of abstraction that is broad enough to
generalize the problem across domains while remaining practical
within each field. The theoretical framework boils down
to five components that are highlighted in Box 2: a space
of the possible, agents, inventions and novelties, emergent

product capabilities30, 31, or human capabilities32, 33. In management
science, particularly transformative innovations (e.g.,
“radical,” “disruptive,”, or “architectural”) are of special interest34,
35 because they change the nature of the market and,
therewith, the competitive structure of an industry, and drive
incumbents out of the market (e.g., digital photography, on2/14
Box 2

At the highest layer, we have emergent constraints. These
are shaped by the collective dynamics of agents—through
cooperation, competition, or swarming—that lead to largerscale
phenomena like selection, self-organization, or social
structures. These emergent dynamics create constraints that
feedback into agents’ actions, defining the macro-scale limits
within which innovation occurs. Such limits might correspond
to competitive forces in an economy in the context of
firm-level innovations. Within the context of organizational
innovations within a firm, they might represent policies to
shield budding inventions and allow them to mature in less
constraining selection environments. In politics, media dynamics
can drive polarization and regulatory stasis, such as
the use of lead additives in fuel, despite evidence of its adverse
impact on health49. Along with the process of novelty
generation, emergent constraints sandwich the innovation at
the “mesoscale” as we show in Figure 1.

Five key elements of innovation and obsolescence

The elements draw on ideas from across fields, demonstrating
the transdisciplinary nature of the problem.
We briefly summarize these here, and elaborate on
them in the main text.

1. Space of the possible is the set of realizable innovations,
bounded by a frontier of innovation
(Kauffman’s “adjacent possible” from theoretical
biology) and the boundary of obsolescence (the
“adjacent obsolescent”).

2. Agents drive innovation and obsolescence, and
their associated capabilities and limitations are
emphasized in the social sciences.

3. Inventions and novelties are precursors of

widespread and successful innovations, as distinguished
in economics.

Finally, metric refers to our limited ability to measure the
processes involved in innovation and obsolescence, which
limits how we can test, rule out, and infer models. For example,
it is impossible to access the full set of novelties at
any given time, or new production techniques may be retained
as trade secrets. We must rely on lower-dimensional
measures of the full process by projecting them down into
simplified measures like citations, productivity, or prevalence
versus performance-based metrics50. This question is not independent
of the ontology, or the definition of what we are
studying, of innovation touched on above. The limits of practical
choices remain to be further explored. Ideally, innovation
can be studied independently of the metric, which future work
may inform by connecting different metrics to one another
from theoretical principles.

4. Emergent constraints are at the macro-scale, or
collective processes that lie above the level of
innovations and feed back into lower-level processes.
Ecology is rich in such examples like
niche construction.

5. Metric refers to the epistemological challenge of
measuring innovation and obsolescence.

line video streaming, etc.). Additionally, organizational innovations
may involve the changing structure of the markets
for technology in the 19th century36 to the R&D labs of the
early 20th century37, and distributed innovation in multidivisional
firms38, changing not technology but the way the firm
searches for technologies. In biology, proposals include genotype
and phenotype39, 40 and, on the ecosystem level, rewiring
of ecological networks41 or the emergence of symbiotic relationships
that permit new metabolic pathways. In science, we
often refer to the space of concepts or theories42, 43
.

The key ideas are in the reduced conceptual diagram in
Figure 1. At the center of the diagram is the space of the
possible, depicted as an orange graph that connects similar
objects within this space. Agents possess properties, traits,
or capabilities that are represented by the space, and so they
live on the graph. Agent behavior drives the space to grow
into the adjacent possible on the right side, which is related to
the dynamics of obsolescence on the left side. This process
is sandwiched between the rising foam of novelties at the
bottom in purple that leads to innovations and the collective
environment at the top that feeds back to constrain agent
behavior, the production of novelties, and the processes of
innovation and obsolescence. In any given domain, multiple
coexisting processes may display such dynamics, whether they
are interacting or not. Thus, the five-component framework
is a minimal but multiscale representation of innovation and
obsolescence, serving as a navigational map for the study of
innovation and obsolescence.

Agents consist of firms, organisms, or scientists at the scale
of individuals and collectives that drive the processes of innovation
and obsolescence44. In our framework, agents occupy
the space of the possible. Some agents may be fixed to specific
sites, analogous to a genotype that uniquely distinguishes
groups. More generally, agents can move from one site to
another, taking up or disposing of innovations flexibly, which
induces a population dynamics within the space of possibilities.Invention
and novelty are the source of innovations, or the
micro-dynamics that precede fixation. These are called “inventions”
in economics and “genetic mutations” in biology.
This is the classic distinction between possibilities that have
occurred at some point versus possibilities that have become
common and widespread as are economically successful innovations,45–48
fixed genes, or dominant scientific paradigms13
.
Sometimes inventions and novelties are distinguished from
one another11
.

As an example, we consider how scientific work on innovation
can be mapped onto key elements of the diagram. Novelty
creation focuses on methods of search through the adjacent
possible, describing both the dynamics of the agents at the
innovation front, the way they are organized, and the inherent

EMERGENT CONSTRAINTS MACRO

adjacent
possible
adjacent
obsolescent

INNOVATIONS
MESO

NOVELTIES MICRO

Figure 1. Conceptual diagram of the space of the possible sandwiched between the adjacent possible and the adjacent

obsolescent as a 3D visualization. From the roiling set of novelties represented by the points on bottom (micro), a few rise to
become innovations, the nodes on the orange graph (meso), that shape the collective environment captured by the hazy regions
in the background (macro).

topology of the adjacent possible17, 51. When the process of
exploration is recombinatorial, the value of fruitful combinations
incentivizes certain choices made in technological
innovation7, 46, 52, appetizing cuisine53, how high-performing
firms collect labor skills54, etc. Sexual reproduction is a
mechanism by which fruitful combinations are favored in evolution55.
How novelties rise to become innovations touches
on the evolution of multicellularity, or how complex individuals
emerge that are then subject to selection forces in the
environment56, 57. From another perspective, we can also examine
the constraints that limit novelty exploration, whether
in economic contexts like firms, or in biological contexts as favored
mutations and evolutionary bottlenecks. More broadly,
constraints frame scientific success58 and depend on factors
like individual attributes59, 60, institutional prestige61, 62, and
team size18. Studies on the challenges of scientific innovation
describe both agent population dynamics (the movement
of scientists through the space of theories) and the effective
constraints generated by the scientific endeavor, not least
funding63. On the other end of the graph lies the study of obsolescence,
which has received less attention. Some examples
include extinction patterns64 or changes in cultural norms65
,

exist as disconnected components. The diagram thus provides
a way to contextualize together the diverse literature—far beyond
the few illustrative examples that we cite here—on both
innovation and obsolescence.

More formally, the elements come together in a mathematical
framework coupling a living space of the possible,
a temporal graph G (t) with vertices x ∈ X and edges e ∈ E
changing with time t, which can be generalized to hypergraphs
with simplicial links66. In addition to the changing structure,
the population dynamics of agents living in the space are described
by a time-dependent occupancy number n(x,t)
27, 67
.
Agent behavior determines how they push into the adjacent
possible (the dynamics of the innovation front xi), and obsolescence
shrinks the graph (the obsolescence front xo) as we
show in the center of Figure 1. The influx of novelties and
effective constraints modify the parameterization of the aforementioned
aspects, e.g., how new edges e from the adjacent
possible are connected to G . In other words, the structure of
the graph encodes the impact of the concomitant processes of
novelty generation and environmental constraints, which in
turn depend on the role of innovations. This corresponds to a
set of nonlinear dynamical equations that reflects the mutual
dependencies between the layers.

though, as with innovation, the exact definition of obsolescence
remains debated. In any given system, one might expect
parallel instances of innovation-obsolescence dynamics to coAs
a result, the diagram provides a shared language and an
incipient mathematical structure for ongoing research in the

field of innovation-obsolescence. In the boxes, we go through
several examples discussed in the workshop that shed light
on different aspects of the framework. For example, a variety
of innovations in materials, manufacturing, and organization
have driven steady cost reductions in the unit prices in solar
cell manufacturing (Box 3). Another example is improvements
in computational algorithms, including observations
of novelty generation that fail to push the performance frontier
(Box 4). In long-term evolutionary dynamics, novelties
can be separated into distinct evolutionary phases, where innovations
drive optimality given physical constraints until
the constraint is modified by a “game-changing” innovation
(Box 5). Again, these examples indicate how the minimal
formulation provides a way of incorporating previous work
by bringing different aspects to light.

Box 3

The green transition is of paramount importance today.
As an example of a problem that could be mapped to
the five-part framework, we discuss the falling costs
of solar cell manufacturing72. One mapping of the
problem to the space of the possible is as a graph of the
set of combinations of cost-saving measures, where
each vertex would correspond to a particular manufacturing
process, and the edges connect proximate
techniques. The high-dimensional space is usually projected
down to cost efficiency as in Figure 3a. The
importance of cost efficiency suggests that obsolescence
is primarily dictated by market forces as manufacturers
eliminate uncompetitive techniques. This
may describe how previous combinations of manufacturing
techniques are replaced by improved ones. One
notable aspect of the problem is that earlier improvements
stem from “low-level” improvements in energy
efficiency and manufacturing, but later ones stem from
“high-level” mechanisms such as economies of scale,
or that the nature of later innovations is different from
that of earlier ones.

Thus, the framework advances three key ideas by building
on the notion of a space of the possible. First, innovation
and obsolescence are related. They may drive each other on—
innovations rendering possibilities obsolete or obsolescence
opening the door to new innovations—or they may (rarely)
proceed independently. Schumpeterian creative destruction12
and Darwinian competition68 are examples of this process.
In the former, the tension between the two forces is maximized
under resource constraints69, which imply zero-sum
dynamics such as with van Valen’s Red Queen hypothesis—
although the strength of the relationship can vary. In many
approaches, it is common to consider innovation and obsolescence
as endogenous (i.e., innovation as the result of random
mutation, and extinction as a natural outcome of competition),
but they may be constitutive elements in the model, which
forces an explicit accounting of the relationship between the
two. Second, the evolving space of the possible is sandwiched
between the microscopic dynamics generating novelty and
the resulting effective constraints on the system, which then
feed back into the variety of novelties explored by the system.
For example, the multitude of biological mutations results
in a few successful ones that can establish a new dominant
ecology, which increasingly favors their survival24. This second
point establishes a multiscale perspective of innovation
with interaction between three scales—the micro is the froth
of inventions, the meso layer is innovations, and the macro
is emergent constraints (Figure 1). Finally, the third point
emphasizes the importance of developing complementary,
multi-scale, and experimental perturbations to extend available
quantitative metrics, which serve as limited proxies of
the process. Historically, the inability to do so has mired
distinctions—such as those between invention and innovation
or between forgetting70, extinction, and obsolescence—in the
conceptual realm. As is the case even with “tangible” physics
variables71, inventing methods of measurement is a crucial
aspect of the understanding8
. Importantly, we emphasize that

Fundamental variations
The unified framework provides a scaffold for exploring variations
across different systems, as we diagram in Figure 2.
These conceptual variations allude to some of the substantive
aspects that remain untranslatable between systems. Clearly,
the substrate in which innovations occur (the constituent elements
of the space of the possible) and the agents that are
innovating differ from system to system. The particular mechanisms
by which innovations occur, innovation drives obsolescence,
or vice versa, are different. Such differences do not
bar statistical or structural similarities. As an example, we
could group different types of relationships between innovation
and obsolescence: if they happen one-to-one as in the
Schumpeterian formulation, we have a case of conservation27
.
A differential rate might be a case where innovation drives
obsolescence because it displaces competitors, obsolescence
drives innovation because it provides new niches for agents to
thrive, or even cases of regulatory obsolescence where certain
innovations are strategically removed from the space to stimulate
innovation83. In other words, the five-part framework
refrains from committing to a particular mechanism, but lies
at a level of abstraction that connects them to one another
through dynamical, statistical, or functional properties, which
then facilitates the comparative studies of diverse systems.

We present several important variations to the proposed
framework:

the framework is not just conceptual but also suggests a mathematical
framework of stochastic, dynamical equations linking
the micro, the meso27, and the macro along feedforward and
feedback loops.

1. Core-periphery of knowledge as a structural variation of
the space of the possible: Innovations may be pinned to
previous ideas. Scientific theories have inertia, where

Box 4

Box 5

How does performance improvement in artificial intelligence
come about73? As another example, we
discuss algorithmic innovations, studied with a detailed
data set of Kaggle data science competitions.
Here, we observe each individual submission and its
relative prediction performance on the entire history of
submissions. As we show in Figure 3b, there is a sea
of algorithmic attempts that do not push the frontier
of performance, but floating on top of it (black line)
are the innovations that do and set the baseline for
the next. Here, one formulation of the space of the
possible is as the set of prediction algorithms for the
task (each algorithm, for example, consisting of a set
of components parameterized by independent performance
parameters), which are then projected down to
a scalar measure of performance. Performance is a
natural metric because the last maximum determines
the winning team. Agents correspond to the individual
coding teams that are submitting to the competition. A
particularly interesting aspect of this study is that we
can distinguish between attempts that do not push the
performance frontier, inventions and novelties. Innovations
show punctuated dynamics, but these can be
shown to arise from the combination of incremental
and radical algorithmic attempts, capturing also the
unseen layer of failures73, 74. In the broader context
of the AI race today, we see the importance of emergent
constraints in how algorithmic improvements alter
the distribution of resources like private investment in
first movers75, how they change worker productivity
and thus shape demand76, and stimulate regulation that
aims to shape pathways of innovation77 such as GPDR.

Metabolic processes in single-celled organisms have
undergone several major evolutionary epochs78, 79
.
With the advent of new metabolic designs, such as

the transition from prokaryotes to unicellular eukaryotes
to metazoans, the relevant physical constraints
change and another limit on growth rate can be saturated78.
Within each epoch, the population devises
innovations that allow organisms to saturate the growth
rate given physical constraints. In terms of the fivepart
framework, we might think of innovations that
improve metabolic efficiency within each phase as
a faster process nested within slowly changing constraints
that lead to discrete jumps in allometric scaling
exponents80. The latter are the metadynamics of innovation
and obsolescence. The space of the possible
consists of cellular structures, often projected down to
rate measures, such as metabolism or growth. Selection
is responsible for the emergence of new cellular
functions and the disappearance of old ones, either in
the sense of extinction or playing an insubstantial role
in future evolutionary trajectories.

peripheral areas was used to stymie innovation in a core
area. Similar refusal to abandon a core idea has led to a
century of innovation in neuroscience86, 87. Innovation
research has long thought of innovation as a directional
or sequential process of recombining existing ideas in
new ways, but this case highlights that the opposite matters.
Human attention, knowledge, and effort are finite.
Innovation requires bracketing off potential avenues. Understanding
which things are overlooked and why are
key to a complete understanding of innovation, including
how agents see the space of the adjacent possible as a
function of their relationship with the space of the possible.
We picture this as a variation of the structure of
the space of the possible, where some innovations (core
ideas) are surrounded by a hierarchy of supporting ones
like in Figure 2a; dense local structure reduces the probability
of obsolescence and even enhances the probability
of innovation.

agents at the level of individual actors and scientific
communities are organized around core concepts that are
resistant to change, yet this resistance to change can itself
drive innovation. A microcosm of such a phenomenon is
the development of the gyroscope within the MIT Instrumentation
Lab84. There, a director stubbornly insisted on
sticking with an older technology, a single degree of freedom
floating gyroscopes, while the rest of the industry
advanced. The unwillingness to question the best kind
of gyroscope forced the lab to innovate in myriad peripheral
areas, such as precision machining, measurement,
material stability, clean room techniques, and bearing
friction, in order to keep up with overall performance.
The lab generated a “protective belt” of innovation to
protect the “hard core” of unquestioned technology, to
borrow Lakatos’ terms85. Refusal to innovate in one area
led to compensatory innovation in others. Or, considered
from a different angle, innovation in a variety of

2. Intentionality as heuristics and strategy: Human innovation
follows a purposeful and biased path towards future
innovations based on planning and decision making23.
Human cognition over evolutionary history has
been particularly good at picking up on the available
non-random mechanisms in the biosphere by specializing
in things like niche construction and epigenetic-type
activities, such as the intentional recombination of materials
to solve adaptive solutions it identifies in the world.
The ability of humans to generate variation intentionally
clearly has its roots in evolved mechanisms but operates

(a) core-periphery (b) intentionality

(c) regulated obsolescence (d) gradual vs. saltational

Figure 2. Diagrammatic variations on the basic framework. (a) Core-periphery. (b) Intentionality. (c) Active obsolescence. (d)
Gradual vs. saltational innovation.

at faster scales than natural selection88. At the societal
level, the purposeful generation of possibilities is manifest
as exploration centered around highly connected
technologies89, perhaps deterred by regulatory policies90
or tied to keystone technologies91 that unlock new ones
(e.g., transistors). Such anchoring may be essential13
,
but it also can lead to incrementalism42. More recent
developments suggest that other organisms also have
developed mechanisms for generating useful novelties.
Such mechanisms include the potentiation of beneficial
mutations92 and hypermutable states93, epigenetics that
selectively modifies genetic expression94, or niche construction
to favor long-term strategies that can affect
evolutionary trajectories95. Including these complexities
into a mathematical model could build on a framework
of constrained combinatorics, but perhaps more broadly
as attempts at prediction and learning by heterogeneous
agents, such as in game-theoretic terms, to assess the
competitive landscape.

free market picture, it is market forces that determine the
trade-off, but the trade-off is generally also shaped by
existing regulatory policies and strategic bets. In the complement,
slowing obsolescence can impede innovation,
such as with monopolies that attempt to stymie some
types of innovation96 or “patent thickets” intended to
build competitive moats or as rent-seeking83. Enhanced
mutation rates that move bacteria away faster from older
lineages, especially directed towards loss of function,
might be a form of active obsolescence in biological
systems put into stressful environments97. The strategic
aspect of this trade-off deserves more attention. We
might formulate this as a dynamic feedback relationship
between finite resources consumed by possibilities in the
adjacent obsolescent and those at the innovation front
or as a game-theoretic dynamic of agents competing for
resources.

4. Gradual vs. saltational in terms of scales: Is the arrival

of innovations gradual or punctuated? How about extinction98?
Again, we emphasize the importance of the
dual and potentially contrasting roles of innovation and
obsolescence. A long-running debate in the biological
literature has been about whether evolutionary trees represent
the slow accumulation of many small changes
or are long periods of stasis interrupted by short periods
of upheaval99–103. Observed shifts in ecosystems
in the fossil record or in the archaeological record of

3. Active obsolescence and regulation as a feedback loop:

In some cases, obsolescence might be a targeted or strategic
process to promote innovation, such as in regulatory
mechanisms. This is of particular importance, as Schumpeter
noted, in a resource-limited economy, where the
number of innovations that can be supported at any given
time is likewise limited. Then, the investment in a new
direction comes at the expense of an old one. In the

Figure 3. (a) Movement of the frontier of manufacturing innovation reflected in the falling costs of solar panels, which results
from the large space of cost-cutting steps to push the productivity front from reference 72. (b) Performance improvements (red
line) floating on the sea of algorithmic contributions (gray points) that fail to push performance boundaries from reference 73.
(c) Covid-19 phylogenetic tree for Europe, where each clade represents the set of detected innovations. Collected up until

August 10, 2022. Data from reference 81. (d) An example of saltational evolution; relative fitness across generations in E. coli
in the Long Term Evolution Experiment. Data points correspond to averages from reference 82.

cultural evolution have not ended the debate65, 104–106
.
A detailed and simultaneous view of both novelties and
innovations across multiple scales would help clarify
the debate around this problem. While the fossil record
is sparse, bacteria offer a good model of study given
their short generation times. The most visible example is
the Long Term Evolutionary Experiment (LTEE), which
propagates bacterial lines for thousands of generations.
There, it has been seen that simple genotypic mutations
precede and “potentiate” a quantum shift in the mutation
rates107, evocative of results from agent-based models108
.
This suggests one possible way of quantifying novelties
(random mutations) and innovations (phenotypic shifts),
but it is difficult to test models without more examples
of transitions than such experiments have historically allowed
(see more recent work that approaches this goal in
reference 109). The study of innovation in other contexts
may bring insight, such as punctuated progress in performance
records in competitive sports110 or for algorithmic
innovation. Underlying the jumps in performance are the

sea of attempts at algorithmic improvement (Figure 3b),
yet we are beginning to scratch the surface of how the bed
of failures matters for success74, 111. The deeper study
of recent, detailed data sets at a fine-grained level of the
innovative process will help translate the distinction into
a measurable, mathematical formulation of classes to
distinguish between the two paradigms originating in the
study of evolution.

New directions

To bring these conceptual and incipient mathematical connections
to life, we must first flesh out the quantitative predictions
implied by the interaction between innovation and
obsolescence. Second, we must take more seriously the role
of mathematical predictions in explaining theory in order to
build testable frameworks across the disciplines. How far do
such coarse-grained theories go for specific domains? At what
point do domain-specific examples require domain-specific
mechanisms? In the strong form, this calls for synthesizing

the threads that we have put together into a field of study,
one of innovation cum obsolescence. Such a challenge requires
bringing together interdisciplinary minds to work on
fundamental problems.

have the longest record of roughly 3.8 billion years of innovation
and obsolescence, but the field has also produced a
number of formal and mathematical theories and experimental
approaches addressing these challenges. In the context of
evolutionary biology, innovation and obsolescence are linked
through the life cycle of systems because there would be no
room for novelty without death and extinction. As we discuss
here, the origin of novelty is a separate problem from the
success of an innovation, and the causes that explain how novelty
originates are connected to the processes that govern the
development and operation of these systems. These include
such phenomena as recombination and the constraints that act
on evolutionary space14 of the possible. Finally, the success of
an innovation involves complex feedback dynamics of niche
construction. The effective space of possibilities depends on
the specific internal and external constraints, evolving with
each transformation. Part of our contribution is to recombine
the key ideas to guide us through the broader topic of innovation
and obsolescence across a large number of systems to
reshape the ongoing debate on ontological and epistemological
differences22, 23
.

One open question is how novelties become innovations,
which echoes the fundamental challenge of the genotypephenotype
map39. This refers to the problem of determining
how mutations at the level of the genetic code correspond
to changes in the phenotype and the level at which selective
pressure is experienced112. An analogue in economics
or science113 is the patent or paper (genotype/invention),
which is insufficient to know its eventual success (phenotype/innovation).
A second challenge is the design of comprehensive
experiments to measure the multiple scales of the
problem and to validate mathematical models thereof. While
the tremendous increase in data sets has led to new opportunities,
studies of innovation are limited by the resolution of
novelty generation and how they yield innovations, leaving
untested model assumptions or parameters. Similar questions
arise in computational models with artificial life114. This calls
for centers in which experimentalists and theoreticians, again
across disciplines, work closer together115
.

The power of an interdisciplinary approach is that contrasting
the dynamics may reveal new mechanisms that differ
across the systems and allow one to test the importance of
various processes by shifting them dramatically. However,
it is unlikely that such problems can be genuinely addressed
where the usual domain walls physically divide departments.
It is a new, innovative place, free from disciplinary constraints,
within or without the university walls, that will seed growth
in the interstitial. The hope is that understanding the diversity
of innovation dynamics across systems also leads to a new
understanding of what is possible in any given system and
allows us to chart the future regions of the possible into which
a system might be moving. The scientific challenge is enormous,
and it spans conceptual, mathematical, and empirical
debates121. With coalescence across disciplinary boundaries,
we are cautiously optimistic about moving towards a unified
and mathematical theory of innovation and obsolescence.

The challenges call for revivifying and further advancing
mathematical frameworks, perhaps those that handle stochasticity
in large, nonlinear dynamical systems: random matrix
theory for many-body interacting and nonequilibrium systems
and stochastic thermodynamics for connecting the apparent
unpredictability of innovations with the question of
computability116. Existing frameworks like scaling theory
that have been put to work in building the interstitial might
provide the next steps, much in the way of metabolic scaling
theory to compare ecosystems117 and as a bridge to urban
ecosystems3, 118–120. Information theory has provided a
rich set of tools and conceptual models for studying crossdisciplinary
problems40. As we touch on here, networks also
provide a natural and versatile way to characterize various
aspects of the problem (e.g., how evolutionary or technological
innovations interact in the space of the possible). Such
tools have been forged in statistical physics22, representing a
fertile scaffolding for extending theory. For example, certain
innovations like the transistor have been transformative and
thus lend themselves to the notion of phase transitions, but
there are few (and fewer mathematical) connections between
the two ideas in the studies of innovation or obsolescence.
A shared mathematical formulation may help us start to understand
how the qualitative differences in a rich conceptual
area are expressed in quantitative distinctions, not least the
distinction between innovative and obsolete objects. It is not
only applications of existing mathematical techniques, but we
imagine that bringing a rich area like innovation and obsolescence
in close proximity to the quantitative realm may also
inspire mathematical advances.
