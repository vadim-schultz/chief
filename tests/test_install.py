import hashlib
import json
import os
import re
from dataclasses import replace
from pathlib import Path, PurePosixPath

import pytest

from chief.__main__ import main
from chief.installation.drift import DriftChecker
from chief.installation.installer import Installer
from chief.installation.manifest import Block, Manifest, ManifestError, ManifestStore, ManifestVersionError
from chief.installation.planner import InstallPlanner
from chief.installation.uninstaller import Uninstaller
from chief.rendering.artifacts import render_artifact
from chief.targets.locations import Locations

BEGIN = "<!-- chief:begin -->"
END = "<!-- chief:end -->"

SKILL = """\
---
name: tdd
description: Test-driven development.
---

# TDD

Body.
"""

AGENT = """\
---
name: chapter-implementer
description: Implements one chapter.
---

Body.
"""

RULE = """\
---
name: tdd
description: Test-driven development
---

Rule body.
"""

RULE_CHANGED = """\
---
name: tdd
description: Test-driven development
---

Rule body changed.
"""


@pytest.fixture(autouse=True)
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point HOME and both XDG roots at one temporary directory for each test."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    return tmp_path


def _installer() -> Installer:
    return Installer(Locations(), ManifestStore(Locations()))


def _uninstaller() -> Uninstaller:
    return Uninstaller(ManifestStore(Locations()))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _config(home: Path) -> Path:
    return home / "opencode"


def _manifest(home: Path) -> Path:
    return home / "chief" / "opencode.manifest.json"


def _rendered(home: Path) -> list[tuple[Path, str]]:
    root = _config(home)
    skill = render_artifact("opencode", root, "skill", SKILL)
    agent = render_artifact("opencode", root, "agent", AGENT)
    return [*skill, *agent]


def _seed_agents(home: Path) -> Path:
    agents = _config(home) / "AGENTS.md"
    agents.parent.mkdir(parents=True, exist_ok=True)
    agents.write_text("Intro text.\n", encoding="utf-8")
    return agents


def test_install_writes_files_and_manifest(home: Path) -> None:
    agents = _seed_agents(home)
    rendered = _rendered(home)

    _installer().install("opencode", rendered, rule_sources=[RULE])

    for path, content in rendered:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8") == content
    manifest = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert manifest["files"] == {str(path): _sha(content) for path, content in rendered}
    assert manifest["block"]["begin"] == BEGIN
    assert manifest["block"]["end"] == END
    assert manifest["block"]["sha256"] == _sha("Rule body.")
    text = agents.read_text(encoding="utf-8")
    assert "Intro text." in text
    assert f"{BEGIN}\nRule body.\n{END}" in text

    agents.write_text(text + "Footer text.\n", encoding="utf-8")
    _installer().install("opencode", rendered, rule_sources=[RULE])
    assert "Footer text." in agents.read_text(encoding="utf-8")
    assert "Intro text." in agents.read_text(encoding="utf-8")


def test_dry_run_writes_nothing(home: Path) -> None:
    agents = _seed_agents(home)
    original = agents.read_text(encoding="utf-8")
    rendered = _rendered(home)

    plan = _installer().install("opencode", rendered, rule_sources=[RULE], dry_run=True)

    assert not any(path.exists() for path, _ in rendered)
    assert not _manifest(home).exists()
    assert agents.read_text(encoding="utf-8") == original
    written = {action.path for action in plan.actions if action.kind == "write"}
    assert {path for path, _ in rendered} <= written


def test_modified_file_is_refused_without_force(home: Path) -> None:
    agents = _seed_agents(home)
    rendered = _rendered(home)
    _installer().install("opencode", rendered, rule_sources=[RULE])
    skill, _ = rendered[0]
    skill.write_text("Edited by the user.\n", encoding="utf-8")
    manifest_before = _manifest(home).read_text(encoding="utf-8")
    agents_before = agents.read_text(encoding="utf-8")

    plan = _installer().install("opencode", rendered, rule_sources=[RULE_CHANGED])

    kinds = {action.path: action.kind for action in plan.actions}
    assert kinds[skill] == "refuse"
    assert skill.read_text(encoding="utf-8") == "Edited by the user.\n"
    assert json.loads(manifest_before)["files"][str(skill)] == _sha(rendered[0][1])
    assert _manifest(home).read_text(encoding="utf-8") == manifest_before
    assert agents.read_text(encoding="utf-8") == agents_before


def test_force_overwrites_modified_file(home: Path) -> None:
    _seed_agents(home)
    rendered = _rendered(home)
    _installer().install("opencode", rendered, rule_sources=[RULE])
    skill, content = rendered[0]
    skill.write_text("Edited by the user.\n", encoding="utf-8")

    plan = _installer().install("opencode", rendered, rule_sources=[RULE], force=True)

    kinds = {action.path: action.kind for action in plan.actions}
    assert kinds[skill] == "write"
    assert skill.read_text(encoding="utf-8") == content
    manifest = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert manifest["files"][str(skill)] == _sha(content)


