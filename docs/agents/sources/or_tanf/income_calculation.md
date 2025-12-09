# Oregon TANF Income Calculation

## Legal Authority
- **Definitions**: OAR 461-001-0000 - Definitions for Chapter 461
- **Earned Income Deduction**: OAR 461-160-0160 - Earned Income Deduction; REF, REFM, TANF
- **Earned Income Treatment**: OAR 461-145-0130 - Earned Income; Treatment
- **Self-Employment**: OAR 461-145-0910, OAR 461-145-0920, OAR 461-145-0930

## Key Definitions

### Countable Income
Income that is available and not excluded from consideration under program rules.

### Adjusted Income (OAR 461-001-0000)
The amount determined by subtracting income deductions from countable income:
```
Adjusted Income = Countable Income - Income Deductions
```

For TANF, the primary deduction is the earned income deduction.

## Earned Income Deduction (OAR 461-160-0160)

The earned income deduction for REF, REFM, and TANF programs is:

**50% of gross earned income** (including self-employment income)

```
Earned Income Deduction = 0.50 * Gross Earned Income
```

Therefore:
```
Adjusted Income = Countable Income - (0.50 * Gross Earned Income)
```

## Earned Income Treatment (OAR 461-145-0130)

### General Rule
Earned income is countable in determining eligibility.

### Exclusions from Earned Income

The following earned income is **excluded** for TANF:

1. **Student Income** - Earned income of dependent children and minor parents:
   - Under 19 years who are full-time students in grade 12 or below
   - Under 18 years attending school part-time and not employed full-time
   - Too young to attend school

2. **Welfare-to-Work Income** - First $260/month of work experience income in REF, REFM, and TANF programs

3. **In-Kind Income** - Earned in-kind income is excluded (with limited exceptions)

### JOBS Plus Treatment
- JOBS Plus income is excluded when determining ongoing eligibility
- Wages received after the last month of work are counted

### Income Remaining After Receipt
Income remaining after the month of receipt is treated as a resource, not income.

## Self-Employment Income (OAR 461-145-0910, 0920, 0930)

### Definition
The following are considered self-employed:
- Child care providers paid by the Department
- Adult foster home providers paid by the Department
- Realty agents
- Individuals who sell plasma, redeem beverage containers, pick mushrooms for sale, etc.

### Counting Self-Employment Income
- Self-employment income is counted **prospectively** to determine eligibility
- Use gross receipts and sales, including mileage reimbursements, before costs

### Cost Deductions (OAR 461-145-0920)
**IMPORTANT**: In the REF, REFM, and TANF programs, **no costs are subtracted** from self-employment income.

This means for TANF, gross self-employment receipts are used without any business expense deductions.

### Annualization
Self-employment income is annualized when:
- Received during less than 12 months but intended as full year's income
- Business has operated for a full year and previous year is representative

## Unearned Income

### Types Counted (OAR 461-145 series)

| Income Type | Treatment | Reference |
|-------------|-----------|-----------|
| Child Support | Countable (with disregard) | OAR 461-145-0080 |
| Spousal Support/Alimony | Countable | OAR 461-145-0505 |
| Social Security | Countable | OAR 461-145-0490 |
| SSI | Countable | OAR 461-145-0490 |
| Unemployment Benefits | Countable | OAR 461-145-0550 |
| Workers' Compensation | Countable | OAR 461-145-0580 |
| Veterans Benefits | Countable | OAR 461-145-0570 |
| Annuity Payments | Countable | OAR 461-145-0020 |
| Dividends/Interest/Royalties | Countable | OAR 461-145-0108 |

### Child Support Disregard (OAR 461-145-0080)

Current child support receives a partial disregard:
- Up to **$50 per dependent child per month**
- Maximum: **$200 per financial group per month**
- Applies to current child support only (not arrears)

**Note**: All child support, including passthrough amounts, is considered countable unearned income, but the disregard reduces the countable amount.

### In-Kind Income (OAR 461-145-0280)
- Unearned third-party payments that should legally be paid to a household member are countable
- Other in-kind income is generally excluded for TANF

## Benefit Calculation Formula

```
1. Calculate Gross Earned Income (including self-employment gross receipts)
2. Apply Earned Income Deduction: Deduction = 0.50 * Gross Earned Income
3. Calculate Countable Unearned Income (with child support disregard applied)
4. Calculate Countable Income = Gross Earned Income + Countable Unearned Income
5. Calculate Adjusted Income = Countable Income - Earned Income Deduction
6. Calculate Benefit = Payment Standard - Adjusted Income
7. Apply minimum benefit rule: If Benefit < $10, Benefit = $0
```

## Example Calculation

**Family of 3 with $1,000 gross earned income and $200 child support (1 child)**

1. Gross Earned Income: $1,000
2. Earned Income Deduction: $1,000 * 0.50 = $500
3. Child Support Disregard: $50 (for 1 child)
4. Countable Child Support: $200 - $50 = $150
5. Countable Income: $1,000 + $150 = $1,150
6. Adjusted Income: $1,150 - $500 = $650
7. Payment Standard (size 3): $506
8. Since Adjusted Income ($650) > Adjusted Income Limit ($485), family is NOT ELIGIBLE under standard rules

If eligible for ELI:
- ELI Standard (size 3): $1,012
- Since Countable Income ($1,150) > ELI Standard, family is NOT ELIGIBLE even under ELI

## References

- OAR 461-001-0000: https://oregon.public.law/rules/oar_461-001-0000
- OAR 461-160-0160: https://secure.sos.state.or.us/oard/displayDivisionRules.action?selectedDivision=2286
- OAR 461-145-0130: https://oregon.public.law/rules/oar_461-145-0130
- OAR 461-145-0080: https://oregon.public.law/rules/oar_461-145-0080
- OAR 461-145-0910: https://oregon.public.law/rules/oar_461-145-0910
