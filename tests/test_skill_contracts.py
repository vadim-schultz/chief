"""Contract tests for the skill texts of the work-package-create and work-package-check skills."""

from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parents[1] / "src/chief/bundle/packs/work-package/skills"


def read_skill(name: str) -> str:
    """Return the text of ``SKILL.md`` in the skill directory ``name``, failing unless the file exists."""
    path = SKILLS / name / "SKILL.md"
    assert path.is_file(), f"missing skill file: {path}"
    return path.read_text(encoding="utf-8")


def assert_skill_contains(text: str, phrase: str) -> None:
    """Assert that ``phrase`` is in ``text``."""
    assert phrase in text, f"missing phrase: {phrase!r}"


def assert_skill_lacks(text: str, phrase: str) -> None:
    """Assert that ``phrase`` is not in ``text``."""
    assert phrase not in text, f"unexpected phrase: {phrase!r}"


def write_copy(text: str, tmp_path: Path) -> str:
    """Write ``text`` to a copy in ``tmp_path``, and return the text read back from the copy."""
    copy = tmp_path / "SKILL.md"
    copy.write_text(text, encoding="utf-8")
    return copy.read_text(encoding="utf-8")


def copy_without(text: str, phrase: str, tmp_path: Path) -> str:
    """Return the text of a copy of ``text`` in ``tmp_path`` with every ``phrase`` removed."""
    return write_copy(text.replace(phrase, ""), tmp_path)


def test_create_skill_names_parallel_phases() -> None:
    text = read_skill("work-package-create")
    for phrase in ("Phase A", "Phase B", "parallel"):
        assert_skill_contains(text, phrase)


def test_create_skill_without_parallel_phases_fails(tmp_path: Path) -> None:
    text = read_skill("work-package-create")
    assert_skill_contains(text, "Phase A")
    copy = copy_without(text, "Phase A", tmp_path)
    with pytest.raises(AssertionError, match="Phase A"):
        assert_skill_contains(copy, "Phase A")


def test_create_skill_no_plan_branch_asks_for_feature_description() -> None:
    text = read_skill("work-package-create")
    for phrase in ("no plan file", "feature description", "chief-of-staff"):
        assert_skill_contains(text, phrase)


def test_no_plan_branch_missing_question_fails(tmp_path: Path) -> None:
    text = read_skill("work-package-create")
    assert_skill_contains(text, "feature description")
    copy = copy_without(text, "feature description", tmp_path)
    with pytest.raises(AssertionError, match="feature description"):
        assert_skill_contains(copy, "feature description")


def test_check_skill_never_fails_on_a_finding() -> None:
    text = read_skill("work-package-check")
    assert_skill_contains(text, "always reports")
    assert_skill_contains(text, "never stops on a normalised finding")
    assert_skill_lacks(text, "stop on error")


def test_check_skill_that_can_fail_is_rejected(tmp_path: Path) -> None:
    text = read_skill("work-package-check")
    copy = write_copy(text + "stop on error\n", tmp_path)
    with pytest.raises(AssertionError, match="stop on error"):
        assert_skill_lacks(copy, "stop on error")
