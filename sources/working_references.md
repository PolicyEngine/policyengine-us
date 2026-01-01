# Collected Documentation

## Alaska Temporary Assistance Program (ATAP) - Alaska TANF Implementation
**Collected**: 2025-12-31
**Implementation Task**: Research and document Alaska's TANF program (ATAP) for PolicyEngine implementation

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Alaska Temporary Assistance Program
**Abbreviation**: ATAP
**Source**: AS 47.27 (Alaska Statutes Chapter 27) and 7 AAC 45 (Alaska Administrative Code)

**Variable Prefix**: `ak_atap` (e.g., `ak_atap_eligible`, `ak_atap_countable_income`)

---

## Legal Authority

### Primary Sources
1. **Alaska Statutes**: AS 47.27 - Alaska Temporary Assistance Program
2. **Alaska Administrative Code**: 7 AAC 45 - Alaska Temporary Assistance Program (Title 7, Part 3, Chapter 45)
3. **Policy Manual**: Alaska DPA Temporary Assistance Manual (dpaweb.hss.state.ak.us/manuals/ta/)

---

## Demographic Eligibility

### Dependent Child Definition
- **Under age 18**: Eligible as dependent child
- **Age 18 and under 19**: Eligible ONLY if full-time student
- **Source**: 7 AAC 45.990(a)(13); AS 47.27.900(9)

**Implementation approach:**
- [ ] Use federal demographic eligibility (age 18/19 matches federal)
- [x] Create state-specific age thresholds (state matches federal standard)

### Full-Time Student Definition (7 AAC 45.475)
- Vocational training: 30 hours/week (25 hours if no shop practices)
- College/university: 12+ semester/quarter credit hours
- High school: 25 hours/week
- Correspondence course: 25 hours/week

### Part-Time Student
- Does not qualify as full-time
- Pursues at least half the course load of comparable full-time program

---

## Immigration Eligibility (7 AAC 45.215)

**State Immigration Rules:**
- Citizenship requirement: Required (U.S. citizen or national)
- Legal permanent residents: Eligible if "qualified alien" per 8 U.S.C. 1641
- Sponsored aliens: 3-year ineligibility period (unless sponsor no longer exists)
- Temporary residents (Immigration Reform and Control Act of 1986): 5-year disqualification (except Cuban/Haitian entrants)
- Canadian Indians: Eligible with at least 50% Native Indian blood (per 8 U.S.C. 1359)

**Source**: 7 AAC 45.215

**Implementation approach:**
- [x] Use federal immigration eligibility (state follows federal qualified alien rules)
- [ ] Create state-specific immigration rules

---

## Resource Limits

### Standard Limits
| Household Type | Resource Limit |
|---------------|----------------|
| Standard household | $2,000 |
| Household with member age 60+ | $3,000 |

**Source**: AS 47.27.010; Official Alaska DPA website

### Exempt Resources (7 AAC 45.300)
- Primary residence (home)
- Household goods and personal property
- Most vehicles
- Tools, machinery necessary for income production
- Funeral agreements (up to $1,500 equity value)
- First $2,000 of Alaska Native Claims Settlement Act (ANCSA) distributions retained annually
- Luxury items with equity value of $1,000 or less

---

## Income Eligibility - TWO-TIER TEST

### Test 1: Gross Income Test (185% Standard)
**Total nonexempt gross monthly income must be equal to or less than the 185% standard**

### Test 2: Net Income Test (Need Standard)
**Countable income (after deductions) must be equal to or less than the need standard**

**Source**: 7 AAC 45.470

**Critical Rule**: If income exceeds EITHER limit by $0.01 or more, benefits are denied/terminated.

---

## Income Standards (7 AAC 45.520)

### Adult-Included Standards (One Caretaker or Two Able-Bodied Parents)

| Household Size | 185% Standard | Need Standard |
|---------------|---------------|---------------|
| 1 | (pregnant woman - see below) | (pregnant woman - see below) |
| 2 | $1,522 | $823 |
| 3 | $1,739 | $940 |
| 4 | $1,956 | $1,057 |
| 5 | $2,173 | $1,174 |
| 6 | $2,390 | $1,291 |
| 7 | $2,607 | $1,408 |
| 8 | $2,824 | $1,525 |
| 9 | $2,955 | $1,597 |
| 10 | $3,086 | $1,669 |
| 11+ | Add for each additional person | Add for each |

**Note**: Values shown are from 7 AAC 45.520 and are adjusted annually by the SSI cost-of-living percentage increase.

### Adult-Included Standards (Two Parents, One Incapacitated)

| Household Size | 185% Standard | Need Standard |
|---------------|---------------|---------------|
| 3 | $1,955 | $1,057 |

### Child-Only Standards (No Caretaker in Unit)

| Number of Children | 185% Standard | Need Standard |
|-------------------|---------------|---------------|
| 1 child | $956 | $517 |
| 2 children | $1,173 | $634 |
| 3 children | $1,390 | $751 |
| Each additional | +$217 | +$117 |

### Pregnant Woman Standard (No Other Eligible Children)

