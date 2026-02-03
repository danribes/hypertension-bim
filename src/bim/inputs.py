"""
Budget Impact Model Input Data Classes.

Contains all input parameters for the BIM including:
- Population sizing
- Market dynamics
- Cost inputs
- Uptake scenarios
- Country-specific configurations
- Clinical events and outcomes
- Subgroup definitions
- Treatment persistence
- Sensitivity analysis parameters
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class EventType(Enum):
    """Clinical event types for outcomes tracking."""
    STROKE = "stroke"
    MI = "mi"  # Myocardial infarction
    HF = "hf"  # Heart failure hospitalization
    CKD = "ckd"  # CKD progression
    ESRD = "esrd"  # End-stage renal disease
    CV_DEATH = "cv_death"  # Cardiovascular death
    ALL_CAUSE_DEATH = "all_cause_death"


class SubgroupType(Enum):
    """Subgroup categories for stratified analysis."""
    AGE = "age"
    CKD_STAGE = "ckd_stage"
    PRIOR_CV = "prior_cv"
    DIABETES = "diabetes"


class UptakeScenario(Enum):
    """Market uptake scenarios for IXA-001."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    OPTIMISTIC = "optimistic"


@dataclass
class PopulationInputs:
    """Population sizing inputs for eligible patient calculation."""

    # Plan/Population size
    total_population: int = 1_000_000

    # Epidemiology cascade
    adult_proportion: float = 0.78          # % aged 18+
    hypertension_prevalence: float = 0.30   # % of adults with HTN
    resistant_htn_proportion: float = 0.12  # % of HTN that is resistant
    uncontrolled_proportion: float = 0.50   # % of resistant that is uncontrolled

    # Treatment-seeking rate
    treatment_seeking_rate: float = 0.80    # % seeking treatment

    @property
    def eligible_patients(self) -> int:
        """Calculate number of eligible patients."""
        return int(
            self.total_population
            * self.adult_proportion
            * self.hypertension_prevalence
            * self.resistant_htn_proportion
            * self.uncontrolled_proportion
            * self.treatment_seeking_rate
        )

    def get_cascade(self) -> Dict[str, int]:
        """Get patient cascade breakdown."""
        adults = int(self.total_population * self.adult_proportion)
        htn = int(adults * self.hypertension_prevalence)
        resistant = int(htn * self.resistant_htn_proportion)
        uncontrolled = int(resistant * self.uncontrolled_proportion)
        eligible = int(uncontrolled * self.treatment_seeking_rate)

        return {
            "total_population": self.total_population,
            "adults_18_plus": adults,
            "with_hypertension": htn,
            "resistant_hypertension": resistant,
            "uncontrolled_resistant": uncontrolled,
            "eligible_for_treatment": eligible,
        }


@dataclass
class MarketInputs:
    """Market dynamics inputs."""

    # Current market shares (baseline - no IXA-001)
    baseline_spironolactone: float = 0.60   # 60%
    baseline_other_mra: float = 0.15        # 15% (eplerenone)
    baseline_no_4th_line: float = 0.25      # 25% untreated

    # IXA-001 uptake by year (5-year horizon)
    # Format: {scenario: [year1, year2, year3, year4, year5]}
    uptake_curves: Dict[UptakeScenario, List[float]] = field(default_factory=lambda: {
        UptakeScenario.CONSERVATIVE: [0.05, 0.10, 0.15, 0.18, 0.20],
        UptakeScenario.MODERATE: [0.10, 0.20, 0.30, 0.35, 0.40],
        UptakeScenario.OPTIMISTIC: [0.15, 0.30, 0.45, 0.50, 0.55],
    })

    # Displacement assumptions (where IXA-001 patients come from)
    displacement_from_spironolactone: float = 0.70  # 70%
    displacement_from_other_mra: float = 0.20       # 20%
    displacement_from_untreated: float = 0.10       # 10% new treatment

    def get_uptake(self, scenario: UptakeScenario, year: int) -> float:
        """Get IXA-001 uptake for a given scenario and year."""
        if year < 1 or year > 5:
            raise ValueError("Year must be between 1 and 5")
        return self.uptake_curves[scenario][year - 1]

    def validate(self) -> bool:
        """Validate that market shares sum to 1."""
        baseline_sum = (
            self.baseline_spironolactone
            + self.baseline_other_mra
            + self.baseline_no_4th_line
        )
        displacement_sum = (
            self.displacement_from_spironolactone
            + self.displacement_from_other_mra
            + self.displacement_from_untreated
        )
        return abs(baseline_sum - 1.0) < 0.01 and abs(displacement_sum - 1.0) < 0.01


