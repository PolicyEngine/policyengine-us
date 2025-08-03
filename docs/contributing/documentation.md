# Documentation Guidelines

Good documentation helps users understand PolicyEngine and contributors maintain it. This guide covers our documentation standards.

## Documentation Structure

```
docs/
├── index.md                 # Home page
├── policy/                  # Policy program documentation
│   ├── federal/            # Federal programs
│   ├── states/             # State programs
│   └── parameters/         # Auto-generated parameter docs
├── api/                    # Python API reference
├── contributing/           # Contributor guides (this section)
├── institutional/          # Guides for institutional users
└── _static/               # Images, custom CSS
```

## Types of Documentation

### 1. Code Documentation

#### Variable Documentation

Variables use metadata attributes, NOT docstrings:

```python
class snap_gross_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP gross income limit"
    unit = USD
    definition_period = MONTH
    documentation = """
    Maximum gross monthly income for SNAP categorical eligibility.
    
    Generally 130% of the Federal Poverty Level, but states with
    Broad-Based Categorical Eligibility (BBCE) may have higher limits.
    This variable accounts for state-specific BBCE policies.
    """
    reference = [
        "7 CFR 273.9(a) - Income eligibility standards",
        "https://www.fns.usda.gov/snap/broad-based-categorical-eligibility"
    ]
```

#### Comments

Use comments for complex logic:

```python
def formula(spm_unit, period, parameters):
    # Check categorical eligibility first (7 CFR 273.2(j)(2))
    if spm_unit("is_categorically_eligible", period):
        return float("inf")  # No gross income test
    
    # Standard gross income limit: 130% FPL (7 CFR 273.9(a)(1))
    fpl = spm_unit("federal_poverty_level", period)
    standard_limit = fpl * 1.3
    
    # Some states have higher limits under BBCE
    state = spm_unit.household("state_code", period)
    p = parameters(period).gov.states
    
    if hasattr(p, state.lower()):
        state_params = getattr(p, state.lower())
        if hasattr(state_params, "snap") and hasattr(state_params.snap, "bbce_gross_income_limit"):
            return state_params.snap.bbce_gross_income_limit
    
    return standard_limit
```

### 2. Policy Documentation

Located in `docs/policy/`, these explain programs for institutional users:

```markdown
# Supplemental Nutrition Assistance Program (SNAP)

## Overview

The Supplemental Nutrition Assistance Program (SNAP) provides nutrition
assistance to low-income individuals and families. Formerly known as
food stamps, SNAP is the largest federal nutrition assistance program.

## Eligibility

### Income Tests

SNAP uses two income tests:

1. **Gross Income Test**: Monthly gross income must be at or below 130%
   of the poverty line
2. **Net Income Test**: Monthly net income must be at or below 100%
   of the poverty line

States with Broad-Based Categorical Eligibility (BBCE) may waive
the gross income test.

### Asset Tests

Standard asset limits (may be waived under BBCE):
- $2,750 for most households
- $4,250 for households with elderly/disabled members

### Work Requirements

Able-bodied adults without dependents (ABAWDs) ages 18-49 must:
- Work at least 20 hours per week, or
- Participate in qualifying education/training

## Benefit Calculation

Benefits are based on the Thrifty Food Plan (TFP) minus 30% of
net income:

```
Benefit = Max TFP - (0.30 × Net Income)
```

### Deductions

From gross income to get net income:
- 20% earned income deduction
- Standard deduction (varies by household size)
- Dependent care costs
- Medical expenses (elderly/disabled)
- Excess shelter costs

## State Variations

While SNAP is federally funded, states have flexibility in:
- BBCE implementation
- Utility allowance standards
- Simplified reporting requirements
- Student eligibility rules

## Legislative History

- 1964: Food Stamp Act establishes permanent program
- 1977: Nationwide implementation
- 2008: Renamed to SNAP
- 2020: COVID-19 emergency allotments

## References

- [7 CFR Part 273](https://www.ecfr.gov/current/title-7/part-273)
- [USDA SNAP Policy](https://www.fns.usda.gov/snap)
```

### 3. API Documentation

Document all public APIs:

```python
class Microsimulation:
    """PolicyEngine US microsimulation interface.
    
    Provides methods to calculate taxes and benefits for the US
    population using enhanced CPS microdata.
    
    Args:
        reform: Optional reform function to modify parameters
        dataset: Dataset name (default: "enhanced_cps_2024")
        
    Examples:
        Basic usage:
        >>> sim = Microsimulation()
        >>> income_tax = sim.calculate("income_tax", 2024)
        
        With reform:
        >>> def reform(parameters):
        ...     parameters.gov.irs.credits.ctc.amount.update(3000, "2024-01-01")
        ...     return parameters
        >>> sim = Microsimulation(reform=reform)
    """
    
    def calculate(
        self,
        variable: str,
        period: int,
        map_to: str = None
    ) -> pd.Series:
        """Calculate a variable for all entities.
        
        Args:
            variable: Name of variable to calculate
            period: Year to calculate for
            map_to: Entity level to map results to
            
        Returns:
            Series with calculated values, indexed by entity ID
            
        Raises:
            VariableNotFound: If variable doesn't exist
            InvalidPeriod: If period is invalid for variable
        """
```

