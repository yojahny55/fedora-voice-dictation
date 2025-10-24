"""Logging configuration and setup for Fedora Voice Dictation.

This module provides centralized logging configuration with console and file
output. Logs are written to ~/.local/share/fedora-voice-dictation/logs/ with
automatic rotation (7-day retention, 10MB max per file).

Usage:
    Call setup_logging() once at application startup:

    >>> from src.utils.logger import setup_logging
    >>> setup_logging(log_level="INFO")

    Then use module-level loggers throughout the codebase:

    >>> import logging
    >>> logger = logging.getLogger(__name__)
    >>> logger.info("Application started")
    >>> logger.error("An error occurred", exc_info=True)
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: Path | None = None) -> None:
    """Configure application logging with console and file handlers.

    Sets up a root logger with two handlers:
    - Console handler (stderr): For interactive terminal output
    - File handler (optional): For persistent logs with rotation

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  Defaults to INFO.
        log_file: Optional file path for log output. If None, defaults to
                 ~/.local/share/fedora-voice-dictation/logs/app.log.

    Example:
        >>> # Basic setup with INFO level
        >>> setup_logging()

        >>> # Debug mode with custom log file
        >>> setup_logging(log_level="DEBUG", log_file=Path("/tmp/debug.log"))

    Notes:
        - Console logs use stderr (not stdout) for proper stream separation
        - File logs include more detail (filename and line number)
        - Log directory is created automatically if it doesn't exist
        - File rotation: 10MB max size, keep last 7 backup files
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicate logs
    if root_logger.handlers:
        root_logger.handlers.clear()

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation (optional)
    if log_file is None:
        # Default log file location
        log_dir = Path.home() / ".local" / "share" / "fedora-voice-dictation" / "logs"
        log_file = log_dir / "app.log"
    else:
        log_dir = log_file.parent

    # Create log directory if it doesn't exist
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # If we can't create log directory, log to console only
        console_handler.setLevel(logging.WARNING)
        root_logger.warning(
            f"Could not create log directory {log_dir}: {e}. "
            "Logging to console only."
        )
        return

    # Rotating file handler: 10MB max, keep last 7 backups (7 days retention)
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=7,  # Keep last 7 rotated log files
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        root_logger.debug(f"Logging initialized. Log file: {log_file}")
    except OSError as e:
        root_logger.warning(
            f"Could not create log file {log_file}: {e}. " "Logging to console only."
        )
