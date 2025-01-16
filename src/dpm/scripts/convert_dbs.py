"""Script to convert database files."""

from pathlib import Path
import logging

from ..convert import process_access_files

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]
    input_dir = project_root / ".scratch" / "db_input"
    output_dir = project_root / ".scratch" / "db_output"
    
    process_access_files(input_dir, output_dir)
