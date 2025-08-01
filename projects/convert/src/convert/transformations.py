"""Schema transformation utilities for database conversion."""

from collections import defaultdict
from collections.abc import Callable, Sequence
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Inspector,
    Integer,
    Row,
    Table,
    Uuid,
)
from sqlalchemy.engine.interfaces import ReflectedColumn

from convert.config import ConversionConfig, load_config

type FieldValue = str | int | bool | date | datetime | None
type TableRow = dict[str, FieldValue]
type TableData = list[TableRow]
type ColumnNames = set[str]
type ColumnEnumMap = dict[str, set[str]]
type Rows = Sequence[Row[Any]]


def init_config(
    config: ConversionConfig | None = None,
) -> Callable[[], ConversionConfig]:
    """Initialize the global configuration instance."""
    _config = config or load_config()

    def get_config() -> ConversionConfig:
        """Get the global configuration instance."""
        return _config

    return get_config


get_config = init_config()


def is_guid(column: str) -> bool:
    """Check if a column is a GUID column."""
    config = get_config()
    return column.lower().endswith(config.patterns.guid_suffixes)


def is_bool(column: str) -> bool:
    """Check if a column is a boolean column."""
    config = get_config()
    return column.lower().startswith(config.patterns.bool_prefixes)


def is_date(column: str) -> bool:
    """Check if a column is a date column."""
    config = get_config()
    return column.lower().endswith(config.patterns.date_suffixes)


def is_enum(column: str) -> bool:
    """Check if a column is an enum column."""
    config = get_config()
    return column.lower().endswith(config.patterns.enum_suffixes)


def genericize(_i: Inspector, _t: str, column: ReflectedColumn) -> None:
    """Refine column datatypes during database reflection.

    This function enhances SQLAlchemy's type reflection by analyzing column names
    and applying more appropriate data types. The source database often uses generic
    types (like Integer or String) for specialized data such as GUIDs, dates, and
    booleans, which this function corrects based on naming conventions and known
    column characteristics.
    """
    config = get_config()
    column_name = column["name"]
    column_type = column["type"]

    if column_name in config.column_type_overrides:
        column_type = config.column_type_overrides[column_name].sql
    elif is_guid(column_name):
        column_type = Uuid()
    elif is_date(column_name):
        column_type = Date()
    elif is_bool(column_name):
        column_type = Boolean()
    elif isinstance(column_type, Integer):
        column_type = Integer()
    else:
        column_type = column_type.as_generic()

    column["type"] = column_type


def cast_value(column: str, value: FieldValue) -> FieldValue:
    """Transform row values to appropriate Python types."""
    if value is None:
        return None

    config = get_config()
    if column in config.column_type_overrides:
        column_config = config.column_type_overrides[column]
        if column_config.python:
            return column_config.python(value)

    if is_date(column) and isinstance(value, str):
        return date.fromisoformat(value)
    if is_bool(column):
        return bool(value)
    return value


def parse(table_rows: Rows) -> tuple[TableData, ColumnEnumMap, ColumnNames]:
    """Transform row values to appropriate Python types."""
    rows: TableData = []
    enums: ColumnEnumMap = defaultdict(set)
    nullables: ColumnNames = set()
    for table_row in table_rows:
        row = table_row._asdict()  # pyright: ignore[reportPrivateUsage]
        rows.append(row)
        for column in row:
            new_value = cast_value(column, row[column])
            row[column] = new_value
            if is_enum(column) and isinstance(new_value, str):
                enums[column].add(new_value)
            if new_value is None:
                nullables.add(column)

    return rows, enums, nullables


def apply_enums(table: Table, enums: ColumnEnumMap) -> None:
    """Set enum columns for a table."""
    for column in table.columns:
        if column.name in enums:
            column.type = Enum(*enums[column.name])


def mark_non_nullable(table: Table, nullables: ColumnNames) -> None:
    """Set nullable status for columns based on data analysis."""
    for column in table.columns:
        if column.name not in nullables:
            column.nullable = False


def add_foreign_key(source_column: str, target_column: str, table: Table) -> None:
    """Set missing foreign keys."""
    column = table.columns.get(source_column)
    if column is None or column.foreign_keys:
        return
    column.append_foreign_key(ForeignKey(target_column))


def add_foreign_keys(table: Table) -> None:
    """Set missing foreign keys."""
    config = get_config()
    for source_col, target_col in config.foreign_key_mappings.items():
        add_foreign_key(source_col, target_col, table)
