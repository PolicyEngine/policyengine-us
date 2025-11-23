# Indiana TANF - Benefit Calculation

## Legal Authority

- **Indiana Code**: IC 12-14-2-5.1 (Time Limitations; Cash Assistance Minimum)
- **Administrative Code**: 470 IAC 10.3-4 (Fiscal Eligibility Requirements)
- **Policy Manual**: Chapter 2800 (Income)

## Payment Standards (2024)

### Maximum Monthly Benefit Amounts

| Family Size | Maximum Benefit | Notes |
|-------------|-----------------|-------|
| 1 | $248 | Single child or adult |
| 2 | $409 | One adult + one child |
| 3 | $513 | Standard family size |
| 4 | $617 | |
| 5 | $721 | |
| 6 | $825 | |
| 7 | $929 | |
| 8 | $1,033 | |
| 9 | $1,137 | |
| 10 | $1,241 | Maximum documented |

**Pattern**: Increases by $104 per additional family member from size 3 onward.

**Source**:
- FSSA website: https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/
- Current as of November 2024

## Benefit Calculation Formula

### Basic Formula

```
TANF Benefit = Maximum Payment Standard - Countable Income
```

Where:
- **Maximum Payment Standard** = Family size-based amount from table above
- **Countable Income** = Income after applying deductions and disregards

### Countable Income Calculation

```
Countable Income = (Gross Earned Income × 0.25) + (Gross Unearned Income × 1.0)
```

This reflects:
- **75% earned income disregard** (only 25% counted)
- **100% unearned income counting** (no disregard for benefit calculation)

**Source**:
- WIOA State Plan: https://wioaplans.ed.gov/node/67731
- Policy Manual Chapter 2800: https://www.in.gov/fssa/dfr/files/2800.pdf

## Benefit Calculation Process

### Step-by-Step Process

**Step 1: Determine Gross Earned Income**
- Wages from employment
- Self-employment income
- After work expense deduction (details in Policy Manual PDF)

