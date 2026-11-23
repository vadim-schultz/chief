"""Tests for the stdlib check script of the work-package-check skill."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "src/chief/bundle/packs/work-package/skills/work-package-check/scripts"
CHECK = SCRIPTS / "check_work_package.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "sample-work-package"
TEMPLATE_JSON = (
    REPO_ROOT / "src/chief/bundle/packs/work-package/skills/work-package-create/templates/required-sections.json"
)
REMOVED_HEADING = '"## Refactor report",'


def _copy_fixture(tmp_path: Path, name: str = "hello") -> Path:
    """Copy the sample work package fixture into ``tmp_path / name`` so that a test may change it."""
    return Path(shutil.copytree(FIXTURE, tmp_path / name))


def _repo_with_harness(tmp_path: Path) -> Path:
    """Create a repository root under ``tmp_path`` that holds a ``ci.sh`` file."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ci.sh").write_text("", encoding="utf-8")
    return repo


def _plant(folder: Path, name: str, text: str) -> None:
    """Append ``text`` to the file ``name`` in ``folder``, for a planted case."""
    with (folder / name).open("a", encoding="utf-8") as handle:
        handle.write(text)


def _drop_line(path: Path, prefix: str) -> None:
    """Remove every line of ``path`` that starts with ``prefix``, for a planted case."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    path.write_text("".join(line for line in lines if not line.startswith(prefix)), encoding="utf-8")


def _drop_closing_fence(path: Path) -> None:
    """Remove the closing ``---`` fence of the frontmatter of ``path``, for a planted case."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    closing = [index for index, line in enumerate(lines) if line.rstrip("\n") == "---"][1]
    del lines[closing]
    path.write_text("".join(lines), encoding="utf-8")


def _replace_frontmatter(path: Path, fields: list[str]) -> None:
    """Replace the field lines between the fences of ``path`` with ``fields``, for a planted case."""
    lines = path.read_text(encoding="utf-8").split("\n")
    end = lines.index("---", 1)
    path.write_text("\n".join(["---", *fields, *lines[end:]]), encoding="utf-8")


def _invoke(folder: Path, repo_root: Path) -> subprocess.CompletedProcess[str]:
    """Run the check script on ``folder`` without writing bytecode, and return the completed process."""
    return subprocess.run(
        [sys.executable, "-B", str(CHECK), str(folder), "--repo-root", str(repo_root)],
        capture_output=True,
        text=True,
        check=False,
    )


def _run(folder: Path, repo_root: Path) -> list[dict[str, Any]]:
    """Run the check on ``folder``, assert the exit code 0 and return the findings of the JSON report."""
    result = _invoke(folder, repo_root)
    assert result.stdout.strip(), f"script printed no report; stderr: {result.stderr}"
    assert result.returncode == 0, result.stderr
    findings: list[dict[str, Any]] = json.loads(result.stdout)["findings"]
    return findings


