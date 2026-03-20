---
source: 2024_Colocation_of_skill_related_suppliers_--_Revisiting_coagglomeration_using_f.pdf
pages: 49
extractor: pdftext
tokens_raw: 24007
tokens_compressed: 13819
compression: 42%
---

Colocation of skill related suppliers – Revisiting

coagglomeration using firm-to-firm network data

arXiv:2405.07071v1 [physics.soc-ph] 11 May 2024

S´andor Juh´asz1,2,*, Zolt´an Elekes2,3, Vir´ag Ily´es2,4, Frank Neffke1

1Complexity Science Hub, Vienna, Austria
2ANETI Lab, HUN-REN Centre for Economic and Regional Studies, Budapest, Hungary
3CERUM, Ume˚a University, Ume˚a, Sweden

4ANETI Lab, Corvinus University of Budapest, Budapest, Hungary
*Corresponding author: juhasz@csh.ac.at

Abstract

Strong local clusters help firms compete on global markets. One explanation for this is
that firms benefit from locating close to their suppliers and customers. However, the
emergence of global supply chains shows that physical proximity is not necessarily a
prerequisite to successfully manage customer-supplier relations anymore. This raises
the question when firms need to colocate in value chains and when they can coordinate
over longer distances. We hypothesize that one important aspect is the extent to which
supply chain partners exchange not just goods but also know-how. To test this, we
build on an expanding literature that studies the drivers of industrial coagglomeration
to analyze when supply chain connections lead firms to colocation. We exploit detailed
micro-data for the Hungarian economy between 2015 and 2017, linking firm registries,
employer-employee matched data and firm-to-firm transaction data from value-added
tax records. This allows us to observe colocation, labor flows and value chain connections
at the level of firms, as well as construct aggregated coagglomeration patterns,
skill relatedness and input-output connections between pairs of industries. We show
that supply chains are more likely to support coagglomeration when the industries involved
are also skill related. That is, input-output and labor market channels reinforce
each other, but supplier connections only matter for colocation when industries have
similar labor requirements, suggesting that they employ similar types of know-how.
We corroborate this finding by analyzing the interactions between firms, showing that
supplier relations are more geographically constrained between companies that operate
in skill related industries.

Keywords: coagglomeration, labor flow network, skill relatedness, supply chain
1 Introduction

Fuelled by a dramatic decrease in transportation costs, global value chains (GVCs) nowadays
span across countries and continents (Crescenzi and Harman 2023; Baldwin and Freeman
2022; Johnson 2018). Yet, buyer-supplier transactions still surprisingly often take place
over short distances (Bernard, Moxnes, and Saito 2019). We argue that this puzzle can
be in part resolved by focusing on the heterogeneity in existing value chain linkages: not
all customer-supplier relations will be equally amenable to long-distance interaction. In
particular, we propose that existing spatial patterns of value chain connections reflect the
degree to which value chain partners use similar know-how, which would allow them to embed
significant amounts of tacit knowledge in their transactions. We evaluate this conjecture by
studying the coagglomeration of industries in Hungary, a country that is deeply embedded in
transnational value chains and for which rich micro-data exist that describe firms’ workforces
as well as their transactions with other firms.

Following Ellison, Glaeser, and Kerr (2010), a growing literature has analyzed agglomeration
externalities by studying coagglomeration (Helsley and Strange 2014; Faggio, Silva,
and Strange 2017; Howard, Newman, and Tarp 2015; Gabe and Abel 2016; Gallagher 2013;
Bertinelli and Decrop 2005; Aleksandrova, Behrens, and Kuznetsova 2020; Kolko 2010). One
strand of this literature has focused on differences between various sectors in their propensity
to coagglomerate, highlighting, for instance, differences between manufacturing and service
industries (Diodato, Neffke, and O’Clery 2018; O’Clery, Heroy, et al. 2021). So far, these

studies have focused on the activities that coagglomerate, neglecting heterogeneity in the
links between them. More importantly, the three Marshallian agglomeration forces – labor
pooling, value chain linkages and knowledge spillovers – have so far been treated as if they
acted independently from one another. In contrast, we argue that these forces can reinforce
one another.

We propose that, while firms coagglomerate to facilitate labor pooling and buyer-supplier
relations, these two channels do not operate independently. Instead, we expect that value
chain partners are more likely to coagglomerate if they operate in skill related (Neffke and

Henning 2013) industries. This proposition is based on the idea that much crucial knowledge
underpinning a firm’s competitive advantage resides in its human capital (Kogut and Zander
1992; Spender and Grant 1996). Firms that require workers with similar skills are cognitively
proximate and thus likely to be able to share knowledge and learn from one another
(Neffke and Henning 2013; Neffke, Otto, and Weyh 2017). Moreover, some intermediate
products require a clear understanding of how they are produced to effectively handle them.
In such cases, buyers may need to increase the cognitive proximity to their suppliers. Be1
cause geographical proximity facilitates both interfirm learning and coordination involving
the exchange of tacit knowledge (Jaffe, Trajtenberg, and Henderson 1993; Audretsch and
Feldman 1996), value chain interactions will benefit most from colocation if the industries
involved are also skill related.

We provide empirical support for this hypothesis, using uniquely detailed administrative
datasets from Hungarian public registers. These data cover all companies operating in
Hungary, 50% of their employees, as well as value-added tax records for buyer-supplier
transactions among them. Building on the literature on coagglomeration, skill relatedness
and production networks, we use these data to construct measures of coagglomeration, skill
relatedness and input-output connections between detailed industries.

We use these data first to show that Ellison, Glaeser, and Kerr (2010)’s finding that
value chain and labor pooling links drive coagglomeration in the US can be replicated for
Hungary. To do so, we rely on the same instrumental variables approach, instrumenting skill
relatedness and input-output linkages in Hungary with analogous quantities calculated in
other countries. Next, we show that input-output connections between industries only lead
to substantial coagglomeration if industries are also skill related. In contrast, skill related
industries always display substantial coagglomeration tendencies, regardless of whether or
not they are connected in value chains. Finally, we corroborate these aggregate findings at
the micro-level by studying detailed spatial patterns of interfirm ties.

