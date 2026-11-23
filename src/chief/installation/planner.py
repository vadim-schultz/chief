"""Install planner: decides each path of one install target against the disk and the prior manifest. Writes nothing."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from chief.installation.files import disk_block_sha, maybe_sha, read_text, sha256
from chief.installation.manifest import Block, Manifest, ManifestStore
from chief.rendering.managed_block import ManagedBlock
from chief.targets.locations import Locations

ActionKind = Literal["write", "skip", "refuse"]
Rendered = Sequence[tuple[Path, str]]
_FORBIDDEN_NAMES = frozenset({"mcp.json", "opencode.json", ".mcp.json"})
_MCP_DIR = ".mcp"


@dataclass(frozen=True)
class Action:
    """One planned step for one path."""

    path: Path
    kind: ActionKind
    content: str


@dataclass(frozen=True)
class Plan:
    """The ordered actions for one install target and the manifest they leave behind."""

    target: str
    actions: tuple[Action, ...]
    manifest: Manifest

    @property
    def refused(self) -> bool:
        """Whether any action refuses, which blocks the whole target."""
        return any(action.kind == "refuse" for action in self.actions)


@dataclass(frozen=True)
class _Facts:
    """What the planner knows about one path before it decides."""

    path: Path
    content: str
    on_disk: str | None
    planned: str
    recorded: str | None

    @property
    def forbidden(self) -> bool:
        """Whether the path is an MCP configuration file that the installer never writes."""
        return self.path.name in _FORBIDDEN_NAMES or self.path.is_relative_to(Path.home() / _MCP_DIR)


_Check = Callable[[_Facts, bool], bool]
_RULES: tuple[tuple[_Check, ActionKind], ...] = (
    (lambda facts, _force: facts.forbidden, "refuse"),
    (lambda facts, _force: facts.on_disk is None, "write"),
    (lambda facts, _force: facts.on_disk == facts.planned, "skip"),
    (lambda facts, _force: facts.recorded is None, "refuse"),
    (lambda facts, force: facts.on_disk != facts.recorded and not force, "refuse"),
    (lambda _facts, _force: True, "write"),
)


class InstallPlanner:
    """Plan the files and managed block of one install target. Reads the disk and the manifest, and writes nothing."""

    def __init__(self, locations: Locations, store: ManifestStore) -> None:
        """Bind the planner to the config roots of ``locations`` and to the manifests of ``store``."""
        self._locations = locations
        self._store = store

    def plan(
        self,
        target: str,
        rendered: Rendered,
        *,
        rule_sources: Sequence[str] = (),
        force: bool = False,
    ) -> Plan:
        """Decide every path of ``target`` against the disk and the prior manifest.

        Args:
            target: Install target name.
            rendered: ``(path, content)`` pairs from the renderer.
            rule_sources: Canonical rule texts for the managed block, or none.
            force: Whether edited files the manifest tracks may be overwritten.

        Returns:
            The plan. Nothing is written.
        """
        prior = self._store.read(target)
        facts = [
            _Facts(path, content, maybe_sha(read_text(path)), sha256(content), prior.files.get(str(path)))
            for path, content in rendered
        ]
        files = {**prior.files, **{str(path): sha256(content) for path, content in rendered}}
        block = prior.block
        if rule_sources:
            block_facts, block = self._block(target, rule_sources, prior)
            facts.append(block_facts)
        actions = tuple(Action(item.path, _decide(item, force), item.content) for item in facts)
        return Plan(target, actions, Manifest(files, block, prior.extra))

    def _block(self, target: str, rule_sources: Sequence[str], prior: Manifest) -> tuple[_Facts, Block]:
        """Return the facts of the managed block of ``target`` and the block record the plan leaves behind."""
        block = ManagedBlock(self._locations.config_root(target))
        text = block.render(read_text(block.path) or "", rule_sources)
        body = sha256(ManagedBlock.body(text))
        recorded = prior.block.sha256 if prior.block and prior.block.path == str(block.path) else None
        facts = _Facts(block.path, text, disk_block_sha(read_text(block.path)), body, recorded)
        return facts, Block(str(block.path), ManagedBlock.BEGIN, ManagedBlock.END, body)


def _decide(facts: _Facts, force: bool) -> ActionKind:
    """Return the action of the first rule in ``_RULES`` that matches ``facts``."""
    return next(kind for check, kind in _RULES if check(facts, force))
