"""Export writer: one tree per target, one folder per target for ``all``, and no overwrite."""

from pathlib import Path

import pytest

from chief.api import ChiefOfStaff
from chief.targets.locations import Locations


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point HOME and both XDG roots at folders under ``tmp_path``, so no export can reach the real home."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    return tmp_path


def _write_skill_pack(packs_dir: Path) -> None:
    """Write one pack with one skill named ``demo``, so each rendered tree holds ``skills/demo/SKILL.md``."""
    folder = packs_dir / "demo"
    (folder / "skills" / "demo").mkdir(parents=True)
    (folder / "pack.toml").write_text('name = "demo"\ndescription = "Demo pack."\nrequires = []\n', encoding="utf-8")
    skill = "---\nname: demo\ndescription: Demo skill.\n---\nBody.\n"
    (folder / "skills" / "demo" / "SKILL.md").write_text(skill, encoding="utf-8")


def test_export_writes_tree_for_one_target(tmp_path: Path) -> None:
    packs_dir = tmp_path / "packs"
    _write_skill_pack(packs_dir)
    output = tmp_path / "out"
    ChiefOfStaff(packs_dir, Locations()).export("cursor", output)
    assert (output / "skills" / "demo" / "SKILL.md").is_file()


def test_export_all_writes_one_folder_per_target(tmp_path: Path) -> None:
    packs_dir = tmp_path / "packs"
    _write_skill_pack(packs_dir)
    output = tmp_path / "out"
    ChiefOfStaff(packs_dir, Locations()).export("all", output)
    for name in ("cursor", "claude", "opencode", "vscode"):
        assert (output / name / "skills" / "demo" / "SKILL.md").is_file()


def test_export_accepts_empty_existing_folder(tmp_path: Path) -> None:
    packs_dir = tmp_path / "packs"
    _write_skill_pack(packs_dir)
    output = tmp_path / "out"
    output.mkdir()
    ChiefOfStaff(packs_dir, Locations()).export("cursor", output)
    assert (output / "skills" / "demo" / "SKILL.md").is_file()


def test_export_refuses_existing_output_without_force(tmp_path: Path) -> None:
    packs_dir = tmp_path / "packs"
    _write_skill_pack(packs_dir)
    output = tmp_path / "out"
    output.write_text("keep\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        ChiefOfStaff(packs_dir, Locations()).export("cursor", output)
    assert output.read_text(encoding="utf-8") == "keep\n"


def _write_agent(packs_dir: Path) -> None:
    """Write one agent named ``demo-agent`` into the ``demo`` pack written by :func:`_write_skill_pack`."""
    agents = packs_dir / "demo" / "agents"
    agents.mkdir()
    text = "---\nname: demo-agent\ndescription: Demo agent.\n---\nBody.\n"
    (agents / "demo-agent.md").write_text(text, encoding="utf-8")


def _write_rule(packs_dir: Path) -> None:
    """Write one rule named ``demo-rule`` into the ``demo`` pack written by :func:`_write_skill_pack`."""
    rules = packs_dir / "demo" / "rules"
    rules.mkdir()
    text = "---\nname: demo-rule\ndescription: Demo rule.\n---\nRule body.\n"
    (rules / "demo-rule.md").write_text(text, encoding="utf-8")


def test_export_vscode_writes_skill_and_agent(tmp_path: Path) -> None:
    packs_dir = tmp_path / "packs"
    _write_skill_pack(packs_dir)
    _write_agent(packs_dir)
    output = tmp_path / "out"
    ChiefOfStaff(packs_dir, Locations()).export("vscode", output)
    assert (output / "skills" / "demo" / "SKILL.md").is_file()
    assert (output / "agents" / "demo-agent.agent.md").is_file()


def test_export_vscode_writes_no_rule_files(tmp_path: Path) -> None:
    packs_dir = tmp_path / "packs"
    _write_skill_pack(packs_dir)
    _write_rule(packs_dir)
    output = tmp_path / "out"
    ChiefOfStaff(packs_dir, Locations()).export("vscode", output)
    assert not (output / "rules").exists()
    assert not any("demo-rule" in path.name for path in output.rglob("*"))
