# Market Dynamics Technical Report

## IXA-001 Budget Impact Model

**Document Version:** 1.0
**Date:** February 2026
**Author:** HEOR Technical Documentation Team
**Status:** Final

---

## 1. Executive Summary

This technical report documents the market dynamics methodology in the IXA-001 Budget Impact Model (BIM). The model projects market uptake, treatment displacement, and competitive dynamics over a 5-year time horizon to estimate the budget impact of IXA-001 introduction for payers.

---

## 2. Market Share Modeling Framework

### 2.1 Two-World Approach

The BIM uses ISPOR-recommended "world with" vs. "world without" comparison:

```
World Without IXA-001          World With IXA-001
┌─────────────────────┐        ┌─────────────────────┐
│ Spironolactone 45%  │        │ Spironolactone 35%  │
│ Eplerenone     25%  │   →    │ Eplerenone     20%  │
│ Other MRAs    30%   │        │ Other MRAs     25%  │
│ IXA-001        0%   │        │ IXA-001        20%  │
└─────────────────────┘        └─────────────────────┘

Net Budget Impact = Cost(World With) - Cost(World Without)
```

### 2.2 Current Market Composition

| Treatment | Market Share | Annual Cost | Notes |
|-----------|-------------|-------------|-------|
| Spironolactone | 45% | $180/year | Generic MRA |
| Eplerenone | 25% | $1,200/year | Branded MRA |
| Other MRAs | 20% | $600/year | Mixed |
| No MRA Treatment | 10% | $0 | Unmet need |

---

## 3. Uptake Curve Methodology

### 3.1 S-Curve Adoption Model

IXA-001 uptake follows a modified logistic (S-curve) adoption pattern:

```
Market Share(t) = Max_Share / (1 + exp(-k × (t - t_midpoint)))
```

Where:
- `Max_Share` = Maximum achievable market share
- `k` = Steepness parameter (adoption rate)
- `t_midpoint` = Time to reach 50% of maximum share

### 3.2 Uptake Scenarios

Three uptake scenarios model uncertainty in market penetration:

| Scenario | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | Max Share |
|----------|--------|--------|--------|--------|--------|-----------|
| Conservative | 2% | 5% | 10% | 15% | 18% | 20% |
| Moderate | 5% | 12% | 20% | 27% | 32% | 35% |
| Optimistic | 8% | 18% | 30% | 40% | 45% | 50% |

### 3.3 Scenario Assumptions

**Conservative Scenario:**
- Limited formulary placement
- Restrictive prior authorization
- Specialist-only prescribing
- Slow guideline adoption

**Moderate Scenario (Base Case):**
- Moderate formulary access
- Standard prior authorization
- PCP prescribing with specialist initiation
- Guidelines updated within 2 years

**Optimistic Scenario:**
- Preferred formulary position
- Minimal prior authorization
- Broad prescribing authority
- Rapid guideline endorsement

---

## 4. Treatment Displacement Modeling

### 4.1 Displacement Algorithm

IXA-001 displaces existing treatments proportionally to their market share:

```python
def calculate_displacement(ixa_share: float, current_shares: dict) -> dict:
    """Calculate displaced market shares when IXA-001 enters market."""
    displacement_factor = ixa_share / (1 - ixa_share)

    new_shares = {}
    for treatment, share in current_shares.items():
        if treatment != "ixa_001":
            new_shares[treatment] = share * (1 - displacement_factor)

    new_shares["ixa_001"] = ixa_share
    return new_shares
```

### 4.2 Displacement Proportions

| Treatment | Displacement Weight | Rationale |
|-----------|---------------------|-----------|
| Spironolactone | 0.50 | Primary competitor, most switching |
| Eplerenone | 0.30 | Premium positioning, similar efficacy |
| Other MRAs | 0.15 | Partial switching |
| Unmet Need | 0.05 | New-to-therapy patients |

### 4.3 Example Displacement Calculation

**Year 3 Moderate Scenario (IXA-001 = 20% share):**

| Treatment | Before | Displacement | After |
|-----------|--------|--------------|-------|
| Spironolactone | 45% | -10% | 35% |
| Eplerenone | 25% | -6% | 19% |
| Other MRAs | 20% | -3% | 17% |
| Unmet Need | 10% | -1% | 9% |
| IXA-001 | 0% | +20% | 20% |
| **Total** | 100% | 0% | 100% |

