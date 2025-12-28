# CSV Parser Requirements

## Overview

This document details requirements specific to parsing Quicken CSV exports.
The CSV parser is now the **primary input method** for this project.

**Status:** ✅ Completed (Dec 27, 2025)

## General Development Requirements

- Refer to pp_requirements.md for the base requirements.
- CSV Input Handling
  - ✅ Quicken (for Mac) CSV export format analyzed and parsed
  - ✅ CSV files contain non-standard formatting: titles, headers, dash separator lines, etc.
  - ✅ Title and separator lines filtered out during parsing
  - ✅ Column headers (date ranges) extracted correctly
  - ✅ Row headers (category names with dash prefixes) parsed correctly
  - ✅ Robust error handling for CSV reading implemented
  - ✅ Date formats standardized
  - ✅ CSV parser output compared to PDF parser for validation

## Implementation Details

### CSV Format Characteristics

- Line 1: Report title (e.g., "Expenses 1H 2024")
- Line 2: Date range (e.g., "1/1/2025 - 11/30/2025")
- Line 3: Account info
- Line 4: Blank line
- Line 5: Column headers (Category + date columns + Total)
- Line 6: Separator line (all dashes)
- Lines 7+: Data rows with category hierarchy

### Category Hierarchy

- Categories use " - " prefixes to indicate nesting level
- Example: " -  -  - Dental Ins" = 4 levels deep
- Empty first column for nested categories
- Category name in second column

### Data Handling

- ✅ Inflows section filtered out (Credit Card Payment, Transfer, etc.)
- ✅ "Total" summary rows excluded
- ✅ Numeric values with commas parsed correctly
- ✅ Quoted values handled properly
- ✅ Non-zero value filtering applied

## Results

**CSV Parser Output:**

- 75 expense categories extracted
- Complete 11-month data for each category
- More comprehensive than PDF parser (19 categories)
- Properly filters summaries and inflows
