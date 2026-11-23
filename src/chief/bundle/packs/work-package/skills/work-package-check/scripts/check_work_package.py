"""Check and normalise a work package, printing a JSON report. Always exits 0."""

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from wp_model import Context, Finding, flag
from wp_normalise import run_rules
from wp_report import render_report

SCRIPT_RULE = "script"
CURRENT_DIR = "."
CHAPTER_SECTIONS: tuple[str, ...] = (
    "## Goal",
    "## Read first",
    "## Coordination scope",
    "## Work items",
    "## Tests or document checks",
    "## Review gate",
    "## Out of scope",
    "## Verification",
    "## Refactor report",
    "## Git workflow",
)


class UsageError(Exception):
    """Raised instead of exiting when the command line cannot be parsed."""


class _Parser(argparse.ArgumentParser):
    """An argument parser that raises :class:`UsageError` instead of exiting with code 2."""

    def error(self, message: str) -> NoReturn:
        """Raise :class:`UsageError` with ``message``."""
        raise UsageError(message)


def main(argv: Sequence[str] | None = None) -> int:
    """Check the work package, print the JSON report and return 0, whatever the outcome."""
    print(render_report(_check(argv)))
    return 0


def _check(argv: Sequence[str] | None) -> list[Finding]:
    """Return the findings for one command line. A usage error becomes a script finding."""
    try:
        ctx = _parse_args(argv)
    except UsageError as error:
        return [_script_finding(str(error))]
    return _run_check(ctx)


def _run_check(ctx: Context) -> list[Finding]:
    """Return the findings of every rule, or a script finding when the folder is missing."""
    if not ctx.folder.is_dir():
        return [_script_finding(f"work package folder not found: {ctx.folder}")]
    return _run_rules_safely(ctx)


def _run_rules_safely(ctx: Context) -> list[Finding]:
    """Run every rule, turning an unexpected exception into a script finding."""
    try:
        return run_rules(ctx)
    except Exception as error:
        return [_script_finding(f"unexpected error: {error}")]


def _script_finding(message: str) -> Finding:
    """Return a ``flag`` finding for the script itself."""
    return flag(SCRIPT_RULE, CURRENT_DIR, message)


def _parse_args(argv: Sequence[str] | None) -> Context:
    """Return the run context for the command line arguments."""
    parser = _Parser(description="Check and normalise a work package.")
    parser.add_argument("folder", type=Path, help="work package folder")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="repository root")
    args = parser.parse_args(argv)
    return Context(folder=args.folder, repo_root=args.repo_root, chapter_sections=CHAPTER_SECTIONS)


if __name__ == "__main__":
    raise SystemExit(main())
