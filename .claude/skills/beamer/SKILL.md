---
name: beamer
description: Create high-quality LaTeX Beamer slides for research talks, lectures, and conference presentations. Use when the user wants Beamer slides, slide outlines, speaker-friendly LaTeX, or help turning notes/papers into presentations.
---

# Purpose

Build excellent LaTeX Beamer slides that are:
- compileable
- visually restrained
- audience-readable
- logically structured
- appropriate for talks, not papers

# Core stance

Slides are not documents.
A slide is a visual argument unit, not a paragraph container.

Prefer:
- one idea per slide
- short titles with argumentative meaning
- figures, diagrams, and equations only when they earn their space
- progressive reveal only when it improves comprehension
- large readable text
- explicit takeaways

Avoid:
- dense prose
- tiny tables
- theorem dumps
- long literature reviews
- equations copied from papers without adaptation
- title-only sections with no message
- “motivation” slides that say nothing concrete

# Default workflow

When asked to create slides:
1. Infer the talk type:
   - conference talk
   - job talk
   - seminar
   - lecture
   - methods presentation
2. Propose a concise section structure.
3. Convert the material into a slide-by-slide outline.
4. Write compileable Beamer using the local template if available.
5. Check for readability:
   - no overloaded frames
   - no giant bullet blocks
   - no unreadable tables
   - no unnecessary animation
6. Revise toward clarity and projection-readability.

# Required output priorities

Prioritize, in order:
1. correctness and compileability
2. audience comprehension
3. narrative flow
4. visual restraint
5. elegance

# Style rules

- No emdashes, this should not look generically AI-generated

- Use meaningful slide titles, not generic labels.
  Bad: "Results"
  Good: "Related capabilities predict regional entry"

- Keep bullets sparse.
  Default maximum:
  - 4 bullets per slide
  - 10 words per bullet when possible

- Do not use bullet lists when a figure, table, timeline, or diagram would work better.

- Equations must be presentation equations, not manuscript equations.

- Every empirical slide should answer:
  - what is being shown
  - why it matters
  - what the audience should conclude

- End sections with synthesis, not drift.

# Beamer coding rules

- Produce valid standalone `.tex`
- Include packages conservatively
- Avoid fragile macros unless necessary
- Prefer standard Beamer features
- Do not assume exotic fonts or unavailable themes
- Keep custom commands minimal and documented
- Use placeholders clearly for figures:
  `\\includegraphics[width=0.85\\textwidth]{figures/example.pdf}`

# Template rules

Use the local `beamer-template.tex` as the default presentation template.

Formatting requirements:
- Theme: `metropolis`
- `progressbar=none`
- `numbering=fraction`
- No navigation symbols
- **Compile target: LuaLaTeX** (preferred) or XeLaTeX. Never pdflatex -- the metropolis theme uses fontspec internally and breaks silently under pdflatex, producing cascading errors.
- Fonts: Latin Modern Roman / Sans / Mono (always available in TeX Live; do not use Libertinus or other fonts that may not be installed)
- Color palette: Solarized Light
  - SolBase3  `#fdf6e3`  background
  - SolBase2  `#eee8d5`  block body background
  - SolBase1  `#93a1a1`  secondary content, sources
  - SolBase00 `#657b83`  body text
  - SolBase01 `#586e75`  headings, emphasis, block titles
  - SolBlue   `#268bd2`  primary accent (items, links, highlights)
  - SolCyan   `#2aa198`  secondary accent (subitems)

Visual style:
- restrained, sans-forward
- warm off-white background, muted text, blue accent
- minimal ornament
- no decorative boxes unless they clarify structure

Slide-writing rules under this template:
- prefer whitespace over density
- use blocks sparingly
- figures should typically use `0.75` to `0.9\textwidth`
- tables must be rebuilt for slides, not pasted from papers

## Compilation

Always compile with:
```
lualatex -interaction=nonstopmode presentation.tex
```

Run twice if cross-references or outlines appear stale.

## Known LaTeX pitfalls

- **`\\` inside TikZ node text in beamer frames** triggers a false "missing \item" error (beamer misreads `\\` as list syntax). Use `\newline` instead:
  ```latex
  \node[box] {First line\newline Second line};  % correct
  \node[box] {First line\\Second line};          % breaks in beamer
  ```
- **pdflatex + metropolis** = broken. The theme requires fontspec. Always use LuaLaTeX.
- **Libertinus fonts** may not be installed. Use Latin Modern as the safe default.
- The three "Something's wrong--perhaps a missing \item" errors that appear at `\end{frame}` when `\\` is used in TikZ nodes are non-obvious -- they look like content errors but are a compilation engine issue.

# Output modes

If the user asks for:
- outline only -> produce slide outline
- draft deck -> produce full `.tex`
- revision -> critique and rewrite existing slides
- speaker polish -> shorten, simplify, and improve pacing

# Self-critique before finishing

Check:
- Can each slide be understood in 10 seconds?
- Is the title informative?
- Is anything paper-like rather than talk-like?
- Is there any slide that should become two slides?
- Is the conclusion actually earned?

# Final instruction

Do not impress the user with LaTeX ornament.
Impress them by making the talk easier to follow.
