---
id: C3
depends_on: [C2]
touches:
  - 04-plan-suite/pyproject.toml
  - 04-plan-suite/uv.lock
  - 04-plan-suite/src/hello/cli.py
  - 04-plan-suite/tests/test_cli.py
  - 04-plan-suite/run.sh
execution: chapter-implementer
---

# C3: Typer CLI

## Goal

Expose the greeting as `hello --language LANG [--name NAME]`. `--name` defaults to `world`. An unknown language or an empty name exits with code 2.

## Boundaries

- Edit only the paths in `touches`. Do not change the contract or adapters; if they need changing, stop and report.
- `run.sh` is in the skeleton. C3 is the first chapter where its demo checks can pass.

## Red: write these tests first and confirm they fail

Use `typer.testing.CliRunner` against `hello.cli.app`.

Happy path:

- `test_cli_greets_named_person`: `--language en --name Ada` exits 0 and prints `Hello, Ada!`.
- `test_cli_defaults_name_to_world`: `--language en` exits 0 and prints `Hello, world!`.

Negative path:

- `test_cli_rejects_unknown_language`: `--language xx` exits 2, and the output contains `Unsupported language 'xx'` and `de, en, es`.
- `test_cli_rejects_empty_name`: `--language en --name ""` exits 2, and the output contains `name must not be empty`.

Confirm the failures come from the missing module, not from typos.

## Green: minimum code

- `pyproject.toml`: add `typer>=0.12` to `dependencies`; add `[project.scripts] hello = "hello.cli:app"`.
- `cli.py`: a `typer.Typer` app with one command. `--language` is a required option (`typer.Option(..., "--language")`). `--name` defaults to `"world"`. Call `get_adapter(language).greet(name)`. Catch `UnsupportedLanguageError` and `ValueError` and re-raise them as `typer.BadParameter`, so both exit with code 2 and name the problem.
- `run.sh` (already in the skeleton; keep it unless a check fails for a reason in this spec): it checks that `uv` is on the PATH, then runs `uv sync`, `uv run pytest`, and three checks:
  - `uv run hello --language en --name Ada` must print exactly `Hello, Ada!`;
  - `uv run hello --language de --name Ada` must print exactly `Hallo, Ada!`;
  - `uv run hello --language xx --name Ada` must exit 2. Capture the exit code with `|| code=$?`, assert it is 2, and continue.
  Each failed check prints a message to stderr and exits 1. The script takes no arguments.

Every public function needs a docstring. Type every signature; no `Any`.

## Refactor gate

Audit `cli.py`. The two error mappings share a shape. Extract a helper such as `_bad_parameter(error, param_hint)` only if the duplication remains after the green step. Confirm the command function is a single dispatch. Report the outcome.

## Verification

- Narrow: `cd 04-plan-suite && uv run pytest tests/test_cli.py`
- Demo: `cd 04-plan-suite && ./run.sh`
- Local CI: `cd 04-plan-suite && uv sync && uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest && uv build`

## Commit

On branch `feat/plans-hello-c3-cli`, in the worktree. Conventional commit: `feat(cli): add typer hello command with language and name options`.
