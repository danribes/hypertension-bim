# Subgroup Analysis Technical Report

## IXA-001 Budget Impact Model

**Document Version:** 1.0
**Date:** February 2026
**Author:** HEOR Technical Documentation Team
**Status:** Final

---

## 1. Executive Summary

This technical report documents the subgroup analysis methodology in the IXA-001 Budget Impact Model (BIM). The model stratifies budget impact estimates across clinically meaningful patient subgroups to inform targeted formulary positioning, prior authorization criteria, and value-based contracting negotiations.

---

## 2. Subgroup Framework

### 2.1 Rationale for Subgroup Analysis

Subgroup analysis in budget impact modeling serves to:
1. Identify high-value patient populations where IXA-001 provides greatest budget efficiency
2. Support prior authorization criteria development
3. Enable value-based contracting based on patient characteristics
4. Inform formulary tier decisions by indication
5. Support regional budget allocation

### 2.2 Pre-Specified Subgroups

| Dimension | Categories | Clinical Rationale |
|-----------|------------|-------------------|
| **Secondary HTN Etiology** | PA, RAS, Pheo, OSA, Essential | IXA-001 targets aldosterone pathway; PA shows greatest benefit |
| **Age** | <65, ≥65 years | Event rates and treatment tolerability vary by age |
| **CKD Status** | CKD Stage 3-4, Non-CKD | Renal protection is key outcome; CKD patients at higher risk |
| **Diabetes Status** | Diabetic, Non-diabetic | Cardiorenal risk amplification |
| **Treatment History** | MRA-naive, MRA-experienced | Prior MRA use affects response expectations |

---

## 3. Secondary HTN Etiology Subgroups

### 3.1 Primary Aldosteronism (PA)

**Prevalence:** 15% of resistant HTN population

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Baseline event multiplier | 1.5-3.0× | Higher aldosterone-mediated damage |
| IXA-001 efficacy multiplier | 1.3× | Targeted mechanism |
| Event cost offset | +85% vs. general | Higher baseline events |
| Net BI impact | Favorable | Significant cost offsets |

**Budget Impact Comparison (5-year, per 1000 patients):**

| Metric | General Population | PA Subgroup | Difference |
|--------|-------------------|-------------|------------|
| Drug cost | $30.0M | $30.0M | $0 |
| Event cost offset | -$12.5M | -$23.1M | -$10.6M |
| Net BI | $17.5M | $6.9M | -$10.6M |
| Cost per event prevented | $18,500 | $7,200 | -61% |

### 3.2 Renovascular Stenosis (RAS)

**Prevalence:** 8% of resistant HTN population

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Baseline event multiplier | 1.2× | Moderate risk elevation |
| IXA-001 efficacy multiplier | 1.1× | Partial mechanism overlap |
| Event cost offset | +35% vs. general | Moderate benefit |

### 3.3 Pheochromocytoma (Pheo)

**Prevalence:** 2% of resistant HTN population

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Baseline event multiplier | 1.4× | Catecholamine-mediated damage |
| IXA-001 efficacy multiplier | 0.9× | Not primary mechanism |
| Event cost offset | +15% vs. general | Limited benefit |

### 3.4 Obstructive Sleep Apnea (OSA)

**Prevalence:** 25% of resistant HTN population

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Baseline event multiplier | 1.3× | Elevated nocturnal BP |
| IXA-001 efficacy multiplier | 1.05× | Some aldosterone overlap |
| Event cost offset | +28% vs. general | Moderate benefit |

### 3.5 Essential HTN (No Secondary Cause)

**Prevalence:** 50% of resistant HTN population

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Baseline event multiplier | 1.0× | Reference population |
| IXA-001 efficacy multiplier | 1.0× | Standard response |
| Event cost offset | Reference | Baseline comparison |

---

## 4. Age-Based Subgroups

### 4.1 Age <65 Years

**Prevalence:** 55% of resistant HTN population

| Parameter | Value | Source |
|-----------|-------|--------|
| CV event rate multiplier | 0.7× | SPRINT subgroup |
| Treatment persistence | 85% at Year 5 | Higher adherence |
| Indirect cost impact | High | Working age, productivity |

**Budget Impact Drivers:**
- Lower baseline event rates reduce cost offset potential
- Higher indirect cost savings (productivity)
- Better treatment persistence sustains benefit

### 4.2 Age ≥65 Years

**Prevalence:** 45% of resistant HTN population

| Parameter | Value | Source |
|-----------|-------|--------|
| CV event rate multiplier | 1.5× | SPRINT subgroup |
| Treatment persistence | 72% at Year 5 | Age-related decline |
| Indirect cost impact | Low | Retired population |

