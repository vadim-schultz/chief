"""Scrub checks for the quality, style and data packs: front matter, examples and third-party headings."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
from test_no_leaks import REPOSITORY_TERMS, denylist_path, local_terms

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKS = REPO_ROOT / "src" / "chief" / "bundle" / "packs"
SCRUBBED_PACKS = ("quality", "style", "data")
PUBLIC_AUTHOR = "human:vadim-schultz"
GENERATED_BY = re.compile(r'^generated: \{ by: "([^"]+)"', re.MULTILINE)
REFERENCE_FILES = (
    "data/skills/designing-data-systems/reference/local-stack.md",
    "data/skills/designing-data-systems/reference/rules-data.md",
    "data/skills/designing-data-systems/reference/rules-reads-ops.md",
    "data/skills/designing-data-systems/reference/rules-writes.md",
    "quality/skills/refactoring/reference/language-notes.md",
    "quality/skills/refactoring/reference/refactorings.md",
    "quality/skills/refactoring/reference/smells.md",
    "style/skills/asd-ste100/reference/reference.md",
    "style/skills/google-docguide/reference/reference.md",
    "style/skills/technical-writing/reference/provenance-map.md",
)
ASD_STE100 = PACKS / "style" / "skills" / "asd-ste100" / "reference" / "reference.md"
GOOGLE_DOCGUIDE = PACKS / "style" / "skills" / "google-docguide" / "reference" / "reference.md"
# Section sizes of ASD-STE100 Part 1, as cited by the provenance map.
ASD_SECTION_SIZES: dict[int, int] = {1: 14, 2: 2, 3: 7, 4: 5, 5: 5, 6: 6, 7: 3, 8: 7, 9: 4}
ASD_HEADING = re.compile(r"^### \[ste:(\d+\.\d+)\] ", re.MULTILINE)
GOOGLE_CITED_HEADINGS = ("Philosophy", "Best practices", "Markdown style", "README (layer guidance)")


def _authors(name: str) -> list[str]:
    """Return the author that each ``generated:`` line of the reference file ``name`` names."""
    return GENERATED_BY.findall((PACKS / name).read_text(encoding="utf-8"))


def _scrubbed_files() -> list[Path]:
    """Return the files of the scrubbed packs, in path order."""
    return sorted(path for pack in SCRUBBED_PACKS for path in (PACKS / pack).rglob("*") if path.is_file())


def _denylist_terms() -> tuple[str, ...]:
    """Return the denylist terms as the bundle contract reads them, minus the repository names."""
    return tuple(term for term in local_terms(denylist_path(os.environ)) if term not in REPOSITORY_TERMS)


def _file_hits(path: Path, pattern: re.Pattern[str]) -> list[str]:
    """Return ``pack/path:line`` for each line of ``path`` that ``pattern`` matches."""
    name = path.relative_to(PACKS).as_posix()
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return [f"{name}:{number}" for number, line in enumerate(lines, start=1) if pattern.search(line)]


def _term_hits(terms: tuple[str, ...]) -> list[str]:
    """Return ``pack/path:line`` for each line of the scrubbed packs that names one of ``terms``."""
    if not terms:
        return []
    pattern = re.compile("|".join(map(re.escape, terms)), re.IGNORECASE)
    return [hit for path in _scrubbed_files() for hit in _file_hits(path, pattern)]


@pytest.mark.parametrize("name", REFERENCE_FILES)
def test_reference_front_matter_uses_public_author(name: str) -> None:
    assert _authors(name) == [PUBLIC_AUTHOR]


def test_reference_files_name_no_other_author() -> None:
    misnamed = [name for name in REFERENCE_FILES if any(author != PUBLIC_AUTHOR for author in _authors(name))]
    assert misnamed == []


def test_bundled_examples_use_neutral_names() -> None:
    assert _term_hits(_denylist_terms()) == []
    assert _term_hits(REPOSITORY_TERMS) == []


def _heading_lines(path: Path) -> set[str]:
    """Return each line of ``path`` that starts with a Markdown heading marker."""
    return {line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("#")}


def test_example_scrub_keeps_third_party_rules() -> None:
    rule_ids = set(ASD_HEADING.findall(ASD_STE100.read_text(encoding="utf-8")))
    expected = {f"{section}.{rule}" for section, size in ASD_SECTION_SIZES.items() for rule in range(1, size + 1)}
    assert {"1.1", "4.1"} <= rule_ids
    assert sorted(expected - rule_ids) == []
    headings = _heading_lines(GOOGLE_DOCGUIDE)
    assert [title for title in GOOGLE_CITED_HEADINGS if f"## {title}" not in headings] == []
