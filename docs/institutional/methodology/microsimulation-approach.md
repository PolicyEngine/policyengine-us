# Microsimulation Methodology

## Overview

PolicyEngine US employs a static microsimulation approach to model the U.S. tax and benefit system. This methodology allows for detailed analysis of policy impacts on individual households while maintaining computational tractability for real-time calculations.

## Model Architecture

### Static vs. Dynamic Microsimulation

PolicyEngine US is primarily a **static microsimulation model**, meaning:

1. **No Behavioral Responses**: Labor supply, savings, and consumption patterns are held constant
2. **Arithmetic Calculations**: Tax and benefit amounts calculated based on current rules
3. **Cross-Sectional Analysis**: Point-in-time calculations rather than lifecycle modeling
4. **Immediate Implementation**: Policy changes take effect instantaneously

However, the model includes optional behavioral response modules for:
- Labor supply elasticity adjustments
- Capital gains realization responses

### Entity Hierarchy

The model uses a hierarchical entity structure reflecting real-world relationships:

```
Household (Geographic unit)
├── Tax Units (Tax filing groups)
│   ├── Head
│   ├── Spouse (if applicable)
│   └── Dependents
├── SPM Units (Resource sharing groups)
│   └── All household members
└── People (Individuals)
    └── Demographic and income attributes
```

## Data Foundation

### Primary Data Source: Current Population Survey (CPS)

**Annual Social and Economic Supplement (ASEC)**
- Sample size: ~98,000 households
- Coverage: Civilian non-institutional population
- Key variables: Demographics, income, employment, health insurance
- Reference period: Prior calendar year

**Enhancements Applied**:
1. **Tax imputation**: Using NBER TAXSIM and IRS SOI
2. **Benefit underreporting correction**: SNAP, TANF, SSI
3. **Geographic coding**: County and sub-state regions
4. **Wealth imputation**: From Survey of Consumer Finances

### Weighting and Representation

**Survey Weights**:
- Person-level weights sum to U.S. population
- Household weights adjusted for complex survey design
- Post-stratification to Census population controls

**Reweighting for Policy Analysis**:
```python
# Differential weighting by income/demographics
# Preserves population totals while targeting subgroups
weights = calibrate_weights(
    original_weights,
    targets={
        "population": census_totals,
        "income_distribution": soi_aggregates,
        "program_participation": admin_counts
    }
)
```

## Calculation Engine

### Variable Dependencies

Variables are calculated through a directed acyclic graph (DAG) of dependencies:

```
employment_income → earned_income → agi → taxable_income → income_tax
                 ↘                    ↗
                  self_employment_income
```

### Calculation Process

1. **Input Variables**: Set from survey data or user input
2. **Formula Variables**: Calculated based on dependencies
3. **Parameter Lookup**: Legislative values for specific time periods
4. **Vectorized Operations**: NumPy arrays for population calculations

Example calculation flow:
```python
def calculate_eitc(person, period, parameters):
    # Get dependencies
    earned_income = person("earned_income", period)
    investment_income = person("investment_income", period)
    num_children = person.tax_unit("eitc_qualifying_children", period)
    
    # Apply eligibility rules
    eligible = investment_income <= parameters.eitc.investment_limit
    
    # Calculate credit amount
    phase_in_rate = parameters.eitc.phase_in_rate[num_children]
    max_credit = parameters.eitc.maximum[num_children]
    
    # Vectorized calculation for all persons
    return where(eligible, 
                 min_(earned_income * phase_in_rate, max_credit), 
                 0)
```

## Quality Assurance

### Validation Against External Sources

**Aggregate Validation**:
- IRS Statistics of Income: Tax revenue and credits
- SSA/CMS administrative data: Benefit enrollment
- USDA Food and Nutrition Service: SNAP participation
- State revenue departments: State tax collections

**Microsimulation Comparisons**:
- NBER TAXSIM: Individual tax calculations
- Tax Policy Center: Distributional tables
- Congressional Budget Office: Baseline projections

### Margin of Error

