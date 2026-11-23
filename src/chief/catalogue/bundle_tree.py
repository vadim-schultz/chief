"""Rendered tree of one install target, built from the packs of an injected bundle directory."""

from dataclasses import dataclass
from pathlib import Path

from chief.catalogue.packs import PackCatalogue
from chief.rendering.artifacts import Destination, render_artifact
from chief.rendering.managed_block import ManagedBlock
from chief.targets import registry
from chief.targets.locations import Locations

_KINDS = (("skill", "skills/*/SKILL.md"), ("agent", "agents/*.md"), ("rule", "rules/*.md"))
_NOT_SUPPORT = frozenset({"SKILL.md", "pack.toml"})


@dataclass(frozen=True)
class Tree:
    """The rendered files of one target, and the canonical rule texts for its managed block."""

    files: tuple[tuple[Path, str], ...]
    rule_sources: tuple[str, ...]


@dataclass(frozen=True)
class _Source:
    """One canonical file of a pack: its kind, its bundle path and its text."""

    kind: str
    path: Path
    text: str


class BundleTree:
    """Render the packs of one bundle directory for one install target."""

    def __init__(self, packs_dir: Path, locations: Locations) -> None:
        """Read the packs under ``packs_dir``, one folder per pack, and root the rendered paths at ``locations``."""
        self.packs_dir = packs_dir
        self.catalogue = PackCatalogue.load(packs_dir)
        self._locations = locations

    def build(self, target: str) -> Tree:
        """Render every pack for ``target``, dependency-first. Writes nothing."""
        root = self._root(target)
        sources = [source for name in self.catalogue.dependency_order() for source in self._pack_sources(name)]
        files = [
            pair for source in sources if not _in_block(target, source.kind) for pair in _render(target, root, source)
        ]
        rules = tuple(source.text for source in sources if _in_block(target, source.kind))
        return Tree(tuple(files), rules)

    def export_pairs(self, target: str) -> list[tuple[Path, str]]:
        """Return the tree of ``target`` with paths relative to its root, managed block included."""
        tree = self.build(target)
        root = self._root(target)
        pairs = list(tree.files)
        if tree.rule_sources:
            block = ManagedBlock(root)
            pairs.append((block.path, block.render("", tree.rule_sources)))
        return [(path.relative_to(root), text) for path, text in pairs]

    def _root(self, target: str) -> Path:
        """Return the config root of ``target`` under the injected locations."""
        return self._locations.config_root(target)

    def _pack_sources(self, pack: str) -> list[_Source]:
        """Return every canonical file of ``pack``, in a stable order."""
        base = self.packs_dir / pack
        return [
            _Source(kind, path, path.read_text(encoding="utf-8"))
            for kind, glob in _KINDS
            for path in sorted(base.glob(glob))
        ]


def _in_block(target: str, kind: str) -> bool:
    """Return whether a rule for ``target`` goes into the managed block, not into its own file."""
    return kind == "rule" and target == "opencode"


def _render(target: str, root: Path, source: _Source) -> list[tuple[Path, str]]:
    """Render one canonical file, and for a skill also copy its support files beside ``SKILL.md``."""
    rendered = render_artifact(target, root, source.kind, source.text)
    if source.kind != "skill":
        return rendered
    skill_path, _ = rendered[0]
    dest = Destination(root, registry.target_spec(target))
    return [*rendered, *_support_files(dest, skill_path.parent, source.path.parent)]


def _support_files(dest: Destination, skill_dir: Path, source_dir: Path) -> list[tuple[Path, str]]:
    """Return every support file of a skill, at the same relative path beside its rendered ``SKILL.md``."""
    return [
        (skill_dir / path.relative_to(source_dir), _support_text(dest, path)) for path in _support_paths(source_dir)
    ]


def _support_paths(source_dir: Path) -> list[Path]:
    """Return every file under a skill folder, except ``SKILL.md`` and ``pack.toml``."""
    return sorted(path for path in source_dir.rglob("*") if path.is_file() and path.name not in _NOT_SUPPORT)


def _support_text(dest: Destination, path: Path) -> str:
    """Return a support file's text, with tokens resolved for Markdown and unchanged otherwise."""
    text = path.read_text(encoding="utf-8")
    return dest.resolve(text) if path.suffix == ".md" else text
