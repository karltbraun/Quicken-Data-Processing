"""
Alternative parser using layout-based text extraction
"""

import re

import pandas as pd
import pdfplumber

PDF_PATH = "./data/Expenses 2025-01 2025-11.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]

    # Get text with layout preserved
    text = page.extract_text(layout=True)

    print("LAYOUT-PRESERVED TEXT:")
    print("=" * 70)
    print(text)
    print("\n" + "=" * 70)

    # Split into lines
    lines = text.split("\n")

    print(f"\nTotal lines: {len(lines)}")
    print("\nFirst 30 lines:")
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:3}. |{line}|")
