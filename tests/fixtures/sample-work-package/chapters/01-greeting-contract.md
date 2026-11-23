---
id: C1
depends_on: []
touches:
  - 04-plan-suite/pyproject.toml
  - 04-plan-suite/uv.lock
  - 04-plan-suite/src/hello/__init__.py
  - 04-plan-suite/src/hello/contract.py
  - 04-plan-suite/src/hello/registry.py
  - 04-plan-suite/tests/test_contract.py
execution: chapter-implementer
---

# C1: greeting contract

## Goal

Write the greeting contract into the existing skeleton: the `GreetingAdapter` protocol, `UnsupportedLanguageError`, the `require_name` check, and `get_adapter` over an `ADAPTERS` registry. The skeleton already has `pyproject.toml`, `src/hello/__init__.py`, and an empty `tests/`. The registry starts empty; C2 fills it.

## Boundaries

- Edit only the paths in `touches`. Do not add adapters, the CLI, or `run.sh`.
- Do not read or copy any other level folder in this repo. Write from this chapter.

## Red: write these tests first and confirm they fail

Happy path:

- `test_get_adapter_returns_registered_adapter`: with `registry.ADAPTERS["en"]` set to a fake adapter (use `monkeypatch.setitem`), `get_adapter("en")` returns that same object.
- `test_require_name_returns_non_empty_name`: `require_name("Ada") == "Ada"`.

Negative path:

- `test_get_adapter_rejects_unknown_language_and_lists_supported`: with fakes registered for `de`, `en`, `es`, `get_adapter("xx")` raises `UnsupportedLanguageError`, and `str(error)` equals `Unsupported language 'xx'. Supported: de, en, es.`
- `test_require_name_rejects_empty_name`: `require_name("")` raises `ValueError` with the message `name must not be empty`.

Run `uv run pytest`. Confirm the failures come from missing modules or behaviour, not from typos in the tests.

## Green: minimum code

- `contract.py`: `UnsupportedLanguageError(ValueError)`; `GreetingAdapter` Protocol with `language: str` and `greet(self, name: str) -> str`; `require_name(name: str) -> str`.
- `registry.py`: `ADAPTERS: dict[str, GreetingAdapter] = {}`; `get_adapter(language: str) -> GreetingAdapter` that raises with the sorted supported codes.
- `__init__.py`: a module docstring only (already in the skeleton).
- `pyproject.toml`: already in the skeleton; confirm it matches this spec: hatchling build backend; `name = "hello"`; `requires-python = ">=3.12"`; `dependencies = []`; `[dependency-groups] dev = ["pytest", "ruff", "mypy"]`; wheel packages `src/hello`; ruff select `E,F,I,B,UP,D`; pydocstyle `google`; per-file ignore `D` for `tests/**`; mypy `strict = true`, `mypy_path = "src"`, `files = ["src", "tests"]`; pytest `testpaths = ["tests"]`.

Every public function, class, and module needs a docstring (ruff `D`). Type every signature; no `Any`.

## Refactor gate

Audit `contract.py` and `registry.py` against the refactor checklist. Check one concern per module, a guard clause in `get_adapter`, and no duplication. Report the outcome even if it is "no change needed".

## Verification

- Narrow: `cd 04-plan-suite && uv run pytest tests/test_contract.py`
- Local CI: `cd 04-plan-suite && uv sync && uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest && uv build`

## Commit

On branch `feat/plans-hello-c1-contract`, in the worktree. Conventional commit: `feat(contract): add greeting protocol, name check, and registry lookup`.
