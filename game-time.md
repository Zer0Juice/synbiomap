

this outline is intentionally casual and irreverent. the goal is to communicate soul, emotion, and overall structure around which a more polished exterior can be built

approximately 5-600 words per page.

Assume 10 figures, each taking up around 200 words per page. That leaves us with approximately 40,000 words to write.

use the WRITING-RULES when generating ALL TEXT.

aim for a paragraph length of 100-250 words

aim for 40k words, 130-200 paragraphs

The word counts and paragraph counts are guidelines, not rules. This just provides a relatively fine-grained structure to conform to

# Sections

## Statement on AI Use
1 page
3 paragraphs
around 600 words
1. AI assisted in literature search, data processing, language embeddings, coding, brainstorming, reviewing, and drafting. Claude Code was the main tool used for this. The entire project lives in a public Github repo that was regularly auto-committed by claude, so clear documentation exists at every stage of the process.
2. I aim to be as transparent as possible, to challenge the stigma against use of artificial intelligence in academia.
3. My most useful markdown files for ideation, such as the one for /discussion and /frankGPT, are available in the appendix.
## Introduction
**what we did**
5 pages
12 paragraphs
Around 3k words
1. We messed up the planet and should fix it
2. But our impact proves that we can have an impact on the biosphere
3. Our biology used to be descriptive, now it's synthetic
4. We can engineer something to save us
5. How does knowledge develop in this sphere? Does it spill over locally? are certain places better positioned for certain technologies?
6. This is important for economics and public policy
7. We must study research to make the right decisions
8. SynBio is hard to study
9. iGEM is a thing and we study it
10. We explore the research landscape of synbio in semantic space
11. different artifacts in the same city are related
12. everythings connected, governments should invest in education to prevent climate armageddon
## Background
**why it matters**
20 pages
48 paragraphs
13k words

1. Public policy and innovation background
2. research is important and linked to industry. cite doblinger and innovation studies
3. governments should be innovation partners
4. it's hard to communicate with them and measure emergent fields
5. but emerging fields are where innovation happens
6. academic research is where innovation happens - bring in neffke and co
7. economic geography has the answers
8. is innovation geographically influenced?
9. its important to empirically measure these things
10. measure them in cities. cities are agglomerations of factors that lead to innovation. its a good functional unit
11. SynBio is popping off and changing rapidly as compute and dna synthesis gets cheaper 
12. could end the world, could save it. so many possibilities. should be understood and studied
13. we should study patents
14. we should study papers
15. we should study... student igem projects
16. in fact let's look at one now. here's igem Uppsala 2009!
17. wow look at all they did afterwards. startups? academic careers? publications based on igem work?
18. biobricks are the shit. look at one of Uppsala's little dna sequences how cute
19. and wow look what happens when you ferment with algae at scale
20. history of OG climate disaster mass extinction caused by algae
21. brief history of algae fermentation technology
22. modern cyanobacteria carbon capture companies
23. startups emerging from igem
24. papers emerging from igem
25. look what's possible 
26. open science is the best
27. we must study these kids in the lab
28. its a gap in the literature but our boy marc santolini been busy working on em
29. such a rich dataset! team science? insight into the precious process of innovation? career trajectories? Possibilities are endless!
30. but how do we draw links between different artifact types?
31. introducing relatedness featuring all the ways to measure relatedness in economic geography
32. and some of the fun things they do with relatedness
33. but all the ways we just said suck for our use case
34. keyword co-occurence is closest but it's boring and limited
35. citation networks are cool but not as useful with limited cross-document links
36. semantic space: a history OG linguist roots
37. Information science developed along the way with latent semantic analysis
38. useful for search algorithms
39. googley word2vec background
40. machine learning is magical
41. what do the weights mean? nobody knows but it still works
42. we surf the waves of the semantic sea uncovering meaning and citations
43. semantic embeddings are amazing
44. SPECTER2 especially
45. but specter2 was trained only on academic document embeddings! will it work across different artifact types
46. precedent for cross-domain embedding space
47. good thing specter2 lets us fine-tune our own adapters
48. now all we need is that data...
## Data
**how we did it**
20 pages
30 paragraphs
12k words