**Budget Impact Drivers:**
- Higher baseline event rates increase cost offsets
- Lower persistence reduces sustained benefit
- Greater absolute risk reduction per patient

---

## 5. CKD Status Subgroups

### 5.1 CKD Stage 3-4

**Prevalence:** 25% of resistant HTN population

| Event | General Rate | CKD Multiplier | CKD Rate |
|-------|--------------|----------------|----------|
| MI | 1.5% | 1.5× | 2.25% |
| Stroke | 1.0% | 1.3× | 1.30% |
| HF | 1.8% | 1.8× | 3.24% |
| ESRD | 0.5% | 3.5× | 1.75% |

**IXA-001 Efficacy in CKD:**
- ESRD RRR: 60% (vs. 55% general)
- Renal protection is primary value driver
- Cost offset: +125% vs. general population

### 5.2 Non-CKD (eGFR ≥60)

**Prevalence:** 75% of resistant HTN population

| Parameter | Value | Notes |
|-----------|-------|-------|
| ESRD risk | Very low | <0.1% annual |
| CV event rates | Standard | Reference |
| Renal cost offset | Minimal | Low ESRD risk |

---

## 6. Diabetes Subgroups

### 6.1 Diabetic Patients

**Prevalence:** 35% of resistant HTN population

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| CV event multiplier | 1.4× | Cardiometabolic risk |
| CKD progression multiplier | 1.6× | Diabetic nephropathy |
| IXA-001 efficacy | 1.15× | Synergistic benefit |

**Budget Impact:**
- Higher baseline events increase cost offset
- Diabetic nephropathy prevention is high-value
- Supports tier 2 placement for T2DM + resistant HTN

### 6.2 Non-Diabetic Patients

**Prevalence:** 65% of resistant HTN population

| Parameter | Value | Notes |
|-----------|-------|-------|
| CV event rate | Standard | Reference |
| CKD progression | Standard | Reference |
| IXA-001 efficacy | Standard | Reference |

---

## 7. Subgroup-Specific Budget Impact Results

### 7.1 Summary Table (5-Year, Moderate Scenario, US)

| Subgroup | Population | Drug BI ($M) | Event Offset ($M) | Net BI ($M) | BI/Patient |
|----------|------------|--------------|-------------------|-------------|------------|
| **All Patients** | 3,659,667 | $19,826 | -$1,496 | $18,330 | $5,010 |
| **PA** | 548,950 | $2,974 | -$551 | $2,423 | $4,414 |
| **Non-PA** | 3,110,717 | $16,852 | -$945 | $15,907 | $5,115 |
| **Age <65** | 2,012,817 | $10,904 | -$688 | $10,216 | $5,075 |
| **Age ≥65** | 1,646,850 | $8,922 | -$808 | $8,114 | $4,927 |
| **CKD 3-4** | 914,917 | $4,957 | -$524 | $4,433 | $4,845 |
| **Non-CKD** | 2,744,750 | $14,870 | -$972 | $13,898 | $5,065 |
| **Diabetic** | 1,280,883 | $6,939 | -$592 | $6,347 | $4,956 |
| **Non-Diabetic** | 2,378,783 | $12,887 | -$904 | $11,983 | $5,038 |

### 7.2 Budget Impact per Patient by Subgroup

```
Budget Impact per Patient (5-Year)

PA               ████████████████████ $4,414
Age ≥65          ████████████████████████ $4,927
CKD 3-4          ████████████████████████ $4,845
Diabetic         ████████████████████████ $4,956
Non-Diabetic     █████████████████████████ $5,038
Age <65          █████████████████████████ $5,075
Non-CKD          █████████████████████████ $5,065
Non-PA           █████████████████████████ $5,115
All Patients     █████████████████████████ $5,010
                 $4,000    $4,500    $5,000    $5,500
```

### 7.3 Key Finding: PA Subgroup Value

The PA subgroup shows **12% lower budget impact per patient** than the general population due to:
1. Higher baseline event rates (3× AF, 2× HF)
2. Greater IXA-001 efficacy (1.3× response multiplier)
3. Substantial cost offsets from event prevention

---

## 8. Implementation Details

### 8.1 SubgroupDefinitions Class

```python
@dataclass
class SubgroupDefinitions:
    """Subgroup category definitions for BIM analysis."""
    # Etiology subgroups
    etiology_categories: Dict[str, float] = field(default_factory=lambda: {
        "primary_aldosteronism": 0.15,
        "renovascular": 0.08,
        "pheochromocytoma": 0.02,
        "sleep_apnea": 0.25,
        "essential": 0.50
    })

    # Age subgroups
    age_categories: Dict[str, float] = field(default_factory=lambda: {
        "under_65": 0.55,
        "65_and_over": 0.45
    })

    # CKD subgroups
    ckd_categories: Dict[str, float] = field(default_factory=lambda: {
        "ckd_stage_3_4": 0.25,
        "non_ckd": 0.75
    })

    # Diabetes subgroups
    diabetes_categories: Dict[str, float] = field(default_factory=lambda: {
        "diabetic": 0.35,
        "non_diabetic": 0.65
    })
```

