"""Skill contract checker, identifier scan and render tests for the stack-docs pack.

The checker and the identifier scan live in ``tests/stack_contract.py`` (decision D15). This file keeps the C2a tests
that exercise them against the stack-docs pack and against planted samples.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from stack_contract import (
    CONFORMING_SKILL,
    GUIDANCE_RULES,
    PACKS,
    SERVICE_RULES,
    VIOLATIONS,
    _table_body_rows,
    failed_rules,
    identifier_hits,
    identifier_hits_in_folder,
    row_cites_source_or_none_verified,
    verified_lines_are_well_formed,
)
from test_bundle_contract import TOKEN_PREFIXES
from test_sibling_name import NAME_WORDS

from chief.catalogue.bundle_tree import BundleTree
from chief.targets.locations import Locations
from chief.targets.names import CONCRETE_TARGETS

STACK_DOCS = PACKS / "stack-docs"
GUIDANCE_SKILLS = ("mcp-setup", "docs-lookup")
CONFIG_LAYOUTS = STACK_DOCS / "skills" / "mcp-setup" / "reference" / "config-layouts.md"
PLACEHOLDER_SNIPPET = """Set the key in the environment: ${ENV_VAR}
Account: <account_id>
Host: https://<project_ref>.supabase.co
"""


def _skill_text(name: str) -> str:
    """Return the text of the ``SKILL.md`` of the stack-docs skill ``name``, failing unless it exists."""
    path = STACK_DOCS / "skills" / name / "SKILL.md"
    assert path.is_file(), f"missing skill file: {path}"
    return path.read_text(encoding="utf-8")


# --- Pack tests. ---


def test_stack_skill_declares_agent_tooling() -> None:
    assert failed_rules(CONFORMING_SKILL, SERVICE_RULES) == []


@pytest.mark.parametrize(("rule", "violation"), list(VIOLATIONS.items()), ids=list(VIOLATIONS))
def test_each_contract_rule_rejects_its_violation(rule: str, violation: str) -> None:
    assert rule in failed_rules(violation, SERVICE_RULES)


def test_stack_docs_pack_loads_and_renders_for_every_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    locations = Locations()
    tree = BundleTree(packs_dir=PACKS, locations=locations)
    for target in CONCRETE_TARGETS:
        rendered = [path for path, _ in tree.build(target.value).files]
        for name in GUIDANCE_SKILLS:
            assert locations.config_root(target.value) / "skills" / name / "SKILL.md" in rendered, (target.value, name)


def test_checker_rejects_skill_without_verified_line() -> None:
    assert "verified line present" in failed_rules(VIOLATIONS["verified line present"], SERVICE_RULES)


def test_checker_rejects_http_endpoint() -> None:
    assert "https endpoints" in failed_rules(VIOLATIONS["https endpoints"], SERVICE_RULES)


def test_checker_rejects_description_over_300_chars() -> None:
    assert "description length" in failed_rules(VIOLATIONS["description length"], SERVICE_RULES)


def test_checker_rejects_skill_over_100_lines() -> None:
    assert "line limit" in failed_rules(VIOLATIONS["line limit"], SERVICE_RULES)


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


def test_identifier_scan_rejects_sibling_project_name() -> None:
    planted = f"Notes mention {'-'.join(NAME_WORDS)} in passing.\n"
    assert identifier_hits(planted) != []


def test_stack_docs_identifier_scan_is_clean() -> None:
    assert STACK_DOCS.is_dir(), f"missing pack folder: {STACK_DOCS}"
    assert identifier_hits_in_folder(STACK_DOCS) == []


def test_config_layouts_rows_cite_a_source() -> None:
    assert CONFIG_LAYOUTS.is_file(), f"missing reference file: {CONFIG_LAYOUTS}"
    text = CONFIG_LAYOUTS.read_text(encoding="utf-8")
    rows = _table_body_rows(text)
    assert rows, "config-layouts.md holds no table rows"
    assert [row for row in rows if not row_cites_source_or_none_verified(row)] == []
    assert verified_lines_are_well_formed(text)
