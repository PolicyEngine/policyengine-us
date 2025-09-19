# Housing Assistance Programs

## Overview

Federal housing assistance helps low-income families afford safe and decent housing through various programs. PolicyEngine US models the major rental assistance programs including Housing Choice Vouchers, Public Housing, and Project-Based Section 8.

## Program Structure

### Major Programs

Housing assistance includes:
- **Housing Choice Vouchers (Section 8)**: Tenant-based rental assistance
- **Public Housing**: Government-owned housing units
- **Project-Based Section 8**: Assistance tied to specific units
- **Other HUD programs**: Various targeted assistance

### Benefit Calculation

All programs use similar formulas:
- Tenant pays 30% of adjusted income
- HUD covers difference to payment standard
- Utility allowances included
- Minimum rent provisions

## Modeled Variables

### Input Variables
- Income from all sources
- Family size and composition
- `receives_housing_assistance`: Participation indicator
- Disability and elderly status
- Location for payment standards

### Calculated Variables
- `housing_assistance`: Monthly subsidy value
- `hud_income_level`: Very low, extremely low, etc.
- `hud_annual_income`: Income per HUD rules
- `hud_adjusted_income`: After deductions
- `hud_ttp`: Total Tenant Payment
- `hud_hap`: Housing Assistance Payment

### Income Variables
- `hud_gross_rent`: Rent plus utilities
- `pha_payment_standard`: Local payment standard
- `hud_utility_allowance`: Utility costs
- Various HUD deductions

### Not Currently Modeled
- Waiting list preferences
- Portability between jurisdictions
- Project-specific rules
- Homeownership vouchers
- Special allocations (VASH, FUP, etc.)

## Legislative References

**Primary Authority**: United States Housing Act of 1937

**Key Regulations**: 24 CFR Parts 5, 8, 880-891, 960-990

**Major Amendments**:
- Quality Housing and Work Responsibility Act of 1998
- Housing Choice Voucher Program regulations

## Income Determination

HUD annual income includes:
- Employment income
- Social Security, pensions
- Public assistance
- Assets over $5,000
- Various other sources

## Deductions

Adjusted income deductions:
- **Dependent Deduction**: Per dependent
- **Elderly/Disabled Deduction**: For families
- **Medical Expenses**: Over 3% of income
- **Disability Expenses**: Permitting work
- **Child Care**: For work/education

## Payment Standards

Housing costs covered:
- Fair Market Rent (FMR) basis
- Payment standards 90-110% of FMR
- Exception payment standards
- Utility allowance schedules

## Program Interactions

Housing assistance affects:
- **SNAP**: Shelter deduction
- **LIHEAP**: Utility assistance
- **Medicaid**: Not counted as income
- **Tax Credits**: Excludable from income

## Special Provisions

The model includes:
- Elderly and disabled families
- Mixed families (immigration)
- Minimum rent hardship exemptions
- Income targeting requirements

## Area Median Income (AMI)

HUD uses AMI to determine:
- Eligibility limits
- Targeting requirements
- Rent reasonableness
- Program priorities

## Data Considerations

The model uses:
- HUD Fair Market Rents
- Area Median Incomes
- Payment standard schedules
- Utility allowance schedules
- Administrative data on participation