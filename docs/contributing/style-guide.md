# Style Guide

This guide ensures consistency across the PolicyEngine US codebase. Following these conventions makes code easier to read, review, and maintain.

## Python Style

### Code Formatting

We use **Black** with a line length of 79 characters and **linecheck** for import organization:

```bash
# Always use make format - it runs both black and linecheck
make format
```

**Never run `black` directly** - always use `make format` as it also runs `linecheck` to fix import ordering.

**All code must be formatted before committing.** CI will fail if code isn't properly formatted.

### Import Organization

Imports are automatically organized by `linecheck` (part of `make format`):

```python
# Standard library
import os
from pathlib import Path

# Third-party
import numpy as np
import pandas as pd

# PolicyEngine
from policyengine_core.variables import Variable

# Local
from policyengine_us.model_api import *
```

### Variable Definitions

Variables follow a specific pattern based on the actual codebase:

```python
from policyengine_us.model_api import *


class eitc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Federal earned income credit"
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
    unit = USD
    defined_for = "eitc_eligible"

    def formula(tax_unit, period, parameters):
        takes_up_eitc = tax_unit("takes_up_eitc", period)
        maximum = tax_unit("eitc_maximum", period)
        phased_in = tax_unit("eitc_phased_in", period)
        reduction = tax_unit("eitc_reduction", period)
        limitation = max_(0, maximum - reduction)
        return min_(phased_in, limitation) * takes_up_eitc
```

Note: Variables do NOT use docstrings. Instead, they use metadata attributes:
- `label`: Human-readable name
- `documentation`: (optional) Extended description for complex logic
- `reference`: URL(s) to authoritative sources
- `defined_for`: (optional) Condition when variable applies

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `adjusted_gross_income` |
| Parameters | snake_case | `standard_deduction` |
| Classes | PascalCase | `TaxUnit` |
| Constants | UPPER_CASE | `MONTHS_IN_YEAR = 12` |
| Files | snake_case | `income_tax.py` |

### Type Hints

Use type hints for better IDE support and clarity:

```python
from typing import Dict, List, Optional
from numpy.typing import ArrayLike


def calculate_phase_out(
    income: ArrayLike,
    threshold: float,
    rate: float,
    max_amount: Optional[float] = None
) -> ArrayLike:
    """Calculate benefit phase-out.
    
    Args:
        income: Household income array
        threshold: Phase-out start threshold  
        rate: Phase-out rate (e.g., 0.05 for 5%)
        max_amount: Maximum phase-out amount
        
    Returns:
        Phase-out amounts
    """
    phase_out = np.maximum(income - threshold, 0) * rate
    if max_amount is not None:
        phase_out = np.minimum(phase_out, max_amount)
    return phase_out
```

### Vectorization

Always use vectorized operations for calculations:

```python
# Good - Vectorized with parameters
def formula(person, period, parameters):
    p = parameters(period).gov.irs.deductions.standard
    age = person("age", period)
    filing_status = person.tax_unit("filing_status", period)
    
    # Get base amounts from parameters
    base_amount = p.amount[filing_status]
    additional = p.aged_or_blind_additional[filing_status]
    
    # Apply additional amount for 65+
    is_elderly = age >= p.aged_or_blind_age_threshold
    return base_amount + where(is_elderly, additional, 0)

# Bad - Not vectorized and hardcoded values
def formula(person, period, parameters):
    age = person("age", period)
    if age >= 65:  # This breaks with arrays!
        return 1_600  # Hardcoded value!
    return 1_300  # Hardcoded value!
```

Common vectorized patterns:

- Use `where` not `if`
- Use `select` for multiple conditions
- Use `max_` and `min_` not `max` and `min`
- Use `&` and `|` not `and` and `or`

### Parameter Access

Follow these parameter conventions:

