import pandas as pd

from quicken_parser.csv_parser import parse_quicken_csv

_CSV = "data/Income and Expenses 2026-01-01 - 2026-04-30.csv"


def _has_income_row(df: pd.DataFrame) -> bool:
    # Use a known income category from the fixture file for a deterministic check.
    return (df["category"] == "Estimated Gross Pay").any()


def test_parse_quicken_csv_default_excludes_inflows():
    df = parse_quicken_csv(_CSV)
    assert not _has_income_row(df)
    assert "section" not in df.columns


def test_parse_quicken_csv_include_inflows_true_includes_income_rows():
    df = parse_quicken_csv(_CSV, include_inflows=True)
    assert _has_income_row(df)


def test_parse_quicken_csv_include_inflows_adds_section_column():
    df = parse_quicken_csv(_CSV, include_inflows=True)
    assert "section" in df.columns
    assert set(df["section"].unique()).issubset({"income", "expense"})
    # Known income row must be stamped correctly
    gross_pay = df[df["category"] == "Estimated Gross Pay"]
    assert not gross_pay.empty
    assert (gross_pay["section"] == "income").all()
    # Expense rows must also be stamped
    expense_rows = df[df["section"] == "expense"]
    assert not expense_rows.empty
