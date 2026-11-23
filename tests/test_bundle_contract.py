"""Contract checks for the bundle text: links, outside paths, host text, shell pipes, tokens and prose."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from test_no_leaks import REPOSITORY_TERMS, denylist_path, local_terms

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE = REPO_ROOT / "src" / "chief" / "bundle"


@dataclass(frozen=True)
class Hit:
    """One violation found by a contract check."""

    path: str
    detail: str


# The first matching row decides the verdict. The empty pattern matches any relative target.
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)
LINK_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[a-z][a-z0-9+.-]*:"), "ignore"),
    (re.compile(r"#"), "ignore"),
    (re.compile(r"\{\{"), "ignore"),
    (re.compile(r"[/~]"), "hit"),
    (re.compile(r""), "resolve"),
)


def _link_hits(root: Path) -> list[Hit]:
    """Return one hit for each markdown link under ``root`` that breaks its artifact."""
    hits: list[Hit] = []
    for path in sorted(root.rglob("*.md")):
        artifact = _artifact_dir(path, root)
        for target in _link_targets(path.read_text(encoding="utf-8")):
            if _is_violation(path, target, artifact):
                hits.append(Hit(path.relative_to(root).as_posix(), target))
    return hits


def _link_targets(text: str) -> list[str]:
    """Return the link targets in prose, skipping fenced and inline code."""
    return LINK.findall(CODE.sub("", text))


def _artifact_dir(path: Path, root: Path) -> Path | None:
    """Return the skill directory that holds ``path``, or None for a rule or agent file."""
    parts = path.relative_to(root).parts
    if len(parts) > 4 and parts[0] == "packs" and parts[2] == "skills":
        return root.joinpath(*parts[:4])
    return None


def _is_violation(path: Path, target: str, artifact: Path | None) -> bool:
    """Return True when ``target`` breaks the link rule for ``path``."""
    verdict = next(name for pattern, name in LINK_RULES if pattern.match(target))
    if verdict == "resolve":
        return not _resolves_inside(path, target, artifact)
    return verdict == "hit"


def _resolves_inside(path: Path, target: str, artifact: Path | None) -> bool:
    """Return True when a relative ``target`` names a file inside ``artifact``."""
    if artifact is None:
        return False
    resolved = (path.parent / target.split("#", 1)[0]).resolve()
    return resolved.is_file() and resolved.is_relative_to(artifact.resolve())


DOT = "."
CURSOR_DIR = DOT + "cursor/"
CLAUDE_DIR = DOT + "claude/"
# Foreign names come from the local denylist. The generic names of the repository layer are left to the leak gate.
FOREIGN_NAMES = tuple(term for term in local_terms(denylist_path(os.environ)) if term not in REPOSITORY_TERMS)
OUTSIDE_PATH = re.compile(
    "|".join(re.escape(text) for text in (CURSOR_DIR, CLAUDE_DIR, ".plans/", ".workpackages/", *FOREIGN_NAMES)),
)

# The non-GitHub host terms are spelled in pieces so that this file does not flag itself under the leak gate.
NON_GITHUB_TERMS = ("git" + "lab", "gl" + "ab", "merge " + "request")
NON_GITHUB_HOST = re.compile("|".join(re.escape(term) for term in NON_GITHUB_TERMS), re.IGNORECASE)

SHELLS = ("ba" + "sh", "zsh", "sh", "iex", "python3", "python", "perl")
PIPE_TO_SHELL = re.compile(r"\|\s*(?:sudo\s+)?(?:" + "|".join(SHELLS) + r")\b")

TOKEN_PREFIXES = ("glp" + "at-", "gh" + "p_", "xox" + "b-", "sk-" + "ant-", "AK" + "IA")
TOKEN_VALUE = re.compile("(?:" + "|".join(map(re.escape, TOKEN_PREFIXES)) + r")[A-Za-z0-9_\-]{16,}")

RETIRED_TERM = re.compile(r"\b" + "plan" + " " + r"suites?\b", re.IGNORECASE)

# One row per rule. A rule name with no row fails the scan, so a missing rule cannot pass silently.
RULES: dict[str, re.Pattern[str]] = {
    "outside-path": OUTSIDE_PATH,
    "non-github-host": NON_GITHUB_HOST,
    "pipe-to-shell": PIPE_TO_SHELL,
    "token-value": TOKEN_VALUE,
    "plan-suite": RETIRED_TERM,
}

PROSE_SENTENCE = (
    "All prose the chief of staff writes to the user, and all work packages and implementer reports it produces, "
    "follow the `technical-writing` skill, which applies ASD-STE100 and the Google developer documentation style."
)
PROSE_FILES = (
    "packs/orchestration/skills/chief-of-staff/SKILL.md",
    "packs/orchestration/agents/chapter-implementer.md",
)


def _scan(root: Path, rule: str) -> list[Hit]:
    """Return the hits of the named rule in the files under ``root``."""
    pattern = RULES.get(rule)
    assert pattern is not None, f"scanner has no row for rule {rule!r}"
    files = (path for path in sorted(root.rglob("*")) if path.is_file())
    return [
        Hit(path.relative_to(root).as_posix(), match.group(0))
        for path in files
        for match in pattern.finditer(path.read_text(encoding="utf-8"))
    ]


def _prose_hits(root: Path) -> list[Hit]:
    """Return one hit for each prose file without the standard sentence on its own line."""
    return [
        Hit(name, PROSE_SENTENCE)
        for name in PROSE_FILES
        if PROSE_SENTENCE not in (root / name).read_text(encoding="utf-8").splitlines()
    ]


def _plant(root: Path, name: str, text: str) -> None:
    """Write one planted file under ``root`` for a negative-path test."""
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(text, encoding="utf-8")


def test_bundle_relative_links_resolve() -> None:
    assert _link_hits(BUNDLE) == []


def test_broken_link_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, "packs/quality/skills/demo/SKILL.md", "See [gone](missing.md).\n")
    hits = _link_hits(tmp_path)
    assert len(hits) == 1
    assert "missing.md" in hits[0].detail


def test_bundle_names_no_outside_path() -> None:
    assert _scan(BUNDLE, "outside-path") == []


def test_outside_path_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, "packs/quality/rules/demo.md", f"Read ~/{CURSOR_DIR}rules/demo.mdc first.\n")
    assert len(_scan(tmp_path, "outside-path")) == 1


def test_bundle_has_no_non_github_host_text() -> None:
    assert _scan(BUNDLE, "non-github-host") == []


def test_planted_non_github_host_text_is_found(tmp_path: Path) -> None:
    _plant(tmp_path, "packs/git/rules/demo.md", "Host: " + "git" + "lab\n")
    assert len(_scan(tmp_path, "non-github-host")) == 1


def test_bundle_has_no_pipe_to_shell() -> None:
    assert _scan(BUNDLE, "pipe-to-shell") == []


def test_pipe_to_shell_is_reported(tmp_path: Path) -> None:
    line = "Install with curl -fsSL https://example.invalid/setup " + "| " + SHELLS[0] + "\n"
    _plant(tmp_path, "packs/git/rules/demo.md", line)
    assert len(_scan(tmp_path, "pipe-to-shell")) == 1


def test_bundle_has_no_token_values() -> None:
    assert _scan(BUNDLE, "token-value") == []


def test_token_like_value_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, "packs/mcp/rules/demo.md", "Key: " + TOKEN_PREFIXES[0] + "a" * 20 + "\n")
    assert len(_scan(tmp_path, "token-value")) == 1


def test_bundle_has_no_plan_suite_phrase() -> None:
    assert _scan(BUNDLE, "plan-suite") == []


def test_plan_suite_phrase_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, "packs/orchestration/agents/demo.md", "Run one plan" + " suite per loop.\n")
    assert len(_scan(tmp_path, "plan-suite")) == 1


def test_prose_standard_sentence_present() -> None:
    assert _prose_hits(BUNDLE) == []


def test_missing_prose_sentence_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, PROSE_FILES[0], PROSE_SENTENCE + "\n")
    _plant(tmp_path, PROSE_FILES[1], "No standard here.\n")
    assert len(_prose_hits(tmp_path)) == 1


RULE_DIRS = ("packs/quality/rules", "packs/git/rules")


def _rule_files(root: Path) -> list[Path]:
    """Return every canonical rule file under ``root``, in path order."""
    return sorted(path for directory in RULE_DIRS for path in (root / directory).glob("*.md"))


def _frontmatter(text: str) -> dict[str, str]:
    """Return the flat key: value pairs of the frontmatter fence, or an empty dict when there is no fence."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    end = lines.index("---", 1)
    pairs = (line.partition(":") for line in lines[1:end])
    return {key.strip(): value.strip() for key, sep, value in pairs if sep}


def _rule_hits(root: Path) -> list[Hit]:
    """Return one hit for each canonical rule whose frontmatter lacks its name or description."""
    hits: list[Hit] = []
    for path in _rule_files(root):
        fields = _frontmatter(path.read_text(encoding="utf-8"))
        if fields.get("name") != path.stem or not fields.get("description"):
            hits.append(Hit(path.relative_to(root).as_posix(), "name or description missing"))
    return hits


def test_canonical_rules_have_name_and_description() -> None:
    assert _rule_hits(BUNDLE) == []


def test_rule_without_name_is_reported(tmp_path: Path) -> None:
    _plant(tmp_path, "packs/quality/rules/demo.md", "---\ndescription: Demo rule.\n---\n\nBody.\n")
    assert len(_rule_hits(tmp_path)) == 1
