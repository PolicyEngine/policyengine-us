# Collected Documentation

## Kansas TANF (Temporary Assistance for Families) Implementation
**Collected**: 2025-12-18
**Implementation Task**: Implement Kansas TANF eligibility and benefit calculation

---

## Program Overview

Kansas TANF is administered by the Kansas Department for Children and Families (DCF) as the "Successful Families Program." The program provides temporary cash assistance to families with children who meet income and resource requirements.

**Key Program Names:**
- Federal: Temporary Assistance for Needy Families (TANF)
- Kansas: Temporary Assistance for Families (TAF)
- Marketing Name: Successful Families Program

---

## Source Information

### Primary Legal Sources

1. **Kansas Statutes Chapter 39, Article 7**
   - Citation: K.S.A. 39-709
   - URL: https://kslegislature.gov/li/b2025_26/statute/039_000_0000_chapter/039_007_0000_article/039_007_0009_section/039_007_0009_k/

2. **Kansas Administrative Regulations (K.A.R.) Article 30-4**
   - Citation: K.A.R. 30-4-41 through 30-4-113
   - URL: https://www.law.cornell.edu/regulations/kansas/agency-30/article-4

3. **Kansas Economic and Employment Support Manual (KEESM)**
   - URL: https://content.dcf.ks.gov/ees/keesm/current/home.htm
   - Publisher: Kansas Department for Children and Families

### Specific Regulatory Citations

| Topic | Regulation | URL |
|-------|------------|-----|
| Assistance Planning | K.A.R. 30-4-41 | https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-41 |
| Assistance Eligibility | K.A.R. 30-4-50 | https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-50 |
| TAF Eligibility Factors | K.A.R. 30-4-70 | https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-70 |
| Payment Standards | K.A.R. 30-4-100 | https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100 |
| Basic Standards | K.A.R. 30-4-101 | https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-101 |
| Income | K.A.R. 30-4-110 | https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110 |

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limit
- **Rule**: 24-month lifetime limit on TANF cash assistance
- **Citation**: K.A.R. 30-4-50, K.S.A. 39-709
- **Status**: CANNOT ENFORCE - requires tracking benefit history across periods
- **Note**: Hardship extensions allow up to 36 months total

### Work History Requirements
- **Rule**: Adults must participate in work activities
- **Citation**: K.A.R. 30-4-64
- **Status**: CANNOT TRACK - requires monitoring compliance over time

### Progressive Sanctions
- **Rule**: Escalating penalties for non-compliance (3 months -> 6 months -> 1 year -> 10 years)
- **Citation**: K.S.A. 39-709
- **Status**: CANNOT ENFORCE - requires tracking violation history

### Work Incentive Payment
- **Rule**: $50/month for 5 consecutive months after losing cash eligibility due to earnings
- **Citation**: KEESM 1111
- **Status**: PARTIALLY SIMULATABLE - cannot track the 5-month limit

---

## Demographic Eligibility

### Child Requirements
**Source**: K.A.R. 30-4-70

- Family must include at least one eligible child
- **Definition of "child":**
  - Under age 18 (including unborn children), OR
  - Age 18 and enrolled in secondary school or pursuing GED

**Implementation Note**: Kansas age threshold (18/19 for students) matches federal baseline. Can use `is_demographic_tanf_eligible`.

### Caretaker Requirements
**Source**: K.A.R. 30-4-70, K.A.R. 30-4-41

The eligible child must reside with:
- Blood relatives within fifth degree of kinship (parents, siblings, aunts, uncles, cousins, grandparents)
- Steprelatives or adoptive relatives
- Court-appointed guardians/conservators
- Spouses or former spouses of qualifying relatives
- Cohabiting partner of the legally responsible person

### Teen Parent Restriction
**Source**: K.A.R. 30-4-70

Teen parents under 18 are **ineligible** if BOTH conditions exist:
1. They are unmarried, AND
2. They lack a high school diploma/GED AND are not pursuing one

### Residency
**Source**: K.A.R. 30-4-70

- Must be Kansas resident
- Temporary absence of 90 days or less maintains eligibility
- Absence for employment maintains eligibility

---

## Resource Eligibility

### Resource Limit
**Source**: KEESM 5110, KEESM 5000

| Standard | Amount | Notes |
|----------|--------|-------|
| Maximum nonexempt resources | $3,000 | Applies to all mandatory filing unit members |

**Note**: Multiple sources cite $2,250 as the limit (e.g., DCF website), but KEESM 5110 explicitly states $3,000. The $2,250 figure may be outdated or from unofficial sources. **Recommend verifying current value with DCF.**

### Exempt Resources
**Source**: KEESM 5430, K.S.A. 39-709

- Primary residence (home)
- One motor vehicle (regardless of value)
- Assets under $3,000
- Furniture and personal items
- Certain tools and equipment used for primary income-earning

