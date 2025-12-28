# Collected Documentation

## Hawaii TANF Implementation
**Collected**: 2025-12-28
**Implementation Task**: Implement Hawaii TANF (Temporary Assistance for Needy Families) program eligibility and benefit calculation
**Related Issue**: #6799 (Hawaii TANF payment values 2017, 2018, 2019)

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Temporary Assistance for Needy Families (TANF) / Temporary Assistance for Other Needy Families (TAONF)
**Abbreviation**: TANF / TAONF
**Source**: Hawaii Revised Statutes Section 346-53; HAR Chapter 17-656.1

**Notes**:
- Hawaii operates two parallel programs:
  - **TANF**: Federally-funded program for U.S. citizen families
  - **TAONF**: State-funded program for mixed-status families (same rules and benefits as TANF)
- Both programs use identical eligibility rules and benefit calculations

**Variable Prefix**: `hi_tanf`

---

## Regulatory Authority

### State Statutes
- **Hawaii Revised Statutes (HRS) Section 346-53**: Determination of amount of assistance
  - URL: https://law.justia.com/codes/hawaii/title-20/chapter-346/section-346-53/
  - Defines Standard of Need (SON) as 100% of 2006 Hawaii Federal Poverty Level
  - Sets monthly assistance allowance between 48% and 62.5% of SON

### Hawaii Administrative Rules (HAR)
- **HAR Chapter 17-656.1**: Temporary Assistance for Needy Families (TANF)
  - URL: https://humanservices.hawaii.gov/admin-rules-2/admin-rules-for-programs/
- **HAR Chapter 17-676**: Income
  - URL: https://humanservices.hawaii.gov/wp-content/uploads/2019/03/HAR-17-676-INCOME.pdf
- **HAR Chapter 17-680**: Eligibility and Benefit Determination
  - URL: https://humanservices.hawaii.gov/wp-content/uploads/2018/09/680.pdf

### Official Program Website
- **Hawaii DHS TANF Page**: https://humanservices.hawaii.gov/bessd/tanf/

---

## Income Eligibility Tests

### Gross Income Test
- **Threshold**: 185% of Standard of Need (SON)
- **SON Definition**: 100% of Hawaii's 2006 Federal Poverty Level (frozen since July 1, 2007)
- **Source**: HRS Section 346-53; Hawaii TANF State Plan

### Net Income Test
- **Threshold for Work-Eligible Households**: 48% of SON (Standard of Assistance)
  - After 2 full months of benefits, reduced by 20% (resulting in approximately 38.4% of SON)
- **Threshold for Non-Work-Eligible Households**: 48% of SON (no 20% reduction)
- **Source**: HRS Section 346-53; Hawaii TANF State Plan (Effective October 1, 2023)

---

## Income Standards by Household Size (Based on 2006 Hawaii FPL)

### 2006 Hawaii Federal Poverty Level (Annual)
| Household Size | Annual Amount | Monthly Amount (SON - 100% FPL) |
|----------------|---------------|----------------------------------|
| 1 | $11,270 | $939 |
| 2 | $15,180 | $1,265 |
| 3 | $19,090 | $1,590 |
| 4 | $23,000 | $1,916 |
| 5 | $26,910 | $2,242 |
| 6 | $30,820 | $2,568 |
| 7 | $34,730 | $2,894 |
| 8 | $38,640 | $3,220 |
| 9+ | Add $3,910/year per person | Add $326/month per person |

**Source**: 2006 HHS Poverty Guidelines (Federal Register, Vol. 71, No. 15, January 24, 2006)
- URL: https://aspe.hhs.gov/2006-hhs-poverty-guidelines

### Gross Income Limit (185% of SON)
| Household Size | Monthly Gross Income Limit |
|----------------|---------------------------|
| 1 | $1,737 |
| 2 | $2,340 |
| 3 | $2,941 |
| 4 | $3,544 |
| 5 | $4,147 |
| 6 | $4,750 |
| 7 | $5,353 |
| 8 | $5,957 |
| 9 | $6,558 |
| 10 | $7,161 |

**Source**: Hawaii DHS Standards Desk Aid
- URL: http://www.hawaii.edu/bridgetohope/downloads/UPDATED%20STANDARD%20OF%20ASSISTANCE%20AND%20DESK%20AID%20%20EFF.%2001-01-20%202.pdf

### Standard of Assistance (SOA) - 48% of SON (Maximum Benefit for Non-Work-Eligible)
| Household Size | Monthly SOA (48% SON) |
|----------------|----------------------|
| 1 | $450 |
| 2 | $607 |
| 3 | $763 |
| 4 | $919 |
| 5 | $1,076 |
| 6 | $1,232 |
| 7 | $1,389 |
| 8 | $1,545 |
| 9 | $1,701 |
| 10 | $1,858 |

**Source**: Hawaii DHS Standards Desk Aid; Hawaii TANF State Plan

