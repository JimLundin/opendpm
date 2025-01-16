"""Script converts Access database files to SQLite and DuckDB formats."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
import sqlite3
import pyodbc
import duckdb

import polars as pl

logger = getLogger(__name__)


def list_access_files(directory: Path) -> list[Path]:
    """List all Access database files in the given directory."""
    return list(directory.glob("*.mdb")) + list(directory.glob("*.accdb"))


def read_access_database(file_path: Path) -> dict[str, pl.DataFrame]:
    """Read all tables from an Access database file."""
    connection_string = (
        f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
        f"DBQ={file_path};"
    )
    with pyodbc.connect(connection_string) as connection:
        try:
            logger.info("Connected to Access database %s", file_path)
            # Get table names
            with connection.cursor() as cursor:
                access_tables = cursor.tables(tableType='TABLE')
                table_names: list[str] = [table.table_name for table in access_tables]
            logger.info("Found tables: %s", table_names)
            
            tables: dict[str, pl.DataFrame] = {}
            for table_name in table_names:
                try:
                    # Read each table into a Polars DataFrame
                    query = f"SELECT * FROM [{table_name}]"
                    df = pl.read_database(query, connection)
                    if not df.is_empty():
                        tables[table_name] = df
                    else:
                        logger.warning("Table %s is empty", table_name)
                except Exception as e:
                    logger.error("Failed to read table %s: %s", table_name, e)
                    continue
            
            if not tables:
                logger.warning("No tables found in %s", file_path)
            
            return tables
        except Exception as e:
            logger.error("Failed to read database %s: %s", file_path, e)
            raise e


def save_to_duckdb(data: dict[str, pl.DataFrame], output_file: Path) -> None:
    """Save all tables in a DuckDB file."""
    with duckdb.connect(output_file) as con:
        for table_name, df in data.items():
            try:
                df.write_database(table_name, con)
                logger.info("Saved table %s to DuckDB", table_name)
            except Exception as e:
                logger.error("Failed to create table %s in DuckDB: %s", table_name, e)
                continue


def save_to_sqlite(data: dict[str, pl.DataFrame], output_file: Path) -> None:
    """Save all tables in a SQLite file."""
    with sqlite3.connect(output_file) as con:
        for table_name, df in data.items():
            try:
                df.write_database(table_name, con)
                logger.info("Saved table %s to SQLite", table_name)
            except Exception as e:
                logger.error("Failed to create table %s in SQLite: %s", table_name, e)
                continue


def process_access_files(input_dir: Path, output_dir: Path) -> None:
    """Process all Access files in the input directory."""
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Input directory: %s", input_dir)
    logger.info("Output directory: %s", output_dir)
    
    # Process each Access file
    for access_file in list_access_files(input_dir):
        try:
            # Read tables from Access database
            data = read_access_database(access_file)
            
            if data:
                # Save to both DuckDB and SQLite
                duckdb_file = output_dir / f"{access_file.stem}.duckdb"
                sqlite_file = output_dir / f"{access_file.stem}.sqlite"
                
                save_to_duckdb(data, duckdb_file)
                save_to_sqlite(data, sqlite_file)
                logger.info("Successfully processed %s", access_file)
            
        except Exception as e:
            logger.error("Failed to process %s: %s", access_file, e)


def main() -> None:
    """Execute the script."""
    # Set up input and output directories
    input_dir = Path("/home/jim/dpm/assets")
    output_dir = Path("/home/jim/dpm/.scratch/db_output")
    
    # Process all Access files
    process_access_files(input_dir, output_dir)


if __name__ == "__main__":
    main()