Our study contributes to several strands of the literature. First, it adds to an expanding
literature on industrial coagglomeration (Ellison, Glaeser, and Kerr 2010; Helsley and
Strange 2014; Delgado, Porter, and Stern 2016; Faggio, Silva, and Strange 2017; Diodato,
Neffke, and O’Clery 2018; Steijn, Koster, and Van Oort 2022). Our main contribution to
this literature is that we uncover important interactions between coagglomeration forces.

Furthermore, we add evidence from Hungary, a small open economy where most inputs need
to be imported (Halpern, Koren, and Szeidl 2015). The exceptionally rich data for the

Hungarian economy allow us to go beyond studying potential linkages between industries
in terms of skill relatedness and input-output coefficients to actual, observed, interactions
between firms, strengthening the micro-foundations in this area of research. Second, our
conceptual framework connects the literature on coagglomeration to discussions on buyersupplier
linkages in regional innovation systems (Cooke and Morgan 1994; Cooke 1996) and

in GVCs (Crescenzi and Harman 2023; Baldwin and Freeman 2022; Johnson 2018; Boschma
2024). Third, our study relates to the field of economic complexity analysis (Hidalgo and
Hausmann 2009; Hidalgo 2021; Balland, Broekel, et al. 2022). In particular, many product
and industry spaces that are used in this literature are derived from coagglomeration patterns.
By analyzing the drivers of coagglomeration patterns, we therefore also shed light

on the forces that are captured in the product and industry spaces of economic complexity
analysis.

The paper is structured as follows. Section 2 reviews prior literature and derives hypotheses.
Section 3 describes the data and construction of coagglomeration, skill relatedness

and input-output metrics. Section 4 reports our empirical findings. Section 5 concludes with
a discussion of implications, limitations and open questions.

2 Colocation of industries and firms

2.1 Coagglomeration

A core insight in economic geography is that firms seek each other’s proximity to benefit from
so-called agglomeration externalities. Accordingly, knowledge spillovers and access to pools
of specialized labor and suppliers provide strong rationales for firms to colocate (Marshall
1920). This results in an economic landscape characterized by marked spatial clusters of
related industries (Delgado, Porter, and Stern 2014). Marshall (1920)’s original account of
why such industrial districts form pointed to access to specialized suppliers, skilled labor
and knowledge: firms choose to colocate with their competitors because accessing these
resources becomes harder as distances increase. In spite of substantial decreases in the cost
of transporting goods, people and ideas (Glaeser and Kohlhase 2004; Agrawal and Goldfarb
2008; Catalini, Fons-Rosen, and Gaul´e 2020), geographical clusters of firms are still thought
to be core drivers of firms’ competitiveness (Porter 1990; Porter 1998).

In parallel, a large literature in economic geography and urban economics has studied
the role of agglomeration externalities in the success of local industries (Glaeser, Kallal,
et al. 1992; Henderson, Kuncoro, and Turner 1995; Rosenthal and Strange 2004; Beaudry
and Schiffauerova 2009; Caragliu, Dominicis, and Groot 2016). However, disentangling the
relative importance of different agglomeration forces proved hard, because they act concurrently
and all three forces lead to the same observable outcome: firms in the same industry
will concentrate geographically. A breakthrough was achieved by Ellison, Glaeser, and Kerr
(2010) who focused, not on agglomeration patterns of individual industries, but instead on
coagglomeration patterns of pairs of industries that differ in the degree to which they share
supplier, skill or knowledge relations. Doing so allowed the authors to show that coagglomeration
is best explained by input-output dependencies, but that the other two forces, labor
pooling and technological spillovers, play significant roles as well.

The work of Ellison, Glaeser, and Kerr (2010) has sparked an expanding literature on
coagglomeration (Helsley and Strange 2014; Faggio, Silva, and Strange 2017; Howard, New3
man, and Tarp 2015; Mukim 2015; Gabe and Abel 2016; Gallagher 2013; Bertinelli and
Decrop 2005; Aleksandrova, Behrens, and Kuznetsova 2020; Kolko 2010). One strand of this
literature has focused on heterogeneity in coagglomeration forces. For instance, focusing on
heterogeneity across time, Diodato, Neffke, and O’Clery (2018) show that, over the course
of the 20th century, the relative importance of labor pooling has increased to the point
that it has surpassed input-output linkages as an explanation for coagglomeration patterns.
Steijn, Koster, and Van Oort (2022) found a similar decrease in the relative importance of
input-output linkages over time. However, these authors also highlight the increasing role of
knowledge spillovers, identified through data on technological relatedness between industries,
which surpassed even that of labor pooling. Moreover, they show that these shifts are, at
least in part, brought about by increasing import penetration, a decrease in transportation
costs and a fall in routine tasks.

The relative importance of different Marshallian channels does not only change over time,
but also varies across economic activities. For instance, Diodato, Neffke, and O’Clery (2018)
show that coagglomeration of service industries tends be more sensitive to labor sharing
opportunities than coagglmeration of manufacturing industries. Whereas existing literature
has so far studied how agglomeration forces vary across time and across economic activities,

our analysis focuses on heterogeneity in the forces themselves. As we will argue below,
agglomeration forces are unlikely to act in isolation, but rather may reinforce each other.

2.2 Relatedness and economic complexity analysis

Another body of related work is the literature on economic complexity analysis (Hidalgo,
Klinger, et al. 2007; Hidalgo and Hausmann 2009) and in particular its adoption in evolutionary
economic geography (EEG) (Boschma, Balland, and Kogler 2015; Balland and Rigby
2017; Balland, Broekel, et al. 2022; Mewes and Broekel 2022). This literature argues that
places develop by accumulating complementary capabilities that together allow economies to
engage in complex economic activities (Hidalgo and Hausmann 2009; Hidalgo 2015; Frenken,
Neffke, and Van Dam 2023). Because many capabilities are hard to access from outside the
region (Neffke, Hartog, et al. 2018; Frenken, Neffke, and Van Dam 2023), economic development
often takes the shape of a branching process in which economies expand by diversifying
into activities that are closely related to their current activities (Frenken and Boschma 2007;
Neffke, Henning, and Boschma 2011; Hidalgo, Balland, et al. 2018).

Empirical work in economic complexity analysis often constructs abstract spaces that
connect industries that are “related”. These so-called industry spaces are relevant to our
analysis in two ways. First, the most widely used industry (or product) spaces are, in fact,

