"""Tests for the stack-web pack: its declared skills, the identifier scan, the skill contract and the Vite rule."""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

import pytest
from test_stack_knowledge import PACKS, SERVICE_RULES, failed_rules, identifier_hits_in_folder

STACK_WEB = PACKS / "stack-web"
EXPECTED_SKILLS = ("chakra-ui", "vite-react")


def _skill_text(pack_dir: Path, name: str) -> str:
    """Return the text of the ``SKILL.md`` of skill ``name`` in ``pack_dir``, failing unless it exists."""
    path = pack_dir / "skills" / name / "SKILL.md"
    assert path.is_file(), f"missing skill file: {path}"
    return path.read_text(encoding="utf-8")


def _missing_skills(pack_dir: Path) -> list[str]:
    """Return the names in ``EXPECTED_SKILLS`` that ``pack_dir`` ships no ``SKILL.md`` for."""
    present = {path.parent.name for path in (pack_dir / "skills").glob("*/SKILL.md")}
    return [name for name in EXPECTED_SKILLS if name not in present]


def _requires(pack_dir: Path) -> list[str]:
    """Return the ``requires`` list of the ``pack.toml`` in ``pack_dir``, failing unless the manifest exists."""
    manifest = pack_dir / "pack.toml"
    assert manifest.is_file(), f"missing pack manifest: {manifest}"
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    requires: list[str] = data["requires"]
    return requires


def test_stack_web_pack_declares_expected_skills() -> None:
    assert STACK_WEB.is_dir(), f"missing pack folder: {STACK_WEB}"
    assert _missing_skills(STACK_WEB) == []
    assert "stack-docs" in _requires(STACK_WEB)


def test_stack_web_declaration_reports_a_removed_skill(tmp_path: Path) -> None:
    assert STACK_WEB.is_dir(), f"missing pack folder: {STACK_WEB}"
    planted = tmp_path / "stack-web"
    shutil.copytree(STACK_WEB, planted)
    shutil.rmtree(planted / "skills" / "vite-react")
    assert _missing_skills(planted) == ["vite-react"]


def test_stack_web_pack_names_no_project_identifier() -> None:
    assert STACK_WEB.is_dir(), f"missing pack folder: {STACK_WEB}"
    assert identifier_hits_in_folder(STACK_WEB) == []


@pytest.mark.parametrize("name", EXPECTED_SKILLS)
def test_stack_web_skills_pass_contract(name: str) -> None:
    assert failed_rules(_skill_text(STACK_WEB, name), SERVICE_RULES) == []


def test_vite_rules_warn_about_public_env_vars() -> None:
    lines = _skill_text(STACK_WEB, "vite-react").splitlines()
    assert any("VITE_" in line and "public" in line and "browser" in line for line in lines)
    assert any("VITE_" in line and "secret" in line for line in lines)
