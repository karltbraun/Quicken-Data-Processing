"""
Tests for the three new quicken-report CLI flags:
  --output DIR
  --add-group SPEC
  --date-range YYYY-MM:YYYY-MM
"""

import pytest
import pandas as pd

from quicken_parser.config import ReportGroup
from quicken_parser.main import filter_date_range, parse_add_group


# ---------------------------------------------------------------------------
# parse_add_group
# ---------------------------------------------------------------------------


class TestParseAddGroup:
    def test_basic(self):
        rg = parse_add_group("name=Travel,categories=Airfare;Hotel")
        assert rg.name == "Travel"
        assert rg.categories == ["Airfare", "Hotel"]
        assert rg.output_name == "travel"

    def test_output_name_slugified(self):
        rg = parse_add_group("name=KTBCS Q2 Review,categories=Client Payment;Domains")
        assert rg.output_name == "ktbcs_q2_review"

    def test_categories_trimmed(self):
        rg = parse_add_group("name=Foo,categories= Cat A ; Cat B ")
        assert rg.categories == ["Cat A", "Cat B"]

    def test_name_with_commas_in_value(self):
        # A category value that contains a comma is kept intact because
        # parse_add_group rejoins tokens that have no '=' sign.
        rg = parse_add_group("name=Misc,categories=Cat A;Cat B")
        assert rg.name == "Misc"

    def test_missing_name_raises(self):
        with pytest.raises(ValueError, match="missing 'name'"):
            parse_add_group("categories=Foo;Bar")

    def test_missing_categories_raises(self):
        with pytest.raises(ValueError, match="missing 'categories'"):
            parse_add_group("name=MyGroup")

    def test_empty_categories_raises(self):
        with pytest.raises(ValueError, match="empty"):
            parse_add_group("name=MyGroup,categories=")

    def test_returns_report_group(self):
        rg = parse_add_group("name=Test,categories=A;B")
        assert isinstance(rg, ReportGroup)
        assert rg.include_group_total is True


# ---------------------------------------------------------------------------
# filter_date_range
# ---------------------------------------------------------------------------


def _make_df(*month_labels):
    """Build a minimal expense DataFrame with given month-range column labels."""
    data = {"category": ["Groceries"], "indent_level": [0]}
    for label in month_labels:
        data[label] = [100.0]
    return pd.DataFrame(data)


class TestFilterDateRange:
    JAN = "1/1/25 - 1/31/25"
    FEB = "2/1/25 - 2/28/25"
    MAR = "3/1/25 - 3/31/25"
    APR = "4/1/25 - 4/30/25"

    def test_keeps_months_in_range(self):
        df = _make_df(self.JAN, self.FEB, self.MAR, self.APR)
        result = filter_date_range(df, "2025-02:2025-03")
        assert self.FEB in result.columns
        assert self.MAR in result.columns
        assert self.JAN not in result.columns
        assert self.APR not in result.columns

    def test_keeps_meta_columns(self):
        df = _make_df(self.JAN, self.FEB)
        result = filter_date_range(df, "2025-02:2025-02")
        assert "category" in result.columns
        assert "indent_level" in result.columns

    def test_inclusive_boundaries(self):
        df = _make_df(self.JAN, self.FEB, self.MAR)
        result = filter_date_range(df, "2025-01:2025-03")
        assert list(result.columns) == ["category", "indent_level", self.JAN, self.FEB, self.MAR]

    def test_single_month(self):
        df = _make_df(self.JAN, self.FEB, self.MAR)
        result = filter_date_range(df, "2025-02:2025-02")
        month_cols = [c for c in result.columns if c not in ("category", "indent_level")]
        assert month_cols == [self.FEB]

    def test_invalid_format_raises(self):
        df = _make_df(self.JAN)
        with pytest.raises(ValueError, match="Invalid --date-range"):
            filter_date_range(df, "bad-format")

    def test_start_after_end_raises(self):
        df = _make_df(self.JAN)
        with pytest.raises(ValueError, match="after end"):
            filter_date_range(df, "2025-06:2025-01")

    def test_no_matching_months_returns_meta_only(self):
        df = _make_df(self.JAN, self.FEB)
        result = filter_date_range(df, "2024-01:2024-12")
        assert list(result.columns) == ["category", "indent_level"]
