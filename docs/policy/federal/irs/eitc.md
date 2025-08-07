# Earned Income Tax Credit (EITC)

## Overview

The Earned Income Tax Credit is a refundable federal tax credit for low- and moderate-income working individuals and families. PolicyEngine US models the complete EITC calculation including eligibility determination, credit computation, and interactions with other tax provisions.

## Program Structure

### Credit Design

The EITC uses a trapezoid structure with three regions:
- **Phase-in**: Credit increases proportionally with earned income
- **Plateau**: Maximum credit maintained over an income range  
- **Phase-out**: Credit decreases as income rises above threshold

Credit amounts and phase-out rates vary by:
- Number of qualifying children (0, 1, 2, or 3+)
- Filing status (single, head of household, or married filing jointly)
- Tax year

### Eligibility Components

PolicyEngine US evaluates the following eligibility criteria:

**Basic Requirements**:
- Earned income presence
- Valid Social Security numbers
- Filing status (excludes married filing separately)
- U.S. residency status
- Investment income below annual limit
- Not claimed as qualifying child by another taxpayer

**Age Requirements** (childless workers only):
- Minimum and maximum age thresholds
- Special rules for former foster youth and homeless youth

**Qualifying Child Tests**:
- Relationship test (biological, adopted, step, foster children, siblings, and descendants)
- Age test (based on child's age and student status)
- Residency test (living arrangement for more than half the year)
- Support test (child cannot provide more than half of own support)

## Modeled Variables

### Input Variables
- `employment_income`: Wages, salaries, and tips
- `self_employment_income`: Net earnings from self-employment
- `age`: For childless worker eligibility
- `is_full_time_student`: For qualifying child age test
- `is_disabled`: Affects qualifying child age limits
- Tax unit relationships and structure

### Calculated Variables
- `eitc`: Final EITC amount
- `eitc_phase_in_rate`: Applicable phase-in percentage
- `eitc_maximum`: Maximum credit for filing status and child count
- `eitc_phase_out_rate`: Applicable phase-out percentage
- `eitc_phase_out_start`: Income level where phase-out begins
- `eitc_child_count`: Number of qualifying children
- `eitc_eligible`: Boolean eligibility indicator
- `eitc_relevant_investment_income`: Investment income for limit test
- `takes_up_eitc`: Take-up rate modeling for eligible non-claimants

### Not Currently Modeled
- EITC due diligence requirements
- Paid preparer penalties
- Disallowance periods for previous EITC errors
- State-level EITC supplements (modeled separately in state modules)

## Legislative References

**Primary Authority**: Internal Revenue Code Section 32

**Key Regulations**: 
- 26 CFR 1.32-1 through 1.32-3
- IRS Publication 596
- IRS Form 8862 (reinstatement after disallowance)

## Program Interactions

The EITC interacts with several other tax provisions:
- Reduces tax liability and can generate refunds beyond taxes paid
- Included in modified AGI for Premium Tax Credit calculations
- Excluded from income for most benefit program eligibility
- Cannot be claimed with foreign earned income exclusion

## Data Considerations

PolicyEngine US models EITC participation through:
- Automatic calculation for all eligible tax units
- Optional take-up rate parameters for policy analysis
- Integration with IRS SOI and CPS tax imputation