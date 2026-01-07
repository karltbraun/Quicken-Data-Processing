"""
Main orchestration module for Quicken expense reporting.

This module provides the entry point for generating expense reports from
Quicken CSV exports. It orchestrates the entire workflow:
1. Load configuration from YAML
2. Parse Quicken CSV data
3. Create report groups based on configuration
4. Generate visual charts and CSV tables

The module supports both raw Quicken exports and pre-parsed CSV files,
with options for generating charts only, tables only, or both.

Command-line usage:
    quicken-report --config reports_config.yaml --input data/expenses.csv

Author: Karl T. Braun
Version: 1.0
"""

import argparse
import os
import sys
from datetime import datetime
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from quicken_parser.charts import plot_monthly_trends
from quicken_parser.config import ReportConfig
from quicken_parser.csv_parser import parse_quicken_csv
from quicken_parser.processors import create_report_groups


def generate_charts(
    reports: dict,
    config: ReportConfig,
    output_dir: str,
    specific_reports: Optional[List[str]] = None,
) -> int:
    """
    Generate charts for all or specific reports.

    Args:
        reports: Dictionary of report DataFrames
        config: Report configuration
        output_dir: Directory to save charts
        specific_reports: Optional list of report names to generate

    Returns:
        Number of charts generated
    """
    os.makedirs(output_dir, exist_ok=True)
    display_settings = config.get_display_settings()
    chart_count = 0

    for output_name, report_df in reports.items():
        # Skip if specific reports requested and this isn't one
        if specific_reports and output_name not in specific_reports:
            continue

        # Get title for chart
        title = None
        for group in config.get_report_groups():
            if group.output_name == output_name:
                title = f"{group.name} - Monthly Expenses"
                break

        if not title:
            for individual in config.get_individual_reports():
                if individual.output_name == output_name:
                    title = f"{individual.name} - Monthly Expenses"
                    break

        # Generate chart
        save_path = os.path.join(output_dir, f"{output_name}.png")

        try:
            fig = plot_monthly_trends(
                report_df,
                categories=report_df["category"].tolist(),
                window=None,  # expanding cumulative average
                title=title,
                figsize=tuple(display_settings.chart_defaults.figsize),
                save_path=save_path,
            )
            plt.close(fig)
            chart_count += 1
            print(f"  ✓ {output_name}.png")
        except Exception as e:
            print(f"  ✗ {output_name}: {e}", file=sys.stderr)

    return chart_count


