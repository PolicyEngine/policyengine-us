# Collected Documentation

## Vermont Reach Up (TANF) Implementation
**Collected**: 2026-01-02
**Implementation Task**: Implement Vermont's TANF program (Reach Up) including eligibility, income calculations, deductions, and benefit calculations.
**GitHub Issue Reference**: #7042

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Reach Up
**Abbreviation**: RU (commonly referred to as "Reach Up")
**Source**: 33 V.S.A. Chapter 11

**Variable Prefix**: `vt_tanf` (following standard state TANF naming convention)

---

## Administering Agency

**Agency**: Vermont Department for Children and Families (DCF)
**Division**: Economic Services Division (ESD)
**Contact**: 1-800-479-6151
**Program Start Date**: July 1, 2001 (Vermont implemented Reach Up as its principal TANF program)

---

## Legal Authority

### Primary Sources

1. **Vermont Statutes**
   - Title: 33 V.S.A. Chapter 11 - Reach Up
   - URL: https://legislature.vermont.gov/statutes/fullchapter/33/011
   - Key Sections:
     - Section 1101: Definitions
     - Section 1103: Eligibility and benefit levels
     - Section 1108: Time limits

2. **Vermont Administrative Rules**
   - Title: 13-220 Code Vt. R. 13-170-220-X - REACH UP (2200)
   - URL: https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X
   - Key Rules:
     - Rule 2221-2223: Eligible household members
     - Rule 2244.1: Basic Needs Standards
     - Rule 2246: Housing Allowance
     - Rule 2252.3: Earned Income Disregard
     - Rule 2254.1: Asset Limits

3. **TANF State Plan (2024-2027)**
   - Title: Vermont TANF State Plan Renewal October 1, 2024 through December 31, 2027
   - URL: https://outside.vermont.gov/dept/DCF/Shared%20Documents/Benefits/VT-TANF-State-Plan-2024-2027.pdf

---

## Demographic Eligibility

### Eligible Child (Rule 2221)
- **Age Limit**: Under 18 years old
- **Extended Age**: 18-year-old full-time secondary student expected to graduate before age 19
- **Note**: Per statute (33 V.S.A. Section 1101), "dependent child" is defined as under 18, or 18-21 if full-time secondary student with expected completion before age 22

### Eligible Parent (Rule 2222)
- Parent living with eligible child
- Not receiving SSI or AABD (Aid to the Aged, Blind, and Disabled)

### Eligible Caretaker (Rule 2223)
- Relative or unrelated adult providing parental care when parent unavailable

### Pregnant Persons (Rule 2235)
- May qualify with no children if due within 30 days of application

**Implementation approach:**
- [ ] Use federal demographic eligibility (if age thresholds match)
- [x] Create state-specific age thresholds (state has slightly different student age rules)

---

## Immigration Eligibility (Rule 2230)

- Must be U.S. citizen, national, or "qualified immigrant" as defined by federal law
- Non-citizens must provide documentation verified through SAVE system
- Most qualified immigrants must wait 5 years
- Exceptions include refugees, asylees, and certain other categories

**Implementation approach:**
- [x] Use federal immigration eligibility (state follows federal rules)

---

## Resource/Asset Limits

### Resource Limit (Rule 2254.1)
| Threshold | Amount | Source |
|-----------|--------|--------|
| Combined household resources | $9,000 | 33 V.S.A. Section 1103(a)(1) |

### Excluded Resources (Rule 2257, 33 V.S.A. Section 1103)
- Primary residence
- One operable vehicle per adult (equity value excluded)
- One operable vehicle per driving-age child needing vehicle for school/work
- Income-producing property
- Retirement accounts (IRAs, 401(k)s, and similar under 26 U.S.C. Section 408)
- Qualified education savings accounts (529 plans)
- Student financial assistance
- One burial plot and funeral agreement per person ($1,500 max)
- EITC/Child Tax Credits (12-month exclusion for continuing eligibility)

**Source**:
- 33 V.S.A. Section 1103(a)(1): "The asset limitation shall be $9,000.00 for families"
- https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/

---

## Income Standards

### Basic Needs Allowance (Rule 2244.1)

The Basic Needs Allowance by Household Size (from TANF State Plan and regulations):

| Household Size | Basic Needs Allowance |
|----------------|----------------------|
| 1 | $644 |
| 2 | $879 |
| 3 | $1,030 |
| 4 | $1,162 |
| 5 | $1,247 |
| 6 | $1,378 |
| 7 | $1,537 |
| 8 | $2,458 |
| Each additional | +$236 |

**Source**: Vermont TANF State Plan, Code Vt. R. 13-170-220-X

**Note**: These are the 2019 basic needs figures still in use. Vermont continues with its current practice of using a 2019 estimation of basic needs (Act 49 of 2023 directs phasing out the ratable reduction over 5 years).

