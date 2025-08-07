# Pell Grant

## Overview

The Pell Grant provides need-based financial aid to low-income undergraduate students to promote access to postsecondary education. PolicyEngine US models Pell Grant eligibility and award calculations based on Expected Family Contribution (EFC) or Student Aid Index (SAI).

## Program Structure

### Award Calculation

Pell Grant awards depend on:
- Financial need (EFC/SAI)
- Cost of attendance
- Full-time or part-time enrollment
- Full academic year or less

### Transition to SAI

The program transitioned from EFC to SAI:
- EFC used through 2023-24
- SAI begins 2024-25
- Similar concepts with formula changes

## Modeled Variables

### Input Variables
- Income and assets for need analysis
- Household size and composition
- Number in college
- `pell_grant_cost_of_attending_college`: School costs
- `pell_grant_months_in_school`: Enrollment duration

### Calculated Variables
- `pell_grant`: Annual grant amount
- `pell_grant_efc`: Expected Family Contribution
- `pell_grant_sai`: Student Aid Index
- `pell_grant_uses_efc`: EFC formula flag
- `pell_grant_uses_sai`: SAI formula flag

### Need Analysis Components
- `pell_grant_head_income`: Parent income
- `pell_grant_head_assets`: Parent assets
- `pell_grant_dependent_available_income`: Student income
- `pell_grant_head_contribution`: Parent contribution
- `pell_grant_dependent_contribution`: Student contribution

### Not Currently Modeled
- Verification requirements
- Satisfactory Academic Progress
- Lifetime eligibility limits
- Year-round Pell
- Iraq/Afghanistan Service Grants

## Legislative References

**Primary Authority**: Title IV of the Higher Education Act of 1965

**Key Regulations**: 34 CFR Part 690

**Major Changes**:
- FAFSA Simplification Act (transition to SAI)
- Various appropriations acts setting maximum awards

## Program Interactions

Pell Grants coordinate with:
- Other Title IV aid (loans, work-study)
- State grant programs
- Institutional aid
- Tax credits (AOTC, LLC)

## Eligibility Requirements

Basic requirements include:
- Undergraduate enrollment
- Satisfactory academic progress
- Valid Expected Family Contribution/SAI
- U.S. citizenship or eligible non-citizen
- High school diploma or equivalent

## Formula Types

PolicyEngine models both:
- **EFC Formula**: Traditional calculation
- **SAI Formula**: Simplified calculation
- Automatic zero EFC/SAI
- Simplified needs test

## Data Considerations

The model uses:
- Federal need analysis formulas
- Maximum grant schedules
- Cost of attendance assumptions
- Enrollment intensity factors