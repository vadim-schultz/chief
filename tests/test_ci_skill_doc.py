"""Contract tests for the ci-harness skill document: its links, its red rule and its outside-path rule."""

from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

from test_ci_profiles import PROFILES
from test_no_leaks import denylist_path, folder_surfaces, local_terms, scan

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "src" / "chief" / "bundle" / "packs" / "quality" / "skills" / "ci-harness"


SKILL_MD = SKILL_DIR / "SKILL.md"
LINK_TARGET = re.compile(r"\]\(([^)\s#]+)\)")
OUTSIDE_PATHS = ("~/", ".cursor/", ".claude/", ".plans/", ".workpackages/", "tox.ini")


def _skill_text() -> str:
    """Return the text of the skill document, failing unless the file exists."""
    assert SKILL_MD.is_file(), f"missing skill document: {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def test_skill_links_resolve_to_templates() -> None:
    links = LINK_TARGET.findall(_skill_text())
    for profile in PROFILES:
        assert f"templates/{profile}/ci.sh" in links, f"no link to the {profile} template"
    for link in links:
        assert (SKILL_DIR / link).is_file(), f"dangling link: {link}"


def test_skill_states_red_rule() -> None:
    text = _skill_text()
    assert "a red test must compile before it fails" in text.lower(), "red rule for compiled languages is missing"
    assert "ci: missing tool" in text, "blocked-toolchain rule is missing"


def test_skill_names_no_outside_path() -> None:
    """No file of the skill names an outside path or a term of the local denylist; failures list file names only."""
    _skill_text()
    hits = scan(folder_surfaces(SKILL_DIR), (OUTSIDE_PATHS, local_terms(denylist_path(os.environ))))
    assert hits == Counter(), f"outside text in {sorted(hits)}"
