"""Guard the package name: one ``chief`` package under ``src/`` and no old package name in the tree."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
TREE_ROOTS = (SRC, REPO_ROOT / "tests")
DENYLIST_VARIABLE = "CHIEF_LEAK_DENYLIST"
DEFAULT_DENYLIST = Path.home() / ".config" / "chief" / "leak-denylist.txt"
PACKAGE_PREFIX = "package:"


def test_src_holds_only_chief_package() -> None:
    """``src/`` holds one package directory, and its name is ``chief``."""
    packages = sorted(path.name for path in SRC.iterdir() if _is_package_dir(path))
    assert packages == ["chief"]


def test_no_source_package_name_in_tree() -> None:
    """No file under ``src/`` or ``tests/`` holds a ``package:`` term of the local leak denylist."""
    terms = _package_terms(_denylist_path())
    hits = [hit for path in _scanned_files() for hit in _line_hits(path, terms)]
    assert not hits, f"old package name found at: {', '.join(hits)}"


def _is_package_dir(path: Path) -> bool:
    """Return whether ``path`` is a package directory, one that holds an ``__init__.py``."""
    return path.is_dir() and (path / "__init__.py").is_file()


def _denylist_path() -> Path:
    """Return ``CHIEF_LEAK_DENYLIST`` when it is set, otherwise the default denylist path."""
    override = os.environ.get(DENYLIST_VARIABLE)
    return Path(override) if override else DEFAULT_DENYLIST


def _require_denylist(path: Path) -> None:
    """Fail with the path named when the leak denylist at ``path`` does not exist."""
    if not path.is_file():
        pytest.fail(f"leak denylist not found at {path}; set {DENYLIST_VARIABLE} or create that file")


def _package_terms(path: Path) -> list[str]:
    """Return the old package names listed on the ``package:`` lines of the denylist at ``path``."""
    _require_denylist(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    terms = [line.removeprefix(PACKAGE_PREFIX).strip() for line in lines if line.startswith(PACKAGE_PREFIX)]
    terms = [term for term in terms if term]
    if not terms:
        pytest.fail(f"leak denylist at {path} has no {PACKAGE_PREFIX} line")
    return terms


def _scanned_files() -> Iterator[Path]:
    """Yield each file under the scanned roots, skipping bytecode caches and build output."""
    for root in TREE_ROOTS:
        for path in root.rglob("*"):
            if path.is_file() and not _is_generated(path):
                yield path


def _is_generated(path: Path) -> bool:
    """Return whether ``path`` is a ``.pyc`` file, or sits under ``__pycache__`` or an ``*.egg-info`` folder."""
    parts = path.relative_to(REPO_ROOT).parts
    return path.suffix == ".pyc" or any(part == "__pycache__" or part.endswith(".egg-info") for part in parts)


def _line_hits(path: Path, terms: list[str]) -> list[str]:
    """Return ``path:line`` for each line of ``path`` that holds a term, without printing the term."""
    text = path.read_text(encoding="utf-8", errors="replace")
    relative = path.relative_to(REPO_ROOT).as_posix()
    return [
        f"{relative}:{number}"
        for number, line in enumerate(text.splitlines(), start=1)
        if any(term.lower() in line.lower() for term in terms)
    ]
