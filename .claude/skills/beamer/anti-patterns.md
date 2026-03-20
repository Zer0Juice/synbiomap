# Anti-patterns

## Content
- “This slide contains the entire abstract”
- “Regression table screenshot from PDF”
- “Three findings, two mechanisms, and one apology on the same slide”
- “Roadmap slide that consumes 10% of the talk”
- “Related literature as an unreadable cemetery of surnames”
- “Citation flows heatmap floating in the middle of a narrative about capabilities” -- every slide must connect to the argument
- “Placeholder results labeled '?' instead of 'pending'” -- be specific about what is outstanding
- “Corpus diagnostics figure on a motivation slide” -- diagnostics are methods content, not motivation
- “Weak opening that states topic without stakes” -- the first slide must answer why the audience should care

## Compilation
- Using pdflatex with metropolis theme -- always LuaLaTeX
- Using `\\` inside TikZ node text in beamer frames -- use `\newline`
- Assuming Libertinus or other non-standard fonts are installed -- default to Latin Modern
- Writing `\begin{frame}{...}` with dense prose paragraphs instead of visual units