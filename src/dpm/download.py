"""Module for downloading and managing Access database files."""

from __future__ import annotations

import io
import logging
import tomllib
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def load_sources(config_file: Path) -> dict[str, str]:
    """Load database source URLs from the config file."""
    with config_file.open("rb") as f:
        return tomllib.load(f)


def download_and_extract(url: str, target_dir: Path) -> None:
    """Download and extract a zip file containing Access databases."""
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Downloading from %s", url)
        if not url.startswith(("http://", "https://")):
            msg = f"Invalid URL: {url}, url should start with http:// or https://"
            raise ValueError(msg)

        response = urlopen(url, timeout=30)  # noqa: S310
        logger.info("Extracting to %s", target_dir)
        with zipfile.ZipFile(io.BytesIO(response.read())) as zip_ref:
            for zip_info in zip_ref.filelist:
                if zip_info.filename.lower().endswith(".accdb"):
                    zip_ref.extract(zip_info, target_dir)
                    logger.info("Extracted %s", zip_info.filename)

    except (URLError, HTTPError, zipfile.BadZipFile):
        logger.exception("Failed to process %s", url)
        raise


def download_databases(config_file: Path, target_dir: Path) -> None:
    """Download all database files specified in the config."""
    sources = load_sources(config_file)
    for version, url in sources.items():
        try:
            download_and_extract(url, target_dir)
            logger.info("Successfully downloaded version %s", version)
        except Exception:
            logger.exception("Failed to download version %s", version)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]
    config_path = project_root / "config" / "sources.toml"
    input_dir = project_root / ".scratch" / "db_input"

    download_databases(config_path, input_dir)
