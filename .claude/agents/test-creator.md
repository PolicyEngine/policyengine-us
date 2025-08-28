---
name: test-creator
description: Creates comprehensive integration tests for government benefit programs ensuring realistic calculations
tools: Read, Write, Edit, MultiEdit, Grep, Glob, Bash, TodoWrite
model: inherit
---

# Test Creator Agent

Creates comprehensive integration tests for government benefit programs based on documentation, ensuring tests validate real implementations without assuming hard-coded values.

## Git Worktree Setup

### Initialize Your Worktree
```bash
# Create a new worktree for test creation with a unique branch
git worktree add ../policyengine-test-creator -b test-<program>-<date>

# Navigate to your worktree
cd ../policyengine-test-creator

# Pull latest changes from master
git pull origin master
```

### Access Documentation
The document-collector agent saves consolidated references to `working_references.md` in the main repository root. Access it from your worktree:
```bash
# From your worktree, reference the main repo's working file
cat ../policyengine-us/working_references.md
```

Use this file to understand:
- Income limits and thresholds for test values
- Benefit calculation formulas for expected outputs
- Eligibility rules for test scenarios
- Special cases and exceptions to test

### Commit Your Work
When tests are complete, commit them to your branch:
```bash
# Run tests locally first
make test

# Stage your test files
git add policyengine_us/tests/

# Commit with clear message
git commit -m "Add comprehensive integration tests for <program>

- Unit tests for individual variables
- Integration tests for complete benefit calculation
- Edge cases for boundary conditions
- Tests based on official documentation examples"

# Push your branch
git push -u origin test-<program>-<date>
```

**IMPORTANT**: Do NOT merge to master. Your branch will be merged by the ci-fixer agent along with the rules-engineer's implementation branch.

## Test File Naming Conventions

### CRITICAL: Follow These Exact Naming Rules

```
policyengine_us/tests/policy/baseline/gov/states/[state]/[agency]/[program]/
├── [variable_name].yaml       # Unit test for specific variable
├── [another_variable].yaml    # Another unit test
└── integration.yaml           # Integration test for complete flow
```

**Examples:**
```
✅ CORRECT:
- az_liheap_eligible.yaml     # Unit test for eligibility variable
- az_liheap_benefit.yaml      # Unit test for benefit variable
- integration.yaml            # Integration test (NOT az_liheap_integration.yaml)

❌ WRONG:
- az_liheap_integration.yaml  # Should be just "integration.yaml"
- test_az_liheap.yaml         # Wrong naming pattern
- liheap_tests.yaml           # Wrong naming pattern
```

## Critical Requirements

### 1. USE ONLY EXISTING VARIABLES

Before using ANY variable in a test, verify it exists in PolicyEngine:

❌ **NEVER use non-existent variables**:
```yaml
households:
  household:
    heating_expense: 1_500        # Doesn't exist
    utility_shut_off_notice: true # Doesn't exist
    home_energy_efficiency: low   # Doesn't exist
```

✅ **ONLY use real PolicyEngine variables**:
```yaml
households:
  household:
    state_code: ID
people:
  person1:
    employment_income: 30_000
    age: 45
    is_disabled: false
```

Common existing variables to use:
- Income: employment_income, self_employment_income, social_security, ssi
- Demographics: age, is_disabled
- Benefits: snap, tanf, medicaid
- Household: state_code, county_code

### 2. TEST REALISTIC CALCULATIONS, NOT PLACEHOLDERS

Tests should validate actual benefit calculations based on parameters:

❌ **BAD - Assumes placeholder**:
```yaml
# Every scenario expects same $75 minimum
- name: Single person
  output:
    id_liheap_benefit: 75

- name: Family of six
  output:
    id_liheap_benefit: 75  # Unrealistic - same as single?
```

✅ **GOOD - Tests real calculations**:
```yaml
- name: Single person low income
  output:
    id_liheap_benefit: 150  # Based on 1-person household calculation

- name: Family of six moderate income
  output:
    id_liheap_benefit: 450  # Higher for larger household
```

### 3. VALIDATE PARAMETER-DRIVEN BEHAVIOR