@dataclass
class CostInputs:
    """Cost inputs for budget impact calculation."""

    currency: str = "USD"

    # Annual drug costs
    ixa_001_annual: float = 6_000.0
    spironolactone_annual: float = 180.0
    other_mra_annual: float = 1_800.0  # Eplerenone (brand)
    no_treatment_annual: float = 0.0

    # Annual monitoring costs
    monitoring_ixa_001: float = 180.0      # Less K+ monitoring needed
    monitoring_spironolactone: float = 240.0  # Quarterly K+ checks
    monitoring_other_mra: float = 240.0
    monitoring_no_treatment: float = 120.0

    # Annual office visit costs
    office_visits_annual: float = 300.0

    # Annual adverse event management
    ae_management_ixa_001: float = 100.0
    ae_management_spironolactone: float = 300.0  # Higher due to hyperkalemia
    ae_management_other_mra: float = 200.0
    ae_management_no_treatment: float = 0.0

    # Avoided event costs (from CEA model)
    # These represent the cost offsets from reduced CV events
    avoided_events_ixa_001_annual: float = 1_200.0  # Per patient per year
    avoided_events_spironolactone_annual: float = 800.0
    avoided_events_other_mra_annual: float = 600.0

    def get_total_annual_cost(self, treatment: str, include_offsets: bool = True) -> float:
        """Get total annual per-patient cost for a treatment."""
        if treatment == "ixa_001":
            base = (
                self.ixa_001_annual
                + self.monitoring_ixa_001
                + self.office_visits_annual
                + self.ae_management_ixa_001
            )
            offset = self.avoided_events_ixa_001_annual if include_offsets else 0
        elif treatment == "spironolactone":
            base = (
                self.spironolactone_annual
                + self.monitoring_spironolactone
                + self.office_visits_annual
                + self.ae_management_spironolactone
            )
            offset = self.avoided_events_spironolactone_annual if include_offsets else 0
        elif treatment == "other_mra":
            base = (
                self.other_mra_annual
                + self.monitoring_other_mra
                + self.office_visits_annual
                + self.ae_management_other_mra
            )
            offset = self.avoided_events_other_mra_annual if include_offsets else 0
        else:  # no_treatment
            base = (
                self.no_treatment_annual
                + self.monitoring_no_treatment
                + self.office_visits_annual
                + self.ae_management_no_treatment
            )
            offset = 0

        return base - offset


@dataclass
class CountryConfig:
    """Country-specific configuration."""

    country_code: str
    country_name: str
    currency: str
    currency_symbol: str

    # Population defaults
    default_population: int
    adult_proportion: float
    hypertension_prevalence: float
    resistant_htn_proportion: float

    # Cost multiplier (relative to US)
    cost_multiplier: float = 1.0

    # Exchange rate to USD (for reporting)
    exchange_rate_to_usd: float = 1.0


# Country configurations
US_CONFIG = CountryConfig(
    country_code="US",
    country_name="United States",
    currency="USD",
    currency_symbol="$",
    default_population=1_000_000,
    adult_proportion=0.78,
    hypertension_prevalence=0.30,
    resistant_htn_proportion=0.12,
    cost_multiplier=1.0,
    exchange_rate_to_usd=1.0,
)

