"""Unit test for the clean Python fixture."""

from greeting import greet


def test_greet_names_the_caller() -> None:
    assert greet("Ada") == "Hello, Ada!"