### Payment Amount After 20% Reduction (Work-Eligible Households After 2 Months)
| Household Size | Monthly Payment (SOA - 20%) |
|----------------|---------------------------|
| 1 | $360 |
| 2 | $485 |
| 3 | $610 |
| 4 | $735 |
| 5 | $860 |

**Note**: The 20% reduction applies only to work-eligible households after receiving their first two full months of assistance at the 48% standard.

**Source**: Hawaii DHS Standards Desk Aid; HRS Section 346-53

---

## Income Deductions & Exemptions

### Earned Income Deductions (Applied in Order)
The following deductions are applied ONLY to earned income:

1. **Standard Deduction**: 20% of gross earned income
   - **Source**: HAR 17-676-72; Hawaii TANF State Plan

2. **Flat Rate Deduction**: $200 per month
   - **Source**: Hawaii TANF State Plan

3. **Earned Income Disregard (EIDR)**: 36% or 55%
   - **55% disregard**: Applied during months 1-24 of TANF receipt for employed recipients
   - **36% disregard**: Applied after 24 months of TANF receipt for employed recipients
   - **Note**: Does NOT apply to applicants or earnings of minor children
   - **Source**: Hawaii TANF State Plan; Rules finalized January 13, 2010

4. **Dependent Care Expense Deduction** (when applicable):
   - Up to **$175/month** if full-time employed
   - Up to **$165/month** if part-time employed
   - **Source**: Hawaii TANF State Plan

### Calculation Order
```
Gross Earned Income
  - 20% Standard Deduction
  - $200 Flat Rate Deduction
  - 36% or 55% EIDR (if applicable)
  - Dependent Care Expense (if applicable)
= Countable Earned Income

Countable Income = Countable Earned Income + Unearned Income
```

### Non-Simulatable Rules

#### Time Limit (CANNOT be simulated)
- **60-month lifetime limit** on TANF/TAONF benefits
- PolicyEngine cannot track cumulative months of receipt
- **Source**: HRS Section 346-53; Hawaii TANF State Plan

#### Earned Income Disregard Tier (Partially Simulatable)
- The 55% vs 36% EIDR depends on whether household has received <= 24 months or > 24 months of benefits
- PolicyEngine cannot track cumulative months
- **Implementation approach**: Apply 55% disregard as default (assumes household in first 24 months), document limitation
- **Source**: Hawaii TANF State Plan

#### 20% SOA Reduction (Partially Simulatable)
- The 20% reduction applies after first 2 full months of assistance
- PolicyEngine cannot track months of receipt
- **Implementation approach**: Apply 20% reduction as default (assumes household past initial 2 months), document limitation
- **Source**: HRS Section 346-53; Hawaii TANF State Plan

---

## Benefit Calculation

### Formula
```
Monthly Benefit = Standard of Assistance (SOA) - Countable Income After Deductions
```

Where:
- **SOA** = 48% of Standard of Need (SON) for applicable household size
- **SOA with 20% Reduction** = SOA * 0.80 (for work-eligible households after 2 months)

If countable income after deductions >= SOA, household is NOT eligible for benefits.

**Source**: Hawaii TANF State Plan; HRS Section 346-53

### Minimum and Maximum Benefits
- **Maximum Benefit**: SOA for household size (or SOA - 20% for work-eligible after 2 months)
- **Minimum Benefit**: Not explicitly specified in sources

---

## Resource/Asset Test

### Asset Limit
- **Disregarded**: Effective April 18, 2013, assets are disregarded under TANF and TAONF programs
- No resource test is applied for eligibility determination

