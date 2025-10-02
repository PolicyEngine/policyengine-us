# Medicaid

## Overview

Medicaid provides health insurance coverage to low-income individuals and families. PolicyEngine US models Medicaid eligibility across different pathways, including MAGI-based and traditional categories, with state-specific income limits and expansions.

## Program Structure

### Eligibility Pathways

Medicaid uses multiple eligibility categories:
- **MAGI-Based**: Adults, children, pregnant women (ACA rules)
- **SSI-Related**: Aged, blind, disabled (traditional rules)
- **Medically Needy**: High medical costs (some states)
- **Special Groups**: Former foster youth, breast/cervical cancer

### Coverage Groups

Major coverage categories include:
- Children (mandatory)
- Pregnant women (mandatory)
- Parents/caretakers (mandatory with variations)
- Expansion adults (state option)
- Aged, blind, disabled (mandatory)

## Modeled Variables

### Input Variables
- `age`: For age-based categories
- `is_pregnant`: Pregnancy category
- `is_disabled`: Disability-based eligibility
- `is_blind`: Blindness category
- Modified AGI components
- Household size and composition

### Calculated Variables
- `medicaid`: Coverage indicator
- `is_medicaid_eligible`: Eligibility determination
- `medicaid_category`: Specific eligibility pathway
- `medicaid_income_level`: FPL percentage for household
- `tax_unit_medicaid_income_level`: Tax unit income level

### Income Calculation Variables
- `medicaid_magi`: Modified AGI for Medicaid
- Household income aggregation
- Income disregards for non-MAGI categories

### Not Currently Modeled
- Asset tests for non-MAGI categories
- Spend-down provisions
- Estate recovery rules
- Retroactive coverage
- Presumptive eligibility
- Emergency Medicaid

## Legislative References

**Primary Authority**: Title XIX of the Social Security Act

**Key Regulations**: 42 CFR Parts 430-456

**Major Amendments**:
- Medicaid Act of 1965
- Affordable Care Act of 2010 (MAGI rules)
- Various state plan amendments

## Program Interactions

Medicaid coordinates with:
- **Medicare**: Dual eligibles
- **CHIP**: Children's health coverage
- **Marketplace**: Premium tax credit coordination
- **SSI**: Automatic eligibility in most states
- **SNAP/TANF**: Simplified applications

## MAGI Methodology

For MAGI-based groups:
- Uses tax filing unit
- Modified AGI per ACA rules
- No asset test
- Standardized income counting

## State Variations

PolicyEngine US captures:
- Medicaid expansion status
- Income limits by category
- Optional eligibility groups
- State-specific disregards
- 1115 waiver provisions

## Special Provisions

The model includes:
- Continuous eligibility for children
- Hospital presumptive eligibility
- Transitional Medical Assistance
- Family planning services
- Katie Beckett eligibility

## Data Considerations

The model uses:
- CMS state plan data
- Kaiser Family Foundation tracking
- State Medicaid agency parameters
- Take-up rate modeling by category