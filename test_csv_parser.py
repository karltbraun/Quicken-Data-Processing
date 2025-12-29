"""
Test script for Quicken CSV Parser

Parses Quicken CSV expense reports and generates output files.
"""

from quicken_parser.csv_parser import parse_quicken_csv

CSV_PATH = "./data/Expenses 20250101 - 20251130.csv"


def main():
    print("=" * 70)
    print("QUICKEN CSV PARSER TEST")
    print("=" * 70)

    # Parse CSV
    print("\n[1] PARSING CSV FILE")
    print("-" * 70)
    try:
        df_csv = parse_quicken_csv(CSV_PATH, verbose=True)
    except Exception as e:
        print(f"ERROR parsing CSV: {e}")
        import traceback

        traceback.print_exc()
        return

    # Display CSV results
    print("\n[2] CSV PARSING RESULTS")
    print("-" * 70)
    print(f"DataFrame Shape: {df_csv.shape} (rows × columns)")
    print(f"\nColumn Names ({len(df_csv.columns)} total):")
    for i, col in enumerate(df_csv.columns, 1):
        print(f"  {i}. {col}")

    print(f"\n\nFirst 10 Rows:")
    print(df_csv.head(10).to_string())

    # Save CSV output with date-based filename
    print("\n[3] SAVING OUTPUT")
    print("-" * 70)
    start_date = df_csv.attrs.get("report_start_date", "unknown")
    end_date = df_csv.attrs.get("report_end_date", "unknown")

    # Convert dates to yyyymmdd format
    from datetime import datetime

    try:
        start_dt = datetime.strptime(start_date, "%m/%d/%Y")
        end_dt = datetime.strptime(end_date, "%m/%d/%Y")
        start_str = start_dt.strftime("%Y%m%d")
        end_str = end_dt.strftime("%Y%m%d")
        output_path = (
            f"./reports/Expense_Report_{start_str}_-_{end_str}.csv"
        )
    except:
        output_path = "./reports/Expense_Report.csv"

    try:
        df_csv.to_csv(output_path, index=False)
        print(f"\n✓ CSV data saved to: {output_path}")
    except Exception as e:
        print(f"\n✗ Could not save CSV: {e}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
