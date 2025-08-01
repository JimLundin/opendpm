"""Main module for database conversion."""

from datetime import UTC, datetime
from logging import getLogger
from pathlib import Path

from sqlalchemy import create_engine, text

from convert.exceptions import (
    ConversionError,
    DatabaseNotFoundError,
    ModelGenerationError,
    SQLiteCreationError,
)
from convert.generation import Model
from convert.processing import (
    create_access_engine,
    extract_schema_and_data,
    get_database,
    load_data,
)
from convert.progress import LoggingProgressReporter

logger = getLogger(__name__)


def convert_access_to_sqlite(source: Path, target: Path) -> None:
    """Migrate Access databases to SQLite.

    Args:
        source: Directory or path to Access database
        target: Directory to store SQLite database

    Raises:
        DatabaseNotFoundError: If no Access database is found
        ConversionError: If conversion fails for any reason

    """
    start_time = datetime.now(UTC)

    try:
        database = source if source.is_file() else get_database(source)
        if not database:
            msg = f"No Access database files found in {source}"
            raise DatabaseNotFoundError(msg)

        logger.info("Processing: %s", database.stem)

        # Database connection and schema extraction
        try:
            access = create_access_engine(database)
            progress_reporter = LoggingProgressReporter(logger)
            metadata, tables = extract_schema_and_data(access, progress_reporter)
        except Exception as e:
            msg = f"Failed to extract data from {database}: {e}"
            raise ConversionError(msg) from e

        # Model generation
        try:
            target.mkdir(parents=True, exist_ok=True)
            model_content = Model(metadata).render()
            with (target / "dpm.py").open("w") as model_file:
                model_file.write(model_content)
        except Exception as e:
            msg = f"Failed to generate SQLAlchemy models: {e}"
            raise ModelGenerationError(msg) from e

        # SQLite database creation
        try:
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
        except Exception as e:
            msg = f"Failed to create SQLite database: {e}"
            raise SQLiteCreationError(msg) from e

        stop_time = datetime.now(UTC)
        logger.info("Migrated database in %s", stop_time - start_time)

    except (
        DatabaseNotFoundError,
        ConversionError,
        ModelGenerationError,
        SQLiteCreationError,
    ):
        raise
    except Exception as e:
        msg = f"Unexpected error during conversion: {e}"
        raise ConversionError(msg) from e
