---
name: docstrings
description: Docstrings required for ruff pydocstyle (D) / docstyle CI
---

# Docstrings (docstyle CI)

Scope: Python only.

When a project runs **ruff pydocstyle** (`D` rules) on its source tree, new or changed Python code must include docstrings so `ruff check` passes.

## Required coverage

| Symbol | Rule | Docstring |
|--------|------|-----------|
| Module | D100 | One-line summary at top of file |
| Public class | D101 | Class purpose |
| Public method / property | D102 | Behavior; mention key args when non-obvious |
| Public function | D103 | Behavior |
| `__init__` | D107 | Brief initializer summary |

Private names (`_` prefix) and `tests/` are exempt.

## Style

- **Imperative mood**, one line when sufficient: `"""Return the parser for ``name``."""`
- Sphinx roles for cross-refs: `:class:`, `:meth:`, `:exc:`, ``double-backtick`` literals
- Match existing modules in the project — no redundant param lists for obvious signatures

```python
# ❌ BAD — public API without docstring
class JsonParser:
    @property
    def name(self) -> str:
        return "json"


# ✅ GOOD
class JsonParser:
    """Parse JSONL lines including generic, journald, and structlog dialects."""

    @property
    def name(self) -> str:
        """Return the parser identifier."""

    def parse_line(self, line: str, *, line_number: int) -> LogRecord:
        """Parse ``line`` into a :class:`LogRecord`."""
```

## Verify locally

```bash
ruff check <source-path>   # e.g. src, lib, or the path your project uses
```
