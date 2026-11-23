"""Rule ``structure``: insert each missing chapter section as a stub, and flag unknown or out-of-order headings."""

from pathlib import Path

from wp_frontmatter import read_frontmatter
from wp_io import write_text_atomic
from wp_model import Context, Finding, flag, normalised
from wp_parser import chapter_files

RULE = "structure"
PLACEHOLDER = "_To be written._"
FENCE = "```"


def check_structure(ctx: Context) -> list[Finding]:
    """Return the structure findings of every chapter; missing sections are written into the chapter in place."""
    return [finding for path in chapter_files(ctx.folder) for finding in _check_chapter(ctx, path)]


def _check_chapter(ctx: Context, path: Path) -> list[Finding]:
    """Return the findings of one chapter, inserting stubs for its missing sections.

    A chapter whose frontmatter is unreadable is left to the frontmatter rule and is not changed here.
    """
    text = path.read_text(encoding="utf-8")
    if read_frontmatter(text).error is not None:
        return []
    lines = text.split("\n")
    headings = _headings(lines)
    names = [name for _, name in headings]
    rel = ctx.relative(path)
    findings = _unknown_findings(rel, names, ctx.chapter_sections)
    findings += _misplaced_findings(rel, names, ctx.chapter_sections)
    missing = _missing_sections(names, ctx.chapter_sections)
    if not missing:
        return findings
    write_text_atomic(path, "\n".join(_insert_stubs(lines, headings, ctx.chapter_sections)))
    return [*findings, *(normalised(RULE, rel, f"inserted stub: {name}") for name in missing)]


def _headings(lines: list[str]) -> list[tuple[int, str]]:
    """Return the index and text of each ``##`` heading outside fenced code."""
    result: list[tuple[int, str]] = []
    fenced = False
    for index, line in enumerate(lines):
        if line.startswith(FENCE):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            result.append((index, line))
    return result


def _unknown_findings(rel: str, names: list[str], sections: tuple[str, ...]) -> list[Finding]:
    """Return one flag for each heading that is not a template section."""
    return [flag(RULE, rel, f"unknown section: {name}") for name in names if name not in sections]


def _misplaced_findings(rel: str, names: list[str], sections: tuple[str, ...]) -> list[Finding]:
    """Return one flag for each template section that appears after a later template section."""
    ordered = [sections.index(name) for name in names if name in sections]
    flagged: list[Finding] = []
    highest = -1
    for position in ordered:
        if position < highest:
            flagged.append(flag(RULE, rel, f"out of template order: {sections[position]}"))
        highest = max(highest, position)
    return flagged


def _missing_sections(names: list[str], sections: tuple[str, ...]) -> list[str]:
    """Return the template sections that have no heading in the chapter, in template order."""
    return [section for section in sections if section not in names]


def _insert_stubs(lines: list[str], headings: list[tuple[int, str]], sections: tuple[str, ...]) -> list[str]:
    """Return ``lines`` with a stub before the next present section for each missing template section."""
    positions = {name: index for index, name in reversed(headings)}
    inserts = _stubs_by_anchor(sections, positions, len(lines))
    result: list[str] = []
    for index in range(len(lines) + 1):
        result.extend(inserts.get(index, []))
        if index < len(lines):
            result.append(lines[index])
    return result


def _stubs_by_anchor(sections: tuple[str, ...], positions: dict[str, int], end: int) -> dict[int, list[str]]:
    """Return the stub lines for each missing section, keyed by the line index they are inserted before."""
    inserts: dict[int, list[str]] = {}
    for position, name in enumerate(sections):
        if name not in positions:
            anchor = _next_present(sections[position + 1 :], positions, end)
            inserts.setdefault(anchor, []).extend([name, "", PLACEHOLDER, ""])
    return inserts


def _next_present(later: tuple[str, ...], positions: dict[str, int], end: int) -> int:
    """Return the line index of the first present section in ``later``, in template order, or ``end``."""
    return next((positions[name] for name in later if name in positions), end)
