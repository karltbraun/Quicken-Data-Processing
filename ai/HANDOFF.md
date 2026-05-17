# Handoff

## Session: 2026-05-17T00:00:00-07:00

### Project
- Root: /Users/karl/Development/KTB/Quicken Data Processing
- Branch: project/parser-inflows-init
- Last commit: 4b688e5 chore: add CLAUDE.md and update handoff

### What was worked on
Two things this session:
1. **Branch initialization** — read `aaHandoff.md` and `aaBranchProject.md`, confirmed we are on the correct branch, rebuilt a broken venv (stale shebang from old path `Ackbook2/...`), ran all tests (24/24 pass).
2. **Context document overhaul** — replaced stub/temp docs with properly tracked equivalents:
   - `TODO.md` — converted from empty stub to active branch checklist with acceptance criteria and remaining tasks
   - `Instructions/ai_instructions.md` — filled in all TBDs (goal, directory map, key files, expectations, conventions)
   - `CLAUDE.md` — added `budget-prep` module section (pipeline, config, income classification, guardrail) and a context-tracking footer
   - Established convention: `aa*` files = gitignored temp scratch; `TODO.md` / `CLAUDE.md` / `Instructions/ai_instructions.md` = tracked durable context

### Status
- All implementation on this branch is uncommitted (see files below)
- Tests: 24/24 passing
- The one remaining unverified acceptance criterion: end-to-end `budget-prep` run producing non-empty income totals in JSON output

### Next action
1. Run end-to-end: `uv run budget-prep --config budget_prep.yaml --input 'data/Income and Expenses 2026-01-01 - 2026-04-30.csv'`
2. Verify `reports/budget/budget_prep.json` has non-zero income monthly totals
3. Update README if income classification section needs tweaking
4. Commit in three groups per `TODO.md`

### Files and areas touched
- `src/quicken_parser/csv_parser.py` — `include_inflows` flag added to `QuickenCSVParser` and `parse_quicken_csv`
- `src/quicken_parser/budget.py` — new: `budget-prep` CLI and transformation logic
- `budget_prep.yaml` — new: example budget-prep config
- `pyproject.toml` — registered `budget-prep` console script
- `tests/test_csv_parser_inflows.py` — new: parser inflows opt-in tests
- `tests/test_budget.py` — new: budget-prep pipeline tests
- `README.md` — added budget-prep CLI usage docs
- `CLAUDE.md` — added budget-prep module section and context-tracking footer
- `Instructions/ai_instructions.md` — filled in all TBDs
- `TODO.md` — converted from stub to active checklist
- `.claude/settings.json` — project-level Claude Code permissions

### Verification
- `PYTHONPATH=src uv run pytest -o "addopts=" tests/test_csv_parser_inflows.py tests/test_budget.py tests/test_cli_flags.py -v` → 22/22 pass
- `PYTHONPATH=src uv run pytest -o "addopts="` → 24/24 pass
- End-to-end `budget-prep` run: **not yet run this session**

### Open questions / blockers
- None

### Flags for /resume-work
- `aa*` files (`aaHandoff.md`, `aaBranchProject.md`, `aaBudgetPlan.md`) are gitignored temp scratch — do not commit them; content has been migrated to tracked docs
- Venv was rebuilt with `uv venv --seed --clear` — if venv issues recur, this is the fix
