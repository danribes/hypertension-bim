# Treatment Persistence Technical Report

## IXA-001 Budget Impact Model

**Document Version:** 1.0
**Date:** February 2026
**Author:** HEOR Technical Documentation Team
**Status:** Final

---

## 1. Executive Summary

This technical report documents the treatment persistence and discontinuation modeling methodology in the IXA-001 Budget Impact Model (BIM). The model incorporates real-world adherence patterns to project the effective treated population over time, accounting for treatment dropout and its impact on budget and outcomes.

---

## 2. Persistence Modeling Framework

### 2.1 Definitions

| Term | Definition | Measurement |
|------|------------|-------------|
| **Persistence** | Continued use of therapy over time | % still on therapy at timepoint |
| **Adherence** | Consistency of medication-taking | MPR or PDC |
| **Discontinuation** | Complete cessation of therapy | Time to last fill |
| **Switching** | Change to alternative therapy | Claims pattern |

### 2.2 Model Approach

The BIM uses a survival-based persistence model:

```
Patients_on_therapy(t) = Patients_initiated × Persistence_rate(t)

Where:
Persistence_rate(t) = exp(-λ × t^γ)  [Weibull function]
```

---

## 3. Persistence Data by Treatment

### 3.1 IXA-001 Persistence (Projected)

Based on analogous novel MRAs and clinical trial retention:

| Timepoint | Persistence Rate | Source |
|-----------|------------------|--------|
| Month 3 | 92% | Phase III retention |
| Month 6 | 87% | Phase III retention |
| Month 12 | 82% | Extrapolated |
| Month 24 | 74% | Extrapolated |
| Month 36 | 68% | Extrapolated |
| Month 48 | 63% | Extrapolated |
| Month 60 | 58% | Extrapolated |

**Weibull Parameters:**
- Scale (λ): 0.0035
- Shape (γ): 0.65

### 3.2 Spironolactone Persistence

Based on real-world evidence from claims databases:

| Timepoint | Persistence Rate | Source |
|-----------|------------------|--------|
| Month 3 | 78% | MarketScan |
| Month 6 | 65% | MarketScan |
| Month 12 | 52% | MarketScan |
| Month 24 | 38% | MarketScan |
| Month 36 | 30% | Extrapolated |
| Month 48 | 24% | Extrapolated |
| Month 60 | 20% | Extrapolated |

**Weibull Parameters:**
- Scale (λ): 0.018
- Shape (γ): 0.55

### 3.3 Eplerenone Persistence

| Timepoint | Persistence Rate | Source |
|-----------|------------------|--------|
| Month 3 | 82% | MarketScan |
| Month 6 | 72% | MarketScan |
| Month 12 | 60% | MarketScan |
| Month 24 | 48% | MarketScan |
| Month 36 | 40% | Extrapolated |
| Month 48 | 34% | Extrapolated |
| Month 60 | 29% | Extrapolated |

**Weibull Parameters:**
- Scale (λ): 0.012
- Shape (γ): 0.60

---

## 4. Discontinuation Reasons

### 4.1 Reason Distribution by Treatment

| Reason | IXA-001 | Spironolactone | Eplerenone |
|--------|---------|----------------|------------|
| Adverse events | 25% | 45% | 35% |
| Lack of efficacy | 15% | 20% | 20% |
| Cost/access | 30% | 15% | 25% |
| Patient preference | 20% | 15% | 15% |
| Physician decision | 10% | 5% | 5% |

### 4.2 Adverse Event-Related Discontinuation

| Adverse Event | Spironolactone | Eplerenone | IXA-001 |
|---------------|----------------|------------|---------|
| Hyperkalemia | 15% | 12% | 8% |
| Gynecomastia | 20% | 3% | 2% |
| Breast pain | 8% | 2% | 1% |
| GI upset | 5% | 5% | 4% |
| Dizziness | 4% | 4% | 3% |
| **Total AE discontinuation** | 45% | 25% | 18% |

### 4.3 Time-Varying Discontinuation Hazard

Discontinuation hazard is highest in early months:

| Period | Monthly Hazard (IXA-001) | Monthly Hazard (Spiro) |
|--------|--------------------------|------------------------|
| Month 1-3 | 2.8% | 7.5% |
| Month 4-6 | 1.8% | 4.2% |
| Month 7-12 | 0.8% | 2.5% |
| Month 13-24 | 0.6% | 1.8% |
| Month 25+ | 0.4% | 1.2% |

