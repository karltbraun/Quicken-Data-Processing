"""
Quicken Data Processing

A Python package for parsing Quicken expense reports (PDF and CSV formats)
and generating financial analysis charts.

Author: Karl T. Braun
Version: 0.1.0
"""

from .charts import (
    plot_category_breakdown,
    plot_hierarchical_view,
    plot_monthly_trends,
    plot_spending_summary,
)
from .csv_parser import QuickenCSVParser, parse_quicken_csv
from .pdf_parser import (
    QuickenPDFParser,
    extract_raw_text,
    parse_quicken_pdf,
)

__version__ = "0.1.0"
__author__ = "Karl T. Braun"

__all__ = [
    "QuickenPDFParser",
    "parse_quicken_pdf",
    "extract_raw_text",
    "QuickenCSVParser",
    "parse_quicken_csv",
]
