# Quicken Data Processing

Parse Quicken expense reports from CSV exports and generate financial analysis charts and tables.

> **Note:**
> This project was mostly vibe-coded. The current version is functional but may contain rough edges. Current objective is to
> review and refine but the current code base will give you reasonable functionality for parsing Quicken CSV exports and generating reports.

## Overview

This project automates the extraction of expense data from Quicken CSV exports and generates visual analysis charts and tabular reports organized by category and month using a flexible YAML configuration system.

## Features

- 📄 **Parse Quicken expense reports**
  - CSV format with complete data capture
  - Supports both "Income and Expense" and "Cash Flow" report formats
  - Handles section detection for Income/Expenses or Inflows/Outflows
- 📊 **Generate monthly trend charts**
  - Customizable color palettes for line graphs (15 colors)
  - Expanding cumulative averages with dashed lines
  - Configurable chart dimensions and styling
- 📈 **Category-based expense analysis**
  - YAML configuration for defining custom report groups
  - Automatic category grouping and totals
- 💾 **Export structured data**
  - Timestamped CSV tables for each report group
  - Monthly expense breakdowns
- 🔍 **Configurable category filtering**
  - Define report groups in YAML configuration
  - Error handling modes (fill_zero, skip, error)
    - if a requested category is missing from the data due to no values in any month, the category is reported on as all zeros in time range.
- 🚫 **Automatic filtering** of inflows and summary rows
- 🖥️ **CLI Tool**: `quicken-report` command for easy report generation

## Project Status

**Current Version:** 1.0

Core functionality complete: CSV parsing, configuration system, chart generation, and table generation are all implemented and tested.

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

## Getting Started

### Exporting Data from Quicken

This tool processes expense reports exported from Quicken. These instructions are based on **Quicken for Mac** (Quicken Classic, Business and Personal).

**Steps to export your data:**

1. **Generate a Category Summary Report** in Quicken:
   - Select the accounts and categories you want to analyze
   - Choose report type: "Income and Expense" or "Cash Flow"
   - Set interval to: **Month**
   - Set columns to: **Time**
   - Verify all target categories appear in the report

2. **Export the report to CSV**:
   - Click the **Export** button in the report window
   - Save the file to the `data/` folder in this repository
   - Example filename: `data/Expenses-20250101-20251231.csv`

### Quick Example

Once you have your CSV export:

```bash
quicken-report --config reports_config.yaml --input data/Expenses-20250101-20251231.csv
```

This will generate charts and tables in the `./reports/` directory.

By default the tool writes a **single Excel workbook** when
`table_format` is set to `xlsx` (the `combined_tables` option defaults to
`true`). If you prefer separate files you can disable it in the config or
on the command line.

Example YAML snippet:

```yaml
output_settings:
  table_format: "xlsx" # csv (default), xlsx, or html
  combined_tables: false # optional; only needed to override the default
```

Command-line overrides:

```bash
quicken-report --config reports_config.yaml \
               --input data/expenses.csv \
               --table-format xlsx        # change format
               --separate-tables          # explicitly ask for separate files
```

## Usage

### Exporting from Quicken

Before using this tool, you need to export your expense data from Quicken as a CSV file. See the [Getting Started](#getting-started) section above for detailed export instructions.

### Command-Line Interface

Generate all reports (charts and tables) using the configuration file:

```bash
quicken-report --config reports_config.yaml --input data/Expenses-2025.csv
```

This will:

- Parse the Quicken CSV export
- Create report groups defined in `reports_config.yaml`
- Generate line charts in `./reports/charts/`
- Generate timestamped CSV tables in `./reports/`

### Configuration File

Create a `reports_config.yaml` file to define your report groups:

```yaml
report_groups:
  - output_name: "groceries"
    title: "Groceries Monthly Expenses"
    categories:
      - "510 Groceries"

  - output_name: "utilities"
    title: "Utilities (Electric, Gas, Water)"
    categories:
      - "570 Utilities:Electric"
      - "570 Utilities:Gas"
      - "570 Utilities:Water"

display_settings:
  colors:
    - "#1f77b4" # Blue
    - "#ff7f0e" # Orange
    # ... (15 colors total)
  group_total_color: "#000000" # Black for totals
```

See the included `reports_config.yaml` for a complete example.

### Using CSV Export Programmatically

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

### Development and Testing

```bash
# Run tests
uv run python test_csv_parser.py
uv run python test_charts.py
uv run python test_e2e.py
```

## Output Format

### Generated Files

Running `quicken-report` creates:

**Charts** (in `./reports/charts/`):

- Line charts for each report group
- PNG format with configurable dimensions
- Expanding cumulative averages (dashed lines)

**Tables** (in `./reports/`):

- Timestamped CSV files (e.g., `groceries_20250121_143022.csv`)
- One table per report group
- Monthly breakdowns with category totals

### DataFrame Structure

Both parsers produce DataFrames with the following structure:

| Column              | Description                                    |
| ------------------- | ---------------------------------------------- |
| `category`          | Expense category name                          |
| `indent_level`      | Hierarchy level (for nested categories)        |
| `1/1/25 - 1/31/25`  | Monthly expense amounts (one column per month) |
| `report_start_date` | Report start date                              |
| `report_end_date`   | Report end date                                |

Example output:

```text
category                  1/1/25 - 1/31/25  2/1/25 - 2/28/25  ...
Groceries                 -1293.53          -1282.94          ...
Dental Ins                -135.66           -135.66           ...
```

## Project Structure

```text
Quicken Data Processing/
├── src/
│   └── quicken_parser/
│       ├── __init__.py          # Package exports
│       ├── main.py              # CLI and orchestration
│       ├── csv_parser.py        # CSV parsing
│       ├── config.py            # Configuration management
│       ├── charts.py            # Chart generation
│       └── processors/
│           └── grouper.py       # Category grouping
├── data/                        # Input data files (.gitignored)
├── reports/                     # Output files (.gitignored)
│   └── charts/                  # Generated chart images
├── tests/                       # Test files
├── reports_config.yaml          # Report configuration
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Development

### Running Tests

```bash
# Run tests
uv run python test_csv_parser.py
uv run python test_charts.py
uv run python test_e2e.py
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

- **CSV Parser**: Requires properly formatted Quicken CSV export (supports "Income and Expense" or "Cash Flow" formats)
- **Section Detection**: Parser stops at "Other" section; lines after this are dropped
- No web-based UI (command-line only)

## Roadmap

- [x] CSV expense parser with hierarchical categories
- [x] Data consolidation and filtering
- [x] Configuration system for category filtering (YAML-based)
- [x] Visualization charts (monthly trends, expanding averages)
- [x] Table generation (timestamped CSV exports)
- [x] CLI tool (`quicken-report`)
- [ ] Excel and HTML table output formats
- [ ] Web-based front-end
- [ ] Scheduled/automated report generation

## License

MIT

## Author

Karl T. Braun
