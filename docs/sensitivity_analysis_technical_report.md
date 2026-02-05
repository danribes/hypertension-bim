# Sensitivity Analysis Technical Report

## IXA-001 Budget Impact Model

**Document Version:** 1.0
**Date:** February 2026
**Author:** HEOR Technical Documentation Team
**Status:** Final

---

## 1. Executive Summary

This technical report documents the sensitivity analysis methodology in the IXA-001 Budget Impact Model (BIM). The model employs deterministic sensitivity analysis (DSA), probabilistic sensitivity analysis (PSA), and scenario analysis to characterize uncertainty in budget impact estimates and support payer decision-making.

---

## 2. Sensitivity Analysis Framework

### 2.1 Analysis Types

| Analysis Type | Purpose | Method | Output |
|---------------|---------|--------|--------|
| **Deterministic (DSA)** | Identify key drivers | One-way variation | Tornado diagram |
| **Probabilistic (PSA)** | Joint uncertainty | Monte Carlo | Distribution, percentiles |
| **Scenario** | Structural uncertainty | Alternative assumptions | Scenario comparison |
| **Threshold** | Decision boundaries | Parameter inversion | Breakeven values |

### 2.2 ISPOR BIA Task Force Alignment

The sensitivity analysis approach follows ISPOR BIA Good Practice guidelines:
- All key parameters subject to uncertainty are varied
- Ranges based on plausible clinical and market variation
- Results presented in multiple formats for different stakeholders

---

## 3. Deterministic Sensitivity Analysis (DSA)

### 3.1 Parameters Varied

| Category | Parameter | Base Case | Low | High | Source |
|----------|-----------|-----------|-----|------|--------|
| **Drug Costs** | IXA-001 annual cost | $6,000 | $4,800 | $7,200 | ±20% |
| | Spironolactone cost | $180 | $144 | $216 | ±20% |
| **Market** | Uptake Year 5 | 32% | 18% | 45% | Scenario range |
| | Market share displacement | Proportional | Conservative | Aggressive | Algorithm |
| **Population** | HTN prevalence | 32% | 26% | 38% | ±20% |
| | Resistant HTN % | 12% | 10% | 14% | ±20% |
| | Eligible % | 80% | 64% | 96% | ±20% |
| **Events** | MI rate | 1.5% | 1.2% | 1.8% | ±20% |
| | HF rate | 1.8% | 1.4% | 2.2% | ±20% |
| | ESRD rate | 0.5% | 0.4% | 0.6% | ±20% |
| **Treatment Effects** | MI RRR | 30% | 18% | 40% | 95% CI |
| | HF RRR | 50% | 38% | 60% | 95% CI |
| | ESRD RRR | 55% | 40% | 67% | 95% CI |
| **Event Costs** | MI cost | $33,500 | $26,800 | $40,200 | ±20% |
| | ESRD cost | $125,000 | $100,000 | $150,000 | ±20% |

### 3.2 Tornado Diagram Results

**5-Year Net Budget Impact Sensitivity (Base: $18.33B)**

```
                           Low ◄────────────────► High

IXA-001 Cost     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $14.7B - $22.0B
Uptake Rate      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $10.3B - $27.0B
HTN Prevalence   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $14.7B - $22.0B
HF RRR           ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $17.5B - $19.2B
ESRD RRR         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $17.8B - $18.9B
MI RRR           ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ $17.9B - $18.8B
ESRD Cost        ▓▓▓▓▓▓▓▓▓▓▓ $18.0B - $18.7B
MI Cost          ▓▓▓▓▓▓▓▓ $18.1B - $18.6B

             $10B      $15B      $20B      $25B      $30B
```

### 3.3 Key Drivers Identified

| Rank | Parameter | Impact (BI Range) | Driver Type |
|------|-----------|-------------------|-------------|
| 1 | Uptake rate | $16.7B swing | Market |
| 2 | IXA-001 cost | $7.3B swing | Cost |
| 3 | HTN prevalence | $7.3B swing | Population |
| 4 | HF RRR | $1.7B swing | Efficacy |
| 5 | ESRD RRR | $1.1B swing | Efficacy |

