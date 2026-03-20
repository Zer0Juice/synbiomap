---
name: pdf-to-context
description: >
  Convert PDFs to token-efficient markdown for LLM context windows. Uses marker-pdf
  with Ollama for high-quality extraction, then compresses output by stripping boilerplate.
  Trigger on: "pdf to context", "pdf for claude", "compress pdf for llm", "pdf to markdown",
  batch-convert PDFs, prepare PDFs for prompts/knowledge bases, reduce PDF token usage.
---

# PDF to Context

Two-stage pipeline: **marker-pdf** extracts → **compression** strips waste.

## Prerequisites

```bash
pip install marker-pdf
ollama pull gemma3:12b   # or any vision-capable model
```

Ollama must be running (`ollama serve` or system service).

## Usage

```bash
python scripts/pdf_to_context.py INPUT [-o OUTPUT] [OPTIONS]
```

INPUT is a PDF file or directory (batch mode). Output defaults to `<name>.md`.

**Options:**
- `--ollama-model MODEL` — Ollama model name (default: `gemma3:12b`)
- `--ollama-url URL` — Ollama base URL (default: `http://localhost:11434`)
- `--no-llm` — skip LLM pass, use marker's ML models only
- `--force-ocr` — force OCR on all pages (for scanned PDFs)
- `--strip-references` — remove bibliography/references sections
- `--max-tokens N` — truncate to ~N tokens
- `--keep-headers` — preserve repeated headers/footers
- `--format md|txt` — output format (default: md)
- `-v, --verbose` — print stats

## What gets stripped

Repeated headers/footers, page numbers, copyright boilerplate, TOC entries,
decorative lines, `![](image)` references, excessive whitespace.

## Output

```markdown
---
source: file.pdf
pages: 47
extractor: marker+ollama
tokens_raw: 31200
tokens_compressed: 11800
compression: 62%
---
# Document content here...
```