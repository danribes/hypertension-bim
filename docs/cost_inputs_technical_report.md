# Cost Inputs Technical Report

## IXA-001 Budget Impact Model

**Document Version:** 1.0
**Date:** February 2026
**Author:** HEOR Technical Documentation Team
**Status:** Final

---

## 1. Executive Summary

This technical report documents all cost inputs used in the IXA-001 Budget Impact Model (BIM). The model incorporates drug acquisition costs, clinical event costs, monitoring costs, and indirect costs to project the total budget impact of IXA-001 introduction over a 5-year time horizon.

---

## 2. Drug Acquisition Costs

### 2.1 IXA-001 Pricing

| Parameter | Value | Source |
|-----------|-------|--------|
| Monthly Cost (US) | $500 | Manufacturer pricing |
| Annual Cost (US) | $6,000 | Calculated |
| WAC vs. Net | 85% net-to-gross | Industry average |

### 2.2 Comparator Drug Costs

| Drug | Monthly Cost | Annual Cost | Source |
|------|--------------|-------------|--------|
| Spironolactone 25-50mg | $15 | $180 | RedBook AWP |
| Eplerenone 25-50mg | $100 | $1,200 | RedBook AWP |
| Other MRAs (average) | $50 | $600 | Weighted average |

### 2.3 Drug Cost Differentials

| Comparison | Monthly Δ | Annual Δ | Multiplier |
|------------|-----------|----------|------------|
| IXA-001 vs. Spironolactone | +$485 | +$5,820 | 33.3× |
| IXA-001 vs. Eplerenone | +$400 | +$4,800 | 5.0× |
| IXA-001 vs. Other MRAs | +$450 | +$5,400 | 10.0× |

---

## 3. Clinical Event Costs

### 3.1 Cardiovascular Event Costs

| Event | Acute Cost | Year 1 Follow-up | Ongoing Annual | Source |
|-------|------------|------------------|----------------|--------|
| Myocardial Infarction | $25,000 | $8,500 | $4,200 | HCUP, CMS |
| Stroke (Ischemic) | $22,000 | $12,000 | $8,500 | HCUP |
| Stroke (Hemorrhagic) | $35,000 | $18,000 | $12,000 | HCUP |
| Heart Failure Hospitalization | $18,000 | $6,500 | $5,200 | HCUP |
| Atrial Fibrillation (new onset) | $8,500 | $4,200 | $3,800 | CMS |

### 3.2 Renal Event Costs

| Event | Acute Cost | Ongoing Annual | Source |
|-------|------------|----------------|--------|
| CKD Stage 3 diagnosis | $2,500 | $3,500 | USRDS |
| CKD Stage 4 diagnosis | $4,500 | $8,500 | USRDS |
| ESRD (dialysis initiation) | $35,000 | $90,000 | USRDS 2023 |
| Kidney transplant | $150,000 | $25,000 | OPTN |

### 3.3 Adverse Event Costs

| Event | Per-Episode Cost | Source |
|-------|------------------|--------|
| Hyperkalemia (hospitalized) | $12,500 | HCUP |
| Hyperkalemia (outpatient) | $850 | Medicare claims |
| Gynecomastia (treatment) | $350 | CPT codes |
| AKI (acute kidney injury) | $18,000 | HCUP |

---

## 4. Monitoring and Management Costs

### 4.1 Routine Monitoring

| Service | Frequency | Unit Cost | Annual Cost |
|---------|-----------|-----------|-------------|
| Office visit (established) | 4/year | $125 | $500 |
| Basic metabolic panel | 4/year | $35 | $140 |
| Potassium level | 4/year | $15 | $60 |
| eGFR/Creatinine | 4/year | $25 | $100 |
| Blood pressure monitoring | 12/year | $25 | $300 |
| **Total Annual Monitoring** | - | - | **$1,100** |

### 4.2 IXA-001 Specific Monitoring

| Service | Frequency | Unit Cost | Annual Cost |
|---------|-----------|-----------|-------------|
| PAC/PRA ratio (initial) | 1× | $185 | $185 |
| Aldosterone level | 2/year | $95 | $190 |
| Additional potassium | 2/year | $15 | $30 |
| **IXA-001 Incremental** | - | - | **$405** |

### 4.3 Total Monitoring Costs by Treatment

| Treatment | Routine | Incremental | Total |
|-----------|---------|-------------|-------|
| Spironolactone | $1,100 | $0 | $1,100 |
| Eplerenone | $1,100 | $150 | $1,250 |
| IXA-001 | $1,100 | $405 | $1,505 |

---

