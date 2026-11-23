"""Pack catalogue: the packs of one bundle directory, their requires closure and graph check."""

import sys
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

BUNDLED_PACKS = Path(__file__).parents[1] / "bundle" / "packs"
_WalkState = Literal["cycle", "unknown", "ok"]


@dataclass(frozen=True)
class Pack:
    """A pack manifest read from ``pack.toml``."""

    name: str
    description: str
    requires: tuple[str, ...]


class PackError(Exception):
    """Raised when the pack requires graph is invalid."""


class PackCatalogue:
    """The packs of one bundle directory, keyed by directory name."""

    def __init__(self, packs: Mapping[str, Pack]) -> None:
        """Hold the packs that were read from a bundle."""
        self.packs = packs

    @classmethod
    def load(cls, packs_dir: Path) -> "PackCatalogue":
        """Read every ``<pack>/pack.toml`` under ``packs_dir``, keyed by directory name."""
        manifests = sorted(packs_dir.glob("*/pack.toml"))
        return cls({manifest.parent.name: _read_pack(manifest) for manifest in manifests})

    def closure(self, roots: Iterable[str]) -> list[str]:
        """Return the roots and every pack they require, dependency-first."""
        return _walk(self.packs, roots)

    def dependency_order(self) -> list[str]:
        """Return every pack, each after the packs it requires."""
        return self.closure(self.packs)

    def check_graph(self) -> list[str]:
        """Return every pack name in dependency-first order, raising on a bad graph."""
        return _walk(self.packs, sorted(self.packs))


def _read_pack(manifest: Path) -> Pack:
    """Parse one ``pack.toml`` file into a :class:`Pack`."""
    with manifest.open("rb") as handle:
        data = tomllib.load(handle)
    return Pack(name=data["name"], description=data["description"], requires=tuple(data["requires"]))


def _walk(packs: Mapping[str, Pack], roots: Iterable[str]) -> list[str]:
    """Walk the requires graph from ``roots``, raising one :class:`PackError` for every problem found."""
    walk = _Walk(packs)
    for root in roots:
        walk.visit(root, ())
    if walk.problems:
        raise PackError("; ".join(sorted(walk.problems)))
    return list(walk.order)


def _chain(path: tuple[str, ...], name: str) -> str:
    """Render the requires chain that leads to ``name`` for an error message."""
    return " -> ".join((*path, name))


def _cycle_message(path: tuple[str, ...], name: str) -> str:
    """Describe the cycle closed by ``name``, starting from its smallest pack so it reads the same from any root."""
    cycle = path[path.index(name) :]
    start = cycle.index(min(cycle))
    rotated = (*cycle[start:], *cycle[:start])
    return f"requires cycle: {_chain(rotated, rotated[0])}"


@dataclass
class _Walk:
    """Depth-first walk of the requires graph that records dependency-first order and problems."""

    packs: Mapping[str, Pack]
    order: dict[str, None] = field(default_factory=dict)
    problems: set[str] = field(default_factory=set)

    def visit(self, name: str, path: tuple[str, ...]) -> None:
        """Visit ``name`` along ``path``, recording each cycle and unknown pack on every simple path."""
        handlers: dict[_WalkState, Callable[[str, tuple[str, ...]], None]] = {
            "cycle": self._record_cycle,
            "unknown": self._record_unknown,
            "ok": self._expand,
        }
        handlers[self._state(name, path)](name, path)

    def _state(self, name: str, path: tuple[str, ...]) -> _WalkState:
        """Name the walk state of ``name`` along ``path``: a cycle, an unknown pack, or a pack to expand."""
        if name in path:
            return "cycle"
        if name not in self.packs:
            return "unknown"
        return "ok"

    def _record_cycle(self, name: str, path: tuple[str, ...]) -> None:
        """Record the requires cycle that ``name`` closes along ``path``."""
        self.problems.add(_cycle_message(path, name))

    def _record_unknown(self, name: str, path: tuple[str, ...]) -> None:
        """Record the unknown pack that ``name`` is required as along ``path``."""
        self.problems.add(f"unknown pack: {_chain(path, name)}")

    def _expand(self, name: str, path: tuple[str, ...]) -> None:
        """Visit every requirement of ``name``, then append ``name`` to the order."""
        for required in self.packs[name].requires:
            self.visit(required, (*path, name))
        self.order[name] = None
