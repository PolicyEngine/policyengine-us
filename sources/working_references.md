# Collected Documentation

## Idaho TAFI (Temporary Assistance for Families in Idaho) Implementation
**Collected**: 2025-12-25
**Implementation Task**: Implement Idaho TANF program (TAFI) for PolicyEngine-US

---

## Official Program Name

**Federal Program**: TANF (Temporary Assistance for Needy Families)
**State's Official Name**: TAFI (Temporary Assistance for Families in Idaho)
**Abbreviation**: TAFI
**Source**: IDAPA 16.03.08.001 - Title, Scope, and Purpose

**Variable Prefix**: `id_tafi`

---

## Regulatory Authority

### Primary Legal Authority
- **Title**: IDAPA 16.03.08 - Temporary Assistance for Families in Idaho (TAFI) Program
- **Citation**: Idaho Administrative Procedure Act, Title 16, Chapter 03, Section 08
- **URL**: https://www.law.cornell.edu/regulations/idaho/title-IDAPA-16/rule-16.03.08
- **Effective Date**: March 17, 2022 (most recent revision)

### Administering Agency
- Idaho Department of Health and Welfare

---

## Demographic Eligibility

### Age Thresholds
- **Dependent Child**: Under age 18
- **Source**: IDAPA 16.03.08.010 - "A child under the age of eighteen (18)"

### Household Composition (IDAPA 16.03.08.125)
Mandatory household members include:
1. **Children**: Under age 18, residing with parent or caretaker relative
2. **Parents**: Parents with an eligible child residing with them
3. **Pregnant Women**: In at least the third calendar month before due date, unable to work due to medical reasons
4. **Spouses**: Individuals related by marriage to another mandatory household member

### Individuals Excluded from Household Size (IDAPA 16.03.08.240)
- Ineligible non-citizens
- Drug-related felony convictions (after August 22, 1996)
- Fleeing felons
- Probation/parole violators
- Fraudulent residency misrepresentation (10-year exclusion)
- Children receiving SSI

**Implementation Approach:**
- [x] Use federal demographic eligibility (age threshold matches federal at 18)
- [x] Use federal immigration eligibility (follows federal rules)

---

## Immigration/Citizenship Eligibility (IDAPA 16.03.08.131)

Eligible categories:
1. U.S. Citizen
2. U.S. National (American Samoa or Swains Island)
3. Active duty military, veterans, and their families (meeting qualified non-citizen definition)
4. Non-citizens who entered before August 22, 1996 with qualified status
5. Refugees, asylees, deportation withholding, Amerasian immigrants, Cuban/Haitian entrants (7 years from entry)
6. Qualified non-citizens with 5+ years of status
7. Trafficking victims (under 18 or HHS-certified)
8. Afghan and Iraqi special immigrants

**Implementation Approach:**
- [x] Use federal immigration eligibility (state follows federal rules)

---

## Resource Eligibility

### Resource Limit (IDAPA 16.03.08.200)
- **Limit**: $5,000
- **Legal Quote**: "The total of the entire household's countable resources must not be greater than five thousand dollars ($5,000) in any month."
- **Effective Date**: March 17, 2022

### Countable Resources (IDAPA 16.03.08.201)
Resources are countable when:
- Household has legal interest in the resource
- Household can take action to obtain or dispose of the resource
- Value = Fair market value minus liens, mortgages, or encumbrances (except vehicles)

### Vehicle Rules (IDAPA 16.03.08.207)
- **One vehicle per adult excluded**: Each adult may exclude their highest-valued vehicle
- **Additional vehicles**: Counted per federal Food Stamp Program rules (7 CFR 273.8)
- **Recreational vehicles**: Fully counted toward resource limit

### Resource Exclusions (IDAPA 16.03.08.208)
1. Home and surrounding land/buildings
2. Household goods (furniture, appliances, cooking utensils)
3. Personal effects (clothing, jewelry, personal care items)
4. One building lot and one partially built home
5. Temporarily unoccupied home (employment, training, medical, disaster)
6. Home loss/damage insurance (12 months from receipt)
7. Income-producing property (annual income consistent with FMV)
8. Business equipment (used or expected within 1 year)
9. Contracts (mortgages, promissory notes, sales contracts)
10. Life insurance (cash surrender value only)
11. Native American payments
12. Funeral agreements (irrevocable, cash value)
13. Education accounts
14. Retirement/tax-preferred accounts

---

## Income Eligibility

### General Rule (IDAPA 16.03.08.214)
"All earned and unearned income is counted in determining eligibility and grant amount, unless specifically excluded by rule."

