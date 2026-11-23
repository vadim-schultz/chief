"""Library entry point: ``ChiefOfStaff`` lists, installs, checks and exports the packs of an injected bundle."""

from __future__ import annotations

from pathlib import Path

from chief._version import version as __version__
from chief.catalogue.bundle_tree import BundleTree
from chief.catalogue.export import Exporter
from chief.catalogue.packs import BUNDLED_PACKS, Pack
from chief.installation.drift import DriftChecker
from chief.installation.installer import Installer
from chief.installation.manifest import ManifestStore
from chief.installation.planner import Plan
from chief.installation.uninstaller import Uninstaller, UninstallResult
from chief.targets.locations import Locations
from chief.targets.names import Target, targets_for

__all__ = ("ChiefOfStaff", "Target", "__version__")


def _names(target: str) -> tuple[str, ...]:
    """Expand ``all`` to the concrete targets through :class:`Target`. Any other name is one target, checked on use."""
    return targets_for(Target.ALL) if target == Target.ALL else (target,)


def _folders(target: str, output: Path) -> dict[str, Path]:
    """Map each target to its folder: one subfolder per target for ``all``, otherwise ``output`` itself."""
    if target != Target.ALL:
        return {target: output}
    return {name: output / name for name in _names(target)}


class ChiefOfStaff:
    """Facade over one bundle directory and one set of locations. Its methods return data and never print."""

    def __init__(self, packs_dir: Path, locations: Locations) -> None:
        """Bind the facade to the pack directory and to the config and state locations."""
        store = ManifestStore(locations)
        self._locations = locations
        self._bundle = BundleTree(packs_dir, locations)
        self._installer = Installer(locations, store)
        self._uninstaller = Uninstaller(store)
        self._checker = DriftChecker(locations, store)

    @classmethod
    def bundled(cls, locations: Locations | None = None) -> ChiefOfStaff:
        """Bind the facade to the packs shipped with the package, and to ``locations`` or to fresh ``Locations()``."""
        return cls(BUNDLED_PACKS, Locations() if locations is None else locations)

    def packs(self) -> list[Pack]:
        """Return every pack of the bundle, in directory-name order."""
        return list(self._bundle.catalogue.packs.values())

    def targets(self) -> list[str]:
        """Return the concrete install target names."""
        return list(targets_for(Target.ALL))

    def roots(self) -> dict[str, Path]:
        """Return the config root of each concrete target, read from the injected locations."""
        return {name: self._locations.config_root(name) for name in self.targets()}

    def has_pack(self, name: str) -> bool:
        """Return whether the bundle holds a pack named ``name``."""
        return name in self._bundle.catalogue.packs

    def install(self, target: str, *, dry_run: bool = False, force: bool = False) -> list[Plan]:
        """Return the plans of ``target``, and apply them unless ``dry_run``. A refused plan writes nothing."""
        return self._installer.install_bundle(self._bundle, _names(target), dry_run=dry_run, force=force)

    def uninstall(self, target: str) -> list[UninstallResult]:
        """Remove the tracked files of ``target`` and return one result per concrete target."""
        return [self._uninstaller.run(name) for name in _names(target)]

    def doctor(self, target: str) -> dict[str, list[str]]:
        """Return the drifted paths of ``target``, keyed by target name."""
        return {name: self._checker.check(name) for name in _names(target)}

    def export(self, target: str, output: Path) -> None:
        """Write the rendered tree of ``target`` beneath ``output``, one folder per target for ``all``."""
        Exporter(self._bundle).write(_folders(target, output))
