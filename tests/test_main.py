"""Tests for the diagrams package."""


def test_hello():
    """Test the hello function."""
    from diagrams.main import hello
    assert hello() == "Hello from diagrams project!"