def test_edited_managed_block_is_refused_without_force(home: Path) -> None:
    agents = _seed_agents(home)
    rendered = _rendered(home)
    _installer().install("opencode", rendered, rule_sources=[RULE])
    agents.write_text(agents.read_text(encoding="utf-8").replace("Rule body.", "Hand edit."), encoding="utf-8")
    edited = agents.read_text(encoding="utf-8")

    plan = _installer().install("opencode", rendered, rule_sources=[RULE])

    kinds = {action.path: action.kind for action in plan.actions}
    assert kinds[agents] == "refuse"
    assert agents.read_text(encoding="utf-8") == edited


def test_uninstall_removes_only_manifest_files(home: Path) -> None:

    agents = _seed_agents(home)
    rendered = _rendered(home)
    _installer().install("opencode", rendered, rule_sources=[RULE])
    unmanaged = rendered[0][0].parent / "notes.md"
    unmanaged.write_text("Mine.\n", encoding="utf-8")
    agents.write_text(agents.read_text(encoding="utf-8") + "Footer text.\n", encoding="utf-8")

    _uninstaller().run("opencode")

    for path, _ in rendered:
        assert not path.exists(), path
    text = agents.read_text(encoding="utf-8")
    assert BEGIN not in text
    assert END not in text
    assert "Intro text." in text
    assert "Footer text." in text
    assert unmanaged.read_text(encoding="utf-8") == "Mine.\n"
    assert not _manifest(home).exists()


def test_uninstall_keeps_edited_file(home: Path) -> None:

    _seed_agents(home)
    rendered = _rendered(home)
    _installer().install("opencode", rendered, rule_sources=[RULE])
    skill, content = rendered[0]
    skill.write_text("Edited by the user.\n", encoding="utf-8")

    result = _uninstaller().run("opencode")

    assert skill in result.refused
    assert skill.read_text(encoding="utf-8") == "Edited by the user.\n"
    assert not rendered[1][0].exists()
    manifest = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert manifest["files"] == {str(skill): _sha(content)}


def test_unmanaged_file_is_refused_on_first_install(home: Path) -> None:
    rendered = _rendered(home)
    skill, _ = rendered[0]
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("Mine.\n", encoding="utf-8")

    plan = _installer().install("opencode", rendered, rule_sources=[RULE])

    kinds = {action.path: action.kind for action in plan.actions}
    assert kinds[skill] == "refuse"
    assert skill.read_text(encoding="utf-8") == "Mine.\n"
    assert not _manifest(home).exists()


def test_untracked_file_is_refused_even_with_force(home: Path) -> None:
    rendered = _rendered(home)
    skill, _ = rendered[0]
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("Mine.\n", encoding="utf-8")

    plan = _installer().install("opencode", rendered, rule_sources=[RULE], force=True)

    kinds = {action.path: action.kind for action in plan.actions}
    assert kinds[skill] == "refuse"
    assert skill.read_text(encoding="utf-8") == "Mine.\n"
    assert not _manifest(home).exists()


@pytest.fixture
def mcp_sentinels(home: Path, monkeypatch: pytest.MonkeyPatch) -> dict[Path, bytes]:
    """Write one MCP configuration sentinel per forbidden location and return each path with its bytes."""
    work = home / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    sentinels = [
        home / ".cursor" / "mcp.json",
        home / "opencode" / "opencode.json",
        work / ".mcp.json",
        home / ".mcp" / "servers.json",
    ]
    for path in sentinels:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"sentinel {path.name}\n".encode())
    return {path: path.read_bytes() for path in sentinels}


def test_install_and_uninstall_succeed_beside_mcp_sentinels(home: Path, mcp_sentinels: dict[Path, bytes]) -> None:

    rendered = _rendered(home)

    _installer().install("opencode", rendered, rule_sources=[RULE])
    for path, _ in rendered:
        assert path.exists(), path
    _uninstaller().run("opencode")
    for path, _ in rendered:
        assert not path.exists(), path
    for path, content in mcp_sentinels.items():
        assert path.read_bytes() == content, path


