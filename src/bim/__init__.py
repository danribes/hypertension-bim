"""
Budget Impact Model (BIM) for IXA-001 in Resistant Hypertension.

This module provides:
- BIMInputs: Data classes for model parameters
- BIMCalculator: Core calculation engine
- ExcelGenerator: User-friendly Excel output generation
- ExtendedBIMInputs: Enhanced inputs with events, subgroups, persistence
- EnhancedBIMCalculator: Extended calculator with PSA, tornado, subgroups
- EnhancedExcelGenerator: Extended Excel output with additional analysis sheets
"""

from .inputs import (
    BIMInputs,
    PopulationInputs,
    MarketInputs,
    CostInputs,
    UptakeScenario,
    CountryConfig,
    US_CONFIG,
    UK_CONFIG,
    GERMANY_CONFIG,
    FRANCE_CONFIG,
    ITALY_CONFIG,
    SPAIN_CONFIG,
    COUNTRY_CONFIGS,
    # Enhanced inputs
    EventType,
    SubgroupType,
    ClinicalEventRates,
    EventCosts,
    SubgroupParameters,
    SubgroupDefinitions,
    TreatmentPersistence,
    SensitivityParameters,
    ExtendedBIMInputs,
)
from .calculator import (
    BIMCalculator,
    BIMResults,
    YearlyResults,
    # Enhanced calculator
    EnhancedBIMCalculator,
    ExtendedBIMResults,
    EventResults,
    SubgroupResults,
    PersistenceResults,
    TornadoResult,
    PSAResults,
)
from .excel_generator import ExcelGenerator
from .excel_enhanced import EnhancedExcelGenerator

__all__ = [
    # Base inputs
    "BIMInputs",
    "PopulationInputs",
    "MarketInputs",
    "CostInputs",
    "UptakeScenario",
    "CountryConfig",
    "US_CONFIG",
    "UK_CONFIG",
    "GERMANY_CONFIG",
    "FRANCE_CONFIG",
    "ITALY_CONFIG",
    "SPAIN_CONFIG",
    "COUNTRY_CONFIGS",
    # Enhanced inputs
    "EventType",
    "SubgroupType",
    "ClinicalEventRates",
    "EventCosts",
    "SubgroupParameters",
    "SubgroupDefinitions",
    "TreatmentPersistence",
    "SensitivityParameters",
    "ExtendedBIMInputs",
    # Base calculator
    "BIMCalculator",
    "BIMResults",
    "YearlyResults",
    # Enhanced calculator
    "EnhancedBIMCalculator",
    "ExtendedBIMResults",
    "EventResults",
    "SubgroupResults",
    "PersistenceResults",
    "TornadoResult",
    "PSAResults",
    # Excel generators
    "ExcelGenerator",
    "EnhancedExcelGenerator",
]