---

## 4. Probabilistic Sensitivity Analysis (PSA)

### 4.1 Parameter Distributions

| Parameter | Distribution | Mean | SE/Shape | Rationale |
|-----------|--------------|------|----------|-----------|
| HTN prevalence | Beta | 0.32 | α=64, β=136 | Proportion |
| Resistant % | Beta | 0.12 | α=24, β=176 | Proportion |
| MI rate | Beta | 0.015 | α=15, β=985 | Rate |
| HF rate | Beta | 0.018 | α=18, β=982 | Rate |
| ESRD rate | Beta | 0.005 | α=5, β=995 | Rate |
| MI cost | Gamma | $33,500 | α=25, β=1,340 | Cost |
| ESRD cost | Gamma | $125,000 | α=25, β=5,000 | Cost |
| IXA-001 RRR (MI) | Lognormal | 0.30 | σ=0.15 | Relative effect |
| IXA-001 RRR (HF) | Lognormal | 0.50 | σ=0.12 | Relative effect |
| Uptake multiplier | Triangular | 1.0 | min=0.6, max=1.4 | Market |

### 4.2 PSA Implementation

```python
def run_probabilistic_sensitivity(
    self,
    n_iterations: int = 1000,
    seed: int = 42
) -> PSAResults:
    """Run Monte Carlo simulation for PSA."""
    np.random.seed(seed)
    results = []

    for i in range(n_iterations):
        # Sample parameters
        sampled_inputs = self._sample_parameters()

        # Run model with sampled inputs
        bi_result = self.calculate(inputs=sampled_inputs)
        results.append({
            "iteration": i,
            "net_budget_impact": bi_result.net_budget_impact,
            "drug_cost": bi_result.total_drug_cost,
            "event_offset": bi_result.event_cost_offset,
            "patients_treated": bi_result.patients_on_ixa
        })

    return PSAResults(
        iterations=pd.DataFrame(results),
        mean=np.mean([r["net_budget_impact"] for r in results]),
        std=np.std([r["net_budget_impact"] for r in results]),
        percentiles=self._calculate_percentiles(results)
    )
```

### 4.3 PSA Results (1,000 iterations)

| Statistic | 5-Year Net BI ($B) |
|-----------|-------------------|
| Mean | $18.42 |
| Median | $18.15 |
| Std. Dev. | $4.23 |
| 5th percentile | $11.68 |
| 25th percentile | $15.44 |
| 75th percentile | $21.12 |
| 95th percentile | $26.35 |

### 4.4 Budget Impact Distribution

```
Probability Distribution of 5-Year Budget Impact

Frequency
    │
 12%├                    ▓▓▓▓
    │                  ▓▓▓▓▓▓▓▓
 10%├                ▓▓▓▓▓▓▓▓▓▓▓▓
    │              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  8%├            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    │          ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  6%├        ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    │      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  4%├    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  2%├▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    └─────────────────────────────────────────────
     $8B    $12B    $16B    $20B    $24B    $28B

     Mean: $18.42B    95% CI: $11.68B - $26.35B
```

---

## 5. Scenario Analysis

### 5.1 Pre-Defined Scenarios

| Scenario | Description | Key Assumptions |
|----------|-------------|-----------------|
| **Base Case** | Moderate uptake | Year 5: 32% share, standard costs |
| **Conservative** | Slow adoption | Year 5: 18% share, -10% efficacy |
| **Optimistic** | Rapid adoption | Year 5: 45% share, +10% efficacy |
| **High Price** | Premium pricing | IXA-001: $7,500/year |
| **Low Price** | Competitive pricing | IXA-001: $4,500/year |
| **PA Only** | Restricted indication | PA subgroup only |
| **Generic Entry** | Competitive threat | Year 3: generic eplerenone |