def _flags(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the findings whose severity is ``flag``."""
    return [finding for finding in findings if finding["severity"] == "flag"]


def test_hello_fixture_has_zero_flag_findings(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    assert [flag for flag in _flags(_run(folder, _repo_with_harness(tmp_path))) if flag["rule"] != "structure"] == []


def test_planted_broken_link_is_flagged(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    planted = "\nSee [notes](missing-note.md).\n"
    _plant(folder, "01-rollout.md", planted)
    before = (folder / "01-rollout.md").read_text(encoding="utf-8")

    flags = [flag for flag in _flags(_run(folder, _repo_with_harness(tmp_path))) if flag["rule"] == "links"]

    assert [(flag["rule"], flag["path"]) for flag in flags] == [("links", "01-rollout.md")]
    assert (folder / "01-rollout.md").read_text(encoding="utf-8") == before


def test_planted_missing_field_is_normalised(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    chapter = folder / "chapters" / "02-language-adapters.md"
    _drop_line(chapter, "execution:")

    findings = _run(folder, _repo_with_harness(tmp_path))

    assert "execution: chapter-implementer" in chapter.read_text(encoding="utf-8").splitlines()
    normalised = [f for f in findings if f["severity"] == "normalised" and f["rule"] == "frontmatter"]
    assert any("execution" in finding["message"] for finding in normalised)


def test_rollout_matrix_wins_on_conflict(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    chapter = folder / "chapters" / "02-language-adapters.md"
    _replace_frontmatter(
        chapter,
        ["id: C2", 'depends_on: ["C9"]', 'touches: ["x.py"]', "execution: chapter-implementer"],
    )
    _plant(folder, "chapters/02-language-adapters.md", "\n**Depends on:** C9\n")

    findings = _run(folder, _repo_with_harness(tmp_path))

    lines = chapter.read_text(encoding="utf-8").splitlines()
    assert 'depends_on: ["C1"]' in lines
    assert 'touches: ["src/hello/{adapters,registry}.py", "tests/{test_adapters,test_registry}.py"]' in lines
    assert "**Depends on:** C1" in lines
    rollout = [f for f in findings if f["severity"] == "normalised" and f["rule"] == "rollout"]
    assert len([f for f in rollout if f["path"] == "chapters/02-language-adapters.md"]) == 1


def _frontmatter_block(text: str) -> str:
    """Return the frontmatter of ``text``, from the opening fence through the closing fence."""
    lines = text.split("\n")
    return "\n".join(lines[: lines.index("---", 1) + 1])


def test_chapter_missing_from_rollout_matrix_is_flagged(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    _drop_line(folder / "01-rollout.md", "| C2 |")
    chapter = folder / "chapters" / "02-language-adapters.md"
    before = _frontmatter_block(chapter.read_text(encoding="utf-8"))

    findings = _run(folder, _repo_with_harness(tmp_path))

    flags = [(f["rule"], f["path"]) for f in _flags(findings) if f["rule"] == "rollout"]
    assert flags == [("rollout", "chapters/02-language-adapters.md")]
    assert _frontmatter_block(chapter.read_text(encoding="utf-8")) == before


def test_repo_without_harness_is_flagged_for_c0(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    empty_repo = tmp_path / "empty"
    empty_repo.mkdir()

    harness = [flag for flag in _flags(_run(folder, empty_repo)) if flag["rule"] == "harness"]

    assert [flag["path"] for flag in harness] == ["ci.sh"]
    assert "chapter C0 must be inserted first" in harness[0]["message"]


def test_repo_with_harness_is_not_flagged_for_c0(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    tox_repo = tmp_path / "tox-repo"
    tox_repo.mkdir()
    (tox_repo / "tox.ini").write_text("", encoding="utf-8")

    findings = _run(folder, tox_repo)

    assert [finding for finding in findings if finding["rule"] == "harness"] == []


def test_block_list_touches_is_normalised_not_flagged(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    chapter = "chapters/01-greeting-contract.md"

    findings = _run(folder, _repo_with_harness(tmp_path))

    assert [f for f in _flags(findings) if f["path"] == chapter and f["rule"] == "frontmatter"] == []
    rollout = [f for f in findings if f["severity"] == "normalised" and f["rule"] == "rollout" and f["path"] == chapter]
    assert len(rollout) == 1


def test_unparseable_frontmatter_is_flagged_not_crashed(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    chapter = folder / "chapters" / "01-greeting-contract.md"
    _drop_closing_fence(chapter)
    before = chapter.read_text(encoding="utf-8")

    findings = _run(folder, _repo_with_harness(tmp_path))

    frontmatter = [(f["rule"], f["path"]) for f in _flags(findings) if f["rule"] == "frontmatter"]
    assert frontmatter == [("frontmatter", "chapters/01-greeting-contract.md")]
    assert chapter.read_text(encoding="utf-8") == before


def test_script_prints_json_report_on_stdout(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    _plant(folder, "01-rollout.md", "\nSee [notes](missing-note.md).\n")

    result = _invoke(folder, _repo_with_harness(tmp_path))

    assert result.stdout.strip(), f"script printed no report; stderr: {result.stderr}"
    findings = json.loads(result.stdout)["findings"]
    assert findings
    for finding in findings:
        assert set(finding) == {"severity", "rule", "path", "message"}


def test_script_always_exits_zero(tmp_path: Path) -> None:
    repo = _repo_with_harness(tmp_path)
    link = _copy_fixture(tmp_path, "link")
    _plant(link, "01-rollout.md", "\nSee [notes](missing-note.md).\n")
    missing_field = _copy_fixture(tmp_path, "field")
    _drop_line(missing_field / "chapters" / "02-language-adapters.md", "execution:")
    unparseable = _copy_fixture(tmp_path, "fence")
    _drop_closing_fence(unparseable / "chapters" / "01-greeting-contract.md")
    no_row = _copy_fixture(tmp_path, "row")
    _drop_line(no_row / "01-rollout.md", "| C2 |")
    bare = tmp_path / "bare"
    bare.mkdir()
    for folder, repo_root in [(link, repo), (missing_field, repo), (unparseable, repo), (no_row, repo), (link, bare)]:
        result = _invoke(folder, repo_root)
        assert result.returncode == 0, result.stderr
        assert "findings" in json.loads(result.stdout)

    missing = _invoke(tmp_path / "absent", repo)
    assert missing.returncode == 0, missing.stderr
    assert [f["rule"] for f in _flags(json.loads(missing.stdout)["findings"])] == ["script"]

    unreadable = _copy_fixture(tmp_path, "bytes")
    (unreadable / "notes.md").write_bytes(b"\xff\xfe")
    result = _invoke(unreadable, repo)
    assert result.returncode == 0, result.stderr
    assert [f["rule"] for f in _flags(json.loads(result.stdout)["findings"])] == ["script"]


def _load_check_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Load the check script by file path, with its sibling modules importable."""
    monkeypatch.syspath_prepend(str(SCRIPTS))
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    spec = importlib.util.spec_from_file_location("check_work_package", CHECK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _chapter_headings(path: Path) -> list[str]:
    """Return the ``##`` headings of the chapter entry in a required-sections file."""
    entries: list[str] = json.loads(path.read_text(encoding="utf-8"))["chapter.md"]
    return [entry for entry in entries if entry.startswith("## ")]


def test_script_section_list_matches_required_sections(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_check_module(monkeypatch)
    expected = _chapter_headings(TEMPLATE_JSON)
    assert len(expected) == 10
    assert tuple(module.CHAPTER_SECTIONS) == tuple(expected)


def test_section_list_drift_is_detected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_check_module(monkeypatch)
    lines = TEMPLATE_JSON.read_text(encoding="utf-8").splitlines(keepends=True)
    drifted = tmp_path / "required-sections.json"
    drifted.write_text("".join(line for line in lines if line.strip() != REMOVED_HEADING), encoding="utf-8")

    copied = _chapter_headings(drifted)

    assert len(module.CHAPTER_SECTIONS) == 10
    assert tuple(module.CHAPTER_SECTIONS) != tuple(copied)


CHAPTER_FILES = ("01-greeting-contract.md", "02-language-adapters.md", "03-typer-cli.md")
UNKNOWN_CHAPTER_HEADINGS = [
    "## Boundaries",
    "## Red: write these tests first and confirm they fail",
    "## Green: minimum code",
    "## Refactor gate",
    "## Commit",
]


def _headings(text: str) -> list[str]:
    """Return the ``##`` heading lines of ``text``, in file order."""
    return [line for line in text.split("\n") if line.startswith("## ")]


def _move_section_to_end(path: Path, heading: str) -> None:
    """Move the section that starts with ``heading`` to the end of ``path``, for a planted case."""
    lines = path.read_text(encoding="utf-8").split("\n")
    start = lines.index(heading)
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    block = lines[start:end]
    del lines[start:end]
    path.write_text("\n".join([*lines, *block]), encoding="utf-8")


def test_missing_section_is_normalised_as_stub(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    template = _chapter_headings(TEMPLATE_JSON)
    missing = {
        name: [h for h in template if h not in _headings((folder / "chapters" / name).read_text(encoding="utf-8"))]
        for name in CHAPTER_FILES
    }
    findings = _run(folder, _repo_with_harness(tmp_path))

    for name, headings in missing.items():
        assert headings, "the fixture lacks some template sections"
        lines = (folder / "chapters" / name).read_text(encoding="utf-8").split("\n")
        for heading in headings:
            index = lines.index(heading)
            assert lines[index + 1] == "" and lines[index + 2].startswith("_") and lines[index + 2].endswith("_")
        present = [heading for heading in _headings("\n".join(lines)) if heading in template]
        assert present == [heading for heading in template if heading in present]
        stubs = [f for f in findings if f["severity"] == "normalised" and f["path"] == f"chapters/{name}"]
        assert len([f for f in stubs if f["rule"] == "structure"]) == len(headings)


def test_unknown_or_misplaced_section_is_flagged_and_kept(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    chapter = folder / "chapters" / "01-greeting-contract.md"
    _move_section_to_end(chapter, "## Goal")
    _plant(folder, "chapters/01-greeting-contract.md", "\n## Scratch notes\n\nKeep this note.\n")

    findings = _run(folder, _repo_with_harness(tmp_path))

    messages = [f["message"] for f in _flags(findings) if f["rule"] == "structure" and f["path"].endswith(chapter.name)]
    assert len([message for message in messages if "## Scratch notes" in message]) == 1
    assert len([message for message in messages if message.endswith("## Goal")]) == 1
    text = chapter.read_text(encoding="utf-8")
    for kept in ("## Scratch notes", "Keep this note.", "## Goal", "Write the greeting contract"):
        assert kept in text


def test_hello_fixture_structure_flags_are_the_unknown_headings(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    structure = [f for f in _flags(_run(folder, _repo_with_harness(tmp_path))) if f["rule"] == "structure"]

    assert {f["path"] for f in structure} == {f"chapters/{name}" for name in CHAPTER_FILES}
    for name in CHAPTER_FILES:
        messages = [f["message"] for f in structure if f["path"] == f"chapters/{name}"]
        assert messages == [f"unknown section: {heading}" for heading in UNKNOWN_CHAPTER_HEADINGS]


def test_link_with_unique_target_is_normalised(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    _plant(folder, "01-rollout.md", "\nSee [contract](wrong/01-greeting-contract.md).\n")

    findings = _run(folder, _repo_with_harness(tmp_path))

    text = (folder / "01-rollout.md").read_text(encoding="utf-8")
    assert "[contract](chapters/01-greeting-contract.md)" in text
    normalised = [f for f in findings if f["severity"] == "normalised" and f["rule"] == "links"]
    assert [f["path"] for f in normalised] == ["01-rollout.md"]


def test_link_with_two_targets_is_flagged(tmp_path: Path) -> None:
    folder = _copy_fixture(tmp_path)
    _plant(folder, "01-rollout.md", "\nSee [contract](wrong/01-greeting-contract.md).\n")
    (folder / "archive").mkdir()
    (folder / "archive" / "01-greeting-contract.md").write_text("# Archived\n", encoding="utf-8")
    before = (folder / "01-rollout.md").read_text(encoding="utf-8")

    findings = _run(folder, _repo_with_harness(tmp_path))

    flags = [f for f in _flags(findings) if f["rule"] == "links"]
    assert [f["path"] for f in flags] == ["01-rollout.md"]
    assert "chapters/01-greeting-contract.md" in flags[0]["message"]
    assert "archive/01-greeting-contract.md" in flags[0]["message"]
    assert (folder / "01-rollout.md").read_text(encoding="utf-8") == before


def _case_missing_execution(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Return the folder, the chapter without ``execution`` and a repository root, for an atomic-write case."""
    folder = _copy_fixture(tmp_path)
    chapter = folder / "chapters" / "02-language-adapters.md"
    _drop_line(chapter, "execution:")
    return folder, chapter, _repo_with_harness(tmp_path)


def test_normalised_write_replaces_file_atomically(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_check_module(monkeypatch)
    folder, chapter, repo = _case_missing_execution(tmp_path)
    destinations: list[Path] = []
    real_replace = os.replace

    def recording_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        destinations.append(Path(dst))
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", recording_replace)
    module.main([str(folder), "--repo-root", str(repo)])

    assert chapter in destinations
    assert "execution: chapter-implementer" in chapter.read_text(encoding="utf-8").splitlines()


def test_failed_write_leaves_original_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_check_module(monkeypatch)
    folder, chapter, repo = _case_missing_execution(tmp_path)
    original = chapter.read_text(encoding="utf-8")

    def failing_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        raise OSError(f"simulated failure replacing {dst}")

    monkeypatch.setattr(os, "replace", failing_replace)
    module.main([str(folder), "--repo-root", str(repo)])

    assert chapter.read_text(encoding="utf-8") == original
