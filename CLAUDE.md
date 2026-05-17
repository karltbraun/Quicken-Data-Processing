# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (editable mode with dev extras)
uv pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_cli_flags.py

# Run a single test by name
pytest tests/test_cli_flags.py::test_parse_add_group_valid

# Lint
ruff src/ tests/

# Format
ruff format src/ tests/

# Run the CLI
quicken-report --config reports_config.yaml --input data/expenses.csv
```

`pytest` is configured in `pyproject.toml` to always run with `--cov=src --cov-report=html --cov-report=term-missing`.

## Architecture

The pipeline is linear: CSV → parse → group → generate outputs.

```
quicken-report (CLI in main.py)
    ↓
csv_parser.py        — QuickenCSVParser reads a Quicken CSV export into a DataFrame
                        Rows: one per leaf expense category
                        Columns: category, indent_level, then one column per month ("1/1/25 - 1/31/25"), total, monthly_average
    ↓
processors/grouper.py — create_report_groups() takes that DataFrame + config
                         and returns dict[output_name → report_df]
                         Each report_df has the requested categories as rows + optional "Group Total" row
    ↓
main.py              — generate_charts() and generate_tables() write outputs
```

**config.py** loads `reports_config.yaml` into typed dataclasses: `ReportGroup`, `IndividualReport`, `DisplaySettings`, `OutputSettings`, `ErrorHandling`. `ReportConfig` is the single object passed through the pipeline.

**Two report types** defined in YAML:
- `report_groups` — multiple categories combined into one report with a "Group Total" row
- `individual_reports` — single category, no total row

**Missing category handling** is controlled by `error_handling.missing_categories` in the YAML: `fill_zero` (default), `skip`, or `error`.

**Output** defaults to a single combined Excel workbook (`reports/tables/all_reports_<timestamp>.xlsx`) with one sheet per report group, plus PNG charts in `reports/charts/`. Both locations are relative to `output_settings.base_dir` (default `./reports`).

## Key CLI flags

| Flag | Purpose |
|---|---|
| `--output DIR` | Override `base_dir` from YAML |
| `--add-group SPEC` | Ad-hoc group: `"name=My Group,categories=Cat A;Cat B"` |
| `--date-range YYYY-MM:YYYY-MM` | Filter month columns before grouping |
| `--table-format csv\|xlsx\|html` | Override format from YAML |
| `--charts-only` / `--tables-only` | Suppress one output type |
| `--separate-tables` | One file per report instead of combined workbook |

## Data files

`data/` holds Quicken CSV exports (git-ignored except `.gitkeep`). The parser auto-detects raw Quicken exports vs. pre-parsed CSVs by filename heuristic (`parsed_expenses`, `Expense_Report`, `_parsed.csv` in the name → load directly with `pd.read_csv`).

Quicken CSV quirks handled by the parser:
- Non-standard header (title + date range in first two lines before the `Category` header row)
- Income/Inflows section is skipped by default; parsing stops at the `Other` top-level category
- Hierarchical categories encoded as leading ` - ` sequences; `indent_level` counts the dashes
- Currency strings like `-1,234.56` converted to float

## budget-prep module

`budget-prep` is a separate CLI (`budget.py`) that produces structured JSON for downstream budgeting workflows.

**Pipeline:** CSV → parse (with inflows) → select window → classify → JSON

```text
budget-prep (CLI in budget.py)
    ↓
load_budget_dataframe()             — raw Quicken export: parse_quicken_csv(include_inflows=True)
                                       pre-parsed CSV (Expense_Report / parsed_expenses suffix): pd.read_csv
    ↓
select_last_complete_month_columns() — N most recent complete months (default 3)
                                        "complete" = earlier than current calendar month
    ↓
build_budget_payload()              — rows matched against income_keywords → income or expense
                                       income split into recurring vs irregular by CV threshold
    ↓
write_budget_payload()              — writes JSON to output_file
```

**Config:** `budget_prep.yaml`. Key settings: `input_csv`, `output_file`, `months` (default 3), `recurring_cv_threshold` (default 0.35), `income_keywords` (list of substring keywords).

**Income classification:** category name matched against `income_keywords` (case-insensitive substring). Recurring = nonzero in ≥ `recurring_min_months` AND CV ≤ `recurring_cv_threshold`.

**Guardrail:** `include_inflows=True` is only set inside `load_budget_dataframe()` in the raw CSV path. The `quicken-report` pipeline never touches this flag — expense-only behavior is preserved.

## Context and task tracking

- **`TODO.md`** — active task checklist; update as work progresses
- **`CLAUDE.md`** (this file) — architecture reference and AI guidance
- **`Instructions/ai_instructions.md`** — project goals, directory map, conventions
- Temporary scratch files (handoffs, branch plans) use the `aa` prefix and are gitignored
