import logging
import sys
from collections.abc import Iterator
from pathlib import Path
from runpy import run_module

import pytest
from typer.testing import CliRunner

from chief import __version__
from chief.__main__ import main
from chief.cli.app import _DEFAULT_LOG_LEVEL, _configure_logger, app, log


class RaiseExceptionOnce:
    def __init__(self, exception):
        self.has_run = False
        self.exception = exception

    def __call__(self, *args, **kwargs):
        if not self.has_run:
            self.has_run = True
            raise self.exception


def test_main_prints_version(capsys):
    with pytest.raises(SystemExit) as error:
        main(["--version"])
    assert error.value.code == 0
    assert capsys.readouterr().out == f"{__version__}\n"


def test_run_as_module(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["chief", "--version"])
    # A cached '__main__' submodule makes runpy warn about a duplicate execution.
    monkeypatch.delitem(sys.modules, "chief.__main__", raising=False)
    with pytest.raises(SystemExit) as error:
        run_module("chief", run_name="__main__", alter_sys=True)
    assert error.value.code == 0
    assert capsys.readouterr().out == f"{__version__}\n"


def test_verbose_logging():
    _configure_logger(verbose=1, quiet=0)
    assert log.getEffectiveLevel() == _DEFAULT_LOG_LEVEL - 10


@pytest.mark.parametrize(
    "verbose, quiet, expected_log_level",
    [
        pytest.param(0, 0, logging.WARNING, id="default"),
        pytest.param(1, 0, logging.INFO, id="v"),
        pytest.param(2, 0, logging.DEBUG, id="vv"),
        pytest.param(3, 0, logging.DEBUG, id="vvv"),
        pytest.param(0, 1, logging.ERROR, id="q"),
        pytest.param(0, 2, logging.CRITICAL, id="qq"),
        pytest.param(0, 3, logging.CRITICAL, id="qqq"),
        pytest.param(2, 2, logging.WARNING, id="vvqq - default"),
        pytest.param(2, 1, logging.INFO, id="vvq"),
        pytest.param(1, 2, logging.ERROR, id="vqq"),
    ],
)
def test_verbosity_setting(verbose, quiet, expected_log_level, monkeypatch):
    default_log_level = logging.WARNING
    monkeypatch.setattr("chief.cli.app._DEFAULT_LOG_LEVEL", default_log_level)
    _configure_logger(verbose, quiet)
    assert log.getEffectiveLevel() == expected_log_level


@pytest.mark.parametrize(
    "options, logs",
    [
        pytest.param([], ["Exception from log.info", "Hint: Rerun with"], id="plain"),
        pytest.param(["-v"], ["Exception from log.info", "Traceback"], id="verbose"),
    ],
)
def test_main_exception(options, logs, monkeypatch, caplog):
    monkeypatch.setattr(log, "info", RaiseExceptionOnce(Exception("Exception from log.info")))
    with pytest.raises(SystemExit) as error:
        main(options)
    assert error.value.code == 1
    assert all(x in caplog.text for x in logs)


def test_main_interrupt(monkeypatch, caplog):
    monkeypatch.setattr(log, "info", RaiseExceptionOnce(KeyboardInterrupt()))
    with pytest.raises(SystemExit) as error:
        main([])
    assert error.value.code == 1
    assert "Aborted by user" in caplog.text


@pytest.fixture
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point HOME and both XDG roots at folders under ``tmp_path``."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    return tmp_path


@pytest.mark.usefixtures("isolated_home")
def test_unknown_option_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["--bogus"])
    assert error.value.code == 2
    err = capsys.readouterr().err
    assert "No such option" in err
    assert "--bogus" in err


@pytest.mark.usefixtures("isolated_home")
def test_check_command_does_not_exist(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["check"])
    assert error.value.code == 2
    err = capsys.readouterr().err
    assert "No such command" in err
    assert "check" in err


@pytest.mark.usefixtures("isolated_home")
def test_main_wrapper_still_returns_exit_code() -> None:
    with pytest.raises(SystemExit) as error:
        main(["list"])
    assert error.value.code == 0


@pytest.mark.usefixtures("isolated_home")
def test_no_command_prints_help_and_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main([])
    assert error.value.code == 2
    assert "Usage:" in capsys.readouterr().out


@pytest.fixture
def restore_log_level() -> Iterator[None]:
    """Restore the package log level after a test that runs the CLI."""
    level = log.level
    yield
    log.setLevel(level)


def test_verbosity_flag_sets_logger_level(restore_log_level: None) -> None:
    """``-vv`` on the real command line sets the package logger to DEBUG from the default WARNING."""
    result = CliRunner().invoke(app, ["-vv", "list"])
    assert result.exit_code == 0
    assert log.getEffectiveLevel() == logging.DEBUG


def test_quiet_flag_does_not_raise_logger_level(restore_log_level: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """``-q`` lowers the level one step from the constant that the logger reads, and never raises it."""
    monkeypatch.setattr("chief.cli.app._DEFAULT_LOG_LEVEL", logging.ERROR)
    result = CliRunner().invoke(app, ["-q", "list"])
    assert result.exit_code == 0
    assert log.getEffectiveLevel() == logging.CRITICAL
