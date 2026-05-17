# TODO

## Active Branch: project/parser-inflows-init

**Objective:** Add opt-in inflow/income parsing for `budget-prep` without breaking the existing `quicken-report` expense-only pipeline.

### Acceptance Criteria

- [x] `parse_quicken_csv()` default excludes inflows (backward compatible)
- [x] `parse_quicken_csv(include_inflows=True)` includes inflow rows
- [x] `quicken-report` behavior unchanged — all regression tests pass (24/24)
- [x] `budget-prep` generates JSON with non-empty income totals from raw CSV input (verify end-to-end)

### Remaining Tasks

None — branch complete.

### Completed This Branch

- [x] `QuickenCSVParser.__init__` accepts `include_inflows: bool = False`
- [x] `parse_quicken_csv()` passes flag through to parser
- [x] `load_budget_dataframe()` calls `parse_quicken_csv(include_inflows=True)` for raw CSV input
- [x] `test_csv_parser_inflows.py` — two tests covering default-exclude and opt-in-include behavior
- [x] Venv rebuilt after stale path issue (2026-05-17)
- [x] End-to-end `budget-prep` run verified — non-empty income totals in JSON (2026-05-17)
- [x] All implementation committed (`1a095e5`), settings permissions updated (`2910f89`)

---

## Backlog

- [ ] Integration test with a real CSV export to exercise `quicken-report` CLI flags end-to-end
- [ ] Budget-prep downstream: Claude-side income classification + budget recommendation generation (architecture captured in CLAUDE.md)