based on coagglomeration patterns (Hidalgo, Klinger, et al. 2007; Hidalgo 2021; Li and Neffke
2023). Consequently, there is a direct link between economic complexity analysis and the
coagglomeration literature. In this light, the coagglomeration literature can be seen as an
effort to understand the underlying factors that are captured in prominent industry spaces.

Second, economic complexity analysis has constructed industry spaces using information
other than coagglomeration patterns. A particularly relevant industry space is based on
Neffke and Henning (2013)’s “revealed skill relatedness”. The authors argue that the degree
to which two industries require similar skills can be inferred from cross-industry labor flows.

In essence, two industries are deemed skill related if labor flows between them are surprisingly
large, compared to a benchmark in which workers move randomly among industries.

In the context of Marshallian agglomeration forces, skill relatedness offers a natural way
to determine which industries draw from the same pool of labor, or from the same “skill
basin” (O’Clery and Kinsella 2022). Moreover, worker mobility is an important vehicle for
knowledge transfer, as evidenced by productivity growth and spillovers following labor flows
and coworker networks (Lengyel and Eriksson 2017; Eriksson and Lengyel 2019; Cs´afordi
et al. 2020). Therefore, apart from identifying skill basins, skill relatedness is also likely to
be a good proxy for cognitive proximity between industries.

2.3 Value chains and knowledge transfer

The importance of local interactions and the cluster literature’s emphasis on localized buyersupplier
networks would, prima facie, seem at odds with the rapid growth of GVCs over the
past decades (Gereffi, Humphrey, and Sturgeon 2005; Baldwin and Freeman 2022; Johnson
2018). That is, the existence of GVCs suggest that improvements in transportation and
communication technologies have allowed coordinating buyer-supplier interactions over long
distances. However, this does not hold true for all parts of GVCs: while the production
and assembly activities at the middle of the value chain have become geographically mobile,
high value-added activities at both ends of the so-called smile curve (Baldwin and Ito 2021),
like R&D and design, or marketing and associated services, exhibit substantial spatial (co-
)concentration (Mudambi 2008).

One of the characteristics that these spatially sticky elements of GVCs share is their reliance
on tacit knowledge. Because tacit knowledge is so hard to transmit over long distances
(Jaffe, Trajtenberg, and Henderson 1993; Audretsch and Feldman 1996), buyer-supplier relations
that embed much tacit knowledge will benefit from geographical proximity. This
point is well-established in the literature on regional innovation systems (e.g., Cooke and
Morgan 1994). For instance, in some cases, innovation needs to be coordinated along the

value chain (Azadegan and Dooley 2010), impelling suppliers to work with their customers
to integrate new technologies or help improve end products. Such interactions require knowledge
transfers and learning processes that are facilitated by geographical proximity (Cooke
1996). In other instances, intermediate goods can be used without much knowledge of how
they are made, which arguably allows for more spatial separation between value chain partners.
While buyer-supplier relationships thus vary widely in the extent to which they need
to embed – often highly tacit – knowledge, this diversity has not been explicitly considered
in the literature on coagglomeration.

2.4 Main hypothesis

Based on these different bodies of research, we expect that Marshallian coagglomeration
forces will reinforce each other. In particular, not all buyer-supplier linkages require spatial
proximity. Instead, we hypothesize that buyer-supplier linkages will only require that firms
colocate if the transactions also involve transferring knowledge. Furthermore, we expect
that industries that share the same pool of labor are often also cognitively proximate. As
a consequence, measures that assess the potential for labor pooling, such as labor flow
based skill relatedness, often also shed light on the degree to which industries operate in
technologically similar environments.

Taken together, these arguments lead to the main hypothesis in this paper: input-output
connections enhance industries to coagglomerate only if the industries are also skill related.
We test this hypothesis in the context of industrial coagglomeration in Hungary by first
adopting the approach proposed by Ellison, Glaeser, and Kerr (2010) in our data, and then
unpack the interacting roles of input-output and skill relatedness at the aggregate level of
industry pairs, as well as at the micro-level of firm-to-firm transactions.

3 Empirical setting

3.1 Measuring the coagglomeration of industries

Our empirical work relies on a firm-level dataset, made available by the Hungarian Central
Statistical Office (HCSO) through the Databank of the HUN-REN Centre for Economic and
Regional Studies1
(HUN-REN CERS Databank). It contains information from balance sheets
of companies doing business in Hungary. The data include the location of the company seats
(headquarter) at the municipal level, the main activity of the firms as four-digit NACE codes
1Databank of HUN-REN Centre for Economic and Regional Studies, https://adatbank.krtk.mta.hu/en/

(Statistical Classification of Economic Activities in the European Community, NACE Rev.
2 classification), the number of employees and further balance sheet indicators. We focus
on 2017 as this is the year for which all of these datasets provide information. A detailed
description of the firm level data and the distribution of employment and firms across regions
and industries can be found in Section 1 of the Supplementary information.
To measure the degree to which firms from different industries tend to colocate, we focus
on companies with at least two employees and aggregate the firm level employment data
to an industry-region matrix. We use this matrix to quantify the tendency of industry i to
coagglomerate with industry j, using the following metric proposed by Ellison, Glaeser, and
Kerr (2010):

EGKij =
PR
r=1(sir − xr)(sjr − xr)
1 −
PR
r=1 x
r

(1)

where sir = Eir/Er is the employment share of industry i in region r (missing indices indicate
summations such as Er =
PR
r=1 Eir), while xr is the mean of these shares in region r across
all industries. Ellison and Glaeser (1997) and Ellison and Glaeser (1999) show that this index
quantifies the likelihood that firms in industries i and j generate spillovers for each other
in a simple location choice model. The index is widely adopted and used as a benchmark
(see e.g., Diodato, Neffke, and O’Clery 2018; Steijn, Koster, and Van Oort 2022; Juh´asz,
Broekel, and Boschma 2021), as it is largely independent of the distribution of firm sizes in
industries and the granularity of spatial units. We calculate this index for both NUTS3 and
NUTS4 regions in Hungary for all pairs of three-digit industries and hereafter refer to it as
EGK coagglomeration.

