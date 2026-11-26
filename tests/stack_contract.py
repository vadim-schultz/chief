"""Shared skill contract checker and identifier scan for the stack packs.

The checker is a set of small predicates, one per contract line. Each predicate takes the text of one skill or one
file and returns True when the text meets its line. The stack pack tests import these predicates unchanged, so every
stack pack meets one contract (decision D15).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from pathlib import Path

from test_bundle_contract import TOKEN_VALUE
from test_sibling_name import NAME as SIBLING_NAME

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKS = REPO_ROOT / "src" / "chief" / "bundle" / "packs"
DESCRIPTION_LIMIT = 300
LINE_LIMIT = 100
MCP_STATUSES = ("official", "community", "none verified")
AGENT_TOOLING_LABELS = ("MCP:", "Endpoint:", "Auth:", "Scope:", "Docs index:", "Verified:")
VERIFIED_BODY = re.compile(r"Verified: \d{4}-\d{2}-\d{2} https://\S+")
SOURCE_URL = re.compile(r"https://[^\s|`]+")
TABLE_SEPARATOR = re.compile(r"\|(?:\s*:?-+:?\s*\|)+")

Rule = Callable[[str], bool]


# --- Text readers. Each one returns plain data and holds no rule. ---


def _frontmatter(text: str) -> dict[str, str]:
    """Return the flat ``key: value`` pairs of the frontmatter fence, or an empty dict when there is none."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    end = lines.index("---", 1)
    pairs = (line.partition(":") for line in lines[1:end])
    return {key.strip(): value.strip() for key, sep, value in pairs if sep}


def _has_heading(text: str, heading: str) -> bool:
    """Return True when a line of ``text`` is exactly ``heading``."""
    return any(line.strip() == heading for line in text.splitlines())


def _bullet_body(line: str) -> str:
    """Return ``line`` without its surrounding spaces and its leading ``- `` bullet."""
    return line.strip().removeprefix("- ")


def _label_bodies(text: str, label: str) -> list[str]:
    """Return the body of each line that starts with ``label``, without its bullet or surrounding spaces."""
    return [body for body in map(_bullet_body, text.splitlines()) if body.startswith(label)]


def table_body_rows(text: str) -> list[str]:
    """Return the body rows of each markdown table in ``text``, without the header and separator rows."""
    lines = text.splitlines()
    rows: list[str] = []
    for index, line in enumerate(lines):
        if not line.startswith("|") or TABLE_SEPARATOR.fullmatch(line.strip()):
            continue
        if index + 1 < len(lines) and TABLE_SEPARATOR.fullmatch(lines[index + 1].strip()):
            continue
        rows.append(line)
    return rows


# --- Contract predicates. Each one checks one line of the skill contract. ---


def has_frontmatter_name_and_description(text: str) -> bool:
    """Return True when the frontmatter holds a ``name`` and a non-empty ``description``."""
    fields = _frontmatter(text)
    return bool(fields.get("name")) and bool(fields.get("description"))


def description_within_limit(text: str) -> bool:
    """Return True when the frontmatter description is at most ``DESCRIPTION_LIMIT`` characters."""
    return len(_frontmatter(text).get("description", "")) <= DESCRIPTION_LIMIT


def skill_within_line_limit(text: str) -> bool:
    """Return True when the skill text is at most ``LINE_LIMIT`` lines."""
    return len(text.splitlines()) <= LINE_LIMIT


def endpoints_are_https(text: str) -> bool:
    """Return True when the text names no plain ``http://`` URL."""
    return "http://" not in text


def verified_lines_are_well_formed(text: str) -> bool:
    """Return True when every ``Verified:`` line holds a date and an https source URL."""
    return all(VERIFIED_BODY.fullmatch(body) for body in _label_bodies(text, "Verified:"))


def has_agent_tooling_section(text: str) -> bool:
    """Return True when the text has a ``## Agent tooling`` heading."""
    return _has_heading(text, "## Agent tooling")


def has_agent_tooling_labels(text: str) -> bool:
    """Return True when every label of ``AGENT_TOOLING_LABELS`` starts a line of the text."""
    return all(_label_bodies(text, label) for label in AGENT_TOOLING_LABELS)


def mcp_status_is_allowed(text: str) -> bool:
    """Return True when the ``MCP:`` line holds one of ``MCP_STATUSES``."""
    values = [body.removeprefix("MCP:").strip() for body in _label_bodies(text, "MCP:")]
    return bool(values) and all(value in MCP_STATUSES for value in values)


def has_verified_line(text: str) -> bool:
    """Return True when the text holds at least one ``Verified:`` line."""
    return bool(_label_bodies(text, "Verified:"))


def has_missing_server_section(text: str) -> bool:
    """Return True when the text has a ``## When the server is missing`` heading."""
    return _has_heading(text, "## When the server is missing")


