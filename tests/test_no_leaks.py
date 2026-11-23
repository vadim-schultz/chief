"""Local leak gate: scans the tracked tree, the history and the built artifacts for denylist terms.

The repository layer holds generic names. The local layer reads the denylist file named by
``CHIEF_LEAK_DENYLIST``, which lives outside the repository. Strict mode runs when ``CHIEF_LEAK_STRICT``
is 1, or when the flag is unset and the release marker ``CI_RELEASE_RUN`` is 1. Otherwise the gate runs
in ratchet mode. Terms are spelled in pieces here so that this file does not flag itself. The scanner
exempts only the private work package folder.
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import TypedDict

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXEMPT_PREFIX = ".workpackages/private-distribution/"
LOCK_FILE = "uv.lock"
DENYLIST_ENV = "CHIEF_LEAK_DENYLIST"
BASELINE_ENV = "CHIEF_LEAK_BASELINE"
STRICT_ENV = "CHIEF_LEAK_STRICT"
DEFAULT_DENYLIST = "~/.config/chief/leak-denylist.txt"
DEFAULT_BASELINE = "~/.config/chief/leak-baseline.json"
PACKAGE_PREFIX = "package:"
BASELINE_SCHEMA = 1
CLEAN_EMAIL = "test@example.invalid"
RELEASE_ENV = "CI_RELEASE_RUN"
SDIST_SUFFIX = ".tar.gz"


def _spelled(*parts: str) -> str:
    """Join ``parts`` so that a term never appears whole in this file."""
    return "".join(parts)


PLANTED_TERM = _spelled("confl", "uence")

# The repository layer: generic names that no tracked file may carry.
REPOSITORY_TERMS: tuple[str, ...] = (
    _spelled("git", "lab"),
    _spelled("gl", "ab"),
    _spelled("j", "ira"),
    PLANTED_TERM,
    _spelled("atlas", "sian"),
    _spelled("artif", "actory"),
    _spelled("sonar", "qube"),
    _spelled("dependency", "-track"),
    _spelled("brick", "maker"),
    _spelled("cook", "iecutter"),
    _spelled("merge ", "request"),
)


class BaselineDocument(TypedDict):
    """On-disk shape of the baseline file: hit counts per key, outside the repository."""

    schema_version: int
    hits: dict[str, int]


HISTORY_FORMAT = "%H%x1f%ae%x1f%ce%x1f%B%x1e"
REGISTRY_HOST = re.compile(r"https?://([^/\s\"]+)")


def scan(surfaces: Iterable[tuple[str, str]], groups: Sequence[tuple[str, ...]]) -> Counter[str]:
    """Return the hit count per key over ``surfaces``, each a (key, text) pair of a tree, a history or an artifact."""
    patterns = _patterns(groups)
    hits: Counter[str] = Counter()
    for key, text in surfaces:
        hits[key] += _count(text, patterns)
    return Counter({key: count for key, count in hits.items() if count})


def artifact_hits(folder: Path, label: str, groups: Sequence[tuple[str, ...]]) -> Counter[str]:
    """Return the hit count per key for the unpacked artifact at ``folder``, with keys of the form ``label:path``."""
    return scan(folder_surfaces(folder, f"{label}:"), groups)


def folder_surfaces(root: Path, prefix: str = "") -> Iterator[tuple[str, str]]:
    """Yield a (key, text) pair for each file under ``root``, where each key starts with ``prefix``."""
    names = [path.relative_to(root).as_posix() for path in sorted(root.rglob("*"))]
    yield from _named_files(root, names, prefix)


def _named_files(root: Path, names: Iterable[str], prefix: str = "") -> Iterator[tuple[str, str]]:
    """Yield a (key, text) pair for each name under ``root`` that the gate scans, keyed by ``prefix`` and the name."""
    for name in names:
        if _is_scanned(root, name):
            yield f"{prefix}{name}", f"{name}\n{_scanned_body(root / name, name)}"


def _patterns(groups: Sequence[tuple[str, ...]]) -> list[re.Pattern[str]]:
    """Compile one case-insensitive pattern per non-empty group of terms."""
    return [re.compile("|".join(map(re.escape, terms)), re.IGNORECASE) for terms in groups if terms]


def _count(text: str, patterns: Sequence[re.Pattern[str]]) -> int:
    """Return the number of matches of all ``patterns`` in ``text``."""
    return sum(len(pattern.findall(text)) for pattern in patterns)


def tree_surfaces(root: Path) -> Iterator[tuple[str, str]]:
    """Yield a (key, text) pair for each tracked file and for each commit reachable from HEAD."""
    yield from _file_surfaces(root)
    yield from _history_surfaces(root)


def _file_surfaces(root: Path) -> Iterator[tuple[str, str]]:
    """Yield the file name and content of each tracked file outside the exempt folder."""
    yield from _named_files(root, _git(root, "ls-files", "-z").split("\0"))


def _is_scanned(root: Path, name: str) -> bool:
    """Return True when ``name`` is a file under ``root`` that the gate scans, which excludes the exempt folder."""
    return bool(name) and not name.startswith(EXEMPT_PREFIX) and (root / name).is_file()


def _scanned_body(path: Path, name: str) -> str:
    """Return the text scanned for a file: its registry hosts for the lock file, else its whole content."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if name == LOCK_FILE:
        return "\n".join(REGISTRY_HOST.findall(text))
    return text


