# Child Tax Credit (CTC)

## Overview

The Child Tax Credit provides tax relief to families with dependent children. PolicyEngine US models both the non-refundable and refundable (Additional Child Tax Credit) portions, including temporary expansions and phase-out calculations.

## Program Structure

### Credit Components

The CTC consists of two parts:
- **Non-refundable Credit**: Reduces tax liability up to the credit amount
- **Additional Child Tax Credit (ACTC)**: Refundable portion for families with insufficient tax liability

Credit structure varies by:
- Child's age (under 17 for regular CTC, under 18 for temporary expansions)
- Number of qualifying children
- Modified adjusted gross income
- Tax year (significant temporary changes in 2021)

### Phase-Out Structure

The credit phases out at higher income levels:
- Begins at income thresholds that vary by filing status
- Reduces by a fixed amount per increment of income over threshold
- Different phase-out rules applied to 2021 expansion amounts

## Modeled Variables

### Input Variables
- `age`: Child's age for qualification
- `is_tax_unit_dependent`: Dependency status
- Tax unit structure and relationships
- Modified AGI components

### Calculated Variables
- `ctc`: Total CTC amount (non-refundable + refundable)
- `ctc_maximum`: Maximum credit before phase-out
- `ctc_phase_out`: Amount of credit reduction
- `ctc_qualifying_children`: Count of eligible children
- `ctc_value`: Per-child credit amount
- `non_refundable_ctc`: Portion applied against tax liability
- `refundable_ctc`: Additional Child Tax Credit amount

### Temporary Expansion Variables (2021)
- `ctc_maximum_with_arpa_addition`: Enhanced maximum credit
- `ctc_phase_out_arpa`: Phase-out of expansion amount
- Advance payment modeling capabilities

### Not Currently Modeled
- Monthly advance payment reconciliation details
- Opt-out elections for advance payments
- Split custody arrangements between tax years
- Prior-year lookback provisions

## Legislative References

**Primary Authority**: Internal Revenue Code Section 24

**Key Modifications**:
- Tax Cuts and Jobs Act of 2017 (current structure)
- American Rescue Plan Act of 2021 (temporary expansion)
- Consolidated Appropriations Act provisions

## Program Interactions

The CTC interacts with other tax provisions:
- Coordinated with dependent exemptions (suspended 2018-2025)
- Cannot claim same child for CTC and other dependent credit
- Affects earned income requirement for refundable portion
- Included in various state tax credit calculations

## Qualifying Child Requirements

PolicyEngine US evaluates:
- **Age Test**: Under applicable age limit at year end
- **Relationship Test**: Child, stepchild, sibling, or descendant
- **Residency Test**: Lives with taxpayer for more than half the year
- **Support Test**: Does not provide more than half of own support
- **Citizenship Test**: U.S. citizen, national, or resident
- **Tax ID Requirement**: Valid SSN for child

## Data Considerations

The model handles:
- Automatic determination of qualifying children
- Proper allocation in split custody situations
- Integration with other dependent benefits
- Historical parameter values for all years