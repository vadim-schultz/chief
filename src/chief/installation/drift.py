"""Drift checker: reports installed files whose sha256 no longer matches the install manifest."""

from pathlib import Path

from chief.installation.files import disk_block_sha, maybe_sha, read_text
from chief.installation.manifest import Manifest, ManifestStore
from chief.targets.locations import Locations


class DriftChecker:
    """Compare each recorded file and managed block of an install target with the disk."""

    def __init__(self, locations: Locations, store: ManifestStore) -> None:
        """Bind the checker to the config roots of ``locations`` and to the manifests of ``store``."""
        self._locations = locations
        self._store = store

    def check(self, target: str) -> list[str]:
        """Return the path, relative to the target root, of each recorded file that is missing or edited.

        Args:
            target: Install target name, such as ``cursor``.

        Returns:
            Relative POSIX paths: the drifted files in manifest order, then the managed block when it drifted.
        """
        root = self._locations.config_root(target)
        return [Path(path).relative_to(root).as_posix() for path in _drifted(self._store.read(target))]


def _drifted(prior: Manifest) -> list[str]:
    """Return the absolute paths whose content no longer matches the recorded sha256."""
    files = [path for path, digest in prior.files.items() if maybe_sha(read_text(Path(path))) != digest]
    block = prior.block
    if block is not None and disk_block_sha(read_text(Path(block.path))) != block.sha256:
        files.append(block.path)
    return files
