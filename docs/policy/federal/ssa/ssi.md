# Supplemental Security Income (SSI)

## Overview

Supplemental Security Income provides cash assistance to aged, blind, and disabled individuals with limited income and resources. PolicyEngine US models SSI eligibility determination, income calculations, deeming rules, and benefit computation including state supplements.

## Program Structure

### Eligibility Categories

SSI serves three distinct populations:
- **Aged**: Individuals 65 or older
- **Blind**: Meeting statutory blindness definition
- **Disabled**: Unable to engage in substantial gainful activity

### Benefit Framework

Benefits are based on:
- Federal Benefit Rate (FBR) for individuals and couples
- Countable income reduces benefits dollar-for-dollar
- Resource limits apply
- State supplements in many states

## Modeled Variables

### Input Variables
- `age`: For aged eligibility
- `is_ssi_disabled`: Disability determination
- `is_blind`: Blindness status
- `employment_income`: Wages and self-employment
- `unearned_income`: Social Security, pensions, etc.
- `ssi_countable_resources`: Assets for resource test
- Household composition for deeming rules

### Calculated Variables
- `ssi`: Final monthly benefit amount
- `is_ssi_eligible`: Eligibility determination
- `ssi_amount_if_eligible`: Benefit before take-up
- `ssi_countable_income`: Income after exclusions
- `ssi_earned_income`: Countable earned income
- `ssi_unearned_income`: Countable unearned income
- `meets_ssi_resource_test`: Under resource limit

### Deeming Variables
- `ssi_income_deemed_from_ineligible_spouse`: Spousal deeming
- `ssi_income_deemed_from_ineligible_parent`: Parental deeming
- `ssi_marital_both_eligible`: Both spouses eligible flag

### State Supplement Variables

PolicyEngine US models SSI state supplements for:
- **California**: Comprehensive state supplement with various living arrangements
- **Colorado**: Basic state supplement
- **Massachusetts**: State supplement program

State supplement variables include:
- `ca_state_supplement`: California's supplement with detailed payment standards
- `co_state_supplement`: Colorado's basic supplement
- `ma_state_supplement`: Massachusetts supplement
- Living arrangement adjustments (CA has detailed facility types)

### Not Currently Modeled
- In-kind support and maintenance (ISM) calculations
- Detailed living arrangement variations
- Retrospective monthly accounting
- Overpayment recovery rules
- Work incentive provisions (PASS, BWE, etc.)

## Legislative References

**Primary Authority**: Title XVI of the Social Security Act

**Key Regulations**: 20 CFR Parts 416

**Major Provisions**:
- Social Security Amendments of 1972 (created SSI)
- Various COLAs and program modifications

## Program Interactions

SSI interacts with multiple programs:
- **Categorical Eligibility**: For SNAP, Medicaid
- **Income Exclusions**: Certain benefits excluded
- **State Administration**: Some states administer supplements
- **Representative Payee**: For beneficiaries needing assistance

## Income Counting Rules

PolicyEngine US models SSI's complex income rules:
- **$20 General Exclusion**: First $20 of any income
- **$65 Earned Income Exclusion**: Additional for wages
- **50% Remainder**: Half of remaining earned income excluded
- **Deeming**: From ineligible spouses and parents
- **Student Earned Income Exclusion**: For those under 22

## Resource Rules

The model includes:
- Individual and couple resource limits
- Excluded resources (home, one vehicle, etc.)
- Deemed resources from spouses/parents
- Conditional eligibility while disposing excess resources

## Living Arrangements

SSI benefits vary by living situation:
- Own household
- Another's household
- Medicaid facility
- Public or private institution
- Homeless

## Data Considerations

The model uses:
- SSA program parameters and FBR amounts
- State supplement schedules
- Historical payment standards
- Take-up rate modeling for eligible non-participants