### 5.2 Scenario Results Comparison

| Scenario | 5-Year Net BI | vs. Base Case | BI/Patient |
|----------|---------------|---------------|------------|
| Base Case | $18.33B | - | $5,010 |
| Conservative | $10.31B | -44% | $5,408 |
| Optimistic | $27.02B | +47% | $5,029 |
| High Price | $23.08B | +26% | $6,307 |
| Low Price | $13.58B | -26% | $3,712 |
| PA Only | $2.42B | -87% | $4,414 |
| Generic Entry | $16.89B | -8% | $4,614 |

### 5.3 Scenario Visualization

```
5-Year Net Budget Impact by Scenario

PA Only        ████ $2.4B
Conservative   ████████████ $10.3B
Low Price      ████████████████ $13.6B
Generic Entry  █████████████████████ $16.9B
Base Case      ██████████████████████████ $18.3B
High Price     ███████████████████████████████ $23.1B
Optimistic     ████████████████████████████████████ $27.0B

               $0      $10B     $20B     $30B
```

---

## 6. Threshold Analysis

### 6.1 Price Threshold Analysis

**Question:** At what price is IXA-001 budget-neutral over 5 years?

```python
def price_threshold_analysis(
    self,
    target_bi: float = 0.0,
    tolerance: float = 0.01
) -> float:
    """Find IXA-001 price for target budget impact."""
    from scipy.optimize import brentq

    def objective(price):
        self.inputs.costs.ixa_001_cost = price
        result = self.calculate()
        return result.net_budget_impact - target_bi

    threshold = brentq(objective, 0, 20000)
    return threshold
```

**Results:**

| Target BI | IXA-001 Price | Price Reduction |
|-----------|---------------|-----------------|
| $18.33B (current) | $6,000/year | Reference |
| $10B | $4,100/year | -32% |
| $5B | $2,750/year | -54% |
| Budget neutral | $890/year | -85% |

### 6.2 Uptake Threshold Analysis

**Question:** At what uptake is BI acceptable (<$15B)?

| Target BI | Required Year 5 Uptake | Scenario Match |
|-----------|------------------------|----------------|
| <$25B | <40% | Within optimistic |
| <$20B | <35% | Within moderate |
| <$15B | <25% | Between scenarios |
| <$10B | <18% | Conservative |

### 6.3 Efficacy Threshold Analysis

**Question:** What efficacy makes IXA-001 cost-neutral in PA subgroup?

| Event | Required RRR | Current RRR | Gap |
|-------|--------------|-------------|-----|
| HF | 35% | 50% | -15% (met) |
| ESRD | 42% | 55% | -13% (met) |
| MI | 22% | 30% | -8% (met) |
| AF | 48% | 60% | -12% (met) |

---

## 7. Implementation Details

### 7.1 TornadoResult Class

```python
@dataclass
class TornadoResult:
    """Result from tornado (one-way) sensitivity analysis."""
    parameter: str
    base_value: float
    low_value: float
    high_value: float
    bi_at_base: float
    bi_at_low: float
    bi_at_high: float
    swing: float  # |high - low|

    @property
    def is_positive_correlation(self) -> bool:
        """True if higher parameter = higher BI."""
        return self.bi_at_high > self.bi_at_low
```

### 7.2 PSAResults Class

```python
@dataclass
class PSAResults:
    """Results from probabilistic sensitivity analysis."""
    iterations: pd.DataFrame
    mean: float
    std: float
    percentiles: Dict[int, float]

    def probability_below(self, threshold: float) -> float:
        """Calculate probability BI is below threshold."""
        below = (self.iterations["net_budget_impact"] < threshold).sum()
        return below / len(self.iterations)

    def credible_interval(self, level: float = 0.95) -> Tuple[float, float]:
        """Return credible interval at specified level."""
        alpha = (1 - level) / 2
        lower = self.iterations["net_budget_impact"].quantile(alpha)
        upper = self.iterations["net_budget_impact"].quantile(1 - alpha)
        return (lower, upper)
```