## 5. Country-Specific Cost Adjustments

### 5.1 Cost Multipliers

| Country | Drug Cost Mult. | Event Cost Mult. | Monitoring Mult. |
|---------|-----------------|------------------|------------------|
| US | 1.00 | 1.00 | 1.00 |
| UK | 0.45 | 0.55 | 0.60 |
| DE | 0.65 | 0.70 | 0.75 |
| FR | 0.55 | 0.65 | 0.70 |
| IT | 0.50 | 0.60 | 0.65 |
| ES | 0.45 | 0.55 | 0.60 |

### 5.2 Currency Conversion

| Country | Currency | Exchange Rate (to USD) |
|---------|----------|------------------------|
| US | USD | 1.00 |
| UK | GBP | 1.25 |
| DE, FR, IT, ES | EUR | 1.08 |

### 5.3 Example: UK Cost Calculation

```
IXA-001 Annual (UK) = $6,000 × 0.45 / 1.25 = £2,160
MI Acute (UK) = $25,000 × 0.55 / 1.25 = £11,000
```

---

## 6. Cost Offsets from Event Prevention

### 6.1 Event Rate Reduction

| Event | IXA-001 RRR | Events Prevented (per 1000) | Cost Offset |
|-------|-------------|----------------------------|-------------|
| MI | 30% | 4.5 | $150,750 |
| Stroke | 40% | 3.2 | $91,200 |
| HF Hospitalization | 50% | 8.7 | $182,700 |
| ESRD | 55% | 1.2 | $150,000 |
| AF | 60% | 12.5 | $162,500 |

### 6.2 Net Cost Calculation

```
Net Cost = Drug Cost + Monitoring - Event Cost Offsets

Per Patient (Year 1):
IXA-001: $6,000 + $1,505 - $1,875 = $5,630
Spiro:   $180 + $1,100 - $0 = $1,280
Incremental: $4,350/patient
```

---

## 7. Indirect Costs (Societal Perspective)

### 7.1 Productivity Loss by Event

| Event | Work Days Lost | Wage/Day | Productivity Loss |
|-------|----------------|----------|-------------------|
| MI (acute) | 45 | $280 | $12,600 |
| MI (ongoing) | 10/year | $280 | $2,800/year |
| Stroke | 90 | $280 | $25,200 |
| HF Hospitalization | 21 | $280 | $5,880 |
| ESRD (dialysis) | 156/year | $280 | $43,680/year |

### 7.2 Caregiver Burden

| Event | Caregiver Hours/Week | Weeks | Hourly Rate | Total |
|-------|----------------------|-------|-------------|-------|
| Stroke (first year) | 25 | 52 | $15 | $19,500 |
| ESRD (ongoing) | 10 | 52 | $15 | $7,800/year |
| HF (ongoing) | 8 | 52 | $15 | $6,240/year |

### 7.3 Total Societal Cost per Event

| Event | Direct Medical | Indirect | Caregiver | Total Societal |
|-------|----------------|----------|-----------|----------------|
| MI | $33,500 | $15,400 | $0 | $48,900 |
| Stroke | $34,000 | $25,200 | $19,500 | $78,700 |
| HF | $23,200 | $5,880 | $6,240 | $35,320 |
| ESRD | $125,000 | $43,680 | $7,800 | $176,480 |

---

## 8. Budget Impact Calculation

### 8.1 Incremental Drug Cost

```
Incremental Drug Cost = Σ (N_patients × IXA_share × ΔCost_drug)

Year 1 (Moderate Scenario):
= 3,760,742 × 0.05 × ($6,000 - $180 × 0.50 - $1,200 × 0.30 - $600 × 0.15)
= 188,037 × $5,400
= $1,015 million
```

### 8.2 Total Budget Impact Formula

```
Total BI = Drug BI + Monitoring BI - Event Cost Offsets

Where:
Drug BI = Σ_years (N_IXA × Cost_IXA - N_displaced × Cost_displaced)
Monitoring BI = Σ_years (N_IXA × ΔMonitoring)
Event Offsets = Σ_events (Events_prevented × Cost_event)
```

### 8.3 5-Year Budget Impact Summary (US, Moderate)

| Year | Drug Cost | Monitoring | Event Offsets | Net BI |
|------|-----------|------------|---------------|--------|
| 1 | $1,015M | $76M | -$145M | $946M |
| 2 | $2,436M | $182M | -$348M | $2,270M |
| 3 | $4,071M | $304M | -$581M | $3,794M |
| 4 | $5,494M | $410M | -$784M | $5,120M |
| 5 | $6,528M | $488M | -$932M | $6,084M |