UK_CONFIG = CountryConfig(
    country_code="UK",
    country_name="United Kingdom",
    currency="GBP",
    currency_symbol="£",
    default_population=500_000,
    adult_proportion=0.80,
    hypertension_prevalence=0.28,
    resistant_htn_proportion=0.10,
    cost_multiplier=0.40,  # NHS costs typically 40% of US
    exchange_rate_to_usd=1.27,
)

GERMANY_CONFIG = CountryConfig(
    country_code="DE",
    country_name="Germany",
    currency="EUR",
    currency_symbol="€",
    default_population=500_000,
    adult_proportion=0.81,
    hypertension_prevalence=0.32,
    resistant_htn_proportion=0.11,
    cost_multiplier=0.50,
    exchange_rate_to_usd=1.08,
)

FRANCE_CONFIG = CountryConfig(
    country_code="FR",
    country_name="France",
    currency="EUR",
    currency_symbol="€",
    default_population=500_000,
    adult_proportion=0.79,
    hypertension_prevalence=0.30,
    resistant_htn_proportion=0.11,
    cost_multiplier=0.45,
    exchange_rate_to_usd=1.08,
)

ITALY_CONFIG = CountryConfig(
    country_code="IT",
    country_name="Italy",
    currency="EUR",
    currency_symbol="€",
    default_population=500_000,
    adult_proportion=0.81,
    hypertension_prevalence=0.33,
    resistant_htn_proportion=0.12,
    cost_multiplier=0.42,
    exchange_rate_to_usd=1.08,
)

SPAIN_CONFIG = CountryConfig(
    country_code="ES",
    country_name="Spain",
    currency="EUR",
    currency_symbol="€",
    default_population=500_000,
    adult_proportion=0.82,
    hypertension_prevalence=0.33,
    resistant_htn_proportion=0.11,
    cost_multiplier=0.38,
    exchange_rate_to_usd=1.08,
)

# All country configs
COUNTRY_CONFIGS = {
    "US": US_CONFIG,
    "UK": UK_CONFIG,
    "DE": GERMANY_CONFIG,
    "FR": FRANCE_CONFIG,
    "IT": ITALY_CONFIG,
    "ES": SPAIN_CONFIG,
}


@dataclass
class BIMInputs:
    """Master container for all BIM inputs."""

    population: PopulationInputs = field(default_factory=PopulationInputs)
    market: MarketInputs = field(default_factory=MarketInputs)
    costs: CostInputs = field(default_factory=CostInputs)
    country: CountryConfig = field(default_factory=lambda: US_CONFIG)

    # Analysis settings
    time_horizon_years: int = 5
    selected_scenario: UptakeScenario = UptakeScenario.MODERATE
    include_event_offsets: bool = True

    @classmethod
    def for_country(cls, country_code: str) -> "BIMInputs":
        """Create BIMInputs with country-specific defaults."""
        config = COUNTRY_CONFIGS.get(country_code, US_CONFIG)

        population = PopulationInputs(
            total_population=config.default_population,
            adult_proportion=config.adult_proportion,
            hypertension_prevalence=config.hypertension_prevalence,
            resistant_htn_proportion=config.resistant_htn_proportion,
        )

        costs = CostInputs(
            currency=config.currency,
            ixa_001_annual=6_000.0 * config.cost_multiplier,
            spironolactone_annual=180.0 * config.cost_multiplier,
            other_mra_annual=1_800.0 * config.cost_multiplier,
            monitoring_ixa_001=180.0 * config.cost_multiplier,
            monitoring_spironolactone=240.0 * config.cost_multiplier,
            monitoring_other_mra=240.0 * config.cost_multiplier,
            monitoring_no_treatment=120.0 * config.cost_multiplier,
            office_visits_annual=300.0 * config.cost_multiplier,
            ae_management_ixa_001=100.0 * config.cost_multiplier,
            ae_management_spironolactone=300.0 * config.cost_multiplier,
            ae_management_other_mra=200.0 * config.cost_multiplier,
            avoided_events_ixa_001_annual=1_200.0 * config.cost_multiplier,
            avoided_events_spironolactone_annual=800.0 * config.cost_multiplier,
            avoided_events_other_mra_annual=600.0 * config.cost_multiplier,
        )

        return cls(
            population=population,
            costs=costs,
            country=config,
        )

    def validate(self) -> List[str]:
        """Validate all inputs, return list of errors."""
        errors = []

        if self.population.total_population <= 0:
            errors.append("Total population must be positive")

        if not self.market.validate():
            errors.append("Market shares must sum to 100%")

        if self.time_horizon_years < 1 or self.time_horizon_years > 5:
            errors.append("Time horizon must be between 1 and 5 years")

        return errors