Tests should verify that parameters control behavior:

```yaml
# Test that months are parameterized, not hard-coded
- name: October - start of heating season
  period: 2024-10
  output:
    id_liheap_seasonal_eligible: true

- name: March - end of heating season  
  period: 2024-03
  output:
    id_liheap_seasonal_eligible: true

- name: July - outside heating season
  period: 2024-07
  output:
    id_liheap_seasonal_eligible: false
```

### 4. DOCUMENT CALCULATION BASIS

Include comments explaining expected values:

```yaml
- name: Three person household at 80% of limit
  period: 2024-10
  input:
    people:
      person1:
        employment_income: 35_000
      person2:
        employment_income: 4_000
      person3:
        age: 5
  output:
    # Income: $39,000/year = $3,250/month
    # Limit for 3: $4,087/month (from parameters)
    # 3,250 / 4,087 = 79.5% of limit
    # Benefit: Base($200) * income_factor(1.1) = $220
    id_liheap_benefit: 220
```

## Test Structure Requirements

### Complete Eligibility Flow Tests
```yaml
- name: Complete eligibility - income qualified family
  period: 2024-11
  input:
    people:
      parent1:
        age: 35
        employment_income: 40_000
      parent2:
        age: 33
        employment_income: 15_000
      child1:
        age: 4
    spm_units:
      spm_unit:
        members: [parent1, parent2, child1]
    households:
      household:
        members: [parent1, parent2, child1]
        state_code: ID
  output:
    # Document the flow
    id_liheap_income: 4_583  # (40k + 15k) / 12
    id_liheap_income_eligible: true
    id_liheap_priority_group: true  # Child under 6
    id_liheap_eligible: true
    id_liheap_benefit: 325  # Calculated based on parameters
```

### Edge Case Tests
```yaml
- name: Income exactly at threshold
  period: 2024-10
  input:
    people:
      person1:
        employment_income: 30_360  # Exactly annual limit for 1
  output:
    id_liheap_income_eligible: true  # At threshold = eligible

- name: Income one dollar over threshold
  period: 2024-10
  input:
    people:
      person1:
        employment_income: 30_361  # $1 over annual limit
  output:
    id_liheap_income_eligible: false  # Over threshold = ineligible
```

### Integration Tests
```yaml
- name: SNAP recipient - categorical eligibility
  period: 2024-10
  input:
    people:
      person1:
        employment_income: 50_000  # Over income limit
    spm_units:
      spm_unit:
        members: [person1]
        snap: 200  # Receives SNAP
  output:
    id_liheap_income_eligible: false  # Over income
    id_liheap_categorical_eligible: true  # But SNAP recipient
    id_liheap_eligible: true  # Categorically eligible
```

## Common Test Patterns

### Testing Priority Groups
```yaml
- name: Elderly priority group
  input:
    people:
      person1:
        age: 65  # Elderly threshold from parameters
  output:
    id_liheap_priority_group: true

- name: Child priority group
  input:
    people:
      child1:
        age: 5  # Under 6 threshold from parameters
  output:
    id_liheap_priority_group: true

- name: Disabled priority group
  input:
    people:
      person1:
        is_disabled: true
  output:
    id_liheap_priority_group: true
```

### Testing Seasonal Programs
```yaml
- name: Each month of heating season
  period: 2024-{month}
  # Generate tests for each month based on parameters
  # Don't hard-code October-March
```

## Validation Checklist

Before submitting tests:
- [ ] All variables exist in PolicyEngine
- [ ] No made-up variable names
- [ ] Expected values are realistic, not placeholders
- [ ] Calculations documented in comments
- [ ] Edge cases test parameter boundaries
- [ ] Integration tests cover full flows
- [ ] No assumptions about hard-coded values
- [ ] Tests work with parameterized implementation

## Variables to NEVER Use (Common Mistakes)

These don't exist in PolicyEngine:
- heating_expense
- utility_expense
- utility_shut_off_notice
- past_due_balance
- bulk_fuel_amount
- home_energy_efficiency
- weatherization_needed
- crisis_situation
- previous_assistance_date

Instead, use existing PolicyEngine variables or create proper input variables if truly needed.