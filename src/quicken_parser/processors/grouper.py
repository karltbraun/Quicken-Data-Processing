"""
Category grouping and aggregation module.

This module processes parsed expense data according to configuration,
creating report-ready DataFrames with proper groupings and totals.
"""

from typing import Dict, List

import pandas as pd

from ..config import (
    ErrorHandling,
    IndividualReport,
    ReportConfig,
    ReportGroup,
)


def get_or_fill_category(
    df: pd.DataFrame,
    category: str,
    month_columns: List[str],
    error_handling: ErrorHandling,
) -> pd.Series:
    """
    Get category data or return zeros if missing.

    Args:
        df: Parsed expense DataFrame
        category: Category name to retrieve
        month_columns: List of month column names
        error_handling: Error handling configuration

    Returns:
        Series with month values (real or zeros)

    Raises:
        ValueError: If category missing and error_handling is 'error'
    """
    matching = df[df["category"] == category]

    if matching.empty:
        if error_handling.missing_categories == "error":
            raise ValueError(f"Required category not found: {category}")
        elif error_handling.missing_categories == "skip":
            return None
        else:  # fill_zero
            zero_data = {col: 0.0 for col in month_columns}
            return pd.Series(zero_data)

    return matching.iloc[0][month_columns]


def add_group_total(
    df: pd.DataFrame, month_columns: List[str]
) -> pd.DataFrame:
    """
    Add a 'Group Total' row summing all categories.

    Args:
        df: DataFrame with category rows
        month_columns: List of month column names

    Returns:
        DataFrame with Group Total row appended
    """
    # Calculate totals for each month
    monthly_totals = {col: df[col].sum() for col in month_columns}

    # Create Group Total row
    group_total_row = pd.DataFrame(
        [
            {
                "category": "Group Total",
                "indent_level": 0,
                **monthly_totals,
            }
        ]
    )

    # Append to dataframe
    return pd.concat([df, group_total_row], ignore_index=True)


def create_grouped_report(
    df: pd.DataFrame,
    group: ReportGroup,
    month_columns: List[str],
    error_handling: ErrorHandling,
) -> pd.DataFrame:
    """
    Create a DataFrame for a grouped report.

    Args:
        df: Parsed expense DataFrame
        group: Report group configuration
        month_columns: List of month column names
        error_handling: Error handling configuration

    Returns:
        DataFrame ready for charting/reporting
    """
    report_data = []

    for category in group.categories:
        series = get_or_fill_category(
            df, category, month_columns, error_handling
        )

        if series is None:  # Skip mode
            continue

        row = {
            "category": category,
            "indent_level": 0,
            **{col: series[col] for col in month_columns},
        }
        report_data.append(row)

    # Check if we have any data
    if not report_data:
        if error_handling.partial_groups == "error":
            raise ValueError(
                f"No categories found for group: {group.name}"
            )
        elif error_handling.partial_groups == "skip":
            return None

    report_df = pd.DataFrame(report_data)

    # Add group total if configured
    if group.include_group_total and not report_df.empty:
        # Debug: Check columns
        # print(f"DEBUG: report_df columns before add_group_total: {report_df.columns.tolist()}")
        # print(f"DEBUG: report_df dtypes: {report_df.dtypes.to_dict()}")
        report_df = add_group_total(report_df, month_columns)

    return report_df


def create_individual_report(
    df: pd.DataFrame,
    report: IndividualReport,
    month_columns: List[str],
    error_handling: ErrorHandling,
) -> pd.DataFrame:
    """
    Create a DataFrame for an individual category report.

    Args:
        df: Parsed expense DataFrame
        report: Individual report configuration
        month_columns: List of month column names
        error_handling: Error handling configuration

    Returns:
        DataFrame with single category ready for charting/reporting
    """
    series = get_or_fill_category(
        df, report.category, month_columns, error_handling
    )

    if series is None:  # Skip mode
        return None

    row = {
        "category": report.category,
        "indent_level": 0,
        **{col: series[col] for col in month_columns},
    }

    return pd.DataFrame([row])


def create_report_groups(
    df: pd.DataFrame, config: ReportConfig
) -> Dict[str, pd.DataFrame]:
    """
    Create grouped DataFrames for all configured reports.

    This is the main entry point for the grouper module. It takes parsed
    expense data and configuration, then produces report-ready DataFrames
    for each configured report.

    Args:
        df: Parsed expense DataFrame from csv_parser
        config: Report configuration

    Returns:
        Dictionary mapping output_name -> DataFrame
        Each DataFrame is ready for charting or table generation

    Example:
        >>> from quicken_parser import parse_quicken_csv
        >>> from quicken_parser.config import ReportConfig
        >>> from quicken_parser.processors import create_report_groups
        >>>
        >>> df = parse_quicken_csv('data/expenses.csv')
        >>> config = ReportConfig('reports_config.yaml')
        >>> reports = create_report_groups(df, config)
        >>>
        >>> # Access specific report
        >>> groceries_df = reports['groceries']
        >>> utilities_df = reports['utilities']
    """
    # Get month columns (exclude metadata columns)
    month_columns = [
        col
        for col in df.columns
        if col
        not in ["category", "indent_level", "total", "monthly_average"]
    ]

    error_handling = config.get_error_handling()
    reports = {}

    # Process report groups
    for group in config.get_report_groups():
        report_df = create_grouped_report(
            df, group, month_columns, error_handling
        )

        if report_df is not None:  # None if skipped
            reports[group.output_name] = report_df

    # Process individual reports
    for report in config.get_individual_reports():
        report_df = create_individual_report(
            df, report, month_columns, error_handling
        )

        if report_df is not None:  # None if skipped
            reports[report.output_name] = report_df

    return reports


def get_month_columns(df: pd.DataFrame) -> List[str]:
    """
    Extract month column names from parsed DataFrame.

    Args:
        df: Parsed expense DataFrame

    Returns:
        List of month column names
    """
    return [
        col
        for col in df.columns
        if col
        not in [
            "category",
            "indent_level",
            "page_num",
            "total",
            "monthly_average",
            "report_start_date",
            "report_end_date",
        ]
    ]


def validate_against_config(
    df: pd.DataFrame, config: ReportConfig
) -> Dict[str, any]:
    """
    Validate parsed data against configuration.

    Checks which configured categories exist in the parsed data.

    Args:
        df: Parsed expense DataFrame
        config: Report configuration

    Returns:
        Dictionary with validation results:
        {
            'total_configured': int,
            'found': list of str,
            'missing': list of str,
            'match_rate': float
        }
    """
    configured_categories = set(config.get_all_categories())
    actual_categories = set(df["category"].tolist())

    found = configured_categories.intersection(actual_categories)
    missing = configured_categories - actual_categories

    return {
        "total_configured": len(configured_categories),
        "found": sorted(found),
        "missing": sorted(missing),
        "match_rate": len(found) / len(configured_categories)
        if configured_categories
        else 0,
    }
