"""
Test script for configuration loading.

Validates that the YAML config loads correctly and all settings are accessible.
"""

from quicken_parser.config import ReportConfig


def main():
    print("=" * 70)
    print("CONFIGURATION TEST")
    print("=" * 70)

    # Load config
    print("\n[1] Loading configuration...")
    try:
        config = ReportConfig("./reports_config.yaml")
        print(f"✓ Config loaded: {config}")
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return

    # Display report groups
    print("\n[2] Report Groups")
    print("-" * 70)
    groups = config.get_report_groups()
    print(f"Total groups: {len(groups)}\n")
    for i, group in enumerate(groups, 1):
        print(f"{i}. {group.name}")
        print(f"   Output: {group.output_name}")
        print(f"   Categories: {len(group.categories)}")
        print(f"   Include total: {group.include_group_total}")
        for cat in group.categories:
            print(f"      - {cat}")
        print()

    # Display individual reports
    print("\n[3] Individual Reports")
    print("-" * 70)
    individual = config.get_individual_reports()
    print(f"Total individual reports: {len(individual)}\n")
    for i, report in enumerate(individual, 1):
        print(f"{i}. {report.name}")
        print(f"   Output: {report.output_name}")
        print(f"   Category: {report.category}")
        print()

    # Display settings
    print("\n[4] Display Settings")
    print("-" * 70)
    display = config.get_display_settings()
    print(f"Color palette: {len(display.colors.palette)} colors")
    print(f"Group total color: {display.colors.group_total_color}")
    print("\nChart defaults:")
    print(f"  Figure size: {display.chart_defaults.figsize}")
    print(f"  Show markers: {display.chart_defaults.show_markers}")
    print(f"  Line width: {display.chart_defaults.line_width}")
    print(f"  Average type: {display.chart_defaults.average_type}")
    print(
        f"  Average line style: {display.chart_defaults.average_line_style}"
    )

    # Output settings
    print("\n[5] Output Settings")
    print("-" * 70)
    output = config.get_output_settings()
    print(f"Base directory: {output.base_dir}")
    print(f"Chart format: {output.chart_format}")
    print(f"Table format: {output.table_format}")
    print(f"Combined tables: {getattr(output, 'combined_tables', False)}")
    print(f"Create summary: {output.create_summary}")

    # Error handling
    print("\n[6] Error Handling")
    print("-" * 70)
    errors = config.get_error_handling()
    print(f"Missing categories: {errors.missing_categories}")
    print(f"Partial groups: {errors.partial_groups}")

    # All categories
    print("\n[7] All Categories")
    print("-" * 70)
    all_cats = config.get_all_categories()
    print(f"Total unique categories: {len(all_cats)}\n")
    for i, cat in enumerate(all_cats, 1):
        print(f"{i:2d}. {cat}")

    print("\n" + "=" * 70)
    print("✓ Configuration test completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
