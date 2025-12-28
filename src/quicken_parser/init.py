"""
Quicken Parser Package

A Python package for parsing Quicken expense reports and generating
financial analysis visualizations.

Author: Karl T. Braun
Version: 0.1.0 (Alpha)
"""

__version__ = "0.1.0"
__author__ = "Karl T. Braun"

from .pdf_parser import (
    QuickenPDFParser,
    extract_raw_text,
    parse_quicken_pdf,
)

__all__ = [
    "QuickenPDFParser",
    "parse_quicken_pdf",
    "extract_raw_text",
]
