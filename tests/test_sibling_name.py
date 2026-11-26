"""Keep the sibling project's name out of the shipped package under ``src/chief``."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = REPO_ROOT / "src" / "chief"
# The name is built from parts, so that this file never spells it out in one piece (decision D9).
NAME_WORDS = ("red", "tape")
NAME = re.compile("[-_]?".join(NAME_WORDS), re.IGNORECASE)
SPELLINGS = ("".join(NAME_WORDS).upper(), "-".join(NAME_WORDS), "_".join(NAME_WORDS).title())


@dataclass(frozen=True)
class Hit:
    """One line of a file under the scanned root that names the sibling project."""

    path: str
    line: int


def _name_hits(root: Path) -> list[Hit]:
    """Return each line under ``root`` that names the sibling project, in path and line order."""
    raise NotImplementedError


def test_shipped_package_names_no_sibling_project() -> None:
    """The shipped package names no sibling project in any case, with or without a separator."""
    assert _name_hits(PACKAGE) == []


@pytest.mark.parametrize("spelling", SPELLINGS, ids=["joined-upper", "hyphen-lower", "underscore-title"])
def test_planted_name_is_reported(tmp_path: Path, spelling: str) -> None:
    """A planted line that names the sibling project is reported with its file and line number."""
    (tmp_path / "notes.md").write_text(f"first line\nsee {spelling}\n", encoding="utf-8")

    assert _name_hits(tmp_path) == [Hit("notes.md", 2)]