As an alternative, inspired by the measures of Porter (2003), we use the correlation of
revealed comparative advantage (RCA) vectors to quantify the coagglomeration of industry
pairs. This indicator, which we refer to in the following as LC coagglomeration, is calculated
as follows. First, we calculate the RCA of industries in regions:

RCAir = (Eir/Er)/(Ei/E) (2)
A region is specialized in an industry when its RCA value is above 1. Next, we use the RCA
values to create a binary specialization matrix Mir:

Mir =
(
1 if RCAir >= 1
0 if RCAir < 1

(3)

Finally, we calculate the LC coagglomeration of two industries as the correlation between
industries’ specialization vectors:

LCij = corr(mi
, mj ), (4)
where mi and mj are column vectors of matrix M that describe the spatial distributions of
industries i and j.

We calculate this index on the basis of both NUTS3 and NUTS4 regions in Hungary for
all pairs of three-digit industries. The above specifications are two prominent ones among the
many ways to calculate coagglomeration indicators (Li and Neffke 2023). Figure 1 illustrates
the construction of these measures from a region-industry matrix, yielding plausible variation
in the coagglomeration intensity of various industry pairs. In Section 2 of the Supplementary
information we provide detailed descriptive statistics on both of these dependent variables
and compare them to common alternatives.

Figure 1: Constructing coagglomeration measures from a region-industry employment matrix.
(A) Region-industry matrix based on NUTS3 regions and three-digit NACE codes.
(B) The distribution of EGK coagglomeration values. For this illustration the tail of the
distribution with extreme values was cut off. The unedited figure can be found in Section 2
of the Supplementary information. (C) The distribution of LC coagglomeration values.

3.2 Skill relatedness

Previous studies established a number of approaches to capture the extent to which two
industries can draw from the same labor pool, including comparing the occupational composition
of industries (e.g., Ellison, Glaeser, and Kerr 2010; Diodato, Neffke, and O’Clery
2018), and measuring significant labor flows between them (e.g., Neffke and Henning 2013;
Neffke, Otto, and Weyh 2017). In this study we opt for the latter approach where the central
assumption is that workers tend to switch jobs between industries across which they can
transfer most of their skills and human capital.

To do so we rely on a Hungarian matched employer-employee dataset managed by the
HUN-REN CERS Databank. This longitudinal dataset contains the work history of a randomly
selected 50% of the total population on a monthly basis between 2003 and 2017.
It links data from different registers, including the Pension Directorate, the Tax Office,
the Health Insurance Fund, the Office of Education, and the Public Employment Service,
thereby providing comprehensive information on workers and their employers. Unique and
anonymized identifiers for both individuals and firms allow us to track the transition of individuals
between firms. We use all observed employment spells for each individual in the
dataset to establish employee transitions from one firm to the next. In cases when an individual
had multiple parallel employment spells before switching, we consider labor flow ties to
be created between the new employer and each of the previous employers. This information
on monthly labor flows between firms is then pooled across 2015-2017.

To measure the skill relatedness of industry pairs, we aggregate firm-to-firm labor flows to
the industry-industry level. Following the approach of Neffke and Henning (2013) and Neffke,
Otto, and Weyh (2017), the skill relatedness between two three-digit industries (NACE Rev.
2 classification) (i and j) is measured by comparing the observed labor flow between them
(Fij ) with what would be expected based on their propensity to take part in labor flows
((FiFj )/F).

SRij =
Fij
(FiFj )/F (5)
Here, Fi
is the total outflow of workers from industry i, Fj
is the total inflow to j and F is
the total flow of workers in the system. Next, we take the average of SRij and SRji to obtain
a symmetric measure. Finally, due to the asymmetric range of the measure ([0,∞)), we
normalize it between −1 and +1 (SR˜
ij =
SRij−1
SRij+1 ) (see Neffke, Otto, and Weyh 2017). As a result,
positive values of the final skill relatedness measure correspond to larger-than-expected
labor flows. Further details can be found in Section 2 of the Supplementary information.

3.3 Input-output relations

To assess the input-output similarity of industries, we rely on two different types of datasets.
First, we rely on data from the World Input-Output Database (WIOD). Using the inputoutput
table for Hungary (Timmer et al. 2015) for 2014, we obtain directed buyer-supplier
relations between two-digit industries.

Using WIOD tables makes our analysis comparable to previous studies, which have also
relied on aggregate input-output tables (Ellison, Glaeser, and Kerr 2010; Diodato, Neffke,
and O’Clery 2018). However, these country-level aggregates may hide much important detail.

Therefore, we use a second, micro-level dataset that records business transactions between
companies in Hungary. These data are derived from the value added tax (VAT) reports collected
by the National Tax and Customs Administration of Hungary. Firms are obligated to
declare all business transactions in Hungary if the VAT content of their operations exceeds
ca. 10,000 EUR in that year. The dataset is anonymized and available for research purposes
through the HUN-REN CERS Databank. It has been used to construct interfirm supplier
networks to study production processes, systemic risks and interdependencies between companies
at the national scale (Diem et al. 2022; L˝orincz, Juh´asz, and O. Szab´o 2024; Pichler
et al. 2023).

We aggregate firm-to-firm supplier transaction values between 2015 and 2017 to the level
of pairs of three-digit industries to derive a dataset that is similar in structure to the IO
tables in the WIOD data. However, we will also use the micro data themselves to analyze
colocation at the firm level.

To construct an indicator that captures the strength of value chain linkages between two
industries, we follow the same approach as for skill relatedness in eq. (5):

IOij =
Vij
(ViVj )/V (6)
where Vij stands for the total value of goods and services that industry i supplies to industry
j. Furthermore, omitted indices indicate summations over the corresponding dimensions.
As before, the ratio compares observed flows to expected flows. We once again symmetrize
the index, taking the average of IOij and IOji, and then use the same rescaling as for skill
relatedness to map all values between -1 and +1 resulting in ˜IOij .

We calculate this index at the two-digit level using WIOD data (IO (WIOD)) and at the
three-digit level using the aggregated transaction values from the VAT records (IO (transactions)).
Basic descriptive statistics for both measures are provided in Table 1. More detailed
statistics can be found in Section 2 of the Supplementary information.
Table 1: Descriptive statistics

Variable Mean Std. dev. Min Max
Coagglomeration (EGK) NUTS3 −0.001 0.077 −0.319 0.966
Coagglomeration (LC) NUTS3 0.031 0.282 −1.000 1.000
Coagglomeration (EGK) NUTS4 −0.001 0.017 −0.071 0.762
Coagglomeration (LC) NUTS4 0.029 0.119 −0.488 0.807
Labor (SR) −0.432 0.495 −1.000 0.999
IO (WIOD) −0.520 0.449 −1.000 0.857
IO (transactions) −0.691 0.447 −1.000 0.999
Note: Statistics for all variables are calculated from 35778 observations.

4 Results

4.1 Drivers of coagglomeration in Hungary

We start our analysis with a replication of the findings of Ellison, Glaeser, and Kerr (2010)
for Hungary. Following Diodato, Neffke, and O’Clery (2018), we focus on the labor pooling
and input-output channels. To assess the relative importance of either channel as a driver of
coagglomeration patterns, we estimate the following baseline equation, using Ordinary Least
Squares (OLS) regression:

ij + β2
˜IOij + ϵij (7)
where SR˜
ij and ˜IOij refer to the skill relatedness and input-output dependency measures

Coagglomerationij = β0 + β1SR˜

defined in sections 3.2 and 3.3. The dependent variable, Coagglomerationij , is either the
EGK or the LC coagglomeration index described in section 3.1.

Unlike Ellison, Glaeser, and Kerr (2010), who only consider manufacturing industries,
and Diodato, Neffke, and O’Clery (2018), who compare manufacturing and service industries,
our analysis includes all sectors of the economy. Moreover, we run our analysis twice, where
the coagglomeration of industries is either measured within NUTS3 regions or within NUTS4
regions. Our preferred specifications are those based on NUTS4 regions, where Budapest,
the capital of Hungary, is divided into 23 micro-regions.

Table 2 presents the OLS regression results. To facilitate the interpretation of the effect
sizes, we rescale all variables such that they are expressed in units of standard deviations.
This rescaling is applied to all subsequent analyses. Results are qualitatively in line with
those in Ellison, Glaeser, and Kerr (2010) and Diodato, Neffke, and O’Clery (2018): also in
Hungary, both Marshallian channels are significant drivers of coagglomeration. Moreover,
labor pooling seems to play a more important role than input-output connections. The
exception to this is when we measure coagglomeration using locational correlations and inputoutput
linkages are based on actual firm-to-firm transactions. In this case, labor pooling and
value chain connections contribute about equally to the coaglomeration patterns we observe.
Ellison, Glaeser, and Kerr (2010) raise the concern that coagglomeration patterns may not
only be a consequence of labor pooling and value chain linkages, but also cause these linkages
themselves. For instance, industries may use similar labor because they are colocated, not
vice versa. Similarly, industries may preferentially use inputs that are available nearby and
adjust their production technologies accordingly instead of value chain links causing firms
to coagglomerate.2 To address this, the authors instrument the different types of linkages
2As an example, Ellison, Glaeser, and Kerr (2010) point to the trade between shoe manufacturers and

Table 2: OLS multivariate regressions

Coagglomeration (EGK) Coagglomeration (LC)
NUTS3 NUTS4 NUTS3 NUTS4 NUTS3 NUTS4 NUTS3 NUTS4
(1) (2) (3) (4) (5) (6) (7) (8)
Labor (SR) 0.096∗∗∗ 0.061∗∗∗ 0.084∗∗∗ 0.057∗∗∗ 0.142∗∗∗ 0.175∗∗∗ 0.106∗∗∗ 0.126∗∗∗
(0.019) (0.012) (0.020) (0.012) (0.018) (0.024) (0.016) (0.020)
IO (WIOD) 0.056∗∗∗ 0.041∗∗∗ 0.064∗∗∗ 0.089∗∗∗
(0.018) (0.011) (0.021) (0.022)
IO (transactions) 0.050∗∗ 0.026∗ 0.112∗∗∗ 0.153∗∗∗
(0.025) (0.015) (0.018) (0.020)
Observations 35,778 35,778 35,778 35,778 35,778 35,778 35,778 35,778
R2 0.014 0.006 0.013 0.005 0.027 0.043 0.033 0.055
Adjusted R2 0.014 0.006 0.013 0.005 0.027 0.043 0.033 0.055

Note: Clustered (industryi and industryj ) standard errors in parentheses. Significance
codes: ***: p<0.01, **: p<0.05, *: p<0.1.

between industries with analogous quantities calculated from data for economies other than
the US.

Table 3: Labor channel through instrumental variable univariate regressions

Coagglomeration (EGK) Coagglomeration (LC)
NUTS3 NUTS4 NUTS3 NUTS4
(1) (2) (3) (4)
Labor (SR) 0.403∗∗∗ 0.285∗∗∗ 0.417∗∗∗ 0.575∗∗∗
(0.074) (0.045) (0.066) (0.083)
Observations 35,778 35,778 35,778 35,778
R2
-0.078 -0.043 -0.048 -0.114
Adjusted R2
-0.078 -0.043 -0.048 -0.114
KP F-statistic 115.955 115.955 115.955 115.955
Note: Clustered (industryi and industryj ) standard errors in parentheses. Significance
codes: ***: p<0.01, **: p<0.05, *: p<0.1.

In Tables 3 and 4, we follow the same identification strategy. To instrument our labor
market pooling variable, we construct a skill relatedness measure between three-digit industries
using data from the Swedish labor market. To instrument value chain linkages we
average all input-output tables in the WIOD data, excluding the Hungarian tables. Detailed

leather producers. The volume of this trade may reflect more than just the inherent technological features
of shoe manufacturing: shoes can be made out of several materials, including leather, but also plastics. The
choice of leather as an input to shoe-making may therefore be a consequence of an idiosyncratic historical
colocation of leather producers with shoe producers. Similarly, shoe manufacturers may have hired workers,
not only by their suitability for shoe-making, but also according to their availability on the the local labor
market. In the longer run, shoe makers may have adjusted their production processes to make better use of
these locally available workers. This would once again lead to some reverse causality between the linkages
between industries and their coagglomeration patterns.

description on the instruments can be found in Section 2 of the Supplementary information.
Our instruments are valid, as long as idiosyncratic patterns in the input-output and labor
dependencies outside Hungary are exogenous to coagglomeration patterns inside Hungary.
As in Ellison, Glaeser, and Kerr (2010), we run univariate analyses, testing for the causal
effect of each channel separately. Univariate OLS regressions for comparison are provided
in Section 3 of the Supplementary information, while in Section 4 we present the first and
second stages of instrumental variable estimations separately.

Table 4: Input-output channel through instrumental variable univariate regressions
Coagglomeration (EGK) Coagglomeration (LC)

NUTS3 NUTS4 NUTS3 NUTS4 NUTS3 NUTS4 NUTS3 NUTS4
(1) (2) (3) (4) (5) (6) (7) (8)
IO (WIOD) 0.083∗∗∗ 0.054∗∗∗ 0.083∗∗∗ 0.106∗∗∗
(0.020) (0.012) (0.023) (0.023)

IO (transactions) 0.475∗∗∗ 0.310∗∗∗ 0.479∗∗∗ 0.609∗∗∗
(0.129) (0.078) (0.128) (0.141)
Observations 35,778 35,778 35,778 35,778 35,778 35,778 35,778 35,778
R2 0.005 0.002 -0.146 -0.066 0.007 0.013 -0.081 -0.122
Adjusted R2 0.005 0.002 -0.146 -0.066 0.007 0.013 -0.081 -0.122
KP F-statistic 12000 12000 38.276 38.276 12000 12000 38.276 38.276

Note: Clustered (industryi and industryj ) standard errors in parentheses. Significance
codes: ***: p<0.01, **: p<0.05, *: p<0.1.

Our results corroborate the OLS analysis of Table 2: both channels have a large and
causal effect on coagglomeration patterns in Hungary. Moreover, the labor pooling channel
has a stronger causal effect than input-output relations, unless we measure the input-output
relations using micro-level transaction data. In the latter case, labor and value chains represent
about equally strong coagglomeration forces.

These results strengthen the external validity of the literature on coagglomeration, which
has mostly focused on the US economy. The generalizability of those results to Hungary is
not trivial: the Hungarian economy is much smaller than the US economy. This not only
affects the amount of spatial variation that is available for our estimations, but also the
degree to which firms can rely on domestic value chains. In the Supplementary information,
we show multiple robustness checks of these results.

In Section 5 of the Supplementary information we present results of using alternative
instruments for input-output connections such as US supply tables or the WIOD table for
the Czech Republic only. Section 6 of the Supplementary information presents the above
OLS and IV regressions separately for manufacturing and service industries. In Section 7,
we apply geographical restrictions and exclude firms located in Budapest from our sample.
Furthermore, we re-run our main models focusing only on firms with a single plant location.

Our main results are valid for all but a few of the listed specifications.
Finally, we also try estimating multivariate IV regressions, where both agglomeration
forces enter the regression simultaneously. However, the Kleibergen-Paap statistic for these
analyses indicates that these models typically suffer from weak instruments. That is, there
is insufficient variation available in our data to reliably disentangle the causal effects of labor
pooling and value chain linkages. Results of these models are reported in Section 8 of the
Supplementary information.

4.2 Interaction effects

We now turn to testing our main hypothesis that the role of value chain links in determining
the locations of industries depends on the degree to which industries are also skill related.
To do so, we interact the metrics for the two Marshallian channels in the following model:

Coagglomerationij = β˜
0 + β˜
1SR˜
ij + β˜
˜IOij + β˜
12 ˜IOijSR˜

ij + ηi + δj + ˜ϵij (8)

Because our instruments proved too weak to estimate multivariate models, these models
are estimated using OLS regressions. To nevertheless minimize confounding, we add two-way
industry fixed effects, denoted by ηi and δj
.

Table 5: OLS multivariate regressions with interaction effects

Coagglomeration (EGK) Coagglomeration (LC)
NUTS4 NUTS4 NUTS4 NUTS4 NUTS4 NUTS4 NUTS4 NUTS4
(1) (2) (3) (4) (5) (6) (7) (8)
Labor (SR) 0.059∗∗∗ 0.052∗∗∗ 0.057∗∗∗ 0.051∗∗∗ 0.173∗∗∗ 0.164∗∗∗ 0.126∗∗∗ 0.138∗∗∗
(0.012) (0.013) (0.011) (0.013) (0.024) (0.016) (0.020) (0.013)
IO (WIOD) 0.037∗∗∗ 0.059∗∗∗ 0.084∗∗∗ 0.057∗∗∗
(0.011) (0.018) (0.022) (0.020)
IO (WIOD)*Labor 0.023∗∗∗ 0.016∗∗ 0.034∗∗ 0.033∗∗∗
(0.008) (0.008) (0.015) (0.010)
IO (trans) 0.012 0.018∗ 0.119∗∗∗ 0.085∗∗∗
(0.017) (0.011) (0.021) (0.013)

IO (trans)*Labor 0.025∗∗∗ 0.019∗∗ 0.065∗∗∗ 0.051∗∗∗
(0.010) (0.009) (0.013) (0.008)
Two way FE No Yes No Yes No Yes No Yes
Observations 35,778 35,778 35,778 35,778 35,778 35,778 35,778 35,778
R2 0.007 0.072 0.006 0.072 0.045 0.317 0.060 0.325
Adjusted R2 0.007 0.058 0.006 0.058 0.045 0.307 0.060 0.315
Note: Clustered (industryi and industryj ) standard errors in parentheses. Significance
codes: ***: p<0.01, **: p<0.05, *: p<0.1.

Table 5 shows results for our preferred specification based on coagglomeration in NUTS4

regions. The interaction effects are positive in all specifications, corroborating our hypothesis
that labor pooling and value chain effects reinforce each other.

Figure 2: Reinforcing effect of input-output connections measured by IO (WIOD) and
labor flow on coagglomeration. (A) The influence of labor flow on Coagglomeration (EGK)
at different levels of IO (WIOD) connections. (B) The influence of IO (WIOD) connections
on Coagglomeration (EGK) at different levels of labor flow. (C) The influence of labor flow
on Coagglomeration (LC) at different levels of IO (WIOD) connections. (D) The influence
of IO (WIOD) connections on Coagglomeration (LC) at different levels of labor flow. (E),
(F), (G), (H) are based on the same settings as the upper row, but IO connections are
measured through the transaction data. Visualizations are based on Table 5 Model (1), (3),
(5) and (7). Green areas depict 95% confidence intervals.

Figure 2 visualizes the implied effects of labor pooling for different values of input-output
linkages in panels A, C, E and G. Along the vertical axis, these graphs plot the effect of
labor pooling on coagglomeration, β˜
1 +β˜
12 ˜IOij , for varying levels of value chain connections
between industries i and j,
˜IOij . Note that the range of the horizontal axis is limited to the
values that ˜IOij can theoretically attain. These panels show that labor pooling effects are
positive and significant at any level of value chain linkages.
This contrasts with the effect of value chain linkages, β˜
2 + β˜
12SR˜
ij , shown in panels
B, D, F and H. The value chain effect is in general positive, but drops to zero when skill
relatedness between industries equals -1, which happens in 35% of all industry combinations.
In other words, value chain partners only tend to significantly coagglomerate if they are not
completely unrelated in terms of the skills of their workforces.
These results hold regardless of whether we use the EGK or LC measures of coagglomeration
and whether we measure value chain linkages using WIOD data or derive them from

micro-level transaction data. In Section 9 of the Supplementary information, we show results
for various other regression specifications with the interaction term.

4.3 Firm-to-firm ties behind coagglomeration

Our data allow us to analyze not just the potential connections between industries that
have been commonly studied in the coagglomeration literature, but the actual connections
between firms. We can do so both in terms of transactions and of labor flows. This allows us
to create networks of firms that are connected either if they supply (or purchase) goods or
services, or if workers move from one firm to the other. To simplify the analysis, we consider
ties as undirected and unweighted in both networks.

Table 6 provides a general description of these networks for the period 2015-2017. Overall,
the input-output network has a lower number of connections, which may in part reflect VAT
reporting thresholds (Pichler et al. 2023). In addition, it is less transitive than the labor flow
network, which is consistent with previous findings that show that production networks have
fewer closed triangles than other social networks (Mattsson et al. 2021). When it comes to
geography, the descriptive statistics of Table 6 suggests that labor flows are more spatially
concentrated than transaction flows. While 48% of the observed labor flows between firms
take place within the same NUTS3 region, only 41% of the transaction linkages are intraregional.
Finally, overlapping connections, i.e., pairs of firms that exchange both workers
and goods or services are rare but highly concentrated geographically.

Table 6: Descriptive statistics of the labor flow and supplier networks

IO Labor IO and Labor
Firms connected 72445 115519 16719
Edges 194231 492818 14209
Average degree 5.362 8.534 1.700
Transitivity 0.013 0.027 0.048
Average distance of ties (km) 68 58 40

Share of edges inside NUTS3 41% 48% 63%
Share of edges inside NUTS4 14% 20% 41%
Share of edges inside Budapest 22% 21% 25%

Note: Edges are undirected and unweighted ties that represent any supply or labor exchange
between two companies.

In line with this, Figure 3A and B indicate the extent to which actual labor flows and
input-output connections happen within or across NUTS3 or NUTS4 regions, respectively.
It compares for each firm the number of cross-region (“external”) ties to the number of
within-region (“local”) ties the firm maintains, by expressing the difference between them

as a share of all ties the firm engages in. The majority of firms either exhibit exclusively
local or exclusively interregional ties. This is most visible for NUTS 3 regions, where there
is a balance between firms with only local and firms with only external ties. However,
what stands out at both spatial scales is that firms tend to have a more local orientation
when it comes to their labor flows compared to their transactions with other firms. At
more disaggregated level of NUTS4 regions, firms with completely external ties naturally
outweigh all other type of firms, as these regions are often part of larger labor markets and
agglomeration areas (T´oth 2014)3
.

Figure 3: Geography of firm-to-firm input-output (IO) and labor flow connections. (A)
Share of input-output and labor flow ties of firms inside their local NUTS3 region and (B)
inside their local NUTS4 region. (C) Probability of labor flow, input-output connections and
overlapping (labor and input-output) ties by distance. (D) Share of input-output connections
between firms in skill related (SR) and not skill related industries inside 25 kilometers.
The figures are based on the sample of firms we used to construct our aggregate measures.

Figure 3 further analyzes how interfirm ties decay with the distance between firms. Figure
3C plots the likelihood that two firms in Hungary are connected through labor flows,
transactions or both for different distance bins. In line with Bernard, Moxnes, and Saito
(2019), input-output connections are highly concentrated in space. However, labor flow
3Maps of both spatial divisions are provided in Section 1 of the Supplementary information)

