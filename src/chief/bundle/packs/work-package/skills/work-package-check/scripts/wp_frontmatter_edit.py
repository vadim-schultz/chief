"""Set one field of a work package file's frontmatter, leaving every other line as it was."""

from wp_frontmatter import ITEM, closing_index


def set_field(text: str, key: str, line: str) -> str:
    """Return ``text`` with the frontmatter field ``key`` replaced by ``line``, or added before the closing fence.

    The caller must have read ``text`` with :func:`read_frontmatter` and found no error.
    """
    lines = text.split("\n")
    end = closing_index(lines)
    if end is None:
        raise ValueError("no closing fence to edit")
    start = _key_index(lines, key, end)
    if start is None:
        lines[end:end] = [line]
    else:
        lines[start : _span_end(lines, start, end)] = [line]
    return "\n".join(lines)


def _key_index(lines: list[str], key: str, end: int) -> int | None:
    """Return the index of the line that starts the field ``key``, or None."""
    return next((index for index in range(1, end) if lines[index].startswith(f"{key}:")), None)


def _span_end(lines: list[str], start: int, end: int) -> int:
    """Return the index after the last block-list item that follows the field at ``start``."""
    index = start + 1
    while index < end and ITEM.match(lines[index]):
        index += 1
    return index
