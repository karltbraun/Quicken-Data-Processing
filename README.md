# Quicken Data Processing

Parse Quicken expense reports (CSV and PDF formats) and generate financial analysis charts.

## Overview

This project automates the extraction of expense data from Quicken CSV exports (primary) or PDF reports (alternative) and generates visual analysis charts organized by category and month.

## Features

- 📄 **Parse Quicken expense reports**
  - CSV format (primary - most complete data)
  - PDF format (alternative/backup method)
- 📊 Generate monthly trend charts
- 📈 Category-based expense analysis
- 💾 Export structured data to CSV format
- 🔍 Configurable category filtering
- 🚫 Automatic filtering of inflows and summary rows

## Project Status

**Current Version:** 0.1.0 (Alpha)

This is an early-stage project. Core parsing functionality is complete. Visualization features are in development.

## Requirements

- Python 3.12 or higher
- See `pyproject.toml` for full dependency list

## Installation

1. Clone the repository:

```bash
git clone https://github.com/karltbraun/Quicken-Data-Processing.git
cd "Quicken Data Processing"
```

2. Create and activate virtual environment using `uv`:

```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install the package in editable mode with development dependencies:

```bash
uv pip install -e ".[dev]"
```

## Usage

### Using CSV Export (Recommended)

1. Export your expense report from Quicken (Mac) to CSV format
2. Parse the CSV file:

```python
from quicken_parser import parse_quicken_csv

# Parse CSV export
df = parse_quicken_csv("./data/Expenses-2025-01-2025-11.csv", verbose=True)

# View results
print(df.head())
print(f"Total categories: {len(df)}")

# Save to CSV
df.to_csv("./reports/expenses_parsed.csv", index=False)
```

### Using PDF Report (Alternative)

```python
from quicken_parser import parse_quicken_pdf

# Parse PDF report
df = parse_quicken_pdf("./data/Expenses-2025-01-2025-11.pdf", verbose=True)

# Note: PDF parsing captures fewer categories than CSV
print(df.head())
```

### Command Line Usage

```bash
# Test CSV parser
python test_csv_parser.py

# Test PDF parser
python test_parser.py
```

## Output Format

Both parsers produce DataFrames with the following structure:

| Column              | Description                                    |
| ------------------- | ---------------------------------------------- |
| `category`          | Expense category name                          |
| `indent_level`      | Hierarchy level (for nested categories)        |
| `1/1/25 - 1/31/25`  | Monthly expense amounts (one column per month) |
| `report_start_date` | Report start date                              |
| `report_end_date`   | Report end date                                |

Example output:
```
category                  1/1/25 - 1/31/25  2/1/25 - 2/28/25  ...
Groceries                 -1293.53          -1282.94          ...
Dental Ins                -135.66           -135.66           ...
```

## Project Structure

```
Quicken Data Processing/
├── src/
│   └── quicken_parser/
│       ├── __init__.py          # Package exports
│       ├── csv_parser.py        # CSV parsing (primary)
│       └── pdf_parser.py        # PDF parsing (alternative)
├── data/                        # Input data files (.gitignored)
├── reports/                     # Output files (.gitignored)
├── tests/                       # Test files
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Development

### Running Tests

```bash
# Test CSV parser with comparison
uv run python test_csv_parser.py

# Test PDF parser
uv run python test_parser.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff src/ tests/

# Type checking
mypy src/
```

## Known Limitations

- **PDF Parser**: Only captures categories with values displayed on parsed pages (~25% of total categories)
- **CSV Parser**: Requires properly formatted Quicken CSV export
- Visualization features are not yet implemented
- No front-end UI (command-line only)

## Roadmap

- [x] CSV expense parser
- [x] PDF expense parser
- [x] Data consolidation and filtering
- [ ] Visualization charts (monthly trends, category breakdowns)
- [ ] Configuration system for category filtering
- [ ] Web-based front-end
- [ ] Automated report generation

## License

MIT

## Author

Karl T. Braun
