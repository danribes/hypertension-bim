# IXA-001 Budget Impact Model: Comprehensive Technical Documentation

## Resistant Hypertension Treatment - Budget Impact Analysis

**Document Version:** 1.0
**Date:** February 2026
**Author:** HEOR Technical Documentation Team
**Regulatory Context:** HTA Submission Package
**Status:** Final

---

# Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Model Overview](#2-model-overview)
3. [Population & Epidemiology](#3-population--epidemiology)
4. [Market Dynamics](#4-market-dynamics)
5. [Cost Inputs](#5-cost-inputs)
6. [Clinical Events](#6-clinical-events)
7. [Treatment Persistence](#7-treatment-persistence)
8. [Subgroup Analysis](#8-subgroup-analysis)
9. [Sensitivity Analysis](#9-sensitivity-analysis)
10. [Results Summary](#10-results-summary)
11. [Validation & Quality Assurance](#11-validation--quality-assurance)
12. [References](#12-references)

---

# 1. Executive Summary

## 1.1 Purpose

This comprehensive technical document consolidates all methodological details of the IXA-001 Budget Impact Model (BIM) for Health Technology Assessment (HTA) submission. The model projects the 5-year financial impact of introducing IXA-001 for treatment of resistant hypertension from the payer perspective.

## 1.2 Model Overview

| Attribute | Specification |
|-----------|---------------|
| **Model Type** | Prevalence-based budget impact model |
| **Time Horizon** | 5 years |
| **Perspective** | US Healthcare Payer |
| **Population** | Adults with resistant hypertension |
| **Intervention** | IXA-001 (novel MRA) |
| **Comparators** | Spironolactone, Eplerenone, Other MRAs |
| **Countries** | US, UK, DE, FR, IT, ES |

## 1.3 Key Results (US, Moderate Scenario)

| Metric | Value |
|--------|-------|
| 5-Year Net Budget Impact | $18.33 billion |
| Peak Annual Budget Impact | $6.08 billion (Year 5) |
| Events Prevented | 61,050 |
| Cost Offset from Events | $1.50 billion |
| Patients Treated (Year 5) | 1.23 million |

## 1.4 Documentation Structure

This document integrates six standalone technical reports:

| Report | Section | Content |
|--------|---------|---------|
| Population & Epidemiology | Section 3 | Eligible population calculation |
| Market Dynamics | Section 4 | Uptake curves, displacement |
| Cost Inputs | Section 5 | Drug, event, and monitoring costs |
| Clinical Events | Section 6 | Event rates and treatment effects |
| Treatment Persistence | Section 7 | Adherence and discontinuation |
| Subgroup Analysis | Section 8 | PA, CKD, age stratification |
| Sensitivity Analysis | Section 9 | DSA, PSA, scenarios |

---

# 2. Model Overview

## 2.1 Conceptual Framework

The BIM uses the ISPOR-recommended "world with" versus "world without" framework:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BUDGET IMPACT MODEL STRUCTURE                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────┐     ┌──────────────────────┐             │
│  │   WORLD WITHOUT      │     │    WORLD WITH        │             │
│  │   IXA-001            │     │    IXA-001           │             │
│  │                      │     │                      │             │
│  │  Spironolactone 45%  │     │  IXA-001       20%   │             │
│  │  Eplerenone     25%  │ vs  │  Spironolactone 35%  │             │
│  │  Other MRAs     20%  │     │  Eplerenone    19%   │             │
│  │  No MRA         10%  │     │  Other         17%   │             │
│  │                      │     │  No MRA         9%   │             │
│  └──────────────────────┘     └──────────────────────┘             │
│            │                            │                           │
│            ▼                            ▼                           │
│  ┌──────────────────────┐     ┌──────────────────────┐             │
│  │  Total Cost (Without)│     │  Total Cost (With)   │             │
│  │  = Drug + Events     │     │  = Drug + Events     │             │
│  └──────────────────────┘     └──────────────────────┘             │
│            │                            │                           │
│            └──────────────┬─────────────┘                           │
│                           ▼                                         │
│                ┌─────────────────────┐                              │
│                │  NET BUDGET IMPACT  │                              │
│                │  = With - Without   │                              │
│                └─────────────────────┘                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 2.2 Model Components

| Component | Implementation | Source File |
|-----------|----------------|-------------|
| Population cascade | Prevalence-based funnel | `inputs.py:PopulationInputs` |
| Market uptake | S-curve adoption | `inputs.py:MarketInputs` |
| Cost calculation | Per-patient annual costs | `inputs.py:CostInputs` |
| Event modeling | Rate × RRR | `calculator.py:_calculate_events` |
| Persistence | Weibull survival | `inputs.py:TreatmentPersistence` |
| Subgroups | Multiplicative modifiers | `inputs.py:SubgroupParameters` |
| Sensitivity | Monte Carlo PSA | `calculator.py:run_probabilistic_sensitivity` |

## 2.3 Key Assumptions

1. **Closed cohort**: No new diagnoses during analysis period
2. **Immediate switch**: Patients switch treatments instantly
3. **Proportional displacement**: IXA-001 displaces competitors proportionally
4. **Constant efficacy**: Treatment effects do not wane over time
5. **No dynamic pricing**: Drug prices remain stable over 5 years

---

# 3. Population & Epidemiology

*Full details: `docs/population_epidemiology_technical_report.md`*

## 3.1 Population Cascade

```
Total Population (US)         331,000,000
        │ × 78% adult
        ▼
Adult Population              258,180,000
        │ × 32% HTN prevalence
        ▼
Hypertensive Adults            82,617,600
        │ × 12% resistant
        ▼
Resistant Hypertension          9,914,112
        │ × 60% uncontrolled
        ▼
Uncontrolled Resistant          5,948,467
        │ × 80% eligible
        ▼
IXA-001 Eligible Population     4,758,774
```

## 3.2 Cascade Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Total US population | 331,000,000 | Census 2024 |
| Adult proportion (≥18) | 78% | Census 2024 |
| HTN prevalence | 32% | Whelton 2018 |
| Resistant HTN proportion | 12% | Carey 2018 |
| Uncontrolled proportion | 60% | Persell 2011 |
| Treatment eligible | 80% | Clinical criteria |

## 3.3 Multi-Country Support

| Country | Population | Eligible (Year 1) | Currency |
|---------|------------|-------------------|----------|
| US | 331M | 3,760,742 | USD |
| UK | 67M | 640,255 | GBP |
| DE | 83M | 890,422 | EUR |
| FR | 67M | 680,315 | EUR |
| IT | 60M | 715,890 | EUR |
| ES | 47M | 505,625 | EUR |

---

# 4. Market Dynamics

*Full details: `docs/market_dynamics_technical_report.md`*

## 4.1 Current Market Composition

| Treatment | Market Share | Annual Cost |
|-----------|-------------|-------------|
| Spironolactone | 45% | $180 |
| Eplerenone | 25% | $1,200 |
| Other MRAs | 20% | $600 |
| No MRA therapy | 10% | $0 |

## 4.2 Uptake Scenarios

| Scenario | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
|----------|--------|--------|--------|--------|--------|
| Conservative | 2% | 5% | 10% | 15% | 18% |
| **Moderate** | **5%** | **12%** | **20%** | **27%** | **32%** |
| Optimistic | 8% | 18% | 30% | 40% | 45% |

## 4.3 Treatment Displacement

IXA-001 displaces existing treatments proportionally:

```python
displacement_weights = {
    "spironolactone": 0.50,  # Primary competitor
    "eplerenone": 0.30,      # Premium segment
    "other_mra": 0.15,       # Mixed
    "unmet_need": 0.05       # New-to-therapy
}
```

## 4.4 Year 3 Market Share Example (Moderate Scenario)

| Treatment | Before IXA-001 | After IXA-001 | Change |
|-----------|----------------|---------------|--------|
| IXA-001 | 0% | 20% | +20% |
| Spironolactone | 45% | 35% | -10% |
| Eplerenone | 25% | 19% | -6% |
| Other MRAs | 20% | 17% | -3% |
| No MRA | 10% | 9% | -1% |

---

# 5. Cost Inputs

*Full details: `docs/cost_inputs_technical_report.md`*

## 5.1 Drug Acquisition Costs

| Drug | Monthly | Annual | Source |
|------|---------|--------|--------|
| IXA-001 | $500 | $6,000 | Manufacturer |
| Spironolactone | $15 | $180 | RedBook |
| Eplerenone | $100 | $1,200 | RedBook |
| Other MRAs | $50 | $600 | Weighted avg |

## 5.2 Clinical Event Costs

| Event | Acute | Year 1 F/U | Ongoing/Year | Total Year 1 |
|-------|-------|------------|--------------|--------------|
| MI | $25,000 | $8,500 | $4,200 | $33,500 |
| Stroke | $22,000 | $12,000 | $8,500 | $34,000 |
| HF Hosp | $18,000 | $5,200 | $5,200 | $23,200 |
| ESRD | $35,000 | - | $90,000 | $125,000 |
| AF | $8,500 | $4,200 | $3,800 | $12,700 |

## 5.3 Monitoring Costs

| Component | Frequency | Unit Cost | Annual Cost |
|-----------|-----------|-----------|-------------|
| Office visit | 4/year | $125 | $500 |
| Basic metabolic panel | 4/year | $35 | $140 |
| eGFR/Creatinine | 4/year | $25 | $100 |
| **Total routine** | - | - | **$1,100** |
| IXA-001 incremental | - | - | **+$405** |

## 5.4 Country-Specific Cost Multipliers

| Country | Drug | Events | Monitoring |
|---------|------|--------|------------|
| US | 1.00 | 1.00 | 1.00 |
| UK | 0.45 | 0.55 | 0.60 |
| DE | 0.65 | 0.70 | 0.75 |
| FR | 0.55 | 0.65 | 0.70 |
| IT | 0.50 | 0.60 | 0.65 |
| ES | 0.45 | 0.55 | 0.60 |

---

# 6. Clinical Events

*Full details: `docs/clinical_events_technical_report.md`*

## 6.1 Baseline Annual Event Rates

| Event | Rate | Source |
|-------|------|--------|
| Myocardial Infarction | 1.5% | PATHWAY-2 |
| Stroke (all) | 1.0% | SPRINT |
| Heart Failure Hospitalization | 1.8% | TOPCAT |
| ESRD | 0.5% | USRDS |
| Atrial Fibrillation | 2.5% | SPRINT-MIND |

## 6.2 Treatment Effects (Relative Risk Reduction)

| Event | IXA-001 | Spironolactone | Eplerenone |
|-------|---------|----------------|------------|
| MI | 30% | 10% | 12% |
| Stroke | 40% | 15% | 18% |
| HF Hosp | 50% | 20% | 25% |
| ESRD | 55% | 15% | 18% |
| AF | 60% | 20% | 22% |
| CV Death | 25% | 8% | 10% |

## 6.3 Events Prevented (5-Year, Moderate Scenario)

| Event | Without IXA-001 | With IXA-001 | Prevented | Cost Offset |
|-------|-----------------|--------------|-----------|-------------|
| MI | 287,450 | 277,600 | 9,850 | $330M |
| Stroke | 167,320 | 162,090 | 5,230 | $178M |
| HF | 324,180 | 305,460 | 18,720 | $434M |
| ESRD | 28,450 | 26,600 | 1,850 | $231M |
| AF | 445,620 | 420,220 | 25,400 | $323M |
| **Total** | - | - | **61,050** | **$1,496M** |

---

# 7. Treatment Persistence

*Full details: `docs/treatment_persistence_technical_report.md`*

## 7.1 Persistence Curves

| Timepoint | IXA-001 | Spironolactone | Eplerenone |
|-----------|---------|----------------|------------|
| Month 6 | 87% | 65% | 72% |
| Month 12 | 82% | 52% | 60% |
| Month 24 | 74% | 38% | 48% |
| Month 36 | 68% | 30% | 40% |
| Month 48 | 63% | 24% | 34% |
| Month 60 | 58% | 20% | 29% |

## 7.2 Weibull Parameters

| Treatment | Scale (λ) | Shape (γ) |
|-----------|-----------|-----------|
| IXA-001 | 0.0035 | 0.65 |
| Spironolactone | 0.018 | 0.55 |
| Eplerenone | 0.012 | 0.60 |

## 7.3 Discontinuation Reasons

| Reason | IXA-001 | Spironolactone | Eplerenone |
|--------|---------|----------------|------------|
| Adverse events | 25% | 45% | 35% |
| Lack of efficacy | 15% | 20% | 20% |
| Cost/access | 30% | 15% | 25% |
| Patient preference | 20% | 15% | 15% |
| Physician decision | 10% | 5% | 5% |

## 7.4 Persistence-Adjusted Impact

| Metric | Perfect Adherence | With Persistence | Difference |
|--------|-------------------|------------------|------------|
| 5-Year Drug Cost | $22.4B | $15.1B | -33% |
| Events Prevented | 61,050 | 43,935 | -28% |
| Net Budget Impact | $20.9B | $13.6B | -35% |

---

# 8. Subgroup Analysis

*Full details: `docs/subgroup_analysis_technical_report.md`*

## 8.1 Subgroup Definitions

| Dimension | Categories | Prevalence |
|-----------|------------|------------|
| **Etiology** | PA, RAS, Pheo, OSA, Essential | 15%, 8%, 2%, 25%, 50% |
| **Age** | <65, ≥65 years | 55%, 45% |
| **CKD** | Stage 3-4, Non-CKD | 25%, 75% |
| **Diabetes** | Diabetic, Non-diabetic | 35%, 65% |

## 8.2 Event Rate Multipliers

| Subgroup | MI | Stroke | HF | ESRD | AF |
|----------|-----|--------|-----|------|-----|
| PA | 1.40× | 1.50× | 2.05× | 1.80× | 3.00× |
| CKD 3-4 | 1.50× | 1.30× | 1.80× | 3.50× | 1.20× |
| Age ≥65 | 1.50× | 1.70× | 2.00× | 1.20× | 2.20× |
| Diabetic | 1.40× | 1.35× | 1.60× | 1.80× | 1.30× |

## 8.3 Subgroup-Specific Budget Impact (5-Year)

| Subgroup | Population | Drug BI | Event Offset | Net BI | BI/Patient |
|----------|------------|---------|--------------|--------|------------|
| **All Patients** | 3.66M | $19.8B | -$1.5B | $18.3B | $5,010 |
| **PA** | 549K | $3.0B | -$0.6B | $2.4B | **$4,414** |
| **CKD 3-4** | 915K | $5.0B | -$0.5B | $4.4B | **$4,845** |
| **Age ≥65** | 1.65M | $8.9B | -$0.8B | $8.1B | $4,927 |
| **Diabetic** | 1.28M | $6.9B | -$0.6B | $6.3B | $4,956 |

## 8.4 Value Ranking by Subgroup

```
Budget Impact per Patient (5-Year, Lower = Better Value)

PA               ████████████████████ $4,414 ← Best value
CKD 3-4          ████████████████████████ $4,845
Age ≥65          ████████████████████████ $4,927
Diabetic         ████████████████████████ $4,956
All Patients     █████████████████████████ $5,010
Non-PA           █████████████████████████ $5,115 ← Lowest value

                 $4,000    $4,500    $5,000    $5,500
```

---

# 9. Sensitivity Analysis

*Full details: `docs/sensitivity_analysis_technical_report.md`*

## 9.1 Deterministic Sensitivity Analysis

### Key Parameter Ranges

| Parameter | Base | Low | High | BI Swing |
|-----------|------|-----|------|----------|
| IXA-001 cost | $6,000 | $4,800 | $7,200 | $7.3B |
| Uptake (Year 5) | 32% | 18% | 45% | $16.7B |
| HTN prevalence | 32% | 26% | 38% | $7.3B |
| HF RRR | 50% | 38% | 60% | $1.7B |
| ESRD RRR | 55% | 40% | 67% | $1.1B |

### Tornado Diagram

```
                           Low ◄────────────────► High

Uptake Rate      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $10.3B - $27.0B
IXA-001 Cost     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $14.7B - $22.0B
HTN Prevalence   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $14.7B - $22.0B
HF RRR           ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $17.5B - $19.2B
ESRD RRR         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $17.8B - $18.9B

             $10B      $15B      $20B      $25B      $30B
```

## 9.2 Probabilistic Sensitivity Analysis

### PSA Results (1,000 iterations)

| Statistic | 5-Year Net BI |
|-----------|---------------|
| Mean | $18.42B |
| Median | $18.15B |
| Std. Dev. | $4.23B |
| 5th percentile | $11.68B |
| 95th percentile | $26.35B |

### Budget Impact Distribution

```
         5th           Mean           95th
          │              │              │
          ▼              ▼              ▼
    ──────┬──────────────┬──────────────┬──────
          │              │              │
    $11.7B        $18.4B         $26.4B
```

## 9.3 Scenario Analysis

| Scenario | 5-Year Net BI | vs. Base |
|----------|---------------|----------|
| Conservative uptake | $10.31B | -44% |
| **Moderate (Base)** | **$18.33B** | **Reference** |
| Optimistic uptake | $27.02B | +47% |
| High price ($7,500) | $23.08B | +26% |
| Low price ($4,500) | $13.58B | -26% |
| PA subgroup only | $2.42B | -87% |
| Generic entry Year 3 | $16.89B | -8% |

## 9.4 Threshold Analysis

| Target Budget Impact | Required IXA-001 Price | Price Change |
|---------------------|------------------------|--------------|
| Current ($18.33B) | $6,000/year | Reference |
| $10B | $4,100/year | -32% |
| $5B | $2,750/year | -54% |
| Budget neutral | $890/year | -85% |

---

# 10. Results Summary

## 10.1 Base Case Results (US, Moderate Scenario)

| Metric | Year 1 | Year 3 | Year 5 | 5-Year Total |
|--------|--------|--------|--------|--------------|
| Patients on IXA-001 | 188,037 | 759,689 | 1,227,687 | - |
| IXA-001 Market Share | 5% | 20% | 32% | - |
| Drug Cost | $1.09B | $3.54B | $6.08B | $19.83B |
| Event Cost Offset | -$145M | -$581M | -$932M | -$1.50B |
| Net Budget Impact | $946M | $2.96B | $5.15B | $18.33B |

## 10.2 Multi-Scenario Summary

| Scenario | Year 5 Patients | 5-Year Net BI | BI per Patient |
|----------|-----------------|---------------|----------------|
| Conservative | 690,574 | $10.31B | $5,408 |
| **Moderate** | **1,227,687** | **$18.33B** | **$5,010** |
| Optimistic | 1,726,435 | $27.02B | $5,029 |

## 10.3 Value Proposition

| Factor | Finding |
|--------|---------|
| **Primary driver** | Drug cost premium (33× spironolactone) |
| **Key offset** | HF hospitalization prevention ($434M over 5 years) |
| **Highest value subgroup** | Primary Aldosteronism ($4,414/patient vs. $5,010 overall) |
| **Uncertainty range** | 95% CI: $11.7B - $26.4B |

---

# 11. Validation & Quality Assurance

## 11.1 Model Validation

| Validation Type | Method | Status |
|-----------------|--------|--------|
| Face validity | Expert review | ✓ Complete |
| Internal validity | Unit testing | ✓ 68 tests passed |
| External validity | Published trial comparison | ✓ Within ranges |
| Cross-validation | Alternative BIA model | ✓ Consistent |

## 11.2 Parameter Validation

| Parameter | Model Value | External Source | Deviation |
|-----------|-------------|-----------------|-----------|
| US Resistant HTN | 3.76M | 3.8M (Carey 2018) | -1.1% |
| PA prevalence | 15% | 11-21% (Douma 2008) | Within range |
| Spiro persistence (1yr) | 52% | 48-55% (MarketScan) | Within range |

## 11.3 ISPOR BIA Checklist Compliance

| Item | Status |
|------|--------|
| Population and disease characteristics | ✓ |
| Current treatment mix | ✓ |
| New intervention characteristics | ✓ |
| Time horizon (3-5 years) | ✓ |
| Costs from payer perspective | ✓ |
| Event cost offsets | ✓ |
| Sensitivity analyses | ✓ |
| Scenario analyses | ✓ |

---

# 12. References

## Primary Sources

1. **Whelton PK et al.** 2017 ACC/AHA Guideline for High Blood Pressure in Adults. *Hypertension*. 2018;71(6):e13-e115.

2. **Carey RM et al.** Resistant Hypertension: Detection, Evaluation, and Management. *Hypertension*. 2018;72(5):e53-e90.

3. **Williams B et al.** Spironolactone versus placebo, bisoprolol, and doxazosin for drug-resistant hypertension (PATHWAY-2). *Lancet*. 2015;386(10008):2059-2068.

4. **SPRINT Research Group.** Intensive vs Standard Blood-Pressure Control. *N Engl J Med*. 2015;373(22):2103-2116.

5. **Monticone S et al.** Cardiovascular events in primary aldosteronism. *Eur Heart J*. 2018;39(30):2727-2737.

## Methodological Guidance

6. **Sullivan SD et al.** Budget impact analysis principles of good practice: ISPOR 2012 Task Force. *Value Health*. 2014;17(1):5-14.

7. **Mauskopf JA et al.** Principles of good practice for budget impact analysis. *Value Health*. 2007;10(5):336-347.

8. **Husereau D et al.** CHEERS 2022 Reporting Standards. *Value Health*. 2022;25(1):3-9.

## Data Sources

9. **United States Renal Data System.** 2023 Annual Data Report. NIDDK.

10. **HCUP National Inpatient Sample.** Agency for Healthcare Research and Quality. 2022.

11. **Medi-Span RedBook.** Drug Pricing Reference. 2024.

12. **Truven Health Analytics.** MarketScan Research Databases. 2023.

---

# Appendices

## Appendix A: Technical Report Cross-Reference

| Topic | Standalone Report | Section |
|-------|-------------------|---------|
| Population & Epidemiology | `population_epidemiology_technical_report.md` | Section 3 |
| Market Dynamics | `market_dynamics_technical_report.md` | Section 4 |
| Cost Inputs | `cost_inputs_technical_report.md` | Section 5 |
| Clinical Events | `clinical_events_technical_report.md` | Section 6 |
| Treatment Persistence | `treatment_persistence_technical_report.md` | Section 7 |
| Subgroup Analysis | `subgroup_analysis_technical_report.md` | Section 8 |
| Sensitivity Analysis | `sensitivity_analysis_technical_report.md` | Section 9 |

## Appendix B: Code Module Reference

| Module | File | Key Classes |
|--------|------|-------------|
| Inputs | `src/bim/inputs.py` | `BIMInputs`, `PopulationInputs`, `MarketInputs`, `CostInputs` |
| Calculator | `src/bim/calculator.py` | `BIMCalculator`, `BIMResults`, `PSAResults` |

## Appendix C: Model Parameters Summary

| Category | Parameters | PSA Distribution |
|----------|------------|------------------|
| Population | 6 | Beta |
| Market | 12 | Triangular |
| Costs | 18 | Gamma |
| Events | 10 | Beta |
| Efficacy | 12 | Lognormal |
| Persistence | 6 | Fixed |
| **Total** | **64** | - |

---

**Document Control:**
- Version 1.0 - Initial release (February 2026)
- Reviewed by: HEOR Technical Lead
- Approved for HTA submission

**End of Document**
