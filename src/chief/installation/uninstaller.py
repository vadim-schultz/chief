"""Uninstaller: removes the files and managed block that the manifest of one install target lists."""

from dataclasses import dataclass
from pathlib import Path

from chief.installation.files import read_text, sha256
from chief.installation.manifest import Block, Manifest, ManifestStore
from chief.rendering.managed_block import ManagedBlock


@dataclass(frozen=True)
class UninstallResult:
    """What one uninstall removed, and what it kept because the file was edited since install."""

    removed: tuple[Path, ...]
    refused: tuple[Path, ...]


class Uninstaller:
    """Remove the manifest-tracked files and managed block of one install target, and keep the rest."""

    def __init__(self, store: ManifestStore) -> None:
        """Bind the uninstaller to the manifests of ``store``."""
        self._store = store

    def run(self, target: str) -> UninstallResult:
        """Remove the manifest-tracked files and managed block of ``target``.

        A file or block whose sha256 differs from the record is kept, and it is reported as refused.
        The manifest is rewritten to track only what was kept, and deleted when nothing was kept.

        Args:
            target: Install target name, such as ``opencode``.

        Returns:
            The paths that are gone, and the paths that were kept.
        """
        prior = self._store.read(target)
        gone = {text: _remove_file(Path(text), digest) for text, digest in prior.files.items()}
        block_gone = prior.block is None or _remove_block(prior.block)
        kept = _kept(prior, gone, block_gone)
        self._record(target, kept)
        return UninstallResult(tuple(Path(text) for text, done in gone.items() if done), _refused(kept))

    def _record(self, target: str, remaining: Manifest) -> None:
        """Rewrite the manifest of ``target`` to ``remaining``, or delete it when nothing is left."""
        if remaining.files or remaining.block:
            self._store.write(target, remaining)
        else:
            self._store.delete(target)


def _kept(prior: Manifest, gone: dict[str, bool], block_gone: bool) -> Manifest:
    """Return the manifest that tracks only the files and block that were not removed."""
    return Manifest(
        {text: digest for text, digest in prior.files.items() if not gone[text]},
        None if block_gone else prior.block,
        prior.extra,
    )


def _refused(kept: Manifest) -> tuple[Path, ...]:
    """Return every path that was kept because it was edited since install."""
    block_paths = () if kept.block is None else (Path(kept.block.path),)
    return (*(Path(text) for text in kept.files), *block_paths)


def _remove_file(path: Path, digest: str) -> bool:
    """Delete ``path`` when it still holds ``digest``. Return whether it is absent afterwards."""
    text = read_text(path)
    if text is None:
        return True
    if sha256(text) != digest:
        return False
    path.unlink()
    return True


def _remove_block(block: Block) -> bool:
    """Strip the managed block when its body still holds the recorded digest. Return whether it is gone."""
    path = Path(block.path)
    text = read_text(path)
    if text is None or ManagedBlock.BEGIN not in text:
        return True
    if sha256(ManagedBlock.body(text)) != block.sha256:
        return False
    path.write_bytes(ManagedBlock.strip(text).encode("utf-8"))
    return True
