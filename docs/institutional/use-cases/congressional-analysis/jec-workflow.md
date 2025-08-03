# Joint Economic Committee Analysis Workflow

## Overview

The Joint Economic Committee (JEC) and other congressional committees use microsimulation models to analyze the distributional and revenue effects of proposed legislation. This guide outlines how PolicyEngine US can support congressional analysis workflows.

## Key Analysis Types

### 1. Revenue Estimation

**Static Revenue Scoring**
Calculate first-order revenue effects without behavioral responses:

```python
from policyengine_us import Microsimulation

# Baseline
baseline = Microsimulation()

# Reform (e.g., increase CTC to $3,000)
def reform(parameters):
    parameters.gov.irs.credits.ctc.amount.update(3_000, "2025-01-01")
    return parameters

reformed = Microsimulation(reform=reform)

# Revenue impact
baseline_revenue = baseline.calculate("income_tax", 2025).sum()
reform_revenue = reformed.calculate("income_tax", 2025).sum()
revenue_impact = reform_revenue - baseline_revenue

print(f"Revenue impact: ${revenue_impact/1e9:.1f} billion")
```

**Multi-Year Budget Window**
Standard congressional scoring uses 10-year windows:

```python
def calculate_budget_impact(reform):
    impacts = {}
    for year in range(2025, 2035):
        baseline = Microsimulation()
        reformed = Microsimulation(reform=reform)
        
        baseline_rev = baseline.calculate("income_tax", year).sum()
        reform_rev = reformed.calculate("income_tax", year).sum()
        impacts[year] = reform_rev - baseline_rev
    
    return impacts
```

### 2. Distributional Analysis

**Income Quintile Tables**
Standard format for congressional distribution tables:

```python
def create_distribution_table(simulation, year):
    income = simulation.calculate("household_income", year)
    weights = simulation.calculate("household_weight", year)
    
    # Calculate weighted quintiles
    quintiles = weighted_quantile(income, weights, [0.2, 0.4, 0.6, 0.8])
    
    results = []
    for i, (low, high) in enumerate(zip([0] + quintiles, quintiles + [np.inf])):
        mask = (income >= low) & (income < high)
        
        results.append({
            "Quintile": i + 1,
            "Income Range": f"${low:,.0f}-${high:,.0f}",
            "Average Tax Change": weighted_mean(tax_change[mask], weights[mask]),
            "Percent Change": percent_change[mask].mean(),
            "Share of Total": share_of_benefit[mask].sum()
        })
    
    return pd.DataFrame(results)
```

### 3. Effective Tax Rate Analysis

Calculate average and marginal tax rates by income group:

```python
def calculate_effective_rates(simulation, year):
    income = simulation.calculate("adjusted_gross_income", year)
    tax = simulation.calculate("income_tax", year)
    
    # Average effective tax rate
    aetr = tax / income
    
    # Marginal rate (using small income increment)
    mtr = simulation.calculate("marginal_tax_rate", year)
    
    return {
        "income_decile": income_decile,
        "average_rate": aetr.groupby(income_decile).mean(),
        "marginal_rate": mtr.groupby(income_decile).mean()
    }
```

## Standard Outputs

### Distribution Table Format

| Income Group | Average Tax Change | Percent with Tax Cut | Share of Total |
|--------------|-------------------|---------------------|----------------|
| Bottom 20% | -$150 | 45% | 5% |
| Second 20% | -$425 | 78% | 12% |
| Middle 20% | -$875 | 85% | 18% |
| Fourth 20% | -$1,250 | 82% | 25% |
| Top 20% | -$3,500 | 90% | 40% |
| All | -$1,250 | 79% | 100% |

### Revenue Table Format

| Fiscal Year | Revenue Impact (billions) | Outlays Impact | Deficit Impact |
|-------------|--------------------------|----------------|----------------|
| 2025 | -$125.3 | +$15.2 | +$140.5 |
| 2026 | -$128.7 | +$15.8 | +$144.5 |
| 2027 | -$132.4 | +$16.4 | +$148.8 |
| ... | ... | ... | ... |
| 2034 | -$155.2 | +$19.7 | +$174.9 |
| **10-Year Total** | **-$1,385.6** | **+$172.3** | **+$1,557.9** |

## Reconciliation Instructions

### Byrd Rule Compliance

When analyzing bills under reconciliation:

1. **Revenue Effects**: Must impact revenues or outlays
2. **Deficit Impact**: Cannot increase deficits beyond budget window
3. **Social Security**: Cannot affect OASDI trust funds

```python
def check_byrd_rule_compliance(reform):
    # Check 10-year deficit impact
    ten_year_impact = sum(calculate_budget_impact(reform).values())
    
    # Check long-term deficit impact (simplified)
    year_10_impact = calculate_budget_impact(reform)[2034]
    year_11_impact = year_10_impact * 1.03  # Rough growth estimate
    
    # Check Social Security impact
    baseline_ss = Microsimulation().calculate("social_security_tax", 2025).sum()
    reform_ss = Microsimulation(reform=reform).calculate("social_security_tax", 2025).sum()
    
    return {
        "ten_year_compliant": ten_year_impact <= 0,
        "long_term_concern": year_11_impact > 0,
        "affects_social_security": abs(reform_ss - baseline_ss) > 1e6
    }
```

