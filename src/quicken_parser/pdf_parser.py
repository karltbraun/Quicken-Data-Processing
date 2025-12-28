"""
PDF Parser Module for Quicken Expense Reports

This module provides functions to extract and parse data from Quicken expense
PDF reports, converting them into structured pandas DataFrames for analysis.

Author: Karl T. Braun
Version: 0.1.0 (Alpha)
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import pdfplumber


class QuickenPDFParser:
    """
    Parse Quicken expense PDF reports and extract expense data.

    This alpha version focuses on extracting tables from the PDF and
    converting them into structured data. Future versions will handle
    different Quicken report formats.

    Attributes:
        pdf_path (str): Path to the Quicken PDF report
        verbose (bool): Enable detailed logging during parsing
    """

    def __init__(self, pdf_path: str, verbose: bool = False):
        """
        Initialize the PDF parser.

        Args:
            pdf_path: Path to the Quicken expense PDF report
            verbose: Print detailed parsing information

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a valid PDF
        """
        self.pdf_path = pdf_path
        self.verbose = verbose
        self._validate_pdf()

    def _validate_pdf(self) -> None:
        """Validate that the PDF file exists and is readable."""
        import os

        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        if not self.pdf_path.lower().endswith(".pdf"):
            raise ValueError(f"File is not a PDF: {self.pdf_path}")

    def parse(self) -> pd.DataFrame:
        """
        Parse the entire PDF and return a structured DataFrame.

        Uses layout-based text extraction to handle Quicken's positioned text format.

        Returns:
            pd.DataFrame: Parsed expense data with columns for each date period

        Raises:
            Exception: If parsing fails
        """
        if self.verbose:
            print(f"Parsing PDF: {self.pdf_path}")

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Extract metadata
                metadata = self._extract_metadata(pdf)
                if self.verbose:
                    print(
                        f"Report period: {metadata['start_date']} to {metadata['end_date']}"
                    )

                # Parse all pages using layout-based extraction
                all_records = []
                for page_num, page in enumerate(pdf.pages):
                    if self.verbose:
                        print(f"  Parsing page {page_num + 1}")
                    records = self._parse_page_layout(page, page_num + 1)
                    all_records.extend(records)

                if not all_records:
                    return pd.DataFrame()

                # Convert to DataFrame
                df = pd.DataFrame(all_records)

                # Consolidate duplicate categories (same category across multiple pages)
                df = self._consolidate_categories(df)

                # Calculate total and monthly average from all month columns
                # Find all columns that are date ranges (contain '/')
                date_cols = [col for col in df.columns if "/" in str(col)]
                if date_cols:
                    df["total"] = df[date_cols].sum(axis=1).round(2)
                    df["monthly_average"] = (
                        df[date_cols].mean(axis=1).round(2)
                    )

                # Store metadata as attributes (not columns)
                df.attrs["report_start_date"] = metadata["start_date"]
                df.attrs["report_end_date"] = metadata["end_date"]

                if self.verbose:
                    print(f"Parsed {len(df)} expense records")

                return df

        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")

    def _extract_metadata(self, pdf) -> Dict[str, str]:
        """
        Extract report metadata from the first page.

        Looks for patterns like "1/1/2025 - 11/30/2025" to identify
        the date range of the report.

        Args:
            pdf: pdfplumber PDF object

        Returns:
            dict: Metadata including start_date, end_date, report_type
        """
        first_page_text = pdf.pages[0].extract_text()

        # Pattern: MM/DD/YYYY - MM/DD/YYYY
        date_pattern = (
            r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})"
        )
        match = re.search(date_pattern, first_page_text)

        if match:
            start_date = match.group(1)
            end_date = match.group(2)
        else:
            # Fallback if no date range found
            start_date = "Unknown"
            end_date = "Unknown"

        return {
            "start_date": start_date,
            "end_date": end_date,
            "report_type": "Expenses",  # Could be extended for other reports
            "parsed_at": datetime.now().isoformat(),
        }

    def _parse_page_layout(self, page, page_num: int) -> List[Dict]:
        """
        Parse a single page using layout-preserved text extraction.

        Args:
            page: pdfplumber page object
            page_num: Page number for tracking

        Returns:
            List of dictionaries containing parsed expense records
        """
        # Extract text with layout preservation
        text = page.extract_text(layout=True)
        if not text:
            return []

        lines = text.split("\n")
        records = []

        # Find header line (contains "Category" and date ranges)
        header_line = None
        header_idx = None
        date_columns = []

        for idx, line in enumerate(lines):
            if "Category" in line and "/" in line:
                header_line = line
                header_idx = idx
                # Extract date ranges from header
                date_pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}\s*-\s*\d{1,2}/\d{1,2}/\d{2,4})"
                date_columns = re.findall(date_pattern, line)
                break

        if not header_line or not date_columns:
            return []

        # Track whether we're in Inflows or Outflows section
        in_inflows = False
        in_outflows = False

        # Parse data lines after header
        for line in lines[header_idx + 1 :]:
            # Skip empty lines, footers, and header repetitions
            if (
                not line.strip()
                or "Page" in line
                or "printed from" in line
                or "Category" in line
            ):
                continue

            # Calculate indentation level
            indent = len(line) - len(line.lstrip())

            # Extract category name (text before first $ or at end if no values)
            category_match = re.match(
                r"^(\s*)(.*?)(?=\s+[-\(]?\$|$)", line
            )
            if not category_match:
                continue

            category = category_match.group(2).strip()
            if not category:
                continue

            # Track section transitions
            if category == "Inflows":
                in_inflows = True
                in_outflows = False
                continue
            elif category == "Outflows":
                in_inflows = False
                in_outflows = True
                continue

            # Skip all Inflows entries (Credit Card Payment, Transfer, etc.)
            if in_inflows:
                continue

            # Only process Outflows (expense) data
            if not in_outflows:
                continue

            # Extract all monetary values from the line
            value_pattern = r"[-\(]?\$[\d,]+\.?\d*\)?"
            values = re.findall(value_pattern, line)

            # Create record if values found
            if values:
                record = {
                    "category": category,
                    "indent_level": indent,
                    "page_num": page_num,
                }

                # Map values to date columns
                for i, (date_col, value) in enumerate(
                    zip(date_columns, values)
                ):
                    record[date_col] = self._convert_to_numeric(value)

                records.append(record)

        return records

    def _consolidate_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Consolidate duplicate categories that appear across multiple pages.

        Each category may appear on 3 pages (one for each set of months).
        This combines them into single records with all month values.

        Args:
            df: DataFrame with potentially duplicate categories

        Returns:
            DataFrame with consolidated categories
        """
        if df.empty:
            return df

        # Get month columns (exclude metadata columns)
        month_cols = [
            col
            for col in df.columns
            if "/" in col and "-" in col and col.count("/") >= 2
        ]

        # Group by category and take the first indent_level
        # For month columns, use first non-null value (coalesce)
        agg_dict = {"indent_level": "first", "page_num": "first"}
        for col in month_cols:
            agg_dict[col] = (
                lambda x: x.dropna().iloc[0]
                if not x.dropna().empty
                else None
            )

        consolidated = df.groupby("category", as_index=False).agg(agg_dict)

        return consolidated

    def _extract_all_tables(self, pdf) -> List[pd.DataFrame]:
        """
        Extract all tables from the PDF using text-based strategy.

        Quicken PDFs don't have formal table structures, so we use
        text positioning to identify columns and rows.

        Args:
            pdf: pdfplumber PDF object

        Returns:
            list: List of DataFrames, one per detected table
        """
        all_tables = []

        for page_num, page in enumerate(pdf.pages):
            if self.verbose:
                print(f"  Extracting tables from page {page_num + 1}")

            # Use text-based strategy for Quicken's layout-based PDFs
            try:
                # Text-based extraction works better for positioned text
                tables = page.extract_tables(
                    {
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                        "intersection_tolerance": 15,
                    }
                )

                if tables:
                    for table in tables:
                        if table and len(table) > 0:
                            # Filter out None values and empty rows
                            filtered_table = [
                                [cell if cell else "" for cell in row]
                                for row in table
                                if row
                            ]
                            if filtered_table:
                                df = pd.DataFrame(
                                    filtered_table[1:],
                                    columns=filtered_table[0],
                                )
                                all_tables.append(df)
                                if self.verbose:
                                    print(
                                        f"    Found table with {len(df)} rows and {len(df.columns)} columns"
                                    )
            except Exception as e:
                if self.verbose:
                    print(
                        f"    Warning: Could not extract tables from page {page_num + 1}: {e}"
                    )

        return all_tables

    def _consolidate_tables(
        self, tables: List[pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Consolidate multiple tables into a single structured DataFrame.

        Handles tables with different column counts and duplicate column names
        by making column names unique before concatenation.

        Args:
            tables: List of DataFrames from PDF tables

        Returns:
            pd.DataFrame: Consolidated expense data
        """
        if not tables:
            return pd.DataFrame()

        # Make column names unique across all tables to avoid pandas concat errors
        cleaned_tables = []
        for i, table in enumerate(tables):
            # Create a copy to avoid modifying original
            df_copy = table.copy()

            # Make duplicate column names unique by adding suffix
            cols = df_copy.columns.tolist()
            seen = {}
            new_cols = []
            for col in cols:
                if col in seen:
                    seen[col] += 1
                    new_cols.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    new_cols.append(col)
            df_copy.columns = new_cols

            # Add page number for tracking
            df_copy["_page_num"] = i + 1

            cleaned_tables.append(df_copy)

        # Concatenate all tables, filling missing columns with NaN
        df = pd.concat(cleaned_tables, ignore_index=True, sort=False)

        # Clean up the data
        df = self._clean_data(df)

        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the extracted data.

        Args:
            df: Raw extracted DataFrame

        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        # Remove empty rows and columns
        df = df.dropna(how="all")
        df = df[df.columns[df.notna().any()]]

        # Convert amount columns to numeric (removing $ and commas)
        for col in df.columns:
            if any(
                char in str(df[col].iloc[0]) for char in ["$", "-", "("]
            ):
                df[col] = df[col].apply(self._convert_to_numeric)

        return df

    @staticmethod
    def _convert_to_numeric(value: str) -> Optional[float]:
        """
        Convert string with currency formatting to numeric value.

        Args:
            value: String value (e.g., "-$1,234.56" or "($100.00)")

        Returns:
            float: Numeric value, or None if conversion fails
        """
        if not isinstance(value, str) or value.strip() == "":
            return None

        # Remove whitespace and currency symbols
        cleaned = value.strip().replace("$", "").replace(",", "")

        # Handle parentheses notation for negative
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = "-" + cleaned[1:-1]

        try:
            return round(float(cleaned), 2)
        except ValueError:
            return None


def parse_quicken_pdf(
    pdf_path: str, verbose: bool = False
) -> pd.DataFrame:
    """
    Convenience function to parse a Quicken expense PDF.

    Args:
        pdf_path: Path to the Quicken PDF report
        verbose: Enable detailed logging

    Returns:
        pd.DataFrame: Parsed expense data

    Example:
        >>> df = parse_quicken_pdf('./data/Expenses-2025-01-2025-11.pdf')
        >>> print(df.head())
    """
    parser = QuickenPDFParser(pdf_path, verbose=verbose)
    return parser.parse()


# Alpha/Testing function - extracts raw text for inspection
def extract_raw_text(pdf_path: str, page_num: int = 0) -> str:
    """
    Extract raw text from a specific page (useful for debugging).

    Args:
        pdf_path: Path to PDF file
        page_num: Page number (0-indexed)

    Returns:
        str: Raw text content of the page
    """
    with pdfplumber.open(pdf_path) as pdf:
        if page_num >= len(pdf.pages):
            raise ValueError(f"PDF has only {len(pdf.pages)} pages")

        return pdf.pages[page_num].extract_text()


if __name__ == "__main__":
    # Example usage for testing
    import sys

    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        print(f"Parsing: {pdf_file}")
        df = parse_quicken_pdf(pdf_file, verbose=True)
        print(f"\nDataFrame shape: {df.shape}")
        print("\nFirst few rows:")
        print(df.head())
        print(f"\nColumns: {df.columns.tolist()}")
    else:
        print("Usage: python pdf_parser.py <path_to_quicken_pdf>")
        print("\nExample:")
        print("  python pdf_parser.py ./data/Expenses-2025-01-2025-11.pdf")
