# frankGPT Knowledge Base

Thematic index files. frankGPT loads these selectively based on the question.

| File | Section | Always loaded? | Papers |
|------|---------|----------------|--------|
| index_neffke.md | Frank Neffke | Yes | ? |
| index_eeg.md | Evolutionary Economic Geography | No | ? |
| index_complexity.md | Economic Complexity | No | ? |
| index_agglomeration.md | Agglomeration & Urban Economics | No | ? |
| index_methods.md | Econometrics & Methods | No | 8 |

## Rebuild
```bash
python .claude/skills/frankGPT/scripts/build_knowledge_base.py
```
Add `--no-cache` to re-fetch from OpenAlex. Add `--section <name>` to rebuild one section.

Cached API responses are in `_cache/` (excluded from git).