"""Rule ``harness``: a repository needs ``ci.sh`` or ``tox.ini`` at its root, or chapter C0 comes first."""

from wp_model import Context, Finding, flag

RULE = "harness"
HARNESS_FILES = ("ci.sh", "tox.ini")
MESSAGE = "no harness at the repository root: chapter C0 must be inserted first"


def check_harness(ctx: Context) -> list[Finding]:
    """Return one ``flag`` for ``ci.sh`` when the repository root holds neither harness file."""
    if any((ctx.repo_root / name).is_file() for name in HARNESS_FILES):
        return []
    return [flag(RULE, "ci.sh", MESSAGE)]
