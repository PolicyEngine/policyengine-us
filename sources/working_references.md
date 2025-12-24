# Collected Documentation

## Nebraska Aid to Dependent Children (ADC) - TANF Implementation
**Collected**: 2025-12-23
**Implementation Task**: Implement Nebraska ADC (TANF) cash assistance program

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Aid to Dependent Children (ADC)
**Abbreviation**: ADC
**Source**: Nebraska Revised Statutes Section 43-512, Title 468 NAC

**Variable Prefix**: `ne_adc`

---

## Regulatory Authority

### Primary Legal Sources

1. **Nebraska Revised Statutes**
   - Section 43-504: Definition of dependent child (age requirements)
   - Section 43-512: ADC application, payment level (55% of Standard of Need)
   - Section 43-513: Standard of Need, CPI adjustment methodology
   - Section 68-1713: Welfare Reform Act implementation requirements
   - Section 68-1726: Earned income disregard, resource limits, eligibility factors

2. **Nebraska Administrative Code Title 468**
   - Chapter 1: General Background
   - Chapter 2: Eligibility Requirements
   - Chapter 3: Calculation of ADC Benefits
   - Chapter 4: Employment First Self-Sufficiency Program
   - Chapter 5: Emergency Assistance to Needy Families with Children

### Source URLs

- Nebraska DHHS TANF Page: https://dhhs.ne.gov/Pages/TANF.aspx
- Title 468 Overview: https://dhhs.ne.gov/Pages/Title-468.aspx
- Statute 43-504: https://nebraskalegislature.gov/laws/statutes.php?statute=43-504
- Statute 43-512: https://nebraskalegislature.gov/laws/statutes.php?statute=43-512
- Statute 43-513: https://nebraskalegislature.gov/laws/statutes.php?statute=43-513
- Statute 68-1713: https://nebraskalegislature.gov/laws/statutes.php?statute=68-1713
- Statute 68-1726: https://nebraskalegislature.gov/laws/statutes.php?statute=68-1726

---

## Demographic Eligibility

### Eligible Children (468 NAC 2-007, Neb. Rev. Stat. 43-504)

**Age Thresholds:**
- Children under age 19 meeting specific residency and support conditions (per 43-504)
- In practice for ADC cash assistance:
  - Children age 18 or younger
  - Children age 18 who are full-time students in secondary school (or equivalent vocational/technical training) and reasonably expected to complete before age 19
  - **Note**: College-level education does NOT qualify for the extended age limit

**Pregnancy:**
- Unborn children are counted beginning the first day of the month of the mother's third trimester
- Pregnant women in final trimester qualify as "families with dependent children"
- Pregnancy must be medically verified
- Even for twins/multiples, ADC grant only reflects needs of ONE unborn child (Medical Assistance can reflect multiples)

**Source**: 468 NAC 2-007, 3-004; Neb. Rev. Stat. 43-504
- https://nebraskalegislature.gov/laws/statutes.php?statute=43-504
- https://public-dhhs.ne.gov/nfocus/Manuals/APX468/apx468/eligibility_of_a_pregant_woman_for_a_grant.htm

### Deprivation Requirement - NONE

**IMPORTANT**: Nebraska does NOT require deprivation of parental support or care as an eligibility factor. Unmarried parents living together as a family are considered a family unit when paternity has been acknowledged or established.

This is notable as many states require demonstration of parental absence, incapacity, or unemployment.

**Source**: Nebraska DHHS TANF documentation

### Implementation Approach

- [ ] Use federal demographic eligibility (if age thresholds match federal 18/19)
- [x] Create state-specific age thresholds (Nebraska has specific student requirements - secondary school only, not college)

---

## Immigration Eligibility

**Implementation approach:**
- [x] Use federal immigration eligibility (state follows federal rules)
- Nebraska requires U.S. citizenship or qualifying alien status per 468 NAC 2-002
- Any individual born in the United States is considered a U.S. citizen (including children of undocumented parents)

**Source**: 468 NAC 2-002

---

## Resource Limits

### Limits by Unit Size (Neb. Rev. Stat. 68-1726, 68-1713)

| Unit Size | Resource Limit |
|-----------|----------------|
| 1 person | $4,000 |
| 2+ persons | $6,000 |

### Excluded Resources

- Primary home and furnishings
- Primary automobile (one vehicle per family - value excluded)
- Cash value of life insurance policies
- Up to $3,000 set aside for burial (pre-need burial trust or insurance policy)
- School grants, scholarships, vocational rehabilitation payments
- Job Training Partnership Act payments
- Education-related loans expected to be repaid

