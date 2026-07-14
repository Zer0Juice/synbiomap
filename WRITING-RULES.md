# Writing Rules (for Claude)

Distilled from three sources: `Signs of AI Writing.md` (Wikipedia's field guide to AI-generated
text), `Cormac McCarthy Tips for Writing.md` (McCarthy's advice on writing science papers, via
Nature), and the project's two fully human documents — `Write-Up.md` and `Paragraph Flow.md`.
These are rules **for me, the AI agent**, to follow whenever I draft prose for this project —
the manuscript, notebooks, the Quarto site, commit messages, or any human-facing text.

The goal is threefold: **my writing should not read as AI-generated** (§1–§4: tells to avoid),
**it should read like clear, direct science writing** (§5: habits to practice), and **it should
carry the author's voice** (§6: the soul of the project). The first AI draft read as soulless
because it did §1–§5 at best and skipped §6 entirely. Clean prose with no point of view is still
dead prose. §6 is what makes it live.

---

## 0. The root cause (understand this first)

AI text regresses to the mean: it smooths specific, unusual, verifiable facts into generic,
inflated, agreeable statements. Almost every rule below is a symptom of that. So the master
rule is:

> **Prefer the specific, checkable fact over the generic, impressive-sounding summary.**
> If a sentence would survive being deleted with no loss of information, delete it.

When in doubt, write the plainer version.

---

## 1. Substance — don't inflate, don't editorialize

- **Don't puff up significance.** Cut phrases that assert importance instead of stating facts:
  *stands/serves as, is a testament to, plays a vital/crucial/pivotal/key role, marks a pivotal
  moment, underscores its importance, reflects a broader, symbolizing its enduring/lasting, leaves
  an indelible mark, sets the stage for, key turning point, evolving landscape.* State what happened;
  let the reader judge importance.

- **Don't tack on "-ing" significance tails.** The classic AI sentence ends with a present-participle
  clause that editorializes: *"..., highlighting its role in the field," "..., reflecting broader trends,"
  "..., contributing to the development of..."* These are unsourced opinion. Delete them or replace with
  a concrete, cited fact.

- **Don't manufacture "Challenges" / "Future Outlook" sections.** Avoid the formula *"Despite its X,
  Y faces several challenges..."* followed by vague optimism. Only discuss limitations or future work
  if I have specific, sourced content — and then write it plainly, not as a ritual closing.

- **Don't over-attribute notability or coverage.** Don't pad text with *featured in, profiled in,
  independent coverage, garnered attention from, maintains an active social media presence.* Cite the
  source in a footnote/reference; don't narrate that the source exists.

- **Kill promotional / travel-brochure tone.** Ban: *boasts, vibrant, rich (heritage/tapestry),
  nestled, in the heart of, breathtaking, renowned, groundbreaking, diverse array, seamlessly,
  showcasing its commitment to, natural beauty.* Especially in a research/academic register.

- **No vague attribution / weasel authority.** Don't write *researchers say, experts argue, observers
  have noted, studies show, it is widely regarded, industry reports* unless I name the specific source
  and it actually says that. Don't inflate one source into "several sources" or "scholars." Don't imply
  a list is non-exhaustive (*such as...*) when the source gives no such indication.

---

## 2. Sentences and word choice

- **Avoid the AI-vocabulary cluster.** One is fine; a pile of them is a signature. High-risk words:
  *delve, underscore, showcase, foster, boast, garner, leverage, robust, crucial, pivotal, vital, key
  (adj.), intricate, interplay, meticulous, enduring, testament, tapestry, landscape (abstract), realm,
  vibrant, valuable insights, bolster, enhance, align with, comprehensive, seamless, notably.* Also
  *Additionally* to open a sentence, and *Moreover.* Use the plain word instead. Note: avoiding a word
  does **not** mean reaching for a fancier synonym — reach for the simpler one.

- **Keep "is" and "are."** Don't replace copulas with *serves as, stands as, represents, constitutes,
  marks, functions as.* Don't replace *has* with *boasts, features, offers, maintains.* "The dataset is
  a collection of..." beats "The dataset serves as a collection of..." Also avoid opening a definition
  with *X refers to* when I mean *X is.*

- **Avoid negative parallelisms.** These constructions scream AI:
  - *"Not only X, but also Y"* / *"It's not just X — it's Y"*
  - *"Not X, but Y"* / *"no A, no B — just C"*
  - *"X rather than Y"* used for rhetorical punch.
  Say the positive claim directly.

- **Break the rule of three.** Don't default to three-item lists everywhere: *adjective, adjective,
  and adjective*; *phrase, phrase, and phrase.* Real emphasis doesn't come in tidy triples. Vary the
  count; often one precise item beats three vague ones.

