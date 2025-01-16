"""Deployment utilities for database conversion and release."""

from __future__ import annotations

from logging import getLogger
import os
from pathlib import Path
import zipfile

import requests

logger = getLogger(__name__)


# The config is just a dict mapping versions to URLs
SourceConfig = dict[str, str]


def load_config(config_path: Path) -> SourceConfig:
    """Load the source configuration."""
    import tomllib
    
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def find_access_file(directory: Path) -> Path:
    """Find the first Access database file in a directory."""
    for path in directory.rglob("*.accdb"):
        return path
    raise FileNotFoundError("No Access database file found in zip")


def download_source(version: str, url: str, output_dir: Path) -> None:
    """Download and extract a source database."""
    logger.info("Processing version %s...", version)

    # Create temporary directory for zip extraction
    temp_dir = output_dir / f"temp_{version}"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Download zip file
        zip_path = temp_dir / "download.zip"
        logger.info("Downloading %s...", url)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract zip
        logger.info("Extracting zip file...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(temp_dir)
        
        # Find and move Access file
        access_file = find_access_file(temp_dir)
        target_path = output_dir / f"dpm_{version}.accdb"
        logger.info("Moving %s to %s", access_file, target_path)
        os.replace(access_file, target_path)
        
        logger.info("Successfully downloaded and extracted version %s", version)
    
    finally:
        # Clean up temp directory
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.info("Cleaned up temporary files")


def download_sources(config_path: Path, output_dir: Path) -> None:
    """Download source Access database files."""
    config = load_config(config_path)
    
    for version, url in config.items():
        try:
            download_source(version, url, output_dir)
        except Exception as e:
            logger.error("Failed to process version %s: %s", version, e)
            raise


def generate_release_notes(config_path: Path, output_path: Path) -> None:
    """Generate release notes from source configuration."""
    config = load_config(config_path)

    # Generate release notes
    notes = ["# Database Conversion Release\n"]
    notes.append("## Source Databases\n")

    for version in sorted(config.keys()):
        notes.append(f"### Version {version}")
        notes.append(f"- URL: {config[version]}\n")

    # Write release notes to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(notes))
    
    logger.info("Generated release notes at %s", output_path)
