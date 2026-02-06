"""
Tests for CostInputs annual cost calculations and country scaling.

Validates per-patient annual costs with and without event offsets,
and country-specific cost multipliers.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bim.inputs import CostInputs, BIMInputs, COUNTRY_CONFIGS


class TestIXA001Costs:
    """Test IXA-001 cost calculations."""

    def test_ixa_with_offsets(self):
        """IXA-001 with offsets: 6000+180+300+100-1200 = $5,380."""
        costs = CostInputs()
        result = costs.get_total_annual_cost("ixa_001", include_offsets=True)
        expected = 6000 + 180 + 300 + 100 - 1200
        print(f"IXA with offsets expected: ${expected}")
        print(f"IXA with offsets actual:   ${result}")
        assert result == expected  # $5,380

    def test_ixa_without_offsets(self):
        """IXA-001 without offsets: 6000+180+300+100 = $6,580."""
        costs = CostInputs()
        result = costs.get_total_annual_cost("ixa_001", include_offsets=False)
        expected = 6000 + 180 + 300 + 100
        print(f"IXA without offsets expected: ${expected}")
        print(f"IXA without offsets actual:   ${result}")
        assert result == expected  # $6,580


class TestSpironolactoneCosts:
    """Test spironolactone cost calculations."""

    def test_spiro_with_offsets(self):
        """Spiro with offsets: 180+240+300+300-800 = $220."""
        costs = CostInputs()
        result = costs.get_total_annual_cost("spironolactone", include_offsets=True)
        expected = 180 + 240 + 300 + 300 - 800
        print(f"Spiro with offsets expected: ${expected}")
        print(f"Spiro with offsets actual:   ${result}")
        assert result == expected  # $220

    def test_spiro_without_offsets(self):
        """Spiro without offsets: 180+240+300+300 = $1,020."""
        costs = CostInputs()
        result = costs.get_total_annual_cost("spironolactone", include_offsets=False)
        expected = 180 + 240 + 300 + 300
        print(f"Spiro without offsets expected: ${expected}")
        print(f"Spiro without offsets actual:   ${result}")
        assert result == expected  # $1,020


class TestOtherMRACosts:
    """Test other MRA cost calculations."""

    def test_other_mra_with_offsets(self):
        """Other MRA with offsets: 1800+240+300+200-600 = $1,940."""
        costs = CostInputs()
        result = costs.get_total_annual_cost("other_mra", include_offsets=True)
        expected = 1800 + 240 + 300 + 200 - 600
        print(f"Other MRA with offsets expected: ${expected}")
        print(f"Other MRA with offsets actual:   ${result}")
        assert result == expected  # $1,940

    def test_other_mra_without_offsets(self):
        """Other MRA without offsets: 1800+240+300+200 = $2,540."""
        costs = CostInputs()
        result = costs.get_total_annual_cost("other_mra", include_offsets=False)
        expected = 1800 + 240 + 300 + 200
        print(f"Other MRA without offsets expected: ${expected}")
        print(f"Other MRA without offsets actual:   ${result}")
        assert result == expected  # $2,540


class TestNoTreatmentCosts:
    """Test no-treatment cost calculations."""

    def test_no_treatment_cost(self):
        """No treatment: 0+120+300+0 = $420 (offsets have no effect)."""
        costs = CostInputs()
        result = costs.get_total_annual_cost("no_treatment", include_offsets=True)
        expected = 0 + 120 + 300 + 0
        print(f"No treatment expected: ${expected}")
        print(f"No treatment actual:   ${result}")
        assert result == expected  # $420

    def test_no_treatment_same_with_or_without_offsets(self):
        """No treatment should be identical with/without offsets."""
        costs = CostInputs()
        with_offsets = costs.get_total_annual_cost("no_treatment", include_offsets=True)
        without_offsets = costs.get_total_annual_cost("no_treatment", include_offsets=False)
        print(f"No treatment with offsets:    ${with_offsets}")
        print(f"No treatment without offsets: ${without_offsets}")
        assert with_offsets == without_offsets


class TestCountryCostScaling:
    """Test country-specific cost multipliers."""

    def test_uk_cost_multiplier(self):
        """UK costs should be 0.40x US costs."""
        uk_inputs = BIMInputs.for_country("UK")
        us_inputs = BIMInputs()
        uk_cost = uk_inputs.costs.get_total_annual_cost("ixa_001")
        us_cost = us_inputs.costs.get_total_annual_cost("ixa_001")
        ratio = uk_cost / us_cost
        print(f"UK IXA cost: ${uk_cost:.2f}, US IXA cost: ${us_cost:.2f}")
        print(f"Ratio: {ratio:.2f} (expected ~0.40)")
        assert abs(ratio - 0.40) < 0.01

    def test_germany_cost_multiplier(self):
        """Germany costs should be 0.50x US costs."""
        de_inputs = BIMInputs.for_country("DE")
        us_inputs = BIMInputs()
        de_cost = de_inputs.costs.get_total_annual_cost("ixa_001")
        us_cost = us_inputs.costs.get_total_annual_cost("ixa_001")
        ratio = de_cost / us_cost
        print(f"DE IXA cost: ${de_cost:.2f}, US IXA cost: ${us_cost:.2f}")
        print(f"Ratio: {ratio:.2f} (expected ~0.50)")
        assert abs(ratio - 0.50) < 0.01

    def test_us_cost_multiplier_is_one(self):
        """US cost multiplier should be 1.0 (no scaling)."""
        us_config = COUNTRY_CONFIGS["US"]
        print(f"US cost multiplier: {us_config.cost_multiplier}")
        assert us_config.cost_multiplier == 1.0

    def test_invalid_country_defaults_to_us(self):
        """Invalid country code should default to US configuration."""
        invalid_inputs = BIMInputs.for_country("XX")
        us_inputs = BIMInputs.for_country("US")
        invalid_cost = invalid_inputs.costs.get_total_annual_cost("ixa_001")
        us_cost = us_inputs.costs.get_total_annual_cost("ixa_001")
        print(f"Invalid country cost: ${invalid_cost:.2f}")
        print(f"US cost:              ${us_cost:.2f}")
        assert invalid_cost == us_cost


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
