"""Command line entry point: ``python -m chief`` and the ``chief`` script."""

import sys
from collections.abc import Sequence
from typing import NoReturn

from chief.cli.entry import run


def main(argv: Sequence[str] | None = None) -> NoReturn:
    """Run the command line with ``argv``, or with ``sys.argv[1:]``, and exit with its code."""
    sys.exit(run(argv))


if __name__ == "__main__":
    main()
