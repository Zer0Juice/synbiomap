
## Title:
Projects Papers and Proteins: How student research in biotech relates to locally publications

## Abstract:
Over 100,000 students, researchers, and practitioners have participated building the International Genetic Engineering Machine, a decentralized worldwide science competition for students and 

We've used linguistic embeddings to compare student iGEM projects with academic publications by city, and found significant overlap between the topics studied by students and professional researchers. Then



## Introduction: The Question
* Introduce iGEM briefly
	* Concept, short history, genetic toolkit
* Why do certain teams innovate? Are the students better educated? Do they have access to better labs? Local companies to partner with?
* Why is synthetic biology important? 

## Case Study
Show an impactful project
* iGEM Edinburgh 2013: WastED
* remediation and valorisation of local industrial waste streams
*  _Bacillus subtilis_ as a chassis
* The parts they created were cited by several followup papers; at 

\begin{frame}{Case Study: Edinburgh 2013}
\begin{columns}[T]
\begin{column}{0.52\textwidth}
	\begin{figure}
		\includegraphics[width=0.7\linewidth]{edinburgh}
	\end{figure}
  \textbf{The project: \highlight{WastED}}\\[0.3em]
  Engineering \textit{Bacillus subtilis} to produce bioethanol from industrial waste\\[0.3em]
  Published in \emph{ACS Synthetic Biology}, 2014\\[0.6em]
\end{column}
\begin{column}{0.45\textwidth}
  \vspace{0.3em}
  \textbf{9 students; where are they now?}
  \begin{itemize}
    \item \highlight{4 pursued PhDs} (Edinburgh, Cambridge, UCL)
    \item \highlight{1 faculty} (asst.\ professor, plant biotech, Krakow)
    \item \highlight{3 moved into biotech industry} (Novonesis, Abbott, Meridian)
    \item \highlight{1 startup founder} (Biotangents Ltd, diagnostics)

  \end{itemize}
\end{column}
\end{columns}


\end{frame}



Notes
* include better intro from igem site
* communicate the why 
	* this is interesting because it offers a fine-grained insight into the normally hidden process of innovation
* say what im trying to do first
* include the 3d projections


Hey everybody! Thanks for coming out here, I'm Zakh, I been here visiting the Transforming Economies group at the Hub since January. Thank you to frank for bringing me here and supervising my project, and thanks to the rest of the group for helping along the way, it's been a lot of fun. I'm here studying regional innovation patterns in biotechnology, and am happy for the chance to do a tuesday talk!

So let's get a show of hands, who here has heard of iGEM? Nobody? not too surprising, i hadn't either until a few years ago when i started working with synthetic biologists. But for synbio, this is it. The International Genetic Engineering Machine is a nonprofit organization that's been advancing the cause of open science and standards in synthetic biology for over 20 years now. They started as a small science fair type project at MIT to test out and promote a modular system for genetic assembly called the "biobrick standard". Biobricks are interoperable genetic "building blocks" which can be used to create synthetic biological circuits that carry out programmed tasks. Students are given one year and a standard toolkit of genetic parts and protocols to solve some problem, often environmental or societal. These can range from whimsical, like bacteria programmed to give off a banana scent, strange but potentially useful, like a bioplastic synthesis platform using human feces as a feedstock for astronauts to make plastic in space, all the way to potentially terrifying, like infectious parasitic fungi designed to kill cockroaches. Over 100,000 students from schools around the world have participated in this program, and many along the way have created genuinely interesting novel ideas that advance science.

The organization is a global hub in an emergent industry that trains and educates the future thought leaders of the field. They are also incredibly committed to open science practices and making all their data freely available. Each student project is documented in a regimented, standardized format, and published as an open-source website on the iGEM git servers. The biobricks, those genetic building blocks the students use and create, are all uploaded and stored in an open-source registry. Each project publishes anywhere from 1 to hundreds of parts; there are 80,000 of them stored in this registry for synbio practitioners to access. Each project is supported by research labs, corporate sponsors, community resources, and open-source protocols.

That brings me to why it's so fascinating to me. Beyond the science projects of the students, the iGEM competition itself functions as a sort of large-scale natural experiment, presenting us with data offering unique fine-grained insights into the process of innovation in a new, interdisciplinary, difficult-to-study field.

So the first thing I'd like to know is, how embedded are these student projects in local innovation systems? Of course, the students generally have help and connections to industry and sponsors; it takes a lot of money, equipment, and expertise to participate in this project. Are they studying the same topics as local researchers?

To look at this, we downloaded a set of synthetic biology papers from openalex based on keywords, and scraped data on 4600 iGEM projects. Also downloaded the biobrick registry, pulled all the papers that individual parts cited by DOI, and downloaded a set of papers that cited the biobricks themselves. This made for approximately 15,000 papers and projects in the field of synthetic biology. To compare the papers and the projects in a meaningful empirical way, we embedded them in a semantic space as you can see right here 

[swipe to project and paper embeddings]

This is based on a 768 dimensional space, and flattened down to 3d it obviously loses some of its characteristics, but still you can see that certain parts and papers cluster together.

For this, we used SPECTER2, which is a document embedding model based on BERT, and trained to predict whether two scientific papers will cite one another. As you can see, it works pretty decent for iGEM projects too.

So first of all, just tested if a project entering the space was likely to be closer to the papers from its own city, vs the papers from another random city.
So we take the centroid of a city's projects. And calculate the cosine distance of each iGEM project to its city's project centroid.

And it turns out, the projects are in fact much closer to their own city's paper centroids. This holds up in a few different statistical tests. 

Very significant relationship, as you can see. And here's a difference-in-difference test showing the same, adding a temporal dimension this time.

And if we split up the data all by year, turns out that the student projects actually are closest in semantic similarity to publications in the future, suggesting that they're indicative of a city's future innovation trajectory.

