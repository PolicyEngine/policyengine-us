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

## Test Naming Within Files

### Case Naming Convention

Use numbered cases with concise descriptions:

**Format:**
```yaml
- name: Case 1, [description].
- name: Case 2, [description].
- name: Case 3, [description].
```

**Examples:**
```yaml
- name: Case 1, single parent with one child.
- name: Case 2, two parents with two children.
- name: Case 3, child receiving SSI excluded from assistance unit.
```

### Person Naming Convention

**Use generic sequential names:**
- `person1`, `person2`, `person3`, etc.
- NOT descriptive names like `parent`, `child`, `grandparent`

**Good:**
```yaml
people:
  person1:
    age: 30
    is_parent: true
  person2:
    age: 10
  person3:
    age: 8
```

**Bad:**
```yaml
people:
  parent:
    age: 30
  child1:
    age: 10
  child2:
    age: 8
```

### Output Format

**Use simplified format without entity key:**

**Good:**
```yaml
output:
  tx_tanf_assistance_unit_size: 2
  tx_tanf_eligible: true
```

**Bad:**
```yaml
output:
  tx_tanf_assistance_unit_size:
    spm_unit: 2
  tx_tanf_eligible:
    spm_unit: true
```

## Which Variables Need Tests

### Variables That DON'T Need Test Files

**Skip creating tests for variables that only use `adds` or `subtracts`:**

```python
# NO TEST NEEDED - just summing
class tx_tanf_countable_income(Variable):
    adds = ["tx_tanf_countable_earned_income", "tx_tanf_countable_unearned_income"]

# NO TEST NEEDED - just summing
class tx_tanf_assistance_unit_size(Variable):
    adds = ["tx_tanf_eligible_child", "tx_tanf_eligible_parent"]

# NO TEST NEEDED - just subtracting
class some_variable(Variable):
    adds = ["income"]
    subtracts = ["deductions"]
```

Why? These are simple composition operations with no logic to test.

### Variables That NEED Test Files

**Create tests for variables with actual formulas:**
- Variables with conditional logic (`where`, `select`, `if`)
- Variables with calculations/transformations
- Variables with business logic
- Variables that apply deductions/disregards
- Variables that determine eligibility

```python
# NEEDS TEST - has conditional logic
class tx_tanf_income_eligible(Variable):
    def formula(spm_unit, period, parameters):
        return where(is_enrolled, passes_recognizable, passes_budgetary & passes_recognizable)

# NEEDS TEST - has calculations
class tx_tanf_budgetary_needs(Variable):
    def formula(spm_unit, period, parameters):
        return select([...], [...])  # Selection logic needs testing
```

## Period Conversion in Tests

**Critical Rule:** When test period is MONTH (e.g., `period: 2025-01`):

### Input Values
- Provide YEAR variables in their **annual amount**
- PolicyEngine will auto-convert to monthly for testing

### Output Values
- YEAR variables will show **monthly values** in output
- Annual amount ÷ 12 = expected monthly output

**Example:**
```yaml
- name: Case 1, employment income conversion.
  period: 2025-01  # MONTH period
  input:
    people:
      person1:
        employment_income: 12_000  # Annual input
  output:
    employment_income: 1_000  # Monthly output (12_000 / 12)
```

**Another example:**
```yaml
- name: Case 2, annual income of $24,000.
  period: 2025-01
  input:
    people:
      person1:
        employment_income: 24_000  # Input: yearly
  output:
    employment_income: 2_000  # Output: monthly (24_000 / 12)
```

**Key point:** Input the full annual amount, expect the monthly amount in output when testing MONTH periods.

## Numeric Value Formatting

**Always use underscore thousands separators:**

**Good:**
```yaml
employment_income: 1_000
spm_unit_cash_assets: 12_000
```

