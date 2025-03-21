# OpenDPM

Convert EBA DPM 2.0 (Data Point Model) databases from AccessDB to SQLite.

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by the European Banking Authority (EBA). The original AccessDB source is available at the [EBA DPM Website](https://www.eba.europa.eu/risk-and-data-analysis/reporting-frameworks/dpm-data-dictionary).

## Overview

This project provides pre-converted SQLite versions of the EBA DPM 2.0 databases, making them accessible across all platforms.

### Why This Project?

The current DPM 2.0 releases from EBA are only provided in AccessDB format, which has limited support outside of Windows operating systems. In addition, the DPM 2.0 releases are only provided in "incremental" format, keeping each release self-contained. This project solves these limitations by:
- Converting the databases to SQLite
- Combining all releases into a single file
- Making the data consistently accessible via HTTP
- Providing automated conversion through GitHub Actions
- Publishing new releases with converted databases

### Database Compatibility

The converted SQLite databases targets full compatibility with the original Access database structure, maintaining all relationships, and constraints. Although due to cyclic dependencies, referential integrity may not be preserved, and Foreign Key constraints are not enforced.

## Getting Started

### Option 1: Download Pre-converted Databases

The easiest way to get started is to download the converted databases from our [Releases page](https://github.com/JimLundin/opendpm/releases). Each release contains the latest converted databases.

You can download the latest releases either by:
- Using this URL in your scripts:
```
https://github.com/JimLundin/opendpm/releases/latest/download/dpm-sqlite.zip
```
- Or clicking here: [Download Latest DPM SQLite Database](https://github.com/JimLundin/opendpm/releases/latest/download/dpm-sqlite.zip)

### Option 2: Run the Conversion Yourself

If you want to run the conversion process yourself:

1. Fork this repository
2. Enable GitHub Actions in your fork
3. Run the conversion workflow manually
4. Find the converted databases in the workflow artifacts

## Development

If you want to run the conversion locally:

1. Clone the repository
2. Ensure you have Python 3.12+ installed
3. Install the Microsoft Access ODBC driver
4. Install the package in development mode: `pip install -e .`
5. Run the conversion:
   ```
   opendpm convert <source_dir> <target_dir>
   ```

## Column Casting Conventions

During the conversion from Access to SQLite, specific column casting rules are applied based on naming conventions to ensure proper data typing:

 - GUID columns are classified as Integer in the Source but due to their representation as String, as such all columns ending in "GUID" are casted to Text.
 - Dates are classified as String in the Source, to account for this we cast any columns ending in "Date" to Date.
 - Boolean columns are classified as Integer in the Source, most likely due to legacy support for older versions of Access, where boolean columns are stored as integer with 0 being false and -1 being true due to it being the twos complement of 0. We classify all columns starting with "is" or "has" as Boolean.
 - Some columns do not follow the above rules and are manually casted to the correct type.
 - All other columns are classified as generic types

These casting rules are not in direct correspondence with the original Access database schema, but they are chosen to ensure proper data typing in the target database.

## Caveats

- Currently only the current DPM release data is extracted, not data from previous releases
- Queries from the original database are not preserved
- Local conversion requires Microsoft Access ODBC driver to be installed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