def _history_surfaces(root: Path) -> Iterator[tuple[str, str]]:
    """Yield the author and committer addresses and the message of each commit reachable from HEAD."""
    if not _has_head(root):
        return
    for record in _git(root, "log", f"--format={HISTORY_FORMAT}", "HEAD").split("\x1e"):
        if not record.strip():
            continue
        sha, author, committer, message = record.strip().split("\x1f", 3)
        yield f"git:{sha}", "\n".join((author, committer, message))


def _has_head(root: Path) -> bool:
    """Return True when the repository at ``root`` has a commit to scan."""
    probe = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "--quiet", "HEAD"],
        capture_output=True,
        check=False,
    )
    return probe.returncode == 0


def _git(root: Path, *args: str) -> str:
    """Return the standard output of a git command run in ``root``."""
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def local_terms(denylist: Path) -> tuple[str, ...]:
    """Return the terms of the local denylist, where ``package:`` lines give their rest as the term."""
    if not denylist.is_file():
        return ()
    terms = (_term(line) for line in denylist.read_text(encoding="utf-8").splitlines())
    return tuple(term for term in terms if term and not term.startswith("#"))


def _term(line: str) -> str:
    """Return the term that one denylist line names."""
    return line.strip().removeprefix(PACKAGE_PREFIX).strip()


def active_groups(environ: Mapping[str, str]) -> tuple[tuple[str, ...], ...]:
    """Return the pattern groups of both layers: the repository terms and the local denylist."""
    return (REPOSITORY_TERMS, local_terms(denylist_path(environ)))


def denylist_path(environ: Mapping[str, str]) -> Path:
    """Return the denylist path named by ``environ``, or the default under the user config."""
    return _configured_path(environ, DENYLIST_ENV, DEFAULT_DENYLIST)


def baseline_path(environ: Mapping[str, str]) -> Path:
    """Return the baseline path named by ``environ``, or the default under the user config."""
    return _configured_path(environ, BASELINE_ENV, DEFAULT_BASELINE)


def _configured_path(environ: Mapping[str, str], variable: str, default: str) -> Path:
    """Return the path that ``variable`` names in ``environ``, or ``default`` when it is unset or empty."""
    return Path(environ.get(variable) or default).expanduser()


def strict_requested(environ: Mapping[str, str]) -> bool:
    """Return True when ``environ`` sets the strict flag to ``1``, or, with the flag unset, marks a release run."""
    if STRICT_ENV in environ:
        return environ[STRICT_ENV] == "1"
    return environ.get(RELEASE_ENV) == "1"


def is_strict_without_denylist(denylist: Path, *, strict: bool) -> bool:
    """Return True when strict mode runs without the local denylist, so the local layer would pass unchecked."""
    return strict and not denylist.is_file()


def failures(hits: Mapping[str, int], baseline: Mapping[str, int], *, strict: bool) -> list[str]:
    """Return the keys that fail: any hit in strict mode, else each key above its baseline count."""
    if strict:
        return _strict_failures(hits)
    return _ratchet_failures(hits, baseline)


def _strict_failures(hits: Mapping[str, int]) -> list[str]:
    """Return every key with at least one hit."""
    return sorted(key for key, count in hits.items() if count)


def _ratchet_failures(hits: Mapping[str, int], baseline: Mapping[str, int]) -> list[str]:
    """Return each key whose hit count exceeds its baseline count, where a key without a baseline has zero."""
    return sorted(key for key, count in hits.items() if count > baseline.get(key, 0))


