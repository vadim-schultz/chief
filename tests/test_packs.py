import json
from pathlib import Path

import pytest

import chief
from chief.catalogue.bundle_tree import BundleTree
from chief.catalogue.packs import PackCatalogue, PackError
from chief.installation.installer import Installer
from chief.installation.manifest import ManifestStore
from chief.rendering.artifacts import UnknownTokenError
from chief.targets.locations import Locations

REAL_PACKS = Path(chief.__file__).parent / "bundle" / "packs"
ALL_PACKS = {"style", "quality", "git", "data", "work-package", "orchestration"}


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point HOME and both XDG roots at folders under ``tmp_path``."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    return tmp_path


def _write_bundle(root: Path, requires: dict[str, list[str]]) -> Path:
    """Write one ``pack.toml`` per entry under ``root/packs`` and return that folder."""
    packs_dir = root / "packs"
    for name, pack_requires in requires.items():
        pack_dir = packs_dir / name
        pack_dir.mkdir(parents=True)
        manifest = f'name = "{name}"\ndescription = "test pack"\nrequires = {json.dumps(pack_requires)}\n'
        (pack_dir / "pack.toml").write_text(manifest, encoding="utf-8")
    return packs_dir


def _demo_bundle(root: Path, support: str) -> Path:
    """Write a one-pack bundle whose skill ships a support file beside ``SKILL.md``."""
    pack = root / "demo"
    (pack / "skills" / "demo").mkdir(parents=True)
    (pack / "pack.toml").write_text('name = "demo"\ndescription = "Demo pack."\nrequires = []\n', encoding="utf-8")
    skill = "---\nname: demo\ndescription: Demo skill.\n---\n\nBody.\n"
    (pack / "skills" / "demo" / "SKILL.md").write_text(skill, encoding="utf-8")
    (pack / "skills" / "demo" / "reference.md").write_text(support, encoding="utf-8")
    return root


def test_orchestration_closure_resolves() -> None:
    closure = PackCatalogue.load(REAL_PACKS).closure(["orchestration"])
    assert set(closure) == {"style", "quality", "git", "data", "work-package", "orchestration"}


def test_all_remaining_packs_resolve() -> None:
    """Every pack in ALL_PACKS exists in the bundle, and each one's requires closure resolves inside it."""
    catalogue = PackCatalogue.load(REAL_PACKS)
    assert set(catalogue.packs) == ALL_PACKS
    for name in sorted(ALL_PACKS):
        assert set(catalogue.closure([name])) <= ALL_PACKS


def test_missing_requires_raises_pack_error(tmp_path: Path) -> None:
    packs_dir = _write_bundle(tmp_path, {"alpha": ["ghost"]})
    with pytest.raises(PackError, match="ghost"):
        PackCatalogue.load(packs_dir).closure(["alpha"])


def test_real_bundle_has_no_cycle() -> None:
    catalogue = PackCatalogue.load(REAL_PACKS)
    order = catalogue.check_graph()
    assert set(order) == ALL_PACKS
    position = {name: index for index, name in enumerate(order)}
    for name, pack in catalogue.packs.items():
        for required in pack.requires:
            assert position[required] < position[name]


def test_cycle_raises_pack_error(tmp_path: Path) -> None:
    packs_dir = _write_bundle(tmp_path, {"alpha": ["beta"], "beta": ["alpha"]})
    with pytest.raises(PackError, match="alpha.*beta"):
        PackCatalogue.load(packs_dir).closure(["alpha"])


def test_check_graph_reports_every_missing_target(tmp_path: Path) -> None:
    packs_dir = _write_bundle(tmp_path, {"alpha": ["ghost-one"], "beta": ["ghost-two"]})
    with pytest.raises(PackError) as error:
        PackCatalogue.load(packs_dir).check_graph()
    assert "ghost-one" in str(error.value)
    assert "ghost-two" in str(error.value)


def test_check_graph_reports_every_cycle(tmp_path: Path) -> None:
    packs_dir = _write_bundle(tmp_path, {"alpha": ["beta"], "beta": ["alpha"], "gamma": ["delta"], "delta": ["gamma"]})
    with pytest.raises(PackError) as error:
        PackCatalogue.load(packs_dir).check_graph()
    assert "alpha -> beta -> alpha" in str(error.value)
    assert "delta -> gamma -> delta" in str(error.value)