## Committee Markup Support

### Amendment Analysis

Quickly analyze amendments during markup:

```python
class AmendmentAnalyzer:
    def __init__(self, base_bill_reform):
        self.base_bill = base_bill_reform
        self.baseline = Microsimulation()
        self.base_reformed = Microsimulation(reform=base_bill_reform)
    
    def analyze_amendment(self, amendment_reform):
        # Stack amendment on top of base bill
        def combined_reform(params):
            params = self.base_bill(params)
            params = amendment_reform(params)
            return params
        
        with_amendment = Microsimulation(reform=combined_reform)
        
        return {
            "revenue_impact": self.calculate_revenue_impact(with_amendment),
            "distributional_impact": self.calculate_distribution(with_amendment),
            "interaction_effects": self.calculate_interactions(with_amendment)
        }
```

### Real-Time Scoring

For committee markups requiring rapid analysis:

```python
@cache
def quick_score(reform_parameters):
    """Cached scoring for rapid iteration"""
    sim = Microsimulation(reform=reform_parameters)
    
    return {
        "fy_revenue": sim.calculate("income_tax_revenue", 2025).sum(),
        "10_year_revenue": quick_10_year_estimate(sim),
        "bottom_quintile_impact": calculate_quintile_impact(sim, 1),
        "middle_quintile_impact": calculate_quintile_impact(sim, 3)
    }
```

## Integration with Official Scores

### JCT Comparison

PolicyEngine estimates should be compared with Joint Committee on Taxation scores:

```python
def compare_with_jct(reform, jct_estimate):
    pe_estimate = calculate_revenue_impact(reform)
    
    difference = pe_estimate - jct_estimate
    percent_difference = difference / jct_estimate * 100
    
    print(f"PolicyEngine: ${pe_estimate/1e9:.1f}B")
    print(f"JCT: ${jct_estimate/1e9:.1f}B")
    print(f"Difference: {percent_difference:.1f}%")
    
    # Decompose differences
    behavioral_gap = estimate_behavioral_gap()
    data_gap = estimate_data_differences()
    methodology_gap = difference - behavioral_gap - data_gap
```

### CBO Baseline Alignment

Ensure consistency with CBO baseline projections:

```python
def align_with_cbo_baseline():
    # Load CBO projection parameters
    cbo_growth_rates = load_cbo_economic_projections()
    
    # Adjust PolicyEngine parameters
    for year in range(2025, 2035):
        inflation_factor = cbo_growth_rates["cpi"][year]
        wage_growth = cbo_growth_rates["wages"][year]
        
        # Update relevant parameters
        parameters.update_all(
            period=f"{year}-01-01",
            inflation_factor=inflation_factor,
            wage_growth=wage_growth
        )
```

## Best Practices

### 1. Documentation Standards

Every analysis should include:
- Assumptions and limitations
- Comparison to official scores
- Sensitivity analysis
- Data sources and vintage

### 2. Presentation Format

Follow congressional presentation standards:
- Tables in millions or billions
- Negative numbers for revenue losses
- Fiscal year basis
- 10-year totals

### 3. Modeling Choices

- Use CBO economic assumptions
- Apply JCT behavioral responses where available
- Document deviations from official methodology
- Include confidence intervals where appropriate

## Common Proposals

### Tax Credit Expansions

```python
# Example: Expand CTC with phase-out modification
def ctc_expansion(parameters):
    ctc = parameters.gov.irs.credits.ctc
    
    # Increase amount
    ctc.amount.update(3_600, "2025-01-01")
    
    # Modify phase-out
    ctc.phase_out.threshold.single.update(112_500, "2025-01-01")
    ctc.phase_out.threshold.joint.update(150_000, "2025-01-01")
    
    # Make fully refundable
    ctc.refundable.maximum.update(3_600, "2025-01-01")
    
    return parameters
```

### Rate Changes

```python
# Example: Add new tax bracket
def add_millionaire_bracket(parameters):
    rates = parameters.gov.irs.income.rates
    
    # Add 45% bracket above $1M
    rates.add_bracket(
        threshold=1_000_000,
        rate=0.45,
        period="2025-01-01"
    )
    
    return parameters
```

## Output Templates

### Summary Box
```
Revenue Impact: -$245.6 billion over 2025-2034
Families Receiving Tax Cut: 75.3 million (68%)
Average Tax Cut: $1,856
Bottom Quintile Average: $456
Middle Quintile Average: $1,234
Deficit Impact: +$245.6 billion (excluding behavioral responses)
```

### Key Takeaways
1. Primarily benefits middle-income families
2. 95% of benefits go to families earning under $200,000
3. Reduces child poverty by 2.1 percentage points
4. Increases labor force participation by 0.3%

## Quality Checklist

Before submitting analysis:
- [ ] Revenue estimates in correct fiscal year basis
- [ ] Distribution tables sum to 100%
- [ ] Comparison with similar historical proposals
- [ ] Behavioral responses documented
- [ ] Interaction with other provisions checked
- [ ] State tax implications noted
- [ ] Administrative costs considered
- [ ] Implementation timeline realistic