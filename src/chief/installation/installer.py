"""Installer: plans one target, applies the plan and records it in the manifest, once per apply."""

from collections.abc import Callable, Mapping, Sequence

from chief.catalogue.bundle_tree import BundleTree
from chief.installation.manifest import ManifestStore
from chief.installation.planner import Action, ActionKind, InstallPlanner, Plan, Rendered
from chief.targets.locations import Locations


class Installer:
    """Plan and apply install targets, and record each applied plan in the manifest store."""

    def __init__(self, locations: Locations, store: ManifestStore) -> None:
        """Bind the installer to the config roots of ``locations`` and to the manifests of ``store``."""
        self._store = store
        self._planner = InstallPlanner(locations, store)

    def install(
        self,
        target: str,
        rendered: Rendered,
        *,
        rule_sources: Sequence[str] = (),
        dry_run: bool = False,
        force: bool = False,
    ) -> Plan:
        """Plan and, unless ``dry_run``, apply one install target.

        Args:
            target: Install target name, such as ``opencode``.
            rendered: ``(path, content)`` pairs from the renderer.
            rule_sources: Canonical rule texts for the managed block. Only ``opencode`` has one.
            dry_run: When true, return the plan and write nothing.
            force: When true, overwrite edited files the manifest tracks.

        Returns:
            The plan that was built.
        """
        plan = self._planner.plan(target, rendered, rule_sources=rule_sources, force=force)
        if not dry_run:
            self.apply(plan)
        return plan

    def install_bundle(
        self,
        bundle: BundleTree,
        targets: Sequence[str],
        *,
        dry_run: bool = False,
        force: bool = False,
    ) -> list[Plan]:
        """Render each target of ``bundle`` in turn, then install it, and return the plans in order."""
        plans: list[Plan] = []
        for name in targets:
            tree = bundle.build(name)
            plans.append(self.install(name, tree.files, rule_sources=tree.rule_sources, dry_run=dry_run, force=force))
        return plans

    def apply(self, plan: Plan) -> None:
        """Validate, apply and record ``plan``. A refused plan writes nothing and records nothing."""
        if plan.refused:
            return
        self._apply_actions(plan)
        self._store.write(plan.target, plan.manifest)

    def _apply_actions(self, plan: Plan) -> None:
        """Run the executor of each action of ``plan``, in plan order."""
        executors = self._executors()
        for action in plan.actions:
            executors[action.kind](action)

    def _executors(self) -> Mapping[ActionKind, Callable[[Action], None]]:
        """Return the executor of each action kind."""
        return {"write": self._write, "skip": self._keep, "refuse": self._keep}

    @staticmethod
    def _write(action: Action) -> None:
        """Create the parent folder of ``action.path`` and write its content."""
        action.path.parent.mkdir(parents=True, exist_ok=True)
        action.path.write_bytes(action.content.encode("utf-8"))

    @staticmethod
    def _keep(action: Action) -> None:
        """Leave the path untouched."""
