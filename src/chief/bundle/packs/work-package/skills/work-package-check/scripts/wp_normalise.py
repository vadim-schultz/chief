"""The rule registry: every rule by id, and the run that collects their findings."""

from collections.abc import Callable

from rule_frontmatter import check_frontmatter
from rule_harness import check_harness
from rule_links import check_links
from rule_rollout import check_rollout
from rule_structure import check_structure
from wp_model import Context, Finding

Rule = Callable[[Context], list[Finding]]

RULES: dict[str, Rule] = {
    "links": check_links,
    "frontmatter": check_frontmatter,
    "rollout": check_rollout,
    "harness": check_harness,
    "structure": check_structure,
}


def run_rules(ctx: Context) -> list[Finding]:
    """Return the findings of every registered rule, in registry order."""
    return [finding for rule in RULES.values() for finding in rule(ctx)]