def test_mcp_config_files_are_never_touched(home: Path, mcp_sentinels: dict[Path, bytes]) -> None:

    mcp_home_before = sorted((home / ".mcp").iterdir())
    _installer().install("opencode", _rendered(home), rule_sources=[RULE])
    _uninstaller().run("opencode")

    for path, content in mcp_sentinels.items():
        assert path.read_bytes() == content, path
    assert sorted((home / ".mcp").iterdir()) == mcp_home_before
    fresh = home / "fresh"
    forbidden = [
        (fresh / "mcp.json", "{}\n"),
        (fresh / "opencode.json", "{}\n"),
        (fresh / ".mcp.json", "{}\n"),
        (home / ".mcp" / "new.json", "{}\n"),
    ]
    plan = _installer().install("opencode", forbidden, dry_run=True)
    kinds = {action.path: action.kind for action in plan.actions}
    for path, _ in forbidden:
        assert kinds[path] == "refuse", path


def test_manifest_round_trip_carries_schema_version(home: Path) -> None:
    ManifestStore(Locations()).write("opencode", Manifest({"/a/skill.md": "abc"}, None))

    raw = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert raw["schema_version"] == 1


def test_failed_manifest_write_keeps_prior_file(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = ManifestStore(Locations())
    store.write("opencode", Manifest({"/a/skill.md": "first"}, None))
    before = _manifest(home).read_text(encoding="utf-8")

    def fail_replace(source: str, target: str) -> None:
        raise OSError("replace refused")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="replace refused"):
        store.write("opencode", Manifest({"/a/skill.md": "second"}, None))

    assert _manifest(home).read_text(encoding="utf-8") == before
    assert sorted(path.name for path in _manifest(home).parent.iterdir()) == ["opencode.manifest.json"]


def _seed_manifest(home: Path, text: str) -> None:
    _manifest(home).parent.mkdir(parents=True, exist_ok=True)
    _manifest(home).write_text(text, encoding="utf-8")


def test_newer_schema_version_is_refused(home: Path) -> None:
    _seed_manifest(home, json.dumps({"schema_version": 2, "files": {}, "block": None}))

    with pytest.raises(ManifestVersionError, match="schema_version 2"):
        ManifestStore(Locations()).read("opencode")


def test_unknown_manifest_fields_survive_rewrite(home: Path) -> None:
    _seed_manifest(home, json.dumps({"schema_version": 1, "files": {}, "block": None, "owner": "docs-team"}))
    store = ManifestStore(Locations())

    manifest = store.read("opencode")
    store.write("opencode", replace(manifest, block=Block(str(home / "AGENTS.md"), BEGIN, END, _sha("Rule body."))))

    raw = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert raw["block"]["sha256"] == _sha("Rule body.")
    assert raw["owner"] == "docs-team"


def test_torn_manifest_is_refused(home: Path) -> None:
    _seed_manifest(home, '{"schema_version": 1, "files": {"/a/skill.md": "ab')

    with pytest.raises(ManifestError) as caught:
        ManifestStore(Locations()).read("opencode")

    assert str(_manifest(home)) in str(caught.value)


def test_legacy_manifest_without_version_is_upgraded_on_write(home: Path) -> None:
    _seed_manifest(home, json.dumps({"files": {"/a/skill.md": "abc"}, "block": None}))
    store = ManifestStore(Locations())

    store.write("opencode", store.read("opencode"))

    raw = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert raw["schema_version"] == 1
    assert raw["files"] == {"/a/skill.md": "abc"}


def test_install_and_uninstall_keep_unknown_manifest_fields(home: Path) -> None:

    _seed_manifest(home, json.dumps({"schema_version": 1, "files": {}, "block": None, "owner": "docs-team"}))
    _seed_agents(home)
    rendered = _rendered(home)

    _installer().install("opencode", rendered, rule_sources=[RULE])
    installed = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert installed["owner"] == "docs-team"

    skill, _ = rendered[0]
    skill.write_text("Edited by the user.\n", encoding="utf-8")
    _uninstaller().run("opencode")
    uninstalled = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert uninstalled["owner"] == "docs-team"
    assert uninstalled["files"] == {str(skill): _sha(rendered[0][1])}


def test_planner_creates_missing_file(home: Path) -> None:
    planner = InstallPlanner(Locations(), ManifestStore(Locations()))
    path, content = render_artifact("opencode", _config(home), "skill", SKILL)[0]

    plan = planner.plan("opencode", [(path, content)])

    assert len(plan.actions) == 1
    action = plan.actions[0]
    assert (action.path, action.kind, action.content) == (path, "write", content)


def test_planner_refuses_mcp_config_targets(home: Path) -> None:
    planner = InstallPlanner(Locations(), ManifestStore(Locations()))
    mcp_config = home / ".cursor" / "mcp.json"

    plan = planner.plan("cursor", [(mcp_config, "{}\n")])

    kinds = {action.path: action.kind for action in plan.actions}
    assert kinds.get(mcp_config) == "refuse"
    assert not any(action.kind == "write" and action.path == mcp_config for action in plan.actions)


SNAPSHOT = Path(__file__).parent / "fixtures" / "install_snapshot.json"


