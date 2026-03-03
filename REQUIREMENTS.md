# Quicken Expense Reporting - Requirements and Architecture

## Overview

A configuration-driven expense reporting system that parses Quicken CSV exports and generates customizable charts and tabular reports. All core features are implemented and tested.

**Status**: Version 1.0 - Production ready

## Code Style Requirements

**Formatting**: This project uses **Ruff** as the code formatter.

### Python Code Style Rules

- **No whitespace on blank lines**: Blank lines must contain only the newline character (`\n`), with no spaces or tabs
- **Consistent indentation**: 4 spaces for Python code
- **Line length**: Maximum 88 characters (Black/Ruff default)
- **Imports**: Organized and sorted per Ruff standards

### Markdown Style Rules

- **Blank line after headers**: All section headers (# ## ### etc.) must be followed by a blank line before content
- **Blank line before lists**: List headers (text immediately before a list) must be followed by a blank line before the first list item
- **Consistent formatting**: Follow standard markdown conventions for readability

### Running Formatter

```bash
# Format all Python files
ruff format .

# Check formatting without changes
ruff format --check .
```

**Note for AI assistants**: Always ensure blank lines contain no whitespace. Run `ruff format` after editing to maintain consistency.

## Architecture

### Module Structure

```text
quicken_parser/
├── __init__.py            # Package exports
├── config.py              # Configuration management (YAML)
├── csv_parser.py          # Raw CSV parsing with section detection
├── processors/
│   ├── __init__.py
│   └── grouper.py         # Category grouping and aggregation
├── charts.py              # Chart generation with matplotlib
└── main.py                # CLI orchestration (quicken-report)
```

### Data Flow

```text
1. Raw Quicken CSV (Income/Expense or Cash Flow format)
   ↓
2. csv_parser.py → DataFrame (all categories, monthly values)
   ↓
3. grouper.py (uses config) → Grouped DataFrames (with Group Total rows)
   ↓
4. charts.py → PNG line charts with expanding averages
   tables.py → Timestamped CSV files (YYYYMMDD_HHMMSS.csv)
```

## Configuration Schema

### Structure

Configuration (YAML) defines:

- **Report Groups**: Logical groupings of expense categories
- **Individual Reports**: Single-category reports
- **Display Settings**: Colors (15-color palette), labels, chart parameters
- **Error Handling**: Modes for missing categories (fill_zero, skip, error)

### Example Config Format (YAML or Python)

```yaml
report_groups:
  - name: "Cell Phones (Family)"
    output_name: "cell_phones_family"
    categories:
      - "Cell Phone Monthly - FAM"
      - "Other Cell Phone Exp - FAM"
      - "Reimb Cell Phones - FAM"
    include_group_total: true

  - name: "Medicare Expenses - KTB"
    output_name: "medicare_ktb"
    categories:
      - "IRMAA Part B - KTB"
      - "Regular Part B - KTB"
      - "IRMAA Part D - KTB"
      - "Regular Part D - KTB"
      - "Supplemental Part G - KTB"
    include_group_total: true

  - name: "Utilities"
    output_name: "utilities"
    categories:
      - "GasElecOnly"
      - "WaterOnly"
    include_group_total: true

individual_reports:
  - name: "Groceries"
    output_name: "groceries"
    category: "Groceries"
  - name: "Internet - Family"
    output_name: "internet_family"
    category: "Internet - FAM"

display_settings:
  colors:
    palette:
      - "#1f77b4" # [web:0] Blue
      - "#ff7f0e" # [web:1] Orange
      - "#2ca02c" # [web:2] Green
      - "#d62728" # [web:3] Red
      - "#9467bd" # [web:4] Purple
      - "#8c564b" # [web:5] Brown
      - "#e377c2" # [web:6] Pink
      - "#7f7f7f" # [web:7] Gray
      - "#bcbd22" # [web:8] Olive
      - "#17becf" # [web:9] Cyan
      - "#aec7e8" # [web:10] Light Blue
      - "#ffbb78" # [web:11] Light Orange
      - "#98df8a" # [web:12] Light Green
      - "#ff9896" # [web:13] Light Red
      - "#c5b0d5" # [web:14] Light Purple
    group_total_color: "#000000" # Black

  chart_defaults:
    figsize: [14, 8]
    show_markers: true
    line_width: 2
    average_line_style: "dashed"
    average_type: "expanding" # "expanding" = cumulative from month 1; "rolling" = fixed window
    # rolling_window: 3  # Only used when average_type is "rolling"

output_settings:
  base_dir: "./reports"
  chart_format: "png"
  table_format: "csv" # or "xlsx", "html"
  # combined_tables defaults to true when format is xlsx; set to false to get
  # separate files instead
  create_summary: true

error_handling:
  missing_categories: "fill_zero" # or "skip", "error"
  partial_groups: "include" # or "skip", "error"
```

## Module Specifications

### 1. Config Module (`config.py`)

**Status**: ✅ Implemented

**Responsibilities:**

- Load configuration from YAML file
- Validate configuration schema with dataclasses
- Provide easy access to config sections
- Support report groups, individual reports, display settings, and error handling

**Implementation:**

```python
@dataclass
class ReportGroup:
    output_name: str
    title: str
    categories: List[str]

@dataclass
class DisplaySettings:
    colors: List[str]
    group_total_color: str

@dataclass
class ReportConfig:
    report_groups: List[ReportGroup]
    individual_reports: List[IndividualReport]
    display_settings: DisplaySettings
    error_handling: ErrorHandling

    @classmethod
    def from_yaml(cls, path: str) -> 'ReportConfig':
        """Load and validate config from YAML file."""
        ...
```

### 2. CSV Parser (`csv_parser.py`)

**Status**: ✅ Implemented

**Responsibilities:**

- Parse non-standard Quicken CSV exports
- Handle both "Income and Expense" and "Cash Flow" report formats
- Detect sections (Income/Expenses or Inflows/Outflows) with exact matching
- Stop parsing at "Other" section
- Extract categories, indent levels, monthly values
- Return clean DataFrame with ALL categories

**Input:** Raw Quicken CSV file path

**Output:** DataFrame with columns:

- `category`: str
- `indent_level`: int
- `{month_1}`: float (e.g., "1/1/25 - 1/31/25")
- `{month_2}`: float
- ...
- `report_start_date`: datetime
- `report_end_date`: datetime

**Implementation:**

```python
class QuickenCSVParser:
    def parse(self, file_path: str, verbose: bool = False) -> pd.DataFrame:
        """
        Parse Quicken CSV export.

        Section detection:
        - Looks for exact match: col == "Income" or col == "Expenses"
        - Also handles: col == "Inflows" or col == "Outflows"
        - Stops at "Other" section to avoid parsing extraneous data
        """
        ...

def parse_quicken_csv(file_path: str, verbose: bool = False) -> pd.DataFrame:
    """Convenience function for parsing Quicken CSV."""
    parser = QuickenCSVParser()
    return parser.parse(file_path, verbose)
```

### 3. Category Grouper (`processors/grouper.py`)

**Status**: ✅ Implemented

**Responsibilities:**

- Read configuration
- Group categories according to config
- Calculate group totals
- Handle missing categories (fill with $0)
- Prepare data structures optimized for reporting

**Input:**

- Parsed DataFrame from csv_parser
- ReportConfig object

**Output:** Dictionary of DataFrames, one per report:

```python
{
    "cell_phones_family": DataFrame,  # Has categories + Group Total row
    "groceries": DataFrame,            # Single category
    ...
}
```

**Key Functions:**

```python
def create_report_groups(
    df: pd.DataFrame,
    config: ReportConfig
) -> Dict[str, pd.DataFrame]:
    """
    Create grouped DataFrames for each report.

    Returns:
        Dict mapping output_name -> DataFrame ready for charting/reporting
    """
    # Implemented - groups categories and adds Group Total rows

def add_group_total(df: pd.DataFrame, month_columns: List[str]) -> pd.DataFrame:
    """
    Add a 'Group Total' row summing all categories.
    Month columns exclude metadata (report_start_date, report_end_date, page_num).
    """
    # Implemented

def get_or_fill_category(
    df: pd.DataFrame,
    category: str,
    month_columns: List[str],
    error_mode: str = "fill_zero"
) -> pd.Series:
    """
    Get category data or return zeros if missing.

    Error modes:
    - fill_zero: Return zeros for missing categories
    - skip: Return None (category skipped)
    - error: Raise ValueError
    """
    # Implemented
```

### 4. Charts Module (`charts.py`)

**Status**: ✅ Implemented

**Responsibilities:**

- Generate line charts from grouped DataFrames
- Apply display settings from config (15-color palette)
- Calculate and plot expanding cumulative averages (dashed lines)
- Use black color (#000000) for Group Total
- Save charts as PNG files

**Input:**

- DataFrame from grouper (single report)
- Display settings from config
- Output directory

**Output:**

- Saved PNG chart file in `./reports/charts/`
- Figure object for display

**Implementation:**

```python
def generate_charts(
    grouped_data: Dict[str, pd.DataFrame],
    config: ReportConfig,
    output_dir: str = "./reports/charts"
) -> None:
    """
    Generate line charts for all report groups.

    Features:
    - Solid lines for actual monthly expenses
    - Dashed lines for expanding cumulative averages
    - Configurable figsize, line width, markers
    - Color cycling from 15-color palette
    - Black for Group Total rows
    """
    # Implemented
```

### 5. Tables Module (`main.py::generate_tables`)

**Status**: ✅ Implemented

**Responsibilities:**

- Generate timestamped CSV tables for each report group
- Export monthly expense breakdowns
- Preserve category hierarchy and Group Total rows

**Key Functions:**

```python
def generate_tables(
    grouped_data: Dict[str, pd.DataFrame],
    output_dir: str = "./reports"
) -> None:
    """
    Generate timestamped CSV tables.

    Output format: {output_name}_{YYYYMMDD_HHMMSS}.csv
    Example: groceries_20250121_143022.csv

    Each table contains:
    - category column
    - Monthly expense columns
    - Group Total row (if applicable)
    """
```

### 6. Main Module (`main.py`)

**Status**: ✅ Implemented

**Responsibilities:**

- Orchestrate the entire pipeline (parse → group → chart → table)
- Provide CLI interface (`quicken-report` command)
- Handle errors gracefully
- Generate all reports

**CLI Interface:**

```bash
# Generate all reports (default behavior)
# Generate all reports (default behavior)
quicken-report --config reports_config.yaml --input data/expenses.csv
```

**Implementation:**

```python
def main(config_path: str, input_csv: str) -> None:
    """
    Main orchestration function:
    1. Load config from YAML
    2. Parse CSV using csv_parser
    3. Create report groups using grouper
    4. Generate charts using charts module
    5. Generate timestamped tables
    6. Print summary
    """
    # Implemented

def cli() -> None:
    """Command-line interface entry point (quicken-report command)."""
    # Implemented with argparse
```

## Implementation Status

### ✅ Completed Modules

1. **config.py**: YAML configuration with dataclass validation
2. **csv_parser.py**: Quicken CSV parsing with section detection
3. **processors/grouper.py**: Category grouping with error handling
4. **charts.py**: Line chart generation with expanding averages
5. **main.py**: Full orchestration with CLI (`quicken-report`)
6. **Table generation**: Timestamped CSV output

### Architecture Benefits

1. **Configuration-Driven**: Change report groups without code changes
2. **Separation of Concerns**: Each module has clear responsibility
3. **Testable**: Each module can be tested independently
4. **Reusable**: Grouped data can be used for charts, tables, or future reports
5. **Maintainable**: Easy to add new report types or change groupings

### Error Handling Strategy

**Implemented error modes:**

- **Missing categories**: Fill with $0 (default), skip, or error
- **Section detection**: Exact matching prevents false positives
- **"Other" section**: Parser stops to avoid extraneous data
- **Invalid config**: Dataclass validation with clear messages 4. Generate charts 5. Generate tables 6. Print summary

### Testing Strategy

**Implemented tests:**

```text
tests/
├── test_config.py          # Config loading and validation - ✅
├── test_csv_parser.py      # CSV parsing - ✅
├── test_grouper.py         # Category grouping logic - ✅
├── test_charts.py          # Chart generation - ✅
├── test_e2e.py             # End-to-end workflow - ✅
└── fixtures/
    └── test_expenses.csv
```

## CSV Format Details

### Supported Report Types

Quicken exports two report formats:

1. **Income and Expense Report**
   - Section headers: "Income" and "Expenses"
   - Used for: Profit & Loss analysis

2. **Cash Flow Report**
   - Section headers: "Inflows" and "Outflows"
   - Used for: Cash flow tracking

### Section Detection

Parser uses **exact matching** to identify sections:

```python
# Correct: Exact match
if col == "Income" or col == "Expenses":
    current_section = col

# Wrong: Substring matching (causes false positives)
# if "Income" in col:  # Matches "012 MES Retirement Income"
```

### "Other" Section Handling

Parser stops at "Other" section:

- Lines after "Other" are dropped and reported
- Prevents parsing extraneous summary data

## Future Enhancements

**Potential additions:**

- [ ] Excel (XLSX) and HTML table formats
- [ ] Rolling average support (in addition to expanding)
- [ ] PDF export of charts
- [ ] Web-based dashboard
- [ ] Scheduled report generation
- [ ] Email report delivery

## Implementation History

**Version 0.1.0**: CSV parsing prototype
**Version 0.2.0**: Configuration system, chart generation, table generation, CLI tool
**Version 1.0**: Production release - Full feature set complete and stable
