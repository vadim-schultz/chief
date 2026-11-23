"""Planted unit test for the Python fixture: the assertion is wrong on purpose."""

from greeting import greet


def test_greet_names_the_caller() -> None:
    assert greet("Ada") == "Hello, Ada"
