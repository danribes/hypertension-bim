"""
Budget Impact Model Calculator.

Core calculation engine for the BIM that computes:
- Year-by-year budget impact
- Treatment mix changes
- Per-member-per-month (PMPM) impact
- Scenario comparisons
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np

from .inputs import (
    BIMInputs,
    UptakeScenario,
    MarketInputs,
    ExtendedBIMInputs,
    EventType,
    SubgroupType,
    SubgroupParameters,
    ClinicalEventRates,
    EventCosts,
)
import copy
from scipy import stats


@dataclass
class YearlyResults:
    """Results for a single year."""

    year: int

    # Patient counts by treatment
    patients_ixa_001: int = 0
    patients_spironolactone: int = 0
    patients_other_mra: int = 0
    patients_no_treatment: int = 0

    # Costs - Current World (no IXA-001)
    cost_current_world: float = 0.0

    # Costs - New World (with IXA-001)
    cost_new_world: float = 0.0

    # Budget impact
    budget_impact: float = 0.0

    # Cost breakdown by treatment (New World)
    cost_ixa_001: float = 0.0
    cost_spironolactone: float = 0.0
    cost_other_mra: float = 0.0
    cost_no_treatment: float = 0.0

    # Market shares (New World)
    share_ixa_001: float = 0.0
    share_spironolactone: float = 0.0
    share_other_mra: float = 0.0
    share_no_treatment: float = 0.0


@dataclass
class BIMResults:
    """Complete BIM results container."""

    # Inputs used
    inputs: BIMInputs = None

    # Summary metrics
    total_eligible_patients: int = 0
    total_budget_impact_5yr: float = 0.0
    average_annual_impact: float = 0.0
    pmpm_impact_year1: float = 0.0
    pmpm_impact_year5: float = 0.0

    # Year-by-year results
    yearly_results: List[YearlyResults] = field(default_factory=list)

    # Scenario used
    scenario: UptakeScenario = UptakeScenario.MODERATE

    # Cost per treated patient (IXA-001)
    cost_per_ixa_patient: float = 0.0
    incremental_cost_per_ixa_patient: float = 0.0

    def get_yearly_budget_impact(self) -> List[float]:
        """Get list of budget impacts by year."""
        return [yr.budget_impact for yr in self.yearly_results]

    def get_cumulative_impact(self) -> List[float]:
        """Get cumulative budget impact by year."""
        impacts = self.get_yearly_budget_impact()
        cumulative = []
        total = 0
        for impact in impacts:
            total += impact
            cumulative.append(total)
        return cumulative

    def to_summary_dict(self) -> Dict:
        """Convert results to summary dictionary."""
        return {
            "scenario": self.scenario.value,
            "eligible_patients": self.total_eligible_patients,
            "total_5yr_impact": self.total_budget_impact_5yr,
            "average_annual_impact": self.average_annual_impact,
            "pmpm_year1": self.pmpm_impact_year1,
            "pmpm_year5": self.pmpm_impact_year5,
            "cost_per_ixa_patient": self.cost_per_ixa_patient,
            "incremental_cost_per_patient": self.incremental_cost_per_ixa_patient,
            "yearly_impacts": self.get_yearly_budget_impact(),
        }


class BIMCalculator:
    """
    Budget Impact Model Calculator.

    Calculates the budget impact of introducing IXA-001 compared to
    a world without IXA-001 (current standard of care).
    """

    def __init__(self, inputs: BIMInputs):
        self.inputs = inputs

    def calculate(
        self,
        scenario: Optional[UptakeScenario] = None
    ) -> BIMResults:
        """
        Run the budget impact calculation.

        Args:
            scenario: Uptake scenario to use (defaults to inputs.selected_scenario)

        Returns:
            BIMResults with complete budget impact analysis
        """
        if scenario is None:
            scenario = self.inputs.selected_scenario

        results = BIMResults(
            inputs=self.inputs,
            scenario=scenario,
            total_eligible_patients=self.inputs.population.eligible_patients,
        )

        eligible = self.inputs.population.eligible_patients

        # Calculate for each year
        for year in range(1, self.inputs.time_horizon_years + 1):
            yearly = self._calculate_year(year, eligible, scenario)
            results.yearly_results.append(yearly)

        # Calculate summary metrics
        results.total_budget_impact_5yr = sum(
            yr.budget_impact for yr in results.yearly_results
        )
        results.average_annual_impact = (
            results.total_budget_impact_5yr / self.inputs.time_horizon_years
        )

        # PMPM calculations
        total_members = self.inputs.population.total_population
        if results.yearly_results:
            results.pmpm_impact_year1 = (
                results.yearly_results[0].budget_impact / total_members / 12
            )
            results.pmpm_impact_year5 = (
                results.yearly_results[-1].budget_impact / total_members / 12
            )

        # Cost per IXA-001 patient
        results.cost_per_ixa_patient = self.inputs.costs.get_total_annual_cost(
            "ixa_001", include_offsets=self.inputs.include_event_offsets
        )

        # Incremental cost vs weighted average current treatment
        weighted_current = self._get_weighted_current_cost()
        results.incremental_cost_per_ixa_patient = (
            results.cost_per_ixa_patient - weighted_current
        )

        return results

    def _calculate_year(
        self,
        year: int,
        eligible_patients: int,
        scenario: UptakeScenario
    ) -> YearlyResults:
        """Calculate budget impact for a single year."""
        yearly = YearlyResults(year=year)

        # Get IXA-001 uptake for this year
        ixa_uptake = self.inputs.market.get_uptake(scenario, year)

        # Calculate market shares in new world
        yearly.share_ixa_001 = ixa_uptake

        # Remaining market is distributed based on displacement
        remaining = 1.0 - ixa_uptake

        # Calculate displaced shares
        displaced_spiro = ixa_uptake * self.inputs.market.displacement_from_spironolactone
        displaced_mra = ixa_uptake * self.inputs.market.displacement_from_other_mra
        displaced_untreated = ixa_uptake * self.inputs.market.displacement_from_untreated

        # New shares = baseline - displaced portion
        yearly.share_spironolactone = max(
            0, self.inputs.market.baseline_spironolactone - displaced_spiro
        )
        yearly.share_other_mra = max(
            0, self.inputs.market.baseline_other_mra - displaced_mra
        )
        yearly.share_no_treatment = max(
            0, self.inputs.market.baseline_no_4th_line - displaced_untreated
        )

        # Normalize to ensure shares sum to 1
        total_share = (
            yearly.share_ixa_001
            + yearly.share_spironolactone
            + yearly.share_other_mra
            + yearly.share_no_treatment
        )
        if total_share > 0:
            yearly.share_ixa_001 /= total_share
            yearly.share_spironolactone /= total_share
            yearly.share_other_mra /= total_share
            yearly.share_no_treatment /= total_share

        # Calculate patient counts (new world)
        yearly.patients_ixa_001 = int(eligible_patients * yearly.share_ixa_001)
        yearly.patients_spironolactone = int(eligible_patients * yearly.share_spironolactone)
        yearly.patients_other_mra = int(eligible_patients * yearly.share_other_mra)
        yearly.patients_no_treatment = int(eligible_patients * yearly.share_no_treatment)

        # Get per-patient costs
        include_offsets = self.inputs.include_event_offsets
        cost_ixa = self.inputs.costs.get_total_annual_cost("ixa_001", include_offsets)
        cost_spiro = self.inputs.costs.get_total_annual_cost("spironolactone", include_offsets)
        cost_mra = self.inputs.costs.get_total_annual_cost("other_mra", include_offsets)
        cost_none = self.inputs.costs.get_total_annual_cost("no_treatment", include_offsets)

        # Calculate costs - New World
        yearly.cost_ixa_001 = yearly.patients_ixa_001 * cost_ixa
        yearly.cost_spironolactone = yearly.patients_spironolactone * cost_spiro
        yearly.cost_other_mra = yearly.patients_other_mra * cost_mra
        yearly.cost_no_treatment = yearly.patients_no_treatment * cost_none

        yearly.cost_new_world = (
            yearly.cost_ixa_001
            + yearly.cost_spironolactone
            + yearly.cost_other_mra
            + yearly.cost_no_treatment
        )

        # Calculate costs - Current World (baseline, no IXA-001)
        patients_spiro_baseline = int(
            eligible_patients * self.inputs.market.baseline_spironolactone
        )
        patients_mra_baseline = int(
            eligible_patients * self.inputs.market.baseline_other_mra
        )
        patients_none_baseline = int(
            eligible_patients * self.inputs.market.baseline_no_4th_line
        )

        yearly.cost_current_world = (
            patients_spiro_baseline * cost_spiro
            + patients_mra_baseline * cost_mra
            + patients_none_baseline * cost_none
        )

        # Budget impact = New World - Current World
        yearly.budget_impact = yearly.cost_new_world - yearly.cost_current_world

        return yearly

    def _get_weighted_current_cost(self) -> float:
        """Get weighted average cost of current treatments."""
        market = self.inputs.market
        costs = self.inputs.costs
        include_offsets = self.inputs.include_event_offsets

        weighted = (
            market.baseline_spironolactone
            * costs.get_total_annual_cost("spironolactone", include_offsets)
            + market.baseline_other_mra
            * costs.get_total_annual_cost("other_mra", include_offsets)
            + market.baseline_no_4th_line
            * costs.get_total_annual_cost("no_treatment", include_offsets)
        )

        return weighted

    def run_all_scenarios(self) -> Dict[UptakeScenario, BIMResults]:
        """Run calculations for all uptake scenarios."""
        return {
            scenario: self.calculate(scenario)
            for scenario in UptakeScenario
        }

    def sensitivity_analysis(
        self,
        parameter: str,
        values: List[float],
        scenario: Optional[UptakeScenario] = None
    ) -> List[Dict]:
        """
        Run one-way sensitivity analysis on a parameter.

        Args:
            parameter: Parameter to vary (e.g., "ixa_001_annual", "resistant_htn_proportion")
            values: List of values to test
            scenario: Uptake scenario to use

        Returns:
            List of dicts with parameter value and results
        """
        if scenario is None:
            scenario = self.inputs.selected_scenario

        results = []

        # Store original value
        original_value = self._get_parameter(parameter)

        for value in values:
            # Set parameter
            self._set_parameter(parameter, value)

            # Run calculation
            bim_results = self.calculate(scenario)

            results.append({
                "parameter": parameter,
                "value": value,
                "budget_impact_5yr": bim_results.total_budget_impact_5yr,
                "pmpm_year5": bim_results.pmpm_impact_year5,
            })

        # Restore original value
        self._set_parameter(parameter, original_value)

        return results

    def _get_parameter(self, parameter: str) -> float:
        """Get a parameter value by name."""
        if hasattr(self.inputs.costs, parameter):
            return getattr(self.inputs.costs, parameter)
        elif hasattr(self.inputs.population, parameter):
            return getattr(self.inputs.population, parameter)
        elif hasattr(self.inputs.market, parameter):
            return getattr(self.inputs.market, parameter)
        else:
            raise ValueError(f"Unknown parameter: {parameter}")

    def _set_parameter(self, parameter: str, value: float):
        """Set a parameter value by name."""
        if hasattr(self.inputs.costs, parameter):
            setattr(self.inputs.costs, parameter, value)
        elif hasattr(self.inputs.population, parameter):
            setattr(self.inputs.population, parameter, value)
        elif hasattr(self.inputs.market, parameter):
            setattr(self.inputs.market, parameter, value)
        else:
            raise ValueError(f"Unknown parameter: {parameter}")

    def price_threshold_analysis(
        self,
        budget_target: float,
        scenario: Optional[UptakeScenario] = None
    ) -> Optional[float]:
        """
        Find IXA-001 price that achieves a target budget impact.

        Args:
            budget_target: Target total 5-year budget impact
            scenario: Uptake scenario to use

        Returns:
            IXA-001 annual price that achieves the target, or None if not achievable
        """
        if scenario is None:
            scenario = self.inputs.selected_scenario

        # Binary search for price
        low_price = 0
        high_price = 50_000  # Maximum reasonable price
        tolerance = 100  # $100 tolerance

        original_price = self.inputs.costs.ixa_001_annual

        while high_price - low_price > tolerance:
            mid_price = (low_price + high_price) / 2
            self.inputs.costs.ixa_001_annual = mid_price

            results = self.calculate(scenario)

            if results.total_budget_impact_5yr < budget_target:
                low_price = mid_price
            else:
                high_price = mid_price

        # Restore original price
        self.inputs.costs.ixa_001_annual = original_price

        return (low_price + high_price) / 2


# ============================================================================
# Enhanced BIM Result Classes
# ============================================================================

@dataclass
class EventResults:
    """Results for clinical event calculations."""

    # Events by type and treatment
    events_by_type: Dict[EventType, Dict[str, float]] = field(default_factory=dict)

    # Events avoided (IXA-001 vs comparator)
    events_avoided: Dict[EventType, float] = field(default_factory=dict)

    # Event costs by type
    event_costs: Dict[EventType, float] = field(default_factory=dict)

    # Total event costs avoided
    total_costs_avoided: float = 0.0

    def get_total_events(self, treatment: str) -> float:
        """Get total events for a treatment."""
        return sum(
            self.events_by_type.get(event, {}).get(treatment, 0)
            for event in EventType
        )


@dataclass
class SubgroupResults:
    """Results for a single subgroup."""

    subgroup_name: str
    subgroup_code: str
    subgroup_type: SubgroupType
    patients: int
    proportion: float

    # Budget impact for this subgroup
    budget_impact_5yr: float = 0.0
    budget_impact_per_patient: float = 0.0

    # Events for this subgroup
    events_avoided: Dict[EventType, float] = field(default_factory=dict)

    # Year-by-year impact
    yearly_impacts: List[float] = field(default_factory=list)


@dataclass
class PersistenceResults:
    """Results for treatment persistence modeling."""

    # Patients on therapy by year (accounting for discontinuation)
    patients_by_year: Dict[str, List[int]] = field(default_factory=dict)

    # Effective patient-years by treatment
    patient_years: Dict[str, float] = field(default_factory=dict)

    # Persistence rates by treatment and year
    persistence_rates: Dict[str, List[float]] = field(default_factory=dict)


@dataclass
class TornadoResult:
    """Result for one parameter in tornado analysis."""

    parameter: str
    parameter_label: str
    base_value: float
    low_value: float
    high_value: float
    impact_at_low: float
    impact_at_high: float
    impact_range: float  # high - low impact


@dataclass
class PSAResults:
    """Results from probabilistic sensitivity analysis."""

    # Number of iterations
    iterations: int

    # Distribution of 5-year budget impacts
    impact_distribution: List[float] = field(default_factory=list)

    # Summary statistics
    mean_impact: float = 0.0
    median_impact: float = 0.0
    std_impact: float = 0.0
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    confidence_level: float = 0.95

    # Probability of budget increase
    prob_budget_increase: float = 0.0

    # Distribution of PMPM
    pmpm_distribution: List[float] = field(default_factory=list)


@dataclass
class ExtendedBIMResults:
    """Complete enhanced BIM results container."""

    # Base results (inherits from BIMResults structure)
    base_results: BIMResults = None

    # Event analysis
    event_results: EventResults = None

    # Subgroup results
    subgroup_results: Dict[SubgroupType, List[SubgroupResults]] = field(default_factory=dict)

    # Persistence results
    persistence_results: PersistenceResults = None

    # Extended horizon (10-year)
    extended_yearly_results: List[YearlyResults] = field(default_factory=list)
    extended_total_impact: float = 0.0

    # Sensitivity analysis
    tornado_results: List[TornadoResult] = field(default_factory=list)
    psa_results: PSAResults = None

    def get_summary(self) -> Dict:
        """Get summary dictionary of all results."""
        summary = {}
        if self.base_results:
            summary.update(self.base_results.to_summary_dict())

        if self.event_results:
            summary["total_events_avoided"] = sum(
                self.event_results.events_avoided.values()
            )
            summary["total_event_costs_avoided"] = self.event_results.total_costs_avoided

        summary["extended_10yr_impact"] = self.extended_total_impact

        if self.psa_results:
            summary["psa_mean_impact"] = self.psa_results.mean_impact
            summary["psa_ci_lower"] = self.psa_results.ci_lower
            summary["psa_ci_upper"] = self.psa_results.ci_upper

        return summary


# ============================================================================
# Enhanced BIM Calculator
# ============================================================================

class EnhancedBIMCalculator:
    """
    Enhanced Budget Impact Model Calculator.

    Extends BIMCalculator with:
    - Subgroup analysis
    - Treatment persistence modeling
    - Detailed event calculations
    - Extended time horizon (10 years)
    - Tornado diagram analysis
    - Multi-way sensitivity analysis
    - Probabilistic sensitivity analysis (Monte Carlo)
    """

    def __init__(self, inputs: ExtendedBIMInputs):
        if not isinstance(inputs, ExtendedBIMInputs):
            # Convert BIMInputs to ExtendedBIMInputs
            extended = ExtendedBIMInputs()
            extended.population = inputs.population
            extended.market = inputs.market
            extended.costs = inputs.costs
            extended.country = inputs.country
            extended.time_horizon_years = inputs.time_horizon_years
            extended.selected_scenario = inputs.selected_scenario
            extended.include_event_offsets = inputs.include_event_offsets
            inputs = extended

        self.inputs = inputs
        self.base_calculator = BIMCalculator(inputs)

    def calculate_full(
        self,
        scenario: Optional[UptakeScenario] = None,
        include_subgroups: bool = True,
        include_persistence: bool = True,
        include_events: bool = True,
        include_extended_horizon: bool = True,
    ) -> ExtendedBIMResults:
        """
        Run complete enhanced BIM calculation.

        Args:
            scenario: Uptake scenario (defaults to inputs.selected_scenario)
            include_subgroups: Whether to run subgroup analysis
            include_persistence: Whether to model treatment persistence
            include_events: Whether to calculate clinical events
            include_extended_horizon: Whether to project to 10 years

        Returns:
            ExtendedBIMResults with complete analysis
        """
        if scenario is None:
            scenario = self.inputs.selected_scenario

        results = ExtendedBIMResults()

        # Run base calculation
        results.base_results = self.base_calculator.calculate(scenario)

        # Event analysis
        if include_events and self.inputs.include_events:
            results.event_results = self._calculate_events(scenario)

        # Subgroup analysis
        if include_subgroups and self.inputs.selected_subgroup_types:
            results.subgroup_results = self._calculate_subgroups(scenario)

        # Persistence modeling
        if include_persistence and self.inputs.include_persistence:
            results.persistence_results = self._calculate_with_persistence(scenario)

        # Extended horizon (10-year)
        if include_extended_horizon:
            results.extended_yearly_results, results.extended_total_impact = (
                self._calculate_extended_horizon(scenario)
            )

        return results

    def _calculate_events(self, scenario: UptakeScenario) -> EventResults:
        """Calculate clinical events and costs avoided."""
        event_results = EventResults()
        eligible = self.inputs.population.eligible_patients
        rates = self.inputs.event_rates
        costs = self.inputs.event_costs

        # Calculate events for each year
        total_events_by_type = {event: {} for event in EventType}
        total_events_avoided = {event: 0.0 for event in EventType}
        total_event_costs = {event: 0.0 for event in EventType}

        for year in range(1, self.inputs.time_horizon_years + 1):
            uptake = self.inputs.market.get_uptake(scenario, year)

            # Patient counts
            patients_ixa = int(eligible * uptake)
            patients_spiro = int(eligible * self.inputs.market.baseline_spironolactone * (1 - uptake))
            patients_mra = int(eligible * self.inputs.market.baseline_other_mra * (1 - uptake))
            patients_none = int(eligible * self.inputs.market.baseline_no_4th_line * (1 - uptake))

            # Current world (no IXA)
            patients_spiro_current = int(eligible * self.inputs.market.baseline_spironolactone)
            patients_mra_current = int(eligible * self.inputs.market.baseline_other_mra)
            patients_none_current = int(eligible * self.inputs.market.baseline_no_4th_line)

            for event in EventType:
                if event in (EventType.CV_DEATH, EventType.ALL_CAUSE_DEATH):
                    # Death events need special handling
                    continue

                rate_ixa = rates.get_rate(event, "ixa_001") / 1000
                rate_spiro = rates.get_rate(event, "spironolactone") / 1000
                rate_mra = rates.get_rate(event, "other_mra") / 1000
                rate_none = rates.get_rate(event, "no_treatment") / 1000

                # Events in new world
                events_new = (
                    patients_ixa * rate_ixa +
                    patients_spiro * rate_spiro +
                    patients_mra * rate_mra +
                    patients_none * rate_none
                )

                # Events in current world
                events_current = (
                    patients_spiro_current * rate_spiro +
                    patients_mra_current * rate_mra +
                    patients_none_current * rate_none
                )

                events_avoided = events_current - events_new

                # Accumulate
                if "ixa_001" not in total_events_by_type[event]:
                    total_events_by_type[event] = {
                        "ixa_001": 0, "spironolactone": 0,
                        "other_mra": 0, "no_treatment": 0
                    }
                total_events_by_type[event]["ixa_001"] += patients_ixa * rate_ixa
                total_events_by_type[event]["spironolactone"] += patients_spiro * rate_spiro
                total_events_by_type[event]["other_mra"] += patients_mra * rate_mra
                total_events_by_type[event]["no_treatment"] += patients_none * rate_none

                total_events_avoided[event] += events_avoided

                # Calculate costs
                acute_cost, followup_cost = costs.get_costs(event)
                event_cost_avoided = events_avoided * acute_cost
                total_event_costs[event] += event_cost_avoided

        event_results.events_by_type = total_events_by_type
        event_results.events_avoided = total_events_avoided
        event_results.event_costs = total_event_costs
        event_results.total_costs_avoided = sum(total_event_costs.values())

        return event_results

    def _calculate_subgroups(
        self,
        scenario: UptakeScenario
    ) -> Dict[SubgroupType, List[SubgroupResults]]:
        """Calculate budget impact stratified by subgroups."""
        all_subgroup_results = {}
        eligible = self.inputs.population.eligible_patients

        for subgroup_type in self.inputs.selected_subgroup_types:
            subgroups = self.inputs.subgroups.get_subgroups(subgroup_type)
            type_results = []

            for sg in subgroups:
                sg_patients = int(eligible * sg.proportion)

                # Create modified inputs for this subgroup
                sg_inputs = copy.deepcopy(self.inputs)
                sg_inputs.population.total_population = int(
                    self.inputs.population.total_population * sg.proportion
                )

                # Adjust event rates by risk multipliers
                sg_inputs.event_rates.stroke_ixa_001 *= sg.stroke_risk_multiplier
                sg_inputs.event_rates.mi_ixa_001 *= sg.mi_risk_multiplier
                sg_inputs.event_rates.hf_ixa_001 *= sg.hf_risk_multiplier

                # Run calculation
                sg_calculator = BIMCalculator(sg_inputs)
                sg_bim_results = sg_calculator.calculate(scenario)

                sg_result = SubgroupResults(
                    subgroup_name=sg.name,
                    subgroup_code=sg.code,
                    subgroup_type=subgroup_type,
                    patients=sg_patients,
                    proportion=sg.proportion,
                    budget_impact_5yr=sg_bim_results.total_budget_impact_5yr,
                    budget_impact_per_patient=(
                        sg_bim_results.total_budget_impact_5yr / sg_patients
                        if sg_patients > 0 else 0
                    ),
                    yearly_impacts=sg_bim_results.get_yearly_budget_impact(),
                )

                type_results.append(sg_result)

            all_subgroup_results[subgroup_type] = type_results

        return all_subgroup_results

    def _calculate_with_persistence(self, scenario: UptakeScenario) -> PersistenceResults:
        """Model treatment patterns with discontinuation."""
        results = PersistenceResults()
        eligible = self.inputs.population.eligible_patients
        persistence = self.inputs.persistence

        treatments = ["ixa_001", "spironolactone", "other_mra", "no_treatment"]

        for treatment in treatments:
            results.patients_by_year[treatment] = []
            results.persistence_rates[treatment] = []

        for year in range(1, self.inputs.time_horizon_years + 1):
            uptake = self.inputs.market.get_uptake(scenario, year)

            # Initial patients (before persistence adjustment)
            initial_ixa = int(eligible * uptake)
            initial_spiro = int(
                eligible * self.inputs.market.baseline_spironolactone *
                (1 - uptake * self.inputs.market.displacement_from_spironolactone)
            )
            initial_mra = int(
                eligible * self.inputs.market.baseline_other_mra *
                (1 - uptake * self.inputs.market.displacement_from_other_mra)
            )
            initial_none = int(
                eligible * self.inputs.market.baseline_no_4th_line *
                (1 - uptake * self.inputs.market.displacement_from_untreated)
            )

            # Apply persistence
            persist_ixa = persistence.get_persistence("ixa_001", year)
            persist_spiro = persistence.get_persistence("spironolactone", year)
            persist_mra = persistence.get_persistence("other_mra", year)

            results.patients_by_year["ixa_001"].append(int(initial_ixa * persist_ixa))
            results.patients_by_year["spironolactone"].append(int(initial_spiro * persist_spiro))
            results.patients_by_year["other_mra"].append(int(initial_mra * persist_mra))
            results.patients_by_year["no_treatment"].append(initial_none)

            results.persistence_rates["ixa_001"].append(persist_ixa)
            results.persistence_rates["spironolactone"].append(persist_spiro)
            results.persistence_rates["other_mra"].append(persist_mra)
            results.persistence_rates["no_treatment"].append(1.0)

        # Calculate patient-years
        for treatment in treatments:
            results.patient_years[treatment] = sum(
                results.patients_by_year[treatment]
            )

        return results

    def _calculate_extended_horizon(
        self,
        scenario: UptakeScenario
    ) -> tuple[List[YearlyResults], float]:
        """Project budget impact to 10 years with plateau assumption."""
        extended_results = []
        eligible = self.inputs.population.eligible_patients

        # Get Year 5 uptake as plateau
        plateau_uptake = self.inputs.market.get_uptake(scenario, 5)

        for year in range(1, self.inputs.extended_time_horizon_years + 1):
            if year <= 5:
                # Use standard uptake curve
                uptake = self.inputs.market.get_uptake(scenario, year)
            else:
                # Plateau at Year 5 level
                uptake = plateau_uptake

            yearly = self._calculate_single_year(year, eligible, uptake)
            extended_results.append(yearly)

        total_impact = sum(yr.budget_impact for yr in extended_results)
        return extended_results, total_impact

    def _calculate_single_year(
        self,
        year: int,
        eligible_patients: int,
        uptake: float
    ) -> YearlyResults:
        """Calculate budget impact for a single year with given uptake."""
        yearly = YearlyResults(year=year)

        # Calculate market shares
        yearly.share_ixa_001 = uptake

        displaced_spiro = uptake * self.inputs.market.displacement_from_spironolactone
        displaced_mra = uptake * self.inputs.market.displacement_from_other_mra
        displaced_untreated = uptake * self.inputs.market.displacement_from_untreated

        yearly.share_spironolactone = max(
            0, self.inputs.market.baseline_spironolactone - displaced_spiro
        )
        yearly.share_other_mra = max(
            0, self.inputs.market.baseline_other_mra - displaced_mra
        )
        yearly.share_no_treatment = max(
            0, self.inputs.market.baseline_no_4th_line - displaced_untreated
        )

        # Normalize
        total_share = (
            yearly.share_ixa_001 + yearly.share_spironolactone +
            yearly.share_other_mra + yearly.share_no_treatment
        )
        if total_share > 0:
            yearly.share_ixa_001 /= total_share
            yearly.share_spironolactone /= total_share
            yearly.share_other_mra /= total_share
            yearly.share_no_treatment /= total_share

        # Patient counts
        yearly.patients_ixa_001 = int(eligible_patients * yearly.share_ixa_001)
        yearly.patients_spironolactone = int(eligible_patients * yearly.share_spironolactone)
        yearly.patients_other_mra = int(eligible_patients * yearly.share_other_mra)
        yearly.patients_no_treatment = int(eligible_patients * yearly.share_no_treatment)

        # Costs
        include_offsets = self.inputs.include_event_offsets
        cost_ixa = self.inputs.costs.get_total_annual_cost("ixa_001", include_offsets)
        cost_spiro = self.inputs.costs.get_total_annual_cost("spironolactone", include_offsets)
        cost_mra = self.inputs.costs.get_total_annual_cost("other_mra", include_offsets)
        cost_none = self.inputs.costs.get_total_annual_cost("no_treatment", include_offsets)

        yearly.cost_ixa_001 = yearly.patients_ixa_001 * cost_ixa
        yearly.cost_spironolactone = yearly.patients_spironolactone * cost_spiro
        yearly.cost_other_mra = yearly.patients_other_mra * cost_mra
        yearly.cost_no_treatment = yearly.patients_no_treatment * cost_none

        yearly.cost_new_world = (
            yearly.cost_ixa_001 + yearly.cost_spironolactone +
            yearly.cost_other_mra + yearly.cost_no_treatment
        )

        # Current world costs
        patients_spiro_baseline = int(
            eligible_patients * self.inputs.market.baseline_spironolactone
        )
        patients_mra_baseline = int(
            eligible_patients * self.inputs.market.baseline_other_mra
        )
        patients_none_baseline = int(
            eligible_patients * self.inputs.market.baseline_no_4th_line
        )

        yearly.cost_current_world = (
            patients_spiro_baseline * cost_spiro +
            patients_mra_baseline * cost_mra +
            patients_none_baseline * cost_none
        )

        yearly.budget_impact = yearly.cost_new_world - yearly.cost_current_world

        return yearly

    def run_tornado_analysis(
        self,
        scenario: Optional[UptakeScenario] = None
    ) -> List[TornadoResult]:
        """
        Run one-way sensitivity analysis for tornado diagram.

        Tests each parameter at low and high values while holding others constant.
        """
        if scenario is None:
            scenario = self.inputs.selected_scenario

        results = []
        base_results = self.base_calculator.calculate(scenario)
        base_impact = base_results.total_budget_impact_5yr

        parameter_labels = {
            "ixa_001_annual": "IXA-001 Annual Cost",
            "resistant_htn_proportion": "Resistant HTN Prevalence",
            "treatment_seeking_rate": "Treatment-Seeking Rate",
            "avoided_events_ixa_001_annual": "Avoided Event Costs (IXA)",
            "displacement_from_spironolactone": "Displacement from Spiro",
            "hypertension_prevalence": "HTN Prevalence",
            "discontinuation_ixa_001_year1": "IXA-001 Yr1 Discontinuation",
        }

        for param_name, low_mult, high_mult in self.inputs.sensitivity.tornado_parameters:
            base_value = self._get_parameter_value(param_name)

            # Test low value
            low_value = base_value * low_mult
            self._set_parameter_value(param_name, low_value)
            low_results = self.base_calculator.calculate(scenario)
            impact_at_low = low_results.total_budget_impact_5yr

            # Test high value
            high_value = base_value * high_mult
            self._set_parameter_value(param_name, high_value)
            high_results = self.base_calculator.calculate(scenario)
            impact_at_high = high_results.total_budget_impact_5yr

            # Restore base value
            self._set_parameter_value(param_name, base_value)

            result = TornadoResult(
                parameter=param_name,
                parameter_label=parameter_labels.get(param_name, param_name),
                base_value=base_value,
                low_value=low_value,
                high_value=high_value,
                impact_at_low=impact_at_low,
                impact_at_high=impact_at_high,
                impact_range=abs(impact_at_high - impact_at_low),
            )
            results.append(result)

        # Sort by impact range (descending)
        results.sort(key=lambda x: x.impact_range, reverse=True)

        return results

    def run_multiway_sensitivity(
        self,
        parameters: List[Tuple[str, List[float]]],
        scenario: Optional[UptakeScenario] = None
    ) -> List[Dict]:
        """
        Run multi-parameter sensitivity analysis.

        Args:
            parameters: List of (parameter_name, [values]) tuples
            scenario: Uptake scenario

        Returns:
            List of results for each combination
        """
        if scenario is None:
            scenario = self.inputs.selected_scenario

        results = []

        # Save original values
        original_values = {param: self._get_parameter_value(param) for param, _ in parameters}

        # Generate combinations (simplified - just varies one at a time for now)
        for param_name, values in parameters:
            for value in values:
                self._set_parameter_value(param_name, value)
                bim_results = self.base_calculator.calculate(scenario)

                results.append({
                    "parameter": param_name,
                    "value": value,
                    "budget_impact_5yr": bim_results.total_budget_impact_5yr,
                    "pmpm_year5": bim_results.pmpm_impact_year5,
                    "eligible_patients": bim_results.total_eligible_patients,
                })

                # Restore
                self._set_parameter_value(param_name, original_values[param_name])

        return results

    def run_probabilistic_sensitivity(
        self,
        iterations: Optional[int] = None,
        scenario: Optional[UptakeScenario] = None,
        seed: Optional[int] = None
    ) -> PSAResults:
        """
        Run Monte Carlo probabilistic sensitivity analysis.

        Samples parameters from distributions and runs model iterations.
        """
        if iterations is None:
            iterations = self.inputs.sensitivity.psa_iterations
        if scenario is None:
            scenario = self.inputs.selected_scenario
        if seed is not None:
            np.random.seed(seed)

        impact_results = []
        pmpm_results = []

        # Store original values
        original_values = {}
        for param_name, _, _, _ in self.inputs.sensitivity.psa_distributions:
            original_values[param_name] = self._get_parameter_value(param_name)

        for _ in range(iterations):
            # Sample from distributions
            for param_name, dist_type, param1, param2 in self.inputs.sensitivity.psa_distributions:
                if dist_type == "normal":
                    sampled = np.random.normal(param1, param2)
                elif dist_type == "lognormal":
                    # param1 = mean, param2 = sd
                    mu = np.log(param1**2 / np.sqrt(param2**2 + param1**2))
                    sigma = np.sqrt(np.log(1 + param2**2 / param1**2))
                    sampled = np.random.lognormal(mu, sigma)
                elif dist_type == "beta":
                    # param1 = alpha, param2 = beta (scaled to proportion)
                    sampled = np.random.beta(param1, param2)
                else:
                    sampled = param1  # Default to mean

                self._set_parameter_value(param_name, sampled)

            # Run calculation
            try:
                bim_results = self.base_calculator.calculate(scenario)
                impact_results.append(bim_results.total_budget_impact_5yr)
                pmpm_results.append(bim_results.pmpm_impact_year5)
            except Exception:
                # Skip failed iterations
                pass

            # Restore original values
            for param_name, value in original_values.items():
                self._set_parameter_value(param_name, value)

        # Calculate statistics
        impact_array = np.array(impact_results)
        confidence_level = self.inputs.sensitivity.psa_confidence_level
        alpha = (1 - confidence_level) / 2

        psa_results = PSAResults(
            iterations=len(impact_results),
            impact_distribution=impact_results,
            mean_impact=float(np.mean(impact_array)),
            median_impact=float(np.median(impact_array)),
            std_impact=float(np.std(impact_array)),
            ci_lower=float(np.percentile(impact_array, alpha * 100)),
            ci_upper=float(np.percentile(impact_array, (1 - alpha) * 100)),
            confidence_level=confidence_level,
            prob_budget_increase=float(np.mean(impact_array > 0)),
            pmpm_distribution=pmpm_results,
        )

        return psa_results

    def _get_parameter_value(self, param_name: str) -> float:
        """Get parameter value by name from various input objects."""
        if hasattr(self.inputs.costs, param_name):
            return getattr(self.inputs.costs, param_name)
        elif hasattr(self.inputs.population, param_name):
            return getattr(self.inputs.population, param_name)
        elif hasattr(self.inputs.market, param_name):
            return getattr(self.inputs.market, param_name)
        elif hasattr(self.inputs.event_rates, param_name):
            return getattr(self.inputs.event_rates, param_name)
        elif hasattr(self.inputs.persistence, param_name):
            return getattr(self.inputs.persistence, param_name)
        else:
            raise ValueError(f"Unknown parameter: {param_name}")

    def _set_parameter_value(self, param_name: str, value: float):
        """Set parameter value by name."""
        if hasattr(self.inputs.costs, param_name):
            setattr(self.inputs.costs, param_name, value)
        elif hasattr(self.inputs.population, param_name):
            setattr(self.inputs.population, param_name, value)
        elif hasattr(self.inputs.market, param_name):
            setattr(self.inputs.market, param_name, value)
        elif hasattr(self.inputs.event_rates, param_name):
            setattr(self.inputs.event_rates, param_name, value)
        elif hasattr(self.inputs.persistence, param_name):
            setattr(self.inputs.persistence, param_name, value)
        else:
            raise ValueError(f"Unknown parameter: {param_name}")