### Eligibility Determination (IDAPA 16.03.08.221)
"To determine initial and continuing eligibility, the countable monthly income that is or will be available to the household is used in the calculation of the grant."

**Note**: Idaho TAFI does NOT have a separate gross income eligibility test. Eligibility is determined through the benefit calculation - if the calculated benefit is $10 or more, the family is eligible.

### Countable Income Sources
**Earned Income:**
- Wages, tips, salary
- Commissions, bonuses
- Self-employment income
- Any income defined as earnings by the IRS

**Unearned Income:**
- Interest, dividends
- Social Security benefits
- Child support (except assigned or non-recurring)
- Retirement income
- Any income from sources other than employment

### Self-Employment Income (IDAPA 16.03.08.229, 16.03.08.231)
- **Definition**: Income from a sole proprietorship (business owned by one person)
- **Standard Deduction**: 50% of gross monthly self-employment income
- **Alternative**: Actual expenses if they exceed standard deduction (requires documentation)

**Non-Allowable Self-Employment Expenses:**
- Net losses from prior tax years
- Income taxes (federal, state, local)
- Retirement savings
- Work-related personal expenses (commuting)
- Depreciation

---

## Income Deductions & Exemptions

### Earned Income Disregard (IDAPA 16.03.08.252)
- **Disregard Rate**: 60% of gross earned income
- **Effect**: Only 40% of gross earned income is counted against benefits
- **Legal Quote**: "subtracting sixty percent (60%) of gross earned income"

### Excluded Income (IDAPA 16.03.08.215)
The following 40 income types are excluded:

1. Supportive services payments
2. Work-related reimbursements
3. **Dependent child's school attendance earnings** (student disregard)
4. Assigned or non-recurring child support
5. Child SSI income
6. Loans with written repayment agreements
7. Third-party payments on household behalf
8. Money gifts up to $100 per person per event
9. Retroactive TAFI grant corrections
10. Social Security overpayment withholdings
11. Bank account interest
12. State and federal income tax refunds
13. EITC payments
14. Disability insurance taxes and attorney fees
15. Sales contract taxes and insurance
16. Foster care payments
17. Adoption assistance payments
18. Food commodities and stamps
19. Child nutrition benefits
20. Elderly nutrition benefits (Title VII)
21. Low Income Energy Assistance Act benefits
22. Home energy assistance payments
23. Utility reimbursement payments
24. Housing subsidies from agencies
25. HUD escrow account interest
26. Native American ancestry payments
27. Educational loans, grants, scholarships, veterans' benefits
28. College work-study income
29. VA educational assistance
30. Senior volunteer program payments
31. Relocation assistance payments
32. Disaster relief assistance
33. Radiation exposure compensation
34. Agent Orange settlements
35. Spina bifida veteran children allowances
36. Japanese-American WWII restitution
37. VISTA program payments
38. Subsidized employment wages
39. Temporary Census Bureau employment (up to 6 months)
40. Income excluded by federal law

---

## Income Standards

### Maximum Grant Amount (IDAPA 16.03.08.248)
- **Amount**: $309 per month
- **Legal Quote**: "The maximum grant is three hundred nine dollars ($309)."
- **Note**: This is FLAT regardless of family size

### Work Incentive Table (IDAPA 16.03.08.251)
Used for calculating benefits for families with earned income:

| Household Members | Monthly Amount |
|-------------------|----------------|
| 1                 | $309           |
| 2                 | $309           |
| 3                 | $389           |
| 4                 | $469           |
| 5                 | $547           |
| 6                 | $628           |
| 7                 | $708           |
| 8                 | $787           |
| 9                 | $867           |
| 10                | $947           |
| Over 10           | Add $80 each   |

**Effective Date**: March 17, 2022

---

## Benefit Calculation

### Minimum Payment Threshold (IDAPA 16.03.08.254)
- **Minimum**: $10
- **Legal Quote**: "A payment is not made when the grant amount is less than ten dollars ($10)."

### For Families with No Income (IDAPA 16.03.08.249)
```
Grant = Maximum Grant ($309) - Penalties
```
**Legal Quote**: "The grant amount for eligible families with no income is the maximum grant minus penalties, if applicable."

### For Families with Unearned Income Only (IDAPA 16.03.08.250)
```
Grant = Maximum Grant ($309) - Unearned Income - Penalties
```
**Legal Quote**: "The grant amount for eligible families with unearned income only is the maximum grant minus the unearned income, and penalties if applicable."