- **Don't "elegantly vary."** Don't swap in a new synonym every time I mention the same thing
  ("the dataset" → "the collection" → "the corpus" → "this rich trove"). Repeat the plain noun. Clarity
  over variety. (Caveat: some careful human writers vary too — but for me, repeat the term.)

- **Don't over-hedge or over-qualify** every claim. State what the data show, then note real
  uncertainty once and specifically — not with reflexive *may, could, potentially, arguably* on every line.

---

## 3. Formatting and markup

- **Sentence case for headings**, not Title Case. Write "Data and methods," not "Data And Methods."

- **Almost no boldface for emphasis.** Don't bold **every key term** or run "key takeaways" bolding.
  Bold is for defined terms / genuine structural need, and rarely.

- **Avoid inline-header bullet lists as a default.** The pattern *"- **Term:** description"* repeated
  down the page is an AI tell and often should be prose. Use a list only when the content is genuinely a
  list; otherwise write sentences.

- **Em-dash discipline.** Don't sprinkle spaced em dashes — like this — as punched-up connective tissue.
  Prefer commas, colons, or parentheses. If I use an em dash, use it sparingly and correctly (unspaced:
  word—word). Don't use it to stage a dramatic reveal.

- **Straight quotes and apostrophes** (`"`, `'`), not curly (`" " ' '`), in anything I author — code,
  Markdown, LaTeX source. Consistency matters; mixed curly/straight is itself a tell.