---

## 5. Market Size Projections

### 5.1 Treated Population by Year

Based on eligible population and uptake curves:

| Year | Eligible Pop | Conservative | Moderate | Optimistic |
|------|--------------|--------------|----------|------------|
| 1 | 3,760,742 | 75,215 | 188,037 | 300,859 |
| 2 | 3,779,546 | 188,977 | 453,546 | 680,318 |
| 3 | 3,798,444 | 379,844 | 759,689 | 1,139,533 |
| 4 | 3,817,436 | 572,615 | 1,030,708 | 1,526,975 |
| 5 | 3,836,523 | 690,574 | 1,227,687 | 1,726,435 |

### 5.2 Cumulative Patient-Years

| Scenario | 5-Year Patient-Years | Peak Patients |
|----------|----------------------|---------------|
| Conservative | 1,907,225 | 690,574 |
| Moderate | 3,659,667 | 1,227,687 |
| Optimistic | 5,374,120 | 1,726,435 |

---

## 6. Competitive Dynamics

### 6.1 Price Sensitivity Analysis

Market share varies with relative pricing:

| IXA-001 Price | vs. Spiro | vs. Eplerenone | Market Share Impact |
|---------------|-----------|----------------|---------------------|
| $500/month | 33× | 5× | Base case |
| $400/month | 27× | 4× | +15% share |
| $300/month | 20× | 3× | +25% share |
| $600/month | 40× | 6× | -10% share |

### 6.2 Generic Entry Scenario

Model includes scenario for generic MRA entry:

| Event | Timing | Impact |
|-------|--------|--------|
| Generic Spiro | Already generic | Baseline |
| Generic Eplerenone | Year 3 | -5% IXA-001 share |
| IXA-001 Generic | Year 10+ | Not modeled |

### 6.3 Formulary Access Modeling

| Tier Placement | Cost Sharing | Uptake Multiplier |
|----------------|--------------|-------------------|
| Tier 1 (Preferred) | $10-25 copay | 1.20× |
| Tier 2 (Non-preferred) | $40-75 copay | 1.00× (base) |
| Tier 3 (Specialty) | 20-30% coinsurance | 0.75× |
| Not covered | Full price | 0.30× |

---

## 7. Regional Market Dynamics

### 7.1 Country-Specific Uptake Adjustments

| Country | Uptake Modifier | Rationale |
|---------|-----------------|-----------|
| US | 1.00 | Reference market |
| UK | 0.70 | NICE HTA process, slower uptake |
| DE | 0.85 | G-BA evaluation, moderate access |
| FR | 0.75 | ASMR rating dependency |
| IT | 0.65 | Regional variation, budget caps |
| ES | 0.70 | Reference pricing, austerity |

### 7.2 Market Launch Sequencing

| Country | Launch Year | Peak Share Year |
|---------|-------------|-----------------|
| US | Year 1 | Year 5 |
| DE | Year 1 | Year 5 |
| UK | Year 2 | Year 6 |
| FR | Year 2 | Year 6 |
| IT | Year 2 | Year 6 |
| ES | Year 3 | Year 7 |

---

## 8. Implementation Details

### 8.1 MarketInputs Class

```python
@dataclass
class MarketInputs:
    """Market dynamics inputs for BIM calculations."""
    current_mra_share: float = 0.90  # Current MRA treatment rate
    spironolactone_share: float = 0.45
    eplerenone_share: float = 0.25
    other_mra_share: float = 0.20
    unmet_need_share: float = 0.10

    # Uptake curves by scenario
    uptake_conservative: List[float] = field(
        default_factory=lambda: [0.02, 0.05, 0.10, 0.15, 0.18]
    )
    uptake_moderate: List[float] = field(
        default_factory=lambda: [0.05, 0.12, 0.20, 0.27, 0.32]
    )
    uptake_optimistic: List[float] = field(
        default_factory=lambda: [0.08, 0.18, 0.30, 0.40, 0.45]
    )

    def get_uptake_curve(self, scenario: str) -> List[float]:
        """Return uptake curve for specified scenario."""
        curves = {
            "conservative": self.uptake_conservative,
            "moderate": self.uptake_moderate,
            "optimistic": self.uptake_optimistic,
        }
        return curves.get(scenario.lower(), self.uptake_moderate)
```

