"""Render the findings as the JSON report that the check script prints."""

import json
from collections.abc import Sequence

from wp_model import Finding


def render_report(findings: Sequence[Finding]) -> str:
    """Return the JSON report, one object per finding under the key ``findings``."""
    return json.dumps({"findings": [_as_dict(finding) for finding in findings]}, indent=2)


def _as_dict(finding: Finding) -> dict[str, str]:
    """Return ``finding`` as a JSON-ready mapping, with its severity as text."""
    return {
        "severity": finding.severity.value,
        "rule": finding.rule,
        "path": finding.path,
        "message": finding.message,
    }
