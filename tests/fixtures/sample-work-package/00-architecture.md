# hello suite: architecture

## Goal

A `hello` command that greets a name in English, German, or Spanish. An unknown language code or an empty name is rejected.

## Behaviour

| Input | Result |
| --- | --- |
| `en`, name `Ada` | `Hello, Ada!` |
| `de`, name `Ada` | `Hallo, Ada!` |
| `es`, name `Ada` | `¡Hola, Ada!` |
| empty name (library) | `ValueError`: `name must not be empty` |
| unknown code `xx` (library) | `UnsupportedLanguageError`: `Unsupported language 'xx'. Supported: de, en, es.` |
| unknown code `xx` (CLI) | exit code 2; message names the supported codes |
| empty `--name ""` (CLI) | exit code 2 |
| no `--name` (CLI) | greets `world` |

## Components

| Module | Responsibility | Chapter |
| --- | --- | --- |
| `hello.contract` | `GreetingAdapter` protocol, `UnsupportedLanguageError`, `require_name` | C1 |
| `hello.registry` | `ADAPTERS` dict and `get_adapter(language)` | C1 (empty), C2 (populated) |
| `hello.adapters` | `EnglishAdapter`, `GermanAdapter`, `SpanishAdapter` | C2 |
| `hello.cli` | Typer command `hello --language LANG [--name NAME]` | C3 |

Dependency direction: `cli` → `registry` → `adapters` → `contract`. `contract` imports nothing from the package.

## Layout after C3

```text
04-plan-suite/
├── .plans/hello/          # this suite
├── pyproject.toml         # hatchling; typer runtime dep; dev: pytest, ruff, mypy
├── uv.lock
├── run.sh                 # uv sync, pytest, three CLI invocations
├── src/hello/
│   ├── __init__.py
│   ├── contract.py
│   ├── adapters.py
│   ├── registry.py
│   └── cli.py
└── tests/
    ├── test_contract.py
    ├── test_adapters.py
    ├── test_registry.py
    └── test_cli.py
```

## Tooling

- Python 3.12 or newer; `uv` for dependencies; `hatchling` as the build backend.
- Ruff rules `E,F,I,B,UP,D`, pydocstyle convention `google`; `D` is exempt under `tests/`.
- `mypy --strict` over `src` and `tests`.
- `pytest` with `testpaths = ["tests"]`.