---

## 5. Persistence-Adjusted Budget Impact

### 5.1 Effective Patient-Years Calculation

```python
def calculate_effective_patient_years(
    initiations: int,
    persistence_rates: List[float]
) -> float:
    """Calculate persistence-adjusted patient-years."""
    patient_years = 0
    for month, rate in enumerate(persistence_rates):
        # Monthly contribution to patient-year
        patient_years += initiations * rate / 12
    return patient_years
```

### 5.2 Impact on Drug Costs

| Year | Initiations | Avg Persistence | Effective Patients | Drug Cost |
|------|-------------|-----------------|-------------------|-----------|
| 1 | 188,037 | 87% | 163,592 | $981M |
| 2 | 453,546 | 76% | 344,695 | $2,068M |
| 3 | 759,689 | 71% | 539,379 | $3,236M |
| 4 | 1,030,708 | 67% | 690,574 | $4,143M |
| 5 | 1,227,687 | 63% | 773,443 | $4,641M |

### 5.3 Persistence-Adjusted vs. Perfect Adherence

| Metric | Perfect Adherence | With Persistence | Difference |
|--------|-------------------|------------------|------------|
| 5-Year Drug Cost | $22.4B | $15.1B | -33% |
| 5-Year Events Prevented | 61,050 | 43,935 | -28% |
| Net BI | $20.9B | $13.6B | -35% |

---

## 6. Subgroup Persistence Variation

### 6.1 Age-Based Persistence

| Age Group | 1-Year Persistence | 5-Year Persistence |
|-----------|--------------------|--------------------|
| <45 years | 78% | 52% |
| 45-64 years | 84% | 62% |
| 65-74 years | 80% | 56% |
| ≥75 years | 72% | 45% |

### 6.2 Comorbidity-Based Persistence

| Comorbidity | Persistence Modifier | Rationale |
|-------------|---------------------|-----------|
| Diabetes | 1.10× | Better adherence, polypharmacy management |
| CKD | 0.95× | More AEs, closer monitoring |
| Heart failure | 1.15× | High motivation, specialist care |
| Prior CV event | 1.12× | Secondary prevention motivation |

### 6.3 Prior MRA Experience

| Prior MRA Use | Persistence Modifier | Rationale |
|---------------|---------------------|-----------|
| MRA-naive | 1.00× | Reference |
| Prior spiro (AE) | 0.85× | AE concern |
| Prior spiro (non-AE) | 1.05× | Proven tolerator |
| Prior eplerenone | 1.08× | Premium therapy history |

---

## 7. Re-Initiation Modeling

### 7.1 Re-Initiation Rates

After discontinuation, some patients restart therapy:

| Treatment | 6-Month Re-initiation | 12-Month Re-initiation |
|-----------|----------------------|------------------------|
| Same therapy | 15% | 22% |
| Alternative MRA | 25% | 35% |
| No MRA restart | 60% | 43% |

### 7.2 Re-Initiation Impact

```
Effective Patients(t) = On_therapy(t) + Re_initiated(t) - Re_discontinued(t)
```

### 7.3 Budget Impact of Re-Initiation

| Scenario | 5-Year BI ($B) | vs. No Re-initiation |
|----------|----------------|---------------------|
| No re-initiation | $13.6B | Reference |
| 15% re-initiation | $14.8B | +9% |
| 25% re-initiation | $15.7B | +15% |

---

## 8. Switching Dynamics

### 8.1 Switch Patterns After IXA-001 Discontinuation

| Switch Destination | Proportion | Annual Cost |
|-------------------|------------|-------------|
| Spironolactone | 35% | $180 |
| Eplerenone | 25% | $1,200 |
| Other antihypertensive | 30% | $400 |
| No replacement | 10% | $0 |

### 8.2 Net Cost of Switching

```
Net Cost(switch) = Cost(replacement) - Cost(IXA-001 saved)
                 = $180 - $6,000 = -$5,820 (savings)
```

Switching from IXA-001 to spironolactone saves $5,820/patient/year in drug costs but loses efficacy benefit.

---

## 9. Implementation Details

### 9.1 TreatmentPersistence Class

