import re

from chief import __version__


def test_version():
    assert re.match(r"[\d.]+", __version__)
