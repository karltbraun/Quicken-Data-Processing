"""
Test script for generating charts based on aaprompt.md requirements.

Generates individual and grouped line graphs with:
- Solid lines for monthly expenses
- Dashed lines for expanding cumulative averages
- $0 values for missing categories (no errors)
"""

import os

import matplotlib.pyplot as plt
import pandas as pd

from quicken_parser import plot_monthly_trends


def get_or_create_zero_series(df, category_name, month_columns):
    """Get category data or create a zero-filled series if category doesn't exist."""
    matching = df[df["category"] == category_name]
    if matching.empty:
        print(f"  ⚠️  Category '{category_name}' not found - using $0 for all months")
        zero_data = {col: 0.0 for col in month_columns}
        return pd.Series(zero_data)
    return matching.iloc[0][month_columns]


def main():
    # Read the already-parsed CSV file
    csv_path = "./reports/Expense_Report_20250101_-_20251130.csv"
    print(f"Reading parsed data: {csv_path}")
    df = pd.read_csv(csv_path)

    print(f"\nDataFrame shape: {df.shape}")
    print(f"Total categories: {len(df)}")

    # Get month columns (exclude category, indent_level, total, monthly_average)
    month_columns = [
        col
        for col in df.columns
        if col not in ["category", "indent_level", "total", "monthly_average"]
    ]
    print(f"Month columns: {month_columns}")

    # Create output directory
    os.makedirs("./reports/charts", exist_ok=True)

    # Individual Line Graphs (2 categories per aaprompt.md)
    print("\n" + "=" * 60)
    print("INDIVIDUAL LINE GRAPHS")
    print("=" * 60)

    individual_categories = [
        "Groceries",
        "Internet - FAM",
    ]

    for i, category in enumerate(individual_categories, 1):
        print(f"\n{i}. Creating chart for: {category}")
        series = get_or_create_zero_series(df, category, month_columns)

        # Create temporary dataframe for this category
        temp_df = pd.DataFrame(
            {
                "category": [category],
                "indent_level": [0],
                **{col: [series[col]] for col in month_columns},
            }
        )

        fig = plot_monthly_trends(
            temp_df,
            categories=[category],
            window=None,  # Use expanding cumulative average
            title=f"{category} - Monthly Expenses",
            save_path=f"./reports/charts/individual_{i:02d}_{category.replace(' ', '_').replace('/', '_')}.png",
        )
        plt.close(fig)

    # Grouped Line Graphs
    print("\n" + "=" * 60)
    print("GROUPED LINE GRAPHS")
    print("=" * 60)

    groups = [
        {
            "name": "Cell Phones (Family)",
            "categories": [
                "Cell Phone Monthly - FAM",
                "Other Cell Phone Exp - FAM",
                "Reimb Cell Phones - FAM",
            ],
        },
        {
            "name": "Medicare Expenses - KTB",
            "categories": [
                "IRMAA Part B - KTB",
                "Regular Part B - KTB",
                "IRMAA Part D - KTB",
                "Regular Part D - KTB",
                "Supplemental Part G - KTB",
            ],
        },
        {
            "name": "Medicare Expenses - MES",
            "categories": [
                "IRMAA Part B - MES",
                "Regular Part B - MES",
                "IRMAA Part D - MES",
                "Regular Part D - MES",
                "Supplemental Part G - MES",
            ],
        },
        {
            "name": "Medical Expenses",
            "categories": [
                "Office Visit - DC",
                "Procedures - DC",
                "Office - Dental",
                "Supplies - Dental",
                "Hospital, Surgery, etc",
                "Med Supplies - MD",
                "Misc - MD",
                "Office Visit - MD",
                "Tests and Procedures - MD",
                "Office Visit - PT",
                "Procedures - PT",
            ],
        },
        {
            "name": "Subscriptions (Family)",
            "categories": [
                "App Subs - FAM",
                "Audio Subs - FAM",
                "NewsAndMags - FAM",
                "Video Subs - FAM",
            ],
        },
        {
            "name": "Utilities",
            "categories": [
                "GasElecOnly",
                "WaterOnly",
            ],
        },
        {
            "name": "Night Out",
            "categories": [
                "Family Night Out",
                "K&L Night Out",
            ],
        },
        {
            "name": "Household Goods",
            "categories": [
                "Consumables - HHG",
                "Fixed - HHG",
            ],
        },
        {
            "name": "Vehicles",
            "categories": [
                "Fuel Veh",
                "Actual Veh Ins",
                "Car Wash",
                "Maint - Veh",
            ],
        },
    ]

    for group_num, group in enumerate(groups, 1):
        print(f"\n{group_num}. Creating grouped chart: {group['name']}")
        print(f"   Categories: {len(group['categories'])}")

        # Build temporary dataframe with all categories (real or $0)
        group_data = []
        monthly_totals = {col: 0.0 for col in month_columns}

        for category in group["categories"]:
            series = get_or_create_zero_series(df, category, month_columns)
            row = {
                "category": category,
                "indent_level": 0,
                **{col: series[col] for col in month_columns},
            }
            group_data.append(row)

            # Accumulate totals for each month
            for col in month_columns:
                monthly_totals[col] += series[col]

        # Add Group Total row
        group_total_row = {
            "category": "Group Total",
            "indent_level": 0,
            **monthly_totals,
        }
        group_data.append(group_total_row)

        temp_df = pd.DataFrame(group_data)

        # Include Group Total in the categories list
        all_categories = group["categories"] + ["Group Total"]

        fig = plot_monthly_trends(
            temp_df,
            categories=all_categories,
            window=None,  # Use expanding cumulative average
            title=f"{group['name']} - Monthly Expenses",
            save_path=f"./reports/charts/group_{group_num:02d}_{group['name'].replace(' ', '_').replace('/', '_')}.png",
        )
        plt.close(fig)

    print("\n" + "=" * 60)
    print("✅ All charts created successfully!")
    print("=" * 60)
    print("📁 Charts saved to: ./reports/charts/")
    print(f"\nGenerated {len(individual_categories)} individual charts")
    print(f"Generated {len(groups)} grouped charts")


if __name__ == "__main__":
    main()
