#!/usr/bin/env python3
"""
Generate Interactive Budget Impact Model.

Creates a fully formula-driven Excel workbook where:
- Users can modify input cells (yellow highlighting)
- All calculations update automatically via Excel formulas
- No Python or macros required for recalculation

Perfect for face-to-face payer discussions.
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from bim import BIMInputs, UptakeScenario
from bim.excel_interactive import InteractiveExcelGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate Interactive BIM Excel Model"
    )
    parser.add_argument(
        "--country",
        choices=["US", "UK", "DE", "FR", "IT", "ES"],
        default="US",
        help="Country for default values"
    )
    parser.add_argument(
        "--output",
        default="IXA001_BIM_Interactive.xlsx",
        help="Output filename"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("INTERACTIVE BUDGET IMPACT MODEL GENERATOR")
    print("=" * 60)

    # Create inputs with country defaults
    inputs = BIMInputs.for_country(args.country)

    print(f"\nCountry: {inputs.country.country_name}")
    print(f"Currency: {inputs.country.currency}")

    # Generate interactive model
    output_path = Path(__file__).parent / args.output

    print(f"\nGenerating interactive Excel model...")

    generator = InteractiveExcelGenerator(inputs)
    result_path = generator.generate(str(output_path))

    print(f"\nModel saved to: {result_path}")

    print("\n" + "=" * 60)
    print("HOW TO USE THE INTERACTIVE MODEL")
    print("=" * 60)
    print("""
1. Open the Excel file in Microsoft Excel or LibreOffice Calc

2. Go to the 'Inputs' sheet

3. Modify any YELLOW cell to change assumptions:
   - Population size and epidemiology
   - Market shares and displacement
   - Drug costs and monitoring costs
   - Uptake curves by scenario
   - Selected scenario (dropdown)

4. ALL calculations update AUTOMATICALLY - no buttons needed!

5. View results on the 'Results' sheet

KEY FEATURES:
- Scenario dropdown: Switch between Conservative/Moderate/Optimistic
- Real-time charts that update with your inputs
- PMPM calculations for payer discussions
- Year-by-year breakdown

This model is designed for face-to-face payer discussions
where you need to run "what-if" scenarios in real-time.
""")
    print("=" * 60)

    return result_path


if __name__ == "__main__":
    main()
