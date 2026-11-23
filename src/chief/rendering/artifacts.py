"""Render canonical skills, agents and rules into one target root, with the destination that owns the root."""

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from chief.targets import registry

_TOKEN = re.compile(r"\{\{(\w+):([^{}\s]+)\}\}")


class MissingFieldError(Exception):
    """Raised when a canonical file lacks a required frontmatter field."""


class UnknownTokenError(Exception):
    """Raised when a body holds a token kind that is not supported."""


@dataclass(frozen=True)
class Destination:
    """The target root and layout that every path of one render call is built from."""

    root: Path
    spec: registry.TargetSpec

    def artifact_path(self, kind: str, name: str) -> Path:
        """Return the output path of one artifact of ``kind`` named ``name``."""
        return self.root / self.spec.paths[kind].format(name=name)

    def resolve(self, body: str) -> str:
        """Replace each ``{{kind:NAME}}`` token in ``body`` with the path it names."""
        return _TOKEN.sub(lambda match: self._token_path(match[1], match[2]), body)

    def _token_path(self, kind: str, name: str) -> str:
        """Return the path a token names, raising :class:`UnknownTokenError` for an unknown kind."""
        builder = _TOKEN_PATHS.get(kind)
        if builder is None:
            raise UnknownTokenError(f"unknown token kind: {kind}")
        return str(builder(self, name))


_TOKEN_PATHS: Mapping[str, Callable[[Destination, str], Path]] = {
    "skill_dir": lambda dest, name: dest.artifact_path("skill", name).parent,
    "agent_file": lambda dest, name: dest.artifact_path("agent", name),
}


def render_artifact(target: str, root: Path, kind: str, source: str) -> list[tuple[Path, str]]:
    """Render one canonical artifact as ``(path, content)`` pairs for ``target``.

    Args:
        target: Target name registered in :data:`registry.TARGETS`.
        root: Target root directory. Only joined to paths; never read or written.
        kind: Artifact kind, one of ``skill``, ``agent`` or ``rule``.
        source: Text of one canonical file.
    """
    dest = Destination(root, registry.target_spec(target))
    fields, body = read_canonical(source)
    path = dest.artifact_path(kind, fields["name"])
    return [(path, _emit(_frontmatter(dest.spec, kind, fields), dest.resolve(body)))]


def read_canonical(source: str) -> tuple[dict[str, str], str]:
    """Split a canonical file into its flat frontmatter fields and its body, checking the required fields."""
    header, body = source.removeprefix("---\n").split("\n---\n", 1)
    fields = dict(_field(line) for line in header.splitlines())
    _require_description(fields)
    return fields, body


def _require_description(fields: Mapping[str, str]) -> None:
    """Raise :class:`MissingFieldError` when ``fields`` has no ``description``."""
    if "description" not in fields:
        raise MissingFieldError("missing required field: description")


def _field(line: str) -> tuple[str, str]:
    """Split one ``key: value`` line into its key and its unquoted value."""
    key, value = line.split(":", 1)
    return key.strip(), _unquote(value.strip())


def _unquote(value: str) -> str:
    """Remove one pair of surrounding double quotes from ``value``."""
    if len(value) > 1 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _frontmatter(spec: registry.TargetSpec, kind: str, fields: Mapping[str, str]) -> list[tuple[str, str]]:
    """Return the kept canonical keys followed by the target keys for ``kind``."""
    kept = [(key, value) for key, value in fields.items() if key not in spec.dropped]
    return [*kept, *spec.keys.get(kind, ())]


def _emit(pairs: list[tuple[str, str]], body: str) -> str:
    """Assemble the ``---`` fence, the ``key: value`` lines, the closing fence and the body."""
    header = "".join(f"{key}: {value}\n" for key, value in pairs)
    return f"---\n{header}---\n{body}"
