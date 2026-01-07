"""
Visualization functions for Quicken expense data.

This module provides charting capabilities for analyzing expense data
parsed from Quicken CSV reports. Charts visualize spending patterns
over time with trend analysis.

Supported Visualizations:
- Monthly trend lines: Track category spending over time
- Moving averages: Identify spending trends (rolling window)
- Expanding averages: Show cumulative average from start
- Category breakdown: Pie/bar charts for composition
- Hierarchical views: Show parent-child category relationships
- Spending summaries: Multi-category comparisons

Charts use a consistent color palette and support:
- Custom titles and sizing
- Automatic legend placement
- Grid lines for readability
- PNG export with configurable DPI
- Special formatting for "Group Total" rows

Author: Karl T. Braun
Version: 1.0
"""

from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set default style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


def plot_monthly_trends(
    df: pd.DataFrame,
    categories: Optional[List[str]] = None,
    window: Optional[int] = 3,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (14, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot monthly expense trends with moving or expanding averages.

    Creates line charts showing:
    - Category totals per month (solid lines)
    - Moving averages or expanding cumulative averages (dashed lines)

    Args:
        df: DataFrame with parsed expense data
        categories: List of category names to plot. If None, plots all categories.
        window: Window size for moving average. If None, uses expanding cumulative average.
                Default: 3 months
        title: Chart title. If None, auto-generates title.
        figsize: Figure size as (width, height)
        save_path: Optional path to save the chart

    Returns:
        matplotlib Figure object

    Example:
        >>> df = parse_quicken_csv('data/expenses.csv')
        >>> fig = plot_monthly_trends(df, categories=['Groceries', 'Gas'])
        >>> plt.show()
    """
    # Get all date columns (contain '/')
    date_cols = [col for col in df.columns if "/" in str(col)]

    if not date_cols:
        raise ValueError("No monthly date columns found in DataFrame")

    # Filter to requested categories or use all
    if categories:
        plot_df = df[df["category"].isin(categories)].copy()
        if plot_df.empty:
            raise ValueError(f"No matching categories found: {categories}")
    else:
        plot_df = df.copy()

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Color palette - use specific colors from aaprompt.md
    base_colors = [
        "#1f77b4",  # Blue
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#ff7f0e",  # Orange
        "#7f7f7f",  # Gray
        "#e377c2",  # Pink
        "#bcbd22",  # Olive
        "#17becf",  # Teal
    ]

    # Extend colors if needed
    colors = (base_colors * ((len(plot_df) // len(base_colors)) + 1))[: len(plot_df)]

    # Plot each category
    for idx, (_, row) in enumerate(plot_df.iterrows()):
        category_name = row["category"]
        values = row[date_cols].values

        # Use black for Group Total, otherwise use the color from palette
        color = "#000000" if category_name == "Group Total" else colors[idx]

        # Convert to positive values for plotting (expenses are negative)
        values = np.abs(values)

        # Plot actual values (solid line)
        ax.plot(
            date_cols,
            values,
            marker="o",
            linewidth=2,
            label=f"{category_name}",
            color=color,
            markersize=6,
        )

        # Calculate and plot average (dashed line)
        if window is None:
            # Expanding cumulative average
            expanding_avg = pd.Series(values).expanding(min_periods=1).mean()
            ax.plot(
                date_cols,
                expanding_avg,
                linestyle="--",
                linewidth=1.5,
                label=f"{category_name} (Expanding Avg)",
                color=color,
                alpha=0.7,
            )
        elif len(values) >= window:
            # Rolling window average
            moving_avg = pd.Series(values).rolling(window=window, min_periods=1).mean()
            ax.plot(
                date_cols,
                moving_avg,
                linestyle="--",
                linewidth=1.5,
                label=f"{category_name} (MA-{window})",
                color=color,
                alpha=0.7,
            )

    # Formatting
    if title:
        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    else:
        ax.set_title(
            f"Monthly Expense Trends ({len(plot_df)} categories)",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )

    ax.set_xlabel("Month", fontsize=12, fontweight="bold")
    ax.set_ylabel("Amount ($)", fontsize=12, fontweight="bold")

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha="right")

    # Add legend
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)

    # Grid
    ax.grid(True, alpha=0.3)

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

    # Tight layout
    plt.tight_layout()

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Chart saved to: {save_path}")

    return fig


def plot_category_breakdown(
    df: pd.DataFrame,
    top_n: int = 10,
    chart_type: str = "bar",
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot expense breakdown by category.

    Args:
        df: DataFrame with parsed expense data
        top_n: Number of top categories to show
        chart_type: 'bar' or 'pie'
        title: Chart title. If None, auto-generates title.
        figsize: Figure size as (width, height)
        save_path: Optional path to save the chart

    Returns:
        matplotlib Figure object

    Example:
        >>> df = parse_quicken_csv('data/expenses.csv')
        >>> fig = plot_category_breakdown(df, top_n=15, chart_type='bar')
        >>> plt.show()
    """
    # Get total column
    if "total" not in df.columns:
        raise ValueError("DataFrame must have 'total' column")

    # Sort by total (most negative = highest expense)
    sorted_df = df.sort_values("total").head(top_n)

    # Convert to positive values
    sorted_df = sorted_df.copy()
    sorted_df["total"] = sorted_df["total"].abs()

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    if chart_type == "bar":
        # Horizontal bar chart
        colors = sns.color_palette("viridis", len(sorted_df))
        bars = ax.barh(sorted_df["category"], sorted_df["total"], color=colors)

        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f"${width:,.0f}",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="bold",
            )

        ax.set_xlabel("Total Expense ($)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Category", fontsize=12, fontweight="bold")
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

    elif chart_type == "pie":
        # Pie chart
        colors = sns.color_palette("husl", len(sorted_df))
        wedges, texts, autotexts = ax.pie(
            sorted_df["total"],
            labels=sorted_df["category"],
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )

        # Improve text readability
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(9)

    else:
        raise ValueError(f"Invalid chart_type: {chart_type}. Use 'bar' or 'pie'.")

    # Title
    if title:
        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    else:
        ax.set_title(
            f"Top {top_n} Expense Categories",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )

    plt.tight_layout()

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Chart saved to: {save_path}")

    return fig


def plot_spending_summary(
    df: pd.DataFrame,
    top_n: int = 10,
    figsize: Tuple[int, int] = (16, 10),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Create a comprehensive spending summary with multiple visualizations.

    Creates a dashboard with:
    - Top categories bar chart
    - Monthly trends for top categories
    - Spending distribution pie chart

    Args:
        df: DataFrame with parsed expense data
        top_n: Number of top categories to show
        figsize: Figure size as (width, height)
        save_path: Optional path to save the chart

    Returns:
        matplotlib Figure object

    Example:
        >>> df = parse_quicken_csv('data/expenses.csv')
        >>> fig = plot_spending_summary(df, top_n=8)
        >>> plt.show()
    """
    # Get date columns and total
    date_cols = [col for col in df.columns if "/" in str(col)]

    if "total" not in df.columns or not date_cols:
        raise ValueError("DataFrame must have 'total' column and date columns")

    # Get top categories
    top_categories = df.nlargest(top_n, "total", keep="all")["category"].tolist()

    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # 1. Top categories bar chart (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    sorted_df = df.sort_values("total").head(top_n)
    colors = sns.color_palette("viridis", len(sorted_df))
    ax1.barh(sorted_df["category"], sorted_df["total"].abs(), color=colors)
    ax1.set_xlabel("Total Expense ($)", fontsize=10, fontweight="bold")
    ax1.set_title(f"Top {top_n} Expense Categories", fontsize=12, fontweight="bold")
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax1.grid(True, alpha=0.3, axis="x")

    # 2. Monthly trends (top right - spans 2 rows)
    ax2 = fig.add_subplot(gs[:, 1])
    colors_trend = sns.color_palette("husl", len(top_categories))

    for idx, category in enumerate(top_categories):
        cat_data = df[df["category"] == category]
        if not cat_data.empty:
            values = cat_data.iloc[0][date_cols].values
            values = np.abs(values)

            # Plot actual values
            ax2.plot(
                date_cols,
                values,
                marker="o",
                linewidth=2,
                label=category,
                color=colors_trend[idx],
                markersize=5,
            )

            # Moving average
            if len(values) >= 3:
                moving_avg = pd.Series(values).rolling(window=3, min_periods=1).mean()
                ax2.plot(
                    date_cols,
                    moving_avg,
                    linestyle="--",
                    linewidth=1.5,
                    color=colors_trend[idx],
                    alpha=0.6,
                )

    ax2.set_xlabel("Month", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Amount ($)", fontsize=10, fontweight="bold")
    ax2.set_title("Monthly Trends (Top Categories)", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=8, loc="best")
    plt.setp(
        ax2.xaxis.get_majorticklabels(),
        rotation=45,
        ha="right",
        fontsize=8,
    )
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax2.grid(True, alpha=0.3)

    # 3. Pie chart (bottom left)
    ax3 = fig.add_subplot(gs[1, 0])
    pie_data = df.nlargest(8, "total", keep="all")
    colors_pie = sns.color_palette("husl", len(pie_data))
    wedges, texts, autotexts = ax3.pie(
        pie_data["total"].abs(),
        labels=pie_data["category"],
        autopct="%1.1f%%",
        colors=colors_pie,
        startangle=90,
    )
    for text in texts:
        text.set_fontsize(8)
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(7)
    ax3.set_title("Expense Distribution", fontsize=12, fontweight="bold")

    # Overall title
    fig.suptitle("Expense Spending Summary", fontsize=16, fontweight="bold", y=0.98)

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Chart saved to: {save_path}")

    return fig


def plot_hierarchical_view(
    df: pd.DataFrame,
    max_depth: int = 2,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot hierarchical view of expenses by indent level.

    Shows parent and child category relationships based on indent_level column.

    Args:
        df: DataFrame with parsed expense data (must have 'indent_level' column)
        max_depth: Maximum indent level to display
        title: Chart title. If None, auto-generates title.
        figsize: Figure size as (width, height)
        save_path: Optional path to save the chart

    Returns:
        matplotlib Figure object
    """
    if "indent_level" not in df.columns or "total" not in df.columns:
        raise ValueError("DataFrame must have 'indent_level' and 'total' columns")

    # Filter by max depth
    filtered_df = df[df["indent_level"] <= max_depth].copy()

    # Sort by indent level and total
    filtered_df = filtered_df.sort_values(["indent_level", "total"])

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Color by indent level
    colors = sns.color_palette("viridis", max_depth + 1)
    color_map = {level: colors[level] for level in range(max_depth + 1)}
    bar_colors = [color_map[level] for level in filtered_df["indent_level"]]

    # Create horizontal bar chart with indentation
    y_positions = range(len(filtered_df))
    bars = ax.barh(y_positions, filtered_df["total"].abs(), color=bar_colors)

    # Add indented category labels
    labels = []
    for _, row in filtered_df.iterrows():
        indent = "  " * row["indent_level"]
        labels.append(f"{indent}{row['category']}")

    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Total Expense ($)", fontsize=12, fontweight="bold")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

    # Title
    if title:
        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    else:
        ax.set_title(
            f"Hierarchical Expense View (Depth ≤ {max_depth})",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )

    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Chart saved to: {save_path}")

    return fig
