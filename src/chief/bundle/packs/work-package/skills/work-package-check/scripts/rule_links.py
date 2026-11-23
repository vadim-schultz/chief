"""Rule ``links``: resolve each broken relative Markdown link to its one file, or flag it."""

import os
import re
from collections.abc import Callable
from pathlib import Path, PurePosixPath

from wp_io import write_text_atomic
from wp_model import Context, Finding, flag, normalised
from wp_parser import Link, find_links, markdown_files

RULE = "links"
SCHEME = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*:")
Outcome = tuple[Finding, str | None]
Handler = Callable[[Context, Path, str, list[Path]], Outcome]


def check_links(ctx: Context) -> list[Finding]:
    """Return one finding for each broken relative link, rewriting each link that has exactly one target."""
    return [finding for path in markdown_files(ctx.folder) for finding in _check_file(ctx, path)]


def _check_file(ctx: Context, path: Path) -> list[Finding]:
    """Return the findings of one file, and write its rewritten links."""
    text = path.read_text(encoding="utf-8")
    broken = [link for link in find_links(text) if _is_broken(path, link.target)]
    outcomes = [_resolve(ctx, path, link) for link in broken]
    rewrites = [(link, new) for link, (_, new) in zip(broken, outcomes) if new is not None]
    if rewrites:
        write_text_atomic(path, _replaced(text, rewrites))
    return [finding for finding, _ in outcomes]


def _is_broken(path: Path, target: str) -> bool:
    """Return True when ``target`` is a relative file reference that names no file beside ``path``."""
    if not _is_relative_file(target):
        return False
    return not (path.parent / _file_part(target)).exists()


def _file_part(target: str) -> str:
    """Return ``target`` without its ``#`` fragment."""
    return target.split("#", 1)[0]


def _is_relative_file(target: str) -> bool:
    """Return True for a target that is neither a URL with a scheme nor a bare ``#`` anchor."""
    return bool(target) and not SCHEME.match(target) and not target.startswith("#")


def _resolve(ctx: Context, path: Path, link: Link) -> Outcome:
    """Return the outcome for one broken link, chosen by how many files carry its file name."""
    candidates = _candidates(ctx, link.target)
    handler: Handler = _BY_CANDIDATE_COUNT[min(len(candidates), len(_BY_CANDIDATE_COUNT) - 1)]
    return handler(ctx, path, link.target, candidates)


def _no_candidate(ctx: Context, path: Path, target: str, candidates: list[Path]) -> Outcome:
    """Flag a broken link whose file name exists nowhere in the work package."""
    name = PurePosixPath(_file_part(target)).name
    return flag(RULE, ctx.relative(path), f"broken link: {target}; no file named {name} exists"), None


def _one_candidate(ctx: Context, path: Path, target: str, candidates: list[Path]) -> Outcome:
    """Rewrite a broken link to the one file that carries its file name."""
    new = _relative_target(path, candidates[0], target)
    return normalised(RULE, ctx.relative(path), f"relinked {target} to {new}"), new


def _several_candidates(ctx: Context, path: Path, target: str, candidates: list[Path]) -> Outcome:
    """Flag a broken link whose file name matches several files, and list each candidate."""
    listed = ", ".join(ctx.relative(candidate) for candidate in candidates)
    return flag(RULE, ctx.relative(path), f"broken link: {target}; candidates: {listed}"), None


# Index = candidate count, capped at the last entry: 0 -> none, 1 -> one, 2 or more -> several.
_BY_CANDIDATE_COUNT: tuple[Handler, ...] = (_no_candidate, _one_candidate, _several_candidates)


def _candidates(ctx: Context, target: str) -> list[Path]:
    """Return every file in the work package whose name equals the file name of ``target``."""
    name = PurePosixPath(_file_part(target)).name
    return [path for path in sorted(ctx.folder.rglob("*")) if path.is_file() and path.name == name]


def _relative_target(path: Path, candidate: Path, target: str) -> str:
    """Return ``candidate`` as a path relative to the folder of ``path``, keeping any ``#`` fragment of ``target``."""
    _, separator, fragment = target.partition("#")
    return Path(os.path.relpath(candidate, path.parent)).as_posix() + separator + fragment


def _replaced(text: str, rewrites: list[tuple[Link, str]]) -> str:
    """Return ``text`` with each link target replaced, working from the end so earlier offsets stay valid."""
    for link, new in sorted(rewrites, key=lambda pair: pair[0].start, reverse=True):
        text = text[: link.start] + new + text[link.end :]
    return text