### Resource Evaluation
**Source**: KEESM 5200

- Resources must be real, measurable, and available
- Value = client's equity (fair market value minus encumbrances)
- Joint ownership: pro rata equity for real property, full equity for personal property
- No resource limit during Work Incentive payment period

---

## Income Eligibility

### Gross Income Limit
**Source**: Multiple sources cite different thresholds

| Measure | Amount | Source |
|---------|--------|--------|
| 30% of FPL | ~$519/month (family of 3) | Kansas Action for Children |
| 28% of FPL | ~$602/month (family of 3) | Some unofficial sources |

**CRITICAL**: Income limit is expressed as a percentage of Federal Poverty Level, NOT a fixed dollar amount.

**Implementation approach:**
- [ ] Store as rate multiplied by FPL (0.30 * FPL)
- [ ] Need to verify exact percentage from official source

### Net Income Test / Budgetary Standard
**Source**: KEESM 7110, K.A.R. 30-4-110

Countable income must be less than the payment standard (which varies by household size and county).

### Income Calculation Method
**Source**: KEESM 7110

Kansas uses **prospective budgeting**:
- Based on income received/expected in the calendar month
- Includes deductions billed to the household

**Conversion factors for income frequency:**
- Weekly income: multiply by 4.3
- Biweekly income: multiply by 2.15
- Twice monthly: add amounts together

---

## Income Types and Exclusions

### Earned Income
**Source**: K.A.R. 30-4-110

- Wages, salary, or profit from employment/self-employment
- Income received in cash or in kind

### Unearned Income
**Source**: KEESM 6220

- Support payments (child support, alimony)
- Other non-work-based revenue
- Gambling winnings (gross amount)

### Excluded Income
**Source**: K.A.R. 30-4-112, K.A.R. 30-4-113

- Self-employment costs (25% standard deduction or actual)
- Youth program income from job training partnership programs
- Earned income of students in elementary/secondary school or pursuing GED
- Work Assessment Reimbursement Allowance

---

## Earned Income Deductions and Disregards

### 60% Earned Income Disregard
**Source**: KEESM Implementation Memo 2008-0326 (Effective May 1, 2008)

- **Disregard Rate**: 60% of earned income
- **Application**: TAF cash assistance recipients
- **Previous Rate**: 40% (prior to May 2008)

**Formula**: Countable Earned Income = Gross Earned Income * (1 - 0.60) = Gross Earned Income * 0.40

**Note**: This means only 40% of earned income is counted against the budget standard.

### $90 Work Expense Deduction
**Source**: DCF TANF webpage, multiple secondary sources

- Standard work expense deduction: $90
- Applied to gross earned income

**Note**: Need to verify if this is per person or per household, and if it applies before or after the 60% disregard.

### Self-Employment Income
**Source**: KEESM 7122

- Standard income producing cost deduction: 25% of gross self-employment earnings
- Option to use actual costs if higher than 25%
- If actual costs < 25%, the 25% standard is used

### Work Expense Deductions for Disabled
**Source**: KEESM 8151

| Type | Standard Disregard | Notes |
|------|-------------------|-------|
| Blind Work Expense (BWE) | First $300 | Actual if verified expenses exceed |
| Impairment-Related Work Expense (IRWE) | First $100 | Actual if verified expenses exceed |

After standard work expense deductions:
- First $65/month of gross earned income disregarded
- One-half (50%) of remaining earnings disregarded

**Note**: The above ($65 + 50%) appears to be for medical programs (MS, QMB, LMB), not TAF. The 60% disregard applies to TAF.

---

## Payment Standards (Benefit Amounts)

### Payment Standard Structure
**Source**: K.A.R. 30-4-100, K.A.R. 30-4-101, DCF TANF webpage

Kansas payment standards consist of:
1. **Basic Standard** (K.A.R. 30-4-101) - covers routine living expenses
2. **Shelter Standard** - varies by county grouping

### Basic Standards by Household Size
**Source**: K.A.R. 30-4-101 (Effective March 1, 1997)

| Household Size | Basic Standard |
|----------------|----------------|
| 1 | $132 |
| 2 | $217 |
| 3 | $294 |
| 4 | $362 |

**Note**: Includes $18 per person as energy supplement

### Total Payment Standards (Non-Shared Living)
**Source**: DCF TANF webpage, KEESM Appendix F-4

| Family Size | Rural (Plan I & II) | High Cost Rural (Plan III) | High Population (Plan IV) | High Cost High Population (Plan V) |
|-------------|---------------------|---------------------------|--------------------------|-----------------------------------|
| 1 | $224 | $229 | $241 | $267 |
| 2 | $309 | $314 | $326 | $352 |
| 3 | $386 | $391 | $403 | $429 |
| 4 | $454 | $459 | $471 | $497 |
| 5 | Add $61 per additional person to base amounts |