### For Families with Earned Income (IDAPA 16.03.08.252)
```
Grant = Work Incentive Table[household_size] - (60% x Gross Earned Income) - (100% x Unearned Income) - Penalties
```
Then:
- Round DOWN to nearest dollar
- Cap at Maximum Grant ($309)

**Legal Quote**: "For eligible families with earned income, an amount is calculated by subtracting sixty percent (60%) of gross earned income, one hundred percent (100%) of any unearned income, and applicable penalties from the figure in the Work Incentive Table based on the household size. The grant amount is the result of this calculation rounded to the next lowest dollar or the maximum grant, whichever is less."

### Benefit Calculation Examples

**Example 1: Family of 3, No Income**
- Work Incentive Table value: $389
- Gross earned income: $0
- Unearned income: $0
- Grant = min($389 - $0 - $0, $309) = $309

**Example 2: Family of 3, Earned Income Only**
- Work Incentive Table value: $389
- Gross earned income: $500
- Unearned income: $0
- Calculation: $389 - (0.60 x $500) - $0 = $389 - $300 = $89
- Grant = min($89, $309) = $89

**Example 3: Family of 4, Mixed Income**
- Work Incentive Table value: $469
- Gross earned income: $400
- Unearned income: $100
- Calculation: $469 - (0.60 x $400) - $100 = $469 - $240 - $100 = $129
- Grant = min($129, $309) = $129

**Example 4: Family of 3, High Earned Income (Zero Benefit)**
- Work Incentive Table value: $389
- Gross earned income: $800
- Unearned income: $0
- Calculation: $389 - (0.60 x $800) = $389 - $480 = -$91
- Grant = max(-$91, 0) = $0 (no payment)

---

## Penalties (IDAPA 16.03.08.242)

### Half-Grant Penalty Priority
If multiple penalties apply:
- Child support penalty (50% reduction for not establishing paternity within 12 months) calculated FIRST
- Then school or work attendance penalties applied

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limits (CANNOT ENFORCE - requires history)
- **State Time Limit**: 24 months lifetime limit for adults (IDAPA 16.03.08.101)
- **Federal Time Limit**: 60 months (counted separately)
- **Interstate Counting**: TANF months from other states (after June 30, 1997) count toward Idaho's 24-month limit

**Legal Quote**: "Lifetime eligibility for adults is limited to twenty-four (24) months unless otherwise provided by these rules."

### Work Requirements (CANNOT TRACK)
- Applicant job search requirements
- Work activities requirements
- Employment and Training Program participation

### Extended Cash Assistance (CANNOT SIMULATE)
- Available after 24-month limit exhausted
- Up to 36 additional months
- Requires physical/mental condition preventing employment at 167% of maximum grant

### Substance Abuse Provisions (CANNOT SIMULATE)
- Screening and testing requirements
- Treatment compliance tracking

---

## Parameter Summary

| Parameter | Value | Source |
|-----------|-------|--------|
| Resource Limit | $5,000 | IDAPA 16.03.08.200 |
| Maximum Grant | $309 | IDAPA 16.03.08.248 |
| Minimum Payment | $10 | IDAPA 16.03.08.254 |
| Earned Income Disregard Rate | 60% | IDAPA 16.03.08.252 |
| Self-Employment Expense Deduction | 50% | IDAPA 16.03.08.231 |
| Dependent Child Age | Under 18 | IDAPA 16.03.08.010 |
| Time Limit (State) | 24 months | IDAPA 16.03.08.101 |
| Work Incentive Table (HH size 1-2) | $309 | IDAPA 16.03.08.251 |
| Work Incentive Table (HH size 3) | $389 | IDAPA 16.03.08.251 |
| Work Incentive Table (HH size 4) | $469 | IDAPA 16.03.08.251 |
| Work Incentive Table (HH size 5) | $547 | IDAPA 16.03.08.251 |
| Work Incentive Table (HH size 6) | $628 | IDAPA 16.03.08.251 |
| Work Incentive Table (HH size 7) | $708 | IDAPA 16.03.08.251 |
| Work Incentive Table (HH size 8) | $787 | IDAPA 16.03.08.251 |
| Work Incentive Table (HH size 9) | $867 | IDAPA 16.03.08.251 |
| Work Incentive Table (HH size 10) | $947 | IDAPA 16.03.08.251 |
| Work Incentive Table (11+) | $947 + $80 per additional | IDAPA 16.03.08.251 |

---

## References for Metadata

