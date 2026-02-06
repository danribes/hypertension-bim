"""
Tests for PopulationInputs cascade calculations.

Validates the population eligibility cascade from total population
through epidemiology filters to eligible treatment-seeking patients.
"""

import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bim.inputs import PopulationInputs


class TestDefaultCascade:
    """Test default population cascade: 1M × 0.78 × 0.30 × 0.12 × 0.50 × 0.80."""

    def test_default_eligible_patients(self):
        """Default cascade should yield 11,232 eligible patients."""
        pop = PopulationInputs()
        expected = int(1_000_000 * 0.78 * 0.30 * 0.12 * 0.50 * 0.80)
        print(f"Expected eligible patients: {expected}")
        print(f"Actual eligible patients:   {pop.eligible_patients}")
        assert pop.eligible_patients == expected

    def test_cascade_keys(self):
        """get_cascade() should return all 6 cascade stages."""
        pop = PopulationInputs()
        cascade = pop.get_cascade()
        expected_keys = {
            "total_population",
            "adults_18_plus",
            "with_hypertension",
            "resistant_hypertension",
            "uncontrolled_resistant",
            "eligible_for_treatment",
        }
        print(f"Cascade keys: {set(cascade.keys())}")
        assert set(cascade.keys()) == expected_keys

    def test_cascade_monotonic_decrease(self):
        """Each cascade stage should be <= previous stage."""
        pop = PopulationInputs()
        cascade = pop.get_cascade()
        stages = [
            cascade["total_population"],
            cascade["adults_18_plus"],
            cascade["with_hypertension"],
            cascade["resistant_hypertension"],
            cascade["uncontrolled_resistant"],
            cascade["eligible_for_treatment"],
        ]
        print(f"Cascade stages: {stages}")
        for i in range(1, len(stages)):
            assert stages[i] <= stages[i - 1], (
                f"Stage {i} ({stages[i]}) > stage {i-1} ({stages[i-1]})"
            )

    def test_cascade_eligible_matches_property(self):
        """eligible_for_treatment in cascade should match eligible_patients property."""
        pop = PopulationInputs()
        cascade = pop.get_cascade()
        print(f"Cascade eligible: {cascade['eligible_for_treatment']}")
        print(f"Property eligible: {pop.eligible_patients}")
        # Note: may differ slightly due to intermediate int() truncation in get_cascade
        # vs multiplicative in eligible_patients
        assert abs(cascade["eligible_for_treatment"] - pop.eligible_patients) <= 1


class TestEdgeCases:
    """Test edge cases for population cascade."""

    def test_zero_population(self):
        """Zero total population should yield 0 eligible patients."""
        pop = PopulationInputs(total_population=0)
        print(f"Zero pop eligible: {pop.eligible_patients}")
        assert pop.eligible_patients == 0

    def test_unit_population(self):
        """Single person population should yield 0 (truncated by int())."""
        pop = PopulationInputs(total_population=1)
        print(f"Unit pop eligible: {pop.eligible_patients}")
        assert pop.eligible_patients == 0

    def test_zero_prevalence(self):
        """Zero hypertension prevalence should yield 0 eligible patients."""
        pop = PopulationInputs(hypertension_prevalence=0.0)
        print(f"Zero prevalence eligible: {pop.eligible_patients}")
        assert pop.eligible_patients == 0

    def test_large_us_population(self):
        """330M US population should scale correctly."""
        pop = PopulationInputs(total_population=330_000_000)
        expected = int(330_000_000 * 0.78 * 0.30 * 0.12 * 0.50 * 0.80)
        print(f"US pop expected: {expected}")
        print(f"US pop actual:   {pop.eligible_patients}")
        assert pop.eligible_patients == expected
        # Approx 3.7M
        assert pop.eligible_patients > 3_000_000
        assert pop.eligible_patients < 4_000_000


class TestCustomProportions:
    """Test custom proportion inputs."""

    def test_custom_proportions(self):
        """Custom proportions should be applied correctly."""
        pop = PopulationInputs(
            total_population=500_000,
            adult_proportion=0.80,
            hypertension_prevalence=0.25,
            resistant_htn_proportion=0.10,
            uncontrolled_proportion=0.60,
            treatment_seeking_rate=0.90,
        )
        expected = int(500_000 * 0.80 * 0.25 * 0.10 * 0.60 * 0.90)
        print(f"Custom expected: {expected}")
        print(f"Custom actual:   {pop.eligible_patients}")
        assert pop.eligible_patients == expected

    def test_all_ones_scenario(self):
        """All proportions = 1.0 should yield total_population."""
        pop = PopulationInputs(
            total_population=100_000,
            adult_proportion=1.0,
            hypertension_prevalence=1.0,
            resistant_htn_proportion=1.0,
            uncontrolled_proportion=1.0,
            treatment_seeking_rate=1.0,
        )
        print(f"All-ones eligible: {pop.eligible_patients}")
        assert pop.eligible_patients == 100_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