def generate_tables(
    reports: dict,
    config: ReportConfig,
    output_dir: str,
    timestamp: str,
    specific_reports: Optional[List[str]] = None,
) -> int:
    """
    Generate Excel tables for all or specific reports.

    Creates timestamped Excel files containing expense data organized by
    category and month, with yearly totals and monthly averages.
    Files are named with pattern: {output_name}_{YYYYMMDD_HHMMSS}.xlsx

    Args:
        reports: Dictionary mapping output names to report DataFrames.
                Each DataFrame contains category rows with monthly expense columns.
        config: Report configuration object (used for future extensions)
        output_dir: Directory path where Excel files will be saved.
                   Created if it doesn't exist.
        timestamp: Timestamp string for filename (YYYYMMDD_HHMMSS)
        specific_reports: Optional list of output names to generate.
                         If None, generates all reports.

    Returns:
        Number of tables successfully generated

    Example:
        >>> reports = {'groceries': groceries_df, 'utilities': utilities_df}
        >>> count = generate_tables(reports, config, './reports', '20260106_120000')
        >>> print(f"Generated {count} tables")
    """
    os.makedirs(output_dir, exist_ok=True)
    table_count = 0

    for output_name, report_df in reports.items():
        # Skip if specific reports requested and this isn't one
        if specific_reports and output_name not in specific_reports:
            continue

        # Get month columns
        month_columns = [
            col
            for col in report_df.columns
            if col not in ["category", "indent_level"]
        ]

        # Add Yearly Total and Monthly Average columns
        report_with_totals = report_df.copy()
        report_with_totals["Yearly Total"] = report_with_totals[
            month_columns
        ].sum(axis=1)
        report_with_totals["Monthly Average"] = (
            report_with_totals["Yearly Total"] / len(month_columns)
        )

        # Reorder columns: category, indent_level, months, Yearly Total, Monthly Average
        column_order = (
            ["category", "indent_level"]
            + month_columns
            + ["Yearly Total", "Monthly Average"]
        )
        report_with_totals = report_with_totals[column_order]

        # Generate table filename with timestamp
        save_path = os.path.join(
            output_dir, f"{output_name}_{timestamp}.xlsx"
        )

        try:
            # Write to Excel with formatting
            with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
                report_with_totals.to_excel(
                    writer, sheet_name="Report", index=False
                )

                # Get the worksheet to apply formatting
                worksheet = writer.sheets["Report"]

                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if cell.value:
                                max_length = max(
                                    max_length, len(str(cell.value))
                                )
                        except Exception:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[
                        column_letter
                    ].width = adjusted_width

                # Create formal Excel Table
                from openpyxl.worksheet.table import Table, TableStyleInfo
                
                # Calculate table range
                num_rows = len(report_with_totals)
                num_cols = len(report_with_totals.columns)
                end_col_letter = worksheet.cell(1, num_cols).column_letter
                table_range = f"A1:{end_col_letter}{num_rows + 1}"
                
                # Create table with a style
                table = Table(displayName=f"Table_{output_name}", ref=table_range)
                style = TableStyleInfo(
                    name="TableStyleMedium2",
                    showFirstColumn=False,
                    showLastColumn=False,
                    showRowStripes=True,
                    showColumnStripes=False
                )
                table.tableStyleInfo = style
                worksheet.add_table(table)

                # Apply accounting number format to expense columns
                # Accounting format: _($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)
                accounting_format = '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'
                
                # Format all columns except 'category' and 'indent_level' (columns 1 and 2)
                for col_idx in range(3, num_cols + 1):  # Start from column C (3)
                    for row_idx in range(2, num_rows + 2):  # Skip header row
                        cell = worksheet.cell(row=row_idx, column=col_idx)
                        cell.number_format = accounting_format

            table_count += 1
            print(f"  ✓ {output_name}_{timestamp}.xlsx")
        except Exception as e:
            print(f"  ✗ {output_name}: {e}", file=sys.stderr)

    return table_count


def generate_summary_excel(
    reports: dict,
    config: ReportConfig,
    output_dir: str,
    timestamp: str,
) -> str:
    """
    Generate a consolidated Excel summary of all reports.

    Creates a single Excel file with all expense categories combined into
    one table, showing monthly totals, yearly totals, and monthly averages.

    Args:
        reports: Dictionary mapping output names to report DataFrames
        config: Report configuration object
        output_dir: Directory path where Excel file will be saved
        timestamp: Timestamp string for filename (YYYYMMDD_HHMMSS)

    Returns:
        Path to the generated Excel file

    Excel Structure:
        - Column A: Category name
        - Columns B-M: Monthly totals (Jan-Dec)
        - Column N: Yearly total
        - Column O: Monthly average
    """
    os.makedirs(output_dir, exist_ok=True)

    # Collect all data with report grouping
    summary_data = []

    # Get month columns from first report (all reports have same structure)
    first_report = next(iter(reports.values()))
    month_columns = [
        col
        for col in first_report.columns
        if col not in ["category", "indent_level"]
    ]

    # Process each report
    for output_name, report_df in reports.items():
        # Get report title
        report_title = None
        for group in config.get_report_groups():
            if group.output_name == output_name:
                report_title = group.name
                break
        if not report_title:
            for individual in config.get_individual_reports():
                if individual.output_name == output_name:
                    report_title = individual.name
                    break

        # Add all rows from this report
        for _, row in report_df.iterrows():
            category = row["category"]
            monthly_values = [row[col] for col in month_columns]
            yearly_total = sum(monthly_values)
            monthly_avg = (
                yearly_total / len(monthly_values) if monthly_values else 0
            )

            summary_data.append(
                {
                    "Report": report_title,
                    "Category": category,
                    **{
                        month_columns[i]: monthly_values[i]
                        for i in range(len(month_columns))
                    },
                    "Yearly Total": yearly_total,
                    "Monthly Average": monthly_avg,
                }
            )

    # Create DataFrame
    summary_df = pd.DataFrame(summary_data)

    # Reorder columns: Report, Category, months, Yearly Total, Monthly Average
    column_order = (
        ["Report", "Category"]
        + month_columns
        + ["Yearly Total", "Monthly Average"]
    )
    summary_df = summary_df[column_order]

    # Save to Excel
    excel_path = os.path.join(
        output_dir, f"expense_summary_{timestamp}.xlsx"
    )

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        summary_df.to_excel(
            writer, sheet_name="Expense Summary", index=False
        )

        # Get the worksheet to apply formatting
        worksheet = writer.sheets["Expense Summary"]

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[
                column_letter
            ].width = adjusted_width

    return excel_path


