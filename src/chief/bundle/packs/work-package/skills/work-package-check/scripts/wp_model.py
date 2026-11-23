"""Severities, findings and the run context that the check script passes to every rule."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Severity(Enum):
    """How a finding was handled: fixed in place, or left for the user's decision."""

    NORMALISED = "normalised"
    FLAG = "flag"


@dataclass(frozen=True)
class Finding:
    """One report entry, with a path relative to the work package folder."""

    severity: Severity
    rule: str
    path: str
    message: str


@dataclass(frozen=True)
class Context:
    """The work package folder and the repository root of one run."""

    folder: Path
    repo_root: Path
    chapter_sections: tuple[str, ...]

    def relative(self, path: Path) -> str:
        """Return ``path`` relative to the work package folder, in POSIX form."""
        return path.relative_to(self.folder).as_posix()


def flag(rule: str, path: str, message: str) -> Finding:
    """Return a ``flag`` finding for ``rule``."""
    return Finding(Severity.FLAG, rule, path, message)


def normalised(rule: str, path: str, message: str) -> Finding:
    """Return a ``normalised`` finding for ``rule``, for a change the script made in place."""
    return Finding(Severity.NORMALISED, rule, path, message)
