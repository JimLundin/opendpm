"""Exception classes for the convert module."""


class ConversionError(Exception):
    """Base exception for all conversion-related errors."""


class DatabaseNotFoundError(ConversionError):
    """Raised when no Access database is found in the specified location."""


class DatabaseConnectionError(ConversionError):
    """Raised when unable to connect to the Access database."""


class SchemaExtractionError(ConversionError):
    """Raised when schema extraction from Access database fails."""


class DataExtractionError(ConversionError):
    """Raised when data extraction from Access database fails."""


class SQLiteCreationError(ConversionError):
    """Raised when SQLite database creation fails."""


class ModelGenerationError(ConversionError):
    """Raised when SQLAlchemy model generation fails."""
