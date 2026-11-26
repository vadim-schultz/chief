"""Skill contract checker, identifier scan and render tests for the stack-docs pack.

The checker is a set of small predicates, one per contract line. Each predicate takes the text of one
skill or one file and returns True when the text meets its line. The stack chapters that follow use the
same predicates unchanged.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from pathlib import Path

import pytest
from test_bundle_contract import FOREIGN_NAMES, TOKEN_PREFIXES

from chief.catalogue.bundle_tree import BundleTree
from chief.targets.locations import Locations
from chief.targets.names import CONCRETE_TARGETS

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKS = REPO_ROOT / "src" / "chief" / "bundle" / "packs"
STACK_DOCS = PACKS / "stack-docs"
GUIDANCE_SKILLS = ("mcp-setup", "docs-lookup")
CONFIG_LAYOUTS = STACK_DOCS / "skills" / "mcp-setup" / "reference" / "config-layouts.md"
DESCRIPTION_LIMIT = 300
LINE_LIMIT = 100
MCP_STATUSES = ("official", "community", "none verified")
AGENT_TOOLING_LABELS = ("MCP:", "Endpoint:", "Auth:", "Scope:", "Docs index:", "Verified:")
VERIFIED_BODY = re.compile(r"Verified: \d{4}-\d{2}-\d{2} https://\S+")
TABLE_SEPARATOR = re.compile(r"\|(?:\s*:?-+:?\s*\|)+")

Rule = Callable[[str], bool]


# --- Contract predicates. Each one checks one line of the skill contract. ---


def has_frontmatter_name_and_description(text: str) -> bool:
    """Return True when the frontmatter holds a ``name`` and a non-empty ``description``."""
    raise NotImplementedError


def description_within_limit(text: str) -> bool:
    """Return True when the frontmatter description is at most ``DESCRIPTION_LIMIT`` characters."""
    raise NotImplementedError


def skill_within_line_limit(text: str) -> bool:
    """Return True when the skill text is at most ``LINE_LIMIT`` lines."""
    raise NotImplementedError


def endpoints_are_https(text: str) -> bool:
    """Return True when the text names no plain ``http://`` URL."""
    raise NotImplementedError


def verified_lines_are_well_formed(text: str) -> bool:
    """Return True when every ``Verified:`` line holds a date and an https source URL."""
    raise NotImplementedError


def has_agent_tooling_section(text: str) -> bool:
    """Return True when the text has a ``## Agent tooling`` heading."""
    raise NotImplementedError


def has_agent_tooling_labels(text: str) -> bool:
    """Return True when every label of ``AGENT_TOOLING_LABELS`` starts a line of the text."""
    raise NotImplementedError


def mcp_status_is_allowed(text: str) -> bool:
    """Return True when the ``MCP:`` line holds one of ``MCP_STATUSES``."""
    raise NotImplementedError


def has_verified_line(text: str) -> bool:
    """Return True when the text holds at least one ``Verified:`` line."""
    raise NotImplementedError


def has_missing_server_section(text: str) -> bool:
    """Return True when the text has a ``## When the server is missing`` heading."""
    raise NotImplementedError


def has_working_rules_section(text: str) -> bool:
    """Return True when the text has a ``## Working rules`` heading."""
    raise NotImplementedError


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


def _term_pattern(term: str) -> str:
    """Return a regex for ``term`` that also matches an optional hyphen or underscore between its parts."""
    parts = [part for part in re.split(r"[-_]", term) if part]
    return r"[-_]?".join(re.escape(part) for part in parts)


SIBLING_PATTERN: re.Pattern[str] | None = (
    re.compile("|".join(_term_pattern(term) for term in FOREIGN_NAMES), re.IGNORECASE) if FOREIGN_NAMES else None
)


def identifier_hits(text: str) -> list[str]:
    """Return the names of the identifier rules that ``text`` breaks."""
    raise NotImplementedError


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
    raise NotImplementedError


def _table_body_rows(text: str) -> list[str]:
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


# --- Helpers that read and edit sample skill text. ---


def _starts_with_label(line: str, label: str) -> bool:
    """Return True when ``line``, without a leading bullet, starts with ``label``."""
    return line.removeprefix("- ").startswith(label)


def _edit_lines(text: str, label: str, replacement: str | None) -> str:
    """Return ``text`` with each line that starts with ``label`` replaced, or removed when ``replacement`` is None."""
    lines: list[str] = []
    for line in text.splitlines():
        if not _starts_with_label(line, label):
            lines.append(line)
        elif replacement is not None:
            lines.append(replacement)
    return "\n".join(lines) + "\n"


def _skill_text(name: str) -> str:
    """Return the text of the ``SKILL.md`` of the stack-docs skill ``name``, failing unless it exists."""
    path = STACK_DOCS / "skills" / name / "SKILL.md"
    assert path.is_file(), f"missing skill file: {path}"
    return path.read_text(encoding="utf-8")


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

