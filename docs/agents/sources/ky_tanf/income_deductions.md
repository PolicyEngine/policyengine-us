# Kentucky TANF (K-TAP) Income Deductions and Exclusions

## Source
- **Regulation**: 921 KAR 2:016 - Standards of need and amount for KTAP
- **Section**: Section 5 - Excluded Income and Deductions
- **URL**: https://apps.legislature.ky.gov/law/kar/titles/921/002/016/

## Overview

Per 921 KAR 2:016 Section 5: Gross non-KTAP income received or anticipated to be received shall be considered with the application of excluded income and deduction policy.

## Work Expense Standard Deduction

Per 921 KAR 2:016 Section 5(3)(a):

| Employment Type | Deduction Amount |
|-----------------|------------------|
| Full-time       | $175             |
| Part-time       | $175             |

**Purpose**: Covers mandatory paycheck deductions, union dues, and tools.

**Note**: This deduction applies to ALL employed individuals regardless of hours worked.

## Dependent Care Disregard

Per 921 KAR 2:016 Section 5(3)(b):

| Employment Type | Maximum Amount per Individual |
|-----------------|-------------------------------|
| Full-time       | $175/month                    |
| Part-time       | $150/month                    |
| Child under 2   | $200/month                    |

**Definitions**:
- **Full-time employment**: 30+ hours weekly or 130+ hours monthly
- **Part-time employment**: Less than 30 hours weekly or 130 hours monthly

**Note**: With the exception of certain circumstances pursuant to Section 5(3)(b), child care expenses incurred as a result of employment shall be paid pursuant to 922 KAR 2:160 (Child Care Assistance Program).

## Earned Income Disregard

Per 921 KAR 2:016 Section 5(3)(e):

| Disregard Type | Amount | Duration | Availability |
|----------------|--------|----------|--------------|
| Standard Disregard | 50% of remaining earned income | 6 months | Two-time only per adult |

**Details**:
- For six (6) months, the first fifty (50) percent of earned income not already deducted is disregarded for each member of the benefit group
- The six (6) months earnings disregard shall be consecutive and is at the option of the recipient
- This is available as a two (2) time only disregard per employed adult member of the benefit group

**New Employment Disregard**:
- For new employment, or increased wages, acquired after approval and reported timely
- Covers six (6) full calendar months earnings
- Two-time only disregard per employed adult

**Sanctions/Penalties**:
- If otherwise eligible, a sanctioned or penalized member of the benefit group may receive the six (6) months earnings disregard
- Deductions from earnings shall not apply for a month where the individual reduces, terminates, or refuses to accept employment within the period of thirty (30) days preceding such month, unless good cause exists

## Child Support Exclusion

Per 921 KAR 2:016 Section 5(2)(v):

| Exclusion | Amount |
|-----------|--------|
| Child support payment | First $50 |

The first fifty (50) dollars of child support payment received by the benefit group is excluded from income.

## Order of Deduction Application

For earned income, apply deductions in this order:

1. **Step 1**: Subtract Work Expense Standard Deduction ($175)
2. **Step 2**: Subtract Dependent Care Disregard (if applicable)
3. **Step 3**: Apply Earned Income Disregard (50% of remaining earned income)

### Calculation Example

**Given**:
- Gross earned income: $1,000/month
- Dependent care costs: $200/month (full-time employment)
- Child support received: $100/month

**Earned Income Calculation**:
1. Start with gross earned income: $1,000
2. Subtract work expense deduction: $1,000 - $175 = $825
3. Subtract dependent care (capped at $175 for full-time): $825 - $175 = $650
4. Apply 50% earned income disregard: $650 * 0.50 = $325
5. Countable earned income: $325

**Unearned Income Calculation**:
1. Start with child support: $100
2. Subtract child support exclusion: $100 - $50 = $50
3. Countable unearned income: $50

**Total Countable Income**: $325 + $50 = $375

## Implementation Notes for Simplified Model

### Simulatable Components
- Work expense standard deduction ($175)
- Dependent care disregard (up to $175/$150/$200 depending on employment and child age)
- Earned income disregard (50%)
- Child support exclusion ($50)

### Non-Simulatable Components (Architecture Limitations)
- **Duration tracking**: The 6-month duration of the earned income disregard cannot be enforced without historical tracking
- **Two-time limit**: The two-time only availability cannot be tracked without lifetime history
- **New employment disregard**: Requires tracking of employment start dates and prior disregard usage

### Simplified Implementation Approach
For a simplified implementation, apply the earned income disregard (50%) as if always available, with documentation noting:
- This assumes the recipient is within the 6-month disregard period
- The two-time lifetime limit is not enforced
- Actual benefits may vary based on case-specific circumstances

## Historical Values (Pre-2023)

For reference, values prior to the 2023 update:

| Deduction | Pre-2023 | Post-2023 |
|-----------|----------|-----------|
| Work Expense | $90 | $175 |
| Earned Income Disregard | $30 + 1/3 for 4 months, then $30 only for 8 months | 50% for 6 months |
| Child Support Exclusion | $50 | $50 (unchanged) |
