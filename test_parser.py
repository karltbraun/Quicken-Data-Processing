"""
Test script for Quicken PDF Parser

This script tests the PDF parser with the sample Quicken expense report
and displays the results for inspection.

Usage:
    python test_parser.py
"""

from quicken_parser import extract_raw_text, parse_quicken_pdf

# Path to the sample PDF
PDF_PATH = "./data/Expenses 2025-01 2025-11.pdf"


def main():
    print("=" * 70)
    print("QUICKEN PDF PARSER TEST")
    print("=" * 70)

    # Step 1: Extract raw text to see PDF structure
    print("\n[1] EXTRACTING RAW TEXT FROM FIRST PAGE")
    print("-" * 70)
    try:
        raw_text = extract_raw_text(PDF_PATH, page_num=0)
        print(raw_text[:1000])  # First 1000 characters
        print("\n... (truncated for display)")
    except Exception as e:
        print(f"ERROR extracting raw text: {e}")
        return

    # Step 2: Parse the full PDF
    print("\n\n[2] PARSING FULL PDF")
    print("-" * 70)
    try:
        df = parse_quicken_pdf(PDF_PATH, verbose=True)
    except Exception as e:
        print(f"ERROR parsing PDF: {e}")
        import traceback

        traceback.print_exc()
        return

    # Step 3: Display results
    print("\n\n[3] PARSING RESULTS")
    print("-" * 70)
    print(f"DataFrame Shape: {df.shape} (rows × columns)")
    print(f"\nColumn Names ({len(df.columns)} total):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")

    print("\n\nFirst 10 Rows:")
    print(df.head(10).to_string())

    print("\n\nData Types:")
    print(df.dtypes.to_string())

    print("\n\nBasic Statistics:")
    print(df.describe().to_string())

    # Check for missing data
    print("\n\nMissing Values:")
    missing = df.isnull().sum()
    print(
        missing[missing > 0].to_string()
        if missing.sum() > 0
        else "  No missing values"
    )

    # Save to CSV with date-based filename
    start_date = df.attrs.get('report_start_date', 'unknown')
    end_date = df.attrs.get('report_end_date', 'unknown')
    
    # Convert dates to yyyymmdd format
    from datetime import datetime
    try:
        start_dt = datetime.strptime(start_date, '%m/%d/%Y')
        end_dt = datetime.strptime(end_date, '%m/%d/%Y')
        start_str = start_dt.strftime('%Y%m%d')
        end_str = end_dt.strftime('%Y%m%d')
        output_path = f"./reports/Expense_Report_{start_str}_-_{end_str}_PDF.csv"
    except:
        output_path = "./reports/Expense_Report_PDF.csv"
    
    try:
        df.to_csv(output_path, index=False)
        print(f"\n✓ Data saved to: {output_path}")
    except Exception as e:
        print(f"\n✗ Could not save CSV: {e}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
