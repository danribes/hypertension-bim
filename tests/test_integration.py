"""
End-to-end integration tests for the BIM model.

Tests complete workflows from input validation through calculation
to result extraction, including country comparisons and extended analysis.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bim.inputs import (
    BIMInputs,
    ExtendedBIMInputs,
    PopulationInputs,
    UptakeScenario,
    SubgroupType,
)
from src.bim.calculator import BIMCalculator, EnhancedBIMCalculator


class TestInputValidation:
    """Test input validation workflows."""

    def test_default_inputs_valid(self):
        """Default BIMInputs should pass validation with no errors."""
        inputs = BIMInputs()
        errors = inputs.validate()
        print(f"Validation errors: {errors}")
        assert errors == []

    def test_invalid_population_caught(self):
        """Zero/negative population should produce validation error."""
        inputs = BIMInputs()
        inputs.population.total_population = 0
        errors = inputs.validate()
        print(f"Validation errors: {errors}")
        assert len(errors) > 0
        assert any("population" in e.lower() for e in errors)

    def test_invalid_time_horizon_caught(self):
        """Time horizon outside 1-5 should produce validation error."""
        inputs = BIMInputs()
        inputs.time_horizon_years = 10
        errors = inputs.validate()
        print(f"Validation errors: {errors}")
        assert len(errors) > 0
        assert any("horizon" in e.lower() for e in errors)

    def test_extended_inputs_valid(self):
        """Default ExtendedBIMInputs should pass validation."""
        inputs = ExtendedBIMInputs()
        errors = inputs.validate()
        print(f"Extended validation errors: {errors}")
        assert errors == []


class TestBasicCalculation:
    """Test basic end-to-end calculation workflow."""

    def test_calculate_returns_correct_structure(self):
        """calculate() should return BIMResults with expected attributes."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        assert results.total_eligible_patients > 0
        assert results.total_budget_impact_5yr > 0
        assert results.average_annual_impact > 0
        assert results.pmpm_impact_year1 > 0
        assert results.pmpm_impact_year5 > 0
        assert len(results.yearly_results) == 5
        print(f"BI 5yr: ${results.total_budget_impact_5yr:,.0f}")
        print(f"PMPM Y1: ${results.pmpm_impact_year1:.4f}")
        print(f"PMPM Y5: ${results.pmpm_impact_year5:.4f}")

    def test_positive_budget_impact(self):
        """Budget impact should be positive (IXA costs more than SoC)."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        print(f"Total 5yr BI: ${results.total_budget_impact_5yr:,.0f}")
        assert results.total_budget_impact_5yr > 0


class TestEnhancedCalculation:
    """Test enhanced calculator workflows."""

    def test_calculate_full_with_events(self):
        """calculate_full() should include event results."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.calculate_full(
            include_subgroups=False,
            include_persistence=True,
            include_events=True,
            include_extended_horizon=True,
        )
        assert results.base_results is not None
        assert results.event_results is not None
        assert results.persistence_results is not None
        assert len(results.extended_yearly_results) == 10
        print(f"Base BI: ${results.base_results.total_budget_impact_5yr:,.0f}")
        print(f"Events avoided (total costs): ${results.event_results.total_costs_avoided:,.0f}")
        print(f"Extended 10yr BI: ${results.extended_total_impact:,.0f}")

    def test_calculate_full_with_subgroups(self):
        """calculate_full() with subgroups should return stratified results."""
        inputs = ExtendedBIMInputs()
        inputs.selected_subgroup_types = [SubgroupType.PRIMARY_ALDOSTERONISM]
        calc = EnhancedBIMCalculator(inputs)
        results = calc.calculate_full(
            include_subgroups=True,
            include_persistence=False,
            include_events=False,
            include_extended_horizon=False,
        )
        assert SubgroupType.PRIMARY_ALDOSTERONISM in results.subgroup_results
        pa_results = results.subgroup_results[SubgroupType.PRIMARY_ALDOSTERONISM]
        assert len(pa_results) == 2  # No PA, With PA
        for sg in pa_results:
            print(f"  {sg.subgroup_name}: BI=${sg.budget_impact_5yr:,.0f}, "
                  f"per_patient=${sg.budget_impact_per_patient:,.0f}")

    def test_extended_horizon_ten_years(self):
        """Extended horizon should project 10 yearly results."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.calculate_full(
            include_subgroups=False,
            include_persistence=False,
            include_events=False,
            include_extended_horizon=True,
        )
        print(f"Extended yearly results: {len(results.extended_yearly_results)}")
        assert len(results.extended_yearly_results) == 10
        assert results.extended_total_impact > 0


class TestCountryComparison:
    """Test cross-country budget impact."""

    def test_uk_bi_less_than_us(self):
        """UK budget impact should be less than US (0.40x cost multiplier)."""
        us_inputs = BIMInputs()
        uk_inputs = BIMInputs.for_country("UK")
        us_calc = BIMCalculator(us_inputs)
        uk_calc = BIMCalculator(uk_inputs)
        us_results = us_calc.calculate()
        uk_results = uk_calc.calculate()
        print(f"US 5yr BI: ${us_results.total_budget_impact_5yr:,.0f}")
        print(f"UK 5yr BI: ${uk_results.total_budget_impact_5yr:,.0f}")
        assert uk_results.total_budget_impact_5yr < us_results.total_budget_impact_5yr


class TestResultsOutput:
    """Test result output methods."""

    def test_cumulative_impact_monotonic(self):
        """Cumulative budget impact should monotonically increase."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        cumulative = results.get_cumulative_impact()
        print(f"Cumulative: {[f'${x:,.0f}' for x in cumulative]}")
        assert len(cumulative) == 5
        for i in range(1, len(cumulative)):
            assert cumulative[i] >= cumulative[i - 1], (
                f"Year {i+1} cumulative (${cumulative[i]:,.0f}) < "
                f"Year {i} (${cumulative[i-1]:,.0f})"
            )

    def test_to_summary_dict_keys(self):
        """to_summary_dict() should have all expected keys."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        summary = results.to_summary_dict()
        expected_keys = {
            "scenario",
            "eligible_patients",
            "total_5yr_impact",
            "average_annual_impact",
            "pmpm_year1",
            "pmpm_year5",
            "cost_per_ixa_patient",
            "incremental_cost_per_patient",
            "yearly_impacts",
        }
        print(f"Summary keys: {set(summary.keys())}")
        assert set(summary.keys()) == expected_keys

    def test_summary_dict_values_consistent(self):
        """Summary dict values should be consistent with results object."""
        inputs = BIMInputs()
        calc = BIMCalculator(inputs)
        results = calc.calculate()
        summary = results.to_summary_dict()
        print(f"Summary 5yr: ${summary['total_5yr_impact']:,.0f}")
        print(f"Results 5yr: ${results.total_budget_impact_5yr:,.0f}")
        assert summary["total_5yr_impact"] == results.total_budget_impact_5yr
        assert summary["eligible_patients"] == results.total_eligible_patients
        assert summary["scenario"] == results.scenario.value
        assert len(summary["yearly_impacts"]) == 5

    def test_extended_get_summary(self):
        """ExtendedBIMResults.get_summary() should include base + extended data."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.calculate_full(
            include_subgroups=False,
            include_persistence=False,
            include_events=True,
            include_extended_horizon=True,
        )
        summary = results.get_summary()
        print(f"Extended summary keys: {list(summary.keys())}")
        assert "total_5yr_impact" in summary
        assert "extended_10yr_impact" in summary
        assert "total_events_avoided" in summary
        assert "total_event_costs_avoided" in summary
        assert summary["extended_10yr_impact"] > summary["total_5yr_impact"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
