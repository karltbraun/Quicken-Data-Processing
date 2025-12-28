"""
Test script for visualization functions.

Demonstrates various chart types for analyzing Quicken expense data.
"""

import matplotlib.pyplot as plt

from quicken_parser import (
    parse_quicken_csv,
    plot_category_breakdown,
    plot_hierarchical_view,
    plot_monthly_trends,
    plot_spending_summary,
)


def main():
    # Parse the CSV file
    csv_path = "./data/Expenses 2025-01 2025-11.csv"
    print(f"Parsing: {csv_path}")
    df = parse_quicken_csv(csv_path, verbose=True)

    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")

    # Create output directory if it doesn't exist
    import os

    os.makedirs("./reports/charts", exist_ok=True)

    # 1. Plot top 5 categories monthly trends
    print("\n1. Creating monthly trends chart for top 5 categories...")
    top_5 = df.nlargest(5, "total")["category"].tolist()
    fig1 = plot_monthly_trends(
        df,
        categories=top_5,
        window=3,
        title="Top 5 Expense Categories - Monthly Trends",
        save_path="./reports/charts/monthly_trends_top5.png",
    )
    plt.close(fig1)

    # 2. Plot category breakdown (bar chart)
    print("2. Creating category breakdown bar chart...")
    fig2 = plot_category_breakdown(
        df,
        top_n=15,
        chart_type="bar",
        title="Top 15 Expense Categories by Total",
        save_path="./reports/charts/category_breakdown_bar.png",
    )
    plt.close(fig2)

    # 3. Plot category breakdown (pie chart)
    print("3. Creating category breakdown pie chart...")
    fig3 = plot_category_breakdown(
        df,
        top_n=10,
        chart_type="pie",
        title="Top 10 Expense Categories Distribution",
        save_path="./reports/charts/category_breakdown_pie.png",
    )
    plt.close(fig3)

    # 4. Create comprehensive spending summary
    print("4. Creating comprehensive spending summary...")
    fig4 = plot_spending_summary(
        df, top_n=8, save_path="./reports/charts/spending_summary.png"
    )
    plt.close(fig4)

    # 5. Plot hierarchical view
    print("5. Creating hierarchical view (depth ≤ 2)...")
    fig5 = plot_hierarchical_view(
        df, max_depth=2, save_path="./reports/charts/hierarchical_view.png"
    )
    plt.close(fig5)

    print("\n✅ All charts created successfully!")
    print("📁 Charts saved to: ./reports/charts/")
    print("\nGenerated files:")
    print("  - monthly_trends_top5.png")
    print("  - category_breakdown_bar.png")
    print("  - category_breakdown_pie.png")
    print("  - spending_summary.png")
    print("  - hierarchical_view.png")


if __name__ == "__main__":
    main()