### Total Payment Standards (Shared Living)
**Source**: KEESM Appendix F-5

| Household Size | Plans I & II | Plan III | Plan IV | Plan V |
|----------------|--------------|----------|---------|--------|
| 1 | $168 | $170 | $175 | $186 |
| 2 | $263 | $265 | $271 | $284 |
| 3 | $349 | $352 | $359 | $375 |
| 4 | $421 | $425 | $432 | $449 |
| 5 | $487 | $490 | $499 | $517 |
| 6 | $557 | $561 | $571 | $592 |
| 7 | $618 | $622 | $632 | $653 |
| 8 | $679 | $683 | $693 | $714 |
| 9+ | Add $61 per additional person (Plans I & II column) |

### Shared Living Reduction Percentages
**Source**: K.A.R. 30-4-100

When non-plan members reside in the home, shelter standard is reduced:

| Plan Members | Shelter Standard |
|--------------|------------------|
| 1 person | 60% reduction |
| 2 persons | 50% reduction |
| 3 persons | 40% reduction |
| 4 persons | 35% reduction |
| 5 persons | 30% reduction |
| 6+ persons | 20% reduction |

### County Payment Groups
**Source**: KEESM, DCF

Counties are classified into payment groups (Plan I-V) based on cost of living:
- **Plan I & II**: Rural counties (lowest cost)
- **Plan III**: High Cost Rural
- **Plan IV**: High Population (urban areas)
- **Plan V**: High Cost High Population (e.g., Johnson County, Shawnee County metro areas)

**Note**: Specific county-to-plan mapping not extracted. Need to reference KEESM Appendix for complete listing.

---

## Benefit Calculation Formula

### General Formula
**Source**: KEESM 7110, K.A.R. 30-4-100

```
TAF Benefit = Payment Standard - Countable Income
```

Where:
- **Payment Standard** = Based on household size + county plan + living arrangement
- **Countable Income** = Gross Income - Applicable Deductions and Disregards

### Step-by-Step Calculation

1. **Calculate Gross Earned Income**
   - Convert to monthly using frequency factors (4.3 for weekly, 2.15 for biweekly)

2. **Apply Self-Employment Deduction (if applicable)**
   - 25% of gross self-employment income

3. **Apply $90 Work Expense Deduction** (needs verification)

4. **Apply 60% Earned Income Disregard**
   - Countable Earned Income = Gross Earned Income * 0.40

5. **Add Unearned Income**
   - Total Countable Income = Countable Earned Income + Unearned Income

6. **Determine Payment Standard**
   - Based on household size and county plan

7. **Calculate Benefit**
   - TAF Benefit = Payment Standard - Total Countable Income
   - If negative, benefit = $0

### Minimum Benefit
**Source**: KEESM 2512

- Family TANF benefit for a one-year period cannot be less than $1,000
- A working family who qualifies for $82 or less per month is NOT eligible

### Proration
**Source**: KEESM 7400

- Applications filed on the 1st: full month benefit
- Applications filed after the 1st: prorated from application date
- Formula: (Monthly benefit / days in month) * remaining days

### Rounding
**Source**: KEESM 7400

- All money payments rounded DOWN to the next lowest dollar

---

## Work Incentive Payment

### Overview
**Source**: KEESM 1111, Implementation Memo 2008-1117

The Work Incentive Payment assists families who become ineligible for TAF due to excess earned income.

### Eligibility
- Income exceeds TAF maximum (failed income check)
- Income includes earnings from employment
- Open TAF case existed in the previous month
- Work Incentive payments haven't exceeded five consecutive months

### Payment Amount
- Fixed $50.00 per month
- No proration
- Per household, not per individual

### Duration
- Maximum 5 consecutive months
- No limit to number of times a household can qualify
- Counts toward lifetime time limit

### Restrictions
- Not available if child support income exceeds $50 monthly
- Cannot be paid simultaneously with regular TAF benefits
- No resource limit during Work Incentive payment period

---

## Mandatory Filing Unit

### Composition
**Source**: K.A.R. 30-4-41, KEESM 4100

The mandatory filing unit includes:
- Applicant/recipient
- All individuals living together with a legal and/or caretaker relationship
- Parents (including stepparents)
- Cohabiting partners of the legally-responsible adult
- All children of parents, stepparents, and cohabiting partners in the home

### Excluded Members Treatment
**Source**: KEESM 4100

When a mandatory filing unit member is excluded:
- Remains part of filing unit for income/resource consideration
- Not eligible for benefits
- Needs excluded from benefit calculations
- Earned income deductions/disregards do NOT apply to excluded members' earnings

---

## Immigration Eligibility

### Requirements
**Source**: K.A.R. 30-4-50, K.S.A. 39-709

