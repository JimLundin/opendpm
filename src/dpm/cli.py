"""Command-line interface for database conversion and deployment."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

from .deploy import download_sources, generate_release_notes
from .main import process_access_files


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> int:
    """Main entry point for deployment CLI."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Set up paths
        project_root = Path(__file__).resolve().parents[2]
        config_path = project_root / "config" / "sources.toml"
        assets_dir = project_root / "assets"
        output_dir = project_root / ".scratch" / "db_output"
        release_notes_path = project_root / "release_notes.md"

        # Ensure directories exist
        assets_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download source files
        download_sources(config_path, assets_dir)

        # Convert databases
        process_access_files(assets_dir, output_dir)

        # Generate release notes
        generate_release_notes(config_path, release_notes_path)

        return 0

    except Exception as e:
        logger.error("Deployment failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
