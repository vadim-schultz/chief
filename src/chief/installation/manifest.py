"""Install manifest: the versioned document of one install target, read and written only through ManifestStore."""

import json
import os
import tempfile
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, TypeAlias

from chief.targets.locations import Locations

SCHEMA_VERSION = 1
_KNOWN_KEYS = frozenset({"schema_version", "files", "block"})

JsonValue: TypeAlias = str | int | float | bool | None | Mapping[str, "JsonValue"]


class ManifestError(Exception):
    """Raised when a manifest file cannot be read as a manifest."""


class ManifestVersionError(ManifestError):
    """Raised when a manifest carries a schema version this release does not read."""


@dataclass(frozen=True)
class Block:
    """The managed block record: its file, its markers and the sha256 of its body."""

    path: str
    begin: str
    end: str
    sha256: str


@dataclass(frozen=True)
class Manifest:
    """What one install wrote: a sha256 per file, at most one managed block, and unknown fields kept as ``extra``."""

    files: dict[str, str]
    block: Block | None
    extra: Mapping[str, JsonValue] = field(default_factory=dict)


class ManifestStore:
    """The only reader and writer of install manifest files, under the state directory of its locations."""

    def __init__(self, locations: Locations) -> None:
        """Bind the store to the state directory that ``locations`` resolves."""
        self._locations = locations

    def path(self, target: str) -> Path:
        """Return ``<state directory>/<target>.manifest.json``."""
        return self._locations.state_dir() / f"{target}.manifest.json"

    def read(self, target: str) -> Manifest:
        """Return the manifest of ``target``, or an empty manifest when none exists.

        Raises:
            ManifestVersionError: If the file carries a schema version newer than this release reads.
        """
        path = self.path(target)
        if not path.exists():
            return Manifest({}, None)
        raw = _load(path)
        _refuse_newer(path, raw)
        return _manifest_of(raw)

    def write(self, target: str, manifest: Manifest) -> None:
        """Write the manifest of ``target`` atomically, carrying ``schema_version`` and unknown fields."""
        path = self.path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        _replace_atomically(path, json.dumps(_document(manifest), indent=2))

    def delete(self, target: str) -> None:
        """Remove the manifest file of ``target`` when it exists."""
        self.path(target).unlink(missing_ok=True)


def _load(path: Path) -> dict[str, Any]:
    """Return the JSON object in ``path``; a file that is not complete JSON is refused, with its path named."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ManifestError(f"manifest {path} is not complete JSON: {error.msg}") from error


def _refuse_newer(path: Path, raw: dict[str, Any]) -> None:
    """Raise ManifestVersionError when ``raw`` carries a schema version this release does not read."""
    version = raw.get("schema_version", SCHEMA_VERSION)
    if version > SCHEMA_VERSION:
        detail = f"{path} has schema_version {version}; this release reads up to {SCHEMA_VERSION}"
        raise ManifestVersionError(detail)


def _manifest_of(raw: dict[str, Any]) -> Manifest:
    """Return the manifest that ``raw`` holds, keeping each field this release does not know."""
    block = Block(**raw["block"]) if raw["block"] else None
    extra = {key: value for key, value in raw.items() if key not in _KNOWN_KEYS}
    return Manifest(dict(raw["files"]), block, extra)


def _document(manifest: Manifest) -> dict[str, JsonValue]:
    """Return the JSON document of ``manifest``: its unknown fields, then the current schema version and entries."""
    block = None if manifest.block is None else asdict(manifest.block)
    return {**manifest.extra, "schema_version": SCHEMA_VERSION, "files": manifest.files, "block": block}


def _replace_atomically(path: Path, text: str) -> None:
    """Write ``text`` to a temporary file beside ``path``, then move it over ``path`` in one step."""
    temporary = _write_temporary(path, text)
    try:
        os.replace(temporary, path)
    except OSError:
        Path(temporary).unlink(missing_ok=True)
        raise


def _write_temporary(path: Path, text: str) -> str:
    """Write ``text`` to a new file in the directory of ``path`` and return its name."""
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(text)
    return name