connections are even more sensitive to distance. Within a distance of 10 kilometers, the
probability of a labor flow between two firms decreases faster than that of input-output
relationships.

The third line shows the likelihood that two firms are connected in both the labor and
the IO network. Note that the figure is plotted using logarithmic axes. Consequently, if
the probabilities of being connected in either network were independent, the resulting line
should equal the sum of the labor and the IO plots.4 The fact that the Overlap line lies far
above this sum means that firms that maintain one connection are disproportionally likely to
maintain the other connection as well. Moreover, in line with our finding that labor pooling
and value chain linkages reinforce each other’s impact on coagglomeration, the Overlap line
shows by far the steepest distance decay of all lines.

Finally, Figure 3D shows how the share of a firm’s transaction ties occur within a given
distance. Highlighting this share for distances for up to 25 km, it shows that firm-to-firm
transaction ties are more likely to be highly localized if firms belong to skill related industries
than if they don’t. Apparently, suppliers are more likely to colocate with their buyers
(or vice versa) if they operate in industries with high cognitive proximity. Section 10 of
the Supplementary information provides further visualizations on firm-to-firm connection
patterns.

5 Conclusion

Why, in a world of globalized supply chains, do supplier-buyer transactions still often take
place in close geographical proximity? We propose that this may happen when value chain
partners need to exchange not just goods, but also know-how. In that case, spatial proximity
facilitates the transfer and coordination of know-how along these value chains. We assess
the validity of this proposition using the empirical framework of coagglomeration. Industries
coagglomerate whenever their interactions are facilitated by spatial proximity. Consequently,
the mere fact that industries belong to the same value chain is insufficient reason for them
to coagglomerate. This changes when interactions between value chain partners embed large
quantities of tacit knowledge. In that case, value chain relations should reinforce the benefits
of colocation.