**Step 2: Determine Gross Unearned Income**
- Unemployment benefits
- Social Security benefits
- Child support (counted as child's income)
- Other unearned income sources

**Step 3: Apply Income Disregards**

For earned income:
```
Countable Earned Income = Gross Earned Income × 0.25
```

For unearned income:
```
Countable Unearned Income = Gross Unearned Income × 1.0
```

**Step 4: Calculate Total Countable Income**
```
Total Countable Income = Countable Earned Income + Countable Unearned Income
```

**Step 5: Determine Maximum Payment Standard**
- Based on family size from payment standards table

**Step 6: Calculate TANF Benefit**
```
TANF Benefit = Maximum Payment Standard - Total Countable Income
```

If result is negative or zero, family receives no TANF cash assistance.

## Example Calculation

**Example Family:**
- Family size: 3 (1 adult, 2 children)
- Gross earned income: $400/month
- Gross unearned income: $0/month

**Calculation:**

1. **Countable Earned Income**: $400 × 0.25 = $100
2. **Countable Unearned Income**: $0 × 1.0 = $0
3. **Total Countable Income**: $100 + $0 = $100
4. **Maximum Payment Standard** (family of 3): $513
5. **TANF Benefit**: $513 - $100 = **$413**

## Historical Benefit Amounts

### Timeline of Increases

| Period | Family of 3 Benefit | % of FPL | Change |
|--------|--------------------|-----------| -------|
| 1996-2022 | $288 | ~13% | No change for 26 years |
| 2022-2023 | $320 | ~15% | +$32 (first increase ever) |
| 2024+ | $513 | ~24% | +$193 (SEA 265 impact) |

**Context**:
- Indiana had not increased TANF benefits since program creation in 1996
- SEA 265 (2023) provided first significant increase
- Current $513 represents 78% increase from historical $288 amount

**Sources**:
- NCCP Profile: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Indiana.pdf
- CBPP Report: https://www.cbpp.org/research/income-security/continued-increases-in-tanf-benefit-levels-are-critical-to-helping
- News coverage of SEA 265

## Future Benefit Adjustments

### Cost of Living Adjustments (SEA 265)

**Provision**:
- Senate Enrolled Act 265 requires yearly cost-of-living adjustments
- Methodology not specified in accessible sources
- First adjustments expected after July 2025

**Implementation Unknown**:
- Specific adjustment formula not found
- May tie to CPI, FPL, or other index
- Details may be in implementing regulations or State Plan PDF

**Source**: Senate Enrolled Act 265 (2023)

## Actual Payment Statistics

### Average Payments

**April 2024:**
- Average payment per case: $229.03
- Average payment per recipient: $107.52

**March 2025:**
- Average payment per case: $401.39
- Represents 74.94% increase from March 2024

**Note**: Average payments are lower than maximum benefits because most families have some countable income that reduces their benefit amount.

**Source**: Indiana Monthly Management Reports
- April 2024: https://www.in.gov/fssa/dfr/files/MMR-STATEWIDE-en-us-Apr-2024.pdf
- March 2025: https://www.in.gov/fssa/dfr/files/MMR-STATEWIDE-en-usMARCH2025.pdf

## Benefit Structure Comparison

### Indiana vs. Federal Baseline

**Indiana Structure:**
- Direct subtraction formula: Max benefit - countable income
- **NOT** percentage of FPL
- **NOT** needs-based test

**Comparison to Other States:**

| State | Structure Type | Notes |
|-------|---------------|-------|
| Indiana | Direct Subtraction | Max - countable income |
| Montana | Needs Test | Income vs. budgetary needs |
| Federal SNAP | Direct Subtraction | Similar to Indiana TANF |

**Implementation Note**: Indiana TANF follows simpler direct subtraction model, unlike states with complex needs-based tests.

## Minimum Benefit

**No Minimum Benefit Found**:
- No minimum benefit amount specified in accessible sources
- If countable income ≥ maximum payment standard, benefit = $0
- Family would lose eligibility if income exceeds limits

**Note**: IC 12-14-2-5.1 references "cash assistance minimum" but text not accessible.

## Maximum Benefit Cap

**No Additional Cap**:
- Maximum benefit is the payment standard for family size
- No household caps beyond family size limits
- Largest documented family size: 10 persons ($1,241/month)

## Special Benefit Provisions

### Pregnant Women

**SEA 265 Addition**:
- Pregnant women (6+ months) now eligible
- Benefit calculation follows same formula
- Counted as household member for payment standard determination

### Child Support Impact

**Treatment in Benefit Calculation**:
- Child support counted as unearned income
- Attributed to child, not parent
- No disregard for benefit calculation (counted 100%)
- Child support collected by state retained for cost recovery

**No Passthrough Identified**:
- No child support passthrough or disregard found in sources
- State Plan PDF may contain additional details

**Source**:
- Policy Manual Chapter 2800: https://www.in.gov/fssa/dfr/files/2800.pdf
- DCS Child Support: https://www.in.gov/dcs/child-support/custodial-party-information/tanf-benefits-and-child-support/

## Implementation in PolicyEngine

### Parameters Needed

```yaml
# in_tanf_payment_standard.yaml
in_tanf:
  payment_standard:
    2024-01-01:
      1: 248
      2: 409
      3: 513
      4: 617
      5: 721
      6: 825
      7: 929
      8: 1_033
      9: 1_137
      10: 1_241
    reference:
      - title: "Indiana FSSA - TANF Payment Standards"
        href: "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/"
```

### Variables Needed

**in_tanf_countable_income:**
```python
def formula(tax_unit, period, parameters):
    # Get income components
    earned = tax_unit("in_tanf_countable_earned_income", period)
    unearned = tax_unit("in_tanf_countable_unearned_income", period)

    # Apply disregards
    countable_earned = earned * 0.25  # 75% disregard
    countable_unearned = unearned * 1.0  # No disregard

    return countable_earned + countable_unearned
```

**in_tanf_benefit_amount:**
```python
def formula(tax_unit, period, parameters):
    p = parameters(period).gov.states.in.tanf

    # Get household size
    household_size = tax_unit("household_size", period)

    # Get maximum payment standard
    max_benefit = p.payment_standard[household_size]

    # Get countable income
    countable_income = tax_unit("in_tanf_countable_income", period)

    # Calculate benefit
    benefit = max_(max_benefit - countable_income, 0)

    return benefit
```

## Outstanding Questions

### Earned Income Disregard Methodology

**Conflicting Information:**

**Version 1 (from WIOA State Plan):**
- 75% disregard for benefit calculation
- $30 and 1/3 disregard for eligibility (first 4 months)

**Version 2 (from NCCP Profile):**
- $120 + 1/3 remaining earnings (months 1-4)
- $120 of earnings (months 5-12)
- $90 of earnings (months 13+)

**Resolution Needed**:
- Extract Policy Manual Chapter 2800 PDF
- Determine if both methods apply (one for eligibility, one for benefit)
- Or if one method has been superseded

### Cost of Living Adjustment Formula

**Unknown:**
- Specific adjustment methodology
- Inflation index used (CPI, FPL, other)
- Timing of annual adjustments
- Rounding methodology

**Source for Resolution**:
- Implementing regulations
- State Plan PDF
- Future policy updates

### Benefit Calculation Edge Cases

**Questions:**
- How are benefits prorated for partial months?
- How are benefits adjusted mid-month for income changes?
- Are there benefit supplements for special circumstances?

**Source for Resolution**: Policy Manual Chapter 2800 PDF

## References

```yaml
# For benefit calculation parameters:
reference:
  - title: "Indiana FSSA - TANF Payment Standards"
    href: "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/"
  - title: "SNAP/TANF Program Policy Manual Chapter 2800 - Income"
    href: "https://www.in.gov/fssa/dfr/files/2800.pdf"
```

```python
# For benefit calculation variables:
reference = "470 IAC 10.3-4"
documentation = "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/"
```

## Next Steps

1. **Extract Policy Manual Chapter 2800** to resolve income disregard methodology
2. **Verify payment standard increments** for family sizes > 10
3. **Confirm cost of living adjustment methodology** from implementing regulations
4. **Review State Plan PDF** for benefit calculation examples
5. **Create YAML tests** with various income scenarios
