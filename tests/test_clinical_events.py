"""
Tests for ClinicalEventRates and EventCosts.

Validates event rate lookups, cost structures, and event
calculation logic in the enhanced calculator.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bim.inputs import (
    ClinicalEventRates,
    EventCosts,
    EventType,
    ExtendedBIMInputs,
    UptakeScenario,
    SubgroupType,
)
from src.bim.calculator import EnhancedBIMCalculator


class TestClinicalEventRates:
    """Test event rate lookups."""

    def test_ixa_stroke_rate(self):
        """IXA-001 stroke rate should be 8.0 per 1,000."""
        rates = ClinicalEventRates()
        result = rates.get_rate(EventType.STROKE, "ixa_001")
        print(f"IXA stroke rate: {result} per 1,000 (expected 8.0)")
        assert result == 8.0

    def test_ixa_rates_lower_than_no_treatment(self):
        """IXA-001 rates should be lower than no_treatment for all events."""
        rates = ClinicalEventRates()
        for event in EventType:
            ixa_rate = rates.get_rate(event, "ixa_001")
            no_tx_rate = rates.get_rate(event, "no_treatment")
            print(f"{event.value}: IXA={ixa_rate}, no_tx={no_tx_rate}")
            assert ixa_rate < no_tx_rate, (
                f"{event.value}: IXA rate ({ixa_rate}) >= no_treatment ({no_tx_rate})"
            )

    def test_unknown_treatment_returns_zero(self):
        """Unknown treatment should return 0.0 (via getattr default)."""
        rates = ClinicalEventRates()
        result = rates.get_rate(EventType.STROKE, "unknown_drug")
        print(f"Unknown treatment stroke rate: {result} (expected 0.0)")
        assert result == 0.0


class TestEventCosts:
    """Test event cost lookups."""

    def test_stroke_costs(self):
        """Stroke costs should be ($35,000 acute, $8,000 followup)."""
        costs = EventCosts()
        acute, followup = costs.get_costs(EventType.STROKE)
        print(f"Stroke acute: ${acute:,.0f}, followup: ${followup:,.0f}")
        assert acute == 35_000
        assert followup == 8_000

    def test_esrd_highest_followup(self):
        """ESRD should have highest annual followup cost ($90,000)."""
        costs = EventCosts()
        esrd_acute, esrd_followup = costs.get_costs(EventType.ESRD)
        print(f"ESRD followup: ${esrd_followup:,.0f}")
        # Check ESRD followup is highest among all event types
        for event in EventType:
            _, followup = costs.get_costs(event)
            assert esrd_followup >= followup, (
                f"ESRD followup (${esrd_followup:,.0f}) < {event.value} (${followup:,.0f})"
            )

    def test_death_events_zero_followup(self):
        """Death events should have zero annual followup cost."""
        costs = EventCosts()
        for event in [EventType.CV_DEATH, EventType.ALL_CAUSE_DEATH]:
            _, followup = costs.get_costs(event)
            print(f"{event.value} followup: ${followup} (expected $0)")
            assert followup == 0.0


class TestEventCalculation:
    """Test event calculation in enhanced calculator."""

    def test_events_avoided_positive(self):
        """Events avoided should be > 0 for non-death events."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.calculate_full(
            include_subgroups=False,
            include_persistence=False,
            include_extended_horizon=False,
        )
        event_results = results.event_results
        assert event_results is not None
        for event, avoided in event_results.events_avoided.items():
            if event not in (EventType.CV_DEATH, EventType.ALL_CAUSE_DEATH):
                print(f"{event.value}: {avoided:.2f} events avoided")
                assert avoided > 0, f"{event.value} should have positive events avoided"

    def test_death_events_skipped(self):
        """Death events should be skipped in event calculation."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.calculate_full(
            include_subgroups=False,
            include_persistence=False,
            include_extended_horizon=False,
        )
        event_results = results.event_results
        # CV_DEATH and ALL_CAUSE_DEATH should have 0 events avoided
        for death_event in [EventType.CV_DEATH, EventType.ALL_CAUSE_DEATH]:
            avoided = event_results.events_avoided.get(death_event, 0.0)
            print(f"{death_event.value}: {avoided} events avoided (expected 0)")
            assert avoided == 0.0

    def test_total_costs_avoided_positive(self):
        """Total costs avoided from events should be > 0."""
        inputs = ExtendedBIMInputs()
        calc = EnhancedBIMCalculator(inputs)
        results = calc.calculate_full(
            include_subgroups=False,
            include_persistence=False,
            include_extended_horizon=False,
        )
        total_costs_avoided = results.event_results.total_costs_avoided
        print(f"Total costs avoided: ${total_costs_avoided:,.2f}")
        assert total_costs_avoided > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
