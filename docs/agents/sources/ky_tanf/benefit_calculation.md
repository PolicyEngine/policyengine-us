# Kentucky TANF (K-TAP) Benefit Calculation

## Source
- **Regulation**: 921 KAR 2:016 - Standards of need and amount for KTAP
- **URL**: https://apps.legislature.ky.gov/law/kar/titles/921/002/016/
- **Effective Date**: 2023 (major update from 1995 levels)

## Payment Standards by Family Size

Per 921 KAR 2:016 Section 9(2)(a):

| Family Size | Payment Maximum |
|-------------|-----------------|
| 1           | $372            |
| 2           | $450            |
| 3           | $524            |
| 4           | $656            |
| 5           | $766            |
| 6           | $864            |
| 7+          | $964            |

## Standard of Need by Family Size

Per 921 KAR 2:016 Section 9(2)(a):

| Family Size | Standard of Need |
|-------------|------------------|
| 1           | $481             |
| 2           | $552             |
| 3           | $631             |
| 4           | $710             |
| 5           | $790             |
| 6           | $869             |
| 7+          | $948             |

## Gross Income Eligibility Limits

Per 921 KAR 2:016 Section 9(2)(b):

| Family Size | Maximum Gross Income |
|-------------|----------------------|
| 1           | $890                 |
| 2           | $1,021               |
| 3           | $1,169               |
| 4           | $1,315               |
| 5           | $1,462               |
| 6           | $1,608               |
| 7+          | $1,754               |

**Eligibility Test**: If total gross income exceeds the gross income limitation standard, the benefit group shall be ineligible.

## Benefit Calculation Formula

Per 921 KAR 2:016 Section 9(3)-(4):

### Step-by-Step Calculation

1. **Calculate Gross Income**
   - Sum all earned and unearned income for the benefit group

2. **Apply Gross Income Test**
   - If gross_income > gross_income_limit: INELIGIBLE
   - Otherwise, continue to step 3

3. **Calculate Countable Income**
   - Start with gross income
   - Subtract excluded income (per Section 5(1) and 5(2))
   - Subtract applicable deductions (per Section 5(3))

4. **Calculate Deficit**
   ```
   deficit = standard_of_need - countable_income
   ```

5. **Apply 45% Ratable Reduction**
   ```
   reduced_benefit = deficit * 0.55
   ```
   (This is equivalent to applying a 45% reduction: deficit - (deficit * 0.45) = deficit * 0.55)

6. **Determine Final Benefit**
   ```
   benefit = min(reduced_benefit, payment_maximum)
   ```

### Formula Summary
```
If gross_income > gross_income_limit:
    benefit = 0
Else:
    countable_income = gross_income - excluded_income - deductions
    If countable_income >= standard_of_need:
        benefit = 0
    Else:
        deficit = standard_of_need - countable_income
        benefit = min(deficit * 0.55, payment_maximum)
```

## Worked Examples

### Example 1: Family of 3 with No Income
- Gross Income: $0
- Gross Income Limit (3): $1,169 - PASSES
- Excluded Income: $0
- Deductions: $0
- Countable Income: $0
- Standard of Need (3): $631
- Deficit: $631 - $0 = $631
- 55% of Deficit: $631 * 0.55 = $347.05
- Payment Maximum (3): $524
- Benefit: min($347.05, $524) = $347.05 (rounded as per state rules)

### Example 2: Family of 4 with Earned Income
- Gross Earned Income: $800/month
- Gross Income Limit (4): $1,315 - PASSES
- Work Expense Deduction: $175
- Earned Income Disregard (50%): ($800 - $175) * 0.50 = $312.50
- Total Deductions: $175 + $312.50 = $487.50
- Countable Income: $800 - $487.50 = $312.50
- Standard of Need (4): $710
- Deficit: $710 - $312.50 = $397.50
- 55% of Deficit: $397.50 * 0.55 = $218.63
- Payment Maximum (4): $656
- Benefit: min($218.63, $656) = $218.63

### Example 3: Family of 2 Over Gross Income Limit
- Gross Income: $1,100/month
- Gross Income Limit (2): $1,021
- Result: INELIGIBLE (gross income exceeds limit)

## Cost of Living Adjustments

Per 921 KAR 2:016, the payment maximum, gross income limit, and standard of need amounts are subject to cost of living adjustments determined by the Social Security Administration beginning in 2023, pursuant to 42 U.S.C. 415(i) and published at https://www.ssa.gov/cola/.

## Historical Comparison (Pre-2023 vs Post-2023)

| Parameter | Pre-2023 (1995 levels) | Post-2023 |
|-----------|------------------------|-----------|
| Payment Max (1 person) | $186 | $372 |
| Payment Max (3 persons) | $262 | $524 |
| Standard of Need (1) | $401 | $481 |
| Standard of Need (3) | $526 | $631 |
| Gross Income Limit (1) | $742 | $890 |
| Gross Income Limit (3) | $974 | $1,169 |

The 2023 update effectively doubled benefit amounts to account for inflation since 1995.
