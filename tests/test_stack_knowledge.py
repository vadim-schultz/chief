"""Skill contract checker, identifier scan and render tests for the stack-docs pack.

The checker and the identifier scan live in ``tests/stack_contract.py`` (decision D15). This file keeps the C2a tests
that exercise them against the stack-docs pack and against planted samples.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from stack_contract import (
    CONFORMING_SKILL,
    GUIDANCE_RULES,
    PACKS,
    SERVICE_RULES,
    VIOLATIONS,
    _table_body_rows,
    description_within_limit,
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


# --- Cross-pack helpers. Each one takes a packs folder, so a negative test can plant a violation in a copy. ---


def _stack_pack_dirs(root: Path) -> list[Path]:
    """Return every ``stack-*`` pack folder under ``root``, in name order."""
    return sorted(path for path in root.glob("stack-*") if path.is_dir())


def _stack_skill_files(root: Path) -> list[Path]:
    """Return every stack ``SKILL.md`` under ``root``, in path order."""
    return sorted(root.glob("stack-*/skills/*/SKILL.md"))


def _contract_problems(root: Path) -> list[str]:
    """Return ``path: rule`` for each service skill outside stack-docs under ``root`` that fails a service rule."""
    return [
        f"{path.relative_to(root).as_posix()}: {rule}"
        for path in _stack_skill_files(root)
        if path.relative_to(root).parts[0] != STACK_DOCS.name
        for rule in failed_rules(path.read_text(encoding="utf-8"), SERVICE_RULES)
    ]


def _description_problems(root: Path) -> list[str]:
    """Return ``path: description length`` for each stack skill under ``root`` whose description is too long."""
    return [
        f"{path.relative_to(root).as_posix()}: description length"
        for path in _stack_skill_files(root)
        if not description_within_limit(path.read_text(encoding="utf-8"))
    ]


def _identifier_problems(root: Path) -> list[str]:
    """Return ``pack/path: rule`` for each identifier hit in any stack pack under ``root``."""
    return [f"{pack.name}/{hit}" for pack in _stack_pack_dirs(root) for hit in identifier_hits_in_folder(pack)]


def _planted_bundle(tmp_path: Path, relative: str, text: str) -> Path:
    """Copy the packs folder into ``tmp_path``, replace the file at ``relative`` with ``text``, and return the copy."""
    planted = Path(shutil.copytree(PACKS, tmp_path / "packs"))
    (planted / relative).write_text(text, encoding="utf-8")
    return planted


# --- Cross-pack tests. Each happy path runs on the real bundle, and each negative path on a planted copy. ---


def test_every_stack_skill_passes_contract() -> None:
    assert _stack_skill_files(PACKS), "no stack skill found"
    assert _contract_problems(PACKS) == []


def test_planted_skill_breaks_cross_pack_contract(tmp_path: Path) -> None:
    planted = _planted_bundle(tmp_path, "stack-web/skills/chakra-ui/SKILL.md", VIOLATIONS["verified line present"])
    assert "stack-web/skills/chakra-ui/SKILL.md: verified line present" in _contract_problems(planted)


def test_stack_packs_name_no_project_identifier() -> None:
    assert _stack_pack_dirs(PACKS), "no stack pack found"
    assert _identifier_problems(PACKS) == []


@pytest.mark.parametrize(
    ("text", "rule"),
    [
        ("Host: https://abcd1234efgh5678.supabase.co/mcp\n", "supabase project host"),
        (f"Notes mention {'-'.join(NAME_WORDS)} in passing.\n", "sibling project name"),
    ],
    ids=["project-host", "sibling-name"],
)
def test_planted_identifier_fails_pack_scan(tmp_path: Path, text: str, rule: str) -> None:
    planted = _planted_bundle(tmp_path, "stack-python/skills/pydantic/SKILL.md", text)
    assert _identifier_problems(planted) == [f"stack-python/skills/pydantic/SKILL.md: {rule}"]


def test_every_stack_description_is_within_limit() -> None:
    assert _stack_skill_files(PACKS), "no stack skill found"
    assert _description_problems(PACKS) == []


def test_planted_long_description_fails_pack_limit(tmp_path: Path) -> None:
    planted = _planted_bundle(tmp_path, "stack-cloud/skills/render/SKILL.md", VIOLATIONS["description length"])
    assert _description_problems(planted) == ["stack-cloud/skills/render/SKILL.md: description length"]
