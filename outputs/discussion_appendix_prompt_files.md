# Discussion: should the prompt files be reproduced in the appendix?

*Generated with the project's `discussion` Claude Code skill
(`.claude/commands/discussion.md`), which stages a structured debate among three
named researchers and ends on a synthesis. This is a meta-analysis: the skill is
turned on the question of whether the skill files themselves belong in the thesis
appendix. Reproduced in Appendix A alongside the prompt that produced it.*

**Topic.** Should the custom Claude Code prompt files (the "skills" such as
`discussion.md` and `frankGPT.md` that steered the AI agents used to build this
thesis) be reproduced in the thesis appendix? A question about methodological
transparency, reproducibility, and the norms of disclosing AI tooling in an
empirical economic-geography thesis.

---

**Frank:** Let me start by being difficult, since that is what I am for. A
regression specification is a method. A geocoding rule is a method. A prompt that
tells a language model to "argue like an economic geographer" is not obviously a
method; it might be set dressing. So before we decide to bind these files into the
back of a thesis, I want an answer to a plain question: did the prompt change a
number, or did it only change the prose around the number? If it only flavored the
writing, it belongs in a footnote, not an appendix.

**Claudia:** That is too clean a line, Frank. In practice the framing changes the
analysis, not just the prose. If a prompt pushed the author to test a lead-lag
structure rather than a static cross-section, it shaped what got estimated. And
there is a norm question you are skipping. Journals have moved fast here: Nature,
Science, and the major publishers now require authors to disclose how they used
large language models and forbid listing them as authors. A thesis that used AI
agents to help design and draft its analysis and then said nothing about how would
look evasive in 2026, not rigorous. Reproducing the prompts is the honest version
of a methods disclosure.

**Marc:** And it is more interesting than mere compliance. Think about what these
files are. They are the experimental apparatus. In the Science of Science we keep
learning that the instrument shapes the finding, and here the instrument is a set
of instructions that configured an agent's whole reasoning posture. That is exactly
the kind of thing open science says you publish. We share code, we share seeds, we
share the notebook. Why would the prompt that steered the reasoning be the one
artifact we keep in a drawer? The whole iGEM ethos this thesis studies is that you
deposit your part in the registry so the next person can build on it. The prompt
files are this author's parts.

**Frank:** Careful with that analogy, because it cuts both ways. A BioBrick is
reproducible: the sequence is the sequence. An LLM prompt is not. Run it twice
against two model versions and you get two different debates. So if the
justification for the appendix is reproducibility, it is a weak justification. You
are not letting me rerun the study. You are handing me a script for a play whose
actors have already been recast.

**Claudia:** But reproducibility was never only bit-for-bit rerunning, even in
econometrics. Half of what a replication package buys you is the ability to see the
decisions. The prompt is the documented decision. I cannot reproduce your fieldwork
interviews either, Frank, yet you would still print your interview guide in the
appendix so I can see what you asked and what you led the respondent toward. That is
the right frame here. The prompt is a questionnaire, and you disclose the
questionnaire.

**Marc:** Yes, and the leading-question worry is the whole point in favor of
printing them. Look at the frankGPT file. It literally instructs the model to prefer
mechanism over description, to push toward relatedness and agglomeration framings, to
be skeptical of a result until it survives a regression. That is a thumb on the
scale, deliberately placed. A reader evaluating this thesis deserves to see that
thumb. Hiding it would be the offense; showing it is a gift to the critic.

**Frank:** That reframing I will actually accept. Not "here is how to reproduce me,"
but "here is the bias I introduced on purpose, read it and adjust." A prompt that
shapes the argument is a researcher degree of freedom, and the cleanest way to handle
a degree of freedom is to declare it out loud. On those grounds, print the ones that
steered reasoning. But only those. If the author includes a prompt that reformatted a
CSV, I will find them at the defense.

**Claudia:** Agreed, and that is the discipline the appendix needs: curate, do not
dump. Two or three files that changed how the work was reasoned about, each with a
line on what it was for. Not the hundred utility instructions. A reader's attention is
a budget, and spending it on scaffolding is its own kind of dishonesty because it
buries the two files that matter under noise.

**Marc:** And the last argument is the reflexive one, which I love too much to leave
out. This thesis has a claim baked into it, that a human supplies the vision and the
machine supplies the scale, and that the division of labor is honest and worth naming.
If that claim is real, the prompts are the vision written down. They are the most
direct evidence the thesis has that a person was steering. Omitting them would quietly
contradict the thesis's own argument about how it was made. Including them makes the
method match the message. The document about humans directing machine tools should
show the directions.

**Frank:** So we have talked ourselves from "probably theater" to "load-bearing,"
which is more than I expected when I opened my mouth. Fine. Include them, frame them as
declared instruments and declared bias rather than as a reproducibility guarantee, keep
it to the files that moved the reasoning, and annotate each one. And put this very
debate next to them, since apparently the instrument can be turned on the question of
its own inclusion, which is either rigorous or unbearably clever.

**Synthesis:** The three converge on a qualified yes: reproduce the reasoning-shaping
prompt files (`discussion`, `frankGPT`) in the appendix, but frame them correctly.
Their value is not bit-for-bit reproducibility, which an LLM cannot offer, but
disclosure of a deliberately introduced framing bias, the same reason one prints an
interview guide or a survey instrument. Include only the files that changed how the
work was reasoned about, annotate each with its purpose, and let the choice double as
evidence for the thesis's own man-and-machine claim, that the human hand steering the
tools should be visible rather than hidden.
