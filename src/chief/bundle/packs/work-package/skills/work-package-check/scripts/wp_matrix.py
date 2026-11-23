"""Read the scheduling matrix of a work package: one row per chapter, with its id, depends-on and touches."""

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from wp_parser import markdown_files

CODE_SPAN = re.compile(r"`([^`]*)`")
LINK_TARGET = re.compile(r"\]\(([^)\s]+)\)")
REQUIRED_COLUMNS = frozenset({"id", "chapter", "touches"})


@dataclass(frozen=True)
class Row:
    """One matrix row: the chapter file name and the values the matrix holds for it."""

    chapter: str
    id: str
    depends_on: list[str]
    touches: list[str]


def read_matrix(folder: Path) -> list[Row]:
    """Return every matrix row found in the Markdown files of the work package."""
    return [row for path in markdown_files(folder) for row in _rows_of_text(path.read_text(encoding="utf-8"))]


def row_for(rows: list[Row], chapter: str) -> Row | None:
    """Return the first row whose chapter file is ``chapter``, or None."""
    return next((row for row in rows if row.chapter == chapter), None)


def _rows_of_text(text: str) -> list[Row]:
    """Return the matrix rows of every table in ``text`` that has the matrix columns."""
    return [row for table in _tables(text) for row in _rows_of_table(table)]


def _tables(text: str) -> list[list[list[str]]]:
    """Return each run of consecutive pipe lines in ``text`` as a table of cells."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.split("\n"):
        if line.strip().startswith("|"):
            current.append(_cells(line))
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def _cells(line: str) -> list[str]:
    """Return the trimmed cells of one pipe line."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _rows_of_table(table: list[list[str]]) -> list[Row]:
    """Return the rows of a table whose header has the matrix columns, skipping the separator row."""
    header = [cell.replace("_", " ").lower() for cell in table[0]]
    if not REQUIRED_COLUMNS <= set(header):
        return []
    records = [dict(zip(header, cells, strict=False)) for cells in table[1:] if not _is_separator(cells)]
    return [row for record in records if (row := _row(record)) is not None]


def _is_separator(cells: list[str]) -> bool:
    """Return True for the ``| --- |`` row that separates a table header from its rows."""
    return all(cell and set(cell) <= set(":-") for cell in cells)


def _row(record: dict[str, str]) -> Row | None:
    """Return the matrix row for one table line, or None when its chapter cell names no file."""
    chapter = _chapter_file(record.get("chapter", ""))
    if chapter is None:
        return None
    return Row(
        chapter=chapter,
        id=record.get("id", "").strip("`"),
        depends_on=_ids(record.get("depends on", "")),
        touches=CODE_SPAN.findall(record.get("touches", "")),
    )


def _chapter_file(cell: str) -> str | None:
    """Return the file name of the chapter named by a code span or a link in ``cell``, or None."""
    targets = [*CODE_SPAN.findall(cell), *LINK_TARGET.findall(cell)]
    return PurePosixPath(targets[0].split("#", 1)[0]).name if targets else None


def _ids(cell: str) -> list[str]:
    """Return the comma-separated ids in ``cell``, or an empty list for ``none``."""
    items = (item.strip().strip("`") for item in cell.split(","))
    return [item for item in items if item and item.lower() != "none"]
