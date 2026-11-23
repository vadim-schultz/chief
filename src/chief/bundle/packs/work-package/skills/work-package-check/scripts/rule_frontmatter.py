"""Rule ``frontmatter``: flag an unreadable chapter frontmatter and add a missing ``execution`` key."""

from pathlib import Path

from wp_frontmatter import read_frontmatter
from wp_frontmatter_edit import set_field
from wp_io import write_text_atomic
from wp_model import Context, Finding, flag, normalised
from wp_parser import chapter_files

RULE = "frontmatter"
EXECUTION = "execution"
EXECUTION_LINE = "execution: chapter-implementer"


def check_frontmatter(ctx: Context) -> list[Finding]:
    """Return one finding for each chapter whose frontmatter is unreadable or lacks ``execution``."""
    return [finding for path in chapter_files(ctx.folder) for finding in _check_chapter(ctx, path)]


def _check_chapter(ctx: Context, path: Path) -> list[Finding]:
    """Return the findings of one chapter, writing the missing ``execution`` key in place."""
    text = path.read_text(encoding="utf-8")
    result = read_frontmatter(text)
    if result.error is not None:
        return [flag(RULE, ctx.relative(path), f"unreadable frontmatter: {result.error}")]
    if EXECUTION in result.fields:
        return []
    write_text_atomic(path, set_field(text, EXECUTION, EXECUTION_LINE))
    return [normalised(RULE, ctx.relative(path), f"added {EXECUTION_LINE}")]