### Housing Allowance Maximum (Rule 2246)

| County | Maximum Housing Allowance |
|--------|--------------------------|
| Outside Chittenden County | $400/month |
| Chittenden County | $450/month |

**Includes**: Rent, mortgage, property taxes, insurance, maintenance

**Special Housing Allowance**: Up to $90 additional for expenses exceeding the maximum

**Source**: Code Vt. R. 13-170-220-X, Rule 2246

**Historical Note**: The housing allowance was last updated in 2001.

### Room and Board Standards (Rule 2246.3)

| Household Size | Room and Board |
|----------------|---------------|
| 1 | $379 |
| 2 | $562 |
| 3 | $701 |
| 4 | $831 |
| 5 | $934 |
| 6 | $1,059 |
| 7 | $1,213 |
| 8+ | $1,403+ |

---

## Income Deductions and Disregards

### Earned Income Disregard (33 V.S.A. Section 1103, Rule 2252.3)

| Component | Amount/Rate | Source |
|-----------|-------------|--------|
| Initial disregard | First $350/month | 33 V.S.A. Section 1103(a)(3) |
| Remaining earnings disregard | 25% of remainder | 33 V.S.A. Section 1103(a)(3) |

**Formula**:
```
Disregarded Earnings = $350 + (Gross Earnings - $350) × 0.25
Countable Earned Income = Gross Earnings - Disregarded Earnings
```

**Example**: If gross earnings = $1,000/month
- Disregarded = $350 + ($1,000 - $350) × 0.25 = $350 + $162.50 = $512.50
- Countable = $1,000 - $512.50 = $487.50

**Source**:
- 33 V.S.A. Section 1103(a)(3): "Not less than the first $350.00 per month of earnings from an unsubsidized or subsidized job and 25 percent of the remaining earnings shall be disregarded"
- https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/

**Historical Note**: Previously was $250 + 25% of remainder (per older regulations)

### Child Support Disregard

| Component | Amount | Source |
|-----------|--------|--------|
| Per statute | First $100/month | 33 V.S.A. Section 1103(a)(4) |
| Per regulations (Family Bonus) | First $50/month | Rule 2250.1 |

**Source**:
- 33 V.S.A. Section 1103(a)(4): "The Commissioner shall also disregard not less than $100.00 per month of child support payments"
- Rule 2250.1: "First $50 monthly child support per calendar month paid to custodial parent without affecting eligibility/benefit"

**Note**: There appears to be a discrepancy between the statute ($100) and regulations ($50). The statute provides the minimum floor. Implementation should use the statutory $100 value as it represents current law.

### Dependent Care Deduction (Rule 2252.2)
| Component | Maximum Amount |
|-----------|---------------|
| Work-related childcare | $175/month |

Includes transportation costs within maximum. Also applies for disabled family member care meeting specified criteria.

### Excluded Income (Rule 2253)
- Student grants/loans
- EITC (federal and state)
- Child Tax Credits
- SSI/AABD recipient income
- 3SquaresVT (SNAP) benefits
- Disaster assistance
- Veterans education benefits
- Reimbursements for volunteer activities
- Education stipends, employment stipends, job training stipends, and incentive payments

### Unearned Income (Rule 2249)
Counted sources include:
- Pensions
- Social Security
- Unemployment compensation
- Child support over disregard amount
- Capital investment income

---

## Benefit Calculation

### Ratable Reduction (Rule 2239)

**Current Rate**: 49.6%

**Formula**:
```
Payment Standard = (Basic Needs Allowance + Housing Allowance) × 0.496
```

Round down to nearest dollar.

**Source**: Vermont TANF State Plan - payment standards calculated by "(1) adding countable housing expenses up to the maximum allowance for the county of residence to the basic needs allowance for the family size, (2) multiplying the sum by the ratable reduction percentage (49.6%), and (3) rounding the result down."

**Legislative Action**: H.94 (Act 49 of 2023) directs the administration to eliminate the ratable reduction over 5 years by 2030.

### Payment Standards by Family Size (Calculated)

**Outside Chittenden County** (Housing Max = $400):

| Family Size | Basic Needs | Housing | Total Needs | Payment Standard (×0.496) |
|-------------|-------------|---------|-------------|---------------------------|
| 1 | $644 | $400 | $1,044 | $517 |
| 2 | $879 | $400 | $1,279 | $634 |
| 3 | $1,030 | $400 | $1,430 | $709 |
| 4 | $1,162 | $400 | $1,562 | $774 |
| 5 | $1,247 | $400 | $1,647 | $816 |

**Chittenden County** (Housing Max = $450):

