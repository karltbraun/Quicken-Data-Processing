import os

import pandas as pd

from quicken_parser.config import ReportConfig
from quicken_parser.main import generate_tables


def test_default_combined_workbook(tmp_path):
    """With table_format=xlsx and no flag, default is a single workbook."""
    cfg = ReportConfig("reports_config.yaml")
    out = cfg.get_output_settings()
    # config file now defaults table_format to "xlsx" and combined_tables=True

    reports = {
        "foo": pd.DataFrame({"category": ["a"], "2025-01": [100]}),
        "bar": pd.DataFrame({"category": ["b"], "2025-01": [200]}),
    }
    ts = "20260101_000000"
    out_dir = str(tmp_path)

    count = generate_tables(reports, cfg, out_dir, ts)
    assert count == 1

    wb_path = os.path.join(out_dir, f"all_reports_{ts}.xlsx")
    assert os.path.exists(wb_path)

    xls = pd.ExcelFile(wb_path)
    assert set(xls.sheet_names) == {"foo", "bar"}

    df_foo = pd.read_excel(xls, sheet_name="foo")
    assert df_foo.loc[0, "category"] == "a"
    df_bar = pd.read_excel(xls, sheet_name="bar")
    assert df_bar.loc[0, "category"] == "b"


def test_disable_combined(tmp_path):
    """Explicitly setting combined_tables False yields separate files."""
    cfg = ReportConfig("reports_config.yaml")
    out = cfg.get_output_settings()
    out.table_format = "xlsx"
    out.combined_tables = False

    reports = {
        "foo": pd.DataFrame({"category": ["a"], "2025-01": [100]}),
        "bar": pd.DataFrame({"category": ["b"], "2025-01": [200]}),
    }
    ts = "20260101_000001"
    out_dir = str(tmp_path)

    count = generate_tables(reports, cfg, out_dir, ts)
    assert count == 2

    assert os.path.exists(os.path.join(out_dir, f"foo_{ts}.xlsx"))
    assert os.path.exists(os.path.join(out_dir, f"bar_{ts}.xlsx"))
