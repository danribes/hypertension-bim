# Budget Impact Model (BIM) Technical Guide

## Overview

This document explains how the Budget Impact Model calculates the financial impact of introducing IXA-001 for resistant hypertension treatment. Unlike the microsimulation CEA, the BIM is a **cohort-level deterministic model** that operates on population aggregates.

**Key distinction from microsimulation:**
- No patient-level stochasticity (first-order uncertainty)
- Uncertainty is captured solely through PSA (second-order/parameter uncertainty)
- Calculations use expected values applied to cohort proportions

---

## Table of Contents

1. [Model Architecture](#1-model-architecture)
2. [Population Funnel](#2-population-funnel)
3. [Market Dynamics](#3-market-dynamics)
4. [Budget Impact Calculation](#4-budget-impact-calculation)
5. [Clinical Event Analysis](#5-clinical-event-analysis)
6. [Subgroup Stratification](#6-subgroup-stratification)
7. [Sensitivity Analysis](#7-sensitivity-analysis)
8. [Key Code References](#8-key-code-references)

---

## 1. Model Architecture

### 1.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUDGET IMPACT MODEL FLOW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                              │
│   │  POPULATION  │                                              │
│   │    FUNNEL    │                                              │
│   │              │                                              │
│   │ 1M members   │                                              │
│   │      ↓       │                                              │
│   │ 11,232       │                                              │
│   │ eligible     │                                              │
│   └──────┬───────┘                                              │
│          │                                                      │
│          ▼                                                      │
│   ┌──────────────┐    ┌──────────────┐                         │
│   │   CURRENT    │    │     NEW      │                         │
│   │    WORLD     │    │    WORLD     │                         │
│   │  (No IXA)    │    │ (With IXA)   │                         │
│   │              │    │              │                         │
│   │ Spiro: 60%   │    │ IXA: 10-55%  │                         │
│   │ MRA:   15%   │    │ Spiro: ↓     │                         │
│   │ None:  25%   │    │ MRA:   ↓     │                         │
│   └──────┬───────┘    └──────┬───────┘                         │
│          │                   │                                  │
│          ▼                   ▼                                  │
│   ┌──────────────────────────────────────┐                     │
│   │          BUDGET IMPACT               │                     │
│   │                                      │                     │
│   │  Impact = Cost_New - Cost_Current    │                     │
│   │                                      │                     │
│   │  Year 1 → Year 2 → ... → Year 5      │                     │
│   └──────────────────────────────────────┘                     │
│                         │                                       │
│                         ▼                                       │
│   ┌──────────────────────────────────────┐                     │
│   │              OUTPUTS                 │                     │
│   │                                      │                     │
│   │  • 5-Year Total Impact               │                     │
│   │  • PMPM (Per Member Per Month)       │                     │
│   │  • Events Avoided                    │                     │
│   │  • Subgroup Analysis                 │                     │
│   │  • Sensitivity (Tornado, PSA)        │                     │
│   └──────────────────────────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Model Types Comparison

| Characteristic | BIM (This Model) | Microsimulation CEA |
|----------------|------------------|---------------------|
| Unit of analysis | Cohort/population | Individual patients |
| Stochasticity | None (deterministic) | Per-patient event sampling |
| Uncertainty | PSA only (parameter) | PSA + first-order |
| Outputs | Budget impact, PMPM | ICER, QALYs, events |
| Time horizon | 5-10 years | 40 years |
| Discounting | None (budget perspective) | 3% annual |

---

## 2. Population Funnel

### 2.1 Epidemiological Cascade

The eligible population is derived through a sequential filter:

```
┌─────────────────────────────────────────────────────────────┐
│                   POPULATION CASCADE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Total Plan Population ────────────────────► 1,000,000     │
│         │                                                   │
│         │ × 78% adults (18+)                               │
│         ▼                                                   │
│  Adult Population ─────────────────────────► 780,000       │
│         │                                                   │
│         │ × 30% hypertension prevalence                    │
│         ▼                                                   │
│  Hypertension Patients ────────────────────► 234,000       │
│         │                                                   │
│         │ × 12% resistant HTN                              │
│         ▼                                                   │
│  Resistant Hypertension ───────────────────► 28,080        │
│         │                                                   │
│         │ × 50% uncontrolled                               │
│         ▼                                                   │
│  Uncontrolled Resistant HTN ───────────────► 14,040        │
│         │                                                   │
│         │ × 80% treatment-seeking                          │
│         ▼                                                   │
│  ═══════════════════════════════════════════════════════   │
│  ELIGIBLE FOR IXA-001 ─────────────────────► 11,232        │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Calculation Formula

```python
eligible_patients = (
    total_population
    × adult_proportion           # 0.78
    × hypertension_prevalence    # 0.30
    × resistant_htn_proportion   # 0.12
    × uncontrolled_proportion    # 0.50
    × treatment_seeking_rate     # 0.80
)
```

**Reference**: `inputs.py:65-75`

---

## 3. Market Dynamics

### 3.1 Baseline Market (Current World)

Without IXA-001, the market consists of:

| Treatment | Market Share | Annual Cost |
|-----------|--------------|-------------|
| Spironolactone | 60% | $180 |
| Other MRA (Eplerenone) | 15% | $1,800 |
| No 4th-line therapy | 25% | $0 |

### 3.2 Uptake Scenarios

IXA-001 uptake follows predefined curves over 5 years:

| Scenario | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
|----------|--------|--------|--------|--------|--------|
| Conservative | 5% | 10% | 15% | 18% | 20% |
| Moderate | 10% | 20% | 30% | 35% | 40% |
| Optimistic | 15% | 30% | 45% | 50% | 55% |

**Reference**: `inputs.py:106-110`

### 3.3 Displacement Assumptions

When patients switch to IXA-001, they are displaced from:

```
IXA-001 patients come from:
├── 70% from Spironolactone
├── 20% from Other MRA
└── 10% from No Treatment (new to 4th-line)
```

### 3.4 Market Share Calculation (New World)

For each year, market shares in the new world are calculated:

```python
def _calculate_year(self, year, eligible_patients, scenario):
    # Get IXA uptake for this year
    ixa_uptake = self.inputs.market.get_uptake(scenario, year)

    # Calculate displacement from each segment
    displaced_spiro = ixa_uptake × displacement_from_spironolactone  # 0.70
    displaced_mra = ixa_uptake × displacement_from_other_mra          # 0.20
    displaced_untreated = ixa_uptake × displacement_from_untreated    # 0.10

    # New shares = baseline - displaced
    share_spiro_new = baseline_spironolactone - displaced_spiro
    share_mra_new = baseline_other_mra - displaced_mra
    share_none_new = baseline_no_4th_line - displaced_untreated

    # Normalize to ensure sum = 1.0
```

**Reference**: `calculator.py:188-281`

---

## 4. Budget Impact Calculation

### 4.1 Per-Patient Annual Costs

Total cost per patient includes:

```
Annual Cost = Drug Cost
            + Monitoring Cost
            + Office Visits
            + AE Management
            - Avoided Event Costs (if enabled)
```

| Component | IXA-001 | Spironolactone | Other MRA | No Treatment |
|-----------|---------|----------------|-----------|--------------|
| Drug | $6,000 | $180 | $1,800 | $0 |
| Monitoring | $180 | $240 | $240 | $120 |
| Office visits | $300 | $300 | $300 | $300 |
| AE management | $100 | $300 | $200 | $0 |
| Avoided events | -$1,200 | -$800 | -$600 | $0 |
| **Total** | **$5,380** | **$220** | **$1,940** | **$420** |

**Reference**: `inputs.py:171-206`

### 4.2 Annual Budget Impact Formula

```
Budget Impact (Year t) = Cost_NewWorld(t) - Cost_CurrentWorld(t)

where:

Cost_NewWorld(t) = Σ [patients_i(t) × cost_per_patient_i]
                   for i ∈ {IXA-001, Spiro, MRA, None}

Cost_CurrentWorld(t) = Σ [patients_baseline_j × cost_per_patient_j]
                       for j ∈ {Spiro, MRA, None}  (no IXA-001)
```

### 4.3 Summary Metrics

```python
# 5-Year Total Impact
total_5yr = Σ budget_impact[year] for year in 1..5

# Per Member Per Month (PMPM)
pmpm_year_t = budget_impact[year_t] / total_population / 12
```

**Reference**: `calculator.py:157-174`

---

## 5. Clinical Event Analysis

### 5.1 Event Types Tracked

| Event | IXA-001 Rate | Spiro Rate | No Tx Rate | Acute Cost |
|-------|--------------|------------|------------|------------|
| Stroke | 8.0‰ | 12.0‰ | 18.0‰ | $35,000 |
| MI | 6.0‰ | 9.0‰ | 14.0‰ | $28,000 |
| HF Hospitalization | 15.0‰ | 22.0‰ | 35.0‰ | $18,000 |
| CKD Progression | 20.0‰ | 28.0‰ | 40.0‰ | $5,000 |
| ESRD | 3.0‰ | 5.0‰ | 8.0‰ | $50,000 |
| CV Death | 4.0‰ | 6.0‰ | 10.0‰ | $45,000 |

*Rates are per 1,000 patient-years*

**Reference**: `inputs.py:388-450`

### 5.2 Events Avoided Calculation

```python
def _calculate_events(self, scenario):
    for year in range(1, time_horizon + 1):
        for event in EventType:
            # Events in new world (with IXA-001)
            events_new = (
                patients_ixa × rate_ixa +
                patients_spiro × rate_spiro +
                patients_mra × rate_mra +
                patients_none × rate_none
            )

            # Events in current world (no IXA-001)
            events_current = (
                patients_spiro_baseline × rate_spiro +
                patients_mra_baseline × rate_mra +
                patients_none_baseline × rate_none
            )

            # Events avoided
            events_avoided = events_current - events_new

            # Cost savings
            cost_avoided = events_avoided × acute_cost
```

**Reference**: `calculator.py:646-722`

---

## 6. Subgroup Stratification

### 6.1 Available Subgroups

| Subgroup Type | Categories | Key Modifier |
|---------------|------------|--------------|
| Age | <65, 65-74, 75+ | Risk multipliers |
| CKD Stage | Stage 1-2, 3, 4 | Event risk |
| Prior CV | No/Yes | Treatment benefit |
| Diabetes | No/Yes | Complication rate |
| Secondary HTN | PA, RAS, Pheo, OSA, Essential | Treatment response |

### 6.2 Secondary HTN Etiology (Key Stratification)

```
┌─────────────────────────────────────────────────────────────┐
│              SECONDARY HTN ETIOLOGY SUBGROUPS               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Primary Aldosteronism (PA) ────────── 17%                 │
│    • HF risk: 2.05×                                        │
│    • CKD risk: 1.80×                                       │
│    • IXA-001 response: 1.70× (OPTIMAL TARGET)              │
│                                                             │
│  Renal Artery Stenosis (RAS) ───────── 11%                 │
│    • CKD risk: 1.80×                                       │
│    • IXA-001 response: 1.05× (minimal benefit)             │
│                                                             │
│  Pheochromocytoma (Pheo) ───────────── 1%                  │
│    • Death risk: 2.00×                                     │
│    • IXA-001 response: 0.40× (CONTRAINDICATED)             │
│                                                             │
│  Obstructive Sleep Apnea (OSA) ─────── 15%                 │
│    • Stroke risk: 1.25×                                    │
│    • IXA-001 response: 1.20× (modest benefit)              │
│                                                             │
│  Essential HTN (No secondary cause) ── 56%                 │
│    • All risks: 1.0× (baseline)                            │
│    • IXA-001 response: 1.0× (standard)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Reference**: `inputs.py:683-741`

### 6.3 Subgroup Calculation

For each subgroup, the model:
1. Scales the population by subgroup proportion
2. Applies risk multipliers to event rates
3. Applies treatment effect modifiers
4. Runs independent BIM calculation

```python
def _calculate_subgroups(self, scenario):
    for subgroup_type in selected_subgroup_types:
        for sg in subgroups.get_subgroups(subgroup_type):
            # Scale population
            sg_patients = eligible × sg.proportion

            # Apply risk multipliers
            sg_inputs.event_rates.stroke_ixa_001 *= sg.stroke_risk_multiplier
            sg_inputs.event_rates.mi_ixa_001 *= sg.mi_risk_multiplier
            sg_inputs.event_rates.hf_ixa_001 *= sg.hf_risk_multiplier

            # Run calculation
            sg_calculator = BIMCalculator(sg_inputs)
            sg_results = sg_calculator.calculate(scenario)
```

**Reference**: `calculator.py:724-772`

---

## 7. Sensitivity Analysis

### 7.1 Deterministic Sensitivity Analysis (Tornado)

One-way DSA varies each parameter ±20-50% while holding others constant:

```python
def run_tornado_analysis(self, scenario):
    base_impact = self.calculate(scenario).total_budget_impact_5yr

    for param_name, low_mult, high_mult in tornado_parameters:
        base_value = get_parameter(param_name)

        # Test low
        set_parameter(param_name, base_value × low_mult)
        impact_at_low = calculate(scenario).total_budget_impact_5yr

        # Test high
        set_parameter(param_name, base_value × high_mult)
        impact_at_high = calculate(scenario).total_budget_impact_5yr

        # Restore
        set_parameter(param_name, base_value)

        # Record impact range
        impact_range = abs(impact_at_high - impact_at_low)
```

**Key parameters tested:**
- IXA-001 annual cost (±25%)
- Resistant HTN proportion (±25%)
- Treatment seeking rate (±20%)
- Avoided event costs (±50%)
- Discontinuation rates (±50%)

**Reference**: `calculator.py:933-992`

### 7.2 Probabilistic Sensitivity Analysis (PSA)

Monte Carlo sampling from parameter distributions:

```
┌─────────────────────────────────────────────────────────────┐
│                    PSA WORKFLOW (BIM)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  For iteration k = 1 to N (default 1,000):                  │
│                                                             │
│    1. Sample parameters from distributions:                 │
│       ┌───────────────────────────────────────────────┐    │
│       │ ixa_001_annual ~ Lognormal(6000, 600)         │    │
│       │ spironolactone_annual ~ Lognormal(180, 20)    │    │
│       │ resistant_htn_proportion ~ Beta(12, 88)       │    │
│       │ treatment_seeking_rate ~ Beta(80, 20)         │    │
│       │ stroke_ixa_001 ~ Lognormal(8, 2)              │    │
│       │ mi_ixa_001 ~ Lognormal(6, 1.5)                │    │
│       │ hf_ixa_001 ~ Lognormal(15, 4)                 │    │
│       └───────────────────────────────────────────────┘    │
│                                                             │
│    2. Apply sampled parameters to model                     │
│                                                             │
│    3. Run DETERMINISTIC budget impact calculation           │
│       (No patient-level randomness)                         │
│                                                             │
│    4. Store result: impact_results[k]                       │
│                                                             │
│  End loop                                                   │
│                                                             │
│  Calculate statistics:                                      │
│    • Mean, Median, SD                                       │
│    • 95% Confidence Interval                                │
│    • P(Budget Increase > 0)                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Reference**: `calculator.py:1036-1111`

### 7.3 Distribution Types

| Distribution | Used For | Parameters |
|--------------|----------|------------|
| Lognormal | Costs, Event rates | mean, sd |
| Beta | Proportions, Rates | alpha, beta |

```python
# Lognormal sampling
if dist_type == "lognormal":
    mu = ln(mean² / √(sd² + mean²))
    sigma = √(ln(1 + sd²/mean²))
    sampled = np.random.lognormal(mu, sigma)

# Beta sampling
if dist_type == "beta":
    sampled = np.random.beta(alpha, beta)
```

**Reference**: `calculator.py:1064-1076`

### 7.4 PSA Outputs

```python
PSAResults:
    iterations: int              # Number of iterations
    impact_distribution: List    # All sampled budget impacts
    mean_impact: float           # Mean 5-year impact
    median_impact: float         # Median 5-year impact
    std_impact: float            # Standard deviation
    ci_lower: float              # 2.5th percentile
    ci_upper: float              # 97.5th percentile
    prob_budget_increase: float  # P(Impact > 0)
    pmpm_distribution: List      # PMPM values
```

**Reference**: `calculator.py:493-515`

---

## 8. Key Code References

### 8.1 Core Calculator

| Component | File:Lines | Description |
|-----------|------------|-------------|
| Base calculation | `calculator.py:128-186` | `BIMCalculator.calculate()` |
| Year calculation | `calculator.py:188-281` | `_calculate_year()` |
| Enhanced calculator | `calculator.py:567-644` | `EnhancedBIMCalculator` |

### 8.2 Event Analysis

| Component | File:Lines | Description |
|-----------|------------|-------------|
| Event calculation | `calculator.py:646-722` | `_calculate_events()` |
| Event rates | `inputs.py:388-450` | `ClinicalEventRates` |
| Event costs | `inputs.py:452-502` | `EventCosts` |

### 8.3 Subgroup Analysis

| Component | File:Lines | Description |
|-----------|------------|-------------|
| Subgroup calculation | `calculator.py:724-772` | `_calculate_subgroups()` |
| Subgroup definitions | `inputs.py:524-754` | `SubgroupDefinitions` |
| Secondary HTN etiology | `inputs.py:683-741` | PA, RAS, Pheo, OSA, Essential |

### 8.4 Sensitivity Analysis

| Component | File:Lines | Description |
|-----------|------------|-------------|
| Tornado analysis | `calculator.py:933-992` | `run_tornado_analysis()` |
| PSA | `calculator.py:1036-1111` | `run_probabilistic_sensitivity()` |
| Distribution parameters | `inputs.py:826-844` | `SensitivityParameters` |

### 8.5 Input Classes

| Component | File:Lines | Description |
|-----------|------------|-------------|
| Population inputs | `inputs.py:50-93` | Population funnel |
| Market inputs | `inputs.py:96-136` | Uptake curves, displacement |
| Cost inputs | `inputs.py:138-207` | Drug, monitoring, AE costs |
| Persistence | `inputs.py:756-803` | Discontinuation rates |

---

## Summary

The Budget Impact Model is a **cohort-level deterministic model** that calculates the financial impact of introducing IXA-001 by comparing:

- **Current World**: Market without IXA-001 (Spiro 60%, MRA 15%, None 25%)
- **New World**: Market with IXA-001 uptake following scenario curves

**Key features:**
1. **Population funnel** derives eligible patients through epidemiological cascade
2. **Market dynamics** model displacement from existing treatments
3. **Event analysis** quantifies clinical outcomes and cost offsets
4. **Subgroup stratification** identifies high-value segments (especially PA patients)
5. **Sensitivity analysis** characterizes parameter uncertainty via PSA

**Unlike the microsimulation:**
- No first-order (patient-level) stochasticity
- All calculations are deterministic given parameters
- Uncertainty is captured solely through second-order (parameter) PSA

---

*Generated: 2026-02-05*
*Model Version: BIM v2.0 with Secondary HTN Etiology Stratification*
