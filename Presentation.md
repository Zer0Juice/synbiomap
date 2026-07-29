
1. Motivation
	* Climate problem
	* Biology -> synbio
	* Carbon Capture
	* Synbio hard to study, certain regions seem to be dominating
	* iGEM projects
2. Question
	* Are iGEM projects embedded in local research?
3. Data Collected
	* Projects from iGEM Teams
	* Papers from OpenAlex
	* Patents from Oldham + USPTO
	* Parts from iGEM Registry
	* Geocoded all
4. Semantic Embeddings
	* Technique for comparing meaning in text
	* Artifacts turned into vectors
	* Measures Relatedness
	* Fine-tuning SPECTER2
	* Links for training data
		* projects cite papers (web crawl)
		* papers cite parts
		* parts cite papers
		* papers connect to patents
	* figure showing improvement over baseline
5. Embedding Space Figure
6. Centroid Measure
7. Topic Clustering
	* UMAP Reduce to 60 dimensions
	* Clustering - Labels done by LLM with human edits
8. Calculating relatedness
	* `overlap (papers x projects) = sum over topics of (paper share in topic) x (project share in topic)`
	* Large when topics overlap, small when they don't
	* Robustness OLS Test

| link             | cities | cosine excess | p      | same-topic lift | beats null? |
| ---------------- | ------ | ------------- | ------ | --------------- | ----------- |
| paper × project  | 120    | +0.0102       | 0.0065 | 1.30x (p 0.016) | yes         |
| paper × patent   | 44     | +0.0347       | 0.0065 | 1.27x (p 0.020) | yes         |
| project × patent | 28     | +0.0043       | 0.2274 | 0.99x (p 0.464) | no          |
10. Mantel Test
11. Conclusion
	* iGEM Projects are related to local research
	* Policy Takeaway: Fund student research
	* Next potential steps: Distribution of patents based on DNA sequences, more in-depth patent retrieval with current data, causal analysis (do iGEM projects influence the research landscape of a city?)


## Extra Slides
1. Embedding model History
2. Example iGEM project (Uppsala)
3. 
