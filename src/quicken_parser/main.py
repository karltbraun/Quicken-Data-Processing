"""
Main orchestration module for Quicken expense reporting.

This module provides the entry point for generating expense reports,
including charts and tables, based on configuration.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
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
    specific_reports: Optional[List[str]] = None,
) -> int:
    """
    Generate CSV tables for all or specific reports.

    Args:
        reports: Dictionary of report DataFrames
        config: Report configuration
        output_dir: Directory to save tables
        specific_reports: Optional list of report names to generate

    Returns:
        Number of tables generated
    """
    os.makedirs(output_dir, exist_ok=True)
    table_count = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for output_name, report_df in reports.items():
        # Skip if specific reports requested and this isn't one
        if specific_reports and output_name not in specific_reports:
            continue

        # Generate table filename with timestamp
        save_path = os.path.join(
            output_dir, f"{output_name}_{timestamp}.csv"
        )

        try:
            report_df.to_csv(save_path, index=False)
            table_count += 1
            print(f"  ✓ {output_name}_{timestamp}.csv")
        except Exception as e:
            print(f"  ✗ {output_name}: {e}", file=sys.stderr)

    return table_count


def main(
    config_path: str,
    input_csv: str,
    charts_only: bool = False,
    tables_only: bool = False,
    specific_reports: Optional[List[str]] = None,
    verbose: bool = False,
) -> int:
    """
    Main orchestration function for report generation.

    Args:
        config_path: Path to YAML configuration file
        input_csv: Path to parsed CSV expense data
        charts_only: Generate only charts
        tables_only: Generate only tables
        specific_reports: Optional list of specific reports to generate
        verbose: Enable verbose output

    Returns:
        Exit code (0 for success, non-zero for error)
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

        generated_charts = 0
        generated_tables = 0

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
            tables_dir = output_dir = base_dir  # Save directly in base_dir
            generated_tables = generate_tables(
                reports, config, tables_dir, specific_reports
            )
            print(
                f"    Generated {generated_tables} table(s) in {tables_dir}/"
            )

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
    """Command-line interface entry point."""
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
        required=True,
        help="Path to YAML configuration file",
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
        verbose=args.verbose,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