Knowledge exchange between industries is more likely to occur between industries that
are cognitively close to one another. Because of the pivotal role of human capital in firms’
competitive advantage, we expect that this cognitive proximity is particularly high between
In a log-transformation, multiplications become additions: log piopsr = log pio + log psr, where pio and
psr are the probabilities that two firms are connected through labor flows or transactions, respectively.

industries that exchange a lot of labor, i.e., that are skill related. We therefore expect that
value chain linkages lead to coagglomeration only if industries are also skill related.

We tested this hypothesis by studying the drivers of industrial coagglomeration in Hungary,
where detailed datasets from public registers allowed us to complement the traditional
coagglomeration framework with a detailed analysis of firm-to-firm networks that underpin
coagglomeration. In line with our hypothesis, we find a positive interaction effect between
the Marshallian agglomeration channels of labor pooling and input-output linkages. The
impact of input-output linkages on coagglomeration increases with the skill relatedness between
industries, that is, with the potential to redeploy human capital between them. In
fact, if industries only share a value chain connection but no skill relatedness link, we do not
find any statistically significant evidence that these industries tend to colocate.

This result contributes to the growing literature on coagglomeration in several ways.
First, whereas the coagglomeration literature has considered various sources of hetereogeneity,
it has so far not considered that different Marshallian agglomeration channels may reinforce
one another. Second, by replicating the empirical findings of Ellison, Glaeser, and Kerr
(2010), we show that many of the main findings in this and subsequent papers extend beyond
the US context. Specifically, using instrumental variables estimation, we replicate the causal
effects of input-output linkages and labor pooling on industrial coagglomeration in the small
and open economy of Hungary where, unlike in the US, many inputs need to be imported
(Halpern, Koren, and Szeidl 2015), which hinders the formation of long domestic supply
chains. Moreover, in line with Diodato, Neffke, and O’Clery (2018) and Steijn, Koster, and
Van Oort (2022), we find that the impact of the labor pooling excedes the impact of value
chain linkages.

