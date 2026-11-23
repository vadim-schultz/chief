"""Fence for invariant I2: the CLI imports only the facade, its own package, and stdlib or third-party code."""

import ast
from collections.abc import Iterable
from pathlib import Path

import chief

SOURCE = Path(chief.__file__).parent
OLD_CLI_MODULES = ("cli.py", "commands.py", "commands_output.py")
ENTRY_MODULE = "__main__.py"


def cli_modules() -> list[Path]:
    """Return every CLI module: the ``cli`` package, the entry module, and the flat modules that the chapter retires."""
    package = sorted((SOURCE / "cli").rglob("*.py"))
    flat = [SOURCE / name for name in (*OLD_CLI_MODULES, ENTRY_MODULE) if (SOURCE / name).exists()]
    return [*package, *flat]


def _library_imports(path: Path) -> list[str]:
    """Return every ``chief`` module that ``path`` imports, with or without a ``from`` clause."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.append(node.module)
    return [name for name in modules if name == "chief" or name.startswith("chief.")]


def _is_allowed(module: str) -> bool:
    """Return whether the CLI may import ``module``: the facade, or its own package."""
    return module in {"chief.api", "chief.cli"} or module.startswith(
        "chief.cli.",
    )


def find_violations(modules: Iterable[Path]) -> list[str]:
    """Return one ``file: module`` line for every import that the fence rejects."""
    return [
        f"{path.name}: {module}" for path in modules for module in _library_imports(path) if not _is_allowed(module)
    ]


def test_cli_imports_only_the_facade() -> None:
    """Every ``chief`` import in the CLI is the facade or the CLI package itself."""
    assert cli_modules(), "no CLI modules found"
    assert find_violations(cli_modules()) == []


def test_fence_rejects_private_library_import(tmp_path: Path) -> None:
    """A CLI module that imports a library internal is reported as one violation."""
    module = tmp_path / "bad_cli.py"
    module.write_text("from chief.installation.planner import InstallPlanner\n", encoding="utf-8")
    violations = find_violations([module])
    assert len(violations) == 1
    assert "chief.installation.planner" in violations[0]
