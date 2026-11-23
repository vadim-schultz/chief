"""Rule ``rollout``: the scheduling matrix wins, so each chapter's id, depends_on and touches follow its row."""

import re
from pathlib import Path

from wp_frontmatter import read_frontmatter
from wp_frontmatter_edit import set_field
from wp_io import write_text_atomic
from wp_matrix import Row, read_matrix, row_for
from wp_model import Context, Finding, flag, normalised
from wp_parser import chapter_files

RULE = "rollout"
DEPENDS_LINE = re.compile(r"\*\*Depends on:\*\*[^·\n]*")


def check_rollout(ctx: Context) -> list[Finding]:
    """Return one finding for each chapter that has no matrix row or whose values differ from its row."""
    rows = read_matrix(ctx.folder)
    return [finding for path in chapter_files(ctx.folder) for finding in _check_chapter(ctx, rows, path)]


def _check_chapter(ctx: Context, rows: list[Row], path: Path) -> list[Finding]:
    """Return the findings of one chapter. A chapter with unreadable frontmatter is left to the frontmatter rule."""
    text = path.read_text(encoding="utf-8")
    result = read_frontmatter(text)
    if result.error is not None:
        return []
    row = row_for(rows, path.name)
    if row is None:
        return [flag(RULE, ctx.relative(path), f"no rollout row names {path.name}")]
    differing = _differing_keys(result.fields, row)
    if not differing:
        return []
    write_text_atomic(path, _rewritten(text, row, differing))
    return [normalised(RULE, ctx.relative(path), f"matrix values written: {', '.join(differing)}")]


def _differing_keys(fields: dict[str, str | list[str]], row: Row) -> list[str]:
    """Return the matrix keys whose frontmatter value in the chapter differs from the row."""
    return [key for key, value in _matrix_values(row).items() if fields.get(key) != value]


def _matrix_values(row: Row) -> dict[str, str | list[str]]:
    """Return the frontmatter values the matrix holds for a chapter, keyed by field name."""
    return {"id": row.id, "depends_on": row.depends_on, "touches": row.touches}


def _rewritten(text: str, row: Row, differing: list[str]) -> str:
    """Return ``text`` with each differing field and the ``Depends on`` line set to the matrix values."""
    values = _matrix_values(row)
    for key in differing:
        text = set_field(text, key, _field_line(key, values[key]))
    return _depends_line(text, row.depends_on)


def _field_line(key: str, value: str | list[str]) -> str:
    """Return the frontmatter line for ``key``: a bare id, or a flow list of quoted strings."""
    if isinstance(value, str):
        return f"{key}: {value}"
    quoted = ", ".join(f'"{item}"' for item in value)
    return f"{key}: [{quoted}]"


def _depends_line(text: str, depends_on: list[str]) -> str:
    """Set the ``**Depends on:**`` line of the body to the matrix value, when the line is present."""
    value = ", ".join(depends_on) or "none"
    return DEPENDS_LINE.sub(lambda match: _depends_replacement(match.group(0), value), text)


def _depends_replacement(matched: str, value: str) -> str:
    """Return the replacement line, keeping the separator space that precedes the next field."""
    return f"**Depends on:** {value}" + (" " if matched.endswith(" ") else "")