### Counted Resources

- Cash on hand
- Money in checking and savings accounts
- Savings certificates
- Stocks or bonds
- Credit card company gift card balances
- Nonrecurring lump sum payments
- Any burial funds over $3,000

**Source**: Nebraska Revised Statutes 68-1726, 68-1713; 468 NAC 2 (Resources)
- https://nebraskalegislature.gov/laws/statutes.php?statute=68-1726
- https://nebraskalegislature.gov/laws/statutes.php?statute=68-1713

---

## Income Eligibility Tests

### Test 1: Initial Eligibility (Standard of Need Test)

For initial ADC eligibility, the family's **net earned income** must be below the **Standard of Need** for their unit size.

**Earned Income Disregard for Applicants**: 20% of gross earned income
**Source**: Neb. Rev. Stat. 68-1726(3)(a)(i)

### Test 2: Ongoing Eligibility

For ongoing recipients:
**Earned Income Disregard**: 50% of gross earned income
**Source**: Neb. Rev. Stat. 68-1726(3)(a)(ii)

### Test 3: Transitional Eligibility (185% FPL Test)

If a family's income increases above the Standard of Need but remains below **185% of the Federal Poverty Level** for their unit size, the family may remain eligible for up to 5 months of transitional ADC grants.

**Source**: 468 NAC 2-024.01

---

## Income Disregards and Deductions

### Earned Income Disregard (Neb. Rev. Stat. 68-1726)

| Status | Disregard Rate | Level |
|--------|----------------|-------|
| Applicants (initial eligibility testing) | 20% of gross earned income | Per GROUP |
| Recipients (after eligibility established) | 50% of gross earned income | Per GROUP |

**Legal Citation**: Neb. Rev. Stat. 68-1726(3)(a):
> "(i) Twenty percent of gross earned income shall be disregarded to test for eligibility during the application process for aid to dependent children assistance; and
> (ii) For aid to dependent children program participants and for applicants after eligibility has been established, fifty percent of the gross earned income shall be disregarded"

**Source**: https://nebraskalegislature.gov/laws/statutes.php?statute=68-1726

### Child Care Disregard

A child care disregard is applied "when appropriate" according to 468 NAC documentation. The specific amount or methodology is documented in the Title 468 PDF.

**Note**: Families receiving ADC are eligible for child care subsidy at no cost.

### Income Exclusions

The following are NOT counted as income:
- Financial assistance intended for books, tuition, or self-sufficiency related expenses
- School grants and scholarships
- Vocational rehabilitation payments
- Job Training Partnership Act payments
- Education-related loans expected to be repaid
- Income earned by children attending school (excluded from family income)

**Source**: Neb. Rev. Stat. 68-1726

---

## Child Support Treatment

### Current Rules (Until June 30, 2027)

- Child support is assigned to the state when receiving ADC
- If average monthly child support collection exceeds the ADC payment amount, the case is closed
- Child support is either:
  - Compared to budgetary need (if less than need, it's assigned and doesn't count)
  - Counted as unearned income (if greater than need, case closes)

### LB233 - Child Support Passthrough (Effective July 1, 2027)

Beginning July 1, 2027, Nebraska will implement a child support passthrough:
- **$100 passthrough** for families with ONE child
- **$200 passthrough** for families with TWO or more children
- Passthrough amount is **disregarded** when calculating ADC eligibility and benefits

**Source**:
- https://www.nebraskalegislature.gov/bills/view_bill.php?DocumentID=50212
- LB233 passed 46-0 on April 11, 2024

---

## Income Standards

### Standard of Need (468 NAC 3, Statute 43-513)

The Standard of Need is the initial income test in ADC "gap" budgeting. It represents the monthly combined cost of food, clothing, sundries, home supplies, utilities, laundry, and shelter including taxes and insurance.

**Effective July 1, 2021** (values adjusted biennially per CPI):

| Unit Size | Standard of Need |
|-----------|------------------|
| 1 | $601 |
| 2 | $741 |
| 3 | $881 |
| 4 | $1,021 |
| 5 | $1,161 |
| 6 | $1,301 |
| 7 | $1,441 |
| 8 | $1,581 |
| 9 | $1,721 |
| 10 | $1,861 |
| Each additional person | +$140 |

