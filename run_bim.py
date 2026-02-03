#!/usr/bin/env python3
"""
Budget Impact Model Runner for IXA-001.

This script demonstrates the BIM functionality and generates
the user-friendly Excel output for payer discussions.

Usage:
    python run_bim.py [--country US|UK|DE|FR|IT|ES] [--scenario conservative|moderate|optimistic]
"""

import argparse
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bim import (
    BIMInputs,
    BIMCalculator,
    BIMResults,
    ExcelGenerator,
    UptakeScenario,
    US_CONFIG,
    UK_CONFIG,
    GERMANY_CONFIG,
    FRANCE_CONFIG,
    ITALY_CONFIG,
    SPAIN_CONFIG,
)


def print_results(results: BIMResults, inputs: BIMInputs):
    """Print formatted BIM results to console."""
    currency = inputs.country.currency_symbol

    print("\n" + "=" * 70)
    print("BUDGET IMPACT MODEL RESULTS")
    print(f"Country: {inputs.country.country_name}")
    print(f"Scenario: {results.scenario.value.capitalize()}")
    print("=" * 70)

    print(f"\n{'POPULATION SIZING':-^70}")
    cascade = inputs.population.get_cascade()
    print(f"  Total Plan Population:     {cascade['total_population']:>15,}")
    print(f"  Adults (18+):              {cascade['adults_18_plus']:>15,}")
    print(f"  With Hypertension:         {cascade['with_hypertension']:>15,}")
    print(f"  Resistant HTN:             {cascade['resistant_hypertension']:>15,}")
    print(f"  Uncontrolled Resistant:    {cascade['uncontrolled_resistant']:>15,}")
    print(f"  Eligible for Treatment:    {cascade['eligible_for_treatment']:>15,}")

    print(f"\n{'KEY METRICS':-^70}")
    print(f"  5-Year Budget Impact:      {currency}{results.total_budget_impact_5yr:>14,.0f}")
    print(f"  Average Annual Impact:     {currency}{results.average_annual_impact:>14,.0f}")
    print(f"  Year 1 PMPM:               {currency}{results.pmpm_impact_year1:>14.2f}")
    print(f"  Year 5 PMPM:               {currency}{results.pmpm_impact_year5:>14.2f}")
    print(f"  Cost per IXA-001 Patient:  {currency}{results.cost_per_ixa_patient:>14,.0f}")
    print(f"  Incremental Cost/Patient:  {currency}{results.incremental_cost_per_ixa_patient:>14,.0f}")

    print(f"\n{'YEAR-BY-YEAR BREAKDOWN':-^70}")
    print(f"  {'Year':<6} {'IXA-001 Pts':>12} {'Current World':>16} {'New World':>16} {'Impact':>14}")
    print("  " + "-" * 64)

    for yr in results.yearly_results:
        print(f"  {yr.year:<6} {yr.patients_ixa_001:>12,} "
              f"{currency}{yr.cost_current_world:>15,.0f} "
              f"{currency}{yr.cost_new_world:>15,.0f} "
              f"{currency}{yr.budget_impact:>13,.0f}")

    print("  " + "-" * 64)
    print(f"  {'TOTAL':<6} {'':<12} {'':<16} {'':<16} "
          f"{currency}{results.total_budget_impact_5yr:>13,.0f}")

    print(f"\n{'MARKET SHARE EVOLUTION':-^70}")
    print(f"  {'Year':<6} {'IXA-001':>10} {'Spiro':>10} {'Other MRA':>12} {'No Tx':>10}")
    print("  " + "-" * 48)

    for yr in results.yearly_results:
        print(f"  {yr.year:<6} {yr.share_ixa_001:>9.0%} {yr.share_spironolactone:>9.0%} "
              f"{yr.share_other_mra:>11.0%} {yr.share_no_treatment:>9.0%}")

    print("\n" + "=" * 70)


