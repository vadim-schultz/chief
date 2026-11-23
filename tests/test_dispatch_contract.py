"""Contract tests for the argument dispatch table of the chief-of-staff skill."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from test_skill_contracts import assert_skill_contains, assert_skill_lacks

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE = REPO_ROOT / "src" / "chief" / "bundle" / "packs"
DISPATCH = BUNDLE / "orchestration" / "skills" / "chief-of-staff" / "dispatch.md"
AGENT = BUNDLE / "orchestration" / "agents" / "chapter-implementer.md"
HOST_WORKFLOW = BUNDLE / "orchestration" / "skills" / "chief-of-staff" / "host-workflow.md"
GIT_RULE = BUNDLE / "git" / "rules" / "git-workflow.md"
GH_COMMANDS = ("gh pr create", "gh pr checks", "gh pr merge", "gh pr view", "gh api")
SIZE_SCOPE = "The size rules apply to every language. The line counts are defaults."
PYTHON_SCOPE = "Scope: Python only."
GIT_SCOPE = "Scope: GitHub only. Conventional Commits apply in every language."
# The retired forge scope line is spelled in pieces so that this file does not flag itself under the leak gate.
FOREIGN_GIT_SCOPE = "Scope: " + "Git" + "Lab only."
LANGUAGES = ("Python", "TypeScript", "Rust", "C/C++", "Go")
NOTES = BUNDLE / "quality" / "skills" / "refactoring" / "reference" / "language-notes.md"
SCOPE_LINES: tuple[tuple[str, str], ...] = (
    ("quality/rules/tdd.md", "In compiled languages, a red test must compile before it fails."),
    ("quality/rules/refactor-step.md", SIZE_SCOPE),
    ("quality/rules/code-structure.md", SIZE_SCOPE),
    ("quality/rules/type-hinting.md", PYTHON_SCOPE),
    ("quality/rules/docstrings.md", PYTHON_SCOPE),
    ("git/rules/git-workflow.md", GIT_SCOPE),
)


def first_body_line(text: str) -> str:
    """Return the first non-empty line after the first heading of ``text``, or an empty string."""
    lines = text.splitlines()
    heading = next((index for index, line in enumerate(lines) if line.startswith("# ")), len(lines))
    return next((line for line in lines[heading + 1 :] if line.strip()), "")


def read_bundled(path: Path) -> str:
    """Return the text of a bundled file, failing with its path unless the file exists."""
    assert path.is_file(), f"missing bundled file: {path}"
    return path.read_text(encoding="utf-8")


def dispatch_row(marker: str) -> str:
    """Return the dispatch table row of ``DISPATCH`` that holds ``marker``."""
    rows = [line for line in read_bundled(DISPATCH).splitlines() if line.startswith("|") and marker in line]
    assert rows, f"no dispatch row for {marker!r} in {DISPATCH}"
    return rows[0]


def test_dispatch_work_package_branch_checks_then_executes() -> None:
    row = dispatch_row("@<work-package>")
    assert_skill_contains(row, "work-package-check")
    assert_skill_contains(row, "execute")
    assert row.index("work-package-check") < row.index("execute"), f"check must precede execution: {row}"


def test_dispatch_unknown_argument_asks_and_writes_nothing() -> None:
    row = dispatch_row("Unknown argument")
    assert_skill_contains(row, "clarify")
    assert_skill_contains(row, "write nothing")


def test_dispatch_plan_file_converts_then_waits() -> None:
    row = dispatch_row("@<plan-file>")
    for phrase in ("work-package-create", "summary", "confirmation"):
        assert_skill_contains(row, phrase)
    assert row.index("work-package-create") < row.index("summary") < row.index("confirmation"), f"wrong order: {row}"


def test_dispatch_plan_file_without_confirmation_starts_no_chapter() -> None:
    row = dispatch_row("@<plan-file>")
    assert_skill_contains(row, "no chapter runs before confirmation")


def test_dispatch_no_argument_starts_plan_first_with_refine_or_exit() -> None:
    row = dispatch_row("No argument")
    for phrase in ("plan-first", "CreatePlan", "refine", "exit"):
        assert_skill_contains(row, phrase)


def test_dispatch_no_argument_writes_nothing_before_acceptance() -> None:
    row = dispatch_row("No argument")
    assert_skill_contains(row, "writes nothing before the plan is accepted")


def test_preflight_text_names_c0_and_return_fields() -> None:
    text = read_bundled(AGENT)
    for phrase in ("./ci.sh unit", "clean checkout", "C0", "language", "profile", "harness", "toolchain"):
        assert_skill_contains(text, phrase)
    assert text.index("./ci.sh unit") < text.index("Use this order: Red"), "preflight must precede the Red step"


def test_preflight_missing_harness_text_is_rejected() -> None:
    text = read_bundled(AGENT)
    for phrase in ("stop and report that C0 must run first", "start no Red step"):
        assert_skill_contains(text, phrase)


def test_scope_lines_present_in_each_rule() -> None:
    for rule, phrase in SCOPE_LINES:
        assert_skill_contains(read_bundled(BUNDLE / rule), phrase)


def test_python_only_rules_state_python_scope() -> None:
    for rule in (rule for rule, phrase in SCOPE_LINES if phrase == PYTHON_SCOPE):
        assert first_body_line(read_bundled(BUNDLE / rule)) == PYTHON_SCOPE, rule


def assert_language_row(text: str, language: str) -> None:
    """Assert that ``text`` has a table row whose first cell is ``language``."""
    assert f"| {language} |" in text, f"missing language row: {language}"


def test_refactoring_language_notes_cover_five_languages() -> None:
    text = read_bundled(NOTES)
    for language in LANGUAGES:
        assert_language_row(text, language)


def test_refactoring_language_notes_missing_language_fails() -> None:
    text = read_bundled(NOTES)
    assert_language_row(text, "Go")
    without_go = "\n".join(line for line in text.splitlines() if not line.startswith("| Go |"))
    with pytest.raises(AssertionError, match="Go"):
        assert_language_row(without_go, "Go")


def test_host_workflow_names_each_gh_command() -> None:
    text = read_bundled(HOST_WORKFLOW)
    for command in GH_COMMANDS:
        assert_skill_contains(text, command)


def test_host_workflow_never_requests_projectcards() -> None:
    json_lines = [line for line in read_bundled(HOST_WORKFLOW).splitlines() if "--json" in line]
    assert json_lines, "host-workflow.md names no gh --json command"
    assert [line for line in json_lines if "projectCards" in line] == []


def test_dispatch_contract_names_github_scope() -> None:
    assert_skill_contains(read_bundled(GIT_RULE), GIT_SCOPE)


def test_git_rule_has_no_non_github_host_scope() -> None:
    assert_skill_lacks(read_bundled(GIT_RULE), FOREIGN_GIT_SCOPE)


LOCAL_GATE_RETURN = "local gate: <command> @ <sha>"
REMOTE_NOT_RUN = "remote ci: not run (policy)"
REMOTE_WAIT = re.compile(
    r"checks --watch|(?:wait|waits) for (?:the )?(?:(?:required|remote) )*(?:checks|remote CI)",
    re.IGNORECASE,
)
RELEASE_FILE = "release-chapter.md"
RELEASE_HEADING = "## Release"


def test_chapter_return_names_local_gate() -> None:
    text = read_bundled(AGENT)
    assert_skill_contains(text, LOCAL_GATE_RETURN)
    assert_skill_contains(text, REMOTE_NOT_RUN)


def _in_release_section(name: str, heading: str) -> bool:
    """Return True when a line under ``heading`` of the text file ``name`` belongs to the release section."""
    return name == RELEASE_FILE or heading.startswith(RELEASE_HEADING)


def _wait_problems(name: str, text: str) -> list[str]:
    """Return ``name:line`` for each line that waits for remote checks outside the release section."""
    problems: list[str] = []
    heading = ""
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            heading = line
        if REMOTE_WAIT.search(line) and not _in_release_section(name, heading):
            problems.append(f"{name}:{number}")
    return problems


def test_no_text_waits_for_remote_ci_per_chapter() -> None:
    problems: list[str] = []
    for path in sorted(BUNDLE.rglob("*.md")):
        problems.extend(_wait_problems(path.name, path.read_text(encoding="utf-8")))
    assert problems == [], f"texts wait for remote checks outside the release section: {problems}"
    assert _wait_problems("chapter.md", "## Git workflow\n- gh pr checks --watch\n"), "a chapter wait must be flagged"
