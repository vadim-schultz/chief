"""Tests for the stack-data-services pack: its declared skills, its requires, its identifiers and its contract.

The contract predicates and the identifier scan come from the C2a checker, now in ``stack_contract`` (moved there in C3). This file
reuses them unchanged.
"""

import shutil
from pathlib import Path

from stack_contract import PACKS, SERVICE_RULES, failed_rules, identifier_hits_in_folder

from chief.catalogue.packs import PackCatalogue

PACK = PACKS / "stack-data-services"
SKILLS = ("supabase", "azure-translator")
REQUIRED_PACK = "stack-docs"
UNVERIFIED_MCP_LINE = "- MCP: none verified"
FORBIDDEN_MCP_STATUSES = ("MCP: official", "MCP: community")


def _assert_pack_exists() -> None:
    """Fail with a clear message unless the pack folder exists."""
    assert PACK.is_dir(), f"missing pack folder: {PACK}"


def _skill_file(pack: Path, name: str) -> Path:
    """Return the path of the ``SKILL.md`` of the skill ``name`` in ``pack``."""
    return pack / "skills" / name / "SKILL.md"


def _skill_text(name: str) -> str:
    """Return the text of the ``SKILL.md`` of the pack skill ``name``, failing unless the file exists."""
    path = _skill_file(PACK, name)
    assert path.is_file(), f"missing skill file: {path}"
    return path.read_text(encoding="utf-8")


def _missing_skills(pack: Path) -> list[str]:
    """Return the names of the expected skills that ``pack`` does not ship, in ``SKILLS`` order."""
    return [name for name in SKILLS if not _skill_file(pack, name).is_file()]


def _pack_problems(pack: Path) -> list[str]:
    """Return one problem line for each missing skill and for a missing ``stack-docs`` requirement."""
    requires = PackCatalogue.load(pack.parent).packs[pack.name].requires
    problems = [f"missing skill: {name}" for name in _missing_skills(pack)]
    if REQUIRED_PACK not in requires:
        problems.append(f"missing requires: {REQUIRED_PACK}")
    return problems


def test_stack_data_services_pack_declares_expected_skills() -> None:
    """The pack ships both service skills and requires the stack-docs pack."""
    _assert_pack_exists()
    assert _pack_problems(PACK) == []


def _planted_pack(tmp_path: Path) -> Path:
    """Copy the pack into ``tmp_path`` and return the copy, failing unless the real pack exists."""
    _assert_pack_exists()
    planted = tmp_path / "packs" / PACK.name
    shutil.copytree(PACK, planted)
    return planted


def test_pack_missing_a_skill_is_reported(tmp_path: Path) -> None:
    """A planted copy with the azure-translator skill removed is reported as missing that skill."""
    planted = _planted_pack(tmp_path)
    shutil.rmtree(planted / "skills" / "azure-translator")
    assert "missing skill: azure-translator" in _pack_problems(planted)


def test_pack_without_stack_docs_requirement_is_reported(tmp_path: Path) -> None:
    """A planted copy whose pack.toml drops the stack-docs requirement is reported."""
    planted = _planted_pack(tmp_path)
    (planted / "pack.toml").write_text(
        'name = "stack-data-services"\ndescription = "Planted copy."\nrequires = []\n',
        encoding="utf-8",
    )
    assert f"missing requires: {REQUIRED_PACK}" in _pack_problems(planted)


def test_stack_data_services_pack_names_no_project_identifier() -> None:
    """The identifier scan finds no project host, token value or sibling project name in the pack."""
    _assert_pack_exists()
    assert identifier_hits_in_folder(PACK) == []


def test_stack_data_services_skills_pass_contract() -> None:
    """Each skill of the pack meets every service-skill rule of the C2a checker."""
    for name in SKILLS:
        assert failed_rules(_skill_text(name), SERVICE_RULES) == [], name


def test_azure_translator_names_no_unverified_server() -> None:
    """The azure-translator skill states MCP: none verified and names no third-party listing as official."""
    text = _skill_text("azure-translator")
    assert UNVERIFIED_MCP_LINE in text.splitlines()
    assert [status for status in FORBIDDEN_MCP_STATUSES if status in text] == []
