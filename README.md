# OpenDPM

Convert EBA DPM (Data Point Model) databases from Access to DuckDB and SQLite formats.

## Overview

This project provides a distribution of the EBA DPM databases in DuckDB and SQLite formats. The original AccessDB source is available at the [EBA DPM Website](https://www.eba.europa.eu/risk-and-data-analysis/reporting-frameworks/dpm-data-dictionary).

### Why This Project?

The current DPM releases are only provided in AccessDB format, which has limited support outside of Windows operating systems. This project solves that limitation by:
- Converting the databases to DuckDB and SQLite formats
- Making the data accessible on any platform
- Providing an distribution of the databases

## Caveats

- Only the current DPM release data is extracted, not data from previous releases
- Functional components (queries, indexes) from the original database are not preserved

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided "as is" and without warranty of any kind, either express or implied. Use at your own risk.

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by the European Banking Authority (EBA).