"""Install target names, and the expansion of ``all`` into the concrete targets."""

from collections.abc import Mapping
from enum import Enum


class Target(str, Enum):
    """Install target names. ``all`` stands for every concrete target."""

    CURSOR = "cursor"
    CLAUDE = "claude"
    OPENCODE = "opencode"
    ALL = "all"


CONCRETE_TARGETS: tuple[Target, ...] = (Target.CURSOR, Target.CLAUDE, Target.OPENCODE)
_EXPANSIONS: Mapping[Target, tuple[Target, ...]] = {Target.ALL: CONCRETE_TARGETS}


def targets_for(target: Target) -> tuple[str, ...]:
    """Expand ``all`` to the concrete target names, and return any other target as its own name."""
    return tuple(member.value for member in _EXPANSIONS.get(target, (target,)))
