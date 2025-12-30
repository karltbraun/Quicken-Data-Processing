# Quicken Expense Reporting - Requirements Document

## Overview

A production-quality expense reporting system that parses Quicken CSV exports and generates configurable charts and tabular reports.

## Architecture

### Module Structure

``` text
quicken_parser/
├── __init__.py
├── config.py              # Configuration management
├── parsers/
│   ├── __init__.py
│   └── csv_parser.py      # Raw CSV parsing
├── processors/
│   ├── __init__.py
│   └── grouper.py         # Category grouping and aggregation
├── reporting/
│   ├── __init__.py
│   ├── charts.py          # Visualization generation
│   └── tables.py          # Tabular/text reports
└── main.py                # Orchestration and CLI
```

### Data Flow

``` text
1. Raw Quicken CSV
   ↓
2. csv_parser.py → DataFrame (all categories, monthly values)
   ↓
3. grouper.py (uses config) → Grouped DataFrame (with totals, ready for reporting)
   ↓
4. charts.py / tables.py → Generated reports
```

## Configuration Schema

### Structure

Configuration defines:

- **Report Groups**: Logical groupings of expense categories
- **Individual Reports**: Single-category reports
- **Display Settings**: Colors, labels, chart parameters
- **Output Settings**: File paths, formats

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
      - "#1f77b4"  # Blue
      - "#2ca02c"  # Green
      - "#d62728"  # Red
      - "#9467bd"  # Purple
      - "#8c564b"  # Brown
      - "#ff7f0e"  # Orange
      - "#7f7f7f"  # Gray
      - "#e377c2"  # Pink
      - "#bcbd22"  # Olive
      - "#17becf"  # Teal
    group_total_color: "#000000"  # Black
  
  chart_defaults:
    figsize: [14, 8]
    show_markers: true
    line_width: 2
    average_line_style: "dashed"
    average_type: "expanding"  # "expanding" = cumulative from month 1; "rolling" = fixed window
    # rolling_window: 3  # Only used when average_type is "rolling"

output_settings:
  base_dir: "./reports"
  chart_format: "png"
  table_format: "csv"  # or "xlsx", "html"
  create_summary: true

error_handling:
  missing_categories: "fill_zero"  # or "skip", "error"
  partial_groups: "include"  # or "skip", "error"
```

## Module Specifications

### 1. Config Module (`config.py`)

**Responsibilities:**

- Load configuration from YAML/JSON file or Python dict
- Validate configuration schema
- Provide easy access to config sections

**Key Functions:**

``` python
class ReportConfig:
    def __init__(self, config_path: str):
        ...
    def get_report_groups(self) -> List[ReportGroup]:
        ...
    def get_individual_reports(self) -> List[IndividualReport]:
        ...
    def get_display_settings(self) -> DisplaySettings:
        ...
    def validate(self) -> bool:
        ...
```

### 2. CSV Parser (`parsers/csv_parser.py`)

**Responsibilities:**

- Parse raw Quicken CSV export
- Extract categories, indent levels, monthly values
- Calculate totals and monthly averages
- Return clean DataFrame with ALL categories

**Input:** Raw Quicken CSV file path

**Output:** DataFrame with columns:

- `category`: str
- `indent_level`: int
- `{month_1}`: float
- `{month_2}`: float
- ...
- `total`: float
- `monthly_average`: float

**Key Functions:**

```python
def parse_quicken_csv(file_path: str) -> pd.DataFrame:
    """Parse raw Quicken CSV into standardized DataFrame."""
    pass
```

### 3. Category Grouper (`processors/grouper.py`)

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
    pass

def add_group_total(df: pd.DataFrame, month_columns: List[str]) -> pd.DataFrame:
    """Add a 'Group Total' row summing all categories."""
    pass

def get_or_fill_category(
    df: pd.DataFrame, 
    category: str, 
    month_columns: List[str]
) -> pd.Series:
    """Get category data or return zeros if missing."""
    pass
```

### 4. Charts Module (`reporting/charts.py`)

**Responsibilities:**

- Generate line charts from grouped DataFrames
- Apply display settings from config
- Use expanding cumulative averages
- Handle colors (including black for Group Total)

