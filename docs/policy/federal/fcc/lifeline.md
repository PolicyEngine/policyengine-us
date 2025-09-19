# Lifeline

## Overview

Lifeline provides discounted phone and internet service to low-income consumers to ensure all Americans have access to essential communications services. PolicyEngine US models Lifeline eligibility and the monthly discount amount.

## Program Structure

### Service Options

Lifeline provides discounts for:
- Voice service
- Broadband internet
- Bundled voice/broadband
- Mobile or fixed service

### Benefit Amount

Standard monthly discount with variations:
- General discount amount
- Enhanced Tribal lands benefit
- One discount per household
- Applied to service bill

## Modeled Variables

### Input Variables
- Income for eligibility determination
- Program participation for categorical eligibility
- Tribal lands residence (if applicable)

### Calculated Variables
- `lifeline`: Monthly discount amount
- `is_lifeline_eligible`: Eligibility determination
- `broadband_cost_after_lifeline`: Net service cost
- `fcc_fpg_ratio`: Income as percent of poverty

### Not Currently Modeled
- Service provider selection
- Documentation requirements
- Annual recertification
- National Verifier process
- Port freeze rules

## Legislative References

**Primary Authority**: Communications Act of 1934, Section 254

**Key Regulations**: 47 CFR Part 54, Subpart E

**Program Administration**: Universal Service Administrative Company (USAC)

## Eligibility Pathways

Qualify through income or program participation:

### Income-Based
- At or below 135% of Federal Poverty Guidelines
- Based on household income
- Documented through National Verifier

### Program-Based
Participation in:
- SNAP
- Medicaid
- SSI
- Federal Public Housing Assistance
- Veterans Pension and Survivors Benefit
- Tribal programs (for Tribal lands)

## Program Rules

Key requirements:
- One benefit per household
- Cannot transfer benefit
- Must recertify annually
- De-enrollment for non-usage
- Port freeze protections

## Tribal Lands Enhancement

Enhanced support includes:
- Additional monthly discount
- Expanded eligibility programs
- Link Up support (installation)

## Data Considerations

The model uses:
- FCC discount amounts
- Federal poverty guidelines
- Program participation indicators
- Simplified benefit calculation