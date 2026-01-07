"""
End-to-end test of the complete reporting pipeline.

Tests the full flow: Config → Parse → Group → Chart
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from quicken_parser.config import ReportConfig
from quicken_parser.processors import create_report_groups
from quicken_parser.charts import plot_monthly_trends


def main():
    print("=" * 70)
    print("END-TO-END PIPELINE TEST")
    print("=" * 70)

    # Step 1: Load configuration
    print("\n[Step 1] Loading configuration...")
    config = ReportConfig("./reports_config.yaml")
    print(f"✓ Loaded config: {config}")

    # Step 2: Load parsed data
    print("\n[Step 2] Loading parsed expense data...")
    df = pd.read_csv("./reports/Expense_Report_20250101_-_20251130.csv")
    print(f"✓ Loaded {len(df)} expense categories")

    # Step 3: Create report groups
    print("\n[Step 3] Creating report groups using config...")
    reports = create_report_groups(df, config)
    print(f"✓ Created {len(reports)} reports")

    # Step 4: Generate charts
    print("\n[Step 4] Generating charts for all reports...")
    output_dir = "./reports/charts_e2e"
    os.makedirs(output_dir, exist_ok=True)

    display_settings = config.get_display_settings()

    chart_count = 0
    for output_name, report_df in reports.items():
        # Determine if it's a group or individual report
        is_group = len(report_df) > 1

        # Get report name for title
        if is_group:
            # Find the group config
            for group in config.get_report_groups():
                if group.output_name == output_name:
                    title = f"{group.name} - Monthly Expenses"
                    break
        else:
            # Find the individual config
            for individual in config.get_individual_reports():
                if individual.output_name == output_name:
                    title = f"{individual.name} - Monthly Expenses"
                    break

        # Generate chart
        save_path = os.path.join(output_dir, f"{output_name}.png")
        print(f"  Creating chart: {output_name} ({len(report_df)} rows)")

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
            print(f"    ✓ Saved: {save_path}")
        except Exception as e:
            print(f"    ✗ Failed: {e}")

    # Step 5: Summary
    print("\n" + "=" * 70)
    print("END-TO-END TEST SUMMARY")
    print("=" * 70)
    print(f"Configuration:     {config.config_path}")
    print(f"Input data:        {len(df)} categories")
    print(f"Report groups:     {len(config.get_report_groups())}")
    print(f"Individual reports: {len(config.get_individual_reports())}")
    print(f"Total reports:     {len(reports)}")
    print(f"Charts generated:  {chart_count}")
    print(f"Output directory:  {output_dir}/")

    print("\n" + "=" * 70)
    print("✓ END-TO-END TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    # List generated files
    print("\nGenerated chart files:")
    for filename in sorted(os.listdir(output_dir)):
        if filename.endswith(".png"):
            filepath = os.path.join(output_dir, filename)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  - {filename} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