| Family Size | Basic Needs | Housing | Total Needs | Payment Standard (×0.496) |
|-------------|-------------|---------|-------------|---------------------------|
| 1 | $644 | $450 | $1,094 | $542 |
| 2 | $879 | $450 | $1,329 | $659 |
| 3 | $1,030 | $450 | $1,480 | $734 |
| 4 | $1,162 | $450 | $1,612 | $799 |
| 5 | $1,247 | $450 | $1,697 | $841 |

**Note**: Maximum benefit for a family of 3 is reported as $856-$880 by NCCP (2024), suggesting possible updates to basic needs standards. Current available documentation shows the calculation above using 2019 basic needs standards.

### Benefit Calculation Formula

```
Benefit = Payment Standard - Countable Income

Where:
- Payment Standard = (Basic Needs + min(Housing Costs, Housing Max)) × Ratable Reduction
- Countable Income = Countable Earned + Countable Unearned
- Countable Earned = Gross Earned - Earned Income Disregard
- Earned Income Disregard = $350 + (Gross Earned - $350) × 0.25
- Countable Unearned = Gross Unearned - Child Support Disregard - Other Exclusions
```

### Minimum Benefit (Rule 2242)
No payment made if benefit is less than $10/month (except parent share payments).

---

## Time Limits (Cannot Be Simulated)

### 60-Month Cumulative Limit (33 V.S.A. Section 1108, Rule 2234)

**Lifetime Limit**: 60 months of TANF benefits

**Months NOT counting toward limit**:
- First 12 months caring for young child (max 12 lifetime)
- Full months deferred for: domestic violence, inability to work, caring for ill/disabled family member
- Postsecondary Education, Reach First, or Reach Ahead program months

**Exceptions to Time Limit (Rule 2234(f))**:
- Single/two-parent households with parent under 18
- Dependent child with non-parent caretaker not in household
- Child living with SSI/AABD-receiving parent(s)

### Non-Simulatable Rules (Architecture Limitation)

- **Time Limit**: 60-month lifetime limit [CANNOT ENFORCE - requires history tracking]
- **Hardship Exemption**: Universal engagement alternative after 60 months [CANNOT TRACK]

---

## Work Requirements (Not Implemented in Eligibility Model)

Work requirements affect service participation but not financial eligibility determination. Key points for reference:

- Adults must participate in employment planning and goal achievement
- Participation activities include: employment, skill development, job search, education, family well-being activities
- Deferments available for: adults 60+, caring for child under 6 weeks, domestic violence situations

---

## Sanctions (Rule 2233, 33 V.S.A. Section 1116)

| Duration | Reduction Amount |
|----------|-----------------|
| Months 1-3 of non-engagement | $75 per sanctioned adult |
| Month 4+ | $150 per sanctioned adult |

**Housing Protection** (first 6 months): Grant cannot be reduced below actual housing costs (up to maximum allowance)

---

## Geographic Variation

Vermont is one of only seven states where benefit levels vary by geographic region.

**Regions**:
1. **Chittenden County**: Higher housing allowance maximum ($450)
2. **All Other Counties**: Standard housing allowance maximum ($400)

---

## Historical Payment Values (From GitHub Issue #7042)

### Pre-August 2019 Values
Source: https://legislature.vermont.gov/assets/Legislative-Reports/Reach-Up-Annual-Report-2018.01.31.pdf#page=17

The 2018 Annual Report shows payment values for families 1-4.

### Post-August 2019 Values
Source: https://ljfo.vermont.gov/assets/Uploads/9bc271c390/Reach-Up-Annual-Report_FINAL_2020.01.15.pdf#page=20

In August 2019, the existing basic needs and payment values changed.