```python
# Good - Using parameters properly
def formula(tax_unit, period, parameters):
    # Use 'p' for the minimally relevant parameter subtree
    p = parameters(period).gov.irs.credits.ctc
    
    income = tax_unit("adjusted_gross_income", period)
    filing_status = tax_unit("filing_status", period)
    
    # Use parameters directly in logic - don't rename
    base_amount = p.amount * tax_unit("ctc_qualifying_children", period)
    
    # Phase-out calculation
    threshold = p.phase_out.threshold[filing_status]
    excess = max_(income - threshold, 0)
    phase_out = excess * p.phase_out.rate
    
    return max_(base_amount - phase_out, 0)

# Bad - Multiple issues
def formula(tax_unit, period, parameters):
    # Don't hardcode policy values!
    amount = 2_000  # NEVER do this
    
    # Don't rename parameters unnecessarily
    p = parameters(period).gov.irs.credits.ctc
    credit_amount = p.amount  # Unnecessary renaming
    
    # Don't use long parameter paths repeatedly
    threshold = parameters(period).gov.irs.credits.ctc.phase_out.threshold.single
```

**Key principles**:
- **Never hardcode policy values** - All amounts, rates, thresholds must be parameters
- **Use `p` convention** - For the minimally relevant parameter subtree
- **Don't rename parameters** - Use them directly to show they're parameters
- **Primary sources required** - All parameters must cite statutes, regulations, or tax forms

### Handling Division by Zero

When formulas calculate rates, ratios, or fractions that could divide by zero, use the mask approach:

```python
# Good - Mask approach (no warnings)
def formula(tax_unit, period, parameters):
    income = tax_unit("adjusted_gross_income", period)
    tax = tax_unit("income_tax", period)
    
    # Create result array and mask
    effective_rate = np.zeros_like(income)
    mask = income != 0
    
    # Only divide where mask is True
    effective_rate[mask] = tax[mask] / income[mask]
    
    return effective_rate

# Bad - where evaluates division before choosing (causes warning)
def formula(tax_unit, period, parameters):
    return where(
        income > 0,
        tax / income,  # Division happens for ALL values!
        0
    )
```

Common cases requiring this pattern:

- Effective tax rates (tax / income)
- Benefit phase-out rates
- Income-to-poverty ratios
- Housing cost burden (rent / income)
- Any percentage or ratio calculation

## YAML Style

### Parameter Files

Parameters must cite primary sources and include all metadata:

```yaml
description: Child Tax Credit maximum amount per qualifying child
metadata:
  label: CTC amount
  unit: USD
  period: year
  reference:
    # Primary source required - statute, regulation, or tax form
    - title: 26 U.S. Code § 24(h)(2)
      href: https://www.law.cornell.edu/uscode/text/26/24
    - title: IRS Form 1040 Instructions (2024)
      href: https://www.irs.gov/pub/irs-pdf/i1040.pdf
values:
  2024-01-01: 2_000
  2022-01-01: 2_000
  2021-01-01: 3_600  # ARPA temporary increase per § 9611
  2020-01-01: 2_000
```

**Parameter requirements**:

- **Primary sources only** - Cite specific statute sections, CFR regulations, or official tax forms
- **Never use secondary sources** - No news articles, Wikipedia, or calculators
- **Specific citations** - Include section numbers (e.g., "§ 24(h)(2)" not just "§ 24")
- **Multiple sources encouraged** - Include both statute and implementing forms/instructions

### Test Files

```yaml
- name: Single parent with two children
  period: 2024
  input:
    people:
      parent:
        age: 35
        employment_income: 50_000
      child1:
        age: 10
      child2:
        age: 14
    tax_units:
      tax_unit:
        members: [parent, child1, child2]
        filing_status: HEAD_OF_HOUSEHOLD
  output:
    ctc: 4_000  # $2,000 × 2 children
```

## Documentation

### Docstrings for Functions

Use Google-style docstrings for regular Python functions (but NOT for Variable classes):

```python
def calculate_phase_out_rate(
    income: ArrayLike,
    threshold: ArrayLike,
    rate: float
) -> ArrayLike:
    """Calculate phase-out amount for a benefit.
    
    All array inputs must be the same shape for vectorized computation.
    
    Args:
        income: Income array 
        threshold: Phase-out threshold array (may vary by filing status)
        rate: Phase-out rate (e.g., 0.05 for 5%)
        
    Returns:
        Phase-out amount array
    """
    excess = max_(income - threshold, 0)
    return excess * rate
```