**Input:**

- DataFrame from grouper (single report)
- Display settings from config

**Output:**

- Saved chart file
- Figure object for display

**Key Functions:**

```python
def create_line_chart(
    df: pd.DataFrame,
    title: str,
    display_settings: DisplaySettings,
    save_path: str
) -> plt.Figure:
    """Create line chart with solid lines + expanding avg dashed lines."""
    pass
```

### 5. Tables Module (`reporting/tables.py`)

**Responsibilities:**

- Generate tabular reports (CSV, Excel, HTML)
- Create summary tables
- Format currency values

**Key Functions:**

```python
def create_summary_table(
    grouped_data: Dict[str, pd.DataFrame],
    save_path: str,
    format: str = "csv"
) -> None:
    """Create summary table with totals for all groups."""
    pass

def create_detail_table(
    df: pd.DataFrame,
    save_path: str,
    format: str = "csv"
) -> None:
    """Create detailed table for a single group."""
    pass
```

### 6. Main Module (`main.py`)

**Responsibilities:**

- Orchestrate the entire pipeline
- Provide CLI interface
- Handle errors gracefully
- Generate all reports

**CLI Interface:**

```bash
# Generate all reports
quicken-report --config reports_config.yaml --input data/expenses.csv

# Generate only charts
quicken-report --config reports_config.yaml --input data/expenses.csv --charts-only

# Generate only tables
quicken-report --config reports_config.yaml --input data/expenses.csv --tables-only

# Specific reports
quicken-report --config reports_config.yaml --input data/expenses.csv --reports "groceries,utilities"
```

**Key Functions:**

```python
def main(config_path: str, input_csv: str, options: Dict) -> None:
    """
    Main orchestration function:
    1. Load config
    2. Parse CSV
    3. Create report groups
    4. Generate charts
    5. Generate tables
    6. Print summary
    """
    pass
```

## Implementation Notes

### Benefits of This Architecture

1. **Configuration-Driven**: Change report groups without code changes
2. **Separation of Concerns**: Each module has clear responsibility
3. **Testable**: Each module can be tested independently
4. **Reusable**: Grouped data can be used for charts, tables, or future reports
5. **Maintainable**: Easy to add new report types or change groupings

### Migration Path from Current Code

1. **Phase 1**: Create config structure and config.py module
2. **Phase 2**: Extract csv_parser.py (mostly done)
3. **Phase 3**: Create grouper.py (logic from test_charts.py)
4. **Phase 4**: Refactor charts.py (mostly done)
5. **Phase 5**: Create tables.py (new)
6. **Phase 6**: Create main.py orchestration
7. **Phase 7**: Add CLI interface

### Error Handling Strategy

- **Missing categories**: Fill with $0 (configurable)
- **Partial groups**: Include available categories (configurable)
- **Invalid config**: Fail fast with clear error message
- **Parse errors**: Provide detailed error with line numbers

### Testing Strategy

``` text
tests/
├── test_config.py          # Config loading and validation
├── test_csv_parser.py      # CSV parsing
├── test_grouper.py         # Category grouping logic
├── test_charts.py          # Chart generation
├── test_tables.py          # Table generation
├── test_integration.py     # End-to-end tests
└── fixtures/
    ├── test_config.yaml
    └── test_expenses.csv
```

## Current vs. Proposed

### Current (Prototype)

``` text
test_csv_parser.py → reports/parsed.csv
test_charts.py (hardcoded groups) → charts/*.png
```

### Proposed (Production)

``` text
config.yaml (defines groups)
↓
main.py orchestrates:
  ├─ csv_parser → raw DataFrame
  ├─ grouper (uses config) → grouped DataFrames
  ├─ charts (uses config) → charts/*.png
  └─ tables (uses config) → tables/*.csv
```

## Next Steps

1. Review and approve this architecture
2. Create detailed config schema (YAML vs Python dict?)
3. Start with config.py and example config file
4. Migrate existing csv_parser.py into new structure
5. Create grouper.py with logic from test_charts.py
6. Iteratively implement remaining modules

Would you like me to proceed with implementing any specific module first?
