"""Config and state locations of the install targets, honouring the XDG base directories."""

import os
from collections.abc import Callable, Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Literal

from chief.targets.registry import target_spec

_STATE_DIR_NAME = "chief"


def _xdg(variable: str, fallback: str) -> Path:
    """Return the directory named by ``variable``, or ``fallback`` under HOME when it is unset or empty."""
    value = os.environ.get(variable)
    return Path(value) if value else Path.home() / fallback


_BASES: Mapping[Literal["home", "xdg_config", "xdg_state"], Callable[[], Path]] = MappingProxyType({
    "home": Path.home,
    "xdg_config": lambda: _xdg("XDG_CONFIG_HOME", ".config"),
    "xdg_state": lambda: _xdg("XDG_STATE_HOME", ".local/state"),
})


class Locations:
    """Resolve each target's config root and the shared state directory, at call time."""

    def config_root(self, target: str) -> Path:
        """Return the directory that ``target`` installs into.

        Args:
            target: Target name, such as ``opencode``.

        Returns:
            The base directory joined with the target's registered directory.

        Raises:
            UnknownTargetError: If ``target`` is not registered.
        """
        spec = target_spec(target)
        return _BASES[spec.base]() / spec.directory

    def state_dir(self) -> Path:
        """Return ``$XDG_STATE_HOME/chief``, the directory that holds the install manifests."""
        return _BASES["xdg_state"]() / _STATE_DIR_NAME