def test_check_graph_reports_cycles_that_share_a_pack(tmp_path: Path) -> None:
    packs_dir = _write_bundle(tmp_path, {"alpha": ["beta", "gamma"], "beta": ["gamma"], "gamma": ["alpha"]})
    with pytest.raises(PackError) as error:
        PackCatalogue.load(packs_dir).check_graph()
    assert "alpha -> beta -> gamma -> alpha" in str(error.value)
    assert "alpha -> gamma -> alpha" in str(error.value)


def test_bundle_tree_reads_injected_packs_dir(isolated_home: Path, tmp_path: Path) -> None:
    packs_dir = _write_bundle(tmp_path, {"alpha": []})
    skill_dir = packs_dir / "alpha" / "skills" / "alpha-skill"
    skill_dir.mkdir(parents=True)
    skill = "---\nname: alpha-skill\ndescription: Alpha skill.\n---\n\nBody.\n"
    (skill_dir / "SKILL.md").write_text(skill, encoding="utf-8")
    tree = BundleTree(packs_dir=packs_dir, locations=Locations()).build("cursor")
    assert [path for path, _ in tree.files] == [
        isolated_home / "home" / ".cursor" / "skills" / "alpha-skill" / "SKILL.md",
    ]


class _RootedLocations(Locations):
    """Locations that root every target beneath one folder, independent of the environment."""

    def __init__(self, root: Path) -> None:
        """Remember the folder that every config root is joined under."""
        self._root = root

    def config_root(self, target: str) -> Path:
        """Return the fixed root joined with ``target``."""
        return self._root / target


def _alpha_bundle(root: Path) -> Path:
    """Write a one-pack bundle whose pack ships one skill, and return its packs folder."""
    packs_dir = _write_bundle(root, {"alpha": []})
    skill_dir = packs_dir / "alpha" / "skills" / "alpha-skill"
    skill_dir.mkdir(parents=True)
    skill = "---\nname: alpha-skill\ndescription: Alpha skill.\n---\n\nBody.\n"
    (skill_dir / "SKILL.md").write_text(skill, encoding="utf-8")
    return packs_dir


def test_bundle_tree_renders_under_injected_locations(tmp_path: Path) -> None:
    """Every rendered file of the cursor tree lies under the config root of the injected locations."""
    locations = _RootedLocations(tmp_path / "injected")
    tree = BundleTree(_alpha_bundle(tmp_path / "bundle"), locations).build("cursor")
    root = locations.config_root("cursor")
    assert tree.files
    assert all(path.is_relative_to(root) for path, _ in tree.files)


def test_bundle_tree_ignores_environment_after_construction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Changing HOME and XDG_CONFIG_HOME after construction does not move the rendered paths."""
    locations = _RootedLocations(tmp_path / "injected")
    tree = BundleTree(_alpha_bundle(tmp_path / "bundle"), locations)
    before = [path for path, _ in tree.build("cursor").files]
    monkeypatch.setenv("HOME", str(tmp_path / "elsewhere-home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "elsewhere-config"))
    after = [path for path, _ in tree.build("cursor").files]
    assert before
    assert after == before
    assert all(path.is_relative_to(locations.config_root("cursor")) for path in after)


def test_unknown_pack_is_rejected(tmp_path: Path) -> None:
    packs_dir = _write_bundle(tmp_path, {"alpha": ["missing"]})
    with pytest.raises(PackError, match="missing"):
        PackCatalogue.load(packs_dir).closure(["alpha"])


def test_install_keeps_supporting_files_beside_skill(isolated_home: Path, tmp_path: Path) -> None:
    bundle = _demo_bundle(tmp_path / "bundle", "# Reference\n\nPlain text.\n")
    rendered = BundleTree(packs_dir=bundle, locations=Locations()).build("cursor")
    Installer(Locations(), ManifestStore(Locations())).install(
        "cursor",
        rendered.files,
        rule_sources=rendered.rule_sources,
    )
    installed = Path.home() / ".cursor" / "skills" / "demo" / "reference.md"
    assert installed.is_file()
    assert installed.read_bytes() == (bundle / "demo" / "skills" / "demo" / "reference.md").read_bytes()


def test_support_file_with_unknown_token_is_rejected(isolated_home: Path, tmp_path: Path) -> None:
    bundle = _demo_bundle(tmp_path / "bundle", "See {{nope:thing}}.\n")
    with pytest.raises(UnknownTokenError):
        BundleTree(packs_dir=bundle, locations=Locations()).build("cursor")
    assert not Path.home().exists()