| | 185% Standard | Need Standard |
|--|---------------|---------------|
| Pregnant woman | $1,089 | $589 |

**Source**: 7 AAC 45.520

---

## Maximum Payment Levels (7 AAC 45.523)

### One Caretaker with Dependent Child(ren)
- Base: **$821** for assistance unit with one caretaker relative and one dependent child
- Additional: **+$102** for each additional child

### Second Parent (if incapacitated)
- **+$102** if second parent cannot perform gainful activity

### Child-Only (Non-Needy Relative Care)
- Base: **$452** for one dependent child
- Additional: **+$102** for each additional child

### Pregnant Woman (No Children)
- **$514** per month

**Source**: 7 AAC 45.523; AS 47.27.025

---

## Benefit Calculation Formula (7 AAC 45.525)

### Step-by-Step Calculation

1. **Determine applicable need standard** based on assistance unit type and size
2. **Subtract countable income** (after all deductions per 7 AAC 45.470(b))
3. **Subtract shelter reduction** if applicable (7 AAC 45.527-45.530)
4. **Apply payment formula**:
   ```
   ATAP Payment = (Step 3 Result) x (Maximum Payment for 2 persons) / (Need Standard for 2 persons)
   ```

### Rounding Rules
- Carry cents throughout calculation
- Round DOWN from $0.99 (e.g., $25.99 becomes $25)

### Minimum Payment
- Payments below $10/month are NOT issued
- Exception: If payment is below $10 only due to mandatory recoupment, payment IS issued

**Source**: 7 AAC 45.525

---

## Earned Income Deductions

### Initial Deduction (First-time or Returning Applicants)
For individuals who have NOT received ATAP in the preceding 4 months:
- **$90 deduction** from gross monthly earned income

**Also applies to**: Stepparents not in unit, disqualified alien parents, parents of minor parents

**Source**: 7 AAC 45.480(a)

### Tiered Work Incentive Deductions (7 AAC 45.480(b))
For recipients who HAVE received ATAP within the previous 4 months:

| Period | Deduction Formula |
|--------|-------------------|
| Months 1-12 | $150 + 33% of remaining earned income |
| Months 13-24 | $150 + 25% of remaining earned income |
| Months 25-36 | $150 + 20% of remaining earned income |
| Months 37-48 | $150 + 15% of remaining earned income |
| Months 49-60 | $150 + 10% of remaining earned income |
| After month 60 | $150 flat (no percentage) |

**Source**: 7 AAC 45.480(b)

### Child Care and Incapacitated Parent Care Disregard (7 AAC 45.485)

| Care Type | Maximum Monthly Disregard |
|-----------|--------------------------|
| Child under age 2 | $200 per dependent |
| Child age 2 and older | $175 per dependent |
| Incapacitated parent | $175 |

**Note**: Only charges for anticipated hours of work plus reasonable commuting time are disregarded if provider charges hourly.

**Source**: 7 AAC 45.485

### Child-Student Earned Income Disregard (7 AAC 45.475)
- Earned income of dependent child who is a full-time or part-time student is **completely disregarded**

---

## Unearned Income Deductions

### Child Support
- Recipients must surrender child support payments to Child Support Services Agency
- Recipients may retain **up to $50** of child support payment monthly
- Amounts over $50 count as unearned income AND non-cooperation

**Source**: 7 AAC 45.400

---

## Shelter Cost Reduction (7 AAC 45.527)

### Standard Shelter Allowance
- **30% of the assistance unit's need standard**

### Low Shelter Cost Reduction
For assistance units WITH caretaker relatives:
- Reduction = Standard Shelter Allowance - Actual Allowable Shelter Costs
- If reduction < $1, reduction = $0

For child-only units (no caretaker): **No reduction** based on shelter costs

**Source**: 7 AAC 45.527

### Utility Regions (7 AAC 45.531)
Alaska has 6 utility regions for determining standard utility allowances:
1. Central (Anchorage Borough, Matanuska-Susitna Borough)
2. Northern (Fairbanks North Star Borough, North Slope Borough, Southeast Fairbanks, Yukon-Koyukuk)
3. Northwest (Nome, Northwest Arctic Borough)
4. Southcentral (Aleutians, Bristol Bay, Kenai, Kodiak, etc.)
5. Southeast (Juneau, Ketchikan, Sitka, etc.)
6. Southwest (Bethel, Wade Hampton)

---

## Two-Parent Family Rules

### Household Size Calculation
- For families with two able-bodied parents: **only one parent counts** toward household size
- Exception: If one parent is incapacitated, different standards apply

### Summer Benefit Reduction
- Benefits are **reduced** for two-parent families during **July, August, and September**
- Rationale: Better employment opportunities during summer months

**Source**: Official Alaska DPA website; AS 47.27.025(d)

---

## Time Limits

### 60-Month Lifetime Limit
- Maximum 60 months (5 years) of ATAP benefits
- Federal TANF requirement

### Extensions (7 AAC 45.610)
Extensions granted for:
1. **Domestic Violence**: Victim currently or recently experiencing domestic violence
2. **Disability**: Unable to perform gainful activity; or caring for disabled child that interferes with work
3. **Hardship**: Circumstances beyond family's control prevent work participation

