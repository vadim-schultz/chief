"""Typer command surface: one happy path and one negative path for each command."""

from pathlib import Path

import pytest

import chief
from chief.__main__ import main
from chief.api import ChiefOfStaff
from chief.cli.app import app
from chief.installation.installer import Installer
from chief.installation.manifest import Manifest, ManifestStore
from chief.installation.planner import Action, ActionKind, Plan
from chief.rendering.artifacts import render_artifact
from chief.targets.locations import Locations

PACKS = Path(chief.__file__).parent / "bundle" / "packs"
TARGETS = ("cursor", "claude", "opencode")


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point HOME and both XDG roots at folders under ``tmp_path``."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    return tmp_path


def _exit_code(argv: list[str]) -> int:
    """Run ``main`` with ``argv`` and return the exit code that it raises."""
    with pytest.raises(SystemExit) as error:
        main(argv)
    assert isinstance(error.value.code, int)
    return error.value.code


def test_list_shows_every_pack(capsys: pytest.CaptureFixture[str]) -> None:
    assert _exit_code(["list"]) == 0
    out = capsys.readouterr().out
    for pack in (path.name for path in PACKS.iterdir() if path.is_dir()):
        assert f"{pack}: " in out
    for target in TARGETS:
        assert target in out


def test_unknown_pack_name_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert _exit_code(["list", "no-such-pack"]) == 2
    err = capsys.readouterr().err
    assert "Invalid value" in err
    assert "no-such-pack" in err


def test_install_dry_run_prints_plan(capsys: pytest.CaptureFixture[str], isolated_home: Path) -> None:
    assert _exit_code(["install", "--target", "cursor", "--dry-run"]) == 0
    assert str(isolated_home / "home") in capsys.readouterr().out
    assert not any(path.is_file() for path in isolated_home.rglob("*"))


def test_install_unknown_target_exits_2(capsys: pytest.CaptureFixture[str], isolated_home: Path) -> None:
    assert _exit_code(["install", "--target", "no-such-target"]) == 2
    err = capsys.readouterr().err
    assert "Invalid value" in err
    assert "no-such-target" in err
    assert not any(path.is_file() for path in isolated_home.rglob("*"))


def _cursor_tree() -> list[tuple[Path, str]]:
    """Render every pack for cursor with the renderer, the way the installer expects."""
    root = Path.home() / ".cursor"
    pairs: list[tuple[Path, str]] = []
    for pattern, kind in (("*/skills/*/SKILL.md", "skill"), ("*/agents/*.md", "agent"), ("*/rules/*.md", "rule")):
        for source in sorted(PACKS.glob(pattern)):
            pairs += render_artifact("cursor", root, kind, source.read_text(encoding="utf-8"))
    return pairs


def _install_cursor() -> None:
    """Write the cursor target with the installer API, so that a test fails only for the command it checks."""
    Installer(Locations(), ManifestStore(Locations())).install("cursor", _cursor_tree())


def _first_skill() -> Path:
    """Return the first installed cursor skill file."""
    return sorted((Path.home() / ".cursor" / "skills").rglob("SKILL.md"))[0]


def test_doctor_clean_install_reports_no_drift(capsys: pytest.CaptureFixture[str]) -> None:
    _install_cursor()
    assert _exit_code(["doctor", "--target", "cursor"]) == 0
    assert "no drift" in capsys.readouterr().out.lower()


def test_doctor_modified_file_reports_drift(capsys: pytest.CaptureFixture[str]) -> None:
    _install_cursor()
    _first_skill().write_text("edited\n", encoding="utf-8")
    assert _exit_code(["doctor", "--target", "cursor"]) == 1
    assert _first_skill().relative_to(Path.home() / ".cursor").as_posix() in capsys.readouterr().out


def test_export_writes_rendered_tree(isolated_home: Path) -> None:
    out = isolated_home / "out"
    assert _exit_code(["export", "--target", "cursor", "--output", str(out)]) == 0
    for skill in {path.parent.name for path in PACKS.glob("*/skills/*/SKILL.md")}:
        assert (out / "skills" / skill / "SKILL.md").is_file()


def test_cli_has_no_mcp_snippet_command() -> None:
    """The command table holds only list, install, uninstall, doctor and export."""
    names = {command.name for command in app.registered_commands}
    assert names == {"list", "install", "uninstall", "doctor", "export"}


def test_install_force_overwrites_modified_file() -> None:
    _install_cursor()
    skill = _first_skill()
    original = skill.read_text(encoding="utf-8")
    skill.write_text("edited\n", encoding="utf-8")
    assert _exit_code(["install", "--target", "cursor", "--force"]) == 0
    assert skill.read_text(encoding="utf-8") == original


def test_install_without_force_keeps_modified_file(capsys: pytest.CaptureFixture[str]) -> None:
    _install_cursor()
    skill = _first_skill()
    skill.write_text("edited\n", encoding="utf-8")
    assert _exit_code(["install", "--target", "cursor"]) == 1
    assert skill.read_text(encoding="utf-8") == "edited\n"
    assert str(skill) in capsys.readouterr().err


def test_uninstall_removes_tracked_files() -> None:
    _install_cursor()
    assert _exit_code(["uninstall", "--target", "cursor"]) == 0
    assert not any(path.exists() for path, _ in _cursor_tree())


def test_uninstall_keeps_untracked_files() -> None:
    _install_cursor()
    extra = _first_skill().parent / "notes.md"
    extra.write_text("mine\n", encoding="utf-8")
    assert _exit_code(["uninstall", "--target", "cursor"]) == 0
    assert extra.read_text(encoding="utf-8") == "mine\n"


def _plan(kind: ActionKind, path: str) -> Plan:
    """Return a one-action plan of ``kind`` for ``path``, with an empty manifest."""
    action = Action(path=Path(path), kind=kind, content="")
    return Plan(target="cursor", actions=(action,), manifest=Manifest(files={}, block=None))


def _fake_facade(monkeypatch: pytest.MonkeyPatch, plans: list[Plan]) -> list[tuple[str, bool, bool]]:
    """Make ``ChiefOfStaff.bundled`` return a fake facade that yields ``plans``, and record its install calls."""
    calls: list[tuple[str, bool, bool]] = []

    class FakeFacade:
        """Stand-in facade whose ``install`` records the call and returns the given plans."""

        def install(self, target: str, *, dry_run: bool = False, force: bool = False) -> list[Plan]:
            """Record the call and return the given plans."""
            calls.append((target, dry_run, force))
            return plans

    monkeypatch.setattr(ChiefOfStaff, "bundled", classmethod(lambda cls, locations=None: FakeFacade()))
    return calls


def test_install_command_prints_plans_from_facade(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _fake_facade(monkeypatch, [_plan("write", "/fake/plan-line.md")])
    assert _exit_code(["install", "--target", "cursor", "--dry-run"]) == 0
    assert "write /fake/plan-line.md" in capsys.readouterr().out
    assert calls == [("cursor", True, False)]


def test_install_command_maps_refusal_to_exit_one(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _fake_facade(monkeypatch, [_plan("refuse", "/fake/refused.md")])
    assert _exit_code(["install", "--target", "cursor"]) == 1
    assert "refuse /fake/refused.md" in capsys.readouterr().err
