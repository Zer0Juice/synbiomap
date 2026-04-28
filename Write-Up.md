Purpose: Organizing thoughts into a coherent draft of the research paper that will be our final deliverable.

How to use:  Do not write in this document, this is solely a space for human-written text. Refer to this document for the goals, purpose, vision, and focus of the project. This is a human-written rough draft that sums up my current level of understanding and where I'm at in the project. Use to understand the direction we're taking the project in, and my own limitations of understanding.

---

# Title: Patents, Papers, Parts, and Planet

Subtitle: Mapping the Innovation Network of Synthetic Biology
Advisors:
	Frank Neffke, Complexity Science Hub
	Claudia Doblinger, Technical University of Munich
## Introduction

Synthetic Biology is an exciting new emergent domain that uses standardized tools to engineer biological systems. Cells are treated like little computers running chunks of genetic code. This code is stored as amino acid in systematized online repositories, cheaply synthesized into real DNA, and introduced into cells. This field is rapidly developing through research happening all over the world, but innovation is not evenly distributed; it seems to cluster in specific regions. There are a lot of potential reasons for this; universities with access to fancy lab equipment and students, venture capital available for startups, existing adjacent industries (like pharma) that already have the infrastructure available for research, favorable regulatory landscapes. We already know that cities tend to specialize in specific technologies, and branch off into adjacent technologies over time, so it stands to reason that different cities will develop capabilities and specialize in different applications and research areas of synthetic biology. For example, a city with a lot of capabilites in producing software might have an easier time developing software tools. A city with a lot of agricultural capability might be better at scaling up plant modifications. A city with a big university where a lot of theoretical research happens could develop enhanced capabilities in producing foundational, theoretical innovations that require a certain knowledge base, and so on and so forth.

However, although these capabilities are vital to the future industrial mix of the city, they can be difficult to measure and compare quantitatively. “Capability” and “innovation” are abstract concepts, and we have to use quantifiable outputs if we hope to understand them empirically at scale. Different artifacts can reflect the creation of new knowledge in unique ways, while pointing to overlapping underlying regional capabilities. For example, an academic research paper and a patent are two different reflections of innovation with different goals. A patent shows that commercial research is occurring, and that the innovators believe an idea has value to industry. An academic paper is the fruit of scholarly research, and the authors benefit off of its publication based on how much it impacts a scientific field. An academic breakthrough could have minimal commercial use and vice versa.

Synthetic Biology is especially interesting because it introduces a novel artifact unique to the field: the iGEM project. The International Genetic Engineering Machine, or iGEM, is a student competition in synthetic biology, a sort of lego robots competition for genetic engineering. Students work together in teams, over the course of a year, to produce an innovative project using the tools of synbio. They all share a basic tool kit of genetic parts, a list of rules and guidelines, and a basic program structure, but the teams are generally left up to their own devices to craft a project that will be entered into this worldwide competition. The result is something like an academic research paper presented at a conference, crossed with a startup in an accelerator. This competition is a major launching points for student’s careers in synthetic biology, and sets standards and norms that have tremendous impact in the industry.

Part of these norms is a dedication to principles of open science, extensive documentation, and the maintenance of a standardized open repository of genetic parts built using the “biobricks” standard to be interoperable pieces of genetic circuits. The biobricks standard was created by Tom Knight of MIT, and as the repository and competition continues to grow, establishes a fascinating, well-documented database of the industry growing over time. Basic parts are often directly based on existing academic research, and composite parts are build by combining existing parts in the registry. These parts are classed into various functions in genetic circuits (such as regulating the expression of a gene or reporting a signal for an observer to read and quantify). As each iGEM project produces a stack of new parts and makes use of existing ones, this produces a fascinating and rich knowledge graph that shows how these research projects are connected, while also providing links to academic literature.

iGEM is a global, integrated, open knowledge base, but that doesn’t mean that regional capabilities don’t show up. Generally, teams are hosted by universities, and draw from a pool of advisors in their faculty or local community. This could mean that iGEM research has a high degree of relatedness to existing academic research going on at a city and university level.

However, this conclusion is nontrivial, because the teams are operating under a different incentive structure, and with a different knowledge base, than an academic research group. Some teams are a result of collaborations between multiple institutions or research groups in a city; for example, the Munich team is a collaboration between TUM and LMU students. Some teams have strong existing networks of collaboration between other teams, with students competing multiple years in a row and establishing long-term cooperative bonds. Team collaboration is outside the focus of this inquiry but has been studied more in depth by Marc Santolini’s research group at the learning planet institute in Paris.

An overarching goal of the iGEM organization in maintaining a registry of open-source tools and standards for synthetic biology. The impact of the organization extends far beyond the boundaries of the organized competition; alumni have gone on to form 

We want to understand if regional specialization in igem research is correlated with regional specialization in academic research and patents. 

