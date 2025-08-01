"""Progress reporting utilities for database conversion."""

from logging import Logger
from typing import Protocol


class ProgressReporter(Protocol):
    """Protocol for progress reporting during conversion."""

    def start_table(self, table_name: str, total_rows: int) -> None:
        """Call when starting to process a table.

        Args:
            table_name: Name of the table being processed
            total_rows: Total number of rows in the table

        """
        ...

    def update_progress(self, table_name: str, processed_rows: int) -> None:
        """Call to update progress for a table.

        Args:
            table_name: Name of the table being processed
            processed_rows: Number of rows processed so far

        """
        ...

    def finish_table(self, table_name: str) -> None:
        """Call when table processing is complete.

        Args:
            table_name: Name of the table that was processed

        """
        ...


class LoggingProgressReporter(ProgressReporter):
    """Progress reporter that logs to the standard logger."""

    def __init__(self, logger: Logger) -> None:
        """Initialize the progress reporter."""
        self.logger = logger
        self._table_totals: dict[str, int] = {}

    def start_table(self, table_name: str, total_rows: int) -> None:
        """Start processing a table."""
        self._table_totals[table_name] = total_rows
        self.logger.info("Processing table: %s (%d rows)", table_name, total_rows)

    def update_progress(self, table_name: str, processed_rows: int) -> None:
        """Update progress for a table."""
        total = self._table_totals.get(table_name, 0)
        if total > 0:
            percentage = (processed_rows / total) * 100
            self.logger.debug(
                "Table %s: %d/%d rows (%.1f%%)",
                table_name,
                processed_rows,
                total,
                percentage,
            )

    def finish_table(self, table_name: str) -> None:
        """Finish processing a table."""
        total = self._table_totals.get(table_name, 0)
        self.logger.info("Completed table: %s (%d rows)", table_name, total)
        self._table_totals.pop(table_name, None)


class SilentProgressReporter(ProgressReporter):
    """Progress reporter that does nothing (for testing or quiet operation)."""

    def start_table(self, table_name: str, total_rows: int) -> None:
        """Start processing a table (silent)."""

    def update_progress(self, table_name: str, processed_rows: int) -> None:
        """Update progress for a table (silent)."""

    def finish_table(self, table_name: str) -> None:
        """Finish processing a table (silent)."""
