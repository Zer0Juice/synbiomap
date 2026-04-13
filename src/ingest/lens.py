"""
lens.py — DEPRECATED. This module has been superseded by patentsview.py.

The patent data source was switched from Lens.org to PatentsView (USPTO)
for the following reasons:
  - PatentsView requires no API key (free, open-government data)
  - PatentsView has a stable, well-documented schema
  - US patents are the dominant jurisdiction for synthetic biology patents
    (Oldham & Hall, 2018), so coverage loss is limited
  - Removing the Lens.org credential dependency improves reproducibility

Use src/ingest/patentsview.py for all new patent retrieval.
"""

raise ImportError(
    "lens.py is deprecated. Import src.ingest.patentsview instead.\n"
    "See scripts/02_ingest_patents.py for the updated pipeline."
)
