---
id: C2
depends_on: [C1]
touches:
  - 04-plan-suite/src/hello/adapters.py
  - 04-plan-suite/src/hello/registry.py
  - 04-plan-suite/tests/test_adapters.py
  - 04-plan-suite/tests/test_registry.py
execution: chapter-implementer
---

# C2: language adapters

## Goal

Add one adapter per language (`en`, `de`, `es`) and register them in `ADAPTERS`, so `get_adapter` finds them.

## Boundaries

- Edit only the paths in `touches`. Do not change `contract.py`, `pyproject.toml`, or add the CLI.
- If the contract seems wrong, stop and report it. Do not weaken the C1 tests.

## Red: write these tests first and confirm they fail

Happy path:

- `test_adapter_greets_ada_exactly`, parametrised over `EnglishAdapter()`/`en`/`Hello, Ada!`, `GermanAdapter()`/`de`/`Hallo, Ada!`, `SpanishAdapter()`/`es`/`¡Hola, Ada!`. Assert the `language` attribute and `greet("Ada")`.
- `test_get_adapter_greets_ada_in_registered_language`, parametrised over `en`, `de`, `es`: `get_adapter(code).greet("Ada")` returns the greeting above.

Negative path:

- `test_get_adapter_rejects_unknown_language_and_lists_supported`: `get_adapter("xx")` raises `UnsupportedLanguageError` with the exact message `Unsupported language 'xx'. Supported: de, en, es.`
- `test_adapter_rejects_empty_name`, parametrised over the three adapters: `greet("")` raises `ValueError` with `name must not be empty`.

Confirm `test_get_adapter_greets_*` fails while `ADAPTERS` is empty.

## Green: minimum code

- `adapters.py`: a private base class `_SalutationAdapter` with a `language: str` and a `_salutation: str` class attribute, and a `greet` that returns `f"{self._salutation}, {require_name(name)}!"`. Subclasses `EnglishAdapter` (`en`, `Hello`), `GermanAdapter` (`de`, `Hallo`), and `SpanishAdapter` (`es`, `¡Hola`) set only those two attributes. Each public class gets a docstring.
- `registry.py`: populate `ADAPTERS` from the three adapters, keyed by each adapter's `language`. Build it from a tuple so the code appears once.

## Refactor gate

Audit `adapters.py` and `registry.py`. Confirm the three adapters differ only by their class attributes, with no `if` on language. Confirm `get_adapter` still has a single guard. Report the outcome.

## Verification

- Narrow: `cd 04-plan-suite && uv run pytest tests/test_adapters.py tests/test_registry.py`
- Local CI: `cd 04-plan-suite && uv sync && uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest && uv build`

## Commit

On branch `feat/plans-hello-c2-adapters`, in the worktree. Conventional commit: `feat(adapters): add English, German, and Spanish greeting adapters`.
