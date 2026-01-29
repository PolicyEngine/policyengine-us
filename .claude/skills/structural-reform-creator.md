---
name: structural-reform-creator
description: Creates structural reforms for proposed legislation in PolicyEngine-US - reforms with toggleable in_effect parameters that can be modeled on policyengine.org
---

# Structural Reform Creator Guide

This skill documents how to create structural reforms for proposed legislation in PolicyEngine-US. Structural reforms allow users to toggle policy changes on/off using an `in_effect` parameter, enabling what-if analysis on policyengine.org.

## When to Use Structural Reforms

Use structural reforms when:
- Implementing proposed legislation (bills not yet enacted)
- Creating alternative policy scenarios for analysis
- Building reforms that need to be toggled on/off via the API

Do NOT use structural reforms for:
- Current law implementations (use standard variables/parameters)
- Simple parameter changes (use direct reform overrides)

## Directory Structure

```
policyengine_us/
├── parameters/gov/contrib/states/{state}/{bill}/
│   ├── in_effect.yaml           # Toggle parameter (REQUIRED)
│   ├── {parameter1}.yaml        # Policy parameters
│   └── {subdirectory}/          # Nested parameters if needed
│       └── {parameter2}.yaml
├── reforms/states/{state}/{bill}/
│   ├── __init__.py              # Exports the reform
│   └── {bill}_reform.py         # Reform class definition
└── tests/policy/contrib/states/{state}/{bill}/
    └── {bill}_reform.yaml       # YAML test file
```

## Step 1: Create Parameters

### in_effect.yaml (REQUIRED)
```yaml
description: {State} {Bill} {short description} applies if this is true. {More detail about what the bill does}.
metadata:
  unit: bool
  period: year
  label: {State} {Bill} in effect
  reference:
    - title: {Full bill title and session}
      href: {URL to official bill text}
values:
  0000-01-01: false  # Default to false - reform only applies when explicitly enabled
```

### Policy Parameter Example
```yaml
description: {State} {Bill} {parameter description}. The bill {changes X from Y to Z}.
metadata:
  unit: currency-USD  # or /1 for rates, bool for booleans
  period: year
  label: {State} {Bill} {short label}
  breakdown:  # Only if parameter varies by filing_status, etc.
    - filing_status
  reference:
    - title: {Bill section reference}
      href: {URL}
    - title: {Relevant law citation}
      href: {URL}
{FILING_STATUS}:  # If using breakdown
  values:
    {effective-date}: {value}
# OR without breakdown:
values:
  {effective-date}: {value}
```

## Step 2: Create Reform Class

### reforms/states/{state}/{bill}/__init__.py
```python
from policyengine_us.reforms.states.{state}.{bill}.{bill}_reform import (
    {bill}_reform,
)

__all__ = ["{bill}_reform"]
```

### reforms/states/{state}/{bill}/{bill}_reform.py
```python
from policyengine_us.model_api import *


def create_{bill}_reform() -> Reform:
    """
    {State} {Bill Number} - {Short Title}

    This bill {description of what the bill does}:
    1. {First change}
    2. {Second change}

    Reference: {URL to bill}
    """

    # Override variables that need to change
    class {variable_name}(Variable):
        value_type = float
        entity = TaxUnit  # or SPMUnit, Person, etc.
        label = "{Label}"
        unit = USD
        definition_period = YEAR
        reference = "{URL}"
        defined_for = StateCode.{STATE}

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.{state}.{bill}
            in_effect = p.in_effect

            # Get baseline values
            baseline = parameters(period).gov.states.{state}.{program}

            # Use where() to conditionally apply reform
            reform_value = p.{parameter}
            baseline_value = baseline.{parameter}

            result = where(in_effect, reform_value, baseline_value)
            return result

    class reform(Reform):
        def apply(self):
            self.update_variable({variable_name})
            # Add more update_variable() calls as needed

    return reform


def create_{bill}_reform_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_{bill}_reform()

    p = parameters(period).gov.contrib.states.{state}.{bill}

    if p.in_effect:
        return create_{bill}_reform()
    else:
        return None


{bill}_reform = create_{bill}_reform_reform(
    None, None, bypass=True
)
```

### reforms/states/{state}/__init__.py
```python
from policyengine_us.reforms.states.{state}.{bill} import {bill}_reform

__all__ = ["{bill}_reform"]
```

## Step 3: Create Tests

### tests/policy/contrib/states/{state}/{bill}/{bill}_reform.yaml
```yaml
# {State} {Bill} {Description} Tests
# Tests {what the reform changes}

- name: {Bill} {test description}
  period: {year}
  reforms: policyengine_us.reforms.states.{state}.{bill}.{bill}_reform.{bill}_reform
  input:
    gov.contrib.states.{state}.{bill}.in_effect: true
    people:
      person:
        age: {value}
        {other_inputs}: {value}
        is_tax_unit_head: true
    tax_units:
      tax_unit:
        members: [person]
        filing_status: {FILING_STATUS}
    households:
      household:
        members: [person]
        state_code: {STATE}
  output:
    {variable_to_test}: {expected_value}

- name: {Bill} not in effect - uses current law
  period: {year}
  reforms: policyengine_us.reforms.states.{state}.{bill}.{bill}_reform.{bill}_reform
  input:
    gov.contrib.states.{state}.{bill}.in_effect: false
    # ... same structure as above
  output:
    # Baseline/current law values
    {variable_to_test}: {baseline_value}
```

## Step 4: Run Tests

```bash
# Run the YAML tests
python -m policyengine_core.scripts.policyengine_command test \
  policyengine_us/tests/policy/contrib/states/{state}/{bill}/{bill}_reform.yaml
```

## Key Patterns

### Pattern 1: Conditional Value Selection
Use `where()` to select between reform and baseline values:
```python
part_b_rate = where(in_effect, p.part_b_rate, rates.part_b)
```

### Pattern 2: Filing Status Lookup
Access parameters by filing status:
```python
filing_status = tax_unit("filing_status", period)
personal_exemption = p.exemptions.personal[filing_status]
```

### Pattern 3: Complete Variable Override
When the reform completely changes a variable's logic, override the entire formula:
```python
class ma_income_tax_before_credits(Variable):
    # ... metadata ...

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.states.ma.h3262
        in_effect = p.in_effect

        # Full calculation with conditional logic
        part_b_rate = where(in_effect, p.part_b_rate, rates.part_b)
        # ... rest of formula
```

## Real Example: MA H3262

See the complete implementation:
- Parameters: `parameters/gov/contrib/states/ma/h3262/`
- Reform: `reforms/states/ma/h3262/ma_h3262_income_tax_reform.py`
- Tests: `tests/policy/contrib/states/ma/h3262/ma_h3262_income_tax_reform.yaml`

This reform:
1. Increases MA Part B tax rate from 5% to 6%
2. Increases personal exemptions by ~50%
3. Uses `in_effect` parameter to toggle between reform and baseline

## Checklist

Before submitting PR:
- [ ] `in_effect.yaml` defaults to `false`
- [ ] All parameters have proper metadata (unit, period, label, reference)
- [ ] Reform uses `where()` for conditional application
- [ ] Tests cover all filing statuses affected
- [ ] Tests verify baseline values when `in_effect: false`
- [ ] All YAML tests pass
- [ ] No hard-coded values in reform logic
