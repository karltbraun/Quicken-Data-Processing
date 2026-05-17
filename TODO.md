# TODO

## Active Branch: project/parser-inflows-init

**Objective:** Add opt-in inflow/income parsing for `budget-prep` without breaking the existing `quicken-report` expense-only pipeline.

### Acceptance Criteria

- [x] `parse_quicken_csv()` default excludes inflows (backward compatible)
- [x] `parse_quicken_csv(include_inflows=True)` includes inflow rows
- [x] `quicken-report` behavior unchanged — all regression tests pass (24/24)
- [ ] `budget-prep` generates JSON with non-empty income totals from raw CSV input (verify end-to-end)

### Remaining Tasks

- [ ] Run end-to-end: `uv run budget-prep --config budget_prep.yaml --input 'data/Income and Expenses 2026-01-01 - 2026-04-30.csv'`
- [ ] Verify `reports/budget/budget_prep.json` has non-zero income monthly totals
- [ ] Update README: note `include_inflows` is internal/opt-in for `budget-prep`
- [ ] Commit 1 — Parser opt-in feature + parser tests (`csv_parser.py`, `test_csv_parser_inflows.py`)
- [ ] Commit 2 — `budget-prep` wiring (`budget.py`, `budget_prep.yaml`, `pyproject.toml`)
- [ ] Commit 3 — Docs (`README.md`, any other updated docs)

### Completed This Branch

- [x] `QuickenCSVParser.__init__` accepts `include_inflows: bool = False`
- [x] `parse_quicken_csv()` passes flag through to parser
- [x] `load_budget_dataframe()` calls `parse_quicken_csv(include_inflows=True)` for raw CSV input
- [x] `test_csv_parser_inflows.py` — two tests covering default-exclude and opt-in-include behavior
- [x] Venv rebuilt after stale path issue (2026-05-17)

---

## Backlog

- [ ] Integration test with a real CSV export to exercise `quicken-report` CLI flags end-to-end
- [ ] Budget-prep downstream: Claude-side income classification + budget recommendation generation (architecture captured in CLAUDE.md)