### For Parameters
```yaml
reference:
  - title: "IDAPA 16.03.08.200 - Resource Limit"
    href: "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.200"
  - title: "IDAPA 16.03.08.248 - Maximum Grant Amount"
    href: "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.248"
  - title: "IDAPA 16.03.08.251 - Work Incentive Table"
    href: "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.251"
  - title: "IDAPA 16.03.08.252 - Grant Amount for Families with Earned Income"
    href: "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.252"
```

### For Variables
```python
reference = "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.252"
```

---

## Implementation Notes

### Key Implementation Differences from Other States

1. **Flat Maximum Grant**: Unlike most states, Idaho's maximum grant is $309 regardless of family size. The Work Incentive Table only affects families with earned income.

2. **No Separate Income Test**: Idaho does not have a separate gross income eligibility threshold. Eligibility is determined through benefit calculation - if calculated benefit is $10+, the family is eligible.

3. **Work Incentive Design**: The 60% earned income disregard encourages work by allowing families to keep 60% of their earnings without reducing benefits dollar-for-dollar.

4. **Simple Unearned Income Rule**: For families with unearned income only, benefits are simply Maximum Grant minus unearned income.

### Suggested Variable Structure

```
id_tafi/
  eligibility/
    id_tafi_demographic_eligible.py (use federal)
    id_tafi_resources_eligible.py
    id_tafi_eligible.py
  income/
    id_tafi_countable_earned_income.py
    id_tafi_countable_unearned_income.py
  benefit/
    id_tafi_work_incentive_table_amount.py
    id_tafi.py
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **IDAPA 16.03.08 Full Text PDF**
   - URL: https://adminrules.idaho.gov/rules/current/16/160308.pdf
   - Expected content: Complete regulatory text including all sections
   - Key pages: Contains all administrative rules for TAFI program

2. **Idaho TANF State Plan (FY2026-FY2028)**
   - URL: Available from https://healthandwelfare.idaho.gov/services-programs/financial-assistance/about-tafi (link to "View TANF State Plan")
   - Expected content: Federal reporting requirements, state plan amendments

3. **NCCP Idaho State Profile Summary**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Idaho.pdf
   - Expected content: Policy summary, comparative data with other states

---

## Quality Checklist

- [x] **Authoritative**: All sources are official Idaho Administrative Code
- [x] **Current**: Rules reflect March 17, 2022 effective date
- [x] **Complete**: All major program components documented
- [x] **Cited**: Every fact has a specific legal citation
- [x] **Clear**: Complex rules are explained with examples
- [x] **Structured**: Information is organized logically

---

## Document Collection Sources

### HTML Sources Used
- [IDAPA 16.03.08 Table of Contents](https://www.law.cornell.edu/regulations/idaho/title-IDAPA-16/rule-16.03.08)
- [IDAPA 16.03.08.010 - Definitions](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.010)
- [IDAPA 16.03.08.100 - TAFI Eligibility](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.100)
- [IDAPA 16.03.08.101 - Time Limit](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.101)
- [IDAPA 16.03.08.125 - Mandatory Household Members](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.125)
- [IDAPA 16.03.08.131 - Citizenship and Qualified Non-Citizen](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.131)
- [IDAPA 16.03.08.200 - Resource Limit](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.200)
- [IDAPA 16.03.08.201 - Countable Resources](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.201)
- [IDAPA 16.03.08.207 - Vehicles](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.207)
- [IDAPA 16.03.08.208 - Resource Exclusions](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.208)
- [IDAPA 16.03.08.214 - Countable Income](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.214)
- [IDAPA 16.03.08.215 - Excluded Income](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.215)
- [IDAPA 16.03.08.221 - Determining Eligibility](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.221)
- [IDAPA 16.03.08.229 - Self-Employment Income](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.229)
- [IDAPA 16.03.08.231 - Calculation of Self-Employment Income](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.231)
- [IDAPA 16.03.08.240 - Individuals Excluded from Household Size](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.240)
- [IDAPA 16.03.08.242 - Half Grant Penalty Priority](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.242)
- [IDAPA 16.03.08.248 - Maximum Grant Amount](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.248)
- [IDAPA 16.03.08.249 - Grant Amount for No Income](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.249)
- [IDAPA 16.03.08.250 - Grant Amount for Unearned Income Only](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.250)
- [IDAPA 16.03.08.251 - Work Incentive Table](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.251)
- [IDAPA 16.03.08.252 - Grant Amount for Earned Income](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.252)
- [IDAPA 16.03.08.254 - Grant Less Than Ten Dollars](https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.254)
- [Idaho Department of Health and Welfare - About TAFI](https://healthandwelfare.idaho.gov/services-programs/financial-assistance/about-tafi)
