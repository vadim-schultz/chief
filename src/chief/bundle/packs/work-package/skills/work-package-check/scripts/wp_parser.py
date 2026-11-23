"""Read work package files: list the Markdown files, blank code spans and find Markdown links."""

import re
from dataclasses import dataclass
from pathlib import Path

CODE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")


@dataclass(frozen=True)
class Link:
    """One Markdown link target and the offsets of that target in the original text."""

    target: str
    start: int
    end: int


def chapter_files(folder: Path) -> list[Path]:
    """Return the chapter files ``chapters/NN-*.md`` of the work package, sorted by path."""
    return sorted((folder / "chapters").glob("[0-9][0-9]-*.md"))


def markdown_files(folder: Path) -> list[Path]:
    """Return every Markdown file under ``folder``, sorted by path."""
    return sorted(folder.rglob("*.md"))


def mask_code(text: str) -> str:
    """Return ``text`` with every code span and fenced block blanked, keeping all offsets."""
    return CODE.sub(_blank, text)


def _blank(match: re.Match[str]) -> str:
    """Return the matched text with each character except a newline replaced by a space."""
    return re.sub(r"[^\n]", " ", match.group(0))


def find_links(text: str) -> list[Link]:
    """Return each Markdown link in ``text`` that lies outside code, with the offsets of its target."""
    return [Link(match.group(1), match.start(1), match.end(1)) for match in LINK.finditer(mask_code(text))]
