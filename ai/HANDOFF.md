# Handoff

## Session: 2026-05-17T17:00:00-07:00

### Project

- Root: /Users/karl/Development/KTB/Quicken Data Processing
- Branch: main
- Last commit: (see git log — commit made end of this session)

### What was worked on

Fixed two income-handling bugs in `budget-prep`, found when running against the real CSV (`data/Income and Expenses 2026-01-01 - 2026-04-30.csv`):

**Bug 1 — "Estimated Gross Pay" silently dropped.** `_is_income_category()` used keyword matching; any income category name that didn't match a keyword fell silently into expenses. Root fix: add a `section` column (`'income'`/`'expense'`) in the parser based on which CSV section a row came from, and use that in `budget.py` instead of keywords.

**Bug 2 — No structural income/expense marker.** `include_inflows=True` returned a flat mixed DataFrame with no way to reliably distinguish income from expense rows. Fixed by stamping `section` onto each record in `_parse_data_rows` when `include_inflows=True`. Expense-only parsing is unchanged (no `section` column).

**Anomaly detection added.** Any income row with a negative monthly value is collected into `payload["anomalies"]` as `type: "negative_income"` with category name and offending month(s). Targets the known case: "State Income Tax Refund" at −$6,690 in March.

### Status

- 27/27 tests passing.
- 5 files committed this session (see files touched below).
- `budget-prep` ready to re-run against real CSV; not re-run yet this session.

### Next action

1. Re-run `budget-prep` against `data/Income and Expenses 2026-01-01 - 2026-04-30.csv` and confirm:
   - "Estimated Gross Pay" appears in `income.recurring` or `income.irregular`
   - "State Income Tax Refund" appears in `anomalies`
2. Budget-prep downstream: Claude-side income classification + budget recommendation generation.
3. Integration test for `quicken-report` CLI flags end-to-end.

### Files and areas touched

- `src/quicken_parser/csv_parser.py` — stamp `section` on records when `include_inflows=True`
- `src/quicken_parser/budget.py` — remove `_DEFAULT_INCOME_KEYWORDS`, `_is_income_category`, all `income_keywords` plumbing; section-based split; anomaly detection in payload
- `budget_prep.yaml` — removed `income_keywords` block
- `tests/test_budget.py` — added `section` column to fixture; dropped `income_keywords` arg; 3 new tests
- `tests/test_csv_parser_inflows.py` — added section-column presence/value test
- `ai/HANDOFF.md` — this file

### Verification

- 27/27 tests passing (2026-05-17)
- End-to-end re-run with real CSV: not done this session — do first after resuming

### Open questions / blockers

None

### Flags for /resume-work

- `aa*` files are gitignored scratch — do not commit them