def _snapshot_mismatch(root: Path) -> list[str]:
    """Return the paths that the recorded snapshot and the install under ``root`` do not share, in path order."""
    recorded = set(json.loads(SNAPSHOT.read_text(encoding="utf-8")))
    return sorted(recorded ^ set(_installed_paths(root)))


def test_install_all_matches_recorded_snapshot(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Install every target into a temporary HOME and compare the installed paths with the recorded snapshot."""
    _install_all(home, monkeypatch)

    assert _snapshot_mismatch(home) == []


HEX_DIGEST = re.compile(r"[0-9a-f]{64}")


def _install_all(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Install every target through the CLI into ``home``, with the XDG roots under it."""
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(home / ".local" / "state"))
    with pytest.raises(SystemExit) as exit_info:
        main(["install", "--target", "all"])
    assert exit_info.value.code == 0


def _installed_paths(root: Path) -> list[str]:
    """Return the path of every installed file under ``root``, relative to it, manifests excluded, in path order."""
    return [
        path.relative_to(root).as_posix()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.name.endswith(".manifest.json")
    ]


def _is_relative_path(entry: str) -> bool:
    """Return True when ``entry`` is a relative POSIX path and not a sha256 digest."""
    return not PurePosixPath(entry).is_absolute() and HEX_DIGEST.fullmatch(entry) is None


def test_snapshot_lists_paths_only() -> None:
    entries: list[str] = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert isinstance(entries, list)
    assert entries == sorted(set(entries))
    assert all(_is_relative_path(entry) for entry in entries)


def test_snapshot_detects_missing_file(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_all(home, monkeypatch)
    removed = _installed_paths(home)[0]
    (home / removed).unlink()

    assert removed in _snapshot_mismatch(home)


def test_installer_writes_files_and_manifest(home: Path) -> None:
    store = ManifestStore(Locations())
    path, content = render_artifact("opencode", _config(home), "skill", SKILL)[0]
    plan = InstallPlanner(Locations(), store).plan("opencode", [(path, content)])

    Installer(Locations(), store).apply(plan)

    assert path.exists(), path
    assert path.read_text(encoding="utf-8") == content
    manifest = json.loads(_manifest(home).read_text(encoding="utf-8"))
    assert manifest["files"] == {str(path): _sha(content)}


def test_installer_writes_nothing_when_a_plan_is_refused(home: Path) -> None:
    store = ManifestStore(Locations())
    store.write("opencode", Manifest({"/recorded/skill.md": _sha("prior")}, None))
    manifest_before = _manifest(home).read_text(encoding="utf-8")
    path, content = render_artifact("opencode", _config(home), "skill", SKILL)[0]
    refused = _config(home) / "opencode.json"
    plan = InstallPlanner(Locations(), store).plan("opencode", [(path, content), (refused, "{}\n")])
    assert plan.refused

    Installer(Locations(), store).apply(plan)

    assert not path.exists(), path
    assert not refused.exists(), refused
    assert _manifest(home).read_text(encoding="utf-8") == manifest_before


def test_uninstaller_removes_only_listed_files(home: Path) -> None:
    store = ManifestStore(Locations())
    path, content = render_artifact("opencode", _config(home), "skill", SKILL)[0]
    _installer().install("opencode", [(path, content)])
    unrelated = path.parent / "notes.md"
    unrelated.write_text("Mine.\n", encoding="utf-8")

    Uninstaller(store).run("opencode")

    assert not path.exists(), path
    assert unrelated.read_text(encoding="utf-8") == "Mine.\n"


def test_uninstaller_runs_from_the_store_alone(home: Path) -> None:
    """An uninstaller built from the manifest store alone removes what install wrote."""
    store = ManifestStore(Locations())
    path, content = render_artifact("opencode", _config(home), "skill", SKILL)[0]
    _installer().install("opencode", [(path, content)])

    Uninstaller(store).run("opencode")

    assert not path.exists(), path


def test_uninstaller_rejects_the_old_two_argument_form(home: Path) -> None:
    """The retired constructor, which took a Locations before the store, raises TypeError."""
    store = ManifestStore(Locations())
    with pytest.raises(TypeError):
        Uninstaller(Locations(), store)  # ty: ignore[invalid-argument-type, too-many-positional-arguments]


def test_drift_checker_reports_edited_file(home: Path) -> None:
    store = ManifestStore(Locations())
    path, content = render_artifact("opencode", _config(home), "skill", SKILL)[0]
    _installer().install("opencode", [(path, content)])
    path.write_text("Edited by the user.\n", encoding="utf-8")

    drifted = DriftChecker(Locations(), store).check("opencode")

    assert drifted == [path.relative_to(_config(home)).as_posix()]
