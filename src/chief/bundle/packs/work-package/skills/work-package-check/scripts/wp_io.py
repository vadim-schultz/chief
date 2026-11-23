"""Write work package files atomically: a temporary file beside the target, then one ``os.replace``."""

import os
import shutil
import tempfile
from pathlib import Path


def write_text_atomic(path: Path, text: str) -> None:
    """Replace the text of ``path`` in one step, so that a failed write leaves the original file in place."""
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    temporary = Path(name)
    try:
        _write_descriptor(descriptor, text)
        shutil.copymode(path, temporary)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _write_descriptor(descriptor: int, text: str) -> None:
    """Write ``text`` as UTF-8 to an open file descriptor and close it."""
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(text)
