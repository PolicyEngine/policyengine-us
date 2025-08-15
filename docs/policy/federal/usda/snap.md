# Supplemental Nutrition Assistance Program (SNAP)

## Overview

The Supplemental Nutrition Assistance Program provides monthly benefits to eligible low-income households to purchase food. PolicyEngine US models SNAP eligibility determination, income calculations, deductions, and benefit computation including state-specific variations.

## Program Structure

### Eligibility Pathways

SNAP uses multiple eligibility pathways:
- **Categorical Eligibility**: Automatic qualification through SSI, TANF, or General Assistance
- **Broad-Based Categorical Eligibility (BBCE)**: State options to extend eligibility
- **Standard Eligibility**: Income and asset tests

### Benefit Calculation Framework

Benefits follow a standard formula:
- Maximum allotment based on household size
- Reduced by 30% of net income after deductions
- Minimum benefit for small households
- State-specific utility allowances and options

## Modeled Variables

### Input Variables
- `employment_income`: Wages and salaries
- `self_employment_income`: Net self-employment earnings
- `age`: For elderly deductions and ABAWD rules
- `is_disabled`: For deductions and exemptions
- `is_full_time_student`: Student eligibility rules
- `childcare_expenses`: Dependent care costs
- `medical_out_of_pocket_expenses`: For elderly/disabled
- `rent`, `mortgage_interest`, `mortgage_principal`: Housing costs
- `electricity_expense`, `gas_expense`, `water_expense`: Utilities
- Household composition and relationships

### Calculated Variables
- `snap`: Final monthly benefit amount
- `is_snap_eligible`: Eligibility determination
- `snap_gross_income`: Countable gross income
- `snap_net_income`: Income after deductions
- `snap_assets`: Countable resources
- `meets_snap_categorical_eligibility`: Auto-eligibility
- `meets_snap_gross_income_test`: Under gross limit
- `meets_snap_net_income_test`: Under net limit
- `meets_snap_asset_test`: Under resource limit

### Deduction Variables
- `snap_standard_deduction`: Based on household size
- `snap_earned_income_deduction`: 20% of earnings
- `snap_dependent_care_deduction`: Actual costs
- `snap_medical_expense_deduction`: Excess over threshold
- `snap_child_support_deduction`: Court-ordered payments
- `snap_excess_shelter_expense_deduction`: Housing costs over 50% of income

### State-Specific Variables
- `snap_bbce_gross_income_limit`: State BBCE threshold
- `snap_standard_utility_allowance`: State SUA amounts
- `snap_emergency_allotment`: COVID-era supplements (historical)

### Not Currently Modeled
- Restaurant Meals Program participation
- SNAP Employment & Training program details
- Work requirement tracking and exemptions
- Trafficking and program integrity measures
- Combined Application Project (CAP) simplifications

## Legislative References

**Primary Authority**: Food and Nutrition Act of 2008 (7 USC 2011-2036)

**Key Regulations**: 7 CFR Parts 271-285

**Major Amendments**:
- Personal Responsibility and Work Opportunity Reconciliation Act of 1996
- Farm Bill reauthorizations (2002, 2008, 2014, 2018)
- COVID-19 response legislation (2020-2023)

## Program Interactions

SNAP coordinates with multiple programs:
- **Categorical Eligibility**: Through SSI, TANF receipt
- **School Meals**: Direct certification for free lunch
- **LIHEAP**: Utility allowance triggers ("Heat and Eat")
- **Medicaid**: Often combined applications
- **WIC**: Different but complementary nutrition support

## Household Composition Rules

PolicyEngine US models SNAP's complex household definitions:
- **SNAP Unit**: People who purchase and prepare food together
- **Mandatory Members**: Children under 22 living with parents
- **Elderly/Disabled Exception**: Can be separate unit
- **Boarders**: Special income counting rules
- **Ineligible Members**: Immigration status, ABAWD time limits

## Work Requirements

The model includes:
- **General Work Registration**: Ages 16-59
- **ABAWD Time Limits**: 3 months in 36 for ages 18-52
- **Exemptions**: Disability, pregnancy, caregiving
- **Student Eligibility**: Special restrictions and exceptions

## State Variations

PolicyEngine US captures state options including:
- BBCE implementation and income limits
- Standard Utility Allowance amounts
- Certification period lengths
- Transitional benefit policies
- Simplified reporting thresholds

## Data Considerations

The model uses:
- USDA Food and Nutrition Service parameters
- State SNAP policy databases
- Quality Control sample data for validation
- Participation rate modeling for take-up