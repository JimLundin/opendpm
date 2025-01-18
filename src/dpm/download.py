"""Module for downloading and managing Access database files."""

from __future__ import annotations

import os
import tempfile
import tomllib
import zipfile
from logging import getLogger
from pathlib import Path

import requests

logger = getLogger(__name__)


def load_sources(config_file: Path) -> dict[str, str]:
    """Load database source URLs from the config file."""
    with open(config_file, "rb") as f:
        return tomllib.load(f)


def download_and_extract(url: str, target_dir: Path) -> None:
    """Download and extract a zip file containing Access databases."""
    target_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        try:
            logger.info("Downloading from %s", url)
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Download the file
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.flush()

            # Extract the file
            logger.info("Extracting to %s", target_dir)
            with zipfile.ZipFile(temp_file.name) as zip_ref:
                for zip_info in zip_ref.filelist:
                    if zip_info.filename.lower().endswith((".mdb", ".accdb")):
                        zip_ref.extract(zip_info, target_dir)
                        logger.info("Extracted %s", zip_info.filename)

        except requests.RequestException as e:
            logger.exception("Failed to download from %s: %s", url, e)
            raise
        except zipfile.BadZipFile as e:
            logger.exception("Failed to extract %s: %s", url, e)
            raise
        finally:
            os.unlink(temp_file.name)


def download_databases(config_file: Path, target_dir: Path) -> None:
    """Download all database files specified in the config."""
    sources = load_sources(config_file)
    for version, url in sources.items():
        try:
            download_and_extract(url, target_dir)
            logger.info("Successfully downloaded version %s", version)
        except Exception as e:
            logger.exception("Failed to download version %s: %s", version, e)