**Source**: Hawaii DHS TANF page (https://humanservices.hawaii.gov/bessd/tanf/)

---

## Demographic Eligibility

### Assistance Unit Composition
- Must include at least one specified relative adult AND a minor dependent child residing in the same home
- **Source**: Hawaii DHS TANF page

### Child Age Requirement
- Minor dependent child under 18 years
- **Source**: HAR 17-656.1-2

### Citizenship/Immigration Requirements
- **TANF**: Family members must be U.S. citizens
- **TAONF**: State-funded program for families with mixed citizen/non-citizen status
- **Source**: Personal Responsibility and Work Opportunity Reconciliation Act of 1996 (P.L. 104-193); Hawaii DHS TANF page

### Work Requirements (Non-Simulatable)
- As a condition of eligibility, recipient families must participate in the First-To-Work Program
- Work eligible individuals must meet work requirements for 21 days before DHS issues the first month of benefits
- **Implementation Note**: Cannot be simulated - document as non-simulatable
- **Source**: Hawaii DHS TANF page; Hawaii TANF State Plan

---

## Housing Assistance Supplement

### First-To-Work Housing Subsidy
- Up to **$500/month** for eligible households participating in First-To-Work program
- **Implementation Note**: This is a separate supplement tied to work program participation; may be implemented as separate variable or noted as non-simulatable
- **Source**: HB2233 SD2 (2022); Hawaii DHS

---

## Implementation Approach

### Use Federal Baseline For:
- [x] Demographic eligibility (age 18 for minor child - matches federal)
- [ ] Immigration eligibility (Hawaii has TANF for citizens only, TAONF for mixed-status - needs state-specific handling)
- [x] Gross income sources (standard employment and self-employment)

### Create State-Specific For:
- Income limits (based on frozen 2006 Hawaii FPL)
- Benefit amounts/payment standards (48% of SON, with 20% reduction option)
- Earned income deductions (20% standard, $200 flat, 36%/55% EIDR)
- Dependent care deduction

### Non-Simulatable (Document Only):
- 60-month lifetime limit
- 55% vs 36% EIDR tier based on months of receipt
- 20% SOA reduction after 2 months
- First-To-Work program participation requirement
- 21-day work requirement before first benefit

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Hawaii TANF State Plan (Effective October 1, 2023)**
   - URL: https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf
   - Expected content: Complete income calculation methodology, deduction details, eligibility rules

2. **Hawaii TANF State Plan FFY 2021-2023**
   - URL: https://humanservices.hawaii.gov/wp-content/uploads/2022/12/1_Hawaii_TANF_State-Plan_FFY-2021-2023-Final_Rev_081722-signed.pdf
   - Expected content: Detailed program rules, income deduction calculations

3. **Hawaii DHS Standards Desk Aid (Effective 01-01-20)**
   - URL: http://www.hawaii.edu/bridgetohope/downloads/UPDATED%20STANDARD%20OF%20ASSISTANCE%20AND%20DESK%20AID%20%20EFF.%2001-01-20%202.pdf
   - Expected content: Complete income/benefit tables by household size

4. **HAR 17-676 (Income)**
   - URL: https://humanservices.hawaii.gov/wp-content/uploads/2019/03/HAR-17-676-INCOME.pdf
   - Expected content: Detailed income definitions, deduction rules

5. **HAR 17-656.1 (TANF)**
   - URL: https://humanservices.hawaii.gov/admin-rules-2/admin-rules-for-programs/
   - Expected content: Complete TANF program rules, definitions, eligibility

6. **Hawaii DHS Databook 2019**
   - URL: https://humanservices.hawaii.gov/wp-content/uploads/2020/07/DHS-Databook-2019-FINAL.pdf#page=9
   - Expected content: Historical benefit tables (relevant for issue #6799)

7. **NCCP TANF Profile (Hawaii)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Hawaii.pdf
   - Expected content: Summary of Hawaii TANF policies, benefit amounts, policy changes

8. **Hawaii TANF Legislative Report (2025)**
   - URL: https://humanservices.hawaii.gov/wp-content/uploads/2024/11/RYamane_2025-HRS-Sect-346-51.5-TANF-Legislative-Report-DHS-BESSD-signed.pdf
   - Expected content: Recent policy updates, benefit information

---

## References for Metadata

### For Parameters:
```yaml
reference:
  - title: "Hawaii Revised Statutes Section 346-53 - Determination of amount of assistance"
    href: "https://law.justia.com/codes/hawaii/title-20/chapter-346/section-346-53/"
  - title: "Hawaii DHS TANF Program Page"
    href: "https://humanservices.hawaii.gov/bessd/tanf/"
```

### For Variables:
```python
reference = (
    "https://law.justia.com/codes/hawaii/title-20/chapter-346/section-346-53/",
    "https://humanservices.hawaii.gov/bessd/tanf/",
)
```

---

## Key Implementation Notes

1. **Frozen FPL**: Hawaii TANF uses 2006 Hawaii FPL values, which have NOT been updated since July 1, 2007. Do NOT use current FPL values.

2. **Standard of Need (SON)**: 100% of 2006 Hawaii FPL (monthly). This is the base for all calculations.

3. **Gross Income Test**: 185% of SON. If gross income exceeds this, household is immediately ineligible.

4. **Standard of Assistance (SOA)**: 48% of SON. This is the maximum benefit amount.

5. **20% Reduction**: For work-eligible households after first 2 months, SOA is reduced by 20% (SOA * 0.80).

6. **EIDR Tier**: 55% for months 1-24, 36% after month 24. Since we cannot track months, default to 55% and document limitation.

7. **Asset Test**: NONE - assets are disregarded since April 2013.

8. **TAONF**: Same rules as TANF but for mixed-status families. Implementation may handle as single variable with citizenship check, or as parallel programs.

---

## Sources Consulted

1. [Hawaii DHS TANF/TAONF Program Page](https://humanservices.hawaii.gov/bessd/tanf/)
2. [Hawaii Revised Statutes Section 346-53](https://law.justia.com/codes/hawaii/title-20/chapter-346/section-346-53/)
3. [2006 HHS Poverty Guidelines](https://aspe.hhs.gov/2006-hhs-poverty-guidelines)
4. [Hawaii TANF State Plan (2023)](https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf)
5. [Hawaii DHS Administrative Rules](https://humanservices.hawaii.gov/admin-rules-2/admin-rules-for-programs/)
6. [Hawaii TANF Strategic Plans Page](https://humanservices.hawaii.gov/tanf-strategic-plans/)
7. [NCCP TANF Profile - Hawaii](https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Hawaii.pdf)
