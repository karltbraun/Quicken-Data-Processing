"""
Processors package for transforming parsed data.

This package contains modules for grouping, aggregating, and preparing
data for reporting.
"""

from .grouper import create_report_groups

__all__ = ["create_report_groups"]
