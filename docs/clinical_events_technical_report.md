# Clinical Events Technical Report

## IXA-001 Budget Impact Model

**Document Version:** 1.0
**Date:** February 2026
**Author:** HEOR Technical Documentation Team
**Status:** Final

---

## 1. Executive Summary

This technical report documents the clinical event modeling methodology in the IXA-001 Budget Impact Model (BIM). The model estimates event rates for cardiovascular outcomes (MI, stroke, HF, AF), renal outcomes (CKD progression, ESRD), and adverse events (hyperkalemia) to project event-related cost offsets from IXA-001 treatment.

---

## 2. Event Modeling Framework

### 2.1 Events Modeled

| Category | Events | Impact on BI |
|----------|--------|--------------|
| Cardiovascular | MI, Stroke, HF, AF | Cost offset (reduction) |
| Renal | CKD progression, ESRD | Cost offset (reduction) |
| Adverse | Hyperkalemia, Gynecomastia | Cost increase |
| Mortality | CV death, All-cause death | Cost offset |

### 2.2 Event Rate Approach

The BIM uses annual incidence rates applied to the treated population:

```
Events(year) = Population × Treatment_Share × Event_Rate × (1 - RRR)

Where:
- Population = Eligible patients in year
- Treatment_Share = Market share of treatment
- Event_Rate = Baseline annual incidence
- RRR = Relative risk reduction (0 for comparators)
```

---

## 3. Baseline Event Rates

### 3.1 Cardiovascular Events

| Event | Annual Rate | Source | Population |
|-------|-------------|--------|------------|
| Myocardial Infarction | 1.5% | PATHWAY-2, SPRINT | Resistant HTN |
| Ischemic Stroke | 0.8% | SPRINT | Resistant HTN |
| Hemorrhagic Stroke | 0.2% | Meta-analysis | Resistant HTN |
| Heart Failure (hospitalization) | 1.8% | TOPCAT | Resistant HTN |
| Atrial Fibrillation (new onset) | 2.5% | SPRINT-MIND | Resistant HTN |

### 3.2 Renal Events

| Event | Annual Rate | Source | Population |
|-------|-------------|--------|------------|
| CKD Stage 3 progression | 3.5% | CKD-PC | HTN + CKD |
| CKD Stage 4 progression | 2.0% | KFRE validation | HTN + CKD Stage 3 |
| ESRD (dialysis initiation) | 0.5% | USRDS | HTN + CKD Stage 4 |

### 3.3 Adverse Events

| Event | IXA-001 Rate | Spiro Rate | Eplerenone Rate |
|-------|--------------|------------|-----------------|
| Hyperkalemia (any) | 8.0% | 12.0% | 10.0% |
| Hyperkalemia (severe) | 1.5% | 3.5% | 2.5% |
| Gynecomastia | 0.5% | 8.0% | 0.5% |
| AKI | 1.0% | 1.5% | 1.2% |

---

## 4. Treatment Effects

### 4.1 IXA-001 Relative Risk Reductions

| Event | RRR | 95% CI | Source |
|-------|-----|--------|--------|
| MI | 30% | 18-40% | Phase III pooled |
| Stroke | 40% | 25-52% | Phase III pooled |
| HF Hospitalization | 50% | 38-60% | Phase III pooled |
| ESRD | 55% | 40-67% | Phase III + extrapolation |
| AF (new onset) | 60% | 45-72% | Phase III PA subgroup |
| CV Death | 25% | 12-36% | Phase III pooled |

### 4.2 Comparator Treatment Effects

| Event | Spironolactone RRR | Eplerenone RRR | Source |
|-------|-------------------|----------------|--------|
| MI | 10% | 12% | Meta-analysis |
| Stroke | 15% | 18% | Meta-analysis |
| HF Hospitalization | 20% | 25% | EMPHASIS-HF |
| ESRD | 15% | 18% | FIDELITY |
| AF | 20% | 22% | Observational |
| CV Death | 8% | 10% | Meta-analysis |

### 4.3 Incremental Benefit (IXA-001 vs. Comparators)

| Event | vs. Spironolactone | vs. Eplerenone | vs. No MRA |
|-------|-------------------|----------------|------------|
| MI | +20% RRR | +18% RRR | +30% RRR |
| Stroke | +25% RRR | +22% RRR | +40% RRR |
| HF | +30% RRR | +25% RRR | +50% RRR |
| ESRD | +40% RRR | +37% RRR | +55% RRR |
| AF | +40% RRR | +38% RRR | +60% RRR |

---

## 5. Subgroup-Specific Event Rates

### 5.1 Primary Aldosteronism (PA)

PA patients have elevated baseline event rates:

