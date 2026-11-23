"""Planted failure for the ci.sh harness test.

The file name does not match test_*.py, so the repository run never collects it.
"""


def test_planted_failure() -> None:
    assert False, "planted failure for the ci.sh harness"