### 8.2 SubgroupParameters Class

```python
@dataclass
class SubgroupParameters:
    """Subgroup-specific parameter modifiers."""
    # Event rate multipliers by subgroup
    event_multipliers: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "primary_aldosteronism": {
            "mi": 1.40, "stroke": 1.50, "hf": 2.05,
            "esrd": 1.80, "af": 3.00
        },
        "ckd_stage_3_4": {
            "mi": 1.50, "stroke": 1.30, "hf": 1.80,
            "esrd": 3.50, "af": 1.20
        },
        "65_and_over": {
            "mi": 1.50, "stroke": 1.70, "hf": 2.00,
            "esrd": 1.20, "af": 2.20
        }
    })

    # Efficacy multipliers
    efficacy_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "primary_aldosteronism": 1.30,
        "ckd_stage_3_4": 1.10,
        "diabetic": 1.15,
        "65_and_over": 0.95
    })
```

### 8.3 Code References

- **Definitions**: `src/bim/inputs.py:SubgroupDefinitions`
- **Parameters**: `src/bim/inputs.py:SubgroupParameters`
- **Calculation**: `src/bim/calculator.py:BIMCalculator._calculate_subgroups`

---

## 9. Formulary Decision Support

### 9.1 Prior Authorization Criteria Recommendations

Based on subgroup analysis, recommended PA criteria:

| Criterion | Requirement | Rationale |
|-----------|-------------|-----------|
| Diagnosis | Confirmed resistant HTN | Target population |
| Prior therapy | Failed ≥2 MRAs or intolerant | Step therapy |
| Testing | Aldosterone-to-renin ratio | Identifies PA |
| Monitoring | K+ at baseline, 4 weeks | Safety |

### 9.2 Tier Placement by Subgroup

| Subgroup | Recommended Tier | Rationale |
|----------|------------------|-----------|
| PA + CKD | Tier 2 (Preferred) | Highest value, greatest offset |
| PA only | Tier 2 (Preferred) | Strong value proposition |
| CKD only | Tier 2 (Preferred) | Renal protection value |
| Diabetic + CKD | Tier 2 (Preferred) | Cardiorenal value |
| General | Tier 3 (Non-preferred) | Lower cost offset |

---

## 10. Validation

### 10.1 Subgroup Prevalence Validation

| Subgroup | Model | Literature | Source |
|----------|-------|------------|--------|
| PA | 15% | 11-21% | Douma 2008 |
| CKD 3-4 | 25% | 20-30% | CRIC |
| Diabetes | 35% | 30-40% | NHANES |
| Age ≥65 | 45% | 40-50% | Census |

### 10.2 Event Multiplier Validation

| Subgroup × Event | Model | Literature | Source |
|------------------|-------|------------|--------|
| PA × AF | 3.0× | 2.8-3.5× | Monticone 2018 |
| PA × HF | 2.05× | 1.8-2.3× | Monticone 2018 |
| CKD × ESRD | 3.5× | 3.0-4.0× | USRDS |

---

## 11. Limitations

1. **Subgroup independence**: Analysis assumes subgroup effects are multiplicative; interactions may differ
2. **Selection bias**: Subgroup definitions based on claims data may miss undiagnosed conditions
3. **Small sample sizes**: Rare subgroups (Pheo) have higher uncertainty
4. **Treatment effect heterogeneity**: RRRs may vary more within subgroups than modeled
5. **Dynamic composition**: Subgroup proportions may change over time horizon

---

## 12. References

1. Douma S, Petidis K, Doumas M, et al. Prevalence of primary hyperaldosteronism in resistant hypertension. Lancet. 2008;371(9628):1921-1926.

2. Monticone S, D'Ascenzo F, Moretti C, et al. Cardiovascular events and target organ damage in primary aldosteronism. Eur Heart J. 2018;39(30):2727-2737.

3. SPRINT Research Group. Intensive Blood-Pressure Control. N Engl J Med. 2015;373(22):2103-2116.

4. Chronic Renal Insufficiency Cohort Study. Design and Methods. J Am Soc Nephrol. 2003;14(7 Suppl 2):S148-S153.

5. United States Renal Data System. 2023 Annual Data Report. NIDDK.

6. Centers for Disease Control and Prevention. National Health and Nutrition Examination Survey. 2020.

---

**Document Control:**
- Version 1.0 - Initial release (February 2026)
- Reviewed by: HEOR Technical Lead
- Approved for HTA submission
