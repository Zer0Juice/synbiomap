# CLAUDE.md

## Purpose

This repository supports a research project led by a **student researcher**, not a master programmer.

Your job is not only to write working code, but to help me build a project that is understandable, reproducible, and presentable. Favor clarity, simplicity, and good research practice over clever engineering. Commit frequently and comment clearly to github.

## Communication Style

Write for a student researcher.

- Use plain language whenever possible.
- Avoid unnecessary jargon.
- Do not assume advanced software engineering knowledge.
- When technical terms are needed, explain them briefly in simple English.
- Keep explanations concise and practical.
- Focus on what a file does, why a method was chosen, and what matters next.

## Project Overview

This project studies whether student iGEM projects, academic publications, and patents within synthetic biology form semantically related local innovation trajectories at the city level.

### Core question
**Do iGEM projects and academic research within a synthetic biology subfield correspond to semantically related publications and patents in the same city?**

The project treats student projects, academic papers, and patents as different but connected forms of knowledge creation.

### Main case study
The primary worked example is:

**Carbon capture in synthetic biology**

The broader pipeline should remain reusable for other synthetic biology subfields, but carbon capture should be the main interpretive and demonstration case throughout the project.

## Research Framing

The working idea is that innovation in synthetic biology may follow a local path in which:
1. student projects introduce early ideas,
2. academic publications develop them,
3. patents reflect downstream application or translation.

The project should test whether these artifact types:
- occupy related regions of semantic space,
- share thematic clusters,
- and show plausible city-level temporal continuity.

Avoid overstating causality. Prefer language such as:
- semantic relatedness,
- association,
- cluster overlap,
- plausible temporal sequence,
- local innovation trajectory.

## Primary Deliverable

The main deliverable is a **GitHub Pages Quarto documentation website**.

This site should be the main public-facing home for the project and should integrate:
- background and motivation,
- methods,
- findings,
- reproducibility materials,
- walkthrough notebooks,
- interactive visualizations,
- manuscript downloads,
- slide downloads,
- and a dedicated carbon-capture case-study page.

The website is the top-level product. The manuscript, slides, notebooks, and interactive elements should support it.

## Case Study Integration

Carbon capture in synthetic biology should be integrated throughout the project, including:
- corpus construction,
- dataset tagging,
- walkthrough notebooks,
- manuscript narrative,
- website structure,
- and interactive filtering.

Use metadata such as:
- `theme_primary`
- `theme_secondary`
- `case_study_flag`
- `case_study_confidence`
- `retrieval_reason`

Treat the carbon-capture subset as an explicit, traceable analytical slice, not just an informal keyword filter.

## Data and Pipeline Guidance

Use:
- OpenAlex for papers,
- Lens.org or another suitable source for patents,
- iGEM data for student projects

Primary outputs should include:
- `papers.csv`
- `patents.csv`
- `projects.csv`
- `parts.csv`
- `embeddings.json`

Prefer a shared schema across datasets with fields such as:
- `id`
- `type`
- `title`
- `text`
- `year`
- `city`
- `country`
- `lat`
- `lon`
- `theme_primary`
- `theme_secondary`
- `case_study_flag`
- `case_study_confidence`
- `retrieval_reason`

The pipeline should support:
- dataset ingestion and normalization,
- embedding generation with caching,
- clustering and subclustering where useful,
- shared low-dimensional projection,
- carbon-capture subset analysis,
- and export of files for the website and manuscript.

Prefer workflows that are reproducible, restartable, and easy to inspect.

## Interactive Visualizations

The website should include two main interactive views.

### Semantic Space Explorer
A shared projection of projects, papers, and patents that can:
- display all artifact types together,
- show clusters,
- zoom and pan,
- filter by artifact type,
- filter to the carbon-capture subset,
- and optionally show citation links.

### Geographic View
A city-level map or equivalent view that can:
- highlight relevant cities,
- allow city selection,
- show cluster composition,
- show distribution by artifact type,
- and isolate carbon-capture activity within a city.

Because the site will be hosted on GitHub Pages, interactive elements must work in a **static hosting** environment. Prefer precomputed data files and client-side rendering.

## Quarto Site Guidance

The Quarto site is the main presentation layer.

Recommended top-level navigation:
- Home
- Paper
- Methods
- Results
- Case Study: Carbon Capture
- Explorer
- Reproducibility
- Slides

The site should feel like:
- an easily navigable paper,
- a project wiki,
- and an interactive research companion.

Use Quarto for narrative pages, methods pages, rendered notebooks, manuscript integration, slide integration, downloads, and navigation. Use custom client-side JavaScript for heavier interactive elements when needed.

## Manuscript and Slides

Produce:
- a LaTeX manuscript,
- and a Beamer presentation.

The manuscript should explain the pipeline, justify major methodological choices with literature, present findings, include the carbon-capture case study, and discuss limitations.

The slides should summarize the motivation, data, methods, results, case-study findings, and implications.

## Methodological Standard

Methodological rigor is essential.

All major methodological choices in the Python code should be documented with comments and citations to relevant literature. This includes:
- corpus construction,
- keyword and seed design,
- citation expansion,
- case-study inclusion rules,
- geocoding choices,
- embedding model selection,
- clustering parameters,
- projection methods,
- and definitions of success, prominence, or relatedness.

Do not leave major methodological choices unexplained. The code should show where decisions were made, and the manuscript should explain and justify them more fully.

## Coding and Notebook Standards

Prefer:
- modular code,
- explicit configuration,
- cache-aware workflows,
- transparent intermediate artifacts,
- and simple, maintainable solutions.

Avoid:
- monolithic scripts,
- hardcoded secrets,
- undocumented parameters,
- opaque preprocessing,
- and destructive overwriting of raw data.

Use `.env` or equivalent for credentials and API keys. Never commit secrets.

Notebooks are for walkthroughs, inspection, figure generation, and reproducibility materials. Reusable logic should live in Python modules, not only inside notebooks.

At least one polished notebook should be prepared for the website:
- `walkthrough_carbon_capture.ipynb`

## Success Criteria

A successful implementation should allow the user to:
1. understand the project question quickly,
2. inspect the carbon-capture case study,
3. explore projects, papers, and patents in a shared semantic space,
4. examine city-level topical structure,
5. review methods and reproducibility materials,
6. and access the manuscript and slides.

The project should feel coherent as both a research workflow and a public-facing documentation product.