**CPI Adjustment**: Values are adjusted biennially (every 2 years) on July 1, using the Consumer Price Index (CPI) for the previous two calendar years, per statute 43-513.

**Note**: Values shown are from July 1, 2021 adjustment. Some sources indicate these may have been updated. The formula is:
- Base (1 person): $601
- Each additional person: +$140

**Source**: Nebraska Appleseed chart; Neb. Rev. Stat. 43-513; 468 NAC 3
- https://neappleseed.org/wp-content/uploads/2023/03/Chart_-ADC-Standard-of-Need-and-Payment-Maximum.pdf
- https://dhhs.ne.gov/Documents/468-000-209.pdf

### Payment Standard (Maximum Benefit)

Effective **September 1, 2015**, the maximum ADC payment is **55% of the Standard of Need** (Neb. Rev. Stat. 43-512).

| Unit Size | Standard of Need | Payment Standard (55%) |
|-----------|------------------|------------------------|
| 1 | $601 | $331 |
| 2 | $741 | $408 |
| 3 | $881 | $485 |
| 4 | $1,021 | $562 |
| 5 | $1,161 | $639 |
| 6 | $1,301 | $716 |
| 7 | $1,441 | $793 |
| Each additional person | +$140 | +$77 |

**Payment Standard Rate**: 0.55 (55%)

**Note**: There has been legislative effort (LB 310) to increase the maximum ADC payment from 55% to 85% of standard of need, but as of this documentation, 55% remains in effect.

**Source**: Neb. Rev. Stat. 43-512; Nebraska Appleseed chart

---

## Benefit Calculation

### Gap Budgeting Methodology (468 NAC 3, Neb. Rev. Stat. 68-1713)

Nebraska uses "Budget the Gap" methodology:

**Step 1**: Calculate **Net Earned Income**:
- For applicants: Gross Earned Income x (1 - 0.20) = Gross Earned Income x 0.80
- For recipients: Gross Earned Income x (1 - 0.50) = Gross Earned Income x 0.50
- Subtract child care disregard if applicable

**Step 2**: Calculate **"Gap"**:
- Gap = Standard of Need - Net Earned Income

**Step 3**: Determine **Benefit Amount**:
- Benefit = min(Gap, Payment Standard)

**Step 4**: Subtract **Unearned Income**:
- Final Benefit = Benefit - Unearned Income

**Step 5**: Apply **Minimum Payment Rule**:
- No payments less than $10/month (except for overpayment recovery)

**Legal Citation**: Neb. Rev. Stat. 68-1713(1)(p): "Budget the Gap Methodology Whereby Countable Earned Income is Subtracted from the Standard of the Need and Payment is Based on the Difference or Maximum Payment Level, Whichever is Less"

**Source**: https://nebraskalegislature.gov/laws/statutes.php?statute=68-1713

---

## Transitional Grants (468 NAC 2-024.01)

### Eligibility Requirements

Families may receive up to **5 transitional grants** if they:
1. Lost ADC eligibility specifically due to increased earnings or hours of employment
2. Qualify for Transitional Medical Assistance (TMA)
3. Actually received an ADC grant in the month immediately before losing eligibility
4. Received or were eligible for grants in at least 3 of the 6 months preceding ineligibility

### Grant Amount

Each transitional grant equals **1/5 of the ADC Payment Standard** for the family's size.

### Ongoing Requirements

To continue receiving transitional grants, families must:
- Maintain earned income not exceeding **185% of the Federal Poverty Level**
- Maintain active employment
- Remain Nebraska residents
- Include a dependent child
- Remain ineligible for regular ADC grants

**Source**: https://publictest-dhhs.ne.gov/nfocus/stg/Manuals/NAC468/nac468/2_024_01_transitional_grant.htm

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limits - CANNOT ENFORCE

- **60-Month Lifetime Limit**: ADC families where parent(s) are capable of attaining independence are limited to 60 months of cash assistance in a lifetime
- **Exception**: Families where adults are not the parent of the child, or parent is disabled/unable to work, are NOT time-limited
- **Hardship Review**: After 56 months, recipients participate in a hardship review; if hardship is found, one 3-month extension may be granted

**Note**: PolicyEngine's single-period architecture cannot track lifetime benefit receipt.

### Work Requirements - NOT MODELED

Nebraska's Employment First (EF) program requires participation for work-eligible adults. This is not modeled in PolicyEngine.

### Waiting Periods - CANNOT TRACK