| Event | General Population | PA Multiplier | PA Rate |
|-------|-------------------|---------------|---------|
| MI | 1.5% | 1.40× | 2.1% |
| Stroke | 1.0% | 1.50× | 1.5% |
| HF | 1.8% | 2.05× | 3.7% |
| ESRD | 0.5% | 1.80× | 0.9% |
| AF | 2.5% | 3.00× | 7.5% |

### 5.2 CKD Stage 3-4

| Event | General | CKD Multiplier | CKD Rate |
|-------|---------|----------------|----------|
| MI | 1.5% | 1.50× | 2.25% |
| Stroke | 1.0% | 1.30× | 1.30% |
| HF | 1.8% | 1.80× | 3.24% |
| ESRD | 0.5% | 3.50× | 1.75% |

### 5.3 Elderly (≥65 years)

| Event | <65 years | ≥65 Multiplier | ≥65 Rate |
|-------|-----------|----------------|----------|
| MI | 1.2% | 1.50× | 1.8% |
| Stroke | 0.7% | 1.70× | 1.2% |
| HF | 1.2% | 2.00× | 2.4% |
| AF | 1.8% | 2.20× | 4.0% |

---

## 6. Event Calculation Methodology

### 6.1 Annual Event Estimation

```python
def calculate_events(
    population: int,
    treatment_shares: Dict[str, float],
    event_rate: float,
    treatment_rrrs: Dict[str, float]
) -> EventResults:
    """Calculate annual events by treatment group."""
    events = {}
    for treatment, share in treatment_shares.items():
        n_treated = population * share
        rrr = treatment_rrrs.get(treatment, 0.0)
        events[treatment] = n_treated * event_rate * (1 - rrr)
    return EventResults(
        total=sum(events.values()),
        by_treatment=events
    )
```

### 6.2 Events Prevented Calculation

```python
def calculate_events_prevented(
    events_with: EventResults,
    events_without: EventResults
) -> int:
    """Calculate events prevented by IXA-001 introduction."""
    return events_without.total - events_with.total
```

### 6.3 Example Calculation

**Year 3, MI Events (Moderate Scenario):**

```
World Without IXA-001:
- Spiro (45%): 3,798,444 × 0.45 × 0.015 × (1-0.10) = 23,037
- Eplerenone (25%): 3,798,444 × 0.25 × 0.015 × (1-0.12) = 12,527
- Other (20%): 3,798,444 × 0.20 × 0.015 × (1-0.05) = 10,828
- No MRA (10%): 3,798,444 × 0.10 × 0.015 × (1-0.00) = 5,698
Total: 52,090 MIs

World With IXA-001 (20% share):
- IXA-001 (20%): 3,798,444 × 0.20 × 0.015 × (1-0.30) = 7,976
- Spiro (35%): 3,798,444 × 0.35 × 0.015 × (1-0.10) = 17,918
- Eplerenone (19%): 3,798,444 × 0.19 × 0.015 × (1-0.12) = 9,521
- Other (17%): 3,798,444 × 0.17 × 0.015 × (1-0.05) = 9,204
- No MRA (9%): 3,798,444 × 0.09 × 0.015 × (1-0.00) = 5,128
Total: 49,747 MIs

MIs Prevented: 52,090 - 49,747 = 2,343 events
Cost Offset: 2,343 × $33,500 = $78.5M
```

---

## 7. Cumulative Event Impact

### 7.1 5-Year Events Prevented (US, Moderate Scenario)

| Event | Events Prevented | Unit Cost | Cost Offset |
|-------|------------------|-----------|-------------|
| MI | 9,850 | $33,500 | $330M |
| Stroke | 5,230 | $34,000 | $178M |
| HF Hospitalization | 18,720 | $23,200 | $434M |
| ESRD | 1,850 | $125,000 | $231M |
| AF | 25,400 | $12,700 | $323M |
| **Total** | **61,050** | - | **$1,496M** |

### 7.2 Events Prevented by Scenario

| Event | Conservative | Moderate | Optimistic |
|-------|--------------|----------|------------|
| MI | 5,420 | 9,850 | 14,480 |
| Stroke | 2,880 | 5,230 | 7,690 |
| HF | 10,310 | 18,720 | 27,530 |
| ESRD | 1,020 | 1,850 | 2,720 |
| AF | 13,990 | 25,400 | 37,350 |

---

## 8. Adverse Event Impact

### 8.1 Hyperkalemia Reduction

IXA-001 has lower hyperkalemia rates than spironolactone:

| Metric | Spironolactone | IXA-001 | Difference |
|--------|----------------|---------|------------|
| Any hyperkalemia | 12.0% | 8.0% | -4.0% |
| Severe (hospitalized) | 3.5% | 1.5% | -2.0% |
| Cost per severe event | $12,500 | $12,500 | - |

**Hyperkalemia Cost Savings (Year 3, IXA-001 patients):**
```
Severe events avoided = 759,689 × (0.035 - 0.015) = 15,194
Cost savings = 15,194 × $12,500 = $190M
```

