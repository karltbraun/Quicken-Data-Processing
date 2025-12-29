"""
Quicken Data Processing

A Python package for parsing Quicken expense reports from CSV format
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

__version__ = "0.1.0"
__author__ = "Karl T. Braun"

__all__ = [
    "QuickenCSVParser",
    "parse_quicken_csv",
    "plot_category_breakdown",
    "plot_hierarchical_view",
    "plot_monthly_trends",
    "plot_spending_summary",
]