@dataclass
class ClinicalEventRates:
    """
    Annual event rates per 1,000 patients by treatment.

    Based on clinical trial data and real-world evidence.
    """

    # Stroke rates (per 1,000 patient-years)
    stroke_ixa_001: float = 8.0
    stroke_spironolactone: float = 12.0
    stroke_other_mra: float = 14.0
    stroke_no_treatment: float = 18.0

    # MI rates (per 1,000 patient-years)
    mi_ixa_001: float = 6.0
    mi_spironolactone: float = 9.0
    mi_other_mra: float = 10.0
    mi_no_treatment: float = 14.0

    # Heart failure hospitalization rates (per 1,000 patient-years)
    hf_ixa_001: float = 15.0
    hf_spironolactone: float = 22.0
    hf_other_mra: float = 25.0
    hf_no_treatment: float = 35.0

    # CKD progression rates (per 1,000 patient-years)
    ckd_ixa_001: float = 20.0
    ckd_spironolactone: float = 28.0
    ckd_other_mra: float = 30.0
    ckd_no_treatment: float = 40.0

    # ESRD rates (per 1,000 patient-years)
    esrd_ixa_001: float = 3.0
    esrd_spironolactone: float = 5.0
    esrd_other_mra: float = 5.5
    esrd_no_treatment: float = 8.0

    # CV death rates (per 1,000 patient-years)
    cv_death_ixa_001: float = 4.0
    cv_death_spironolactone: float = 6.0
    cv_death_other_mra: float = 7.0
    cv_death_no_treatment: float = 10.0

    # All-cause death rates (per 1,000 patient-years)
    all_cause_death_ixa_001: float = 12.0
    all_cause_death_spironolactone: float = 16.0
    all_cause_death_other_mra: float = 18.0
    all_cause_death_no_treatment: float = 24.0

    def get_rate(self, event: EventType, treatment: str) -> float:
        """Get event rate for a specific event type and treatment."""
        event_map = {
            EventType.STROKE: "stroke",
            EventType.MI: "mi",
            EventType.HF: "hf",
            EventType.CKD: "ckd",
            EventType.ESRD: "esrd",
            EventType.CV_DEATH: "cv_death",
            EventType.ALL_CAUSE_DEATH: "all_cause_death",
        }
        attr_name = f"{event_map[event]}_{treatment}"
        return getattr(self, attr_name, 0.0)


