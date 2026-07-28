# Final presentation — 12-slide arc

Audience: Frank Neffke (economic geography) and Claudia Doblinger (innovation / clean-tech).
Format: 20 min talk + 10 min Q&A. Present the whole project, but weight toward findings/implications.
Deck lives in `website/slides.qmd` (Quarto reveal.js). Numbers come from notebook 2
(`notebooks/02_tripartite_city_analysis.py`). Setup = slides 1–4; findings/implications = slides 5–12.

1. Motivation & the question *(one slide)*
	* Climate: we are warming the planet and want tools to draw carbon back down
	* Biology moved from *reading* life to *writing* it — synthetic biology
	* Carbon capture is the running example (engineer microbes to fix CO2)
	* iGEM: an open, geotagged record of students entering the field
	* Synbio is hard to study, and a few regions seem to dominate
	* **Question: do a city's students, academics, and inventors work on the same things?**
	* We test semantic relatedness and co-location, *not* causation
2. Building the corpus (data)
	* Projects from iGEM teams (wikis + registry)
	* Papers from OpenAlex
	* Patents from the Oldham USPTO set — geocoded to inventor cities (Breschi & Lissoni 2001)
	* Parts from the iGEM BioBrick Registry (~89k)
	* Shared schema, all geocoded to a city
	* Corpus: **17,826 docs = 10,319 papers + 4,606 projects + 2,901 patents**
3. Semantic embeddings + fine-tuning
	* SPECTER2 turns each title/abstract into 768 numbers; similar work lands nearby
	* Measures relatedness by cosine distance
	* Fine-tuned on ~100k cross-type citation links (wiki DOIs, patent–paper pairs)
	* One shared space for all three artifact types
	* (baseline-vs-fine-tuned improvement → backup; result survives on base SPECTER2)
4. The map of the field
	* One shared UMAP projection of all 17,826 docs
	* 80 HDBSCAN topics (30% left as noise); labels drafted by an LLM, edited by hand
	* Papers spread across the whole field; projects and patents each gather in their own regions;
	  papers overlap both
5. The measure that failed (centroid)
	* Average each city's projects and papers into two vectors, take the cosine → ≈0.95 everywhere
	* But it correlates **r = 0.71 with city size** (~50% of the variance)
	* It measures *how much* a city publishes, not *what* — keep as a yardstick, build a better test
6. The measure that works (shared topics)
	* Represent each city as a profile over the 80 topics, scaled to length one
	* `overlap = sum over topics of (paper share in topic) x (project share in topic)`
	* Large when the two types weight the same topics, small when they don't; city size drops out
	* Test against a **within-country permutation null**: shuffle which city pairs with which, holding
	  size and topic popularity fixed. p = share of shuffles that match/beat the observed overlap
7. Headline result — papers are the hub

	| link             | cities | cosine excess | p      | same-topic lift | beats null? |
	| ---------------- | ------ | ------------- | ------ | --------------- | ----------- |
	| paper × project  | 120    | +0.0102       | 0.0065 | 1.30x (p 0.016) | yes         |
	| paper × patent   | 44     | +0.0347       | 0.0065 | 1.27x (p 0.020) | yes         |
	| project × patent | 28     | +0.0043       | 0.227  | 0.99x (p 0.464) | no          |

	* A city's papers share topics with both its projects and its patents
	* The direct project–patent link is not detected once country and size are held fixed
	* **The local science a city publishes is the common ground its students and its inventors both
	  build on** (papers are the hub; projects and inventors meet through the local science)
8. Trying to break it (robustness)
	* Drop a whole country — paper×patent survives dropping the US (≈ p 0.001); **paper×project leans
	  on the US and China, softens to p 0.069 without the US** (state this honestly)
	* Change the number of topics (k = 10–120) — both paper links stay significant, project×patent never
	* Starve the sample — squeeze a working link to 28 cities and it often reads non-significant, so
	  project×patent is **undetected, not shown absent** (a power problem)
	* Survives on base SPECTER2 — fine-tuning sharpens, it does not invent the signal
9. The parts agree (Mantel)
	* Build a city-by-city distance matrix from the mix of BioBrick part classes
	* Compare it to the semantic topic-distance matrix
	* Mantel r = 0.127, p = 0.0005, 164 cities
	* Part classes are functional DNA labels the model never read — a second, independent window seeing
	  the same shape. The strongest single piece of evidence the relatedness is real
10. A dynamic trace (DiD)
	* Difference-in-differences within a city and topic, after differencing out each city's baseline and
	  each topic's global trend
	* Paper → patent: β = +0.355, p = 0.028 (N = 44) — academic output co-moves with later same-topic
	  patenting
	* Project → paper: significant in the larger bipartite sample, underpowered in the tripartite one
	* Frame as **co-movement, not identified causation** (lead-lag "projects lead ~3 yrs" → backup)
11. Case study: carbon capture
	* Three adjacent clusters trace the ladder: cyanobacterial metabolic engineering (projects) →
	  cyanobacterial chassis development (papers) → industrial fermentation (patents)
	* Leaderboard: Auckland, Uppsala, Daejeon, San Diego, Gainesville
	* Alignment inside the subfield is about as strong as field-wide
12. What it shows, what it can't — and implications
	* Establishes real, size-independent local relatedness (project–paper, paper–patent), robust to
	  country / cluster count / model, anchored in physical parts
	* Does **not** establish causation — the three share local causes (same universities, mentors, funders)
	* Policy: where students cluster is a signal of where a field is putting down roots; funding student
	  science and open tools is an early investment. Phrase as "consistent with," never "proves"
	* Next: deeper patent retrieval, patent distribution by DNA sequence, causal analysis

Closer (title-style): thank you + links (website, GitHub, PDF on Paper page), advisor credits.

## Backup slides
1. Lead-lag profile + permutation (projects lead papers ~3 yrs; a null at tripartite sample size)
2. Baseline vs fine-tuned SPECTER2 comparison
3. Embedding-model history / why SPECTER2
4. Worked iGEM example — Uppsala 2009 *Booze Bugs* → 2014 paper citing its own BioBrick
5. The co-membership test re-run as a same-city OLS regression (forest plot) for Neffke
