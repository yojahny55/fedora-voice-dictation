"""Main entry point for Fedora Voice Dictation.

This module serves as the application entry point when run as:
    python -m src [arguments]

Currently implements basic health check and version reporting.
Full application functionality will be added in future stories.
"""

import argparse
import sys

from src import __version__


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = argparse.ArgumentParser(
        prog="fedora-voice-dictation",
        description="Offline, low-latency voice-to-text dictation for Fedora Linux",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and exit",
    )

    # Parse arguments
    parser.parse_args()

    # If we get here, no arguments were provided
    print(f"Fedora Voice Dictation v{__version__}")
    print("Run with --help for usage information")
    print("\nNote: Full application functionality coming in future releases.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
