# Budget Impact Model (BIM) for IXA-001

## Resistant Hypertension - Payer Analysis Tool

**Version:** 1.0
**Date:** February 2026
**Sponsor:** Atlantis Pharmaceuticals

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Model Structure](#model-structure)
5. [Input Parameters](#input-parameters)
6. [Modifying Inputs](#modifying-inputs)
7. [Output Description](#output-description)
8. [Command Line Options](#command-line-options)
9. [Multi-Country Support](#multi-country-support)
10. [Technical Details](#technical-details)
11. [File Structure](#file-structure)
12. [Linking to CEA Model](#linking-to-cea-model)

---

## Overview

This Budget Impact Model (BIM) estimates the financial impact of introducing **IXA-001** (a selective aldosterone synthase inhibitor) to a healthcare plan's formulary for treating **uncontrolled resistant hypertension**.

### What This Model Does

The BIM compares two scenarios over a 5-year time horizon:

| Scenario | Description |
|----------|-------------|
| **Current World** | Standard of care without IXA-001 (spironolactone, other MRAs, or no 4th-line therapy) |
| **New World** | IXA-001 available and gaining market share according to uptake assumptions |

### Key Outputs

- **Total Budget Impact**: Aggregate incremental cost over 5 years
- **PMPM (Per Member Per Month)**: Cost impact per plan member
- **Year-by-Year Breakdown**: Annual budget impact trajectory
- **Market Share Evolution**: How treatment mix changes over time
- **Price Threshold Analysis**: Budget-neutral price point for IXA-001

### Hybrid Approach

This model uses a **hybrid Python + Excel approach**:

- **Python**: Core calculation engine with flexibility for sensitivity analysis, scenario comparison, and programmatic modifications
- **Excel**: User-friendly output workbook for payer discussions with interactive inputs and visualizations

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

```bash
# Navigate to the project directory
cd "/home/dan/Genesis Interview/hypertension_bim"

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openpyxl` | >=3.1.0 | Excel file generation |
| `numpy` | >=1.24.0 | Numerical calculations |

---

## Quick Start

### Basic Usage

```bash
# Run with default settings (US, moderate scenario, 1M population)
python run_bim.py

# Run and compare all scenarios
python run_bim.py --compare-scenarios
```

### Output

The model will:
1. Print results to the console
2. Generate an Excel file: `IXA001_Budget_Impact_Model.xlsx`

---

## Model Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUDGET IMPACT MODEL                          │
│                   IXA-001 in Resistant HTN                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  POPULATION  │───▶│   MARKET     │───▶│    COST      │      │
│  │    MODULE    │    │    MODULE    │    │    MODULE    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  • Plan size         • Current Tx mix    • Drug costs          │
│  • HTN prevalence    • IXA-001 uptake    • Monitoring          │
│  • Resistant HTN %   • Displacement      • AE management       │
│  • Eligible patients • Scenario curves   • Avoided events      │
│                                                                 │
│                           │                                     │
│                           ▼                                     │
│                  ┌──────────────────┐                           │
│                  │     OUTPUTS      │                           │
│                  └──────────────────┘                           │
│                  • Total Budget Impact                          │
│                  • PMPM Impact                                  │
│                  • Year-by-Year Breakdown                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Input Parameters

### 1. Population Inputs

These parameters define the patient cascade from total plan membership to eligible patients.

| Parameter | Default (US) | Description | Impact on Model |
|-----------|--------------|-------------|-----------------|
| `total_population` | 1,000,000 | Total plan membership (lives) | Directly scales all patient counts and costs |
| `adult_proportion` | 78% | Proportion aged 18+ | Filters to adult population |
| `hypertension_prevalence` | 30% | HTN prevalence in adults | Key driver of eligible population |
| `resistant_htn_proportion` | 12% | % of HTN that is resistant | Critical epidemiology parameter |
| `uncontrolled_proportion` | 50% | % of resistant HTN uncontrolled | Defines treatment-eligible subset |
| `treatment_seeking_rate` | 80% | % seeking active treatment | Final filter for eligible patients |

**Patient Cascade Calculation:**
```
Eligible = Population × Adult% × HTN% × Resistant% × Uncontrolled% × Treatment-Seeking%
Example: 1,000,000 × 0.78 × 0.30 × 0.12 × 0.50 × 0.80 = 11,232 patients
```

### 2. Market Inputs

These parameters define the baseline treatment landscape and IXA-001 uptake dynamics.

#### Baseline Market Shares (Current World - No IXA-001)

| Treatment | Default | Description |
|-----------|---------|-------------|
| `baseline_spironolactone` | 60% | Patients on spironolactone as 4th-line |
| `baseline_other_mra` | 15% | Patients on eplerenone or other MRA |
| `baseline_no_4th_line` | 25% | Patients with no 4th-line therapy |

**Note:** These must sum to 100%.

#### IXA-001 Uptake Scenarios

| Scenario | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
|----------|--------|--------|--------|--------|--------|
| Conservative | 5% | 10% | 15% | 18% | 20% |
| Moderate | 10% | 20% | 30% | 35% | 40% |
| Optimistic | 15% | 30% | 45% | 50% | 55% |

#### Displacement Assumptions

When patients switch to IXA-001, they come from:

| Source | Default | Description |
|--------|---------|-------------|
| `displacement_from_spironolactone` | 70% | Switching from spironolactone |
| `displacement_from_other_mra` | 20% | Switching from other MRAs |
| `displacement_from_untreated` | 10% | Previously untreated (new starts) |

**Note:** These must sum to 100%.

### 3. Cost Inputs (Annual, Per Patient)

#### Drug Costs

| Parameter | US Default | UK Default | Description |
|-----------|------------|------------|-------------|
| `ixa_001_annual` | $6,000 | £2,400 | IXA-001 annual drug cost |
| `spironolactone_annual` | $180 | £72 | Generic spironolactone |
| `other_mra_annual` | $1,800 | £720 | Eplerenone (branded) |
| `no_treatment_annual` | $0 | £0 | No 4th-line drug cost |

#### Monitoring Costs

| Parameter | US Default | UK Default | Description |
|-----------|------------|------------|-------------|
| `monitoring_ixa_001` | $180 | £72 | Less frequent K+ monitoring |
| `monitoring_spironolactone` | $240 | £96 | Quarterly K+ checks required |
| `monitoring_other_mra` | $240 | £96 | Similar to spironolactone |
| `monitoring_no_treatment` | $120 | £48 | Basic BP monitoring only |

#### Other Costs

| Parameter | US Default | UK Default | Description |
|-----------|------------|------------|-------------|
| `office_visits_annual` | $300 | £120 | Routine office visits |
| `ae_management_ixa_001` | $100 | £40 | Lower AE burden |
| `ae_management_spironolactone` | $300 | £120 | Hyperkalemia, gynecomastia |
| `ae_management_other_mra` | $200 | £80 | Moderate AE burden |

#### Avoided Event Offsets (from CEA Model)

| Parameter | US Default | Description |
|-----------|------------|-------------|
| `avoided_events_ixa_001_annual` | $1,200 | CV event cost savings per patient |
| `avoided_events_spironolactone_annual` | $800 | Baseline comparator savings |
| `avoided_events_other_mra_annual` | $600 | Other MRA savings |

### 4. Analysis Settings

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `time_horizon_years` | 5 | 1-5 | Analysis period |
| `selected_scenario` | Moderate | Conservative, Moderate, Optimistic | Uptake scenario |
| `include_event_offsets` | Yes | Yes/No | Include avoided CV events |

---

## Modifying Inputs

### Method 1: Command Line Arguments

```bash
# Change country
python run_bim.py --country UK

# Change scenario
python run_bim.py --scenario optimistic

# Change population size
python run_bim.py --population 500000

# Change IXA-001 price
python run_bim.py --ixa-price 4500

# Combine multiple options
python run_bim.py --country UK --population 500000 --scenario conservative
```

### Method 2: Modify Python Code

Edit `run_bim.py` or create a custom script:

```python
from src.bim import BIMInputs, BIMCalculator, ExcelGenerator, UptakeScenario

# Create inputs with country defaults
inputs = BIMInputs.for_country("US")

# Modify population parameters
inputs.population.total_population = 2_000_000
inputs.population.resistant_htn_proportion = 0.15  # 15% instead of 12%

# Modify market assumptions
inputs.market.baseline_spironolactone = 0.70  # 70% on spiro

# Modify costs
inputs.costs.ixa_001_annual = 5_000  # Lower price point

# Modify uptake curves (custom scenario)
inputs.market.uptake_curves[UptakeScenario.MODERATE] = [0.08, 0.15, 0.25, 0.30, 0.35]

# Run calculation
calculator = BIMCalculator(inputs)
results = calculator.calculate(scenario=UptakeScenario.MODERATE)

# Generate Excel
generator = ExcelGenerator(inputs, results)
generator.generate("Custom_BIM_Output.xlsx")
```

### Method 3: Edit the Excel Output

After generating the Excel file, you can:

1. Open `IXA001_Budget_Impact_Model.xlsx`
2. Go to the **Input Dashboard** sheet
3. Modify the yellow-highlighted cells
4. Values will update in linked cells (note: full recalculation requires re-running Python)

**Important:** The Excel file is primarily for **presentation and payer discussions**. For full recalculation with modified inputs, use the Python script.

### What Happens When You Change Inputs

| Input Changed | Effect on Model |
|---------------|-----------------|
| **Population size** | All patient counts and total costs scale proportionally |
| **HTN prevalence** | Eligible patients change; budget impact scales accordingly |
| **Resistant HTN %** | Major driver; small changes have large impact on eligible population |
| **IXA-001 price** | Directly affects incremental cost per patient and total budget impact |
| **Uptake scenario** | Changes trajectory of budget impact (faster uptake = higher early costs) |
| **Displacement assumptions** | Affects which treatments IXA-001 replaces (cost differential varies) |
| **Avoided events** | If disabled, removes cost offsets; increases net budget impact |

---

## Output Description

### Console Output

```
======================================================================
BUDGET IMPACT MODEL RESULTS
Country: United States
Scenario: Moderate
======================================================================

POPULATION SIZING
  Total Plan Population:           1,000,000
  Eligible for Treatment:             11,232

KEY METRICS
  5-Year Budget Impact:      $    72,712,540
  Average Annual Impact:     $    14,542,508
  Year 1 PMPM:               $          0.45
  Year 5 PMPM:               $          1.80

YEAR-BY-YEAR BREAKDOWN
  Year   IXA-001 Pts   Current World      New World        Impact
  1            1,123   $    5,928,900   $   11,315,480   $  5,386,580
  ...
```

### Excel Output Sheets

| Sheet | Description | Use Case |
|-------|-------------|----------|
| **Cover** | Model overview, key results, quick start guide | Executive summary |
| **Input Dashboard** | All modifiable inputs in one place | Parameter review |
| **Population** | Patient cascade breakdown with percentages | Epidemiology discussion |
| **Market Dynamics** | Baseline shares, uptake curves, chart | Market assumptions |
| **Costs** | Per-patient cost breakdown by treatment | Cost justification |
| **Results Dashboard** | Key metrics, year-by-year table, charts | Main presentation slide |
| **Scenario Comparison** | Side-by-side Conservative/Moderate/Optimistic | Risk assessment |
| **Sensitivity** | Price and prevalence sensitivity tables | Uncertainty analysis |
| **Documentation** | Data sources, assumptions, limitations | Technical appendix |

---

## Command Line Options

```bash
python run_bim.py [OPTIONS]

Options:
  --country {US,UK,DE,FR,IT,ES}    Country for analysis (default: US)
  --scenario {conservative,moderate,optimistic}
                                    Uptake scenario (default: moderate)
  --population INTEGER              Total plan population (default: 1,000,000)
  --ixa-price FLOAT                 Annual IXA-001 drug cost (overrides default)
  --output FILENAME                 Output Excel filename (default: IXA001_Budget_Impact_Model.xlsx)
  --no-excel                        Skip Excel generation (console only)
  --compare-scenarios               Compare all uptake scenarios
```

### Examples

```bash
# US market with optimistic uptake
python run_bim.py --scenario optimistic

# UK market with 500K population
python run_bim.py --country UK --population 500000

# Price sensitivity test
python run_bim.py --ixa-price 4000 --output BIM_Price4000.xlsx

# Console output only (no Excel)
python run_bim.py --no-excel --compare-scenarios

# Generate for all EU5 markets
for country in UK DE FR IT ES; do
    python run_bim.py --country $country --output "BIM_${country}.xlsx"
done
```

---

## Multi-Country Support

The model supports 6 markets with pre-configured defaults:

| Country | Code | Currency | Cost Multiplier | HTN Prevalence |
|---------|------|----------|-----------------|----------------|
| United States | US | USD ($) | 1.00 | 30% |
| United Kingdom | UK | GBP (£) | 0.40 | 28% |
| Germany | DE | EUR (€) | 0.50 | 32% |
| France | FR | EUR (€) | 0.45 | 30% |
| Italy | IT | EUR (€) | 0.42 | 33% |
| Spain | ES | EUR (€) | 0.38 | 33% |

**Note:** Cost multipliers are applied to US base costs. Epidemiology parameters are country-specific based on published literature.

---

## Technical Details

### Calculation Methodology

1. **Eligible Population**: Cascade calculation from plan size through epidemiology filters

2. **Market Share Projection**: For each year, IXA-001 uptake displaces existing treatments according to displacement assumptions

3. **Cost Calculation**:
   ```
   Annual Budget Impact =
       Σ(Patients_treatment × Cost_treatment) [New World]
     - Σ(Patients_treatment × Cost_treatment) [Current World]
   ```

4. **PMPM Calculation**:
   ```
   PMPM = Annual Budget Impact / Total Population / 12 months
   ```

### Key Assumptions

- Population remains stable over the analysis period
- Treatment costs are applied for full year per patient
- No discounting applied (standard BIM practice)
- Avoided CV events are calculated from linked CEA model
- Treatment adherence and discontinuation not explicitly modeled

### Data Sources

| Category | Source |
|----------|--------|
| Epidemiology | NHANES, ESC Guidelines, Carey et al. Circulation 2018 |
| Drug Costs | RED BOOK/WAC (US), BNF/MIMS (UK/EU) |
| Medical Costs | CMS Fee Schedule (US), NHS Reference Costs (UK) |
| Market Shares | IQVIA, Symphony Health |
| CV Event Rates | Linked IXA-001 Cost-Effectiveness Model |

---

## File Structure

```
hypertension_bim/
├── README.md                         # This file
├── requirements.txt                  # Python dependencies
├── run_bim.py                        # Main runner script
├── IXA001_Budget_Impact_Model.xlsx   # Generated Excel (US)
├── IXA001_BIM_UK.xlsx               # Generated Excel (UK)
└── src/
    ├── __init__.py
    └── bim/
        ├── __init__.py               # Package exports
        ├── inputs.py                 # Data classes for all inputs
        ├── calculator.py             # Core calculation engine
        └── excel_generator.py        # Excel workbook generator
```

---

## Linking to CEA Model

The BIM uses avoided event costs derived from the **Cost-Effectiveness Analysis (CEA) Model** located in the companion `hypertension_microsim` project.

### How Avoided Events Are Calculated

From the CEA microsimulation results:

| Treatment | CV Events Avoided (vs. no treatment) | Annual Cost Offset |
|-----------|--------------------------------------|-------------------|
| IXA-001 | ~37 fewer strokes per 1000 | $1,200/patient/year |
| Spironolactone | ~18 fewer strokes per 1000 | $800/patient/year |
| Other MRA | ~12 fewer strokes per 1000 | $600/patient/year |

### Updating Avoided Event Values

If the CEA model is re-run with updated parameters:

```python
# Update avoided event costs based on new CEA results
inputs.costs.avoided_events_ixa_001_annual = 1500  # New value
inputs.costs.avoided_events_spironolactone_annual = 900
```

---

## Support

For questions about this model, contact:

**Atlantis Pharmaceuticals - HEOR Team**

---

*Model developed: February 2026*
