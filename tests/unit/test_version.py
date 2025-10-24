"""Unit tests for version reporting and package initialization.

Tests basic package health: version variable existence, format, and
command-line version reporting via `python -m src --version`.
"""

import subprocess
import sys

from src import __version__


def test_version_exists():
    """Test that version variable is defined in package __init__."""
    assert __version__ is not None, "Version variable should be defined"


def test_version_is_string():
    """Test that version is a string type."""
    assert isinstance(
        __version__, str
    ), f"Version should be str, got {type(__version__)}"


def test_version_format():
    """Test that version follows semantic versioning format.

    Expected format: MAJOR.MINOR.PATCH[-PRERELEASE]
    Example: "0.1.0-dev"
    """
    assert __version__, "Version should not be empty string"
    # Should have at least one dot (e.g., "0.1")
    assert "." in __version__, f"Version '{__version__}' should contain dots"


def test_version_command():
    """Test that --version command works via python -m src."""
    result = subprocess.run(
        [sys.executable, "-m", "src", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Command failed with code {result.returncode}"
    assert (
        __version__ in result.stdout
    ), f"Version '{__version__}' not found in output: {result.stdout}"


def test_main_without_args():
    """Test that running main without arguments doesn't error."""
    result = subprocess.run(
        [sys.executable, "-m", "src"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Command failed with code {result.returncode}"
    assert (
        __version__ in result.stdout
    ), f"Version '{__version__}' should appear in main output"
    assert (
        "Fedora Voice Dictation" in result.stdout
    ), "Application name should appear in output"