---

## 9. Implementation Details

### 9.1 CostInputs Class

```python
@dataclass
class CostInputs:
    """Cost inputs for BIM calculations."""
    # Drug costs (annual)
    ixa_001_cost: float = 6000.0
    spironolactone_cost: float = 180.0
    eplerenone_cost: float = 1200.0
    other_mra_cost: float = 600.0

    # Monitoring costs (annual)
    routine_monitoring: float = 1100.0
    ixa_incremental_monitoring: float = 405.0

    # Event costs (acute + year 1)
    mi_cost: float = 33500.0
    stroke_cost: float = 34000.0
    hf_cost: float = 23200.0
    esrd_cost: float = 125000.0
    af_cost: float = 12700.0
    hyperkalemia_cost: float = 12500.0
```

### 9.2 EventCosts Class

```python
@dataclass
class EventCosts:
    """Detailed event costs for budget impact calculations."""
    mi_acute: float = 25000.0
    mi_followup: float = 8500.0
    mi_ongoing: float = 4200.0

    stroke_acute: float = 22000.0
    stroke_followup: float = 12000.0
    stroke_ongoing: float = 8500.0

    hf_acute: float = 18000.0
    hf_followup: float = 6500.0
    hf_ongoing: float = 5200.0

    esrd_initiation: float = 35000.0
    esrd_annual: float = 90000.0

    af_acute: float = 8500.0
    af_ongoing: float = 3800.0
```

### 9.3 Code References

- **Implementation**: `src/bim/inputs.py:CostInputs, EventCosts`
- **Calculation**: `src/bim/calculator.py:BIMCalculator._calculate_costs`

---

## 10. Data Sources

### 10.1 Drug Cost Sources

| Source | Data Type | Year |
|--------|-----------|------|
| RedBook | AWP drug prices | 2024 |
| CMS ASP | Medicare reimbursement | 2024 |
| NADAC | Pharmacy acquisition | 2024 |
| Manufacturer | IXA-001 pricing | 2026 |

### 10.2 Medical Cost Sources

| Source | Data Type | Year |
|--------|-----------|------|
| HCUP NIS | Inpatient costs | 2022 |
| MEPS | Outpatient costs | 2022 |
| USRDS | ESRD costs | 2023 |
| Medicare Claims | Procedure costs | 2023 |

### 10.3 Indirect Cost Sources

| Source | Data Type | Year |
|--------|-----------|------|
| BLS | Wage data | 2024 |
| AARP | Caregiver survey | 2023 |
| Published literature | Productivity loss | Various |

---

## 11. PSA Distributions

### 11.1 Drug Costs

| Parameter | Distribution | Mean | SE | α/β |
|-----------|--------------|------|-----|-----|
| IXA-001 cost | Fixed | $6,000 | - | - |
| Spiro cost | Gamma | $180 | $36 | 25, 7.2 |
| Eplerenone cost | Gamma | $1,200 | $240 | 25, 48 |

### 11.2 Event Costs

| Parameter | Distribution | Mean | SE | α/β |
|-----------|--------------|------|-----|-----|
| MI cost | Gamma | $33,500 | $6,700 | 25, 1,340 |
| Stroke cost | Gamma | $34,000 | $6,800 | 25, 1,360 |
| HF cost | Gamma | $23,200 | $4,640 | 25, 928 |
| ESRD cost | Gamma | $125,000 | $25,000 | 25, 5,000 |

---

## 12. Limitations

1. **Price uncertainty**: IXA-001 pricing subject to negotiation and contracting
2. **Regional variation**: Costs vary significantly by payer and region
3. **Inflation**: Medical cost inflation not dynamically modeled
4. **Indirect costs**: Productivity estimates based on average wages
5. **Event attribution**: All events attributed to hypertension may overestimate offsets

---

## 13. References

1. Agency for Healthcare Research and Quality. HCUP National Inpatient Sample. 2022.

2. United States Renal Data System. 2023 Annual Data Report. NIDDK.

3. Centers for Medicare & Medicaid Services. Medicare Provider Payment Data. 2024.

4. Medi-Span RedBook. Drug Pricing Reference. 2024.

5. Medical Expenditure Panel Survey. Agency for Healthcare Research and Quality. 2022.

6. Bureau of Labor Statistics. Occupational Employment and Wage Statistics. 2024.

7. AARP Public Policy Institute. Valuing the Invaluable: 2023 Update.

---

**Document Control:**
- Version 1.0 - Initial release (February 2026)
- Reviewed by: HEOR Technical Lead
- Approved for HTA submission
