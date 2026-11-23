"""OpenCode managed block: the rule bodies written between markers in the shared AGENTS.md file."""

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Literal

from chief.rendering.artifacts import Destination, read_canonical
from chief.targets import registry

MarkerState = Literal["none", "both", "malformed"]


class MalformedBlockError(Exception):
    """Raised when an OpenCode managed block has an unpaired or misordered marker."""


class ManagedBlock:
    """The OpenCode managed block of one configuration root: its markers, its state and its body."""

    BEGIN = "<!-- chief:begin -->"
    END = "<!-- chief:end -->"
    FILE = "AGENTS.md"

    def __init__(self, root: Path) -> None:
        """Bind the block to the OpenCode configuration directory ``root``."""
        self.path = root / self.FILE
        self._dest = Destination(root, registry.target_spec("opencode"))

    def render(self, existing: str, rule_sources: Iterable[str]) -> str:
        """Return ``existing`` with the managed block written in.

        Args:
            existing: Current text of AGENTS.md, possibly empty.
            rule_sources: Text of each canonical rule, in the order they appear in the block.

        Returns:
            The new text.

        Raises:
            MalformedBlockError: If the markers are unpaired, repeated or out of order.
        """
        block = self._block(rule_sources)
        return _OUTCOMES[self.state(existing)](existing, block)

    @staticmethod
    def state(existing: str) -> MarkerState:
        """Name the marker state of ``existing``: ``none``, ``both`` or ``malformed``."""
        return next(name for check, name in _STATES if check(existing))

    @staticmethod
    def body(text: str) -> str:
        """Return the block body in ``text``, between its markers and without them."""
        start, stop = ManagedBlock._span(text)
        return text[start:stop].removeprefix(f"{ManagedBlock.BEGIN}\n").removesuffix(f"\n{ManagedBlock.END}")

    @staticmethod
    def frame(content: str) -> str:
        """Return ``content`` wrapped in the begin and end markers, the inverse of :meth:`body`."""
        return f"{ManagedBlock.BEGIN}\n{content}\n{ManagedBlock.END}"

    @staticmethod
    def strip(text: str) -> str:
        """Return ``text`` without its managed block, keeping the user text on either side."""
        start, stop = ManagedBlock._span(text)
        parts = [part for part in (text[:start].rstrip("\n"), text[stop:].lstrip("\n")) if part]
        return "\n\n".join(parts) + "\n" if parts else ""

    @staticmethod
    def _span(text: str) -> tuple[int, int]:
        """Return the index of the begin marker and the index just past the end marker."""
        return text.index(ManagedBlock.BEGIN), text.index(ManagedBlock.END) + len(ManagedBlock.END)

    def _block(self, rule_sources: Iterable[str]) -> str:
        """Return the marker-delimited block that holds every rule body."""
        bodies = [self._rule_body(source) for source in rule_sources]
        return ManagedBlock.frame("\n\n".join(bodies))

    def _rule_body(self, source: str) -> str:
        """Return one rule body with its frontmatter removed and its tokens resolved."""
        _, body = read_canonical(source)
        return self._dest.resolve(body).strip("\n")


def _no_markers(text: str) -> bool:
    """Return whether ``text`` holds neither marker."""
    return ManagedBlock.BEGIN not in text and ManagedBlock.END not in text


def _one_ordered_pair(text: str) -> bool:
    """Return whether ``text`` holds each marker once, with the begin marker first."""
    return (
        text.count(ManagedBlock.BEGIN) == 1
        and text.count(ManagedBlock.END) == 1
        and text.index(ManagedBlock.BEGIN) < text.index(ManagedBlock.END)
    )


_STATES: tuple[tuple[Callable[[str], bool], MarkerState], ...] = (
    (_no_markers, "none"),
    (_one_ordered_pair, "both"),
    (lambda _text: True, "malformed"),
)


def _append(existing: str, block: str) -> str:
    """Append the block after the kept text, separated by one empty line."""
    head = existing.rstrip("\n")
    return f"{head}\n\n{block}\n" if head else f"{block}\n"


def _replace(existing: str, block: str) -> str:
    """Replace only the text from the begin marker through the end marker."""
    start, stop = ManagedBlock._span(existing)
    return existing[:start] + block + existing[stop:]


def _refuse(existing: str, block: str) -> str:
    """Refuse a half-written or misordered block instead of writing it."""
    raise MalformedBlockError("managed block needs each marker once, with the begin marker first")


_OUTCOMES: Mapping[MarkerState, Callable[[str, str], str]] = {
    "none": _append,
    "both": _replace,
    "malformed": _refuse,
}