def has_working_rules_section(text: str) -> bool:
    """Return True when the text has a ``## Working rules`` heading."""
    return _has_heading(text, "## Working rules")


GUIDANCE_RULES: tuple[tuple[str, Rule], ...] = (
    ("frontmatter name and description", has_frontmatter_name_and_description),
    ("description length", description_within_limit),
    ("line limit", skill_within_line_limit),
    ("https endpoints", endpoints_are_https),
    ("verified lines well formed", verified_lines_are_well_formed),
)
SERVICE_RULES: tuple[tuple[str, Rule], ...] = GUIDANCE_RULES + (
    ("agent tooling section", has_agent_tooling_section),
    ("agent tooling labels", has_agent_tooling_labels),
    ("mcp status", mcp_status_is_allowed),
    ("verified line present", has_verified_line),
    ("missing server section", has_missing_server_section),
    ("working rules section", has_working_rules_section),
)


def failed_rules(text: str, rules: Iterable[tuple[str, Rule]]) -> list[str]:
    """Return the names of the rules that ``text`` fails, in rule order."""
    return [name for name, rule in rules if not rule(text)]


# --- Identifier scan. Each rule names one kind of identifier that stack files must not hold. ---

PROJECT_HOST = re.compile(r"\b[a-z0-9][a-z0-9-]*\.supabase\.co\b", re.IGNORECASE)
IDENTIFIER_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("supabase project host", PROJECT_HOST),
    ("token value", TOKEN_VALUE),
    ("sibling project name", SIBLING_NAME),
)


def identifier_hits(text: str) -> list[str]:
    """Return the names of the identifier rules that ``text`` breaks."""
    return [name for name, pattern in IDENTIFIER_RULES if pattern.search(text)]


def identifier_hits_in_folder(root: Path) -> list[str]:
    """Return one ``path: rule`` entry for each identifier hit in the files under ``root``."""
    return [
        f"{path.relative_to(root).as_posix()}: {name}"
        for path in sorted(root.rglob("*"))
        if path.is_file()
        for name in identifier_hits(path.read_text(encoding="utf-8"))
    ]


# --- Config layout rows. Each row cites a vendor page or says that nothing was verified. ---


def row_cites_source_or_none_verified(row: str) -> bool:
    """Return True when a table row holds an https source URL or the words ``none verified``."""
    return bool(SOURCE_URL.search(row)) or "none verified" in row


# --- Helpers that edit sample skill text. ---


def _edit_lines(text: str, label: str, replacement: str | None) -> str:
    """Return ``text`` with each line that starts with ``label`` replaced, or removed when ``replacement`` is None."""
    lines: list[str] = []
    for line in text.splitlines():
        if not _bullet_body(line).startswith(label):
            lines.append(line)
        elif replacement is not None:
            lines.append(replacement)
    return "\n".join(lines) + "\n"


CONFORMING_SKILL = """---
name: sample-service
description: Sample service skill for the contract checker. Use when the sample service is named in a request.
---

# Sample service

Short introduction for the sample service.

## Agent tooling

- MCP: official
- Endpoint: https://mcp.example.invalid/mcp
- Auth: OAuth in the MCP client
- Scope: read-only first
- Docs index: https://docs.example.invalid/llms.txt
- Verified: 2026-11-26 https://docs.example.invalid/

## When the server is missing

Say so. Point to the mcp-setup skill. Never edit MCP configuration.

## Working rules

- Check current limits on the vendor page.
"""

# One planted violation per contract rule, keyed by the rule name. Each one breaks only its own rule.
VIOLATIONS: dict[str, str] = {
    "frontmatter name and description": _edit_lines(CONFORMING_SKILL, "name:", None),
    "description length": _edit_lines(
        CONFORMING_SKILL,
        "description:",
        "description: " + "x" * (DESCRIPTION_LIMIT + 1),
    ),
    "line limit": CONFORMING_SKILL + "filler\n" * LINE_LIMIT,
    "https endpoints": CONFORMING_SKILL.replace("https://mcp.example.invalid/mcp", "http://mcp.example.invalid/mcp"),
    "verified lines well formed": _edit_lines(
        CONFORMING_SKILL,
        "Verified:",
        "- Verified: yesterday https://docs.example.invalid/",
    ),
    "agent tooling section": CONFORMING_SKILL.replace("## Agent tooling", "## Tooling"),
    "agent tooling labels": _edit_lines(CONFORMING_SKILL, "Scope:", None),
    "mcp status": _edit_lines(CONFORMING_SKILL, "MCP:", "- MCP: maybe"),
    "verified line present": _edit_lines(CONFORMING_SKILL, "Verified:", None),
    "missing server section": CONFORMING_SKILL.replace("## When the server is missing", "## Missing"),
    "working rules section": CONFORMING_SKILL.replace("## Working rules", "## Rules"),
}
