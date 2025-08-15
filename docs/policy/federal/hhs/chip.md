# Children's Health Insurance Program (CHIP)

## Overview

The Children's Health Insurance Program provides health coverage to uninsured children in families with incomes too high to qualify for Medicaid but too low to afford private coverage. PolicyEngine US models CHIP eligibility including state-specific income limits and coordination with Medicaid.

## Program Structure

### Coverage Design

CHIP operates through three models:
- **Medicaid Expansion**: CHIP funds expand Medicaid
- **Separate CHIP**: Stand-alone program
- **Combination**: Both approaches

### Target Population

CHIP primarily covers:
- Uninsured children under 19
- Families above Medicaid limits
- Some states cover pregnant women
- Limited adult coverage (ended)

## Modeled Variables

### Input Variables
- `age`: Child age for eligibility
- `is_pregnant`: For states covering pregnancy
- Health insurance coverage status
- Modified AGI components
- Household composition

### Calculated Variables
- `chip`: Coverage indicator
- `is_chip_eligible`: Overall eligibility
- `is_chip_eligible_child`: Child eligibility
- `is_chip_eligible_pregnant`: Pregnant woman eligibility
- `chip_category`: Eligibility category
- `per_capita_chip`: Per person amount

### Eligibility Components
- `is_chip_fcep_eligible_person`: Former foster care
- `is_chip_eligible_standard_pregnant_person`: Standard pregnancy coverage
- Income level calculations

### Not Currently Modeled
- Waiting periods
- Crowd-out prevention
- Premium schedules
- Cost-sharing rules
- Express Lane eligibility

## Legislative References

**Primary Authority**: Title XXI of the Social Security Act

**Key Legislation**:
- Balanced Budget Act of 1997 (created CHIP)
- CHIPRA 2009 (reauthorization)
- Various extensions

## Program Interactions

CHIP coordinates with:
- **Medicaid**: Screen and enroll
- **Marketplace**: Premium tax credit exclusion
- **Employer Coverage**: Coordination rules
- **Other Insurance**: Third-party liability

## Income Methodology

CHIP uses:
- Modified AGI (like Medicaid)
- Household composition rules
- No asset test
- Standard 5% income disregard

## State Variations

States determine:
- Income eligibility limits (median ~255% FPL)
- Benefits package design
- Cost-sharing requirements
- Enrollment procedures
- Coverage of pregnant women

## Special Provisions

CHIP includes:
- Continuous eligibility option
- Presumptive eligibility
- No wrong door with Medicaid
- Premium assistance programs

## Data Considerations

The model uses:
- State CHIP income limits
- Federal poverty guidelines
- Enrollment data by state
- Coordination with Medicaid model