**Bad:**
```yaml
employment_income: 1000
spm_unit_cash_assets: 12000
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

## Integration Test Quality Standards

Integration tests should meet high quality standards. Use IL TANF as the reference implementation.

### Inline Calculation Comments

**Every integration test should include step-by-step calculation comments:**

```yaml
- name: Case 2, household with earnings and child care expenses.
  period: 2025-01
  absolute_error_margin: 0.01
  input:
    people:
      person1:
        employment_income: 3_000  # $250/month
      person2:
        age: 1
    spm_units:
      spm_unit:
        members: [person1, person2]
        childcare_expenses: 2_400  # $200/month
  output:
    tx_tanf_gross_earned_income: [250, 0]
    # Person1: 3,000 / 12 = 250, Person2: 0

    tx_tanf_earned_income_after_disregard_person: [87.1, 0]
    # Person1 (applicant, 1/3 disregard):
    #   After work expense: 250 - 120 = 130
    #   Disregard = 130 / 3 = 43.33
    #   After disregard = 130 - 43.33 = 86.67 ≈ 87.1

    tx_tanf_dependent_care_deduction: 200
    # Child age 1 → $200/month cap

    tx_tanf_countable_earned_income: 0
    # Sum person-level: 87.1 + 0 = 87.1
    # After dependent care: max(87.1 - 200, 0) = 0
```

**Why inline comments matter:**
- Makes tests self-documenting
- Easier to verify correctness
- Helps others understand the calculation
- Catches errors during test creation

### Comprehensive Scenarios

**Aim for 5-7 integration test scenarios covering:**

1. **Basic eligible case** - Low income, eligible, receives full benefit
2. **Earnings + deductions** - Income with work expense, child care
3. **Edge case eligibility** - Just passes/fails income test
4. **Applicant vs continuing** - Same household, different enrollment status
5. **Mixed immigration** - Undocumented parent, citizen children
6. **SSI exclusion** - Children receiving SSI excluded from unit
7. **Ineligible case** - Exceeds income or resource limits

**Don't just test:**
- One eligible case
- One ineligible case
- Call it done

### Intermediate Value Checks

**Verify 8-10 intermediate values per integration test:**

```yaml
output:
  # Assistance unit
  program_assistance_unit_size: 2
  program_caretaker_type: CARETAKER_WITHOUT_SECOND_PARENT

  # Income calculation
  program_gross_earned_income: [250, 0]
  program_earned_income_after_disregard: [87.1, 0]
  program_dependent_care_deduction: 200
  program_countable_earned_income: 0
  program_countable_income: 0

  # Eligibility tests
  program_budgetary_needs: 650
  program_income_eligible: true
  program_resources_eligible: true
  program_eligible: true

  # Payment
  program_payment_standard: 320
  program: 320
```

**Why verify intermediate values:**
- Catches errors at each step of calculation
- Makes debugging easier
- Documents the full calculation pipeline
- Verifies the entire flow works together

### Quality Bar

**Integration tests should:**
- [ ] Include 5-7 comprehensive scenarios
- [ ] Have inline calculation comments for all steps
- [ ] Verify 8-10 intermediate values per test
- [ ] Cover edge cases (mixed status, SSI, enrollment differences)
- [ ] Show WHY values are what they are (not just WHAT they are)

## Always Verify Enum Values Before Testing

Before writing tests that use enum values, **ALWAYS check the actual Enum class definition**.

### Common Mistake

**Wrong - guessing enum values:**
```yaml
- name: Case, permanent resident eligible.
  input:
    immigration_status: PERMANENT_RESIDENT  # WRONG - doesn't exist!
```

**Right - using actual enum values:**
```yaml
- name: Case, permanent resident eligible.
  input:
    immigration_status: LEGAL_PERMANENT_RESIDENT  # Correct!
```

### How to Find Enum Values

1. **Search for the Enum class:**
```bash
grep -r "class ImmigrationStatus" policyengine_us/variables --include="*.py"
```

2. **Read the enum definition:**
```python
class ImmigrationStatus(Enum):
    CITIZEN = "Citizen"
    LEGAL_PERMANENT_RESIDENT = "Legal Permanent Resident"  # Not PERMANENT_RESIDENT!
    REFUGEE = "Refugee"
    ASYLEE = "Asylee"
    UNDOCUMENTED = "Undocumented"
    DACA = "Deferred Action for Childhood Arrivals"
    # No "OTHER" or "TEMPORARY_VISITOR"!
```

3. **Use exact enum values in tests**

### Common Enums to Check

- `ImmigrationStatus` - Check for exact names
- `StateCode` - Use two-letter codes (TX, CA, IL)
- Program-specific enums (TxTanfCaretakerType, etc.)

**Don't guess - verify!**

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