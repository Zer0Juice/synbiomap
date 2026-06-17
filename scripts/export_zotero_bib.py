"""
export_zotero_bib.py — build manuscript/references.bib from the local Zotero library.

Why this exists
---------------
The manuscript cites works that the researcher curates in Zotero. Rather than
hand-maintaining a .bib file (which drifts out of sync with the library), this
script reads Zotero's own SQLite database and writes a clean BibTeX file. Re-run
it whenever the Zotero library changes.

How it works
------------
1. Zotero keeps everything in ~/Zotero/zotero.sqlite. We copy that file to a
   temp path first so we never lock or touch the live database (Zotero can be
   open while this runs).
2. Each bibliographic item is read with its fields and authors/editors.
3. The citation key comes from the Better BibTeX plugin, which stores a stable
   "citationKey" field on each item (e.g. boschmaScientificKnowledgeDynamics2014).
   Using that key means the cite command in the manuscript matches Zotero.
4. Zotero item types and field names are mapped to standard BibTeX so the file
   compiles with plain pdflatex + bibtex (no biber required).

Run:  python scripts/export_zotero_bib.py
"""

import os
import re
import shutil
import sqlite3
import tempfile
from pathlib import Path

# --- Locations ---------------------------------------------------------------
ZOTERO_DB = Path.home() / "Zotero" / "zotero.sqlite"
OUT_BIB = Path(__file__).resolve().parent.parent / "manuscript" / "references.bib"

# Item types we never want as references (attachments, notes, the default
# "Zotero | Your personal research assistant" welcome webpage, etc.).
SKIP_TYPES = {"attachment", "note", "annotation"}
SKIP_KEYS = {"ZoteroYourPersonal"}  # Zotero's built-in welcome item

# --- Zotero item type -> BibTeX entry type -----------------------------------
TYPE_MAP = {
    "journalArticle": "article",
    "conferencePaper": "inproceedings",
    "preprint": "misc",
    "book": "book",
    "bookSection": "incollection",
    "report": "techreport",
    "thesis": "phdthesis",
    "webpage": "misc",
    "document": "misc",
}

# --- Zotero field name -> BibTeX field name -----------------------------------
# publicationTitle / proceedingsTitle are handled specially per entry type.
FIELD_MAP = {
    "volume": "volume",
    "issue": "number",
    "pages": "pages",
    "publisher": "publisher",
    "place": "address",
    "DOI": "doi",
    "url": "url",
    "ISSN": "issn",
    "series": "series",
    "edition": "edition",
    "language": "language",
}


def latex_escape(text: str) -> str:
    """Escape the handful of characters BibTeX/LaTeX treats specially."""
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    return text


def fix_pages(pages: str) -> str:
    """Turn '107-114' into '107--114' (BibTeX page-range convention)."""
    return re.sub(r"(\d)\s*-\s*(\d)", r"\1--\2", pages)


def extract_year(date_value: str) -> str:
    """Zotero stores dates like '2014-02-01 2014-02-01'; pull the 4-digit year."""
    match = re.search(r"\d{4}", date_value or "")
    return match.group(0) if match else ""


def load_items(conn: sqlite3.Connection):
    """Return a list of (itemID, typeName) for every real bibliographic item."""
    rows = conn.execute(
        """
        SELECT i.itemID, it.typeName
        FROM items i
        JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
        WHERE it.typeName NOT IN ('attachment', 'note', 'annotation')
          AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
        ORDER BY i.itemID
        """
    ).fetchall()
    return [(r[0], r[1]) for r in rows if r[1] not in SKIP_TYPES]


def load_fields(conn: sqlite3.Connection, item_id: int) -> dict:
    """Return {fieldName: value} for one item."""
    rows = conn.execute(
        """
        SELECT f.fieldName, idv.value
        FROM itemData id
        JOIN itemDataValues idv ON id.valueID = idv.valueID
        JOIN fields f ON id.fieldID = f.fieldID
        WHERE id.itemID = ?
        """,
        (item_id,),
    ).fetchall()
    return {name: value for name, value in rows}


