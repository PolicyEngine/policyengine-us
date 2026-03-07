# Idaho AABD Cash Assistance (State Supplemental Payment)

## Official Program Name

**Federal Program**: State Supplemental Payment (SSP) to SSI
**State's Official Name**: Aid to the Aged, Blind, and Disabled (AABD) Cash Assistance
**Abbreviation**: AABD
**Source**: IDAPA 16.03.05 - Eligibility for Aid to the Aged, Blind, and Disabled
**Administering Agency**: Idaho Department of Health and Welfare (DHW)
**Administration Type**: State-administered

**Variable Prefix**: `id_aabd`

## Program Overview

Idaho's AABD Cash Assistance program provides monthly cash payments to SSI recipients
based on their living arrangement. The program is governed by IDAPA 16.03.05, Sections
500-514.

Key requirement: "Only a participant who receives an SSI payment for the month is
eligible for an AABD cash payment in the same month." (IDAPA 16.03.05.514)

## Payment Amounts (IDAPA 16.03.05.514, effective 7-1-24)

### Maximum Monthly AABD Cash Payments

| Living Arrangement | Max Payment | Reference |
|---|---|---|
| Single participant (Sec 501.01) | $53 | IDAPA 16.03.05.514.01 |
| Couple (Sec 501.02) | $20 | IDAPA 16.03.05.514.02.a |
| Participant w/ essential person (Sec 501.02) | $18 | IDAPA 16.03.05.514.02.b |
| Semi-Independent Group (SIGRIF) (Sec 501.03) | $169 | IDAPA 16.03.05.514.03 |
| Room and Board (Sec 512) | $198 | IDAPA 16.03.05.514.04 |
| RALF or CFH | $0 (ineligible) | IDAPA 16.03.05.514.05 |

### Basic Allowances (IDAPA 16.03.05.501)

These are the "financial need" amounts used to determine if a participant qualifies:

| Living Arrangement | Basic Allowance | COLA Adjustment |
|---|---|---|
| Single participant | $545 (base) + annual SSI COLA $ amount | Yes, by SSI individual COLA $ |
| Couple/essential person | $768 (base) + annual SSI couple COLA $ | Yes, by SSI couple COLA $ |
| SIGRIF | $349 | No annual adjustment |
| Room and Board | $77 basic + $693 R&B allowance = $770 total | Yes, by SSI individual COLA % |

### Payment Calculation

AABD cash payment = min(max_payment, max(0, allowances - countable_income))

Where:
- allowances = basic allowance + any special needs allowances
- countable_income = income after SSI-style disregards
- max_payment = maximum from table above

## Eligibility Criteria

1. **SSI Receipt Required**: Must receive an SSI payment for the month (IDAPA 16.03.05.514)
2. **Age/Disability**: Must be aged (65+), blind, or disabled (IDAPA 16.03.05, general)
3. **Residency**: Idaho resident
4. **Living Arrangement**: Must NOT reside in RALF or CFH (IDAPA 16.03.05.514.05)

## Living Arrangement Definitions (IDAPA 16.03.05.501)

- **501.01 Single**: Living alone, with ineligible spouse, with another participant (not spouse), in another's household, or with TAFI child
- **501.02 Couple/Essential Person**: Living with participant spouse or essential person
- **501.03 SIGRIF**: Living in semi-independent group residential facility
- **512 Room and Board**: Purchasing lodging and meals from non-relative they live with
- **513 RALF/CFH**: Residential Assisted Living Facility or Certified Family Home (NOT eligible for AABD cash)

## Special Needs Allowances (IDAPA 16.03.05.502)

- Restaurant meals: $50/month (physician must certify inability to prepare food)
- Service animal food: Amount varies

## Income Disregards (IDAPA 16.03.05.540-546)

- $20 standard disregard (Section 540)
- $65 earned income disregard (Section 542)
- 1/2 remaining earned income (Section 544)
- Impairment-related work expenses (Section 543)
- Blindness work expenses (Section 545)
- PASS deductions (Section 546)

## Key Sources

1. IDAPA 16.03.05 (full text): https://adminrules.idaho.gov/rules/current/16/160305.pdf
2. Cornell Law - Section 514: https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.05.514
3. Idaho DHW AABD page: https://healthandwelfare.idaho.gov/services-programs/financial-assistance/about-aabd-cash-assistance
4. SSA State Assistance Programs (2011): https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/id.html