Second, analyzing actual labor flows and transactions between firms, we show that distance
decays are particularly steep in supply-chain connections between firms in cognitively
proximate industries. This micro-level evidence lends further plausibility to existing findings
about aggregate coagglomeration patterns. Moreover, because coagglomeration patterns are

pivotal inputs in the construction of product and industry spaces, these findings may also
bear relevance on the literature on economic complexity. This literature argues that economic
development unfolds by the gradual accumulation of complementary capabilities in
places (Hidalgo 2021; Balland, Broekel, et al. 2022). As capabilities are notoriously difficult
to observe directly, the combinatorial potential of places (economic complexity) and capability
requirements of activities (activity complexity) are often inferred from the geographical
distribution of these activities. In this context, our findings suggest that important localized
capabilities reside in value chain interactions that embed tacit knowledge and that such
connections are important drivers of the place-activity matrix that underlies industry spaces

and complexity metrics.

Finally, our findings connect to the literature on regional clusters. They highlight that
although value chain connections in a cluster may contribute to the competitiveness of clusters,
whether they do so will crucially depend on the extent to which these value chain
interactions are enriched with knowledge transfers, possibly facilitated by the exchange of
skilled labor.

Our study also has several limitations. First, while Hungary represents a novel test
case with detailed information on the drivers of industrial coagglomeration, the country
is also strongly dependent on exports and imports. Such dependencies are presently not
covered in our data and adding export and import data would be a valuable extension of
the current work. In addition, foreign direct investment (FDI) and multinational enterprises
(MNEs) play an important role in the Hungarian economy. Moreover, this foreign-owned
part of the economy may behave very differently from the domestic economy (B´ek´es, Kleinert,
and Toubal 2009; Halpern, Koren, and Szeidl 2015; Elekes, Boschma, and Lengyel 2019),
because these firms can access resources in other locations through their internal corporate
networks. Distinguishing between coagglomeration patterns of foreign-owned and domestic
firms therefore represents a promising avenue for future research. This would connect the
research on coagglomeration forces to a well-established literature on knowledge spillovers
from MNEs to their host regions, which are often mediated through value chains linkages.