### 7.3 Code References

- **Tornado**: `src/bim/calculator.py:BIMCalculator.run_tornado_analysis`
- **PSA**: `src/bim/calculator.py:BIMCalculator.run_probabilistic_sensitivity`
- **Parameters**: `src/bim/inputs.py:SensitivityParameters`

---

## 8. Convergence Analysis

### 8.1 PSA Convergence

The PSA was tested for convergence by tracking mean BI across iterations:

| Iterations | Mean BI ($B) | SE ($B) | CV |
|------------|--------------|---------|-----|
| 100 | $18.51 | $0.42 | 2.3% |
| 500 | $18.44 | $0.19 | 1.0% |
| 1,000 | $18.42 | $0.13 | 0.7% |
| 5,000 | $18.41 | $0.06 | 0.3% |
| 10,000 | $18.41 | $0.04 | 0.2% |

**Recommendation:** 1,000 iterations provide acceptable convergence (CV < 1%)

### 8.2 Convergence Plot

```
Mean Budget Impact by PSA Iteration Count

$19.0B├─────────────────────────────────────
      │╲
$18.8B├──╲───────────────────────────────────
      │   ╲
$18.6B├────╲──────────────────────────────────
      │     ╲
$18.4B├──────────────────────────────────────
      │         ──────────────────────────────
$18.2B├──────────────────────────────────────
      └─────────────────────────────────────
       100   500   1000  2500  5000  10000
                   Iterations
```

---

## 9. Validation

### 9.1 Distribution Validation

| Parameter | Distribution | Mean Check | Variance Check |
|-----------|--------------|------------|----------------|
| HTN prevalence | Beta(64,136) | 0.320 ✓ | 0.0011 ✓ |
| MI rate | Beta(15,985) | 0.015 ✓ | 0.000015 ✓ |
| MI cost | Gamma(25,1340) | $33,500 ✓ | $44.9M ✓ |
| RRR | Lognormal | 0.30 ✓ | 0.002 ✓ |

### 9.2 Face Validity

Sensitivity analysis results were reviewed by clinical and HEOR experts:
- Key drivers align with clinical expectations (uptake, price, efficacy)
- PSA distribution shape is plausible (right-skewed, bounded)
- Scenario ranges span realistic market conditions

---

## 10. Limitations

1. **Parameter independence**: PSA assumes uncorrelated parameters; some may correlate
2. **Distributional assumptions**: True distributions unknown; selected based on convention
3. **Scenario completeness**: Not all possible scenarios can be pre-specified
4. **Non-linearity**: Tornado assumes linear relationships within ranges
5. **Dynamic effects**: Model is static; does not capture time-varying uncertainty

---

## 11. References

1. Briggs AH, Weinstein MC, Fenwick EAL, et al. Model parameter estimation and uncertainty: a report of the ISPOR-SMDM Modeling Good Research Practices Task Force-6. Value Health. 2012;15(6):835-842.

2. Sullivan SD, Mauskopf JA, Augustovski F, et al. Budget impact analysis-principles of good practice: report of the ISPOR 2012 Budget Impact Analysis Good Practice II Task Force. Value Health. 2014;17(1):5-14.

3. Caro JJ, Briggs AH, Siebert U, Kuntz KM. Modeling good research practices--overview: a report of the ISPOR-SMDM Modeling Good Research Practices Task Force-1. Value Health. 2012;15(6):796-803.

4. Husereau D, Drummond M, Augustovski F, et al. Consolidated Health Economic Evaluation Reporting Standards 2022 (CHEERS 2022). Value Health. 2022;25(1):3-9.

---

**Document Control:**
- Version 1.0 - Initial release (February 2026)
- Reviewed by: HEOR Technical Lead
- Approved for HTA submission
