"""Declaration, identifier and contract tests for the stack-cloud pack.

The contract predicates and the identifier scan come from ``tests/stack_contract.py`` (chapter C2a, moved there in C3). This file
reuses them unchanged, so every stack pack meets one contract.
"""

from __future__ import annotations

import re
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path

import pytest
from stack_contract import (
    PACKS,
    SERVICE_RULES,
    VIOLATIONS,
    failed_rules,
    identifier_hits_in_folder,
    row_cites_source_or_none_verified,
    verified_lines_are_well_formed,
)
from test_sibling_name import NAME_WORDS

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

STACK_CLOUD = PACKS / "stack-cloud"
SKILLS = ("cloudflare", "render", "github-actions", "uptimerobot")
CLOUDFLARE_REFERENCES = ("workers-and-pages.md", "r2.md", "workers-ai.md", "browser-run.md")
CHECK_DATE = "2026-11-26"
VERIFIED_DATE = re.compile(r"Verified: (\d{4}-\d{2}-\d{2}) ")


# --- Readers. Each one returns plain data and holds no rule. ---


def _labelled(text: str, label: str) -> list[str]:
    """Return the lines of ``text`` that start with ``label`` after their spaces and any ``- `` bullet."""
    bodies = (line.strip().removeprefix("- ") for line in text.splitlines())
    return [body for body in bodies if body.startswith(label)]


def _is_verified(line: str) -> bool:
    """Return True when ``line`` is a ``Verified:`` line, bulleted or not."""
    return bool(_labelled(line, "Verified:"))


def _existing_pack() -> Path:
    """Return the stack-cloud pack folder, failing unless it exists."""
    assert STACK_CLOUD.is_dir(), f"missing pack folder: {STACK_CLOUD}"
    return STACK_CLOUD


def _skill_text(name: str) -> str:
    """Return the text of the stack-cloud skill ``name``, failing unless its ``SKILL.md`` exists."""
    path = STACK_CLOUD / "skills" / name / "SKILL.md"
    assert path.is_file(), f"missing skill file: {path}"
    return path.read_text(encoding="utf-8")


def _pack_files(root: Path) -> list[Path]:
    """Return every file under ``root``, in path order."""
    return sorted(path for path in root.rglob("*") if path.is_file())


def _requires(root: Path) -> list[str]:
    """Return the ``requires`` list of the ``pack.toml`` under ``root``."""
    with (root / "pack.toml").open("rb") as handle:
        requires: list[str] = tomllib.load(handle)["requires"]
    return requires


# --- Rules. Each one returns the problems that it finds, so an empty list passes. ---


def _declaration_problems(root: Path) -> list[str]:
    """Return one problem for each missing skill, missing Cloudflare reference or missing ``stack-docs`` requirement."""
    skills = root / "skills"
    problems = [f"missing skill: {name}" for name in SKILLS if not (skills / name / "SKILL.md").is_file()]
    references = skills / "cloudflare" / "reference"
    problems += [f"missing reference: {name}" for name in CLOUDFLARE_REFERENCES if not (references / name).is_file()]
    if "stack-docs" not in _requires(root):
        problems.append("pack does not require stack-docs")
    return problems


def _stale_dates(root: Path, check_date: str) -> list[str]:
    """Return ``path: date`` for each ``Verified:`` line under ``root`` that is dated before ``check_date``."""
    return [
        f"{path.relative_to(root).as_posix()}: {date}"
        for path in _pack_files(root)
        for date in VERIFIED_DATE.findall(path.read_text(encoding="utf-8"))
        if date < check_date
    ]


def _plant_skill(root: Path, text: str) -> None:
    """Write ``text`` as the demo skill under ``root``, for a negative-path test."""
    planted = root / "skills" / "demo" / "SKILL.md"
    planted.parent.mkdir(parents=True)
    planted.write_text(text, encoding="utf-8")


def _copy_pack(tmp_path: Path) -> Path:
    """Copy the stack-cloud pack into ``tmp_path`` and return the copy."""
    return Path(shutil.copytree(STACK_CLOUD, tmp_path / "stack-cloud"))


def _without_verified_lines(text: str) -> str:
    """Return ``text`` with every ``Verified:`` line removed."""
    kept: Iterable[str] = (line for line in text.splitlines() if not _is_verified(line))
    return "\n".join(kept) + "\n"


# --- Happy path: the real pack. ---


def test_stack_cloud_pack_declares_expected_skills() -> None:
    assert _declaration_problems(_existing_pack()) == []


def test_stack_cloud_pack_names_no_project_identifier() -> None:
    assert identifier_hits_in_folder(_existing_pack()) == []


@pytest.mark.parametrize("name", SKILLS)
def test_stack_cloud_skills_pass_contract(name: str) -> None:
    assert failed_rules(_skill_text(name), SERVICE_RULES) == []


def test_stack_cloud_docs_index_cites_source_or_none_verified() -> None:
    for name in SKILLS:
        lines = _labelled(_skill_text(name), "Docs index:")
        assert lines, f"{name}: no Docs index line"
        assert all(row_cites_source_or_none_verified(line) for line in lines), name


def test_stack_cloud_verified_lines_are_well_formed() -> None:
    for path in _pack_files(_existing_pack()):
        assert verified_lines_are_well_formed(path.read_text(encoding="utf-8")), path.name


def test_stack_cloud_verified_dates_are_not_older_than_check() -> None:
    assert _stale_dates(_existing_pack(), CHECK_DATE) == []


# --- Negative path: planted samples and planted copies. ---


def test_declaration_reports_missing_skill(tmp_path: Path) -> None:
    copy = _copy_pack(tmp_path)
    shutil.rmtree(copy / "skills" / "uptimerobot")
    assert "missing skill: uptimerobot" in _declaration_problems(copy)


def test_declaration_reports_missing_stack_docs_requirement(tmp_path: Path) -> None:
    copy = _copy_pack(tmp_path)
    (copy / "pack.toml").write_text('name = "stack-cloud"\ndescription = "Planted."\nrequires = []\n', encoding="utf-8")
    assert "pack does not require stack-docs" in _declaration_problems(copy)


def test_identifier_scan_flags_sibling_name_planted_in_pack(tmp_path: Path) -> None:
    _plant_skill(tmp_path, f"Notes mention {'-'.join(NAME_WORDS)} in passing.\n")
    assert identifier_hits_in_folder(tmp_path) != []


def test_contract_rejects_cloudflare_skill_without_verified_line() -> None:
    planted = _without_verified_lines(_skill_text("cloudflare"))
    assert "verified line present" in failed_rules(planted, SERVICE_RULES)


def test_docs_index_check_rejects_line_without_source() -> None:
    assert not row_cites_source_or_none_verified("Docs index: the vendor website")


def test_verified_line_check_rejects_bad_date() -> None:
    assert not verified_lines_are_well_formed(VIOLATIONS["verified lines well formed"])


def test_stale_verified_date_is_reported(tmp_path: Path) -> None:
    _plant_skill(tmp_path, "- Verified: 2026-01-01 https://docs.example.invalid/\n")
    assert _stale_dates(tmp_path, CHECK_DATE) == ["skills/demo/SKILL.md: 2026-01-01"]
