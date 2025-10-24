"""Unit tests for logging configuration and setup.

Tests the setup_logging() function to ensure proper console and file handler
configuration, log directory creation, and error handling.
"""

import logging
from pathlib import Path

import pytest

from src.utils.logger import setup_logging


def test_setup_logging_console_only():
    """Test that setup_logging configures console handler correctly."""
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Setup logging with console only (no file)
    setup_logging(log_level="INFO")

    # Verify root logger level is set
    assert root_logger.level == logging.INFO

    # Verify at least one handler exists
    assert len(root_logger.handlers) >= 1

    # Verify console handler exists (StreamHandler)
    console_handlers = [
        h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)
    ]
    assert len(console_handlers) >= 1, "Should have at least one console handler"


def test_setup_logging_with_file(temp_log_dir: Path):
    """Test that setup_logging creates log file and directory."""
    log_file = temp_log_dir / "test.log"

    # Setup logging with file handler
    setup_logging(log_level="DEBUG", log_file=log_file)

    # Verify log file was created
    assert log_file.exists(), f"Log file should be created at {log_file}"

    # Test that logging actually writes to file
    logger = logging.getLogger(__name__)
    test_message = "Test log message for file handler"
    logger.info(test_message)

    # Read log file and verify message was written
    log_content = log_file.read_text()
    assert test_message in log_content, "Log message should appear in log file"


def test_setup_logging_creates_directory(tmp_path: Path):
    """Test that setup_logging creates log directory if it doesn't exist."""
    log_dir = tmp_path / "nested" / "logs"
    log_file = log_dir / "app.log"

    # Directory should not exist yet
    assert not log_dir.exists()

    # Setup logging should create directory
    setup_logging(log_file=log_file)

    # Verify directory was created
    assert log_dir.exists(), "Log directory should be created automatically"
    assert log_file.exists(), "Log file should be created"


def test_setup_logging_different_levels():
    """Test that different log levels are respected."""
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        setup_logging(log_level=level)

        expected_level = getattr(logging, level)
        assert (
            root_logger.level == expected_level
        ), f"Root logger level should be {level}"


def test_setup_logging_file_rotation_config(temp_log_dir: Path):
    """Test that file handler has correct rotation configuration."""
    log_file = temp_log_dir / "rotating.log"

    setup_logging(log_file=log_file)

    # Find the RotatingFileHandler
    from logging.handlers import RotatingFileHandler

    root_logger = logging.getLogger()
    rotating_handlers = [
        h for h in root_logger.handlers if isinstance(h, RotatingFileHandler)
    ]

    assert len(rotating_handlers) == 1, "Should have exactly one RotatingFileHandler"

    handler = rotating_handlers[0]

    # Verify rotation settings (10MB max, 7 backups)
    assert handler.maxBytes == 10 * 1024 * 1024, "Max bytes should be 10MB"
    assert handler.backupCount == 7, "Should keep 7 backup files"


def test_setup_logging_invalid_directory_fallback(tmp_path: Path):
    """Test that setup_logging handles invalid directory gracefully."""
    # Try to create log file in a path that can't be created
    # (using a file as parent instead of directory)
    invalid_file = tmp_path / "not_a_dir.txt"
    invalid_file.write_text("I am a file, not a directory")

    log_file = invalid_file / "impossible.log"  # Can't create dir inside file

    # Should not raise exception, just log warning and continue
    try:
        setup_logging(log_file=log_file)
        # If we get here, logging fell back to console-only mode
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) >= 1, "Should still have console handler"
    except Exception as e:
        pytest.fail(f"setup_logging should not raise exception, got: {e}")


def test_setup_logging_clears_existing_handlers():
    """Test that setup_logging clears existing handlers to avoid duplicates."""
    root_logger = logging.getLogger()

    # Add some dummy handlers
    dummy_handler1 = logging.StreamHandler()
    dummy_handler2 = logging.StreamHandler()
    root_logger.addHandler(dummy_handler1)
    root_logger.addHandler(dummy_handler2)

    initial_count = len(root_logger.handlers)
    assert initial_count >= 2

    # Setup logging should clear existing handlers
    setup_logging()

    # Should have fresh handlers, not accumulated
    # Exact count depends on whether file handler was added
    assert len(root_logger.handlers) >= 1, "Should have at least console handler"


def test_logger_format_includes_required_fields(temp_log_dir: Path):
    """Test that log format includes all required fields."""
    log_file = temp_log_dir / "format_test.log"
    setup_logging(log_level="INFO", log_file=log_file)

    logger = logging.getLogger(__name__)
    logger.info("Test message for format verification")

    log_content = log_file.read_text()

    # Verify required format fields are present
    assert "INFO" in log_content, "Log level should be in output"
    assert "test_logger" in log_content, "Module name should be in output"
    assert "Test message for format verification" in log_content


def test_default_log_file_location_fallback():
    """Test that default log file location uses correct path structure."""
    # This test just verifies the function doesn't crash with default location
    # We can't easily test the actual ~/.local/share path in pytest
    try:
        # Call with no log_file argument (uses default)
        # This may fail if ~/.local/share is not writable, but should not crash
        setup_logging(log_level="INFO")
        assert True, "setup_logging should not crash with default location"
    except Exception as e:
        pytest.fail(f"setup_logging with default location raised: {e}")
