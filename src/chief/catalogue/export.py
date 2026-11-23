"""Export writer: writes each target's rendered tree into the folder that the facade chose for it."""

from collections.abc import Mapping
from pathlib import Path

from chief.catalogue.bundle_tree import BundleTree


class Exporter:
    """Write rendered trees to folders, refusing any folder that already holds output."""

    def __init__(self, bundle: BundleTree) -> None:
        """Bind the exporter to the rendered trees of ``bundle``."""
        self._bundle = bundle

    def write(self, folders: Mapping[str, Path]) -> None:
        """Write the tree of each target into its folder. Refuses before any write when a folder holds output."""
        for folder in folders.values():
            _refuse_existing(folder)
        for name, folder in folders.items():
            self._write_tree(name, folder)

    def _write_tree(self, name: str, folder: Path) -> None:
        """Write every file of the rendered tree of target ``name`` beneath ``folder``."""
        for relative, text in self._bundle.export_pairs(name):
            _write(folder / relative, text)


def _refuse_existing(folder: Path) -> None:
    """Raise :class:`FileExistsError` when ``folder`` holds output, so that export never overwrites."""
    if _holds_output(folder):
        raise FileExistsError(f"refusing to overwrite existing output: {folder}")


def _holds_output(folder: Path) -> bool:
    """Return whether ``folder`` is a file, or a folder with anything in it. A missing or empty folder holds none."""
    return folder.is_file() or (folder.is_dir() and any(folder.iterdir()))


def _write(path: Path, text: str) -> None:
    """Write ``text`` to ``path``, creating its folder first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