## Background

Boschma et al (2014) studied the impact of scientific relatedness on knowledge dynamics in biotechnology at the city level. This analysis provides a clean methodological base to build from.

Santolini et al (2023) presents the iGEM data as a well-structured dataset for studying team dynamics and innovation.

More background literature that forms a methodological basis for comparing patents, papers, and project abstracts across the same embedding space would be very useful, as would anything linking patents, papers, and genetic code.
## Case Study: Carbon Capture

To better understand this space, it could be helpful to focus on a specific example. We will do a deep-dive into one iGEM project, looking at its biobricks, the literature that those biobricks cite, the literature that cites them, and the patents that contain their genetic sequences.
## Data

### iGEM Projects data
built from https://teams.igem.org/
Teams were geocoded in a few different ways. First by directly passing the institutions to OpenAlex API for exact, very accurate locations, then by extracting their city from their home country, institution, and team name using Haiku API and geocoding with nominatim.
### iGEM Parts Data
Built from https://registry.igem.org/
55% of parts are associated with an academic publication as a "source". Generally these are parts based on that publication, translated into the biobrick format.

Including cited paprs in the corpus? Concerns of p-hacking?

x% of biobricks are "composite parts", which means their code includes one or more basic parts, resulting in a citation network between parts.

Parts are all linked to the iGEM projects that originated them. iGEM projects can be treated as bundles of parts which cite papers and other projects.

Thus, we have a multilayer network where projects are connected to each other, and to papers.

### Papers Data
Built from https://openalex.org/

Papers citing igem projects? Papers using biobricks? Which would be easier to measure?
### Patent Data
Uses USPTO patent dataset

Matt Marx papers-patent pairs code leads to citation-style links between patents and papers.

## Methods

To do this we need some way to identify topics in patents, papers, projects, and parts, to make meaningful comparisons across these different artifacts with disparate documentation, language, and underlying causes. We’re taking advantage of the fact that patents, papers, and projects all have abstracts and titles, written using the nomenclature of synthetic biology. We make use of a bidirectional language encoding model called SPECTER2 to generate embeddings of these in high-dimensional space.

Then we project the embeddings onto a lower dimensional space so they can be clustered. 60 dimensions or so. Once the clusters are identified, they're labeled by running the 10 abstracts closest to the cluster of each centroid through an LLM (Claude Haiku API), to understand what they have in common and label the clusters.

We also collect the papers cited by the iGEM biobrick registry; including these papers connects the corpus of literature to the network in a unique way. This pulls papers concerned with the methods actually used by synbio practitioners, deliberately curated by the igemers, and offering a unique link to the biobrick corpus.

The methods section will be organized across three escalating claims of increasingly general nature.
1. The semantic embedding approach is internally valid. Projects cluster close to the papers they cite
2. iGEM projects and papers co-specialize in cities with sufficient data depth
3. iGEM activity precedes or accompanies publication and patent activity. The temporal analysis is meant to be exploratory, not to make causal claims.

### Parts
We downloaded the entire dataset of ~90,000 biobricks from the iGEM registry API, and matched them to the teams that originated them.
### Patents
We ran a few BLAST searches on patent sequence data using Lens.org's PatSeq tool, but rate limits prevented us from executing this at scale. However, this would be a fascinating project with the right resources. Tracing the pathways of individual sequences of genetic code through the knowledge space.

## Findings

The most compelling part of this data collection so far may be the papers referencing biobricks. Even though there isn't a standard for citing open-source genetic parts registries in the literature, and even with the limitations of full-text search, there were still 671 papers collected that directly cite biobricks in the registry, from PubMedCentral alone. This represents but a small fraction of their true impact, as it only returns papers that:
1. Open access
2. indexed by pubmedcentral
3. Use a full biobrick ID in their text



## Limitations
As this is a Master's thesis with limited budget and a fixed time constraint, the depth of analysis and breadth of the data used has some room for further development. For instance, it would be quite interesting to be able to search the sequences of academic research projects and patents. Datasets such as Lens.org PatSeq make this data available, but acquiring it was outside the scope and budget of this project, so patents are instead connected by their abstract's semantic similarity to clusters. 

The model used for embedding, SPECTER2 developed by the AllenAI institute, is also not trained on data for patents or student iGEM projects. It was trained on a corpus of academic publication abstracts and titles to predict whether two papers were related by a citation.

We are assuming that the artifacts are similar enough that their linguistic embeddings in SPECTER2 can be meaningfully compared.

Searching full-text papers for biobrick IDs was challenging for practical reasons; BBa_xxx strings all contain underscores, which do not play nicely with the search algorithms


## Open Questions
* Are publications by iGEM teams related to the papers published in their same 

* Do cities produce iGEM research related to their academic publications?

* Do iGEM research projects draw on local academic knowledge?