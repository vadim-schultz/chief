"""Config roots and the state directory, resolved from the XDG variables at call time."""

from pathlib import Path

import pytest

from chief.targets.locations import Locations
from chief.targets.registry import UnknownTargetError


def test_locations_honour_xdg_config_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    locations = Locations()
    assert locations.config_root("opencode") == tmp_path / "opencode"
    assert locations.config_root("cursor") == Path.home() / ".cursor"


def test_locations_reject_unknown_target() -> None:
    with pytest.raises(UnknownTargetError):
        Locations().config_root("no-such-target")


def test_locations_honour_xdg_state_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    assert Locations().state_dir() == tmp_path / "chief"


def test_state_dir_is_chief(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The shared state directory is named ``chief``."""
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    assert Locations().state_dir().name == "chief"