### 4. User Guides

Create task-focused guides:

```markdown
# Calculating Effective Tax Rates

This guide shows how to calculate average and marginal tax rates
using PolicyEngine US.

## Average Effective Tax Rate

The average effective tax rate (AETR) is total tax divided by income:

```python
from policyengine_us import Microsimulation

sim = Microsimulation()

# Calculate components
income = sim.calculate("adjusted_gross_income", 2024)
tax = sim.calculate("income_tax", 2024)

# Calculate AETR
aetr = tax / income
aetr = aetr.fillna(0)  # Handle zero income

# Get summary statistics
print(f"Mean AETR: {aetr.mean():.1%}")
print(f"Median AETR: {aetr.median():.1%}")
```

## Writing Style

### Clarity

Write for your audience:
- **Code docs**: Technical, precise
- **Policy docs**: Clear, accessible to non-engineers
- **User guides**: Task-focused, example-driven

### Consistency

- Use American English spelling
- Write in present tense
- Use active voice
- Define acronyms on first use

### Examples

Always include examples in documentation:

```python
# Good - Variable with clear documentation
class child_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child Tax Credit"
    unit = USD
    documentation = """
    The Child Tax Credit reduces tax liability for families with
    qualifying children. For 2024, the credit is $2,000 per child
    under 17, with phase-outs based on income.
    """
    reference = "https://www.irs.gov/credits-deductions/child-tax-credit"

# Bad - Minimal documentation
class child_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC"  # Unclear acronym
    # No documentation or reference
```

## Jupyter Book Features

### Cross-references

Link between pages:

```markdown
See the {doc}`/policy/federal/taxation/credits/eitc` documentation
for more details on EITC calculation.

The {func}`~policyengine_us.variables.gov.irs.income.taxable_income.taxable_income`
variable implements this calculation.
```

### Math

Use LaTeX for formulas:

```markdown
The phase-out is calculated as:

$$
\text{Phase-out} = \max(0, \text{Income} - \text{Threshold}) \times \text{Rate}
$$
```

### Admonitions

Highlight important information:

```markdown
```{note}
State-specific rules may override federal parameters.
```

```{warning}
This calculation assumes 2024 parameters. Always verify
current law before policy analysis.
```

```{tip}
Use `period.this_year` when accessing yearly variables
from monthly calculations.
```
```

### Code Tabs

Show examples in multiple formats:

````markdown
```{tab-set}
```{tab-item} Python
:sync: python

```python
sim = Microsimulation()
eitc = sim.calculate("earned_income_tax_credit", 2024)
```

```{tab-item} YAML Test
:sync: yaml

```yaml
- name: EITC calculation
  period: 2024
  input:
    employment_income: 15_000
  output:
    earned_income_tax_credit: 3_584
```
```
````

## Building Documentation

### Local Build

```bash
# Build HTML documentation
make documentation

# Opens in browser
open docs/_build/html/index.html

# Clean and rebuild
cd docs
jupyter-book clean .
jupyter-book build .
```

### Auto-generated Content

Some documentation is generated automatically:

```bash
# Generate parameter documentation
python docs/scripts/generate_parameter_docs.py

# Generate variable reference
python docs/scripts/generate_variable_docs.py
```

### CI/CD

Documentation builds automatically on:
- Every PR (preview deployment)
- Merge to master (production deployment)

## Documentation Checklist

When adding new features:

- [ ] Add docstrings to all public functions
- [ ] Include `documentation` attribute in variables
- [ ] Add `reference` links to authoritative sources
- [ ] Create/update relevant policy documentation
- [ ] Add examples to user guides
- [ ] Update API reference if needed
- [ ] Test documentation builds locally
- [ ] Check all links work

## Common Issues

### Broken References

```markdown
# Wrong - Undefined reference
See {doc}`nonexistent-page`

# Right - Valid path
See {doc}`/policy/federal/transfers/snap`
```

### Missing Dependencies

If build fails:
```bash
# Install documentation dependencies
pip install -e ".[dev]"
```

### Large Files

Keep documentation lightweight:
- Compress images
- Use external links for large datasets
- Avoid embedding large code blocks

## Getting Help

- Check existing documentation for patterns
- Review Jupyter Book documentation
- Ask in GitHub issues
- Tag documentation PRs for review