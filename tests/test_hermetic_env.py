"""Hermetic tool environment: ci.sh exports the settings that keep uv, pip and npm off the workstation config."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CI_SCRIPT = REPO_ROOT / "ci.sh"
PUBLIC_INDEX = "https://pypi.org/simple"
PLANTED_INDEX = "https://planted.invalid/simple"
EXPECTED_EXPORTS = {
    "UV_NO_CONFIG": "1",
    "UV_DEFAULT_INDEX": PUBLIC_INDEX,
    "PIP_CONFIG_FILE": "/dev/null",
    "NPM_CONFIG_USERCONFIG": "/dev/null",
}
INHERITED_PREFIXES = ("UV_", "PIP_", "NPM_CONFIG_", "XDG_")


def _ci_exports() -> dict[str, str]:
    """Return the ``export NAME=value`` assignments that ci.sh makes after ``set -euo pipefail``."""
    lines = CI_SCRIPT.read_text(encoding="utf-8").splitlines()
    start = lines.index("set -euo pipefail") + 1
    exports: dict[str, str] = {}
    for line in lines[start:]:
        if line.startswith("export "):
            name, _, value = line.removeprefix("export ").partition("=")
            exports[name] = value
    return exports


def _index_toml() -> str:
    """Return a uv configuration that makes the planted index the default."""
    return f'[[index]]\nurl = "{PLANTED_INDEX}"\ndefault = true\n'


def _inherited_environ() -> dict[str, str]:
    """Return the current environment without any uv, pip, npm or XDG setting, so only ci.sh settings apply."""
    return {name: value for name, value in os.environ.items() if not name.startswith(INHERITED_PREFIXES)}


def test_ci_exports_hermetic_env() -> None:
    exports = _ci_exports()

    for name, value in EXPECTED_EXPORTS.items():
        assert exports.get(name) == value, name


def test_uv_ignores_corporate_config(tmp_path: Path) -> None:
    home = tmp_path / "home"
    (home / ".config" / "uv").mkdir(parents=True)
    (home / ".config" / "uv" / "uv.toml").write_text(_index_toml(), encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()
    (project / "uv.toml").write_text(_index_toml(), encoding="utf-8")
    (project / "requirements.in").write_text("packaging\n", encoding="utf-8")
    env = {**_inherited_environ(), **_ci_exports(), "HOME": str(home)}

    result = subprocess.run(
        ["uv", "pip", "compile", "--emit-index-url", "--no-header", "requirements.in"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert PUBLIC_INDEX in result.stdout
    assert "planted.invalid" not in result.stdout
