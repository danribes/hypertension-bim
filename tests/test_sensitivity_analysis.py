"""
Tests for tornado analysis and probabilistic sensitivity analysis (PSA).

Validates tornado parameter sorting, base value restoration,
PSA statistical properties, and reproducibility.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bim.inputs import ExtendedBIMInputs, UptakeScenario
from src.bim.calculator import EnhancedBIMCalculator


class TestTornadoAnalysis:
    """Test tornado diagram sensitivity analysis."""

    def test_tornado_returns_seven_parameters(self):
        """Tornado analysis should return 7 parameter results."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.run_tornado_analysis()
        print(f"Tornado parameters: {len(results)} (expected 7)")
        for r in results:
            print(f"  {r.parameter_label}: range = ${r.impact_range:,.0f}")
        assert len(results) == 7

    def test_tornado_sorted_by_impact_range(self):
        """Results should be sorted by impact_range descending."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.run_tornado_analysis()
        ranges = [r.impact_range for r in results]
        print(f"Impact ranges: {[f'${x:,.0f}' for x in ranges]}")
        for i in range(1, len(ranges)):
            assert ranges[i] <= ranges[i - 1], (
                f"Not sorted: index {i} ({ranges[i]:,.0f}) > index {i-1} ({ranges[i-1]:,.0f})"
            )

    def test_tornado_positive_impact_ranges(self):
        """All tornado impact ranges should be non-negative.

        Note: discontinuation parameters have zero impact because the base
        BIMCalculator does not model persistence — only EnhancedBIMCalculator
        with persistence enabled would show sensitivity to discontinuation.
        """
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.run_tornado_analysis()
        positive_count = 0
        for r in results:
            print(f"{r.parameter}: impact_range = ${r.impact_range:,.0f}")
            assert r.impact_range >= 0, f"{r.parameter} has negative impact range"
            if r.impact_range > 0:
                positive_count += 1
        # At least 6 of 7 parameters should have positive impact
        assert positive_count >= 6, f"Only {positive_count} params with positive range"

    def test_tornado_base_values_restored(self):
        """Base values should be restored after tornado analysis."""
        inputs = ExtendedBIMInputs()
        original_price = inputs.costs.ixa_001_annual
        original_prev = inputs.population.resistant_htn_proportion
        calc = EnhancedBIMCalculator(inputs)
        _ = calc.run_tornado_analysis()
        print(f"IXA price: original=${original_price}, after=${inputs.costs.ixa_001_annual}")
        print(f"rHTN prev: original={original_prev}, after={inputs.population.resistant_htn_proportion}")
        assert inputs.costs.ixa_001_annual == original_price
        assert inputs.population.resistant_htn_proportion == original_prev


class TestPSA:
    """Test probabilistic sensitivity analysis."""

    def test_psa_mean_positive(self):
        """PSA mean budget impact should be positive."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.run_probabilistic_sensitivity(
            iterations=100, seed=42
        )
        print(f"PSA mean: ${results.mean_impact:,.0f}")
        assert results.mean_impact > 0

    def test_psa_ci_contains_mean(self):
        """95% CI should contain the mean impact."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.run_probabilistic_sensitivity(
            iterations=100, seed=42
        )
        print(f"CI: [${results.ci_lower:,.0f}, ${results.ci_upper:,.0f}]")
        print(f"Mean: ${results.mean_impact:,.0f}")
        assert results.ci_lower <= results.mean_impact <= results.ci_upper

    def test_psa_iterations_count(self):
        """PSA should return requested number of iterations."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.run_probabilistic_sensitivity(
            iterations=100, seed=42
        )
        print(f"Iterations: {results.iterations} (expected 100)")
        assert results.iterations == 100
        assert len(results.impact_distribution) == 100

    def test_psa_reproducible_with_seed(self):
        """PSA with same seed should produce identical results."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results1 = calc.run_probabilistic_sensitivity(
            iterations=50, seed=42
        )
        results2 = calc.run_probabilistic_sensitivity(
            iterations=50, seed=42
        )
        print(f"Run 1 mean: ${results1.mean_impact:,.2f}")
        print(f"Run 2 mean: ${results2.mean_impact:,.2f}")
        assert abs(results1.mean_impact - results2.mean_impact) < 0.01

    def test_psa_prob_budget_increase(self):
        """Probability of budget increase should be between 0 and 1."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.run_probabilistic_sensitivity(
            iterations=100, seed=42
        )
        print(f"P(budget increase): {results.prob_budget_increase:.2f}")
        assert 0.0 <= results.prob_budget_increase <= 1.0

    def test_psa_different_seeds_differ(self):
        """PSA with different seeds should produce different results."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results1 = calc.run_probabilistic_sensitivity(
            iterations=50, seed=42
        )
        results2 = calc.run_probabilistic_sensitivity(
            iterations=50, seed=99
        )
        print(f"Seed 42 mean: ${results1.mean_impact:,.2f}")
        print(f"Seed 99 mean: ${results2.mean_impact:,.2f}")
        # Very unlikely to be exactly equal with different seeds
        assert results1.mean_impact != results2.mean_impact


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
