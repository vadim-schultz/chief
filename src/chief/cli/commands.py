"""Command handlers: each one makes one facade call and prints its result."""

from pathlib import Path
from typing import Annotated

import typer

from chief.api import ChiefOfStaff, Target


def _target_choices() -> str:
    """List the target names of :class:`Target` for the ``--target`` help, with ``all`` last."""
    names = [member.value for member in Target]
    return f"{', '.join(names[:-1])} or {names[-1]}"


_TARGET_CHOICES = _target_choices()


def _known_pack(value: str | None) -> str | None:
    """Reject a pack name that the bundle does not hold."""
    if value is not None and not ChiefOfStaff.bundled().has_pack(value):
        raise typer.BadParameter(f"'{value}' is not a pack in the bundle.")
    return value


def list_command(
    pack: Annotated[str | None, typer.Argument(callback=_known_pack, help="Pack to list. Default: every pack.")] = None,
) -> None:
    """List the packs and the directory that each target installs into."""
    facade = ChiefOfStaff.bundled()
    for line in [f"{item.name}: {item.description}" for item in facade.packs() if pack in (None, item.name)]:
        typer.echo(line)
    for name, root in facade.roots().items():
        typer.echo(f"{name}: {root}")


def _exit_on_failure(failed: bool) -> None:
    """Exit with code 1 when a target was refused or drifted. Every failing run ends this way."""
    if failed:
        raise typer.Exit(1)


def install_command(
    target: Annotated[Target, typer.Option(help=f"Target to install into: {_TARGET_CHOICES}.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Print the plan and write nothing.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Overwrite edited files that the manifest tracks.")] = False,
) -> None:
    """Install every pack for one target, or for every target."""
    plans = ChiefOfStaff.bundled().install(target.value, dry_run=dry_run, force=force)
    for action in [action for plan in plans for action in plan.actions]:
        typer.echo(f"{action.kind} {action.path}", err=action.kind == "refuse")
    _exit_on_failure(any(plan.refused for plan in plans))


def _echo_paths(prefix: str, paths: tuple[Path, ...], *, err: bool) -> None:
    """Print one ``prefix path`` line for each path."""
    for path in paths:
        typer.echo(f"{prefix} {path}", err=err)


def uninstall_command(
    target: Annotated[Target, typer.Option(help=f"Target to uninstall: {_TARGET_CHOICES}.")],
) -> None:
    """Remove the files and managed block that the install manifest tracks."""
    results = ChiefOfStaff.bundled().uninstall(target.value)
    for result in results:
        _echo_paths("removed", result.removed, err=False)
        _echo_paths("kept", result.refused, err=True)
    _exit_on_failure(any(result.refused for result in results))


def _drift_lines(name: str, paths: list[str]) -> list[str]:
    """Return one line per drifted path, or a single ``no drift`` line when there is none."""
    return [f"{name}: {path}" for path in paths] or [f"{name}: no drift"]


def doctor_command(
    target: Annotated[Target, typer.Option(help=f"Target to check: {_TARGET_CHOICES}.")] = Target.ALL,
) -> None:
    """Report installed files that differ from their install record. Drift only."""
    drift = ChiefOfStaff.bundled().doctor(target.value)
    for name, paths in drift.items():
        typer.echo("\n".join(_drift_lines(name, paths)))
    _exit_on_failure(any(drift.values()))


def export_command(
    target: Annotated[Target, typer.Option(help=f"Target to export: {_TARGET_CHOICES}.")],
    output: Annotated[Path, typer.Option(help="Folder to write the rendered tree into.")],
) -> None:
    """Write the rendered tree of a target to a folder, for machines without Python."""
    ChiefOfStaff.bundled().export(target.value, output)
