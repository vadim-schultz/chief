from pathlib import Path

import pytest

from chief.rendering.artifacts import Destination, MissingFieldError, UnknownTokenError, render_artifact
from chief.rendering.managed_block import MalformedBlockError, ManagedBlock
from chief.targets import registry

ROOT = Path("example-root")

SKILL = """\
---
name: tdd
description: Test-driven development.
disable-model-invocation: true
---

# TDD

Body.
"""

AGENT = """\
---
name: chapter-implementer
description: Implements one chapter.
---

Body.
"""

RULE = """\
---
name: tdd
description: "Test-driven development"
---

Rule body.
"""

AGENT_WITH_MODEL = """\
---
name: chapter-implementer
description: Implements one chapter.
model: inherit
---

Body.
"""

CURSOR_RULE = """\
---
name: tdd
description: Test-driven development
alwaysApply: true
---

Rule body.
"""

CLAUDE_RULE = """\
---
name: tdd
description: Test-driven development
---

Rule body.
"""

NO_DESCRIPTION = """\
---
name: tdd
---

Body.
"""

TOKEN_SKILL = """\
---
name: tdd
description: Test-driven development.
disable-model-invocation: true
---

See [tdd](tdd.md) and {{skill_dir:tdd}}.
"""

OPENCODE_SKILL = f"""\
---
name: tdd
description: Test-driven development.
---

See [tdd](tdd.md) and {ROOT / "skills" / "tdd"}.
"""

OPENCODE_AGENT = """\
---
name: chapter-implementer
description: Implements one chapter.
mode: subagent
---

Body.
"""

UNKNOWN_TOKEN_SKILL = """\
---
name: tdd
description: Test-driven development.
---

{{rule_file:tdd}}
"""


def _content_for(pairs: list[tuple[Path, str]], path: Path) -> str:
    """Assert that ``pairs`` holds exactly one output at ``path`` and return its content."""
    assert [written for written, _ in pairs] == [path]
    return pairs[0][1]


def test_cursor_paths_and_frontmatter() -> None:
    skill = _content_for(render_artifact("cursor", ROOT, "skill", SKILL), ROOT / "skills/tdd/SKILL.md")
    assert skill == SKILL

    agent = _content_for(render_artifact("cursor", ROOT, "agent", AGENT), ROOT / "agents/chapter-implementer.md")
    assert agent == AGENT_WITH_MODEL

    rule = _content_for(render_artifact("cursor", ROOT, "rule", RULE), ROOT / "rules/tdd.mdc")
    assert rule == CURSOR_RULE


def test_unknown_target_is_rejected() -> None:
    with pytest.raises(registry.UnknownTargetError):
        render_artifact("vscode", ROOT, "skill", SKILL)


def test_claude_paths_and_frontmatter() -> None:
    skill = _content_for(render_artifact("claude", ROOT, "skill", SKILL), ROOT / "skills/tdd/SKILL.md")
    assert skill == SKILL

    agent = _content_for(render_artifact("claude", ROOT, "agent", AGENT), ROOT / "agents/chapter-implementer.md")
    assert agent == AGENT_WITH_MODEL

    rule = _content_for(render_artifact("claude", ROOT, "rule", RULE), ROOT / "rules/tdd.md")
    assert rule == CLAUDE_RULE


def test_missing_description_is_rejected() -> None:
    with pytest.raises(MissingFieldError):
        render_artifact("cursor", ROOT, "skill", NO_DESCRIPTION)


def test_opencode_paths_and_frontmatter() -> None:
    skill = _content_for(render_artifact("opencode", ROOT, "skill", TOKEN_SKILL), ROOT / "skills/tdd/SKILL.md")
    assert skill == OPENCODE_SKILL

    agent = _content_for(
        render_artifact("opencode", ROOT, "agent", AGENT),
        ROOT / "agents/chapter-implementer.md",
    )
    assert agent == OPENCODE_AGENT


def test_unknown_token_is_rejected() -> None:
    with pytest.raises(UnknownTokenError):
        render_artifact("cursor", ROOT, "skill", UNKNOWN_TOKEN_SKILL)


def test_destination_names_skill_dir_token() -> None:
    dest = Destination(ROOT, registry.target_spec("cursor"))
    assert dest.resolve("{{skill_dir:x}}") == str(ROOT / "skills" / "x")


def test_destination_rejects_unknown_token_kind() -> None:
    dest = Destination(ROOT, registry.target_spec("cursor"))
    with pytest.raises(UnknownTokenError):
        dest.resolve("{{nope:x}}")


BEGIN = "<!-- chief:begin -->"
END = "<!-- chief:end -->"

INTRO_WITH_BLOCK = f"""\
Intro text.

{BEGIN}
old rule
{END}

Footer text.
"""

MANAGED_WITH_RULE = f"""\
Intro text.

{BEGIN}
Rule body.
{END}

Footer text.
"""

INTRO_ONLY = "Intro text.\n"

UNPAIRED_BEGIN = f"Intro text.\n{BEGIN}\nold rule\n"

END_BEFORE_BEGIN = f"Intro text.\n{END}\nold rule\n{BEGIN}\n"


def test_opencode_managed_block_is_idempotent() -> None:
    first = ManagedBlock(ROOT).render(INTRO_WITH_BLOCK, [RULE])
    assert first == MANAGED_WITH_RULE

    second = ManagedBlock(ROOT).render(first, [RULE])
    assert second == first


def test_opencode_managed_block_appends_when_no_marker() -> None:
    block = ManagedBlock(ROOT)
    assert block.path == ROOT / "AGENTS.md"
    assert block.render(INTRO_ONLY, [RULE]) == f"Intro text.\n\n{BEGIN}\nRule body.\n{END}\n"


def test_opencode_block_with_unpaired_marker_is_rejected() -> None:
    with pytest.raises(MalformedBlockError):
        ManagedBlock(ROOT).render(UNPAIRED_BEGIN, [RULE])


def test_opencode_block_with_end_before_begin_is_rejected() -> None:
    with pytest.raises(MalformedBlockError):
        ManagedBlock(ROOT).render(END_BEFORE_BEGIN, [RULE])
    with pytest.raises(MalformedBlockError):
        ManagedBlock(ROOT).render(f"{BEGIN}\n{BEGIN}\n{END}\n", [RULE])


def test_managed_block_state_reports_both_markers_in_order() -> None:
    assert ManagedBlock(ROOT).state(MANAGED_WITH_RULE) == "both"


def test_managed_block_refuses_misordered_markers() -> None:
    block = ManagedBlock(ROOT)
    assert block.state(END_BEFORE_BEGIN) == "malformed"
    with pytest.raises(MalformedBlockError):
        block.render(END_BEFORE_BEGIN, [RULE])


def test_managed_block_markers_use_chief() -> None:
    """The managed block is framed by the ``chief`` begin and end markers."""
    assert ManagedBlock.BEGIN == "<!-- chief:begin -->"
    assert ManagedBlock.END == "<!-- chief:end -->"
