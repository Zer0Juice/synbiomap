Script to scrape all iGEM wikis for DOI citations and link them

Predicting the innovation trajectory of each city

Cluster-based validation of iGEM projects coming before publications


## The thing being tested (one refresher)

For a city, take one artifact type (say its papers) and count how many fall in each of the 80 topics. That's a list of 80 counts. Do the same for another type (projects). Scale each list to length 1, then take the **cosine** — a number from 0 to 1 that's high when the two types pile into the _same_ topics and low when they don't.

$$\text{overlap} = \cos(\text{paper topic-counts},\ \text{project topic-counts})$$

We measured that overlap for 120 cities, averaged it (**0.050**), and compared it to a "shuffled" baseline (**0.040**). The gap, **+0.010**, is the signal. Every check below is a different way of asking _"is that +0.010 real, or an accident?"_

---

## 1. The size control (is it just city size in disguise?)

**The worry.** Last time (notebook 01), a similar-looking number turned out to be _nothing but city size_. Big cities produce more documents, and more documents make a steadier, more "average" fingerprint, which mechanically pushes overlaps up. So before we trust the new number, we have to rule out the same trap.

**How the check works.** We ask a plain question with a regression: _if I already know how many papers and how many projects a city has, how much of its overlap can I predict?_ In math, we fit a straight-line model:

$$\text{overlap} \approx \beta_0 + \beta_1 \log(#\text{papers}) + \beta_2 \log(#\text{projects})$$

(We use $\log$ — which grows slowly — because going from 5 to 50 documents matters more than 500 to 550. We also add a "country" adjustment so we're comparing cities within the same country.)

**What we read off it.** The output is an **R²**, a number from 0 to 1 meaning _"fraction of the overlap that size alone explains."_

- Centroid measure last time: R² was **high** → the measure _was_ size. Dead on arrival.
- What we need here: R² **low** (say under ~0.15) → size barely predicts overlap, so the +0.010 is about _which topics_ cities share, not _how much_ they produce.

That's the whole point of this check: one sentence — "unlike the centroid, size explains little" — retires the old ghost.

---

## 2. The k-sweep (did we get lucky with one clustering?)

**The worry.** We chose 80 topics from one clustering run (HDBSCAN), and it labeled 30% of documents as "noise" and threw them out. A skeptic says: _maybe the signal only appears at exactly 80 topics, or only because you discarded the awkward third of the data._

**How the check works.** Re-do the topics at many different resolutions and see if the answer wobbles. We use a simpler clustering method (**KMeans**) that just splits everything into exactly **k** groups — and crucially assigns _every_ document, no noise thrown away. Then we run the identical decisive test at each setting:

$$k = 10,\ 20,\ 40,\ 60,\ 80,\ 120 \quad\longrightarrow\quad \text{excess and } p \text{ at each } k$$

- $k=10$: coarse, ten big themes.
- $k=120$: fine, many narrow themes.

**What we read off it.** A curve. If the excess stays positive and $p$ stays small across _every_ $k$, the finding doesn't depend on a magic number of topics — and because KMeans keeps all documents, it _also_ proves the result wasn't an artifact of dropping the noisy third. One figure does two jobs. If instead the signal only shows up at one $k$ and vanishes elsewhere, that's a red flag and we'd have to be honest about it.

---

## 3. Leave-one-city-out (is one big city carrying the whole result?)

**The worry.** Boston, Cambridge, and San Francisco are huge and appear in every version of the test. Maybe the +0.010 is really "the Boston effect" wearing a coat labeled "120 cities."

**How the check works.** The simplest idea in the whole list: **remove one city, redo the test, put it back, repeat for all 120.** Each time you get a p-value with that city missing:

$$p_{-\text{Boston}},\quad p_{-\text{Cambridge}},\quad p_{-\text{Paris}},\ \dots\ (120 \text{ of them})$$

**What we read off it.** If the result is genuinely _local and distributed_, then no single removal should change much — every one of those 120 p-values stays small. If pulling out Boston sends the p-value from 0.006 up to, say, 0.3, then you don't have a "cities in general" result, you have a "Boston" result, and you must say so. This is the most _intuitive_ check to explain to a non-statistician: "we checked that no one city is driving it" needs no math background at all.

---

## 4. Downsampling power (is the failed link truly empty, or just too small to see?)

**The worry.** The direct project↔patent link came out non-significant (p = 0.22) — but only **28 cities** had enough of both. A weak test on 28 cities can miss a real effect just from lack of data. We must not confuse _"no signal"_ with _"not enough data to detect a signal."_ Those are very different claims.

**How the check works.** Take the links that _did_ work (paper-project on 120 cities) and deliberately **cripple them to 28 cities** — randomly keep only 28, rerun, repeat many times:

$$\text{paper-project on 120 cities} ;\xrightarrow{\text{keep random 28}}; \text{is it still significant?}$$

**What we read off it.** Two possible conclusions, both honest:

- If paper-project _also_ becomes non-significant when squeezed to 28 cities → then project-patent's failure is about **sample size**, and we write "underpowered, cannot distinguish from the null," _not_ "no link exists."
- If paper-project _stays_ significant even at 28 cities → then 28 cities was plenty, and project-patent's flat result is a **real absence** of a direct link — which is exactly what the "papers-as-hub" story predicts anyway.

Either way, we get to say something defensible instead of quietly reporting a p-value and hoping no one asks how many cities were behind it.

---

**The through-line:** check 1 kills the old confound, check 2 shows we didn't cherry-pick the clustering, check 3 shows no single city is faking it, and check 4 keeps us honest about the one link that didn't fire. Four small checks, each answering one plain-English objection — no extra machinery.

Want me to run them and drop the four figures into the notebook?