@dataclass
class EventCosts:
    """
    Costs associated with clinical events.

    Includes both acute episode costs and annual follow-up costs.
    """

    currency: str = "USD"

    # Stroke costs
    stroke_acute: float = 35_000.0  # Initial hospitalization
    stroke_followup_annual: float = 8_000.0  # Rehabilitation, ongoing care

    # MI costs
    mi_acute: float = 28_000.0
    mi_followup_annual: float = 5_000.0

    # Heart failure hospitalization costs
    hf_acute: float = 18_000.0
    hf_followup_annual: float = 12_000.0  # High due to frequent readmissions

    # CKD progression costs (moving to higher stage)
    ckd_acute: float = 5_000.0  # Testing, specialist visits
    ckd_followup_annual: float = 8_000.0

    # ESRD costs
    esrd_acute: float = 50_000.0  # Dialysis initiation, access surgery
    esrd_followup_annual: float = 90_000.0  # Ongoing dialysis

    # Death costs (terminal care)
    cv_death_acute: float = 45_000.0
    cv_death_followup_annual: float = 0.0  # No follow-up after death

    all_cause_death_acute: float = 35_000.0
    all_cause_death_followup_annual: float = 0.0

    def get_costs(self, event: EventType) -> Tuple[float, float]:
        """Get (acute, annual_followup) costs for an event type."""
        event_map = {
            EventType.STROKE: ("stroke_acute", "stroke_followup_annual"),
            EventType.MI: ("mi_acute", "mi_followup_annual"),
            EventType.HF: ("hf_acute", "hf_followup_annual"),
            EventType.CKD: ("ckd_acute", "ckd_followup_annual"),
            EventType.ESRD: ("esrd_acute", "esrd_followup_annual"),
            EventType.CV_DEATH: ("cv_death_acute", "cv_death_followup_annual"),
            EventType.ALL_CAUSE_DEATH: ("all_cause_death_acute", "all_cause_death_followup_annual"),
        }
        acute_attr, followup_attr = event_map[event]
        return getattr(self, acute_attr), getattr(self, followup_attr)


@dataclass
class SubgroupParameters:
    """Parameters for a single subgroup."""

    name: str  # Display name (e.g., "Age <65")
    code: str  # Internal code (e.g., "age_lt65")
    proportion: float  # Proportion of eligible population

    # Risk multipliers (relative to average population)
    stroke_risk_multiplier: float = 1.0
    mi_risk_multiplier: float = 1.0
    hf_risk_multiplier: float = 1.0
    ckd_risk_multiplier: float = 1.0
    death_risk_multiplier: float = 1.0

    # Treatment effect modifier (1.0 = same as average)
    treatment_effect_modifier: float = 1.0


