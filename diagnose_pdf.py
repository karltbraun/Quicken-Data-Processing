"""
Diagnostic script to understand the PDF structure
"""

import pdfplumber

PDF_PATH = "./data/Expenses 2025-01 2025-11.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    print("\n" + "=" * 70)

    # Check first page
    page = pdf.pages[0]

    print("PAGE 1 ANALYSIS")
    print("=" * 70)

    # Try different table extraction settings
    print("\n[1] Default table extraction:")
    tables = page.extract_tables()
    print(f"   Tables found: {len(tables)}")

    print("\n[2] With explicit table settings:")
    tables_explicit = page.extract_tables(
        {"vertical_strategy": "lines", "horizontal_strategy": "lines"}
    )
    print(f"   Tables found: {len(tables_explicit)}")

    print("\n[3] With text-based strategy:")
    tables_text = page.extract_tables(
        {"vertical_strategy": "text", "horizontal_strategy": "text"}
    )
    print(f"   Tables found: {len(tables_text)}")

    print("\n[4] Check for lines/rectangles in PDF:")
    print(f"   Horizontal lines: {len(page.lines)}")
    print(f"   Vertical lines: {len(page.vertical_edges)}")
    print(f"   Rectangles: {len(page.rects)}")

    print("\n[5] Extract text with layout preservation:")
    text_with_layout = page.extract_text(layout=True)
    print("   First 1000 chars with layout:")
    print(text_with_layout[:1000])

    print("\n[6] Check words and their positions:")
    words = page.extract_words()
    print(f"   Total words on page 1: {len(words)}")
    print("   First 10 words with positions:")
    for i, word in enumerate(words[:10]):
        print(
            f"      {i + 1}. '{word['text']}' at x={word['x0']:.1f}, y={word['top']:.1f}"
        )
