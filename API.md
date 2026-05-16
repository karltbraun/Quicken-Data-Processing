# API Reference — Quicken Data Processing

Last Updated: 2026-05-16

## `quicken-report`

Parse a Quicken CSV export and generate Excel tables and/or charts.

```
quicken-report [OPTIONS]
```

### Required flags

| Flag | Type | Description |
|------|------|-------------|
| `-i`, `--input PATH` | string | Path to the input CSV (raw Quicken export or pre-parsed file) |

### Optional flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-c`, `--config PATH` | string | `reports_config.yaml` | Path to YAML configuration file |
| `--output DIR` | string | value from config `base_dir` | Override the base output directory |
| `--add-group SPEC` | string | — | Add an ad-hoc report group (see format below). May be repeated. |
| `--date-range YYYY-MM:YYYY-MM` | string | — | Restrict output to months within this range (inclusive) |
| `--charts-only` | flag | false | Generate only charts; skip tables |
| `--tables-only` | flag | false | Generate only tables; skip charts |
| `-r`, `--reports NAMES` | string | all | Comma-separated list of report `output_name` values to generate |
| `--summary-excel` | flag | false | Generate a consolidated Excel summary sheet and pie chart |
| `--table-format {csv,xlsx,html}` | string | value from config | Override table format |
| `--combined-tables` | flag | false | Write all xlsx reports into one workbook (one sheet per report) |
| `--separate-tables` | flag | false | Force one file per report even when format is xlsx |
| `-v`, `--verbose` | flag | false | Enable verbose progress output |

### `--add-group` format

```
"name=<display name>,categories=<Cat A>;<Cat B>;<Cat C>"
```

- Key-value pairs are separated by `,`
- Category names within `categories` are separated by `;`
- `output_name` is derived automatically by slugifying the name (lowercase, spaces → underscores)
- The group is appended to the YAML-configured groups; existing groups are unchanged

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Runtime error (file not found, invalid config, parse failure) |
| 2 | Invalid command-line arguments |

### Examples

```bash
# Standard run — all reports to the default output directory
quicken-report --config reports_config.yaml --input data/incoming/report.csv

# Override output directory (useful for AI orchestrator)
quicken-report \
  --config reports_config.yaml \
  --input data/incoming/report.csv \
  --output /path/to/PersonalFinanceManagement/reports/

# Add a one-off group at runtime
quicken-report \
  --config reports_config.yaml \
  --input data/incoming/report.csv \
  --add-group "name=KTBCS Q2 Review,categories=Client Payment;Travel - KTBCS;Domains and web services - KTBCS"

# Restrict to a date range
quicken-report \
  --config reports_config.yaml \
  --input data/incoming/report.csv \
  --date-range 2026-01:2026-04

# Combined: override output, add ad-hoc group, filter to Q1, tables only
quicken-report \
  --config reports_config.yaml \
  --input data/incoming/report.csv \
  --output /path/to/reports/ \
  --add-group "name=Q1 Review,categories=Groceries;Utilities" \
  --date-range 2026-01:2026-03 \
  --tables-only
```

---

## Breaking Changes

_(none yet)_
