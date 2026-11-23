"""Tests for the CI scope: the GitHub workflows, the local gate they call, and the template profiles.

The workflows are read as text with the same line-based parsing as the other harness tests, so no YAML parser is needed.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import ModuleType

import test_ci_templates as templates
from test_ci_profiles import STAGE_TOOLS
from test_ci_templates import TEMPLATE_PROFILES

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
CI_WORKFLOW = WORKFLOWS / "ci.yml"
RELEASE_WORKFLOW = WORKFLOWS / "release.yml"
CI_SCRIPT = REPO_ROOT / "ci.sh"
MAIN_BRANCH = "main"
ALLOWED_TRIGGERS = frozenset({"pull_request", "push", "workflow_dispatch"})
FOREIGN_TOOLS = frozenset({"npx", "cargo", "clang-format"})
KEY_LINE = re.compile(r"^( *)([A-Za-z0-9_-]+):")
USES_LINE = re.compile(r"^\s*-?\s*uses:\s*(\S+)(.*)$")
ACTION_REF = re.compile(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}")
VERSION_COMMENT = re.compile(r"\s*#\s*v\d")
WRITE_LEVEL = re.compile(r":\s*write(-all)?\b")
RUN_MODE = re.compile(r"\./ci\.sh\s+(\w+)")
MODE_STAGES = re.compile(r'\[(\w+)\]="([^"]*)"')


def _workflow_text(path: Path) -> str:
    """Return the text of the workflow at ``path``, failing with its path unless the file exists."""
    assert path.is_file(), f"missing workflow: {path}"
    return path.read_text(encoding="utf-8")


def _workflows() -> dict[str, str]:
    """Return the text of each workflow of the repository, keyed by file name."""
    return {path.name: _workflow_text(path) for path in (CI_WORKFLOW, RELEASE_WORKFLOW)}


def _key_at(line: str, indent: int) -> str | None:
    """Return the key that ``line`` opens at ``indent`` spaces, or None when it opens no key there."""
    match = KEY_LINE.match(line)
    if match is None or len(match.group(1)) != indent:
        return None
    return match.group(2)


def _blocks_at(text: str, indent: int) -> dict[str, str]:
    """Map each key at ``indent`` spaces in ``text`` to the lines under it. Comment lines are skipped."""
    groups: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        key = _key_at(line, indent)
        if key is not None:
            current = key
            groups[key] = [line]
        elif current is not None:
            groups[current].append(line)
    return {key: "\n".join(lines) for key, lines in groups.items()}


def _top_level(text: str, key: str) -> str:
    """Return the text under the top-level ``key`` of a workflow, or an empty string when it has none."""
    return _blocks_at(text, 0).get(key, "")


def _triggers(text: str) -> dict[str, str]:
    """Map each trigger under ``on:`` to its body."""
    return _blocks_at(_top_level(text, "on"), 2)


def _jobs(text: str) -> dict[str, str]:
    """Map each job under ``jobs:`` to its body."""
    return _blocks_at(_top_level(text, "jobs"), 2)


def _top_permissions(text: str) -> dict[str, str]:
    """Map each scope under the top-level ``permissions:`` key to its level."""
    lines = _top_level(text, "permissions").splitlines()[1:]
    scopes = (line.strip().partition(":") for line in lines if line.strip())
    return {scope: level.strip() for scope, _, level in scopes}


def _inline_list(body: str, key: str) -> list[str] | None:
    """Return the items of the inline list ``key: [a, b]`` in ``body``, or None when ``body`` has no such list."""
    match = re.search(rf"\b{key}:\s*\[([^\]]*)\]", body)
    if match is None:
        return None
    return [item.strip().strip("\"'") for item in match.group(1).split(",") if item.strip()]


def _trigger_problems(name: str, text: str) -> list[str]:
    """Return one problem for each trigger outside the allowed set and each pull request or push with a wrong filter."""
    triggers = _triggers(text)
    problems = [f"{name}: trigger not allowed: {trigger}" for trigger in triggers if trigger not in ALLOWED_TRIGGERS]
    if "pull_request" in triggers and _inline_list(triggers["pull_request"], "branches") != [MAIN_BRANCH]:
        problems.append(f"{name}: pull_request must name branches: [{MAIN_BRANCH}]")
    if "push" in triggers:
        problems.extend(_push_problems(name, triggers["push"]))
    return problems


def _runs_on_all_branches(body: str) -> bool:
    """Return True when a push trigger body has no tag filter, so the push runs on every branch."""
    return _inline_list(body, "tags") is None


def _push_problems(name: str, body: str) -> list[str]:
    """Return the problems of a push trigger body that is not limited to tags."""
    problems: list[str] = []
    if _inline_list(body, "branches") is not None:
        problems.append(f"{name}: push must name only tags")
    if _runs_on_all_branches(body):
        problems.append(f"{name}: push trigger on all branches")
    return problems


def _wildcard_problems(name: str, text: str) -> list[str]:
    """Return one problem for each branch filter with a wildcard and each push trigger with no tag filter."""
    problems: list[str] = []
    for trigger, body in _triggers(text).items():
        branches = _inline_list(body, "branches") or []
        problems.extend(f"{name}: {trigger} branch wildcard: {branch}" for branch in branches if "*" in branch)
        if trigger == "push" and _runs_on_all_branches(body):
            problems.append(f"{name}: push trigger on all branches")
    return problems


def _pin_problem(name: str, ref: str, comment: str) -> str | None:
    """Return the problem of the action ``ref`` and its trailing ``comment``, or None when both are correct."""
    if not ACTION_REF.fullmatch(ref):
        return f"{name}: action not pinned to a commit SHA: {ref}"
    if not VERSION_COMMENT.match(comment):
        return f"{name}: no version comment after {ref}"
    return None


def _unpinned_uses(name: str, text: str) -> list[str]:
    """Return one problem for each ``uses:`` line with no 40-character commit SHA or no version comment."""
    matches = [match for match in map(USES_LINE.match, text.splitlines()) if match is not None]
    problems = [_pin_problem(name, match.group(1), match.group(2)) for match in matches]
    return [problem for problem in problems if problem is not None]


def _mode_stages() -> dict[str, frozenset[str]]:
    """Return the stage set of each mode that ``ci.sh`` declares."""
    declared = MODE_STAGES.findall(CI_SCRIPT.read_text(encoding="utf-8"))
    return {mode: frozenset(stages.split()) for mode, stages in declared}


def _job_problems(name: str, text: str, modes: dict[str, frozenset[str]]) -> list[str]:
    """Return one problem for each job that runs no ``./ci.sh`` mode, an unknown mode, or stages outside ``all``."""
    problems: list[str] = []
    for job, body in _jobs(text).items():
        called = RUN_MODE.findall(body)
        if not called:
            problems.append(f"{name}:{job} runs no ./ci.sh mode")
        problems.extend(_mode_problems(name, job, called, modes))
    return problems


def _mode_problems(name: str, job: str, called: list[str], modes: dict[str, frozenset[str]]) -> list[str]:
    """Return one problem for each called mode that is unknown or covers stages that ``all`` does not."""
    problems: list[str] = []
    for mode in called:
        if mode not in modes:
            problems.append(f"{name}:{job} runs unknown mode {mode}")
        elif not modes[mode] <= modes["all"]:
            problems.append(f"{name}:{job} runs stages outside ./ci.sh all: {mode}")
    return problems


def test_workflow_triggers_only_on_main_and_tags() -> None:
    workflows = _workflows()
    assert "pull_request" in _triggers(workflows["ci.yml"]), "ci.yml runs on the pull request into main"
    assert "push" in _triggers(workflows["release.yml"]), "release.yml runs on tags"
    problems = [problem for name, text in workflows.items() for problem in _trigger_problems(name, text)]
    assert problems == [], f"trigger problems: {problems}"


def test_workflow_has_no_branch_wildcard_trigger() -> None:
    for name, text in _workflows().items():
        assert _wildcard_problems(name, text) == [], f"{name} has a wildcard trigger"
    planted = 'on:\n  push:\n    branches: ["feat/**"]\n'
    assert _wildcard_problems("planted.yml", planted), "a wildcard branch filter must be flagged"


def test_workflow_token_is_read_only() -> None:
    workflows = _workflows()
    for name, text in workflows.items():
        assert _top_permissions(text) == {"contents": "read"}, f"{name} top-level token is not read-only"
    assert WRITE_LEVEL.search(workflows["ci.yml"]) is None, "ci.yml grants a write scope"
    assert "secrets." not in workflows["ci.yml"], "ci.yml must not read secrets"


def test_ci_pins_actions_to_sha() -> None:
    workflows = _workflows()
    assert any(USES_LINE.match(line) for line in workflows["ci.yml"].splitlines()), "ci.yml uses no action"
    problems = [problem for name, text in workflows.items() for problem in _unpinned_uses(name, text)]
    assert problems == [], f"unpinned actions: {problems}"
    assert _unpinned_uses("planted.yml", "      - uses: actions/checkout@v7 # v7\n"), "a tag ref must be flagged"


def test_remote_jobs_are_subset_of_local_gate() -> None:
    modes = _mode_stages()
    assert "./ci.sh all" in _jobs(_workflows()["ci.yml"]).get("gate", ""), "the gate job runs ./ci.sh all"
    problems = _job_problems(CI_WORKFLOW.name, _workflow_text(CI_WORKFLOW), modes)
    assert problems == [], f"remote jobs outside the local gate: {problems}"


def test_release_job_builds_without_gate() -> None:
    release = _jobs(_workflow_text(RELEASE_WORKFLOW))
    assert "tox -e build" in release.get("release", ""), "the release job builds the distributions"
    assert RUN_MODE.findall("\n".join(release.values())) == [], "the release job runs no ./ci.sh mode"


def test_unit_matrix_runs_nested_unit_stage() -> None:
    unit = _jobs(_workflows()["ci.yml"]).get("unit", "")
    assert _inline_list(unit, "python") == ["3.10", "3.14"], "the unit matrix covers Python 3.10 and 3.14"
    assert 'CI_HARNESS_NESTED: "1"' in unit, "the unit matrix excludes tests/ci"
    assert "./ci.sh unit" in unit and "./ci.sh all" not in unit


def test_template_profiles_are_python_only() -> None:
    assert TEMPLATE_PROFILES == ("python",)


def _parametrised_profiles(module: ModuleType) -> list[str]:
    """Return every ``profile`` value that a test function of ``module`` is parametrised over."""
    values: list[str] = []
    for item in vars(module).values():
        for mark in getattr(item, "pytestmark", []):
            if mark.name == "parametrize" and mark.args[0] == "profile":
                values.extend(mark.args[1])
    return values


def test_no_foreign_toolchain_is_run_by_templates() -> None:
    foreign = sorted({STAGE_TOOLS[profile] for profile in _parametrised_profiles(templates)} & FOREIGN_TOOLS)
    assert foreign == [], f"template tests still run foreign toolchains: {foreign}"
