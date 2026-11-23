"""Tests for the ci-harness skill: profile detection, and the shared fixture and command helpers."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import pytest

# The stage tool of each profile is the first command word of its stage 1 (format).
STAGE_TOOLS = {"python": "ruff", "typescript": "npx", "rust": "cargo", "c-cpp": "clang-format"}
PROFILES = tuple(STAGE_TOOLS)
REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "src" / "chief" / "bundle" / "packs" / "quality" / "skills" / "ci-harness"
DETECT_SCRIPT = SKILL_DIR / "scripts" / "detect_profile.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "languages"


class Run(NamedTuple):
    """Exit code, stdout, and stdout plus stderr of one command."""

    returncode: int
    stdout: str
    output: str


def run_command(argv: list[str], cwd: Path, *, env: dict[str, str] | None = None, timeout: float | None = None) -> Run:
    """Run ``argv`` in ``cwd`` and capture its output. A timeout kills the whole process group."""
    with subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    ) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate()
            raise
    return Run(proc.returncode, stdout, stdout + stderr)


def _detect(root: Path) -> Run:
    """Run the detection script on ``root``."""
    return run_command([sys.executable, str(DETECT_SCRIPT), str(root)], REPO_ROOT)


def test_python_fixture_detects_python_profile() -> None:
    result = _detect(FIXTURES / "python" / "clean")
    assert result.stdout.strip() == "python", result.output
    assert result.returncode == 0, result.output


FIXTURE_CASES = [(profile, kind) for profile in PROFILES for kind in ("clean", "planted")]


@pytest.mark.parametrize(("profile", "kind"), FIXTURE_CASES)
def test_each_language_fixture_detects_its_profile(profile: str, kind: str) -> None:
    result = _detect(FIXTURES / profile / kind)
    assert result.stdout.strip() == profile, result.output
    assert result.returncode == 0, result.output


def test_empty_directory_detects_no_profile(tmp_path: Path) -> None:
    result = _detect(tmp_path)
    assert result.returncode != 0, result.output
    assert result.stdout.strip() == "no profile", result.output
