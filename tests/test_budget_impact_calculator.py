"""
Tests for BIMCalculator core calculation logic.

Validates budget impact computation, PMPM metrics, scenario comparisons,
and price threshold analysis.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bim.inputs import BIMInputs, PopulationInputs, UptakeScenario
from src.bim.calculator import BIMCalculator, BIMResults


class TestEligiblePatients:
    """Test eligible patient calculation through calculator."""

    def test_default_eligible_patients(self):
        """Default eligible patients should be 11,232."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        expected = int(1_000_000 * 0.78 * 0.30 * 0.12 * 0.50 * 0.80)
        print(f"Expected eligible: {expected}")
        print(f"Actual eligible:   {results.total_eligible_patients}")
        assert results.total_eligible_patients == expected


class TestYearlyResults:
    """Test year-by-year budget impact results."""

    def test_five_yearly_results(self):
        """Default 5-year horizon should return 5 yearly results."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        print(f"Number of yearly results: {len(results.yearly_results)}")
        assert len(results.yearly_results) == 5

    def test_budget_impact_positive(self):
        """Budget impact should be positive (IXA-001 is more expensive)."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        for yr in results.yearly_results:
            print(f"Year {yr.year}: budget_impact = ${yr.budget_impact:,.2f}")
            assert yr.budget_impact > 0, f"Year {yr.year} should have positive BI"

    def test_budget_impact_increases_with_uptake(self):
        """Budget impact should generally increase as uptake grows."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        impacts = [yr.budget_impact for yr in results.yearly_results]
        print(f"Yearly impacts: {[f'${x:,.0f}' for x in impacts]}")
        # Year-over-year should increase (moderate scenario: 10%→40%)
        for i in range(1, len(impacts)):
            assert impacts[i] >= impacts[i - 1], (
                f"Year {i+1} (${impacts[i]:,.0f}) < Year {i} (${impacts[i-1]:,.0f})"
            )


class TestSummaryMetrics:
    """Test summary-level budget impact metrics."""

    def test_total_equals_sum_of_yearly(self):
        """Total 5-year impact should equal sum of yearly impacts."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        yearly_sum = sum(yr.budget_impact for yr in results.yearly_results)
        print(f"Total 5yr:     ${results.total_budget_impact_5yr:,.2f}")
        print(f"Sum of yearly: ${yearly_sum:,.2f}")
        assert abs(results.total_budget_impact_5yr - yearly_sum) < 0.01

    def test_average_annual_impact(self):
        """Average annual impact should be total / 5."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        expected_avg = results.total_budget_impact_5yr / 5
        print(f"Average annual: ${results.average_annual_impact:,.2f}")
        print(f"Expected avg:   ${expected_avg:,.2f}")
        assert abs(results.average_annual_impact - expected_avg) < 0.01

    def test_pmpm_calculation(self):
        """PMPM should be yearly_impact / total_population / 12."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        yr1_impact = results.yearly_results[0].budget_impact
        expected_pmpm = yr1_impact / inputs.population.total_population / 12
        print(f"PMPM Year 1:  ${results.pmpm_impact_year1:.4f}")
        print(f"Expected:     ${expected_pmpm:.4f}")
        assert abs(results.pmpm_impact_year1 - expected_pmpm) < 0.0001

    def test_current_world_cost_constant(self):
        """Current world cost should be constant across years (no IXA-001)."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        current_costs = [yr.cost_current_world for yr in results.yearly_results]
        print(f"Current world costs: {[f'${x:,.0f}' for x in current_costs]}")
        for cost in current_costs:
            assert cost == current_costs[0], (
                f"Current world cost should be constant: ${cost:,.0f} != ${current_costs[0]:,.0f}"
            )


class TestScenarioComparisons:
    """Test run_all_scenarios() and scenario ordering."""

    def test_run_all_scenarios_returns_three(self):
        """run_all_scenarios() should return results for all 3 scenarios."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        all_results = calc.run_all_scenarios()
        print(f"Number of scenarios: {len(all_results)}")
        assert len(all_results) == 3
        assert UptakeScenario.CONSERVATIVE in all_results
        assert UptakeScenario.MODERATE in all_results
        assert UptakeScenario.OPTIMISTIC in all_results

    def test_scenario_ordering(self):
        """Conservative < Moderate < Optimistic budget impact."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        all_results = calc.run_all_scenarios()
        conservative = all_results[UptakeScenario.CONSERVATIVE].total_budget_impact_5yr
        moderate = all_results[UptakeScenario.MODERATE].total_budget_impact_5yr
        optimistic = all_results[UptakeScenario.OPTIMISTIC].total_budget_impact_5yr
        print(f"Conservative: ${conservative:,.0f}")
        print(f"Moderate:     ${moderate:,.0f}")
        print(f"Optimistic:   ${optimistic:,.0f}")
        assert conservative < moderate < optimistic


class TestPriceThreshold:
    """Test price threshold analysis."""

    def test_price_threshold_below_list(self):
        """Price threshold for zero BI should be below $6,000 list price."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        threshold = calc.price_threshold_analysis(budget_target=0)
        print(f"Price threshold for zero BI: ${threshold:,.2f}")
        print(f"IXA-001 list price:          $6,000")
        assert threshold is not None
        assert threshold < 6000

    def test_inputs_restored_after_threshold(self):
        """Original IXA-001 price should be restored after analysis."""
        inputs = BIMInputs()
        original_price = inputs.costs.ixa_001_annual
        calc = BIMCalculator(inputs)
        _ = calc.price_threshold_analysis(budget_target=0)
        print(f"Original price:  ${original_price}")
        print(f"Restored price:  ${inputs.costs.ixa_001_annual}")
        assert inputs.costs.ixa_001_annual == original_price

    def test_cumulative_impact_monotonic(self):
        """Cumulative budget impact should monotonically increase."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        cumulative = results.get_cumulative_impact()
        print(f"Cumulative: {[f'${x:,.0f}' for x in cumulative]}")
        for i in range(1, len(cumulative)):
            assert cumulative[i] >= cumulative[i - 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