@dataclass
class SubgroupDefinitions:
    """Container for all subgroup configurations."""

    # Age subgroups
    age_subgroups: List[SubgroupParameters] = field(default_factory=lambda: [
        SubgroupParameters(
            name="Age <65",
            code="age_lt65",
            proportion=0.35,
            stroke_risk_multiplier=0.6,
            mi_risk_multiplier=0.7,
            hf_risk_multiplier=0.5,
            ckd_risk_multiplier=0.7,
            death_risk_multiplier=0.4,
            treatment_effect_modifier=1.1,  # Better response in younger
        ),
        SubgroupParameters(
            name="Age 65-74",
            code="age_65_74",
            proportion=0.40,
            stroke_risk_multiplier=1.0,
            mi_risk_multiplier=1.0,
            hf_risk_multiplier=1.0,
            ckd_risk_multiplier=1.0,
            death_risk_multiplier=1.0,
            treatment_effect_modifier=1.0,
        ),
        SubgroupParameters(
            name="Age 75+",
            code="age_75plus",
            proportion=0.25,
            stroke_risk_multiplier=1.8,
            mi_risk_multiplier=1.5,
            hf_risk_multiplier=2.0,
            ckd_risk_multiplier=1.5,
            death_risk_multiplier=2.5,
            treatment_effect_modifier=0.9,  # Slightly reduced in elderly
        ),
    ])

    # CKD stage subgroups
    ckd_subgroups: List[SubgroupParameters] = field(default_factory=lambda: [
        SubgroupParameters(
            name="CKD Stage 1-2 (eGFR≥60)",
            code="ckd_1_2",
            proportion=0.50,
            stroke_risk_multiplier=0.8,
            mi_risk_multiplier=0.8,
            hf_risk_multiplier=0.7,
            ckd_risk_multiplier=0.5,
            death_risk_multiplier=0.7,
            treatment_effect_modifier=1.0,
        ),
        SubgroupParameters(
            name="CKD Stage 3 (eGFR 30-59)",
            code="ckd_3",
            proportion=0.35,
            stroke_risk_multiplier=1.2,
            mi_risk_multiplier=1.3,
            hf_risk_multiplier=1.4,
            ckd_risk_multiplier=1.5,
            death_risk_multiplier=1.4,
            treatment_effect_modifier=1.0,
        ),
        SubgroupParameters(
            name="CKD Stage 4 (eGFR 15-29)",
            code="ckd_4",
            proportion=0.15,
            stroke_risk_multiplier=1.8,
            mi_risk_multiplier=1.8,
            hf_risk_multiplier=2.2,
            ckd_risk_multiplier=3.0,
            death_risk_multiplier=2.5,
            treatment_effect_modifier=0.85,  # Reduced efficacy
        ),
    ])

    # Prior CV event subgroups
    prior_cv_subgroups: List[SubgroupParameters] = field(default_factory=lambda: [
        SubgroupParameters(
            name="No Prior CV Events",
            code="no_prior_cv",
            proportion=0.70,
            stroke_risk_multiplier=0.7,
            mi_risk_multiplier=0.6,
            hf_risk_multiplier=0.6,
            ckd_risk_multiplier=0.9,
            death_risk_multiplier=0.6,
            treatment_effect_modifier=1.0,
        ),
        SubgroupParameters(
            name="Prior CV Events",
            code="prior_cv",
            proportion=0.30,
            stroke_risk_multiplier=2.0,
            mi_risk_multiplier=2.5,
            hf_risk_multiplier=2.5,
            ckd_risk_multiplier=1.3,
            death_risk_multiplier=2.5,
            treatment_effect_modifier=1.1,  # Greater absolute benefit
        ),
    ])

    # Diabetes subgroups
    diabetes_subgroups: List[SubgroupParameters] = field(default_factory=lambda: [
        SubgroupParameters(
            name="No Diabetes",
            code="no_diabetes",
            proportion=0.55,
            stroke_risk_multiplier=0.8,
            mi_risk_multiplier=0.7,
            hf_risk_multiplier=0.7,
            ckd_risk_multiplier=0.6,
            death_risk_multiplier=0.7,
            treatment_effect_modifier=1.0,
        ),
        SubgroupParameters(
            name="With Diabetes",
            code="with_diabetes",
            proportion=0.45,
            stroke_risk_multiplier=1.3,
            mi_risk_multiplier=1.5,
            hf_risk_multiplier=1.5,
            ckd_risk_multiplier=1.8,
            death_risk_multiplier=1.5,
            treatment_effect_modifier=1.05,  # Aldosterone effects in diabetes
        ),
    ])

    def get_subgroups(self, subgroup_type: SubgroupType) -> List[SubgroupParameters]:
        """Get subgroups for a given type."""
        mapping = {
            SubgroupType.AGE: self.age_subgroups,
            SubgroupType.CKD_STAGE: self.ckd_subgroups,
            SubgroupType.PRIOR_CV: self.prior_cv_subgroups,
            SubgroupType.DIABETES: self.diabetes_subgroups,
        }
        return mapping[subgroup_type]


