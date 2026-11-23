"""File helpers of the installer: read a text file or none, and the sha256 of what is on disk."""

import hashlib
from pathlib import Path

from chief.rendering.managed_block import ManagedBlock


def sha256(text: str) -> str:
    """Return the sha256 hex digest of ``text`` encoded as UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str | None:
    """Return the UTF-8 text of ``path``, or ``None`` when it does not exist."""
    return path.read_bytes().decode("utf-8") if path.exists() else None


def maybe_sha(text: str | None) -> str | None:
    """Return the sha256 of ``text``, or ``None`` when there is no text."""
    return None if text is None else sha256(text)


def disk_block_sha(text: str | None) -> str | None:
    """Return the sha256 of the managed block body in ``text``, or ``None`` when it holds no block."""
    return None if text is None or ManagedBlock.BEGIN not in text else sha256(ManagedBlock.body(text))