### 8.2 Gynecomastia Reduction

| Metric | Spironolactone | IXA-001 | Difference |
|--------|----------------|---------|------------|
| Incidence | 8.0% | 0.5% | -7.5% |
| Treatment cost | $350 | $350 | - |
| Discontinuation rate | 15% | 2% | -13% |

---

## 9. Implementation Details

### 9.1 ClinicalEventRates Class

```python
@dataclass
class ClinicalEventRates:
    """Baseline annual event rates for resistant HTN population."""
    mi_rate: float = 0.015
    stroke_ischemic_rate: float = 0.008
    stroke_hemorrhagic_rate: float = 0.002
    hf_hospitalization_rate: float = 0.018
    af_new_onset_rate: float = 0.025

    ckd_progression_rate: float = 0.035
    esrd_rate: float = 0.005

    hyperkalemia_any_rate: float = 0.10
    hyperkalemia_severe_rate: float = 0.025
    gynecomastia_rate: float = 0.05

    def get_stroke_rate(self) -> float:
        """Return combined stroke rate."""
        return self.stroke_ischemic_rate + self.stroke_hemorrhagic_rate
```

### 9.2 Treatment Effect Parameters

```python
@dataclass
class TreatmentEffects:
    """Relative risk reductions by treatment."""
    # IXA-001 effects
    ixa_mi_rrr: float = 0.30
    ixa_stroke_rrr: float = 0.40
    ixa_hf_rrr: float = 0.50
    ixa_esrd_rrr: float = 0.55
    ixa_af_rrr: float = 0.60
    ixa_death_rrr: float = 0.25

    # Spironolactone effects
    spiro_mi_rrr: float = 0.10
    spiro_stroke_rrr: float = 0.15
    spiro_hf_rrr: float = 0.20
    spiro_esrd_rrr: float = 0.15
    spiro_af_rrr: float = 0.20
    spiro_death_rrr: float = 0.08
```

### 9.3 Code References

- **Event rates**: `src/bim/inputs.py:ClinicalEventRates`
- **Calculation**: `src/bim/calculator.py:BIMCalculator._calculate_events`
- **Subgroup modifiers**: `src/bim/inputs.py:SubgroupParameters`

---

## 10. Validation

### 10.1 Baseline Event Rate Validation

| Event | Model Rate | SPRINT Trial | PATHWAY-2 | Deviation |
|-------|------------|--------------|-----------|-----------|
| MI | 1.5% | 1.4% | 1.6% | Within range |
| Stroke | 1.0% | 0.9% | 1.1% | Within range |
| HF | 1.8% | 1.6% | 2.0% | Within range |

### 10.2 Treatment Effect Validation

| Event | IXA-001 RRR | Phase III Result | Published MRA Data |
|-------|-------------|------------------|-------------------|
| MI | 30% | 28% (95% CI: 18-40%) | Aligned |
| HF | 50% | 52% (95% CI: 38-60%) | Aligned |
| ESRD | 55% | Extrapolated | Consistent with BP effect |

---

## 11. Limitations

1. **Event independence**: Events modeled independently; competing risks not fully captured
2. **Constant rates**: Annual rates assumed constant; no age-dependent acceleration
3. **Treatment effects**: RRRs assumed constant over time (no waning)
4. **Recurrent events**: Only first events counted; recurrence not modeled
5. **Subgroup interactions**: Multiplicative subgroup effects may overestimate risk

---

## 12. References

1. Williams B, MacDonald TM, Morant S, et al. Spironolactone versus placebo, bisoprolol, and doxazosin to determine the optimal treatment for drug-resistant hypertension (PATHWAY-2). Lancet. 2015;386(10008):2059-2068.

2. SPRINT Research Group. A Randomized Trial of Intensive versus Standard Blood-Pressure Control. N Engl J Med. 2015;373(22):2103-2116.

3. Pitt B, Pfeffer MA, Assmann SF, et al. Spironolactone for heart failure with preserved ejection fraction. N Engl J Med. 2014;370(15):1383-1392.

4. Monticone S, D'Ascenzo F, Moretti C, et al. Cardiovascular events and target organ damage in primary aldosteronism compared with essential hypertension. Eur Heart J. 2018;39(30):2727-2737.

5. Bakris GL, Agarwal R, Anker SD, et al. Effect of Finerenone on Chronic Kidney Disease Outcomes in Type 2 Diabetes. N Engl J Med. 2020;383(23):2219-2229.

6. United States Renal Data System. 2023 Annual Data Report. National Institute of Diabetes and Digestive and Kidney Diseases.

---

**Document Control:**
- Version 1.0 - Initial release (February 2026)
- Reviewed by: HEOR Technical Lead
- Approved for HTA submission
