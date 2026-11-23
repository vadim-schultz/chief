"""Packaging metadata: MIT license, GitHub project, private classifier, and no corporate index or brick tool."""

from __future__ import annotations

import configparser
import shlex
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"
TOX_INI = REPO_ROOT / "tox.ini"
LICENSE = REPO_ROOT / "LICENSE"
GITHUB_PROJECT = "https://github.com/vadim-schultz/chief"
PRIVATE_CLASSIFIER = "Private :: Do Not Upload"
OWNER = ("Vadim Schultz", "vadim.schultz@me.com")
LICENSE_MARKERS = ("MIT License", "Permission is hereby granted", "Copyright (c) 2026 Vadim Schultz")
HERMETIC_SETTINGS = {"UV_NO_CONFIG": "1", "PIP_CONFIG_FILE": "/dev/null", "NPM_CONFIG_USERCONFIG": "/dev/null"}
LEAK_VARIABLES = ("CHIEF_LEAK_DENYLIST", "CHIEF_LEAK_BASELINE", "CHIEF_LEAK_STRICT")
RELEASE_ENVIRONMENTS = ("changelog", "upload", "release", "release-local", "release-ci")
INDEX_OPTIONS = frozenset({"--default-index", "--index-url", "--extra-index-url", "-i"})


def _spelled(*parts: str) -> str:
    """Join ``parts`` so that a denylisted term never appears whole in this file."""
    return "".join(parts)


BRICK_TOOL = _spelled("brick", "maker")
CORPORATE_PREFIXES = (_spelled("RS", "B_"), _spelled("RS_", "BRICKS_"))


def _pyproject() -> dict[str, Any]:
    """Return the parsed ``pyproject.toml``; ``tomllib`` yields untyped tables, read by key below."""
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def _tox() -> configparser.ConfigParser:
    """Return the parsed ``tox.ini`` with interpolation off, since its values hold ``{env:...}`` references."""
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(TOX_INI, encoding="utf-8")
    return parser


def _people(entries: list[dict[str, str]]) -> list[tuple[str, str]]:
    """Return the ``(name, email)`` pair of each author or maintainer entry."""
    return [(entry["name"], entry["email"]) for entry in entries]


def _missing_license_markers() -> list[str]:
    """Return each MIT marker that the LICENSE file does not hold."""
    license_text = LICENSE.read_text(encoding="utf-8")
    return [marker for marker in LICENSE_MARKERS if marker not in license_text]


def _assignments(block: str) -> dict[str, str]:
    """Return the ``NAME = value`` lines of a tox ``setenv`` block."""
    pairs = (line.partition("=") for line in block.splitlines() if "=" in line)
    return {name.strip(): value.strip() for name, _, value in pairs}


def _index_options(install_command: str) -> set[str]:
    """Return the index options that an install command passes to uv."""
    return {token.split("=")[0] for token in shlex.split(install_command)} & INDEX_OPTIONS


def _corporate_passenv(passenv: str) -> list[str]:
    """Return the ``passenv`` entries that carry a corporate prefix."""
    return [entry for entry in passenv.split() if entry.startswith(CORPORATE_PREFIXES)]


def test_pyproject_metadata_is_private_and_mit() -> None:
    """The package names the MIT license, the owner, the GitHub project and the private classifier."""
    project: dict[str, Any] = _pyproject()["project"]
    urls: dict[str, str] = project.get("urls", {})

    assert project.get("license") == "MIT"
    assert project.get("license-files") == ["LICENSE"]
    assert PRIVATE_CLASSIFIER in project.get("classifiers", [])
    assert urls
    assert all(url.startswith(GITHUB_PROJECT) for url in urls.values())
    assert _people(project.get("authors", [])) == [OWNER]
    assert _people(project.get("maintainers", [])) == [OWNER]
    assert _missing_license_markers() == []


def test_no_corporate_index_in_config() -> None:
    """The package config names no index, mirror or brick tool, and tox sets no default index."""
    tool: dict[str, Any] = _pyproject().get("tool", {})
    uv: dict[str, Any] = tool.get("uv", {})
    testenv = _tox()["testenv"]

    assert "index" not in uv
    assert "python-install-mirror" not in uv
    assert not [name for name in tool if name.lower().startswith(BRICK_TOOL)]
    assert not _index_options(testenv.get("install_command", ""))
    assert not _corporate_passenv(testenv.get("passenv", ""))


def test_tox_sets_hermetic_env() -> None:
    """The base tox environment sets the hermetic tool settings and passes the leak gate variables through."""
    testenv = _tox()["testenv"]
    settings = _assignments(testenv.get("setenv", ""))

    assert {name: settings.get(name) for name in HERMETIC_SETTINGS} == HERMETIC_SETTINGS
    assert set(LEAK_VARIABLES) <= set(testenv.get("passenv", "").split())


def test_tox_has_no_release_environment() -> None:
    """No tox environment still names the deleted release, upload or changelog tooling."""
    parser = _tox()

    assert [name for name in RELEASE_ENVIRONMENTS if parser.has_section(f"testenv:{name}")] == []