@dataclass
class TreatmentPersistence:
    """
    Treatment discontinuation and switching patterns.

    Models real-world adherence and persistence on therapy.
    """

    # Annual discontinuation rates by treatment
    discontinuation_ixa_001_year1: float = 0.15
    discontinuation_ixa_001_year2_plus: float = 0.08

    discontinuation_spironolactone_year1: float = 0.25  # Higher due to AEs
    discontinuation_spironolactone_year2_plus: float = 0.12

    discontinuation_other_mra_year1: float = 0.20
    discontinuation_other_mra_year2_plus: float = 0.10

    # Switching patterns (proportion of discontinuers who switch)
    switch_to_ixa_001_from_spiro: float = 0.30  # If IXA available
    switch_to_spiro_from_ixa: float = 0.20
    switch_to_no_treatment: float = 0.50  # Give up on 4th line

    def get_discontinuation_rate(self, treatment: str, year: int) -> float:
        """Get discontinuation rate for treatment and year."""
        if year == 1:
            rates = {
                "ixa_001": self.discontinuation_ixa_001_year1,
                "spironolactone": self.discontinuation_spironolactone_year1,
                "other_mra": self.discontinuation_other_mra_year1,
                "no_treatment": 0.0,
            }
        else:
            rates = {
                "ixa_001": self.discontinuation_ixa_001_year2_plus,
                "spironolactone": self.discontinuation_spironolactone_year2_plus,
                "other_mra": self.discontinuation_other_mra_year2_plus,
                "no_treatment": 0.0,
            }
        return rates.get(treatment, 0.0)

    def get_persistence(self, treatment: str, year: int) -> float:
        """Get cumulative proportion still on treatment at end of year."""
        persistence = 1.0
        for y in range(1, year + 1):
            disc_rate = self.get_discontinuation_rate(treatment, y)
            persistence *= (1.0 - disc_rate)
        return persistence


@dataclass
class SensitivityParameters:
    """
    Ranges and distributions for sensitivity analysis.

    Defines min/max for tornado and distributions for PSA.
    """

    # Parameter ranges (base, low, high) for tornado analysis
    # Format: (parameter_name, low_multiplier, high_multiplier)
    tornado_parameters: List[Tuple[str, float, float]] = field(default_factory=lambda: [
        ("ixa_001_annual", 0.75, 1.25),  # Drug cost ±25%
        ("resistant_htn_proportion", 0.75, 1.25),  # Prevalence ±25%
        ("treatment_seeking_rate", 0.80, 1.20),  # Treatment seeking ±20%
        ("avoided_events_ixa_001_annual", 0.50, 1.50),  # Event offsets ±50%
        ("displacement_from_spironolactone", 0.80, 1.20),  # Displacement ±20%
        ("hypertension_prevalence", 0.85, 1.15),  # HTN prevalence ±15%
        ("discontinuation_ixa_001_year1", 0.50, 1.50),  # Discontinuation ±50%
    ])

    # Distribution types for PSA
    # Format: (parameter_name, distribution_type, param1, param2)
    # Distributions: "normal" (mean, sd), "lognormal" (mean, sd), "beta" (alpha, beta)
    psa_distributions: List[Tuple[str, str, float, float]] = field(default_factory=lambda: [
        ("ixa_001_annual", "lognormal", 6000, 600),  # Log-normal for costs
        ("spironolactone_annual", "lognormal", 180, 20),
        ("resistant_htn_proportion", "beta", 12, 88),  # Beta for proportions
        ("treatment_seeking_rate", "beta", 80, 20),
        ("stroke_ixa_001", "lognormal", 8, 2),  # Event rates
        ("mi_ixa_001", "lognormal", 6, 1.5),
        ("hf_ixa_001", "lognormal", 15, 4),
    ])

    # Number of PSA iterations
    psa_iterations: int = 1000

    # Confidence interval for PSA results
    psa_confidence_level: float = 0.95


