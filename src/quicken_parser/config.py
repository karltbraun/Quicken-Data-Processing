"""
Configuration management for Quicken expense reporting.

This module provides configuration loading, validation, and access
for the expense reporting system. Configuration is defined in YAML format
with sections for report groups, individual reports, display settings,
and error handling.

Configuration Structure:
    report_groups:      # Groups of related categories
      - name: "Group Name"
        output_name: "file_name"
        categories: ["Cat1", "Cat2"]
        include_group_total: true

    individual_reports: # Single-category reports
      - name: "Report Name"
        output_name: "file_name"
        category: "Category Name"

    display_settings:   # Chart colors and defaults
      colors:
        palette: ["#color1", "#color2"]
      chart_defaults:
        figsize: [14, 8]

    error_handling:     # Missing data behavior
      missing_categories: "fill_zero"  # or "skip", "error"
      partial_groups: "include"        # or "skip", "error"

Author: Karl T. Braun
Version: 0.2.0
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ReportGroup:
    """
    Configuration for a grouped report.

    Groups multiple expense categories into a single report with an
    optional total row. Used for analyzing related expenses together
    (e.g., all medical expenses, all vehicle expenses).

    Attributes:
        name: Display name for the report (used in chart titles)
        output_name: Filename base for output files (no extension)
        categories: List of Quicken category names to include
        include_group_total: Whether to add a summary "Group Total" row

    Example:
        ReportGroup(
            name="Cell Phones (Family)",
            output_name="cell_phones_family",
            categories=["Cell Phone Monthly - FAM", "Other Cell Phone Exp - FAM"],
            include_group_total=True
        )
    """

    name: str
    output_name: str
    categories: List[str]
    include_group_total: bool = True

    def __post_init__(self):
        """Validate report group configuration."""
        if not self.name:
            raise ValueError("Report group must have a name")
        if not self.output_name:
            raise ValueError("Report group must have an output_name")
        if not self.categories:
            raise ValueError(f"Report group '{self.name}' must have categories")


@dataclass
class IndividualReport:
    """
    Configuration for an individual category report.

    Creates a report for a single expense category. Useful for tracking
    specific high-importance or high-variability expenses.

    Attributes:
        name: Display name for the report (used in chart titles)
        output_name: Filename base for output files (no extension)
        category: Quicken category name to report on

    Example:
        IndividualReport(
            name="Groceries",
            output_name="groceries",
            category="Groceries"
        )
    """"

    name: str
    output_name: str
    category: str

    def __post_init__(self):
        """Validate individual report configuration."""
        if not self.name:
            raise ValueError("Individual report must have a name")
        if not self.output_name:
            raise ValueError("Individual report must have an output_name")
        if not self.category:
            raise ValueError(f"Individual report '{self.name}' must have a category")


@dataclass
class ColorSettings:
    """
    Color palette configuration for charts.

    Defines colors used for category lines in charts. Colors are applied
    in order to categories. If more categories than colors, palette cycles.

    Attributes:
        palette: List of hex color codes (e.g., ["#1f77b4", "#2ca02c"])
        group_total_color: Color for "Group Total" rows (default: black)
    """

    palette: List[str]
    group_total_color: str = "#000000"

    def __post_init__(self):
        """Validate color settings."""
        if not self.palette:
            raise ValueError("Color palette cannot be empty")
        # Validate hex colors
        for color in self.palette + [self.group_total_color]:
            if not color.startswith("#") or len(color) != 7:
                raise ValueError(f"Invalid hex color: {color}")


@dataclass
class ChartDefaults:
    """
    Default chart settings and styling.

    Controls the appearance and behavior of generated charts including
    size, line styles, and averaging method.

    Attributes:
        figsize: Chart dimensions as [width, height] in inches
        show_markers: Whether to show data point markers on lines
        line_width: Width of category trend lines
        average_line_style: Style for average lines ("dashed", "dotted", "solid")
        average_type: "expanding" (cumulative) or "rolling" (moving window)
        rolling_window: Window size for rolling average (required if average_type="rolling")
    """

    figsize: List[int] = field(default_factory=lambda: [14, 8])
    show_markers: bool = True
    line_width: int = 2
    average_line_style: str = "dashed"
    average_type: str = "expanding"
    rolling_window: Optional[int] = None

    def __post_init__(self):
        """Validate chart defaults."""
        if len(self.figsize) != 2:
            raise ValueError("figsize must be [width, height]")
        if self.average_type not in ["expanding", "rolling"]:
            raise ValueError("average_type must be 'expanding' or 'rolling'")
        if self.average_type == "rolling" and self.rolling_window is None:
            raise ValueError("rolling_window required when average_type is 'rolling'")
        if self.average_line_style not in ["dashed", "dotted", "solid"]:
            raise ValueError(
                "average_line_style must be 'dashed', 'dotted', or 'solid'"
            )


@dataclass
class DisplaySettings:
    """
    Display configuration for charts.

    Combines color palette and chart default settings into a single
    configuration object.

    Attributes:
        colors: Color palette configuration
        chart_defaults: Default chart sizing and styling
    """

    colors: ColorSettings
    chart_defaults: ChartDefaults


@dataclass
class OutputSettings:
    """
    Output configuration for generated files.

    Specifies where and how to save generated reports.

    Attributes:
        base_dir: Base directory for all outputs (default: "./reports")
        chart_format: Image format for charts ("png", "jpg", "svg", "pdf")
        table_format: Format for data tables ("csv", "xlsx", "html")
        create_summary: Whether to generate summary report (future feature)
    """

    base_dir: str = "./reports"
    chart_format: str = "png"
    table_format: str = "csv"
    create_summary: bool = True

    def __post_init__(self):
        """Validate output settings."""
        if self.chart_format not in ["png", "jpg", "svg", "pdf"]:
            raise ValueError(
                "chart_format must be 'png', 'jpg', 'svg', or 'pdf'"
            )
        if self.table_format not in ["csv", "xlsx", "html"]:
            raise ValueError("table_format must be 'csv', 'xlsx', or 'html'")


@dataclass
class ErrorHandling:
    """
    Error handling configuration.

    Controls how the system handles missing or incomplete data.

    Attributes:
        missing_categories: How to handle categories in config but not in data:
            - "fill_zero": Create row with zero values (default)
            - "skip": Omit category from report
            - "error": Raise ValueError
        partial_groups: How to handle groups where some categories are missing:
            - "include": Include group with available categories (default)
            - "skip": Omit entire group
            - "error": Raise ValueError
    """

    missing_categories: str = "fill_zero"
    partial_groups: str = "include"

    def __post_init__(self):
        """Validate error handling settings."""
        if self.missing_categories not in ["fill_zero", "skip", "error"]:
            raise ValueError(
                "missing_categories must be 'fill_zero', 'skip', or 'error'"
            )
        if self.partial_groups not in ["include", "skip", "error"]:
            raise ValueError("partial_groups must be 'include', 'skip', or 'error'")


class ReportConfig:
    """
    Main configuration class for expense reporting.

    Loads and validates configuration from YAML file, providing typed
    access to all settings. Performs validation on load to catch
    configuration errors early.

    The class parses YAML into typed dataclass objects for:
    - Report groups and individual reports
    - Display settings (colors, chart defaults)
    - Output settings (directories, formats)
    - Error handling behavior

    Example:
        >>> config = ReportConfig('reports_config.yaml')
        >>> groups = config.get_report_groups()
        >>> colors = config.get_display_settings().colors.palette
    """

    def __init__(self, config_path: str):
        """
        Initialize configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Load YAML
        with open(self.config_path, "r") as f:
            self._raw_config = yaml.safe_load(f)

        # Parse and validate
        self._parse_config()
        self.validate()

    def _parse_config(self):
        """Parse raw config dict into typed objects."""
        # Parse report groups
        self._report_groups = [
            ReportGroup(**group)
            for group in self._raw_config.get("report_groups", [])
        ]

        # Parse individual reports
        self._individual_reports = [
            IndividualReport(**report)
            for report in self._raw_config.get("individual_reports", [])
        ]

        # Parse display settings
        display_raw = self._raw_config.get("display_settings", {})
        colors = ColorSettings(**display_raw.get("colors", {}))
        chart_defaults = ChartDefaults(**display_raw.get("chart_defaults", {}))
        self._display_settings = DisplaySettings(
            colors=colors, chart_defaults=chart_defaults
        )

        # Parse output settings
        self._output_settings = OutputSettings(
            **self._raw_config.get("output_settings", {})
        )

        # Parse error handling
        self._error_handling = ErrorHandling(
            **self._raw_config.get("error_handling", {})
        )

    def get_report_groups(self) -> List[ReportGroup]:
        """Get all configured report groups."""
        return self._report_groups

    def get_individual_reports(self) -> List[IndividualReport]:
        """Get all configured individual reports."""
        return self._individual_reports

    def get_display_settings(self) -> DisplaySettings:
        """Get display settings."""
        return self._display_settings

    def get_output_settings(self) -> OutputSettings:
        """Get output settings."""
        return self._output_settings

    def get_error_handling(self) -> ErrorHandling:
        """Get error handling settings."""
        return self._error_handling

    def validate(self) -> bool:
        """
        Validate the entire configuration.

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Check for duplicate output names
        all_output_names = [g.output_name for g in self._report_groups] + [
            r.output_name for r in self._individual_reports
        ]
        if len(all_output_names) != len(set(all_output_names)):
            duplicates = [
                name for name in all_output_names if all_output_names.count(name) > 1
            ]
            raise ValueError(f"Duplicate output_name found: {duplicates}")

        # Validate at least one report is configured
        if not self._report_groups and not self._individual_reports:
            raise ValueError("No reports configured")

        return True

    def get_all_categories(self) -> List[str]:
        """
        Get list of all categories mentioned in config.

        Useful for validation against parsed data.

        Returns:
            Sorted list of unique category names
        """
        categories = set()

        # From report groups
        for group in self._report_groups:
            categories.update(group.categories)

        # From individual reports
        for report in self._individual_reports:
            categories.add(report.category)

        return sorted(categories)

    def __repr__(self) -> str:
        """String representation of config."""
        return (
            f"ReportConfig("
            f"groups={len(self._report_groups)}, "
            f"individual={len(self._individual_reports)}, "
            f"from={self.config_path})"
        )
