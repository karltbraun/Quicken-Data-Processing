---
title: AI Instructions - Quicken Data Processing
version: 1.1
updated: 2026-05-17
---

## Goal

Automate personal financial reporting and budgeting from Quicken CSV exports. Two primary workflows:

1. **`quicken-report`** — Expense reports: grouped category summaries as Excel workbooks + PNG charts.
2. **`budget-prep`** — Budget preparation: structured JSON with income/expense breakdown and 3-month averages for downstream budgeting analysis.

## Key directories (relative to repo root)

| Path | Purpose |
|---|---|
| `src/quicken_parser/` | All source code |
| `tests/` | pytest test suite |
| `data/` | Quicken CSV exports (gitignored; place exports here) |
| `reports/` | All generated output (gitignored) |
| `config/` | Example YAML configs |
| `docs/` | Design and reference docs |
| `Instructions/` | AI and workflow guidance (this file) |

Key source files:
- `csv_parser.py` — Raw Quicken CSV parser (`QuickenCSVParser`, `parse_quicken_csv`)
- `budget.py` — `budget-prep` CLI and transformation logic
- `main.py` — `quicken-report` CLI entry point
- `config.py` — Config dataclasses loaded from YAML
- `processors/grouper.py` — Category grouping for reports

## Expectations for AI-written code and changes

- Follow existing patterns: typed dataclasses for config, argparse for CLIs, `uv` for environment.
- Default parser behavior is expense-only. `include_inflows=True` is only used in `budget-prep`'s raw CSV path — never enable it in `quicken-report`.
- Do not add new metadata columns to the parsed DataFrame without verifying that month-column detection in `grouper.py` will not be affected.
- Tests live in `tests/`; use pytest fixtures and real fixture CSV files in `data/` rather than mocks when testing parser behavior.
- Prefer `uv run` for executing scripts and tests.

## Environment and tooling

- Python 3.12, managed with `uv`. Virtual environment at `.venv/`.
- `uv pip install -e ".[dev]"` installs all dependencies including dev/test extras.
- pytest is configured in `pyproject.toml`: always runs with coverage.
- Linting/formatting: `ruff src/ tests/` and `ruff format src/ tests/`.
- Use `PYTHONPATH=src uv run pytest -o "addopts="` when running tests without the default coverage flags.

## Workflow and branch conventions

- Feature branches: `feature/<short-description>`
- Project branches (multi-step work): `project/<short-description>`
- Temporary/scratch files: prefix with `aa` (e.g. `aaHandoff.md`) — these are gitignored and never committed.
- Persistent context lives in tracked files: `TODO.md` (task list), `CLAUDE.md` (architecture + AI guidance), this file.