1. we gather a hoard of data
2. patents straight from Oldham
3. then we process them using USPTO API
4. decided to use only USPTO data due to simpler geocoding
5. geocoding based on either first author or fractionally. acknowledge the limitation. show others have been here in the literature
6. we started data acquisition from lens.org but it got noisy and ultimately decided to go with oldham's pre-cleaned and publicly available dataset
7. address some of oldham's challenges with building a synbio patent dataset
8. go over a few different methods for sourcing literature for synbio / biotech
9. papers sourced straight from OpenAlex, which is wonderful because of the commitment to open science and easy access, geocoding etc
10. tried several strategies for search parameters. keywords, citation expansion, etc. Stuck with a keyword search criteria, citation expansion introduced too much noise
11. iGEM project data harvested directly from their API
12. light web crawling for abstracts
13. geocoding them was a pain
14. web crawling for DOIs; wasn't perfect, but got plenty of links that show igem projects citing the literature. did not include all the articles in the corpus; same issue with citation expansion as before.
15. downloaded the parts registry too
16. many parts were linked to source DOIs
17. some papers cite parts! did full text searches on pubmedcentral for biobrick part ID strings. some limitations to this process but created some edges
18. added those papers to the openalex corpus
19. patent-paper-pair edges from matt marx, incomplete and did not reproduce full PPP code due to time constraints, but added some edges to the training data.
20. linking them all together like a schizophrenic with a ball of string
21. fine-tuning specter2 adapter with all the links we drew
22. our adapter outperforms the baseline
23. Embedded all the docs, now they all live in semantic space together
24. UMAP reduction
25. Projection into a pretty map (with graphic)
26. HDBscan clustering
27. Cluster labeling - man and machine
28. pretty map 2 feat. cluster labels & tables
29. bring it back to carbon capture with clusters 7, 8, and 62
30. world map showing cities working on carbon capture
## Results
**what it means**
20 pages. Figures and interpretation. Includes math equations and explanations so more figures
20 paragraphs
10k words

1. we got the data all warmed up now we gonna get in there and get dirty with it
2. we think centroids / vector averages could be a good measure
3. psych. robustness check knocked it flat. city size is a cold bastard.
4. what will we do? was this all for nothing? no. we are strong. we will rise up. we will use the clusters!
5. we count the topics in each city. if cities share topics they're related
6. revealed co-occurence through semantic space
7. we built it up, now let's try and knock it down
8. dropping countries. what happens? still strong
9. change the number of topics. does kmeans knock it flat? no we good
10. Number of cities? nah we stay winning
11. OLS with a table to show we're doing *metrics*
12. DiD on time period and city because its interpretable as shit
13. the dark horse weird validation: parts data class co-occurence space comparison
14. mendel test background
15. graph showing it and interpretation
16. perm test, still good
17. which cities are central to carbon capture?
18. build a network from all those training data links. pretty network graph.
19. centrality measure
20. Table listing top cities in the fermentation and cyanobacteria clusters
## Conclusion
**bring it home**
5 pages
12 paragraphs
3k words

1. Recap a bit. It's been a long ride
2. iGEM got the sauce, and spreads it around the world
3. in cities, patents are related to papers, and papers are related to projects, but patents aren't all that related to projects
4. the data supports the narrative of student projects being embedded in the local research scene
5. we are not making any causal claims!
6. but they could form the basis for an interesting follow-up
7. in fact, we could follow up the project in a number of ways. this thesis was limited by time constraints
8. the fine-tuned semantic embeddings could be used as the basis for an app doing semantic search on synthetic biology artifacts. patents, papers, projects, and parts
9. Uppsala and Auckland are the places to go if you want to do cyanobacteria fermentation
10. many patents have digitized genetic data available! lens.org has a service that works with it; unfortunately it was out of our budget. You could look for biobrick sequences data in patents, or embed the patent abstracts in one space and the sequences in another (using the BLAST model or something similar), to see if the spaces are related.
11. These ecosystems are all deeply intertwined. governments should fund academic research. student igem projects are important and may be an early signal on research coming out of their city.
12. With the dizzying rate of technological advancement, with everything from human creativity to life itself automated and manipulable, it'll be a brave new world out there. These technologies hold enormous potential for harm or help depending on how they are utilized. Science fiction has become science fact, and the future itself is on the line. It's up to us to be a part of whatever future we'd like to live in.