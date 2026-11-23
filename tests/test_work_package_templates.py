"""Contract tests for the work package templates of the work-package-create skill."""

import json
import re
from pathlib import Path

TEMPLATES = (
    Path(__file__).resolve().parents[1] / "src/chief/bundle/packs/work-package/skills/work-package-create/templates"
)
RELEASE_TEMPLATE = "release-chapter.md"
CHAPTER_BRANCH = re.compile(r"<CHAPTER BRANCH>|<chapterBranch>|-c\d{2}-")


def read_template(name: str) -> Path:
    """Return the path of template ``name``, failing unless the file exists."""
    path = TEMPLATES / name
    assert path.is_file(), f"missing template: {name}"
    return path


def copy_without(tmp_path: Path, name: str, marker: str) -> Path:
    """Copy template ``name`` into ``tmp_path``, dropping every line that starts with ``marker``."""
    lines = read_template(name).read_text(encoding="utf-8").splitlines(keepends=True)
    copy = tmp_path / name
    copy.write_text("".join(line for line in lines if not line.startswith(marker)), encoding="utf-8")
    return copy


def required_sections() -> dict[str, list[str]]:
    """Return the required markers of every template, keyed by template file name."""
    return json.loads((TEMPLATES / "required-sections.json").read_text(encoding="utf-8"))


def section_problems(path: Path) -> list[str]:
    """Return the missing and out-of-order markers of the template at ``path``."""
    lines = path.read_text(encoding="utf-8").splitlines()
    markers = required_sections()[path.name]
    return [*_missing(lines, markers), *_out_of_order(lines, markers)]


def _line_of(lines: list[str], marker: str) -> int | None:
    """Return the index of the first line that starts with ``marker``, or None."""
    return next((index for index, line in enumerate(lines) if line.startswith(marker)), None)


def _missing(lines: list[str], markers: list[str]) -> list[str]:
    """Return one ``missing`` problem for each marker with no line."""
    return [f"missing: {marker}" for marker in markers if _line_of(lines, marker) is None]


def _out_of_order(lines: list[str], markers: list[str]) -> list[str]:
    """Return one ``out of order`` problem for each marker that starts above an earlier marker."""
    problems: list[str] = []
    latest = -1
    for marker in markers:
        position = _line_of(lines, marker)
        if position is None:
            continue
        if position < latest:
            problems.append(f"out of order: {marker}")
        latest = max(latest, position)
    return problems


def test_chapter_template_has_ten_sections_in_order() -> None:
    assert section_problems(read_template("chapter.md")) == []


def test_chapter_template_missing_a_section_fails(tmp_path: Path) -> None:
    copy = copy_without(tmp_path, "chapter.md", "## Review gate")
    assert section_problems(copy) == ["missing: ## Review gate"]


def test_rollout_template_has_required_sections() -> None:
    assert section_problems(read_template("rollout.md")) == []


def test_rollout_template_missing_parallel_batches_fails(tmp_path: Path) -> None:
    copy = copy_without(tmp_path, "rollout.md", "## Parallel batches")
    assert section_problems(copy) == ["missing: ## Parallel batches"]


def test_remaining_templates_have_required_sections() -> None:
    for name in ("architecture.md", "gaps-and-decisions.md", "chapters-readme.md", "run-ledger.md"):
        assert section_problems(read_template(name)) == []


def test_ledger_template_without_final_gate_row_fails(tmp_path: Path) -> None:
    copy = copy_without(tmp_path, "run-ledger.md", "| Final gate |")
    assert section_problems(copy) == ["missing: | Final gate |"]


def chapter_branch_lines(text: str) -> list[str]:
    """Return each line of ``text`` that names a chapter branch, by placeholder or by a ``-cNN-`` branch name."""
    return [line for line in text.splitlines() if CHAPTER_BRANCH.search(line)]


def test_release_chapter_template_has_required_sections() -> None:
    path = read_template(RELEASE_TEMPLATE)
    assert section_problems(path) == []
    release_markers = required_sections()[RELEASE_TEMPLATE]
    missing = [marker for marker in required_sections()["chapter.md"] if marker not in release_markers]
    assert missing == [], f"release template lacks chapter sections: {missing}"


def test_release_chapter_template_forbids_chapter_branch() -> None:
    text = read_template(RELEASE_TEMPLATE).read_text(encoding="utf-8")
    assert chapter_branch_lines(text) == []
    assert chapter_branch_lines("Check out feat/private-distribution-c07-ci-policy\n"), (
        "a chapter branch must be flagged"
    )