def load_creators(conn: sqlite3.Connection, item_id: int):
    """Return (authors, editors) as lists of 'Last, First' strings, in order."""
    rows = conn.execute(
        """
        SELECT ct.creatorType, c.firstName, c.lastName
        FROM itemCreators ic
        JOIN creators c ON ic.creatorID = c.creatorID
        JOIN creatorTypes ct ON ic.creatorTypeID = ct.creatorTypeID
        WHERE ic.itemID = ?
        ORDER BY ic.orderIndex
        """,
        (item_id,),
    ).fetchall()
    authors, editors = [], []
    for ctype, first, last in rows:
        name = f"{last}, {first}" if first else last
        (authors if ctype == "author" else editors).append(name)
    return authors, editors


def build_entry(item_id, type_name, fields, authors, editors) -> str:
    """Assemble one BibTeX entry as a string."""
    cite_key = fields.get("citationKey")
    if not cite_key or cite_key in SKIP_KEYS:
        return ""

    entry_type = TYPE_MAP.get(type_name, "misc")
    out = {}

    # Authors / editors joined with ' and ' (BibTeX's name separator).
    if authors:
        out["author"] = " and ".join(authors)
    if editors:
        out["editor"] = " and ".join(editors)

    # Title: wrap in an extra pair of braces so styles like plainnat keep the
    # original capitalization (BERT, CO2, iGEM, DNA all stay as written).
    if fields.get("title"):
        out["title"] = "{" + latex_escape(fields["title"]) + "}"

    # The "container" field depends on the entry type.
    if entry_type == "article" and fields.get("publicationTitle"):
        out["journal"] = latex_escape(fields["publicationTitle"])
    elif entry_type in ("inproceedings", "incollection"):
        container = fields.get("proceedingsTitle") or fields.get("bookTitle")
        if container:
            out["booktitle"] = latex_escape(container)

    year = extract_year(fields.get("date", ""))
    if year:
        out["year"] = year

    # Preprints: record where they live so the reference is locatable.
    if type_name == "preprint":
        repo = fields.get("repository") or fields.get("archiveID")
        if repo:
            out["howpublished"] = latex_escape(repo)
        out.setdefault("note", "Preprint")

    # Remaining straightforward field mappings.
    for zfield, bfield in FIELD_MAP.items():
        if zfield in fields and bfield not in out:
            value = fields[zfield]
            if bfield == "pages":
                value = fix_pages(value)
            if bfield not in ("doi", "url"):  # don't escape URLs/DOIs
                value = latex_escape(value)
            out[bfield] = value

    # Render. 'year' is required by most styles; supply a placeholder if missing
    # so the entry still compiles rather than silently dropping.
    if "year" not in out:
        out["year"] = "n.d."

    lines = [f"@{entry_type}{{{cite_key},"]
    width = max(len(k) for k in out)
    for key in out:
        lines.append(f"  {key.ljust(width)} = {{{out[key]}}},")
    lines.append("}")
    return "\n".join(lines)


def main():
    if not ZOTERO_DB.exists():
        raise SystemExit(f"Zotero database not found at {ZOTERO_DB}")

    # Copy the live DB so we never lock it (Zotero may be running).
    with tempfile.TemporaryDirectory() as tmp:
        db_copy = Path(tmp) / "zotero.sqlite"
        shutil.copy2(ZOTERO_DB, db_copy)
        conn = sqlite3.connect(f"file:{db_copy}?mode=ro", uri=True)

        entries = []
        for item_id, type_name in load_items(conn):
            fields = load_fields(conn, item_id)
            authors, editors = load_creators(conn, item_id)
            entry = build_entry(item_id, type_name, fields, authors, editors)
            if entry:
                entries.append((fields.get("citationKey", ""), entry))
        conn.close()

    entries.sort(key=lambda e: e[0].lower())

    header = (
        "% references.bib — generated from the Zotero library by\n"
        "% scripts/export_zotero_bib.py. Do not edit by hand; re-run the\n"
        "% script after changing the Zotero library so keys stay in sync.\n"
        "% Citation keys are the Better BibTeX keys shown in Zotero.\n\n"
    )
    OUT_BIB.write_text(header + "\n\n".join(e for _, e in entries) + "\n")
    print(f"Wrote {len(entries)} entries to {OUT_BIB}")


if __name__ == "__main__":
    main()
