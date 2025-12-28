"""
CSV Parser Module for Quicken Expense Reports

This module provides functions to extract and parse data from Quicken expense
CSV exports, converting them into structured pandas DataFrames for analysis.

Author: Karl T. Braun
Version: 0.1.0 (Alpha)
"""

import csv
import re
from typing import Dict, List, Optional

import pandas as pd


class QuickenCSVParser:
    """
    Parse Quicken expense CSV exports and extract expense data.

    Quicken CSV exports have a non-standard format with title lines,
    separators, and hierarchical categories indicated by dashes.

    Attributes:
        csv_path (str): Path to the Quicken CSV export
        verbose (bool): Enable detailed logging during parsing
    """

    def __init__(self, csv_path: str, verbose: bool = False):
        """
        Initialize the CSV parser.

        Args:
            csv_path: Path to the Quicken expense CSV export
            verbose: Print detailed parsing information

        Raises:
            FileNotFoundError: If CSV file doesn't exist
        """
        self.csv_path = csv_path
        self.verbose = verbose
        self._validate_csv()

    def _validate_csv(self) -> None:
        """Validate that the CSV file exists and is readable."""
        import os

        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        if not self.csv_path.lower().endswith(".csv"):
            raise ValueError(f"File is not a CSV: {self.csv_path}")

    def parse(self) -> pd.DataFrame:
        """
        Parse the entire CSV and return a structured DataFrame.

        Returns:
            pd.DataFrame: Parsed expense data with columns for each date period

        Raises:
            Exception: If parsing fails
        """
        if self.verbose:
            print(f"Parsing CSV: {self.csv_path}")

        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                lines = list(reader)

            # Extract metadata from header lines
            metadata = self._extract_metadata(lines)
            if self.verbose:
                print(
                    f"Report period: {metadata['start_date']} to {metadata['end_date']}"
                )

            # Find header row and extract date columns
            header_idx, date_columns = self._find_header(lines)
            if self.verbose:
                print(f"Found {len(date_columns)} date columns")

            # Parse data rows
            records = self._parse_data_rows(
                lines, header_idx, date_columns
            )

            if not records:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(records)

            # Calculate total and monthly average from all month columns
            # Find all columns that are date ranges (contain '/')
            date_cols = [col for col in df.columns if "/" in str(col)]
            if date_cols:
                df["total"] = df[date_cols].sum(axis=1).round(2)
                df["monthly_average"] = df[date_cols].mean(axis=1).round(2)

            # Store metadata as attributes (not columns)
            df.attrs["report_start_date"] = metadata["start_date"]
            df.attrs["report_end_date"] = metadata["end_date"]

            if self.verbose:
                print(f"Parsed {len(df)} expense records")

            return df

        except Exception as e:
            raise Exception(f"Failed to parse CSV: {str(e)}")

    def _extract_metadata(self, lines: List[List[str]]) -> Dict[str, str]:
        """
        Extract report metadata from the first few lines.

        Args:
            lines: All CSV lines as list of lists

        Returns:
            dict: Metadata including start_date, end_date
        """
        # Line 2 should have the date range
        if len(lines) > 1:
            date_line = lines[1][0] if lines[1] else ""
            date_pattern = (
                r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})"
            )
            match = re.search(date_pattern, date_line)

            if match:
                return {
                    "start_date": match.group(1),
                    "end_date": match.group(2),
                    "report_type": "Expenses",
                }

        return {
            "start_date": "Unknown",
            "end_date": "Unknown",
            "report_type": "Expenses",
        }

    def _find_header(self, lines: List[List[str]]) -> tuple:
        """
        Find the header row and extract date column names.

        Args:
            lines: All CSV lines

        Returns:
            tuple: (header_row_index, list_of_date_columns)
        """
        for idx, line in enumerate(lines):
            if line and "Category" in line[0]:
                # This is the header row
                # Extract date columns (skip "Category" and "Total")
                date_columns = [
                    col for col in line[2:-1] if col and "/" in col
                ]
                return idx, date_columns

        raise ValueError("Could not find header row with 'Category'")

    def _parse_data_rows(
        self,
        lines: List[List[str]],
        header_idx: int,
        date_columns: List[str],
    ) -> List[Dict]:
        """
        Parse all data rows after the header.

        Args:
            lines: All CSV lines
            header_idx: Index of the header row
            date_columns: List of date column names

        Returns:
            List of dictionaries containing parsed expense records
        """
        records = []
        in_inflows = False
        in_outflows = False

        # Start parsing after separator line (header_idx + 1)
        for line in lines[header_idx + 2 :]:
            if not line or not any(line):  # Skip empty lines
                continue

            # Get category from first or second column
            category_col = (
                line[1] if len(line) > 1 and line[1] else line[0]
            )

            # Check for section markers
            if "Inflows" in category_col:
                in_inflows = True
                in_outflows = False
                continue
            elif "Outflows" in category_col:
                in_inflows = False
                in_outflows = True
                continue

            # Skip Inflows section
            if in_inflows:
                continue

            # Only process Outflows
            if not in_outflows:
                continue

            # Parse category and indentation level
            category, indent_level = self._parse_category(category_col)
            if not category:
                continue

            # Skip "Total" summary rows
            if category.startswith("Total ") or category == "Total":
                continue

            # Explicitly skip Inflows categories (redundant safeguard)
            if category in ("Credit Card Payment", "Transfer"):
                continue

            # Extract values for each month (skip Category column and Total column)
            values = (
                line[2:-1] if len(line) > len(date_columns) else line[2:]
            )

            # Only create record if there are actual numeric values (excluding 0.00)
            has_nonzero_values = any(
                val
                and val.strip()
                and val.strip() not in ("0.00", "0", "")
                for val in values
                if val
            )

            if has_nonzero_values:
                record = {
                    "category": category,
                    "indent_level": indent_level,
                }

                # Map values to date columns
                for date_col, value in zip(date_columns, values):
                    if value:
                        record[date_col] = self._convert_to_numeric(value)

                records.append(record)

        return records

    def _parse_category(self, category_text: str) -> tuple:
        """
        Parse category name and calculate indentation level from dashes.

        Args:
            category_text: Raw category text with possible " - " prefixes

        Returns:
            tuple: (clean_category_name, indentation_level)
        """
        if not category_text:
            return None, 0

        # Count leading " - " sequences
        dash_pattern = r"^(\s*-\s*)+"
        match = re.match(dash_pattern, category_text)

        if match:
            # Count the number of dashes
            indent_level = category_text.count(" - ")
            # Remove all leading dashes and spaces
            category = re.sub(r"^\s*(-\s*)+", "", category_text).strip()
        else:
            indent_level = 0
            category = category_text.strip()

        return category, indent_level

    @staticmethod
    def _convert_to_numeric(value: str) -> Optional[float]:
        """
        Convert string with currency formatting to numeric value.

        Args:
            value: String value (e.g., "-1,234.56" or "1,234.56")

        Returns:
            float: Numeric value, or None if conversion fails
        """
        if not isinstance(value, str) or not value.strip():
            return None

        # Remove quotes, dollar signs, commas, and whitespace
        cleaned = (
            value.strip()
            .strip('"')
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        if not cleaned:
            return None

        try:
            return round(float(cleaned), 2)
        except ValueError:
            return None


def parse_quicken_csv(
    csv_path: str, verbose: bool = False
) -> pd.DataFrame:
    """
    Convenience function to parse a Quicken expense CSV.

    Args:
        csv_path: Path to the Quicken CSV export
        verbose: Enable detailed logging

    Returns:
        pd.DataFrame: Parsed expense data

    Example:
        >>> df = parse_quicken_csv('./data/Expenses-2025-01-2025-11.csv')
        >>> print(df.head())
    """
    parser = QuickenCSVParser(csv_path, verbose=verbose)
    return parser.parse()


if __name__ == "__main__":
    # Example usage for testing
    import sys

    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        print(f"Parsing: {csv_file}")
        df = parse_quicken_csv(csv_file, verbose=True)
        print(f"\nDataFrame shape: {df.shape}")
        print(f"\nFirst few rows:")
        print(df.head())
        print(f"\nColumns: {df.columns.tolist()}")
    else:
        print("Usage: python csv_parser.py <path_to_quicken_csv>")
        print("\nExample:")
        print("  python csv_parser.py ./data/Expenses-2025-01-2025-11.csv")
