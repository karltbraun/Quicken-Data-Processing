"""
Quicken Data Processing

A Python package for parsing Quicken expense reports from CSV format
and generating financial analysis charts and tables.

Features:
- Parse raw Quicken CSV exports with non-standard format
- Extract and normalize expense categories
- Group categories into custom reports via YAML configuration
- Generate time-series charts with trends and averages
- Export data tables as CSV with timestamps
- Handle missing categories gracefully
- Support for hierarchical category visualization

Quick Start:
    # Parse a Quicken export
    from quicken_parser import parse_quicken_csv
    df = parse_quicken_csv('data/expenses.csv')

    # Generate reports from command line
    $ quicken-report --config config.yaml --input data/expenses.csv

    # Or use programmatically
    from quicken_parser.config import ReportConfig
    from quicken_parser.processors import create_report_groups

    config = ReportConfig('config.yaml')
    reports = create_report_groups(df, config)

Author: Karl T. Braun
Version: 1.0
"""

from .charts import (
    plot_category_breakdown,
    plot_hierarchical_view,
    plot_monthly_trends,
    plot_spending_summary,
)
from .csv_parser import QuickenCSVParser, parse_quicken_csv

__version__ = "1.0"
__author__ = "Karl T. Braun"

__all__ = [
    "QuickenCSVParser",
    "parse_quicken_csv",
    "plot_category_breakdown",
    "plot_hierarchical_view",
    "plot_monthly_trends",
    "plot_spending_summary",
]