def read_baseline(path: Path) -> dict[str, int]:
    """Return the baseline hit counts at ``path``, or none when the file is absent."""
    if not path.is_file():
        return {}
    document: BaselineDocument = json.loads(path.read_text(encoding="utf-8"))
    version = document.get("schema_version")
    if version != BASELINE_SCHEMA:
        raise ValueError(f"baseline schema_version {version} is not supported; expected {BASELINE_SCHEMA}")
    return dict(document["hits"])


def write_baseline(path: Path, hits: Mapping[str, int]) -> None:
    """Write ``hits`` as the baseline at ``path``."""
    document: BaselineDocument = {"schema_version": BASELINE_SCHEMA, "hits": dict(sorted(hits.items()))}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def _write_baseline_command() -> None:
    """Scan the repository, write the baseline, and print the number of keys it holds."""
    hits = scan(tree_surfaces(REPO_ROOT), active_groups(os.environ))
    write_baseline(baseline_path(os.environ), hits)
    print(f"baseline written: {len(hits)} keys")


def _report_command() -> None:
    """Print each scanned key with its hit count. Paths and numbers only, never terms."""
    for key, count in sorted(scan(tree_surfaces(REPO_ROOT), active_groups(os.environ)).items()):
        print(f"{count}\t{key}")


COMMANDS: dict[str, Callable[[], None]] = {
    "--write-baseline": _write_baseline_command,
    "--report": _report_command,
}


def _cli(argv: Sequence[str]) -> int:
    """Run the command that the single argument in ``argv`` names; return 2 for any other argument list."""
    if len(argv) != 1 or argv[0] not in COMMANDS:
        print(f"usage: test_no_leaks.py {' | '.join(COMMANDS)}", file=sys.stderr)
        return 2
    COMMANDS[argv[0]]()
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))


def _tree(root: Path, files: Mapping[str, str], *, email: str = CLEAN_EMAIL, message: str = "chore: seed") -> Path:
    """Create a git repository at ``root`` that holds ``files`` in one commit by the given author address."""
    _write_files(root, files)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    _commit_all(root, email, message)
    return root


def _write_files(root: Path, files: Mapping[str, str]) -> None:
    """Write each file of ``files`` under ``root``, creating folders as needed."""
    for name, text in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def _commit_all(root: Path, email: str, message: str) -> None:
    """Stage every file under ``root`` and commit it, with ``email`` as the author address."""
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": CLEAN_EMAIL,
    }
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "-c", "commit.gpgsign=false", "commit", "-q", "-m", message],
        check=True,
        env=env,
    )


def _built_folders(workdir: Path) -> Iterator[tuple[str, Path]]:
    """Yield the label and the unpacked package root of the sdist and the wheel built from the working tree."""
    dist = _build(_copy_tree(workdir / "source"), workdir / "dist")
    archives = sorted([*dist.glob(f"*{SDIST_SUFFIX}"), *dist.glob("*.whl")])
    assert sorted(_kind(archive) for archive in archives) == ["sdist", "wheel"], (
        f"expected one sdist and one wheel in {dist}"
    )
    for archive in archives:
        yield _kind(archive), _unpack(archive, workdir / "unpacked" / archive.name)


