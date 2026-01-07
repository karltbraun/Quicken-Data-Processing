"""
Test script for grouper module.

Validates that the grouper correctly processes parsed data according to config.
"""

import pandas as pd

from quicken_parser.config import ReportConfig
from quicken_parser.processors import create_report_groups
from quicken_parser.processors.grouper import (
    get_month_columns,
    validate_against_config,
)


def main():
    print("=" * 70)
    print("GROUPER TEST")
    print("=" * 70)

    # Load configuration
    print("\n[1] Loading configuration...")
    config = ReportConfig("./reports_config.yaml")
    print(f"✓ Config loaded: {config}")

    # Parse CSV
    print("\n[2] Loading parsed CSV data...")
    csv_path = "./reports/Expense_Report_20250101_-_20251130.csv"
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df)} categories from {csv_path}")

    # Validate against config
    print("\n[3] Validating data against config...")
    validation = validate_against_config(df, config)
    print(f"Configured categories: {validation['total_configured']}")
    print(f"Found in data: {len(validation['found'])}")
    print(f"Missing from data: {len(validation['missing'])}")
    print(f"Match rate: {validation['match_rate']:.1%}")

    if validation["missing"]:
        print("\nMissing categories (will be filled with $0):")
        for cat in validation["missing"]:
            print(f"  - {cat}")

    # Create report groups
    print("\n[4] Creating report groups...")
    reports = create_report_groups(df, config)
    print(f"✓ Created {len(reports)} reports\n")

    month_columns = get_month_columns(df)
    print(f"Month columns: {len(month_columns)}")

    # Display each report summary
    print("\n[5] Report Summaries")
    print("-" * 70)

    for output_name, report_df in reports.items():
        print(f"\n{output_name}:")
        print(f"  Rows: {len(report_df)}")
        print(f"  Columns: {list(report_df.columns)}")

        # Check for Group Total
        has_total = "Group Total" in report_df["category"].values
        if has_total:
            print("  ✓ Has Group Total row")

        # Show categories
        print("  Categories:")
        for cat in report_df["category"].values:
            print(f"    - {cat}")

        # Show first month's values
        if month_columns:
            first_month = month_columns[0]
            print(f"  First month ({first_month}) values:")
            for _, row in report_df.iterrows():
                print(f"    {row['category']}: ${row[first_month]:,.2f}")

    # Test specific report access
    print("\n[6] Testing Specific Report Access")
    print("-" * 70)

    # Groceries (individual)
    if "groceries" in reports:
        groceries = reports["groceries"]
        print("\nGroceries Report:")
        print(f"  Shape: {groceries.shape}")
        print(groceries.to_string())

    # Utilities (grouped)
    if "utilities" in reports:
        utilities = reports["utilities"]
        print("\nUtilities Report:")
        print(f"  Shape: {utilities.shape}")
        print(utilities.to_string())

    print("\n" + "=" * 70)
    print("✓ Grouper test completed successfully!")
    print("=" * 70)
    print(f"\nAll {len(reports)} reports are ready for charting/table generation")


if __name__ == "__main__":
    main()