**Calculation for family sizes larger than 4**:
```
Payment = (Basic Needs + Housing Allowance for county) × 0.496
Example: Family of 5 in Chittenden County = ($1,247 + $450) × 0.496 = $842
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Vermont TANF State Plan 2024-2027**
   - URL: https://outside.vermont.gov/dept/DCF/Shared%20Documents/Benefits/VT-TANF-State-Plan-2024-2027.pdf
   - Expected content: Complete benefit calculation methodology, current payment standards, basic needs tables

2. **Vermont TANF State Plan 2021-2024**
   - URL: https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Reports/TANF-State-Plan-2021-24.pdf
   - Expected content: Historical program parameters

3. **Reach Up Annual Report 2018**
   - URL: https://legislature.vermont.gov/assets/Legislative-Reports/Reach-Up-Annual-Report-2018.01.31.pdf#page=17
   - Expected content: Payment values for 2017-2019 period

4. **Reach Up Annual Report 2020**
   - URL: https://ljfo.vermont.gov/assets/Uploads/9bc271c390/Reach-Up-Annual-Report_FINAL_2020.01.15.pdf#page=20
   - Expected content: Updated basic needs and payment values post-August 2019

5. **Vermont DCF Reach Up Rules (2200 series)**
   - URL: https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2200-Reach-Up.pdf
   - Expected content: Complete administrative rules with all tables

6. **NCCP Vermont TANF Profile 2024**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Vermont.pdf
   - Expected content: Current benefit amounts as percentage of FPL

7. **NCCP TANF Benefit Amounts 2024**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-Benefit-Amounts-2024-FINAL.pdf
   - Expected content: 50-state comparison with Vermont data

---

## Implementation Notes

### Key Vermont-Specific Features

1. **Geographic Variation**: Two housing allowance tiers (Chittenden vs. non-Chittenden)
2. **Ratable Reduction**: 49.6% factor applied to need standard
3. **Generous Earned Income Disregard**: $350 + 25% of remainder
4. **High Asset Limit**: $9,000 (relatively generous compared to other states)
5. **Broad Resource Exclusions**: Retirement accounts, 529 plans, vehicles excluded

### Variables Needed

| Variable | Type | Entity | Period | Description |
|----------|------|--------|--------|-------------|
| vt_tanf_eligible | bool | SPMUnit | MONTH | Vermont TANF eligibility |
| vt_tanf_income_eligible | bool | SPMUnit | MONTH | Vermont TANF income eligibility |
| vt_tanf_resource_eligible | bool | SPMUnit | MONTH | Vermont TANF resource eligibility |
| vt_tanf_countable_earned_income | float | SPMUnit | MONTH | Countable earned income after disregard |
| vt_tanf_countable_unearned_income | float | SPMUnit | MONTH | Countable unearned income |
| vt_tanf_countable_income | float | SPMUnit | MONTH | Total countable income |
| vt_tanf_basic_needs_allowance | float | SPMUnit | MONTH | Basic needs allowance by family size |
| vt_tanf_housing_allowance | float | SPMUnit | MONTH | Housing allowance (capped by county) |
| vt_tanf_payment_standard | float | SPMUnit | MONTH | Payment standard after ratable reduction |
| vt_tanf | float | SPMUnit | MONTH | Vermont TANF benefit amount |
| is_in_chittenden_county | bool | Household | YEAR | Whether household is in Chittenden County |

### Parameters Needed

| Parameter | Path | Description |
|-----------|------|-------------|
| Basic needs by family size | gov.states.vt.dcf.tanf.income.basic_needs | Basic needs allowance table |
| Housing max (non-Chittenden) | gov.states.vt.dcf.tanf.income.housing.maximum.non_chittenden | $400 |
| Housing max (Chittenden) | gov.states.vt.dcf.tanf.income.housing.maximum.chittenden | $450 |
| Ratable reduction | gov.states.vt.dcf.tanf.benefit.ratable_reduction | 0.496 |
| Earned income disregard flat | gov.states.vt.dcf.tanf.income.disregard.earned.flat | $350 |
| Earned income disregard rate | gov.states.vt.dcf.tanf.income.disregard.earned.rate | 0.25 |
| Child support disregard | gov.states.vt.dcf.tanf.income.disregard.child_support | $100 |
| Resource limit | gov.states.vt.dcf.tanf.resources.limit | $9,000 |
| Dependent care max | gov.states.vt.dcf.tanf.income.deduction.dependent_care.max | $175 |
| Minimum benefit | gov.states.vt.dcf.tanf.benefit.minimum | $10 |

---

## References Summary

### Statutes
- [33 V.S.A. Chapter 11 - Reach Up](https://legislature.vermont.gov/statutes/fullchapter/33/011)
- [33 V.S.A. Section 1103 - Eligibility and benefit levels](https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/)

### Administrative Rules
- [Code of Vermont Rules 13-220 (Reach Up 2200 series)](https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X)

### State Plans and Reports
- [Vermont TANF State Plan 2024-2027](https://outside.vermont.gov/dept/DCF/Shared%20Documents/Benefits/VT-TANF-State-Plan-2024-2027.pdf)
- [Vermont TANF State Plan 2021-2024](https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Reports/TANF-State-Plan-2021-24.pdf)

### DCF Resources
- [DCF Reach Up Program Page](https://dcf.vermont.gov/benefits/reachup)
- [DCF ESD Laws, Rules & Procedures](https://dcf.vermont.gov/esd/laws-rules)

### Third-Party Analysis
- [VT Law Help - Money/Cash Benefits: Reach Up](https://vtlawhelp.org/money-cash-benefits-reach-up)
- [Voices for Vermont's Children - Reach Up](https://www.voicesforvtkids.org/reachup)
- [Voices for Vermont's Children - Ratable Reduction Explainer](https://www.voicesforvtkids.org/ratable-reduction)
