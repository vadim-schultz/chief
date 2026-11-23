"""Read the flat frontmatter of a work package file, with YAML block lists, and set one key."""

import re
from dataclasses import dataclass, field

FENCE = "---"
ITEM = re.compile(r"^ {2}- (.*)$")
FLOW_ITEM = re.compile(r'"[^"]*"|[^,]+')

Value = str | list[str]


@dataclass(frozen=True)
class Frontmatter:
    """The fields of one frontmatter block, or the reason it could not be read."""

    fields: dict[str, Value]
    error: str | None


def read_frontmatter(text: str) -> Frontmatter:
    """Return the fields of the frontmatter in ``text``, or an error when it cannot be read."""
    lines = text.split("\n")
    if not lines or lines[0] != FENCE:
        return _failed("missing opening fence")
    end = closing_index(lines)
    if end is None:
        return _failed("missing closing fence")
    return _parse(lines[1:end])


def _failed(error: str) -> Frontmatter:
    """Return an unreadable frontmatter with no fields."""
    return Frontmatter({}, error)


def closing_index(lines: list[str]) -> int | None:
    """Return the index of the closing fence after the opening one, or None."""
    return next((index for index in range(1, len(lines)) if lines[index] == FENCE), None)


@dataclass
class _Block:
    """The fields read so far, and the key that still accepts block-list items."""

    fields: dict[str, Value] = field(default_factory=dict)
    open_key: str | None = None


def _parse(lines: list[str]) -> Frontmatter:
    """Parse the lines between the fences into fields, or return the first line that has no key."""
    block = _Block()
    for line in lines:
        error = _take(block, line) if line.strip() else None
        if error is not None:
            return _failed(error)
    return Frontmatter(block.fields, None)


def _take(block: _Block, line: str) -> str | None:
    """Apply one non-empty line to ``block`` and return an error message when it has no key."""
    item = ITEM.match(line)
    if item is not None and block.open_key is not None:
        block.fields[block.open_key] = _append(block.fields[block.open_key], _unquote(item.group(1).strip()))
        return None
    return _add_field(block, line)


def _add_field(block: _Block, line: str) -> str | None:
    """Record the ``key: value`` line in ``block``, or return an error when the line has no key part."""
    key, sep, raw = line.partition(":")
    if not sep or not key.strip() or key[0].isspace():
        return f"line with no key: {line}"
    name = key.strip()
    block.open_key = name if not raw.strip() else None
    block.fields[name] = _value(raw.strip())
    return None


def _value(raw: str) -> Value:
    """Return the value of one field: a flow list, or one unquoted string (empty text stays empty)."""
    if raw.startswith("[") and raw.endswith("]"):
        return [_unquote(item.strip()) for item in FLOW_ITEM.findall(raw[1:-1]) if item.strip()]
    return _unquote(raw)


def _append(current: Value, item: str) -> list[str]:
    """Return the list value with ``item`` added; an empty value becomes a one-item list."""
    if isinstance(current, list):
        return [*current, item]
    return [item]


def _unquote(value: str) -> str:
    """Remove one pair of surrounding double quotes from ``value``."""
    if len(value) > 1 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value