def generate_summary_pie_chart(
    reports: dict,
    config: ReportConfig,
    output_dir: str,
    timestamp: str,
) -> str:
    """
    Generate a pie chart showing expense distribution by monthly averages.

    Creates a pie chart visualization of expense categories based on their
    monthly average spending. Shows only categories/groups with spending
    (excludes categories with zero or positive values).

    Args:
        reports: Dictionary mapping output names to report DataFrames
        config: Report configuration object
        output_dir: Directory path where chart will be saved
        timestamp: Timestamp string for filename (YYYYMMDD_HHMMSS)

    Returns:
        Path to the generated pie chart PNG file
    """
    os.makedirs(output_dir, exist_ok=True)

    # Collect group totals and individual reports with their monthly averages
    chart_data = []

    # Get month columns from first report
    first_report = next(iter(reports.values()))
    month_columns = [
        col
        for col in first_report.columns
        if col not in ["category", "indent_level"]
    ]

    # Process each report
    for output_name, report_df in reports.items():
        # Get report title
        report_title = None
        for group in config.get_report_groups():
            if group.output_name == output_name:
                report_title = group.name
                # For grouped reports, use the Group Total row
                group_total_row = report_df[
                    report_df["category"] == "Group Total"
                ]
                if not group_total_row.empty:
                    row = group_total_row.iloc[0]
                    monthly_values = [
                        abs(row[col]) for col in month_columns
                    ]
                    monthly_avg = sum(monthly_values) / len(monthly_values)
                    if monthly_avg > 0:  # Only include if there's spending
                        chart_data.append(
                            {"label": report_title, "value": monthly_avg}
                        )
                break

        if not report_title:
            # Individual report - use the single row
            for individual in config.get_individual_reports():
                if individual.output_name == output_name:
                    report_title = individual.name
                    row = report_df.iloc[0]
                    monthly_values = [
                        abs(row[col]) for col in month_columns
                    ]
                    monthly_avg = sum(monthly_values) / len(monthly_values)
                    if monthly_avg > 0:  # Only include if there's spending
                        chart_data.append(
                            {"label": report_title, "value": monthly_avg}
                        )
                    break

    # Sort by value descending
    chart_data.sort(key=lambda x: x["value"], reverse=True)

    # Prepare data for pie chart
    labels = [item["label"] for item in chart_data]
    values = [item["value"] for item in chart_data]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create pie chart
    colors = plt.cm.Set3(range(len(labels)))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct=lambda pct: f"${pct * sum(values) / 100:.0f}\n({pct:.1f}%)",
        startangle=90,
        colors=colors,
        textprops={"fontsize": 9},
    )

    # Enhance text visibility
    for autotext in autotexts:
        autotext.set_color("black")
        autotext.set_weight("bold")
        autotext.set_fontsize(8)

    # Add title
    ax.set_title(
        f"Monthly Average Expense Distribution\nTotal: ${sum(values):.2f}/month",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    # Equal aspect ratio ensures circular pie
    ax.axis("equal")

    # Save chart
    chart_path = os.path.join(
        output_dir, f"expense_summary_pie_{timestamp}.png"
    )
    plt.tight_layout()
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return chart_path


def main(
    config_path: str,
    input_csv: str,
    charts_only: bool = False,
    tables_only: bool = False,
    specific_reports: Optional[List[str]] = None,
    summary_excel: bool = False,
    verbose: bool = False,
) -> int:
    """
    Main orchestration function for report generation.

    Coordinates the complete report generation workflow from data loading
    through output generation. Supports both raw Quicken exports and
    pre-parsed CSV files.

    The function performs these steps:
    1. Loads and validates configuration from YAML file
    2. Parses input CSV (auto-detects format)
    3. Creates report groups by aggregating categories
    4. Generates charts (PNG files) and/or tables (CSV files)
    5. Displays summary of generated outputs

    Args:
        config_path: Path to YAML configuration file defining report groups,
                    categories, and display settings
        input_csv: Path to CSV expense data. Can be:
                  - Raw Quicken export (auto-parsed)
                  - Pre-parsed CSV (with 'parsed_expenses' or 'Expense_Report' in name)
        charts_only: If True, generates only charts (skips table generation)
        tables_only: If True, generates only tables (skips chart generation)
        specific_reports: Optional list of report output names to generate.
                         If None, generates all configured reports.
        verbose: If True, prints detailed progress information

    Returns:
        Exit code:
        - 0: Success
        - 1: Error (file not found, invalid config, parsing failure, etc.)

    Raises:
        FileNotFoundError: If config or input file doesn't exist
        ValueError: If configuration is invalid or data can't be parsed
    """
    try:
        print("=" * 70)
        print("QUICKEN EXPENSE REPORT GENERATOR")
        print("=" * 70)

        # Step 1: Load configuration
        if verbose:
            print(f"\n[1] Loading configuration from {config_path}...")
        else:
            print("\n[1] Loading configuration...")

        config = ReportConfig(config_path)
        if verbose:
            print(
                f"    Reports: {len(config.get_report_groups())} groups, "
                f"{len(config.get_individual_reports())} individual"
            )

        # Step 2: Load data
        if verbose:
            print(f"\n[2] Loading expense data from {input_csv}...")
        else:
            print("\n[2] Loading expense data...")

        # Check if input is already parsed or raw Quicken export
        if (
            "Expense_Report" in input_csv
            or "parsed_expenses" in input_csv
            or input_csv.endswith("_parsed.csv")
        ):
            # Already parsed
            df = pd.read_csv(input_csv)
            if verbose:
                print(
                    f"    Loaded {len(df)} expense categories (pre-parsed)"
                )
        else:
            # Raw Quicken export
            df = parse_quicken_csv(input_csv, verbose=verbose)
            if verbose:
                print(f"    Parsed {len(df)} expense categories")

        # Step 3: Create report groups
        if verbose:
            print("\n[3] Creating report groups...")
        else:
            print("\n[3] Creating report groups...")

        reports = create_report_groups(df, config)

        if specific_reports:
            # Filter to requested reports
            reports = {
                k: v for k, v in reports.items() if k in specific_reports
            }
            if not reports:
                print(
                    f"Error: None of the specified reports found: {specific_reports}"
                )
                return 1

        print(f"    Created {len(reports)} report(s)")

        # Step 4: Generate outputs
        output_settings = config.get_output_settings()
        base_dir = output_settings.base_dir
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        generated_charts = 0
        generated_tables = 0
        excel_summary_path = None
        pie_chart_path = None

        # Generate charts
        if not tables_only:
            print("\n[4] Generating charts...")
            charts_dir = os.path.join(base_dir, "charts")
            generated_charts = generate_charts(
                reports, config, charts_dir, specific_reports
            )
            print(
                f"    Generated {generated_charts} chart(s) in {charts_dir}/"
            )

        # Generate tables
        if not charts_only:
            print("\n[5] Generating tables...")
            tables_dir = os.path.join(base_dir, "tables")
            generated_tables = generate_tables(
                reports, config, tables_dir, timestamp, specific_reports
            )
            print(
                f"    Generated {generated_tables} table(s) in {tables_dir}/"
            )

        # Generate Excel summary
        if summary_excel:
            print("\n[6] Generating Excel summary...")
            excel_summary_path = generate_summary_excel(
                reports, config, base_dir, timestamp
            )
            print(f"    ✓ {os.path.basename(excel_summary_path)}")

            # Generate pie chart
            pie_chart_path = generate_summary_pie_chart(
                reports, config, base_dir, timestamp
            )
            print(f"    ✓ {os.path.basename(pie_chart_path)}")

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Configuration:  {config_path}")
        print(f"Input data:     {input_csv}")
        print(f"Reports:        {len(reports)}")
        if not tables_only:
            print(f"Charts:         {generated_charts}")
        if not charts_only:
            print(f"Tables:         {generated_tables}")
        if summary_excel:
            print(
                f"Excel Summary:  {os.path.basename(excel_summary_path)}"
            )
            print(f"Pie Chart:      {os.path.basename(pie_chart_path)}")
        print(f"Output:         {base_dir}/")
        print("=" * 70)
        print("✓ Report generation completed successfully!")
        print("=" * 70)

        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(
            f"Error: Invalid configuration or data - {e}", file=sys.stderr
        )
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if verbose:
            import traceback

            traceback.print_exc()
        return 1


def cli():
    """
    Command-line interface entry point.

    Parses command-line arguments and invokes the main report generation
    function. This is the entry point configured in pyproject.toml as the
    'quicken-report' console script.

    Exit codes:
        0: Success
        1: Error during execution
        2: Invalid command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate expense reports from Quicken CSV data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all reports
  quicken-report --config reports_config.yaml --input data/expenses.csv

  # Generate only charts
  quicken-report --config config.yaml --input data.csv --charts-only

  # Generate specific reports
  quicken-report --config config.yaml --input data.csv --reports groceries,utilities

  # Verbose output
  quicken-report --config config.yaml --input data.csv --verbose
        """,
    )

    parser.add_argument(
        "-c",
        "--config",
        default="reports_config.yaml",
        help="Path to YAML configuration file (default: reports_config.yaml)",
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to CSV expense data (parsed or raw Quicken export)",
    )

    parser.add_argument(
        "--charts-only",
        action="store_true",
        help="Generate only charts (skip tables)",
    )

    parser.add_argument(
        "--tables-only",
        action="store_true",
        help="Generate only tables (skip charts)",
    )

    parser.add_argument(
        "-r",
        "--reports",
        help="Comma-separated list of specific reports to generate",
    )

    parser.add_argument(
        "--summary-excel",
        action="store_true",
        help="Generate consolidated Excel summary and pie chart of all reports",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.charts_only and args.tables_only:
        parser.error("Cannot specify both --charts-only and --tables-only")

    # Parse specific reports if provided
    specific_reports = None
    if args.reports:
        specific_reports = [r.strip() for r in args.reports.split(",")]

    # Run main function
    exit_code = main(
        config_path=args.config,
        input_csv=args.input,
        charts_only=args.charts_only,
        tables_only=args.tables_only,
        specific_reports=specific_reports,
        summary_excel=args.summary_excel,
        verbose=args.verbose,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
