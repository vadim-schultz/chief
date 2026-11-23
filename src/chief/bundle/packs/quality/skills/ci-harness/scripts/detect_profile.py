"""Detect the language profile of a repository root from its marker files."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

# Each profile lists its marker sets. A set matches when every file in it exists in the root.
PROFILE_MARKERS: tuple[tuple[str, tuple[tuple[str, ...], ...]], ...] = (
    ("python", (("pyproject.toml",),)),
    ("typescript", (("package.json", "tsconfig.json"),)),
    ("rust", (("Cargo.toml",),)),
    ("c-cpp", (("CMakeLists.txt",), ("Makefile",))),
)


def _set_present(root: Path, markers: tuple[str, ...]) -> bool:
    """Return True when every marker file of one set exists directly in ``root``."""
    return all((root / marker).is_file() for marker in markers)


def _matching_profiles(root: Path) -> list[str]:
    """Return the names of every profile that has a marker set present in ``root``."""
    return [name for name, sets in PROFILE_MARKERS if any(_set_present(root, s) for s in sets)]


def detect_profile(root: Path) -> str | None:
    """Return the profile name for ``root``, or None when no profile or several profiles match."""
    matches = _matching_profiles(root)
    return matches[0] if len(matches) == 1 else None


def _no_profile(_matches: list[str]) -> str:
    """Return the refusal line for a directory that no profile matches."""
    return "no profile"


def _ambiguous(matches: list[str]) -> str:
    """Return the refusal line for a directory that several profiles match."""
    return "ambiguous profile: " + ", ".join(matches)


# Refusal line by the number of matching profiles. Any count not listed is ambiguous.
REFUSALS: dict[int, Callable[[list[str]], str]] = {0: _no_profile}


def _refusal(root: Path) -> str:
    """Return the stdout line for a directory that does not match exactly one profile."""
    matches = _matching_profiles(root)
    return REFUSALS.get(len(matches), _ambiguous)(matches)


def main(argv: list[str]) -> int:
    """Print the profile of the directory in ``argv`` and return the exit code."""
    root = Path(argv[0]) if argv else Path.cwd()
    profile = detect_profile(root)
    if profile is not None:
        print(profile)
        return 0
    print(_refusal(root))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
