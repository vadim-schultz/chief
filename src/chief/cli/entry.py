"""Run one command line: map usage errors, aborts and failures to exit codes."""

from collections.abc import Sequence

import typer
from typer import Abort
from typer.exceptions import TyperException
from typer.main import get_command

from chief.cli.app import app, log, traceback_enabled

_PROG_NAME = "chief"


def run(argv: Sequence[str] | None) -> int:
    """Return the exit code of one command line."""
    try:
        result = get_command(app).main(args=argv, prog_name=_PROG_NAME, standalone_mode=False)
    except TyperException as error:
        return _usage_error(error)
    except (Abort, KeyboardInterrupt):
        return _aborted()
    except Exception as error:
        return _failed(error)
    return _exit_code(result)


def _exit_code(result: int | None) -> int:
    """Return the code that a command returned, or 0 when it returned nothing."""
    return 0 if result is None else result


def _usage_error(error: TyperException) -> int:
    """Print a usage error and its help hint on stderr, and return its exit code, 2."""
    typer.echo(f"Error: {error.format_message()}", err=True)
    typer.echo(f"Try '{_PROG_NAME} --help' for help.", err=True)
    return error.exit_code


def _aborted() -> int:
    """Log the abort and return exit code 1."""
    log.warning("Aborted by user")
    return 1


def _failed(error: Exception) -> int:
    """Log a runtime error with or without its traceback, and return exit code 1."""
    if traceback_enabled():
        log.exception(error)
    else:
        log.error(error)
        log.warning("Hint: Rerun with '--verbose' to show exception traceback.")
    return 1
