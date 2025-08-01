"""Main module for database conversion."""

from datetime import UTC, datetime
from logging import getLogger
from pathlib import Path

from sqlalchemy import create_engine, text

from convert.generation import Model
from convert.processing import (
    create_access_engine,
    extract_schema_and_data,
    get_database,
    load_data,
)

logger = getLogger(__name__)


def convert_access_to_sqlite(source: Path, target: Path) -> None:
    """Migrate Access databases to SQLite.

    Args:
        source: Directory or path to Access database
        target: Directory to store SQLite database

    """
    start_time = datetime.now(UTC)

    database = source if source.is_file() else get_database(source)
    if not database:
        logger.warning("No Access database files found in %s", source)
        return

    logger.info("Processing: %s", database.stem)

    access = create_access_engine(database)
    metadata, tables = extract_schema_and_data(access)

    target.mkdir(parents=True, exist_ok=True)
    with (target / "dpm.py").open("w") as model_file:
        model_file.write(Model(metadata).render())

    sqlite_path = target / "dpm.sqlite"
    if sqlite_path.exists():
        logger.warning("Target database already exists, overwriting.")
        sqlite_path.unlink(missing_ok=True)

    sqlite = create_engine("sqlite:///:memory:")
    metadata.create_all(sqlite)
    load_data(sqlite, tables)

    with sqlite.connect() as connection:
        connection.execute(text(f"VACUUM INTO '{sqlite_path}'"))
        logger.info("Saved: %s", sqlite_path)

    stop_time = datetime.now(UTC)
    logger.info("Migrated database in %s", stop_time - start_time)
