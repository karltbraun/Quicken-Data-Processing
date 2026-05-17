from datetime import date

import pandas as pd
import pytest

from quicken_parser.budget import (
    build_budget_payload,
    create_budget_parser,
    load_budget_config,
    merge_runtime_settings,
    select_last_complete_month_columns,
)


class TestBudgetCLIConfig:
    def test_parser_accepts_output_file_short_and_long(self):
        parser = create_budget_parser()

        args_short = parser.parse_args(["--input", "data.csv", "-o", "out.json"])
        assert args_short.input_csv == "data.csv"
        assert args_short.output_file == "out.json"

        args_long = parser.parse_args(["--input", "data.csv", "--output-file", "out.json"])
        assert args_long.output_file == "out.json"

    def test_merge_runtime_settings_cli_overrides_config(self, tmp_path):
        cfg_path = tmp_path / "budget.yaml"
        cfg_path.write_text(
            """
budget_prep:
  input_csv: from_config.csv
  output_file: from_config.json
  months: 6
  recurring_min_months: 2
  recurring_cv_threshold: 0.5
""".strip()
            + "\n",
            encoding="utf-8",
        )

        config = load_budget_config(str(cfg_path))
        parser = create_budget_parser()
        args = parser.parse_args(["--input", "from_cli.csv", "-o", "from_cli.json", "--months", "3"])

        settings = merge_runtime_settings(args, config)

        assert settings.input_csv == "from_cli.csv"
        assert settings.output_file == "from_cli.json"
        assert settings.window_months == 3
        assert settings.recurring_min_months == 2
        assert settings.recurring_cv_threshold == 0.5

    def test_merge_runtime_settings_requires_input_and_output(self):
        parser = create_budget_parser()
        args = parser.parse_args([])

        with pytest.raises(ValueError, match="Missing input CSV"):
            merge_runtime_settings(args, {})


class TestBudgetTransforms:
    def _sample_df(self):
        return pd.DataFrame(
            {
                "category": ["Salary", "Bonus", "Groceries", "Utilities"],
                "indent_level": [0, 0, 0, 0],
                "2/1/26 - 2/28/26": [5000, 0, 1200, 300],
                "3/1/26 - 3/31/26": [5000, 1500, 1100, 320],
                "4/1/26 - 4/30/26": [5000, 0, 1300, 310],
                "5/1/26 - 5/31/26": [5000, 0, 900, 290],
            }
        )

    def test_select_last_complete_month_columns_excludes_current_month(self):
        df = self._sample_df()
        month_cols = select_last_complete_month_columns(
            df,
            window_months=3,
            today=date(2026, 5, 17),
        )

        assert month_cols == [
            "2/1/26 - 2/28/26",
            "3/1/26 - 3/31/26",
            "4/1/26 - 4/30/26",
        ]

    def test_build_budget_payload_classifies_income(self):
        df = self._sample_df()
        month_cols = [
            "2/1/26 - 2/28/26",
            "3/1/26 - 3/31/26",
            "4/1/26 - 4/30/26",
        ]

        payload = build_budget_payload(
            df=df,
            source_input="sample.csv",
            month_cols=month_cols,
            recurring_min_months=3,
            recurring_cv_threshold=0.35,
            income_keywords=["salary", "bonus"],
        )

        recurring_income_categories = [entry["category"] for entry in payload["income"]["recurring"]]
        irregular_income_categories = [entry["category"] for entry in payload["income"]["irregular"]]
        expense_categories = [entry["category"] for entry in payload["expenses"]["categories"]]

        assert recurring_income_categories == ["Salary"]
        assert irregular_income_categories == ["Bonus"]
        assert set(expense_categories) == {"Groceries", "Utilities"}

        assert payload["window_months"] == 3
        assert payload["selected_months"] == month_cols
        assert payload["net"]["three_month_average"] == pytest.approx(3990.0, rel=1e-3)
