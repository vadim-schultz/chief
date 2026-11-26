"""Pack tests for the stack-python pack: declared skills, skill contract, identifier scan and docs claims."""

from __future__ import annotations

import shutil
from pathlib import Path

import tomllib
from test_stack_knowledge import SERVICE_RULES, failed_rules, identifier_hits_in_folder

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKS = REPO_ROOT / "src" / "chief" / "bundle" / "packs"
STACK_PYTHON = PACKS / "stack-python"
SKILLS = ("litestar", "sqlalchemy-alembic", "pydantic")
REQUIRED_PACK = "stack-docs"
PLUGIN_SPELLINGS = ("litestar-mcp", "litestar mcp")


def _existing_pack() -> Path:
    """Return the stack-python pack folder, failing when it is missing."""
    assert STACK_PYTHON.is_dir(), f"missing pack folder: {STACK_PYTHON}"
    return STACK_PYTHON


def _skill_file(pack_root: Path, name: str) -> Path:
    """Return the path of the ``SKILL.md`` of the skill ``name`` under ``pack_root``."""
    return pack_root / "skills" / name / "SKILL.md"


def _skill_text(name: str) -> str:
    """Return the text of the ``SKILL.md`` of the stack-python skill ``name``, failing unless it exists."""
    path = _skill_file(_existing_pack(), name)
    assert path.is_file(), f"missing skill file: {path}"
    return path.read_text(encoding="utf-8")


def _requires(pack_root: Path) -> list[str]:
    """Return the ``requires`` list of the ``pack.toml`` under ``pack_root``."""
    manifest = tomllib.loads((pack_root / "pack.toml").read_text(encoding="utf-8"))
    return list(manifest.get("requires", []))


def _missing_skills(pack_root: Path) -> list[str]:
    """Return the expected skills that have no ``SKILL.md`` under ``pack_root``."""
    return [name for name in SKILLS if not _skill_file(pack_root, name).is_file()]


def _requires_problems(pack_root: Path) -> list[str]:
    """Return a problem when the ``requires`` list of ``pack_root`` lacks ``REQUIRED_PACK``."""
    return [] if REQUIRED_PACK in _requires(pack_root) else [f"requires lacks {REQUIRED_PACK}"]


def _declaration_problems(pack_root: Path) -> list[str]:
    """Return one problem for each missing skill and for a missing ``stack-docs`` requirement."""
    if not pack_root.is_dir():
        return [f"missing pack folder: {pack_root}"]
    return [f"missing skill: {name}" for name in _missing_skills(pack_root)] + _requires_problems(pack_root)


def _mcp_values(text: str) -> list[str]:
    """Return the value of each ``MCP:`` line of ``text``, without its bullet."""
    bodies = (line.strip().removeprefix("- ") for line in text.splitlines())
    return [body.removeprefix("MCP:").strip() for body in bodies if body.startswith("MCP:")]


def test_stack_python_pack_declares_expected_skills() -> None:
    assert _declaration_problems(_existing_pack()) == []


def test_stack_python_declaration_check_flags_planted_missing_skill(tmp_path: Path) -> None:
    planted = tmp_path / "stack-python"
    shutil.copytree(_existing_pack(), planted)
    shutil.rmtree(planted / "skills" / "pydantic")
    assert _declaration_problems(planted) == ["missing skill: pydantic"]


def test_stack_python_pack_names_no_project_identifier() -> None:
    assert identifier_hits_in_folder(_existing_pack()) == []


def test_stack_python_skills_pass_contract() -> None:
    for name in SKILLS:
        assert failed_rules(_skill_text(name), SERVICE_RULES) == [], name


def _plugin_lines(text: str) -> list[str]:
    """Return each line of ``text`` that names the Litestar MCP plugin, in either spelling."""
    return [line for line in text.splitlines() if any(name in line.lower() for name in PLUGIN_SPELLINGS)]


def test_litestar_claims_no_official_docs_server() -> None:
    text = _skill_text("litestar")
    assert _mcp_values(text) == ["none verified"]
    plugin_lines = _plugin_lines(text)
    assert plugin_lines, "the skill should name the community plugin"
    assert all("not a documentation source" in line for line in plugin_lines)
