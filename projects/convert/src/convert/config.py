"""Configuration management for the convert module."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import Boolean, DateTime
from sqlalchemy.types import TypeEngine

from convert.transformations import FieldValue


@dataclass
class ColumnType:
    """Column type mapping with SQL type and optional Python transformer."""

    sql: TypeEngine[Any]
    python: Callable[[FieldValue], FieldValue] | None = None


@dataclass
class ColumnPatterns:
    """Configuration for column pattern recognition."""

    # Suffixes that indicate enum columns
    enum_suffixes: tuple[str, ...] = (
        "type",
        "status",
        "sign",
        "optionality",
        "direction",
        "number",
        "endorsement",
        "source",
        "severity",
        "errorcode",
    )

    # Suffixes that indicate GUID columns
    guid_suffixes: tuple[str, ...] = ("guid",)

    # Prefixes that indicate boolean columns
    bool_prefixes: tuple[str, ...] = ("is", "has")

    # Suffixes that indicate date columns
    date_suffixes: tuple[str, ...] = ("date",)


@dataclass
class ConversionConfig:
    """Main configuration for database conversion."""

    # Column pattern recognition
    patterns: ColumnPatterns = field(default_factory=ColumnPatterns)

    # Specific column type overrides
    column_type_overrides: dict[str, ColumnType] = field(
        default_factory=lambda: {
            "ParentFirst": ColumnType(sql=Boolean(), python=bool),
            "UseIntervalArithmetics": ColumnType(sql=Boolean(), python=bool),
            "StartDate": ColumnType(sql=DateTime()),
            "EndDate": ColumnType(sql=DateTime()),
        },
    )

    # Foreign key mappings
    foreign_key_mappings: dict[str, str] = field(
        default_factory=lambda: {
            "RowGUID": "Concept.ConceptGUID",
            "ParentItemID": "Item.ItemID",
        },
    )

    # SQLite optimization settings
    sqlite_settings: dict[str, Any] = field(
        default_factory=lambda: {
            "disable_rowid_for_pk_tables": True,
            "clear_indexes": True,
        },
    )

    # Model generation settings
    model_generation: dict[str, Any] = field(
        default_factory=lambda: {
            "base_class_name": "DPM",
            "indent": "    ",
            "use_type_checking_imports": True,
        },
    )


def load_config(config_path: Path | None = None) -> ConversionConfig:
    """Load configuration from file or return default configuration.

    Args:
        config_path: Optional path to configuration file (TOML format)

    Returns:
        ConversionConfig instance

    Note:
        Currently returns default config. File loading can be implemented
        using tomllib when needed.

    """
    if config_path and config_path.exists():
        pass

    return ConversionConfig()