- Redetermination every 6 months
- Transitional benefit requirements for prior receipt

---

## Summary of Implementation Parameters

### Parameters to Create

| Parameter | Value | Unit | Source |
|-----------|-------|------|--------|
| Standard of Need (base, 1 person) | 601 | USD/month | 43-513, 468 NAC 3 |
| Standard of Need (additional person) | 140 | USD/month | 43-513, 468 NAC 3 |
| Payment Standard Rate | 0.55 | rate | 43-512 |
| Earned Income Disregard (applicant) | 0.20 | rate | 68-1726(3)(a)(i) |
| Earned Income Disregard (recipient) | 0.50 | rate | 68-1726(3)(a)(ii) |
| Resource Limit (1 person) | 4_000 | USD | 68-1726 |
| Resource Limit (2+ persons) | 6_000 | USD | 68-1726 |
| Minimum Payment | 10 | USD/month | 43-512 |
| Minor Child Age Threshold | 18 | years | 468 NAC 2-007, 43-504 |
| Student Age Threshold | 19 | years | 468 NAC 2-007, 43-504 |
| Transitional Eligibility FPL Rate | 1.85 | rate | 468 NAC 2-024.01 |
| Child Support Passthrough (1 child) | 100 | USD/month | LB233 (eff. 2027-07-01) |
| Child Support Passthrough (2+ children) | 200 | USD/month | LB233 (eff. 2027-07-01) |

---

## Simplified Implementation Approach

Given the complexity of Nebraska ADC with applicant vs. recipient distinctions, consider implementing:

1. **Simplified version**: Use recipient disregard rate (50%) for all cases
   - This is more generous and represents ongoing eligibility
   - Avoids needing to track applicant vs. recipient status

2. **Full version**: Implement both rates with a parameter or variable to distinguish

**Recommendation**: Start with simplified version using 50% disregard for initial implementation.

---

## References for Metadata

### For Parameters

```yaml
reference:
  - title: Nebraska Revised Statutes 43-512
    href: https://nebraskalegislature.gov/laws/statutes.php?statute=43-512
  - title: Nebraska Revised Statutes 68-1726
    href: https://nebraskalegislature.gov/laws/statutes.php?statute=68-1726
```

### For Variables

```python
reference = "https://nebraskalegislature.gov/laws/statutes.php?statute=43-512"
# or for regulations:
reference = "https://dhhs.ne.gov/Pages/Title-468.aspx"
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Title 468 - Aid to Dependent Children (Complete)**
   - URL: https://dhhs.ne.gov/Documents/Title-468-Complete.pdf
   - Expected content: Complete ADC regulations including detailed benefit calculation, child care disregard amounts, all eligibility rules
   - Note: This is the authoritative source for Nebraska ADC regulations

2. **Title 468 Guidance Document**
   - URL: https://dhhs.ne.gov/Guidance%20Docs/Title%20468%20-%20Aid%20to%20Dependent%20Children.pdf
   - Expected content: Implementation guidance for ADC program

3. **ADC Standard of Need and Payment Maximum Chart**
   - URL: https://neappleseed.org/wp-content/uploads/2023/03/Chart_-ADC-Standard-of-Need-and-Payment-Maximum.pdf
   - Expected content: Current Standard of Need and Payment Maximum amounts by household size
   - Key information: Standard of Need table with payment standards

4. **Nebraska TANF State Plan 2024**
   - URL: https://dhhs.ne.gov/Documents/Nebraska-State-TANF-Plan-2024.pdf
   - Expected content: Current TANF state plan with benefit methodology, eligibility criteria

5. **468-000-209 Appendix Material**
   - URL: https://dhhs.ne.gov/Documents/468-000-209.pdf
   - Expected content: Standard of Need charts, effective July 1, 2021

6. **Nebraska TANF Expenditures Report 2024**
   - URL: https://nebraskalegislature.gov/pdf/reports/fiscal/2024_tanf_report.pdf
   - Expected content: TANF fund usage and program statistics

---

## Open Questions for Implementation

1. **Child Care Disregard Amount**: The specific child care disregard amount/methodology needs to be confirmed from Title 468 PDF
2. **Current Standard of Need Values**: Values may have been adjusted since July 2021 per CPI methodology - need to verify current amounts
3. **Simplified vs Full Implementation**: Decision on whether to implement applicant/recipient distinction or use single rate
4. **Unearned Income Treatment**: Current child support assignment rules vs. future passthrough (2027)
