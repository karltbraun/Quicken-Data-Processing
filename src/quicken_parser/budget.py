"""Budget preparation CLI and transformation utilities.

This module adds the `budget-prep` command, which prepares structured JSON
from Quicken export data for downstream budgeting workflows.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quicken_parser.csv_parser import parse_quicken_csv

_META_COLUMNS = {"category", "indent_level", "section", "total", "monthly_average"}


@dataclass
class BudgetRuntimeSettings:
    """Runtime settings after merging config file values and CLI overrides."""

    input_csv: str
    output_file: str
    window_months: int = 3
    recurring_min_months: int = 3
    recurring_cv_threshold: float = 0.35


def create_budget_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser for the budget-prep CLI."""
    parser = argparse.ArgumentParser(
        description="Prepare budgeting JSON from Quicken CSV data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  budget-prep --input data/expenses.csv --output-file reports/budget.json
  budget-prep -c budget_prep.yaml -o reports/test_budget.json
        """,
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Path to budget-prep YAML config (optional)",
    )

    parser.add_argument(
        "-i",
        "--input",
        dest="input_csv",
        help="Path to CSV expense data (parsed or raw Quicken export)",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        dest="output_file",
        metavar="FILE",
        help="Path to output JSON file",
    )

    parser.add_argument(
        "--months",
        type=int,
        help="Number of complete months to include (default: 3)",
    )

    parser.add_argument(
        "--recurring-min-months",
        type=int,
        help="Minimum non-zero months to treat income as recurring",
    )

    parser.add_argument(
        "--recurring-cv-threshold",
        type=float,
        help="Max coefficient of variation for recurring income",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    return parser


def load_budget_config(config_path: str | None) -> dict[str, Any]:
    """Load budget-prep configuration from YAML.

    Accepts either top-level keys or a nested `budget_prep` section.
    """
    if not config_path:
        return {}

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    if not isinstance(raw, dict):
        raise ValueError("Budget config must be a YAML mapping")

    nested = raw.get("budget_prep")
    if isinstance(nested, dict):
        return nested

    return raw


def merge_runtime_settings(args: argparse.Namespace, config: dict[str, Any]) -> BudgetRuntimeSettings:
    """Merge CLI and config values. CLI values always win."""
    input_csv = args.input_csv or config.get("input_csv")
    output_file = args.output_file or config.get("output_file")

    if not input_csv:
        raise ValueError("Missing input CSV. Provide --input or set input_csv in config.")
    if not output_file:
        raise ValueError(
            "Missing output file. Provide -o/--output-file or set output_file in config."
        )

    window_months = args.months if args.months is not None else int(config.get("months", 3))
    recurring_min_months = (
        args.recurring_min_months
        if args.recurring_min_months is not None
        else int(config.get("recurring_min_months", 3))
    )
    recurring_cv_threshold = (
        args.recurring_cv_threshold
        if args.recurring_cv_threshold is not None
        else float(config.get("recurring_cv_threshold", 0.35))
    )

    if window_months <= 0:
        raise ValueError("months must be greater than 0")
    if recurring_min_months <= 0:
        raise ValueError("recurring_min_months must be greater than 0")
    if recurring_cv_threshold < 0:
        raise ValueError("recurring_cv_threshold must be >= 0")

    return BudgetRuntimeSettings(
        input_csv=input_csv,
        output_file=output_file,
        window_months=window_months,
        recurring_min_months=recurring_min_months,
        recurring_cv_threshold=recurring_cv_threshold,
    )


def parse_month_start(column_name: str) -> date | None:
    """Parse the first date in a month range column label."""
    if " - " not in column_name:
        return None

    start_segment = column_name.split(" - ", 1)[0].strip()
    try:
        parsed = datetime.strptime(start_segment, "%m/%d/%y")
        return date(parsed.year, parsed.month, 1)
    except ValueError:
        return None


def month_columns_in_order(df: pd.DataFrame) -> list[str]:
    """Return parseable month columns sorted in ascending date order."""
    parsed_pairs: list[tuple[str, date]] = []
    for col in df.columns:
        if col in _META_COLUMNS:
            continue
        month_start = parse_month_start(str(col))
        if month_start is not None:
            parsed_pairs.append((str(col), month_start))

    parsed_pairs.sort(key=lambda item: item[1])
    return [col for col, _ in parsed_pairs]


def select_last_complete_month_columns(
    df: pd.DataFrame,
    window_months: int = 3,
    today: date | None = None,
) -> list[str]:
    """Select the most recent complete month columns.

    Complete means earlier than the current month represented by `today`.
    """
    if today is None:
        today = date.today()

    current_month_start = date(today.year, today.month, 1)
    ordered_cols = month_columns_in_order(df)
    with_dates = [(col, parse_month_start(col)) for col in ordered_cols]

    complete_cols = [col for col, month in with_dates if month is not None and month < current_month_start]

    # If no complete months exist (e.g. test fixtures with only current month),
    # fall back to latest available columns so output is still usable.
    candidate_cols = complete_cols if complete_cols else ordered_cols

    if not candidate_cols:
        raise ValueError("No month columns were found in input data")

    return candidate_cols[-window_months:]


def load_budget_dataframe(input_csv: str, verbose: bool = False) -> pd.DataFrame:
    """Load a dataframe from either pre-parsed or raw Quicken CSV input."""
    if (
        "Expense_Report" in input_csv
        or "parsed_expenses" in input_csv
        or input_csv.endswith("_parsed.csv")
    ):
        df = pd.read_csv(input_csv)
        if verbose:
            print(f"Loaded {len(df)} rows (pre-parsed CSV)")
        return df

    df = parse_quicken_csv(
        input_csv,
        verbose=verbose,
        include_inflows=True,
    )
    if verbose:
        print(f"Parsed {len(df)} rows from raw Quicken export")
    return df


def _safe_float(value: Any) -> float:
    if pd.isna(value):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_month_value_map(row: pd.Series, month_cols: list[str]) -> dict[str, float]:
    return {col: round(_safe_float(row.get(col, 0.0)), 2) for col in month_cols}


def _classify_income_entry(
    category: str,
    month_values: dict[str, float],
    recurring_min_months: int,
    recurring_cv_threshold: float,
) -> tuple[str, dict[str, Any]]:
    values = [abs(v) for v in month_values.values()]
    nonzero_values = [v for v in values if v > 0]
    avg = round(sum(values) / len(values), 2) if values else 0.0

    if not values or not nonzero_values:
        label = "irregular"
        cv = None
    else:
        series = pd.Series(values, dtype="float")
        mean = float(series.mean())
        std = float(series.std(ddof=0))
        cv = round(std / mean, 4) if mean > 0 else None
        nonzero_months = len(nonzero_values)

        recurring = nonzero_months >= recurring_min_months and (cv is not None and cv <= recurring_cv_threshold)
        label = "recurring" if recurring else "irregular"

    payload = {
        "category": category,
        "monthly_values": month_values,
        "three_month_average": avg,
    }
    if cv is not None:
        payload["coefficient_of_variation"] = cv

    return label, payload


def build_budget_payload(
    df: pd.DataFrame,
    source_input: str,
    month_cols: list[str],
    recurring_min_months: int,
    recurring_cv_threshold: float,
) -> dict[str, Any]:
    """Build the budget JSON payload from selected month columns.

    Income vs expense is determined by the `section` column added by the parser
    when include_inflows=True. Rows without a section column are treated as expenses.
    """
    has_section = "section" in df.columns

    recurring_income: list[dict[str, Any]] = []
    irregular_income: list[dict[str, Any]] = []
    expense_categories: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        category = str(row.get("category", "")).strip()
        if not category:
            continue

        month_values = _to_month_value_map(row, month_cols)
        is_income = has_section and row.get("section") == "income"

        if is_income:
            negative_months = {col: v for col, v in month_values.items() if v < 0}
            if negative_months:
                anomalies.append(
                    {
                        "type": "negative_income",
                        "category": category,
                        "negative_months": negative_months,
                    }
                )
            label, payload = _classify_income_entry(
                category,
                month_values,
                recurring_min_months,
                recurring_cv_threshold,
            )
            if label == "recurring":
                recurring_income.append(payload)
            else:
                irregular_income.append(payload)
        else:
            normalized = {col: round(abs(v), 2) for col, v in month_values.items()}
            avg = round(sum(normalized.values()) / len(normalized), 2)
            expense_categories.append(
                {
                    "category": category,
                    "monthly_values": normalized,
                    "three_month_average": avg,
                }
            )

    income_monthly_totals: dict[str, float] = {}
    expense_monthly_totals: dict[str, float] = {}
    net_monthly_totals: dict[str, float] = {}

    for col in month_cols:
        income_total = round(
            sum(entry["monthly_values"][col] for entry in recurring_income + irregular_income), 2
        )
        expense_total = round(sum(entry["monthly_values"][col] for entry in expense_categories), 2)

        income_monthly_totals[col] = income_total
        expense_monthly_totals[col] = expense_total
        net_monthly_totals[col] = round(income_total - expense_total, 2)

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_input": source_input,
        "window_months": len(month_cols),
        "selected_months": month_cols,
        "income": {
            "recurring": recurring_income,
            "irregular": irregular_income,
            "monthly_totals": income_monthly_totals,
            "three_month_average": round(sum(income_monthly_totals.values()) / len(month_cols), 2),
        },
        "expenses": {
            "categories": expense_categories,
            "monthly_totals": expense_monthly_totals,
            "three_month_average": round(sum(expense_monthly_totals.values()) / len(month_cols), 2),
        },
        "net": {
            "monthly_totals": net_monthly_totals,
            "three_month_average": round(sum(net_monthly_totals.values()) / len(month_cols), 2),
        },
        "anomalies": anomalies,
    }

    return payload


def write_budget_payload(payload: dict[str, Any], output_file: str) -> None:
    """Write budget payload JSON to disk."""
    path = Path(output_file)
    if path.parent and str(path.parent) not in ("", "."):
        os.makedirs(path.parent, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def run_budget_prep(
    settings: BudgetRuntimeSettings,
    verbose: bool = False,
    today: date | None = None,
) -> dict[str, Any]:
    """Run budget preparation and return the generated payload."""
    df = load_budget_dataframe(settings.input_csv, verbose=verbose)
    month_cols = select_last_complete_month_columns(
        df,
        window_months=settings.window_months,
        today=today,
    )

    payload = build_budget_payload(
        df=df,
        source_input=settings.input_csv,
        month_cols=month_cols,
        recurring_min_months=settings.recurring_min_months,
        recurring_cv_threshold=settings.recurring_cv_threshold,
    )
    write_budget_payload(payload, settings.output_file)

    return payload


def budget_main(args: argparse.Namespace) -> int:
    """Execute budget-prep workflow from parsed argparse namespace."""
    config = load_budget_config(args.config)
    settings = merge_runtime_settings(args, config)

    payload = run_budget_prep(settings, verbose=args.verbose)

    print("=" * 70)
    print("BUDGET PREP COMPLETE")
    print("=" * 70)
    print(f"Input:          {settings.input_csv}")
    print(f"Months used:    {len(payload['selected_months'])}")
    print(f"Output JSON:    {settings.output_file}")
    print("=" * 70)

    return 0


def budget_cli() -> None:
    """Console script entrypoint for budget-prep."""
    parser = create_budget_parser()
    args = parser.parse_args()

    try:
        exit_code = budget_main(args)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        exit_code = 1
    except ValueError as e:
        print(f"Error: Invalid configuration or data - {e}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if getattr(args, "verbose", False):
            import traceback

            traceback.print_exc()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    budget_cli()