Must be one of:
- U.S. citizen
- Lawfully admitted alien
- Qualified immigrant

**Implementation Note**: Kansas follows federal immigration eligibility rules. Can use `is_citizen_or_legal_immigrant`.

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Kansas TANF State Plan FFY 2024-2026**
   - URL: https://www.dcf.ks.gov/services/ees/Documents/Reports/TANF State Plan FFY 2024 - 2026.pdf
   - Expected content: Complete TANF state plan with detailed eligibility criteria, benefit calculations, county groupings
   - Key pages: State Plan typically contains income methodology and benefit formulas

2. **KEESM Appendix F-4: TAF Non-Shared Living Standards**
   - URL: https://content.dcf.ks.gov/ees/keesm/appendix/F-4_TAFtable07_11.pdf
   - Expected content: Complete payment standard table by household size and county plan for non-shared living
   - Effective date: July 2011

3. **Kansas's Cash Assistance (TANF) Policy Profile (NCCP)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Kansas.pdf
   - Expected content: Summary of Kansas TANF policies including income limits as percentage of FPL

4. **50-State TANF Benefit Amounts Comparison**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-Benefit-Amounts-2024-FINAL.pdf
   - Expected content: Comparison data for validating Kansas benefit amounts

5. **Kansas Administrative Regulations Volume 3 (2022)**
   - URL: https://sos.ks.gov/publications/KAR/2022/2022_KAR_Volumes_Book_3.pdf
   - Expected content: Full text of K.A.R. 30-4 regulations

---

## Implementation Notes

### Verified Values for Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Resource limit | $3,000 | KEESM 5110 |
| Earned income disregard | 60% | KEESM Implementation Memo 2008-0326 |
| Self-employment deduction | 25% | KEESM 7122 |
| Work incentive payment | $50/month | KEESM Implementation Memo 2008-1117 |
| Minimum monthly benefit | $82 | KEESM 2512 |
| Minor child age | Under 18 | K.A.R. 30-4-70 |
| Student age | Under 19 (in school) | K.A.R. 30-4-70 |

### Values Needing Verification

| Parameter | Uncertain Value | Notes |
|-----------|-----------------|-------|
| Income limit as % FPL | 30% or 28% | Multiple sources cite different values |
| Work expense deduction | $90 | Cited in secondary sources, not verified in regulations |
| County-to-plan mapping | N/A | Need complete listing from KEESM Appendix |

### Implementation Approach

1. **Demographic Eligibility**: Use federal baseline (`is_demographic_tanf_eligible`) - Kansas age thresholds match federal (18/19 for students)

2. **Immigration Eligibility**: Use federal baseline (`is_citizen_or_legal_immigrant`) - Kansas follows federal rules

3. **Income Sources**: Create Kansas-specific versions to handle:
   - 60% earned income disregard
   - Self-employment 25% deduction
   - Student income exclusion

4. **Payment Standards**: Create parameter file with:
   - Breakdown by household size (1-8+)
   - Breakdown by county plan (I-V or simplified to 4 categories)
   - Separate tables for shared vs non-shared living

5. **Benefit Calculation**:
   - Payment Standard - Countable Income
   - Round down to nearest dollar
   - Minimum benefit threshold check ($82/month)

---

## References for Metadata

### For Variables
```python
reference = "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-70"  # TAF eligibility
reference = "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100"  # Payment standards
reference = "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110"  # Income
reference = "https://content.dcf.ks.gov/ees/keesm/implem_memo/2008_0326_TAF_ei_disregard.htm"  # 60% disregard
```

### For Parameters
```yaml
reference:
  - title: K.A.R. 30-4-101 Basic Standards
    href: https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-101
  - title: KEESM Implementation Memo - TAF Earned Income Disregard (2008)
    href: https://content.dcf.ks.gov/ees/keesm/implem_memo/2008_0326_TAF_ei_disregard.htm
```

---

## Key Differences from Federal Baseline

| Component | Federal Baseline | Kansas |
|-----------|-----------------|--------|
| Time limit | 60 months | 24 months (36 with hardship) |
| Earned income disregard | Varies by state | 60% |
| Resource limit | Varies by state | $3,000 |
| Payment standards | Varies by state | 4-5 payment plans by county |
| Age threshold | 18 (19 for students) | Same as federal |

---

## Summary of Key Rules

1. **To qualify**: Family must have child under 18 (or 18 in school), meet income test (<30% FPL gross), and have resources under $3,000

2. **Earned income treatment**: 60% of earned income is disregarded (only 40% counted)

3. **Benefit amount**: Payment standard (based on family size and county) minus countable income

4. **Payment varies by county**: Rural counties get lower payments than urban/high-cost counties

5. **Time limit**: 24 months lifetime (cannot simulate)

6. **Minimum benefit**: $82/month threshold - families qualifying for less are ineligible