### Variable Documentation

Every variable should include:

- Clear `label`
- `documentation` for complex logic
- `reference` with authoritative sources

```python
class alternative_minimum_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alternative Minimum Tax"
    unit = USD
    definition_period = YEAR
    documentation = """
    Alternative Minimum Tax (AMT) ensures taxpayers pay a minimum
    amount of tax by adding back certain deductions and applying
    a flatter rate structure.
    """
    reference = [
        "https://www.irs.gov/forms-pubs/about-form-6251",
        "26 U.S. Code § 55"
    ]
```

## Comments

### When to Comment

Comment:

- Complex algorithms
- Non-obvious business logic
- Legislative references
- Workarounds or special cases

```python
def formula(tax_unit, period, parameters):
    # IRC Section 24(h)(4) - special rule for 2021
    # The CTC was temporarily fully refundable for 2021 only
    if period.start.year == 2021:
        return tax_unit("ctc_maximum", period)
    
    # Normal refundability rules apply for other years
    # Limited to $1,400 per child (2022-2025)
    # See IRC Section 24(h)(5)(A)
    return min_(
        tax_unit("ctc_maximum", period),
        tax_unit("ctc_refundable_maximum", period)
    )
```

### Legislative Citations

Always cite specific sections:

```python
# Good - Specific citation
# IRC Section 32(c)(1)(A) - earned income definition

# Bad - Vague reference  
# Based on tax law
```

## Common Patterns

### Income Aggregation

Use the `add` function for combining income:

```python
# Good
total_income = add(person, period, [
    "wages",
    "self_employment_income", 
    "interest_income",
    "dividend_income"
])

# Less clear
total_income = (
    person("wages", period) +
    person("self_employment_income", period) +
    person("interest_income", period) +
    person("dividend_income", period)
)
```

### Categorical Logic

For multiple categories:

```python
# Good - Using select
filing_status = tax_unit("filing_status", period)
amount = select(
    [
        filing_status == filing_status.possible_values.SINGLE,
        filing_status == filing_status.possible_values.JOINT,
        filing_status == filing_status.possible_values.HEAD_OF_HOUSEHOLD,
    ],
    [
        12_950,  # Single
        25_900,  # Joint
        19_400,  # Head of household
    ],
    default=12_950  # Separate filers
)

# Bad - Nested where statements
amount = where(
    filing_status == filing_status.possible_values.SINGLE,
    12_950,
    where(
        filing_status == filing_status.possible_values.JOINT,
        25_900,
        # ... more nesting
    )
)
```

### Phase-outs

Standard pattern for benefit phase-outs:

```python
def calculate_phase_out(tax_unit, period, parameters):
    p = parameters(period).gov.program.phase_out
    income = tax_unit("adjusted_gross_income", period)
    filing_status = tax_unit("filing_status", period)
    
    # Get threshold based on filing status
    threshold = p.threshold[filing_status]
    
    # Calculate phase-out
    excess = max_(income - threshold, 0)
    phase_out_amount = excess * p.rate
    
    # Cap at maximum benefit
    max_benefit = tax_unit("benefit_before_phase_out", period)
    return min_(phase_out_amount, max_benefit)
```

## File Organization

```text
policyengine_us/
├── parameters/
│   └── gov/
│       ├── irs/           # Federal tax parameters
│       ├── ssa/           # Social Security
│       ├── hud/           # Housing
│       └── states/        # State-specific
│           └── ny/
│               └── tax/
├── variables/
│   └── gov/               # Same structure as parameters
└── tests/
    └── policy/
        └── baseline/      # Same structure for tests
```

## Commit Messages

Follow conventional commits:

```text
type(scope): subject

body

footer
```

Examples:

```text
feat(irs): Add AMT exemption phase-out

Implement Alternative Minimum Tax exemption phase-out based on
income levels. Phase-out rates differ by filing status.

References: 26 U.S. Code § 55(d)(3)
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

## Pre-commit Checklist

Before committing:

- [ ] Run `make format` (not `black` directly!)
- [ ] Run `make test`
- [ ] Add/update tests
- [ ] Include references
- [ ] Update changelog
- [ ] Check variable naming
