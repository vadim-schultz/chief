"""Tests for the ci.sh harness: a clean unit run, a planted failure and the required tools."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_SCRIPT = REPO_ROOT / "ci.sh"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "planted-failure"


class UnitRun(NamedTuple):
    """Exit code and combined stdout and stderr of one nested ``./ci.sh unit`` run."""

    returncode: int
    output: str


def _assert_ci_script_ready() -> None:
    assert CI_SCRIPT.is_file(), f"ci.sh is missing at {CI_SCRIPT}"
    assert os.access(CI_SCRIPT, os.X_OK), "ci.sh is not executable"


def _run_unit(cwd: Path, tox_dir: Path, *, path: str | None = None) -> UnitRun:
    env = {**os.environ, "CI_HARNESS_NESTED": "1", "TOX_WORK_DIR": str(tox_dir)}
    if path is not None:
        env["PATH"] = path
    result = subprocess.run(["./ci.sh", "unit"], cwd=cwd, env=env, capture_output=True, text=True, check=False)
    return UnitRun(result.returncode, result.stdout + result.stderr)


def test_ci_clean_repo_passes(tmp_path: Path) -> None:
    _assert_ci_script_ready()
    run = _run_unit(REPO_ROOT, tmp_path / "tox")
    assert run.returncode == 0, run.output


def test_ci_planted_failure_exits_nonzero(tmp_path: Path) -> None:
    _assert_ci_script_ready()
    project = tmp_path / "project"
    (project / "tests").mkdir(parents=True)
    shutil.copy2(CI_SCRIPT, project / "ci.sh")
    shutil.copy2(FIXTURE_DIR / "tox.ini", project / "tox.ini")
    shutil.copy2(FIXTURE_DIR / "planted_failure.py", project / "tests" / "test_planted.py")
    run = _run_unit(project, tmp_path / "tox")
    assert run.returncode != 0, run.output
    assert "ci: stage unit failed" in run.output, run.output
    assert "test_planted_failure" in run.output, run.output


def test_ci_preflight_passes_with_tools_present(tmp_path: Path) -> None:
    _assert_ci_script_ready()
    run = _run_unit(REPO_ROOT, tmp_path / "tox")
    assert run.returncode == 0, run.output
    assert "ci: stage unit" in run.output, run.output
    assert "ci: missing tool" not in run.output, run.output


def test_ci_missing_tool_fails_with_message(tmp_path: Path) -> None:
    _assert_ci_script_ready()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("bash", "env"):
        resolved = shutil.which(tool)
        assert resolved is not None, f"{tool} must exist on the test host"
        (bin_dir / tool).symlink_to(resolved)
    path = str(bin_dir)
    assert shutil.which("uv", path=path) is None, "uv must not resolve under the test PATH"
    run = _run_unit(REPO_ROOT, tmp_path / "tox", path=path)
    assert run.returncode != 0, run.output
    assert "ci: missing tool uv" in run.output, run.output