def run_scenario_comparison(inputs: BIMInputs):
    """Run and compare all scenarios."""
    calculator = BIMCalculator(inputs)
    all_results = calculator.run_all_scenarios()

    currency = inputs.country.currency_symbol

    print(f"\n{'SCENARIO COMPARISON':-^70}")
    print(f"  {'Metric':<30} {'Conservative':>12} {'Moderate':>12} {'Optimistic':>12}")
    print("  " + "-" * 66)

    for scenario, results in all_results.items():
        name = scenario.value.capitalize()
        if scenario == UptakeScenario.CONSERVATIVE:
            print(f"  {'5-Year Budget Impact':<30} "
                  f"{currency}{results.total_budget_impact_5yr:>11,.0f} ", end="")
        elif scenario == UptakeScenario.MODERATE:
            print(f"{currency}{results.total_budget_impact_5yr:>11,.0f} ", end="")
        else:
            print(f"{currency}{results.total_budget_impact_5yr:>11,.0f}")

    # Print other rows
    metrics = [
        ("Year 5 PMPM", "pmpm_impact_year5", ".2f"),
        ("Year 5 IXA-001 Patients", None, ","),
    ]

    for label, attr, fmt in metrics:
        values = []
        for scenario in [UptakeScenario.CONSERVATIVE, UptakeScenario.MODERATE, UptakeScenario.OPTIMISTIC]:
            results = all_results[scenario]
            if attr:
                value = getattr(results, attr)
            else:
                value = results.yearly_results[-1].patients_ixa_001 if results.yearly_results else 0
            values.append(value)

        if fmt == ".2f":
            print(f"  {label:<30} {currency}{values[0]:>11.2f} {currency}{values[1]:>11.2f} {currency}{values[2]:>11.2f}")
        else:
            print(f"  {label:<30} {values[0]:>12,} {values[1]:>12,} {values[2]:>12,}")

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="IXA-001 Budget Impact Model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_bim.py                          # US, moderate scenario
  python run_bim.py --country UK             # UK market
  python run_bim.py --scenario optimistic    # Optimistic uptake
  python run_bim.py --population 500000      # Custom plan size
        """
    )

    parser.add_argument(
        "--country",
        choices=["US", "UK", "DE", "FR", "IT", "ES"],
        default="US",
        help="Country for analysis (default: US)"
    )

    parser.add_argument(
        "--scenario",
        choices=["conservative", "moderate", "optimistic"],
        default="moderate",
        help="Uptake scenario (default: moderate)"
    )

    parser.add_argument(
        "--population",
        type=int,
        default=1_000_000,
        help="Total plan population (default: 1,000,000)"
    )

    parser.add_argument(
        "--ixa-price",
        type=float,
        help="Annual IXA-001 drug cost (overrides country default)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="IXA001_Budget_Impact_Model.xlsx",
        help="Output Excel filename"
    )

    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="Skip Excel generation (console output only)"
    )

    parser.add_argument(
        "--compare-scenarios",
        action="store_true",
        help="Compare all uptake scenarios"
    )

    args = parser.parse_args()

    # Set up inputs
    inputs = BIMInputs.for_country(args.country)
    inputs.population.total_population = args.population

    # Map scenario string to enum
    scenario_map = {
        "conservative": UptakeScenario.CONSERVATIVE,
        "moderate": UptakeScenario.MODERATE,
        "optimistic": UptakeScenario.OPTIMISTIC,
    }
    inputs.selected_scenario = scenario_map[args.scenario]

    # Override IXA-001 price if specified
    if args.ixa_price:
        inputs.costs.ixa_001_annual = args.ixa_price

    print("\n" + "=" * 70)
    print("IXA-001 BUDGET IMPACT MODEL")
    print("Resistant Hypertension - Payer Analysis Tool")
    print("=" * 70)

    # Run calculation
    calculator = BIMCalculator(inputs)
    results = calculator.calculate()

    # Print results
    print_results(results, inputs)

    # Run scenario comparison if requested
    if args.compare_scenarios:
        run_scenario_comparison(inputs)

    # Generate Excel if not disabled
    if not args.no_excel:
        try:
            output_path = Path(__file__).parent / args.output
            generator = ExcelGenerator(inputs, results)
            generated_path = generator.generate(str(output_path))
            print(f"\nExcel model generated: {generated_path}")
        except ImportError as e:
            print(f"\nWarning: Could not generate Excel file - {e}")
            print("Install openpyxl with: pip install openpyxl")

    # Price threshold analysis
    print(f"\n{'PRICE THRESHOLD ANALYSIS':-^70}")
    budget_neutral_price = calculator.price_threshold_analysis(0)
    if budget_neutral_price:
        currency = inputs.country.currency_symbol
        print(f"  Budget-neutral IXA-001 price: {currency}{budget_neutral_price:,.0f}/year")
        print(f"  (Price at which 5-year budget impact = $0)")

    print("\n" + "=" * 70)
    print("Model run complete.")
    print("=" * 70 + "\n")

    return results


if __name__ == "__main__":
    main()