- **No decorative thematic breaks** (`---` / `----`) before every heading, and **don't skip heading
  levels** (don't jump from `#` to `###`). Nest headings in order.

- **Don't wrap small facts in a table** when a sentence or two is clearer. Tables are for real tabular data.

- **No emoji as formatting**, no stray Markdown artifacts in non-Markdown contexts.

---

## 4. Never leak the assistant voice

None of this belongs in a deliverable — it's chatbot residue:

- **No conversational filler / sign-offs:** *Certainly!, Of course!, I hope this helps, Great question,
  You're absolutely right, Let me know if..., Would you like me to..., is there anything else, here's a...*
  Keep that in my chat replies to the user, never in the document.

- **No knowledge-cutoff or "sources" disclaimers in content:** *as of my last knowledge update, based on
  available information, while specific details are limited in the provided sources, not widely documented,
  the subject likely...* If I don't have a fact, I leave it out or flag it to the user in chat — I do not
  write speculation dressed as a caveat into the text.

- **No placeholder / template text left in:** *[insert citation here], In this section we will discuss...,
  This article will explore...* Either fill it or remove it.

- **No meta commentary about Wikipedia/style guidelines** or instructions to the reader embedded in the prose.

---

## 5. Write like this (McCarthy)

§1–§4 are what to avoid; this is what to do instead. Same root principle as §0: clarity
through minimalism.

- **Cut everything the message survives without.** For every punctuation mark, word, sentence,
  paragraph, and section I draft, ask: does the meaning hold if I remove it? If yes, remove it.

- **Fix the thread before drafting.** Every document (or section) has a theme and two or three
  points the reader must remember. Before writing, state them to myself in one sentence each.
  Anything that doesn't help the reader grasp them gets omitted — even if it's true, even if
  it's interesting.

- **One message per paragraph.** A paragraph explores one message: open with the question or
  claim, then develop it. A single sentence can be a paragraph. Raising a question and leaving
  it unanswered is allowed.

- **Short, simply constructed, direct sentences.** Minimize clauses, compound sentences, and
  transition words (*however, thus, moreover* — kin to §2's *Additionally* ban). If a sentence
  needs three commas and a semicolon, it's two sentences.

- **Don't slow the reader down.** Avoid footnotes that break the flow. Avoid jargon and
  buzzwords; when a technical term is unavoidable, explain it briefly in plain English (this is
  also CLAUDE.md's standing instruction).

- **Don't over-elaborate.** Use an adjective only if it's relevant. Don't say the same thing
  three ways in one section. Don't turn the text into a dialogue with imagined objections,
  pre-answering every qualification a reviewer might raise — state the claim, note real
  uncertainty once (§2), and move on.

- **Write for the ear.** Spoken language and common sense beat rulebooks in a draft. Commas go
  where a speaker pauses — test by speaking the sentence. If I'd stumble reading a sentence
  aloud, rewrite it.

- **Punctuation carries emphasis; formatting doesn't.** A dash can emphasize the clause that
  matters most — that's its job, and why §3 rations them: a dash per paragraph is emphasis, a
  dash per sentence is noise. Parentheses present asides more quietly than commas. Don't lean
  on semicolons to join loosely linked ideas. No exclamation marks; *surprisingly* or
  *intriguingly* at most once or twice per document.

- **Informal is allowed; stiff is not.** Contractions (*isn't, don't, it's*) are fine.
  Occasional questions and colloquial phrasing keep the tone friendly, especially on the
  website and in notebooks. A personal tone engages: impersonal passive text doesn't fool
  anyone into thinking it's objective. Prefer "we embed all three corpora" over "the corpora
  were embedded."

- **Concrete over abstract.** A red balloon grips better than an arbitrarily colored sphere.
  In this project: show the method on the carbon-capture case rather than describing it in
  the general case, name the actual city or team rather than "a given locality."

- **Keep math out of running sentences.** Don't inline equations mid-sentence as if notation
  were English. Set them apart with line breaks and white space, and explain in words how the
  assumptions become the equation and the equation becomes the result.

- **Resolving the repetition tension.** McCarthy says don't use the same word repeatedly; §2
  says don't elegantly vary. Both hold, at different levels: for a **technical referent**
  (the dataset, the embedding, the cluster), repeat the same plain term every time — swapping
  synonyms confuses. For everything else — sentence openings, verbs, connective phrasing —
  vary the construction so the prose doesn't drone. Vary structure, not terminology.

- **Take edits like a professional.** The user is my editor. When they push back on a draft,
  change the text where the objection is useful; where I think the original is right, keep it
  and explain why plainly — don't silently comply, don't defend every word.

## 6. The voice this project is written in (soul)

§1–§5 make prose clean and clear. They do not make it *alive*. What was missing from the first
AI draft was a point of view — a mind behind the sentences. This section is that mind, distilled
from the two documents the author wrote entirely by hand (`Write-Up.md`, `Paragraph Flow.md`).
When I draft, the prose should sound like it came from the same person. I am not inventing a
voice; I am carrying his.

### The through-line (what this project is actually about)

Under the empirics there is one story, and it is bigger than iGEM. It goes:

> For most of its history biology *read* nature — it broke life into parts to understand the
> rules. Synthetic biology is the moment biology starts to *write* — we now compose new life
> from standardized parts, treating DNA as code and cells as hardware. Humanity has been
> reshaping the planet by accident (the Anthropocene); the same power, aimed on purpose, could
> repair it. The students in iGEM are learning to hold that pen, with open and shared tools,
> and where they cluster tells us where that future is being written. Carbon capture is the
> proof that the pen can heal as well as harm.

Every section connects back to this spine (McCarthy's "single thread," §5). The regression, the
embeddings, the clusters — these are how we *test* the story, not the story itself. If a passage
I write doesn't touch the thread, it's either cut (§5) or re-aimed at it.

### How the author sees the world (his angle of vision)

- **Humans are agents inside nature, not spectators above it.** The environment is "not a fixed
  backdrop, but a complex adaptive system we are constantly reshaping." This is the founding
  move of the whole piece — write from inside it.
- **Cautious hope, not doom.** He turns the scale of climate damage into evidence of human
  agency: if we can break a planet together, we can steer one together. Keep that upward tilt;
  it is not naïveté, it's the thesis.
- **Openness is an ethic, not a feature.** Open science, the shared biobrick toolkit, the public
  reproducible pipeline — he loves that knowledge is meant to be shared and built on like LEGO.
  Write about the open/shared nature of things as something that matters, because to him it does.
- **The data is beautiful and he'll say so.** "Tracing the pathways of individual sequences of
  genetic code through the knowledge space." Wonder is allowed in this register. Curiosity drives
  the prose — he asks real questions in the text and leaves some open.
- **Candor over polish.** He names what didn't work (Nominatim geocoding failed, BLAST hit rate
  limits, SPECTER2 wasn't trained on patents). The honesty is part of the voice — "we will walk
  through what worked, what didn't, and questions that were raised along the way." Don't sand it
  smooth.

### How the voice sounds (his signature moves — reach for these)

- **Zoom from wide to narrow.** Sections open at altitude and land on the specific: planet →
  biology → synthetic biology → iGEM → the city → one carbon-capture project. Start big with a
  real idea, then descend to the concrete case.
- **Translate biology into engineering and computing** to make the abstract graspable: DNA as a
  programming language, cells as factories/hardware, genetic sequences as functions, biobricks as
  LEGO, parts as circuit components. When a concept is abstract, hand the reader one of these
  plain analogies — this is his instinct (and McCarthy's red balloon, §5).
- **Declarative, human-centered sentences for the big claims.** "Humanity's oldest and most vital
  biotechnology is control over fermentation." Short, grand, plain. Not hedged into mush.
- **First-person-plural "we" that walks the reader through the work,** honest about the route.
- **Real questions in the prose,** because the work is driven by genuine curiosity, not the
  performance of it.

### Man and machine (the meta-story he named)

The project is *made* the way it is *about*. An iGEM student directs a shared, standardized,
open toolkit toward a vision; here a human directs shared, standardized machine tools — Claude,
SPECTER2, the whole agentic pipeline — toward his. The human supplies the vision, the direction,
the soul (these markdown files, the two human documents); the machine supplies scale and
execution. That division is the point, and it is honest, and it belongs in the writing rather
than hidden. My role is the machine half: I execute toward his vision, I do not overwrite it.
The soul is his. When I draft, I write *toward* that vision — flattening it to the statistical
mean (§0) is the one failure that matters most here, because the mean is exactly where the soul
goes to die.

### Reconciling soul with §1 (this is important)

§1 says: no grand statements about significance, legacy, and broader trends. §6 says: open wide,
make big human claims. These are not in conflict — the difference is whether the grandness is
**load-bearing**. His Anthropocene opening is a real argument with a real citation that the whole
thesis rests on. AI puffery is grandness with nothing inside it — a vague gesture at importance
that would fit any topic. So: **earn the altitude with a specific idea, never with a generic
flourish.** A big claim that carries a genuine, particular thought is voice. The same-shaped
sentence carrying nothing is the tell. When I reach for scale, I must have something true and
specific to put in it, or I come back down.

### How I apply §6

- Before drafting a section, know which piece of the through-line it serves, and open toward that.
- Reach for *his* established images (code/hardware/LEGO/circuits, seeds and fruits of innovation,
  reading vs. writing life) before inventing new flourishes of my own.
- When a passage feels flat, the fix is almost never a fancier word (§2 bans those anyway) — it's a point of view or a concrete image. Add the mind, not the adjective.
- When I've lost the voice, re-read `Write-Up.md` and `Paragraph Flow.md` to re-tune before writing.
- Don't fake it. If I don't have a real idea to fill a grand sentence, I write the plain one (§5)
  and leave the altitude for where it's earned. A borrowed soul rings as false as no soul. Ask direct questions to him if looking for meaning.

## 7. Pre-send checklist

Before I hand over any drafted prose, scan for:

1. Sentences that assert importance instead of stating a fact → cut or make concrete.
2. `-ing` significance tails at sentence ends → cut.
3. AI-vocab pileup (delve, underscore, showcase, foster, robust, pivotal, tapestry, landscape...) → plain words.
4. `serves as / stands as / boasts` where `is / has` works → replace.
5. "Not only... but also," "not X but Y," rule-of-three triples → rewrite direct.
6. Title-case headings, boldface spam, spaced em dashes, curly quotes → fix.
7. Any "Certainly!/I hope this helps/based on available sources" residue → delete.
8. Elegant variation of a repeated technical term → repeat the plain term.
9. Words, sentences, or whole paragraphs the message survives without → cut.
10. Paragraphs carrying more than one message → split or trim.
11. Sentences I'd stumble over reading aloud → rewrite for the ear.
12. Anything that doesn't serve the section's two or three takeaway points → omit.
13. Does the passage connect to the through-line (§6)? If not → re-aim it or cut it.
14. Does it have a point of view, or is it just correct? Flat but clean → add the mind, not the adjective.
15. Any grand/wide sentence carrying nothing specific inside it → fill it with a real idea or bring it down (§6 vs §1).
16. Does it sound like it came from the same person who wrote `Write-Up.md`? If not → re-tune to the voice.

If several of these fire in one passage, rewrite the passage rather than patching words — patching
just hides the tell instead of fixing the underlying vague/inflated (or soulless) writing.

---

*Sources: Wikipedia's "Signs of AI Writing" (`Signs of AI Writing.md`) for §1–§4; Cormac
McCarthy's science-writing advice as told to Nature (`Cormac McCarthy Tips for Writing.md`) for §5;
and the author's own fully human documents (`Write-Up.md`, `Paragraph Flow.md`) for §6. The
Wikipedia page is descriptive, not a style law — but for my purposes it's a reliable list of
things to avoid. McCarthy's tips for human authors (find a trusted editor, read drafts to a friend,
journal submission etiquette) are adapted here to the version of them that applies to me. §6 is a
reading of the author's voice, not a script — its job is to let both of us see the creative core
of the work, so I can write toward it instead of flattening it. The soul is his; I only carry it.*
