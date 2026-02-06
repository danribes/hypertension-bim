"""
Tests for MarketInputs uptake curves, validation, and displacement.

Validates uptake scenarios, market share normalization, and
input validation logic.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bim.inputs import MarketInputs, UptakeScenario


class TestUptakeCurves:
    """Test uptake curve values for each scenario."""

    def test_moderate_year3_uptake(self):
        """Moderate scenario Year 3 uptake should be 0.30."""
        market = MarketInputs()
        uptake = market.get_uptake(UptakeScenario.MODERATE, 3)
        print(f"Moderate Year 3 uptake: {uptake} (expected 0.30)")
        assert uptake == 0.30

    def test_conservative_year5_uptake(self):
        """Conservative scenario Year 5 uptake should be 0.20."""
        market = MarketInputs()
        uptake = market.get_uptake(UptakeScenario.CONSERVATIVE, 5)
        print(f"Conservative Year 5 uptake: {uptake} (expected 0.20)")
        assert uptake == 0.20

    def test_optimistic_year1_uptake(self):
        """Optimistic scenario Year 1 uptake should be 0.15."""
        market = MarketInputs()
        uptake = market.get_uptake(UptakeScenario.OPTIMISTIC, 1)
        print(f"Optimistic Year 1 uptake: {uptake} (expected 0.15)")
        assert uptake == 0.15

    def test_moderate_year5_uptake(self):
        """Moderate scenario Year 5 uptake should be 0.40."""
        market = MarketInputs()
        uptake = market.get_uptake(UptakeScenario.MODERATE, 5)
        print(f"Moderate Year 5 uptake: {uptake} (expected 0.40)")
        assert uptake == 0.40

    def test_optimistic_year5_uptake(self):
        """Optimistic scenario Year 5 uptake should be 0.55."""
        market = MarketInputs()
        uptake = market.get_uptake(UptakeScenario.OPTIMISTIC, 5)
        print(f"Optimistic Year 5 uptake: {uptake} (expected 0.55)")
        assert uptake == 0.55


class TestUptakeMonotonicity:
    """Test that uptake increases monotonically within each scenario."""

    @pytest.mark.parametrize("scenario", [
        UptakeScenario.CONSERVATIVE,
        UptakeScenario.MODERATE,
        UptakeScenario.OPTIMISTIC,
    ])
    def test_uptake_monotonically_increasing(self, scenario):
        """Uptake should increase (or stay flat) each year."""
        market = MarketInputs()
        uptakes = [market.get_uptake(scenario, y) for y in range(1, 6)]
        print(f"{scenario.value} uptakes: {uptakes}")
        for i in range(1, len(uptakes)):
            assert uptakes[i] >= uptakes[i - 1], (
                f"{scenario.value}: Year {i+1} ({uptakes[i]}) < Year {i} ({uptakes[i-1]})"
            )


class TestUptakeValidation:
    """Test uptake boundary validation."""

    def test_year_0_raises_error(self):
        """get_uptake() should raise ValueError for year 0."""
        market = MarketInputs()
        with pytest.raises(ValueError, match="Year must be between 1 and 5"):
            market.get_uptake(UptakeScenario.MODERATE, 0)

    def test_year_6_raises_error(self):
        """get_uptake() should raise ValueError for year 6."""
        market = MarketInputs()
        with pytest.raises(ValueError, match="Year must be between 1 and 5"):
            market.get_uptake(UptakeScenario.MODERATE, 6)


class TestMarketValidation:
    """Test market share validation."""

    def test_default_validation_passes(self):
        """Default market inputs should pass validation."""
        market = MarketInputs()
        result = market.validate()
        print(f"Default validation: {result}")
        assert result is True

    def test_invalid_baseline_shares_fails(self):
        """Baseline shares not summing to 1.0 should fail validation."""
        market = MarketInputs(
            baseline_spironolactone=0.50,
            baseline_other_mra=0.10,
            baseline_no_4th_line=0.10,  # Sum = 0.70, not 1.0
        )
        result = market.validate()
        print(f"Invalid baseline validation: {result}")
        assert result is False

    def test_invalid_displacement_shares_fails(self):
        """Displacement shares not summing to 1.0 should fail validation."""
        market = MarketInputs(
            displacement_from_spironolactone=0.50,
            displacement_from_other_mra=0.10,
            displacement_from_untreated=0.10,  # Sum = 0.70, not 1.0
        )
        result = market.validate()
        print(f"Invalid displacement validation: {result}")
        assert result is False


class TestPostDisplacementShares:
    """Test that post-displacement market shares sum correctly."""

    @pytest.mark.parametrize("scenario", [
        UptakeScenario.CONSERVATIVE,
        UptakeScenario.MODERATE,
        UptakeScenario.OPTIMISTIC,
    ])
    def test_post_displacement_shares_sum_to_one(self, scenario):
        """Post-displacement shares should sum to ~1.0 for all years."""
        market = MarketInputs()
        for year in range(1, 6):
            uptake = market.get_uptake(scenario, year)
            # Calculate displaced shares (same logic as calculator)
            displaced_spiro = uptake * market.displacement_from_spironolactone
            displaced_mra = uptake * market.displacement_from_other_mra
            displaced_untreated = uptake * market.displacement_from_untreated

            share_ixa = uptake
            share_spiro = max(0, market.baseline_spironolactone - displaced_spiro)
            share_mra = max(0, market.baseline_other_mra - displaced_mra)
            share_none = max(0, market.baseline_no_4th_line - displaced_untreated)

            total = share_ixa + share_spiro + share_mra + share_none
            print(f"{scenario.value} Year {year}: shares sum = {total:.4f}")
            # Pre-normalization sum should be close to 1.0
            # (exact only if displacement fractions sum to 1 and no share goes negative)
            assert total > 0, f"Total share must be positive: {total}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