**Source**: 7 AAC 45.610

---

## Exempt Income Sources

The following are NOT counted as income:
- ATAP supportive service payments (child care, transportation, work expenses)
- AmeriCorps/Senior Corps volunteer payments
- VA vocational rehabilitation payments
- Heating Assistance Program payments
- Alaska Housing Finance Corporation utility assistance
- PASS I, II, III childcare payments
- Aleut/Japanese restitution payments (P.L. 100-383)
- Federal disaster assistance
- Work-study program income (adults and children)
- Title IV Higher Education grants/scholarships
- ANCSA Alaska Native corporation payments
- ATAP retroactive corrective payments (7 AAC 45.405)

**Source**: 7 AAC 45.470; DPA Manual

---

## Non-Simulatable Rules (Architecture Limitation)

### Cannot Enforce - Requires History
- **60-month lifetime limit**: Cannot track cumulative months of benefits
- **Tiered earned income disregard progression**: Cannot track which "tier" recipient is in (months 1-12, 13-24, etc.)
- **4-month lookback for deduction eligibility**: Cannot determine if person received ATAP in preceding 4 months
- **Summer reduction for two-parent families**: Cannot automatically detect July-September without period-specific logic

### Implementation Approach for Time-Limited Deductions
Since we cannot track the time-based progression, implement the MOST FAVORABLE deduction tier (Months 1-12: $150 + 33%) with a comment noting the limitation.

---

## Partially Simulatable (Time-Limited Benefits)

### Earned Income Disregard Tiers
- **Applied assumption**: Use Tier 1 (Months 1-12): $150 + 33% of remaining earned income
- **Cannot track**: Progression through tiers over time

### Child Support Passthrough
- **$50 passthrough** - Can be simulated as monthly exclusion

---

## References for Implementation

### For Parameters
```yaml
reference:
  - title: "7 AAC 45.520 - Qualifying standards"
    href: "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.520"
  - title: "7 AAC 45.523 - Maximum payment levels"
    href: "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523"
  - title: "7 AAC 45.480 - Deductions from income"
    href: "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.480"
```

### For Variables
```python
reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.470"
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Alaska TANF State Plan**
   - URL: https://aws.state.ak.us/OnlinePublicNotices/Notices/Attachment.aspx?id=105752
   - Expected content: Complete state plan submitted to federal government, may contain additional policy details

2. **NCCP TANF Profile - Alaska (2024)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Alaska-.pdf
   - Expected content: Summary of Alaska TANF policies, benefit amounts, income limits

3. **Alaska Program Descriptions**
   - URL: https://health.alaska.gov/media/lorb0pgw/program-descriptions.pdf
   - Expected content: Overview of DPA programs including ATAP

---

## Key Implementation Notes

### Income Calculation Order
1. Start with gross earned income
2. Apply $90 or tiered deduction ($150 + %)
3. Apply child/dependent care disregard
4. Add unearned income (child support above $50, etc.)
5. Result = Countable income for need standard test

### Eligibility Logic
1. Check resource limit ($2,000 or $3,000 for elderly)
2. Check gross income vs 185% standard (Test 1)
3. Calculate countable income with all deductions
4. Check countable income vs need standard (Test 2)
5. Both tests must pass for eligibility

### Benefit Calculation
```
Benefit = max(0, (Need Standard - Countable Income - Shelter Reduction)
          * (Max Payment for 2) / (Need Standard for 2))
```
- Round down to nearest dollar
- Minimum $10 to issue payment

---

## Sources

- [Alaska Temporary Assistance Program (ATAP) | State of Alaska](https://health.alaska.gov/en/services/alaska-temporary-assistance/)
- [7 AAC 45 - Alaska Temporary Assistance Program | Cornell Law](https://www.law.cornell.edu/regulations/alaska/title-7/part-3/chapter-45)
- [7 AAC 45.520 - Qualifying standards](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.520)
- [7 AAC 45.523 - Maximum payment levels](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523)
- [7 AAC 45.525 - Determining the amount of payment](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.525)
- [7 AAC 45.470 - Income eligibility](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.470)
- [7 AAC 45.480 - Deductions from income](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.480)
- [7 AAC 45.475 - Child-student earned income disregard](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.475)
- [7 AAC 45.485 - Incapacitated-parent and child care disregard](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.485)
- [7 AAC 45.215 - Citizenship or legal alien status](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.215)
- [7 AAC 45.527 - Standard shelter allowance](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.527)
- [7 AAC 45.531 - Utility regions](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.531)
- [7 AAC 45.610 - Sixty-month time limit](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.610)
- [7 AAC 45.335 - Assistance unit composition](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.335)
- [7 AAC 45.400 - Child support treatment](https://www.law.cornell.edu/regulations/alaska/7-AAC-45.400)
- [Alaska DPA Work Incentive Deductions Manual](http://dpaweb.hss.state.ak.us/manuals/ta/700/760/760-2_work_incentive_deductions.htm)
- [Alaska Law Help - Cash Assistance](https://alaskalawhelp.org/resource/cash-or-rental-assistance-options-in-Alaska)