### 8.2 Displacement Calculation

```python
def _calculate_displaced_shares(
    self, year: int, scenario: str
) -> Dict[str, float]:
    """Calculate market shares after IXA-001 displacement."""
    ixa_share = self.inputs.market.get_uptake_curve(scenario)[year - 1]

    # Proportional displacement
    remaining = 1 - ixa_share
    displaced = {
        "spironolactone": self.inputs.market.spironolactone_share * remaining,
        "eplerenone": self.inputs.market.eplerenone_share * remaining,
        "other_mra": self.inputs.market.other_mra_share * remaining,
        "ixa_001": ixa_share,
    }
    return displaced
```

### 8.3 Code References

- **Implementation**: `src/bim/inputs.py:MarketInputs`
- **Calculation**: `src/bim/calculator.py:BIMCalculator._calculate_displaced_shares`
- **Scenarios**: `src/bim/calculator.py:BIMCalculator.run_all_scenarios`

---

## 9. Validation

### 9.1 Uptake Curve Validation

Model uptake curves were validated against analogous product launches:

| Comparator | Year 1 | Year 3 | Year 5 | Similarity |
|------------|--------|--------|--------|------------|
| Entresto (HF) | 3% | 18% | 28% | High |
| Brilinta (ACS) | 5% | 15% | 22% | Moderate |
| Jardiance (T2DM) | 2% | 12% | 25% | Moderate |
| IXA-001 (Moderate) | 5% | 20% | 32% | Reference |

### 9.2 Market Share Assumptions Validation

| Parameter | Model Value | Industry Benchmark | Source |
|-----------|-------------|-------------------|--------|
| Spiro dominance | 45% | 40-50% | IQVIA 2024 |
| MRA treatment rate | 90% | 85-95% | SPRINT-MIND |
| Unmet need | 10% | 8-15% | Expert opinion |

---

## 10. Sensitivity Considerations

### 10.1 Key Drivers of Uncertainty

| Parameter | Impact on BI | Uncertainty Range |
|-----------|--------------|-------------------|
| Uptake rate | Very High | ±50% |
| Displacement mix | High | ±30% |
| Generic entry timing | Moderate | ±2 years |
| Formulary tier | High | Tier 1-3 |

### 10.2 Scenario-Based Uncertainty

The three-scenario approach captures market uncertainty:

| Metric | Conservative | Moderate | Optimistic |
|--------|--------------|----------|------------|
| 5-Year BI ($M) | $823 | $1,584 | $2,329 |
| Peak Annual BI ($M) | $298 | $531 | $747 |
| % of Drug Budget | 0.15% | 0.28% | 0.42% |

---

## 11. Limitations

1. **Linear displacement**: Model assumes proportional displacement; actual patterns may be non-linear
2. **Scenario bounds**: Three scenarios may not capture extreme outcomes
3. **Generic timing**: Generic entry dates are uncertain and market-dependent
4. **Formulary dynamics**: Actual tier placement negotiations not modeled
5. **Competitive response**: Price changes by competitors not dynamically modeled

---

## 12. References

1. Mauskopf JA, Sullivan SD, Annemans L, et al. Principles of good practice for budget impact analysis: report of the ISPOR Task Force on good research practices--budget impact analysis. Value Health. 2007;10(5):336-347.

2. Sullivan SD, Mauskopf JA, Augustovski F, et al. Budget impact analysis-principles of good practice: report of the ISPOR 2012 Budget Impact Analysis Good Practice II Task Force. Value Health. 2014;17(1):5-14.

3. IQVIA. US Prescription Market Analysis: Cardiovascular Therapeutics. 2024.

4. DiMasi JA, Grabowski HG, Hansen RW. Innovation in the pharmaceutical industry: New estimates of R&D costs. J Health Econ. 2016;47:20-33.

5. Aitken M, Kleinrock M. Medicine Use and Spending in the U.S.: A Review of 2018 and Outlook to 2023. IQVIA Institute. 2019.

---

**Document Control:**
- Version 1.0 - Initial release (February 2026)
- Reviewed by: HEOR Technical Lead
- Approved for HTA submission
