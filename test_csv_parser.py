"""
Test script for Quicken CSV Parser

Compares CSV parser output to PDF parser output for consistency validation.
"""

from quicken_parser import parse_quicken_pdf
from quicken_parser.csv_parser import parse_quicken_csv

CSV_PATH = "./data/Expenses 2025-01 2025-11.csv"
PDF_PATH = "./data/Expenses 2025-01 2025-11.pdf"


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
    print("\n\n[2] CSV PARSING RESULTS")
    print("-" * 70)
    print(f"DataFrame Shape: {df_csv.shape} (rows × columns)")
    print(f"\nColumn Names ({len(df_csv.columns)} total):")
    for i, col in enumerate(df_csv.columns, 1):
        print(f"  {i}. {col}")

    print(f"\n\nFirst 10 Rows:")
    print(df_csv.head(10).to_string())

    # Parse PDF for comparison
    print("\n\n[3] PARSING PDF FILE FOR COMPARISON")
    print("-" * 70)
    try:
        df_pdf = parse_quicken_pdf(PDF_PATH, verbose=False)
    except Exception as e:
        print(f"ERROR parsing PDF: {e}")
        return

    print(f"PDF DataFrame Shape: {df_pdf.shape}")

    # Compare results
    print("\n\n[4] COMPARISON: CSV vs PDF")
    print("-" * 70)

    # Compare row counts
    print(f"CSV records: {len(df_csv)}")
    print(f"PDF records: {len(df_pdf)}")
    print(f"Difference: {abs(len(df_csv) - len(df_pdf))} records")

    # Compare categories
    csv_categories = set(df_csv["category"].tolist())
    pdf_categories = set(df_pdf["category"].tolist())

    print(f"\nUnique categories in CSV: {len(csv_categories)}")
    print(f"Unique categories in PDF: {len(pdf_categories)}")

    only_csv = csv_categories - pdf_categories
    only_pdf = pdf_categories - csv_categories

    if only_csv:
        print(f"\nCategories only in CSV ({len(only_csv)}):")
        for cat in sorted(only_csv):
            print(f"  - {cat}")

    if only_pdf:
        print(f"\nCategories only in PDF ({len(only_pdf)}):")
        for cat in sorted(only_pdf):
            print(f"  - {cat}")

    if not only_csv and not only_pdf:
        print("\n✓ All categories match between CSV and PDF!")

    # Save CSV output with date-based filename
    start_date = df_csv.attrs.get('report_start_date', 'unknown')
    end_date = df_csv.attrs.get('report_end_date', 'unknown')
    
    # Convert dates to yyyymmdd format
    from datetime import datetime
    try:
        start_dt = datetime.strptime(start_date, '%m/%d/%Y')
        end_dt = datetime.strptime(end_date, '%m/%d/%Y')
        start_str = start_dt.strftime('%Y%m%d')
        end_str = end_dt.strftime('%Y%m%d')
        output_path = f"./reports/Expense_Report_{start_str}_-_{end_str}.csv"
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
