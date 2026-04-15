Purpose: Organizing thoughts into a coherent draft of the research paper that will be our final deliverable.

How to use:  Do not write in this document, this is solely a space for human-written text. Refer to this document for the goals, purpose, vision, and focus of the project. This is a human-written rough draft that sums up my current level of understanding and where I'm at in the project. Use to understand the direction we're taking the project in, and my own limitations of understanding

---

# Title: Patents, Papers, Parts, and Planet

Subtitle: Mapping the Innovation Network of Synthetic Biology
## Introduction

Synthetic Biology is an exciting new emergent domain that uses standardized tools to engineer biological systems. Cells are treated like little computers running chunks of genetic code. This code is stored as amino acid in systematized online repositories, cheaply synthesized into real DNA, and introduced into cells. This field is rapidly developing through research happening all over the world, but innovation is not evenly distributed; it seems to cluster in specific regions. There are a lot of potential reasons for this; universities with access to fancy lab equipment and students, venture capital available for startups, existing adjacent industries (like pharma) that already have the infrastructure available for research, favorable regulatory landscapes. We already know that cities tend to specialize in specific technologies, and branch off into adjacent technologies over time, so it stands to reason that different cities will develop capabilities and specialize in different applications and research areas of synthetic biology. For example, a city with a lot of capabilites in producing software might have an easier time developing software tools. A city with a lot of agricultural capability might be better at scaling up plant modifications. A city with a big university where a lot of theoretical research happens could develop enhanced capabilities in producing foundational, theoretical innovations that require a certain knowledge base, and so on and so forth.

However, although these capabilities are vital to the future industrial mix of the city, they can be difficult to measure and compare quantitatively. “Capability” and “innovation” are abstract concepts, and we have to use quantifiable outputs if we hope to understand them empirically at scale. Different artifacts can reflect the creation of new knowledge in unique ways, while pointing to overlapping underlying regional capabilities. For example, an academic research paper and a patent are two different reflections of innovation with different goals. A patent shows that commercial research is occurring, and that the innovators believe an idea has value to industry. An academic paper is the fruit of scholarly research, and the authors benefit off of its publication based on how much it impacts a scientific field. An academic breakthrough could have minimal commercial use and vice versa.

Synthetic Biology is especially interesting because it introduces a novel artifact unique to the field: the iGEM project. The International Genetic Engineering Machine, or iGEM, is a student competition in synthetic biology, a sort of lego robots competition for genetic engineering. Students work together in teams, over the course of a year, to produce an innovative project using the tools of synbio. They all share a basic tool kit of genetic parts, a list of rules and guidelines, and a basic program structure, but the teams are generally left up to their own devices to craft a project that will be entered into this worldwide competition. The result is something like an academic research paper presented at a conference, crossed with a startup in an accelerator. This competition is a major launching points for student’s careers in synthetic biology, and sets standards and norms that have tremendous impact in the industry.

Part of these norms is a dedication to principles of open science, extensive documentation, and the maintenance of a standardized open repository of genetic parts built using the “biobricks” standard to be interoperable pieces of genetic circuits. The biobricks standard was created by Tom Knight of MIT, and as the repository and competition continues to grow, establishes a fascinating, well-documented database of the industry growing over time. Basic parts are often directly based on existing academic research, and composite parts are build by combining existing parts in the registry. These parts are classed into various functions in genetic circuits (such as regulating the expression of a gene or reporting a signal for an observer to read and quantify). As each iGEM project produces a stack of new parts and makes use of existing ones, this produces a fascinating and rich knowledge graph that shows how these research projects are connected, while also providing links to academic literature.

iGEM is a global, integrated, open knowledge base, but that doesn’t mean that regional capabilities don’t show up. Generally, teams are hosted by universities, and draw from a pool of advisors in their faculty or local community. This could mean that iGEM research has a high degree of relatedness to existing academic research going on at a city and university level.

However, this conclusion is nontrivial, because the teams are operating under a different incentive structure, and with a different knowledge base, than an academic research group. Some teams are a result of collaborations between multiple institutions or research groups in a city; for example, the Munich team is a collaboration between TUM and LMU students. Some teams have strong existing networks of collaboration between other teams, with students competing multiple years in a row and establishing long-term cooperative bonds. Team collaboration is outside the focus of this inquiry but has been studied more in depth by Marc Santolini’s research group at the learning planet institute in Paris.

We want to understand if regional specialization in igem research is correlated with regional specialization in academic research and patents. 

## Case Study: Carbon Capture

To better understand this space, we focus on a very specific example: carbon capture projects.
## Data

### iGEM Projects data
built from https://teams.igem.org/
Teams were geocoded in a few different ways. First by directly passing the institutions to OpenAlex API for exact, very accurate locations, then by extracting their city from their home country, institution, and team name using Haiku API and geocoding with nominatim.
### iGEM Parts Data
Built from https://registry.igem.org/

### Papers Data
Built from https://openalex.org/

### Patent Data
Uses USPTO patent dataset


## Methods

To do this we need some way to identify topics in patents, papers, projects, and parts, to make meaningful comparisons across these different artifacts with disparate documentation, language, and underlying causes. We’re taking advantage of the fact that patents, papers, and projects all have abstracts and titles, written using the nomenclature of synthetic biology. We make use of a bidirectional language encoding model called SPECTER2 to generate embeddings of these in high-dimensional space.

Then we project the embeddings onto a lower dimensional space so they can be clustered. 60 dimensions or so. Once the clusters are identified, they're labeled by running the 10 abstracts closest to the cluster of each centroid through an LLM (Claude Haiku), to understand what they have in common and label the clusters.

We need to take the papers data
## Limitations
As this is a Master's thesis with limited budget and a fixed time constraint, the depth of analysis and breadth of the data used has some room for further development. For instance, it would be quite interesting to be able to search the sequences of academic research projects and patents. Datasets such as Lens.org PatSeq make this data available, but acquiring it was outside the scope and budget of this project, so patents are instead connected by their abstract's semantic similarity to clusters. 

The model used for embedding, SPECTER2 developed by the AllenAI institute, is also not trained on 

## Open Questions
* Are publications by iGEM teams related to the papers published in their same 

* Do cities produce iGEM research related to their academic publications?

* Do iGEM research projects draw on local academic knowledge?