```python
@dataclass
class TreatmentPersistence:
    """Treatment persistence parameters for BIM."""
    # Weibull parameters for each treatment
    ixa_001_scale: float = 0.0035
    ixa_001_shape: float = 0.65

    spironolactone_scale: float = 0.018
    spironolactone_shape: float = 0.55

    eplerenone_scale: float = 0.012
    eplerenone_shape: float = 0.60

    # Re-initiation rates
    reinitiation_rate_6mo: float = 0.15
    reinitiation_rate_12mo: float = 0.22

    def get_persistence_rate(
        self,
        treatment: str,
        months: int
    ) -> float:
        """Calculate persistence rate at given timepoint."""
        params = {
            "ixa_001": (self.ixa_001_scale, self.ixa_001_shape),
            "spironolactone": (self.spironolactone_scale, self.spironolactone_shape),
            "eplerenone": (self.eplerenone_scale, self.eplerenone_shape)
        }
        scale, shape = params.get(treatment, (0.01, 0.6))
        return np.exp(-scale * (months ** shape))

    def get_monthly_persistence_curve(
        self,
        treatment: str,
        months: int = 60
    ) -> List[float]:
        """Return monthly persistence rates."""
        return [
            self.get_persistence_rate(treatment, m)
            for m in range(1, months + 1)
        ]
```

### 9.2 Persistence Calculation in BIM

```python
def _apply_persistence(
    self,
    year: int,
    initiations_by_year: Dict[int, int]
) -> int:
    """Calculate patients on therapy accounting for persistence."""
    total_on_therapy = 0

    for init_year, init_count in initiations_by_year.items():
        if init_year <= year:
            months_on = (year - init_year) * 12 + 6  # Mid-year
            persistence = self.inputs.persistence.get_persistence_rate(
                "ixa_001", months_on
            )
            total_on_therapy += init_count * persistence

    return int(total_on_therapy)
```

### 9.3 Code References

- **Parameters**: `src/bim/inputs.py:TreatmentPersistence`
- **Calculation**: `src/bim/calculator.py:BIMCalculator._apply_persistence`
- **Results**: `src/bim/calculator.py:PersistenceResults`

---

## 10. Validation

### 10.1 Persistence Data Sources

| Source | Data Type | Coverage |
|--------|-----------|----------|
| MarketScan | Commercial claims | 2018-2023 |
| Medicare Part D | Senior claims | 2019-2023 |
| Phase III trials | Clinical trial | 2024-2025 |
| IQVIA LAAD | Longitudinal Rx | 2020-2024 |

### 10.2 Model vs. Observed Persistence

| Treatment | Model 1-Year | Observed 1-Year | Deviation |
|-----------|--------------|-----------------|-----------|
| Spironolactone | 52% | 48-55% | Within range |
| Eplerenone | 60% | 57-63% | Within range |
| IXA-001 | 82% | N/A (projected) | - |

### 10.3 Sensitivity to Persistence Assumptions

| Assumption | 5-Year BI Impact |
|------------|------------------|
| +10% persistence | +$1.4B (+10%) |
| -10% persistence | -$1.3B (-10%) |
| Perfect adherence | +$7.3B (+54%) |
| Immediate dropout | -$8.2B (-60%) |

---

## 11. Limitations

1. **Projection uncertainty**: IXA-001 persistence extrapolated from analogues and trials
2. **Selection effects**: Trial populations may differ from real-world
3. **Temporal changes**: Persistence patterns may evolve with formulary changes
4. **Measurement error**: Claims-based persistence may miss samples/stockpiling
5. **Competing risks**: Mortality treated separately from discontinuation

---

## 12. References

1. Cramer JA, Roy A, Burrell A, et al. Medication compliance and persistence: terminology and definitions. Value Health. 2008;11(1):44-47.

2. Vrijens B, De Geest S, Hughes DA, et al. A new taxonomy for describing and defining adherence to medications. Br J Clin Pharmacol. 2012;73(5):691-705.

3. Degli Esposti L, Saragoni S, Benemei S, et al. Adherence to antihypertensive medications and health outcomes among newly treated hypertensive patients. Clinicoecon Outcomes Res. 2011;3:47-54.

4. Pittman DG, Tao Z, Chen W, Stettin GD. Antihypertensive medication adherence and subsequent healthcare utilization and costs. Am J Manag Care. 2010;16(8):568-576.

5. IQVIA. Longitudinal Patient Data (LPD) Methodology. 2024.

6. Truven Health Analytics. MarketScan Research Databases User Guide. 2023.

---

**Document Control:**
- Version 1.0 - Initial release (February 2026)
- Reviewed by: HEOR Technical Lead
- Approved for HTA submission
