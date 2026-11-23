"""Tests for the ci-harness templates: the verdict on each fixture, and the tool check of each stage."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from test_ci_profiles import FIXTURES, SKILL_DIR, STAGE_TOOLS, Run, run_command

TEMPLATES = SKILL_DIR / "templates"
TEMPLATE_PROFILES = ("python",)


def _template_env(path: str | None = None) -> dict[str, str]:
    """Return the environment of one template run, with an optional PATH."""
    env = dict(os.environ)
    if path is not None:
        env["PATH"] = path
    return env


def _copy_fixture(profile: str, kind: str, tmp_path: Path) -> Path:
    """Copy one fixture into ``tmp_path`` and return the copy."""
    project = tmp_path / profile / kind
    shutil.copytree(FIXTURES / profile / kind, project)
    return project


def _shell_only_path(tmp_path: Path) -> str:
    """Return a PATH that holds only ``bash`` and ``env``, so that no stage tool resolves under it."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("bash", "env"):
        resolved = shutil.which(name)
        assert resolved is not None, f"{name} must exist on the test host"
        (bin_dir / name).symlink_to(resolved)
    return str(bin_dir)


def _run_template(profile: str, project: Path, *, path: str | None = None) -> Run:
    """Copy the template of ``profile`` to ``ci.sh`` in ``project`` and run it there."""
    script = project / "ci.sh"
    shutil.copy2(TEMPLATES / profile / "ci.sh", script)
    script.chmod(0o755)
    return run_command(["./ci.sh"], project, env=_template_env(path))


def test_python_planted_fixture_fails_harness(tmp_path: Path) -> None:
    project = _copy_fixture("python", "planted", tmp_path)
    result = _run_template("python", project)
    assert result.returncode != 0, result.output
    assert "ci: stage unit failed" in result.output, result.output
    assert "ci: stage build" not in result.output, result.output


@pytest.mark.parametrize("profile", TEMPLATE_PROFILES)
def test_each_clean_fixture_passes_harness(profile: str, tmp_path: Path) -> None:
    project = _copy_fixture(profile, "clean", tmp_path)
    result = _run_template(profile, project)
    assert result.returncode == 0, result.output


@pytest.mark.parametrize("profile", TEMPLATE_PROFILES)
def test_each_planted_fixture_fails_harness(profile: str, tmp_path: Path) -> None:
    project = _copy_fixture(profile, "planted", tmp_path)
    result = _run_template(profile, project)
    assert result.returncode != 0, result.output
    assert "ci: stage unit failed" in result.output, result.output
    assert "ci: stage build" not in result.output, result.output


@pytest.mark.parametrize("profile", TEMPLATE_PROFILES)
def test_present_tool_passes_stage(profile: str, tmp_path: Path) -> None:
    tool = STAGE_TOOLS[profile]
    project = _copy_fixture(profile, "clean", tmp_path)
    result = _run_template(profile, project)
    assert f"ci: tool {tool} found" in result.output, result.output
    assert "ci: stage lint" in result.output, result.output


@pytest.mark.parametrize("profile", TEMPLATE_PROFILES)
def test_missing_tool_fails_stage_with_message(profile: str, tmp_path: Path) -> None:
    tool = STAGE_TOOLS[profile]
    path = _shell_only_path(tmp_path)
    assert shutil.which(tool, path=path) is None, f"{tool} must not resolve under the test PATH"
    project = _copy_fixture(profile, "clean", tmp_path)
    result = _run_template(profile, project, path=path)
    assert result.returncode != 0, result.output
    assert f"ci: missing tool {tool}" in result.output, result.output
    assert "ci: stage lint" not in result.output, result.output
