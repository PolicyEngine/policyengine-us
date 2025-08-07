# Testing Guidelines

Comprehensive testing ensures PolicyEngine US produces accurate results. This guide covers our testing approach and best practices.

> **Note**: PolicyEngine US is built on top of PolicyEngine Core. For detailed documentation on the testing framework, calculation methods (`calc` vs `calculate`), and simulation APIs, see the [PolicyEngine Core documentation](https://github.com/PolicyEngine/policyengine-core).

## Test-Driven Development (TDD)

We follow TDD principles:
1. **Write tests first** - Define expected behavior
2. **Run tests** - See them fail
3. **Implement code** - Make tests pass
4. **Refactor** - Improve code while tests still pass

## Types of Tests

### Unit Tests

Test individual variables in isolation:

```yaml
# policyengine_us/tests/policy/baseline/gov/irs/credits/ctc/test_ctc_phase_out.yaml
- name: CTC phase-out for single filer
  period: 2024
  input:
    filing_status: SINGLE
    adjusted_gross_income: 220_000
    ctc_maximum: 2_000
  output:
    ctc_phase_out: 1_000  # ($220k - $200k) * 0.05
```

### Integration Tests

Test complete calculation chains:

```yaml
# policyengine_us/tests/policy/baseline/integration/test_family_benefits.yaml
- name: Family with children receiving multiple benefits
  period: 2024
  input:
    people:
      parent:
        age: 35
        employment_income: 25_000
      child1:
        age: 8
      child2:
        age: 12
    tax_units:
      tax_unit:
        members: [parent, child1, child2]
        filing_status: HEAD_OF_HOUSEHOLD
    families:
      family:
        members: [parent, child1, child2]
    households:
      household:
        members: [parent, child1, child2]
        state_code: NY
  output:
    # Test the full benefit calculation
    household_net_income: 35_850
    snap: 4_800
    eitc: 5_450
    ctc: 4_000
```

### Microsimulation Tests

Test against real survey data:

```python
# policyengine_us/tests/microsimulation/test_poverty_rates.py
def test_poverty_rate_reasonable():
    """Ensure poverty rate is within expected bounds"""
    sim = Microsimulation()
    poverty = sim.calc("in_poverty", period=2024)
    weights = sim.calc("person_weight", period=2024)
    
    poverty_rate = poverty.sum() / weights.sum()
    
    # Poverty rate should be between 8% and 15%
    assert 0.08 <= poverty_rate <= 0.15
```

## Writing Effective Tests

### YAML Test Structure

```yaml
# Required fields
- name: Descriptive test name  # Clear description of what's being tested
  period: 2024                  # Tax year (not "2024-01")
  
  # Input section
  input:
    # For simple person-level tests
    age: 65
    employment_income: 50_000
    
    # For household tests with multiple people
    people:
      person1:
        age: 35
      person2:
        age: 33
    tax_units:
      tax_unit:
        members: [person1, person2]
    
  # Output section - what we expect
  output:
    income_tax: 6_250
    # Can test multiple outputs
    standard_deduction: 13_850
    taxable_income: 36_150
```

### Test Naming Conventions

File names should match the variable being tested:
- `ctc.yaml` tests `ctc.py`
- `ny_income_tax.yaml` tests `ny_income_tax.py`
- Use `integration.yaml` for multi-variable tests

### Numeric Formatting

**Always use underscores for readability**:
```yaml
# Good
income: 50_000
tax: 6_250

# Bad
income: 50000
tax: 6250
```

### Edge Cases to Test

Always test:
1. **Zero values** - No income, no children
2. **Boundary values** - Right at phase-out thresholds
3. **Maximum values** - High incomes, benefit caps
4. **Different filing statuses** - Single, joint, head of household
5. **Different states** - State-specific rules
6. **Different years** - Parameter changes over time

Example edge case tests:
```yaml
- name: Zero income case
  period: 2024
  input:
    employment_income: 0
  output:
    income_tax: 0
    eitc: 0

- name: Exactly at phase-out threshold
  period: 2024
  input:
    filing_status: SINGLE
    adjusted_gross_income: 200_000  # Exactly at threshold
  output:
    ctc_phase_out: 0  # No phase-out yet

- name: One dollar over threshold
  period: 2024
  input:
    filing_status: SINGLE
    adjusted_gross_income: 200_001
  output:
    ctc_phase_out: 0.05  # $1 * 5%
```

## Running Tests

### Command Line Options

```bash
# Run all tests
make test

# Run specific test file
pytest policyengine_us/tests/policy/baseline/gov/irs/credits/test_eitc.py

# Run specific test function
pytest policyengine_us/tests/policy/baseline/gov/irs/credits/test_eitc.py::test_eitc_joint -v

# Run YAML tests in a directory
policyengine-core test policyengine_us/tests/policy/baseline/gov/irs/credits -c policyengine_us

# Run with verbose output (see calculation tree)
policyengine-core test path/to/test.yaml -c policyengine_us -v

# Run tests matching a pattern
pytest -k "test_ctc" -v

# Run with coverage
pytest --cov=policyengine_us --cov-report=html
```

### Debugging Failed Tests

When tests fail:

1. **Run with verbose mode** to see the calculation tree:
   ```bash
   policyengine-core test failing_test.yaml -c policyengine_us -v
   ```

2. **Check intermediate values** by adding them to output:
   ```yaml
   output:
     # Debug intermediate calculations
     adjusted_gross_income: 50_000
     taxable_income: 36_150
     # Final value
     income_tax: 4_500
   ```

3. **Use the Python debugger**:
   ```python
   def formula(person, period, parameters):
       import pdb; pdb.set_trace()  # Debugger stops here
       income = person("employment_income", period)
       return income * 0.1
   ```

## Test Data Guidelines

### Realistic Scenarios

Use realistic values that represent common cases:
```yaml
- name: Typical middle-income family
  period: 2024
  input:
    people:
      parent1:
        age: 38
        employment_income: 65_000
      parent2:
        age: 36
        employment_income: 45_000
      child:
        age: 10
```

### Document Calculations

Add comments explaining complex calculations:
```yaml
- name: EITC with investment income limit
  period: 2024
  input:
    employment_income: 20_000
    interest_income: 11_500  # Exceeds $11,000 limit for 2024
  output:
    eitc: 0  # Disqualified due to investment income
```

### Regulatory Examples

When implementing from regulations, create tests matching their examples:
```yaml
- name: IRS Publication 596 Example 1
  period: 2024
  # Recreate exact example from IRS documentation
  input:
    people:
      parent:
        age: 30
        employment_income: 15_000
      child:
        age: 10
    tax_units:
      tax_unit:
        members: [parent, child]
        filing_status: SINGLE
  output:
    eitc: 3_584  # Matches publication
```

## Performance Testing

For expensive calculations:
```python
def test_performance():
    """Ensure calculation completes in reasonable time"""
    import time
    
    sim = Microsimulation()
    start = time.time()
    
    sim.calc("household_net_income", 2024)
    
    duration = time.time() - start
    assert duration < 60  # Should complete within 1 minute
```

## Continuous Integration

All tests run automatically on:
- Every push to a PR
- Before merging to master
- Nightly against the full test suite

Monitor CI results and fix failures promptly.

## Best Practices

1. **Test behavior, not implementation** - Focus on outputs, not how they're calculated
2. **One assertion per test** - Makes failures clear
3. **Use descriptive names** - "test_1" bad, "test_ctc_phase_out_joint_filers" good
4. **Keep tests fast** - Mock expensive operations
5. **Update tests when changing behavior** - Tests document expected behavior
6. **Test the happy path and edge cases** - Both normal and unusual inputs
7. **Don't test the framework** - Trust that OpenFisca works correctly

## Common Pitfalls

### Period Specification
```yaml
# Wrong - don't use full date for year variables
period: 2024-01-01

# Correct - just the year
period: 2024
```

### Variable Scope
```yaml
# Wrong - mixing entity types without structure
input:
  person_variable: 100
  household_variable: 200

# Correct - use proper structure for household tests
input:
  people:
    person1:
      person_variable: 100
  households:
    household:
      members: [person1]
      household_variable: 200
```

### Calculation Dependencies
Always provide all required inputs:
```yaml
# Wrong - missing required income components
input:
  employment_income: 50_000
output:
  agi: 50_000  # Fails if agi includes other income

# Correct - provide all components
input:
  employment_income: 50_000
  interest_income: 0
  dividend_income: 0
  capital_gains: 0
output:
  agi: 50_000
```

## Getting Help

- Run tests with `-v` for verbose output
- Check existing tests for examples
- Ask in GitHub issues if stuck
- Review test failures in CI logs