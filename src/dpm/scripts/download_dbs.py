"""Script to download database files."""

from pathlib import Path
import logging

from ..download import download_databases

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]
    config_path = project_root / "config" / "sources.toml"
    input_dir = project_root / ".scratch" / "db_input"
    
    download_databases(config_path, input_dir)
