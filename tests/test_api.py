"""Library facade: ``ChiefOfStaff`` answers from the packs and locations it is given, and returns data."""

from collections.abc import Callable
from pathlib import Path

import pytest

import chief
from chief import api
from chief.api import ChiefOfStaff
from chief.catalogue.bundle_tree import BundleTree, Tree
from chief.catalogue.packs import BUNDLED_PACKS
from chief.targets import names
from chief.targets.locations import Locations
from chief.targets.registry import UnknownTargetError


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point HOME and both XDG roots at folders under ``tmp_path``."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    return tmp_path


def _write_pack(packs_dir: Path, name: str) -> None:
    """Write a minimal ``pack.toml`` for a pack named ``name`` under ``packs_dir``."""
    folder = packs_dir / name
    folder.mkdir(parents=True)
    (folder / "pack.toml").write_text(f'name = "{name}"\ndescription = "Test pack."\nrequires = []\n', encoding="utf-8")


def _tree_with(path: Path) -> Callable[[BundleTree, str], Tree]:
    """Return a stand-in for ``BundleTree.build`` that renders one file, at ``path``, for any target."""
    return lambda _bundle, _target: Tree(((path, "{}\n"),), ())


def _cursor_skill(isolated_home: Path) -> Path:
    """Return the path of the first bundled cursor skill, under the isolated home."""
    name = sorted(path.parent.name for path in BUNDLED_PACKS.glob("*/skills/*/SKILL.md"))[0]
    return isolated_home / "home" / ".cursor" / "skills" / name / "SKILL.md"


def _edit(path: Path) -> None:
    """Overwrite ``path`` with edited text, creating its folder first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("edited\n", encoding="utf-8")


def test_facade_lists_packs_from_injected_bundle(tmp_path: Path) -> None:
    packs_dir = tmp_path / "packs"
    _write_pack(packs_dir, "demo")
    facade = ChiefOfStaff(packs_dir, Locations())
    assert [pack.name for pack in facade.packs()] == ["demo"]


def test_facade_has_pack_reports_only_bundled_packs(tmp_path: Path) -> None:
    packs_dir = tmp_path / "packs"
    _write_pack(packs_dir, "demo")
    facade = ChiefOfStaff(packs_dir, Locations())
    assert facade.has_pack("demo")
    assert not facade.has_pack("missing")


def test_facade_refuses_unknown_target() -> None:
    facade = ChiefOfStaff(BUNDLED_PACKS, Locations())
    with pytest.raises(UnknownTargetError):
        facade.install("no-such-target", dry_run=True)


def test_api_has_no_mcp_snippet_method() -> None:
    """The facade holds no MCP snippet method once the corporate code is removed."""
    assert not hasattr(ChiefOfStaff, "mcp_snippet")


def test_facade_install_returns_plans_without_writing_in_dry_run(isolated_home: Path) -> None:
    plans = ChiefOfStaff(BUNDLED_PACKS, Locations()).install("cursor", dry_run=True)
    assert [plan.target for plan in plans] == ["cursor"]
    assert any(action.kind == "write" for action in plans[0].actions)
    assert not any(path.is_file() for path in isolated_home.rglob("*"))


def test_install_still_refuses_mcp_config_paths(isolated_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mcp_config = isolated_home / "home" / "mcp.json"
    monkeypatch.setattr(BundleTree, "build", _tree_with(mcp_config))
    plans = ChiefOfStaff(BUNDLED_PACKS, Locations()).install("cursor")
    kinds = [action.kind for plan in plans for action in plan.actions if action.path == mcp_config]
    assert kinds == ["refuse"]
    assert not any(path.is_file() for path in isolated_home.rglob("*"))


def test_facade_doctor_reports_edited_file_as_drift(isolated_home: Path) -> None:
    facade = ChiefOfStaff(BUNDLED_PACKS, Locations())
    facade.install("cursor")
    skill = _cursor_skill(isolated_home)
    _edit(skill)
    expected = skill.relative_to(isolated_home / "home" / ".cursor").as_posix()
    assert facade.doctor("cursor") == {"cursor": [expected]}


def test_facade_doctor_reports_no_drift_after_clean_install(isolated_home: Path) -> None:
    facade = ChiefOfStaff(BUNDLED_PACKS, Locations())
    facade.install("cursor")
    assert facade.doctor("cursor") == {"cursor": []}


def test_facade_uninstall_removes_tracked_files(isolated_home: Path) -> None:
    facade = ChiefOfStaff(BUNDLED_PACKS, Locations())
    facade.install("cursor")
    skill = _cursor_skill(isolated_home)
    results = facade.uninstall("cursor")
    assert len(results) == 1
    assert not skill.exists()


def test_facade_uninstall_keeps_edited_file(isolated_home: Path) -> None:
    facade = ChiefOfStaff(BUNDLED_PACKS, Locations())
    facade.install("cursor")
    skill = _cursor_skill(isolated_home)
    _edit(skill)
    results = facade.uninstall("cursor")
    assert len(results) == 1
    assert skill in results[0].refused
    assert skill.read_text(encoding="utf-8") == "edited\n"


def test_bundled_facade_lists_the_bundled_packs() -> None:
    facade = ChiefOfStaff.bundled()
    bundled = {path.parent.name for path in BUNDLED_PACKS.glob("*/pack.toml")}
    assert {pack.name for pack in facade.packs()} == bundled
    assert facade.has_pack("work-package")


def test_bundled_facade_refuses_an_unknown_pack() -> None:
    facade = ChiefOfStaff.bundled()
    assert not facade.has_pack("no-such-pack")
    assert "no-such-pack" not in [pack.name for pack in facade.packs()]


class _FixedLocations(Locations):
    """Locations that root every target beneath one folder, so the facade's injected source is observable."""

    def __init__(self, root: Path) -> None:
        """Remember the folder that every config root is joined under."""
        self._root = root

    def config_root(self, target: str) -> Path:
        """Return the fixed root joined with ``target``."""
        return self._root / target


def test_roots_follow_the_injected_locations(tmp_path: Path) -> None:
    default = ChiefOfStaff(BUNDLED_PACKS, Locations()).roots()
    assert default["opencode"] == tmp_path / "config" / "opencode"
    injected = ChiefOfStaff(BUNDLED_PACKS, _FixedLocations(tmp_path / "injected")).roots()
    assert injected["opencode"] == tmp_path / "injected" / "opencode"


def test_roots_name_only_concrete_targets() -> None:
    roots = ChiefOfStaff(BUNDLED_PACKS, Locations()).roots()
    assert set(roots) == {"cursor", "claude", "opencode", "vscode"}
    assert "all" not in roots


def test_api_exposes_target_and_version() -> None:
    assert api.Target is names.Target
    assert api.__version__ == chief.__version__


def test_api_all_lists_only_the_public_names() -> None:
    assert api.__all__ == ("ChiefOfStaff", "Target", "__version__")
    assert not {"_names", "_folders"} & set(api.__all__)
