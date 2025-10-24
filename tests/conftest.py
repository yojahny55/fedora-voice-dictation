"""Pytest configuration and shared fixtures for Fedora Voice Dictation tests.

This module contains pytest configuration and fixtures that are shared across
all test modules. Fixtures defined here are automatically available to all tests.
"""

import logging
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Configure logging for test runs.

    Sets up console-only logging at WARNING level to reduce noise during tests.
    Individual tests can override this by setting specific logger levels.
    """
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    yield
    # Cleanup after all tests
    logging.shutdown()


@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for log files during tests.

    Args:
        tmp_path: pytest's built-in temporary directory fixture.

    Returns:
        Path to a temporary logs directory.

    Example:
        >>> def test_logger(temp_log_dir):
        ...     log_file = temp_log_dir / "test.log"
        ...     setup_logging(log_file=log_file)
        ...     assert log_file.exists()
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for config files during tests.

    Args:
        tmp_path: pytest's built-in temporary directory fixture.

    Returns:
        Path to a temporary config directory.
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
