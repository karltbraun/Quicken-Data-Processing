# Changelog

## [1.1.0] — 2026-05-16

### Added

- `--output DIR` — override the `base_dir` from `reports_config.yaml` at runtime
- `--add-group SPEC` — inject one or more ad-hoc `ReportGroup` objects without editing YAML.
  Format: `"name=My Group,categories=Cat A;Cat B"`. May be repeated.
- `--date-range YYYY-MM:YYYY-MM` — restrict all output to months within the specified range
  (inclusive). Month columns outside the range are dropped before grouping and output.
- `API.md` — complete CLI reference for `quicken-report`
- `tests/test_cli_flags.py` — unit tests for `parse_add_group` and `filter_date_range`

---

## [1.0.0] — 2025-xx-xx

Initial release with `quicken-report` CLI, Excel table output, chart generation,
combined-workbook mode, and summary Excel/pie chart features.
