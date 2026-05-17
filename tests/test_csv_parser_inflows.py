import pandas as pd

from quicken_parser.csv_parser import parse_quicken_csv


def _has_income_row(df: pd.DataFrame) -> bool:
    # Use a known income category from the fixture file for a deterministic check.
    return (df["category"] == "Estimated Gross Pay").any()


def test_parse_quicken_csv_default_excludes_inflows():
    df = parse_quicken_csv("data/Income and Expenses 2026-01-01 - 2026-04-30.csv")
    assert not _has_income_row(df)


def test_parse_quicken_csv_include_inflows_true_includes_income_rows():
    df = parse_quicken_csv(
        "data/Income and Expenses 2026-01-01 - 2026-04-30.csv",
        include_inflows=True,
    )
    assert _has_income_row(df)