Sources of uncertainty:
1. **Survey Sampling Error**: CPS standard errors
2. **Imputation Error**: Missing data procedures
3. **Model Specification**: Simplifying assumptions
4. **Parameter Uncertainty**: Legislative interpretation

Typical confidence intervals:
- Tax liability: ±2-3% at aggregate level
- Benefit amounts: ±5-7% for major programs
- Distributional statistics: ±1-2 percentage points

## Time Period Handling

### Historical Accuracy
- Parameters traced to original legislation
- Annual values from authoritative sources
- Inflation adjustments using specified indices

### Current Law Baseline
- Scheduled changes under existing law
- Sunset provisions (e.g., TCJA in 2025)
- Inflation indexing projections

### Reform Modeling
- Immediate implementation assumed
- No transition rules unless specified
- Full-year effects calculated

## Distributional Analysis

### Income Concepts

**Household Income**: Comprehensive income measure including:
- Market income (wages, business, capital)
- Transfer income (Social Security, UI, benefits)
- Less: Federal and state taxes
- Plus: Tax credits (including refundable)

**Equivalization**: Adjust for household size using square root scale

### Distribution Metrics

**Income Percentiles**: Weighted percentiles of household income
**Poverty Measures**: 
- Official Poverty Measure (OPM)
- Supplemental Poverty Measure (SPM)

**Inequality Indices**:
- Gini coefficient
- 90/10 ratio
- Top income shares

## Behavioral Responses (Optional Module)

### Labor Supply Elasticities

Based on empirical literature:
- **Extensive Margin**: Participation elasticity = 0.25
- **Intensive Margin**: Hours elasticity = 0.1
- **Income Effects**: -0.05 to -0.1

Implementation:
```python
def adjust_labor_supply(original_income, mtr_change):
    elasticity = 0.1  # Intensive margin
    return original_income * (1 + elasticity * mtr_change)
```

### Capital Gains Realization

Elasticity with respect to tax rate: -0.7
```python
realizations_new = realizations_old * (
    (1 - rate_new) / (1 - rate_old)
) ** 0.7
```

## Limitations and Caveats

### Model Limitations

1. **Static Nature**: No macroeconomic feedback effects
2. **Perfect Take-Up**: Assumes full benefit participation unless specified
3. **Compliance**: Assumes full tax compliance
4. **Household Formation**: Fixed household structures
5. **Geography**: Limited sub-state variation

### Data Limitations

1. **Top-Coding**: High incomes censored in public data
2. **Underreporting**: Some income sources systematically underreported
3. **Item Non-Response**: Imputation for missing values
4. **Sample Size**: Small samples for some subpopulations

### Appropriate Uses

**Well-Suited For**:
- First-order revenue estimates
- Distributional analysis
- Household impact examples
- Cross-program interactions
- State policy comparisons

**Less Suited For**:
- Long-term dynamic effects
- Macroeconomic impacts
- Behavioral response precision
- Small area estimates
- Employer responses

## Technical Implementation

### Performance Optimization

- **Vectorization**: NumPy array operations
- **Caching**: Computed values stored
- **Lazy Evaluation**: Calculate only requested variables
- **Parallelization**: Multi-core processing for large runs

### Reproducibility

- **Version Control**: Git-tracked parameters
- **Random Seeds**: Consistent sampling
- **Docker Containers**: Reproducible environments
- **Testing Suite**: Validation against known cases

## Citations and References

### Core Methodology
```
Immervoll, H., & O'Donoghue, C. (2009). 
"What drives tax and benefit reforms? A microsimulation analysis."
In Lelkes & Sutherland (eds), Tax and Benefit Policies in the EU.

Bourguignon, F., & Spadaro, A. (2006).
"Microsimulation as a tool for evaluating redistribution policies."
Journal of Economic Inequality, 4(1), 77-106.
```

### US Applications
```
Bakija, J., & Gentry, W. (2014).
"Capital gains taxes and realizations: Evidence from a long panel."
National Tax Journal, 67(2), 431-457.

CBO (2024). "The Distribution of Household Income, 2021."
Congressional Budget Office.
```