def _copy_tree(dest: Path) -> Path:
    """Copy the files that git lists as tracked or unignored into ``dest``, without ``.git``."""
    for name in _git(REPO_ROOT, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0"):
        source = REPO_ROOT / name
        if name and source.is_file():
            (dest / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest / name)
    return dest


def _build(source: Path, dist: Path) -> Path:
    """Build the sdist and the wheel of ``source`` into ``dist`` and return ``dist``."""
    env = {**os.environ, "SETUPTOOLS_SCM_PRETEND_VERSION": "0.0.0"}
    built = subprocess.run(
        ["uv", "build", "--sdist", "--wheel", "--out-dir", str(dist), str(source)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if built.returncode != 0:
        pytest.fail(f"uv build failed:\n{built.stdout}\n{built.stderr}")
    return dist


def _kind(archive: Path) -> str:
    """Return ``sdist`` for a source distribution archive and ``wheel`` for any other archive."""
    return "sdist" if archive.name.endswith(SDIST_SUFFIX) else "wheel"


def _unpack(archive: Path, folder: Path) -> Path:
    """Unpack ``archive`` into the new, empty ``folder`` and return the package root inside it."""
    folder.mkdir(parents=True)
    if _kind(archive) == "sdist":
        with tarfile.open(archive) as tar:
            tar.extractall(folder, filter="data")
        return folder / archive.name.removesuffix(SDIST_SUFFIX)
    with zipfile.ZipFile(archive) as zipped:
        zipped.extractall(folder)
    return folder


def _archive(path: Path, files: Mapping[str, str]) -> Path:
    """Write ``files`` into a new archive at ``path``: an sdist holds them under one top folder, a wheel at its root."""
    if _kind(path) == "sdist":
        top = path.name.removesuffix(SDIST_SUFFIX)
        with tarfile.open(path, "w:gz") as tar:
            for name, text in files.items():
                data = text.encode("utf-8")
                info = tarfile.TarInfo(f"{top}/{name}")
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
        return path
    with zipfile.ZipFile(path, "w") as zipped:
        for name, text in files.items():
            zipped.writestr(name, text)
    return path


def test_leak_gate_ignores_clean_tree(tmp_path: Path) -> None:
    root = _tree(tmp_path / "clean", {"README.md": "A plain readme.\n"})

    assert scan(tree_surfaces(root), (REPOSITORY_TERMS,)) == Counter()


def test_leak_gate_flags_planted_token(tmp_path: Path) -> None:
    root = _tree(tmp_path / "planted", {"README.md": f"Notes on {PLANTED_TERM}.\n"})

    hits = scan(tree_surfaces(root), (REPOSITORY_TERMS,))

    assert hits == Counter({"README.md": 1})
    assert failures(hits, {}, strict=True) == ["README.md"]


@pytest.mark.parametrize(
    ("files", "email", "message"),
    [
        pytest.param({f"{PLANTED_TERM}-notes.md": "clean\n"}, CLEAN_EMAIL, "chore: seed", id="file-name"),
        pytest.param({"README.md": "clean\n"}, f"test@{PLANTED_TERM}.example.invalid", "chore: seed", id="address"),
        pytest.param({"README.md": "clean\n"}, CLEAN_EMAIL, f"chore: {PLANTED_TERM}", id="message"),
        pytest.param(
            {LOCK_FILE: f'source = {{ registry = "https://packages.{PLANTED_TERM}.example.invalid/simple" }}\n'},
            CLEAN_EMAIL,
            "chore: seed",
            id="lock-host",
        ),
    ],
)
def test_leak_gate_flags_planted_term_on_each_surface(
    tmp_path: Path,
    files: dict[str, str],
    email: str,
    message: str,
) -> None:
    root = _tree(tmp_path / "surface", files, email=email, message=message)

    hits = scan(tree_surfaces(root), (REPOSITORY_TERMS,))

    assert len(hits) == 1
    assert sum(hits.values()) == 1


def test_uv_lock_hashes_are_not_scanned(tmp_path: Path) -> None:
    root = _tree(tmp_path / "lock", {LOCK_FILE: f'[[package]]\nhash = "{PLANTED_TERM}"\n'})

    assert scan(tree_surfaces(root), (REPOSITORY_TERMS,)) == Counter()


def test_private_distribution_folder_is_exempt(tmp_path: Path) -> None:
    root = _tree(tmp_path / "exempt", {f"{EXEMPT_PREFIX}plan.md": f"{PLANTED_TERM}\n", "README.md": "clean\n"})

    assert scan(tree_surfaces(root), (REPOSITORY_TERMS,)) == Counter()


def test_other_workpackage_folder_is_scanned(tmp_path: Path) -> None:
    root = _tree(tmp_path / "other", {".workpackages/other/plan.md": f"{PLANTED_TERM}\n"})

    assert scan(tree_surfaces(root), (REPOSITORY_TERMS,)) == Counter({".workpackages/other/plan.md": 1})


def test_ratchet_allows_hits_within_baseline() -> None:
    assert failures({"a.md": 2}, {"a.md": 2}, strict=False) == []


def test_ratchet_fails_when_a_file_exceeds_its_baseline() -> None:
    assert failures({"a.md": 3, "b.md": 1}, {"a.md": 2}, strict=False) == ["a.md", "b.md"]


def test_strict_passes_a_clean_tree() -> None:
    assert failures({}, {"a.md": 2}, strict=True) == []


def test_strict_fails_on_a_hit_within_baseline() -> None:
    assert failures({"a.md": 2}, {"a.md": 2}, strict=True) == ["a.md"]


def test_leak_paths_and_strict_flag_come_from_environment(tmp_path: Path) -> None:
    environ = {DENYLIST_ENV: str(tmp_path / "deny.txt"), BASELINE_ENV: str(tmp_path / "base.json"), STRICT_ENV: "1"}

    assert denylist_path(environ) == tmp_path / "deny.txt"
    assert baseline_path(environ) == tmp_path / "base.json"
    assert strict_requested(environ)


def test_strict_is_off_unless_flag_is_one() -> None:
    assert not strict_requested({STRICT_ENV: "0"})
    assert not strict_requested({})


def test_release_run_is_strict_by_default() -> None:
    assert strict_requested({RELEASE_ENV: "1"})


def test_explicit_flag_overrides_the_release_default() -> None:
    assert not strict_requested({RELEASE_ENV: "1", STRICT_ENV: "0"})


def test_local_denylist_reads_plain_and_package_terms(tmp_path: Path) -> None:
    denylist = tmp_path / "deny.txt"
    denylist.write_text("plain-term\npackage: old-name\n\n# note\n", encoding="utf-8")

    assert local_terms(denylist) == ("plain-term", "old-name")


def test_missing_local_denylist_adds_no_terms(tmp_path: Path) -> None:
    assert local_terms(tmp_path / "absent.txt") == ()


def test_strict_run_with_a_denylist_is_allowed(tmp_path: Path) -> None:
    denylist = tmp_path / "deny.txt"
    denylist.write_text("plain-term\n", encoding="utf-8")

    assert not is_strict_without_denylist(denylist, strict=True)


def test_strict_run_without_a_denylist_is_refused(tmp_path: Path) -> None:
    absent = tmp_path / "absent.txt"

    assert is_strict_without_denylist(absent, strict=True)
    assert not is_strict_without_denylist(absent, strict=False)


def test_baseline_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "baseline.json"

    write_baseline(path, {"a.md": 2})

    assert read_baseline(path) == {"a.md": 2}


def test_baseline_with_unknown_schema_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({"schema_version": 2, "hits": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="schema_version 2"):
        read_baseline(path)


def test_tree_stays_within_baseline() -> None:
    environ = os.environ
    strict = strict_requested(environ)

    assert not is_strict_without_denylist(denylist_path(environ), strict=strict), "strict mode needs the local denylist"
    hits = scan(tree_surfaces(REPO_ROOT), active_groups(environ))
    assert failures(hits, read_baseline(baseline_path(environ)), strict=strict) == []


STRICT_RUN = strict_requested(os.environ)


@pytest.mark.skipif(not STRICT_RUN, reason=f"strict only: set {STRICT_ENV}=1 or {RELEASE_ENV}=1")
def test_leak_gate_is_strict_after_sweep() -> None:
    """The tree and the history hold no hit in strict mode, and the strict run has its local denylist."""
    assert not is_strict_without_denylist(denylist_path(os.environ), strict=True), (
        "strict mode needs the local denylist"
    )
    hits = scan(tree_surfaces(REPO_ROOT), active_groups(os.environ))
    assert failures(hits, {}, strict=True) == []


def test_built_artifacts_are_clean(tmp_path: Path) -> None:
    """The sdist and the wheel built from the working tree hold no hit, each unpacked into its own folder."""
    hits: Counter[str] = Counter()
    for label, folder in _built_folders(tmp_path):
        hits += artifact_hits(folder, label, active_groups(os.environ))
    assert hits == Counter()


def test_artifact_scan_flags_planted_hit(tmp_path: Path) -> None:
    """A hit planted in a temporary sdist-shaped archive is reported under its artifact key."""
    archive = _archive(tmp_path / "planted-0.0.0.tar.gz", {"notes.md": f"{PLANTED_TERM}\n"})
    folder = _unpack(archive, tmp_path / "unpacked")
    label = _kind(archive)
    assert artifact_hits(folder, label, (REPOSITORY_TERMS,)) == Counter({"sdist:notes.md": 1})


@pytest.mark.parametrize("name", ["planted-0.0.0.tar.gz", "planted-0.0.0-py3-none-any.whl"], ids=["sdist", "wheel"])
def test_artifact_scan_skips_only_the_exempt_folder(tmp_path: Path, name: str) -> None:
    """The exempt work package folder is skipped in both artifact shapes, and no other folder is."""
    files = {f"{EXEMPT_PREFIX}plan.md": f"{PLANTED_TERM}\n", ".workpackages/other/plan.md": f"{PLANTED_TERM}\n"}
    archive = _archive(tmp_path / name, files)
    folder = _unpack(archive, tmp_path / "unpacked")
    label = _kind(archive)
    assert artifact_hits(folder, label, (REPOSITORY_TERMS,)) == Counter({f"{label}:.workpackages/other/plan.md": 1})