@dataclass
class ExtendedBIMInputs(BIMInputs):
    """
    Extended BIM inputs with additional parameters for enhanced analysis.

    Inherits from BIMInputs and adds:
    - Clinical event rates
    - Event costs
    - Subgroup definitions
    - Treatment persistence
    - Sensitivity parameters
    """

    # Clinical events
    event_rates: ClinicalEventRates = field(default_factory=ClinicalEventRates)
    event_costs: EventCosts = field(default_factory=EventCosts)

    # Subgroups
    subgroups: SubgroupDefinitions = field(default_factory=SubgroupDefinitions)

    # Persistence
    persistence: TreatmentPersistence = field(default_factory=TreatmentPersistence)

    # Sensitivity
    sensitivity: SensitivityParameters = field(default_factory=SensitivityParameters)

    # Extended analysis settings
    extended_time_horizon_years: int = 10
    plateau_year: int = 5  # Year after which uptake plateaus
    include_persistence: bool = True
    include_events: bool = True

    # Selected subgroups for analysis (empty = all)
    selected_subgroup_types: List[SubgroupType] = field(default_factory=list)

    @classmethod
    def for_country(cls, country_code: str) -> "ExtendedBIMInputs":
        """Create ExtendedBIMInputs with country-specific defaults."""
        config = COUNTRY_CONFIGS.get(country_code, US_CONFIG)

        population = PopulationInputs(
            total_population=config.default_population,
            adult_proportion=config.adult_proportion,
            hypertension_prevalence=config.hypertension_prevalence,
            resistant_htn_proportion=config.resistant_htn_proportion,
        )

        costs = CostInputs(
            currency=config.currency,
            ixa_001_annual=6_000.0 * config.cost_multiplier,
            spironolactone_annual=180.0 * config.cost_multiplier,
            other_mra_annual=1_800.0 * config.cost_multiplier,
            monitoring_ixa_001=180.0 * config.cost_multiplier,
            monitoring_spironolactone=240.0 * config.cost_multiplier,
            monitoring_other_mra=240.0 * config.cost_multiplier,
            monitoring_no_treatment=120.0 * config.cost_multiplier,
            office_visits_annual=300.0 * config.cost_multiplier,
            ae_management_ixa_001=100.0 * config.cost_multiplier,
            ae_management_spironolactone=300.0 * config.cost_multiplier,
            ae_management_other_mra=200.0 * config.cost_multiplier,
            avoided_events_ixa_001_annual=1_200.0 * config.cost_multiplier,
            avoided_events_spironolactone_annual=800.0 * config.cost_multiplier,
            avoided_events_other_mra_annual=600.0 * config.cost_multiplier,
        )

        # Scale event costs by country multiplier
        event_costs = EventCosts(
            currency=config.currency,
            stroke_acute=35_000.0 * config.cost_multiplier,
            stroke_followup_annual=8_000.0 * config.cost_multiplier,
            mi_acute=28_000.0 * config.cost_multiplier,
            mi_followup_annual=5_000.0 * config.cost_multiplier,
            hf_acute=18_000.0 * config.cost_multiplier,
            hf_followup_annual=12_000.0 * config.cost_multiplier,
            ckd_acute=5_000.0 * config.cost_multiplier,
            ckd_followup_annual=8_000.0 * config.cost_multiplier,
            esrd_acute=50_000.0 * config.cost_multiplier,
            esrd_followup_annual=90_000.0 * config.cost_multiplier,
            cv_death_acute=45_000.0 * config.cost_multiplier,
            all_cause_death_acute=35_000.0 * config.cost_multiplier,
        )

        return cls(
            population=population,
            costs=costs,
            country=config,
            event_costs=event_costs,
        )

    def validate(self) -> List[str]:
        """Validate all inputs including extended parameters."""
        errors = super().validate()

        # Validate subgroup proportions sum to 1
        for subgroup_type in SubgroupType:
            subgroups = self.subgroups.get_subgroups(subgroup_type)
            total_proportion = sum(sg.proportion for sg in subgroups)
            if abs(total_proportion - 1.0) > 0.01:
                errors.append(
                    f"{subgroup_type.value} subgroup proportions must sum to 100% "
                    f"(currently {total_proportion:.1%})"
                )

        if self.extended_time_horizon_years < self.time_horizon_years:
            errors.append(
                "Extended time horizon must be >= standard time horizon"
            )

        return errors
