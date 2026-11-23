"""Check that the built wheel ships every pack and every ``pack.toml``."""

from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import NamedTuple

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PACKS = "chief/bundle/packs"


class WheelListing(NamedTuple):
    """Zip entry names of the built wheel and the pack names in the source tree."""

    entries: list[str]
    packs: list[str]


def missing_packs(entries: list[str], packs: list[str]) -> list[str]:
    """Return, in input order, each pack with no entry under the bundle packs folder."""
    return [pack for pack in packs if not _members_of(entries, pack)]


def packs_without_toml(entries: list[str], packs: list[str]) -> list[str]:
    """Return, in input order, each pack with no ``pack.toml`` entry."""
    return [pack for pack in packs if f"{BUNDLE_PACKS}/{pack}/pack.toml" not in _members_of(entries, pack)]


def _members_of(entries: list[str], pack: str) -> list[str]:
    """Return the entries under the folder of ``pack``."""
    prefix = f"{BUNDLE_PACKS}/{pack}/"
    return [entry for entry in entries if entry.startswith(prefix)]


@pytest.fixture(scope="module")
def built_wheel_listing(tmp_path_factory: pytest.TempPathFactory) -> WheelListing:
    """Build a wheel from a copy of the working tree and list its entries."""
    _require_tools("git", "uv")
    workdir = tmp_path_factory.mktemp("wheel")
    copy = _copy_working_tree(workdir / "source")
    wheel = _build_wheel(copy, workdir / "dist")
    return WheelListing(entries=_read_entries(wheel), packs=_pack_names(copy))


def _require_tools(*tools: str) -> None:
    """Fail, naming each tool that is not on PATH."""
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        pytest.fail(f"required tools missing from PATH: {', '.join(missing)}; install them and rerun")


def _copy_working_tree(dest: Path) -> Path:
    """Copy the files git lists as tracked or unignored into ``dest``, without ``.git``."""
    for rel in _listed_files():
        source = REPO_ROOT / rel
        if source.is_file():
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest / rel)
    return dest


def _listed_files() -> list[str]:
    """Return the repository paths that git lists as tracked or unignored."""
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if listed.returncode != 0:
        pytest.fail(f"git ls-files failed in {REPO_ROOT}: {listed.stderr}")
    return [rel for rel in listed.stdout.split("\0") if rel]


def _build_wheel(source: Path, dist: Path) -> Path:
    """Run ``uv build --wheel`` on ``source`` and return the wheel it writes to ``dist``."""
    env = {**os.environ, "SETUPTOOLS_SCM_PRETEND_VERSION": "0.0.0"}
    built = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(dist), str(source)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if built.returncode != 0:
        pytest.fail(f"uv build failed:\n{built.stdout}\n{built.stderr}")
    return next(dist.glob("*.whl"))


def _pack_names(source: Path) -> list[str]:
    """Return the sorted names of the pack folders in the copied source tree."""
    packs = sorted(p.name for p in (source / "src" / BUNDLE_PACKS).iterdir() if p.is_dir())
    if not packs:
        pytest.fail(f"no packs found under {BUNDLE_PACKS} in the source tree")
    return packs


def _read_entries(wheel: Path) -> list[str]:
    """Return the zip entry names of ``wheel``."""
    with zipfile.ZipFile(wheel) as archive:
        return archive.namelist()


def _write_wheel(path: Path, names: list[str]) -> Path:
    """Write an empty zip at ``path`` with one entry per name and return ``path``."""
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            archive.writestr(name, "")
    return path


def test_missing_pack_in_wheel_is_reported(tmp_path: Path) -> None:
    wheel = _write_wheel(
        tmp_path / "rsb.whl",
        [f"{BUNDLE_PACKS}/style/pack.toml", f"{BUNDLE_PACKS}/style/skills/technical-writing/SKILL.md"],
    )
    assert missing_packs(_read_entries(wheel), ["style", "mcp"]) == ["mcp"]


def test_pack_without_toml_in_wheel_is_reported(tmp_path: Path) -> None:
    wheel = _write_wheel(tmp_path / "rsb.whl", [f"{BUNDLE_PACKS}/mcp/skills/mcp-setup/SKILL.md"])
    assert packs_without_toml(_read_entries(wheel), ["mcp"]) == ["mcp"]


@pytest.mark.slow
def test_wheel_contains_every_pack(built_wheel_listing: WheelListing) -> None:
    listing = built_wheel_listing
    assert missing_packs(listing.entries, listing.packs) == []


@pytest.mark.slow
def test_wheel_contains_every_pack_toml(built_wheel_listing: WheelListing) -> None:
    listing = built_wheel_listing
    assert packs_without_toml(listing.entries, listing.packs) == []
