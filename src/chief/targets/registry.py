"""Install target registry: output layout, config root and target keys for each supported tool."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

_SKILL_PATH = "skills/{name}/SKILL.md"
_AGENT_PATH = "agents/{name}.md"
_INHERIT_MODEL = (("model", "inherit"),)


class UnknownTargetError(Exception):
    """Raised when a target name is not in the registry."""


@dataclass(frozen=True)
class TargetSpec:
    """Output layout and target-specific keys for one install target."""

    #: Relative path template per artifact kind, with ``{name}`` for the canonical name.
    paths: Mapping[str, str]
    #: Target keys appended to each artifact kind, as ``(key, value)`` pairs.
    keys: Mapping[str, tuple[tuple[str, str], ...]]
    #: Base directory of the config root: the home directory or the XDG config home.
    base: Literal["home", "xdg_config"]
    #: Config root directory, relative to ``base``.
    directory: str
    #: Canonical keys that the target does not keep.
    dropped: frozenset[str] = frozenset()


TARGETS: Mapping[str, TargetSpec] = MappingProxyType({
    "cursor": TargetSpec(
        paths={"skill": _SKILL_PATH, "agent": _AGENT_PATH, "rule": "rules/{name}.mdc"},
        keys={"agent": _INHERIT_MODEL, "rule": (("alwaysApply", "true"),)},
        base="home",
        directory=".cursor",
    ),
    "claude": TargetSpec(
        paths={"skill": _SKILL_PATH, "agent": _AGENT_PATH, "rule": "rules/{name}.md"},
        keys={"agent": _INHERIT_MODEL},
        base="home",
        directory=".claude",
    ),
    "opencode": TargetSpec(
        paths={"skill": _SKILL_PATH, "agent": _AGENT_PATH},
        keys={"agent": (("mode", "subagent"),)},
        base="xdg_config",
        directory="opencode",
        dropped=frozenset({"disable-model-invocation"}),
    ),
})


def target_spec(target: str) -> TargetSpec:
    """Return the spec registered for ``target``.

    Args:
        target: Target name, such as ``cursor``.

    Returns:
        The registered :class:`TargetSpec`.

    Raises:
        UnknownTargetError: If ``target`` is not registered.
    """
    try:
        return TARGETS[target]
    except KeyError as error:
        raise UnknownTargetError(f"unknown target: {target}") from error
