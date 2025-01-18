"""Functions for converting Access databases to DuckDB and SQLite formats."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import MetaData, create_engine

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def list_access_databases(directory: Path) -> list[Path]:
    """List all Access databases in a directory."""
    return list(directory.glob("**/*.accdb"))


def migrate_databases(source_dir: Path, target_paths: list[Path]) -> None:
    """Migrate databases from source directory to target databases."""
    # Create target engines based on file extensions
    target_engines: list[Engine] = []
    for path in target_paths:
        if path.suffix == ".sqlite":
            url = f"sqlite:///{path}"
        elif path.suffix == ".duckdb":
            url = f"duckdb:///{path}"
        else:
            logger.error("Unsupported database type: %s", path.suffix)
            continue

        logger.info("Creating target engine for: %s", path)
        target_engines.append(create_engine(url))

    # Process each source database
    for source_path in list_access_databases(source_dir):
        logger.info("Processing database: %s", source_path.name)
        driver = "{Microsoft Access Driver (*.mdb, *.accdb)}"
        conn_str = f"DRIVER={driver};DBQ={source_path}"
        source_engine = create_engine(f"access+pyodbc:///?odbc_connect={conn_str}")

        # Get all tables
        metadata = MetaData()
        metadata.reflect(bind=source_engine)

        # Copy each table to all targets
        for table_name, table in metadata.tables.items():
            logger.info("Copying table: %s", table_name)

            try:
                # Read all data
                data = source_engine.execute(table.select()).fetchall()

                # Copy to each target
                for engine in target_engines:
                    table.metadata = MetaData()
                    table.create(engine, checkfirst=True)

                    if data:
                        with engine.begin() as conn:
                            conn.execute(table.insert(), data)
                    else:
                        logger.warning("Table %s is empty", table_name)
            except Exception:
                logger.exception("Failed to process table %s", table_name)
                continue


def process_access_files(input_dir: Path, output_dir: Path) -> None:
    """Process all Access files in the input directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = [
        output_dir / "dpm.sqlite",
        output_dir / "dpm.duckdb",
    ]

    migrate_databases(input_dir, targets)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]
    input_dir = project_root / ".scratch" / "db_input"
    output_dir = project_root / ".scratch" / "db_output"
    process_access_files(input_dir, output_dir)