PLACEHOLDER_SNIPPET = """Set the key in the environment: ${ENV_VAR}
Account: <account_id>
Host: https://<project_ref>.supabase.co
"""


# --- Pack tests. ---


def test_stack_skill_declares_agent_tooling() -> None:
    assert failed_rules(CONFORMING_SKILL, SERVICE_RULES) == []


@pytest.mark.parametrize(
    ("rule", "violation"),
    [
        ("frontmatter name and description", _edit_lines(CONFORMING_SKILL, "name:", None)),
        (
            "description length",
            _edit_lines(CONFORMING_SKILL, "description:", "description: " + "x" * (DESCRIPTION_LIMIT + 1)),
        ),
        ("line limit", CONFORMING_SKILL + "filler\n" * LINE_LIMIT),
        (
            "https endpoints",
            CONFORMING_SKILL.replace("https://mcp.example.invalid/mcp", "http://mcp.example.invalid/mcp"),
        ),
        (
            "verified lines well formed",
            _edit_lines(CONFORMING_SKILL, "Verified:", "- Verified: yesterday https://docs.example.invalid/"),
        ),
        ("agent tooling section", CONFORMING_SKILL.replace("## Agent tooling", "## Tooling")),
        ("agent tooling labels", _edit_lines(CONFORMING_SKILL, "Scope:", None)),
        ("mcp status", _edit_lines(CONFORMING_SKILL, "MCP:", "- MCP: maybe")),
        ("verified line present", _edit_lines(CONFORMING_SKILL, "Verified:", None)),
        ("missing server section", CONFORMING_SKILL.replace("## When the server is missing", "## Missing")),
        ("working rules section", CONFORMING_SKILL.replace("## Working rules", "## Rules")),
    ],
)
def test_each_contract_rule_rejects_its_violation(rule: str, violation: str) -> None:
    assert rule in failed_rules(violation, SERVICE_RULES)


def test_stack_docs_pack_loads_and_renders_for_every_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    locations = Locations()
    for target in CONCRETE_TARGETS:
        rendered = [path for path, _ in BundleTree(packs_dir=PACKS, locations=locations).build(target.value).files]
        for name in GUIDANCE_SKILLS:
            assert locations.config_root(target.value) / "skills" / name / "SKILL.md" in rendered, (target.value, name)


def test_checker_rejects_skill_without_verified_line() -> None:
    assert "verified line present" in failed_rules(_edit_lines(CONFORMING_SKILL, "Verified:", None), SERVICE_RULES)


def test_checker_rejects_http_endpoint() -> None:
    plain = CONFORMING_SKILL.replace("https://mcp.example.invalid/mcp", "http://mcp.example.invalid/mcp")
    assert "https endpoints" in failed_rules(plain, SERVICE_RULES)


def test_checker_rejects_description_over_300_chars() -> None:
    long = _edit_lines(CONFORMING_SKILL, "description:", "description: " + "x" * (DESCRIPTION_LIMIT + 1))
    assert "description length" in failed_rules(long, SERVICE_RULES)


def test_checker_rejects_skill_over_100_lines() -> None:
    long = CONFORMING_SKILL + "filler\n" * LINE_LIMIT
    assert "line limit" in failed_rules(long, SERVICE_RULES)


def test_stack_docs_skills_meet_guidance_rules() -> None:
    for name in GUIDANCE_SKILLS:
        assert failed_rules(_skill_text(name), GUIDANCE_RULES) == [], name


def test_identifier_scan_accepts_placeholders() -> None:
    assert identifier_hits(PLACEHOLDER_SNIPPET) == []


def test_checker_rejects_literal_secret_in_snippet() -> None:
    planted = "Key: " + TOKEN_PREFIXES[0] + "a" * 20 + "\n"
    assert identifier_hits(planted) != []


def test_identifier_scan_rejects_supabase_project_host() -> None:
    planted = "Host: https://abcd1234efgh5678.supabase.co/mcp\n"
    assert identifier_hits(planted) != []


@pytest.mark.skipif(not FOREIGN_NAMES, reason="needs the local leak denylist named by CHIEF_LEAK_DENYLIST")
def test_identifier_scan_rejects_sibling_project_name() -> None:
    planted = f"Notes mention {FOREIGN_NAMES[0]} in passing.\n"
    assert identifier_hits(planted) != []


def test_stack_docs_identifier_scan_is_clean() -> None:
    assert STACK_DOCS.is_dir(), f"missing pack folder: {STACK_DOCS}"
    assert identifier_hits_in_folder(STACK_DOCS) == []


def test_config_layouts_rows_cite_a_source() -> None:
    assert CONFIG_LAYOUTS.is_file(), f"missing reference file: {CONFIG_LAYOUTS}"
    rows = _table_body_rows(CONFIG_LAYOUTS.read_text(encoding="utf-8"))
    assert rows, "config-layouts.md holds no table rows"
    assert [row for row in rows if not row_cites_source_or_none_verified(row)] == []
