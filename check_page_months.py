"""
Check which months appear on each page
"""

import pdfplumber

PDF_PATH = "./data/Expenses 2025-01 2025-11.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    for page_num in range(min(5, len(pdf.pages))):  # Check first 5 pages
        page = pdf.pages[page_num]
        text = page.extract_text(layout=True)
        lines = text.split("\n")

        # Find header line with date ranges
        for line in lines:
            if "Category" in line and "/" in line:
                print(f"\nPage {page_num + 1} header:")
                print(line)
                break
