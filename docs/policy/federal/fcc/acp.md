# Affordable Connectivity Program (ACP)

## Overview

The Affordable Connectivity Program provided discounted broadband service to low-income households. PolicyEngine US models ACP eligibility and benefit calculations. Note: The program ended in May 2024 due to funding exhaustion.

## Program Structure

### Benefit Design

ACP provided monthly discounts:
- Standard households: Monthly discount
- Tribal lands: Enhanced discount
- Applied directly to broadband bill
- One discount per household

## Modeled Variables

### Input Variables
- Income for eligibility determination
- Tribal lands residence
- `broadband_cost_after_lifeline`: Net broadband cost
- Program participation for categorical eligibility

### Calculated Variables
- `acp`: Monthly discount amount
- `is_acp_eligible`: Eligibility determination

### Not Currently Modeled
- Device discount benefit
- Provider participation
- Benefit transfer between providers

## Legislative References

**Primary Authority**: Infrastructure Investment and Jobs Act of 2021

**Program End**: May 2024 (funding exhausted)

## Eligibility

Qualified through:
- Income at or below 200% FPL
- Participation in qualifying programs:
  - SNAP
  - Medicaid
  - WIC
  - Lifeline
  - Federal housing assistance
  - Veterans Pension
  - Tribal programs

## Program Interactions

ACP coordinated with:
- **Lifeline**: Could receive both benefits
- **SNAP/Medicaid**: Categorical eligibility
- **Tribal Programs**: Enhanced benefits

## Data Considerations

The model:
- Calculates benefits based on program rules
- Historical modeling through May 2024
- Can model hypothetical program extensions