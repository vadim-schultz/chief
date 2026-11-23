"""Typer app: the group callback, the logging setup and the command table."""

import logging
from collections.abc import Callable, Mapping
from functools import wraps
from typing import Annotated, ParamSpec, TypeVar

import typer

from chief.api import __version__
from chief.cli.commands import (
    doctor_command,
    export_command,
    install_command,
    list_command,
    uninstall_command,
)

_DEFAULT_LOG_LEVEL = logging.WARNING
log = logging.getLogger("chief")
_P = ParamSpec("_P")
_R = TypeVar("_R")

app = typer.Typer(add_completion=False, help="Install, check and export the chief-of-staff bundle.")


def _abortable(handler: Callable[_P, _R]) -> Callable[_P, _R]:
    """Raise a Typer abort for Ctrl-C inside ``handler``, so that ``main`` logs it and exits 1."""

    @wraps(handler)
    def run(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        try:
            return handler(*args, **kwargs)
        except KeyboardInterrupt as error:
            raise typer.Abort() from error

    return run


def _print_version(value: bool) -> None:
    """Print the package version and exit."""
    if value:
        typer.echo(__version__)
        raise typer.Exit()


def _configure_logger(verbose: int, quiet: int) -> None:
    """Set the package log level from additive ``-v`` and ``-q`` counts.

    Args:
        verbose: Number of ``-v`` flags.
        quiet: Number of ``-q`` flags.
    """
    logging.basicConfig(
        format="{asctime} [{levelname:^8}] ({filename}:{lineno}) {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    verbosity = _DEFAULT_LOG_LEVEL - ((verbose - quiet) * 10)
    log.setLevel(min(logging.CRITICAL, max(logging.DEBUG, verbosity)))


def traceback_enabled() -> bool:
    """Return whether a runtime error logs its traceback at the current log level."""
    return log.getEffectiveLevel() < _DEFAULT_LOG_LEVEL or _DEFAULT_LOG_LEVEL <= logging.DEBUG


def _help_without_command(ctx: typer.Context) -> None:
    """Print the help text and exit with usage code 2 when no command was given."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(2)


def _register(commands: Mapping[str, Callable[..., None]]) -> None:
    """Register every handler of the command table as a Typer command."""
    for name, handler in commands.items():
        app.command(name)(_abortable(handler))


_register({
    "list": list_command,
    "install": install_command,
    "uninstall": uninstall_command,
    "doctor": doctor_command,
    "export": export_command,
})


@app.callback(invoke_without_command=True)
@_abortable
def _group(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", callback=_print_version, is_eager=True, help="Show version number and exit."),
    ] = False,
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, help="Increase output (additive).")] = 0,
    quiet: Annotated[int, typer.Option("--quiet", "-q", count=True, help="Reduce output (additive).")] = 0,
) -> None:
    """Install, check and export the chief-of-staff bundle."""
    _configure_logger(verbose, quiet)
    log.info(f"Loglevel set to {logging.getLevelName(log.getEffectiveLevel())}")
    _help_without_command(ctx)