Second, there are only a few years in which all official registers are available. This precluded
analyzing changes in coagglomeration forces over time. In particular, we could not
assess whether the stronger colocation of value chain interactions among cognitively proximate
partners is a new phenomenon, or has persisted over time. Because the coagglomeration
literature has pointed to an increased importance of labor pooling and knowledge-sharing
channels (Diodato, Neffke, and O’Clery 2018; Steijn, Koster, and Van Oort 2022), the shift
in modern economies towards services may increase the share of input-output linkages that
embed substantial tacit knowledge.

Third, the spatial units used in this paper, NUTS3 and NUTS4 regions, do not necessarily
represent the most adequate spatial scales for all industries and all interactions. Future
research could therefore use the exact geolocations of firms to construct coagglomeration
patterns directly from the microgeography of firms.

Notwithstanding these limitations and open questions, we believe that our analysis advances
our understanding of why industries coagglomerate, drawing attention to the importance
of knowledge linkages along the value chain.

Acknowledgement

S´andor Juh´asz’s work was supported by the European Union’s Marie Sk lodowska-Curie
Postdoctoral Fellowship Program (SUPPED, grant number 101062606). Zolt´an Elekes and
Vir´ag Ily´es were supported by the Hungarian Scientific Research Fund project ”Structure
and robustness of regional supplier networks” (Grant No. OTKA FK-143064). Frank Neffke
acknowledges financial support from the Austrian Research Agency (FFG), project #873927
(ESSENCSE). The authors would like to thank the Databank of HUN-REN Centre for
Economic and Regional Studies for their support. This research paper is based on the valueadded
tax return data files of the Hungarian Central Statistical Office. The calculations
and conclusions drawn from them are the sole intellectual property of the authors. The
authors are grateful for the feedback of Mercedes Delgado, Max Nathan, Neave O’Clery,
Cesar Hidalgo, Andrea Caragliu, Johannes Wachs and L´aszl´o Czaller.
