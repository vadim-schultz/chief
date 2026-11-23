"""Contract checks for the OKF reference bundles that the skills carry (OKF v0.3)."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE = REPO_ROOT / "src" / "chief" / "bundle"
OKF_VERSION = "0.3"
ROOT_KEYS = frozenset({"okf_version", "title", "description", "license"})
RESERVED = frozenset({"index.md", "log.md"})
FENCE = "---"
KEY_LINE = re.compile(r"^([A-Za-z_][\w-]*):(?: (.*))?$")
DEMO = "packs/demo/skills/demo/reference"
CONCEPT = '---\ntype: Reference\ntitle: "Topic"\ndescription: "A topic."\n---\n\nBody.\n'


def _reference_dirs(root: Path) -> list[Path]:
    """Return every skill ``reference/`` folder under ``root``, in path order."""
    return sorted(root.glob("packs/*/skills/*/reference"))


def _reference_files(root: Path) -> list[Path]:
    """Return every concept file under a reference folder, excluding reserved names."""
    return [
        path for folder in _reference_dirs(root) for path in sorted(folder.rglob("*.md")) if path.name not in RESERVED
    ]


def _unquote(value: str) -> str:
    """Remove one pair of surrounding double quotes from ``value``."""
    return value[1:-1] if len(value) > 1 and value[0] == value[-1] == '"' else value


def _pair(line: str) -> tuple[str, str] | None:
    """Return the key and raw value of one flat frontmatter line, or None when YAML would reject it."""
    match = KEY_LINE.match(line)
    if match is None:
        return None
    value = match[2] or ""
    if not value.startswith(('"', "[", "{")) and ": " in value:
        return None
    return match[1], value


def _frontmatter(text: str) -> dict[str, str] | None:
    """Return the flat frontmatter of ``text``, or None when it is absent, not flat, or repeats a key."""
    lines = text.splitlines()
    if not lines or lines[0] != FENCE or FENCE not in lines[1:]:
        return None
    parsed = [_pair(line) for line in lines[1 : lines.index(FENCE, 1)]]
    pairs = [pair for pair in parsed if pair is not None]
    if len(pairs) != len(parsed) or len({key for key, _ in pairs}) != len(pairs):
        return None
    return dict(pairs)


def _meta(path: Path) -> dict[str, str] | None:
    """Return the flat frontmatter of the file at ``path``."""
    return _frontmatter(path.read_text(encoding="utf-8"))


def _type_of(path: Path) -> str:
    """Return the unquoted ``type`` of a concept file, or an empty string."""
    return _unquote((_meta(path) or {}).get("type", ""))


def _invalid_concepts(root: Path) -> list[str]:
    """Return each reference concept whose frontmatter does not parse, or whose type is empty."""
    return [path.relative_to(root).as_posix() for path in _reference_files(root) if not _type_of(path)]


def _listed(path: Path) -> bool:
    """Return whether the index beside ``path`` has the line ``* [title](name) - description``."""
    meta = _meta(path) or {}
    index = path.parent / "index.md"
    if not index.is_file() or not meta:
        return False
    title = _unquote(meta.get("title", ""))
    description = _unquote(meta.get("description", ""))
    line = f"* [{title}]({path.name}) - {description}"
    return line in index.read_text(encoding="utf-8").splitlines()


def _unlisted(root: Path) -> list[str]:
    """Return each reference concept that its folder's index does not list with its title and description."""
    return [path.relative_to(root).as_posix() for path in _reference_files(root) if not _listed(path)]


def _root_meta_ok(text: str) -> bool:
    """Return whether a bundle-root index has only bundle keys and declares the OKF version."""
    fields = _frontmatter(text)
    return fields is not None and set(fields) <= ROOT_KEYS and _unquote(fields.get("okf_version", "")) == OKF_VERSION


def _index_broken(index: Path, folder: Path) -> bool:
    """Return whether ``index`` breaks §8: subdirectory frontmatter, or a root index without the version."""
    text = index.read_text(encoding="utf-8")
    if index.parent != folder:
        return text.startswith(FENCE + "\n")
    return not _root_meta_ok(text)


def _index_hits(root: Path) -> list[str]:
    """Return each index under a reference folder that breaks §8."""
    return [
        index.relative_to(root).as_posix()
        for folder in _reference_dirs(root)
        for index in sorted(folder.rglob("index.md"))
        if _index_broken(index, folder)
    ]


def _plant(root: Path, name: str, text: str) -> None:
    """Write one planted file under ``root`` for a negative-path test."""
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(text, encoding="utf-8")


def test_every_reference_concept_is_typed() -> None:
    assert _reference_files(BUNDLE)
    assert _invalid_concepts(BUNDLE) == []


def test_reference_file_without_type_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, f"{DEMO}/topic.md", '---\ntitle: "Topic"\n---\n\nBody.\n')
    assert _invalid_concepts(tmp_path) == [f"{DEMO}/topic.md"]


def test_unquoted_colon_in_frontmatter_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, f"{DEMO}/topic.md", "---\ntype: Reference\ndescription: Steps: triage\n---\n\nBody.\n")
    assert _invalid_concepts(tmp_path) == [f"{DEMO}/topic.md"]


def test_index_lists_every_concept_with_its_description() -> None:
    assert _reference_files(BUNDLE)
    assert _unlisted(BUNDLE) == []


def test_concept_missing_from_index_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, f"{DEMO}/index.md", '---\nokf_version: "0.3"\n---\n\n# Demo\n')
    _plant(tmp_path, f"{DEMO}/topic.md", CONCEPT)
    assert _unlisted(tmp_path) == [f"{DEMO}/topic.md"]


def test_index_frontmatter_is_limited_to_bundle_roots() -> None:
    assert _reference_files(BUNDLE)
    assert _index_hits(BUNDLE) == []


def test_subdirectory_index_with_frontmatter_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, f"{DEMO}/sub/index.md", '---\nokf_version: "0.3"\n---\n\n# Sub\n')
    assert _index_hits(tmp_path) == [f"{DEMO}/sub/index.md"]
