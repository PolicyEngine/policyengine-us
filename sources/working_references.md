# Collected Documentation

## Kentucky TANF (K-TAP) Implementation
**Collected**: 2025-12-04
**Implementation Task**: Kentucky TANF (K-TAP) Program - Simplified Implementation
**GitHub Issue**: #6908

---

## Source Information

### Primary Legal Authority
- **Title**: 921 KAR 2:016 - Standards of need and amount for the Kentucky Transitional Assistance Program (KTAP)
- **Citation**: 921 KAR 2:016
- **URL**: https://apps.legislature.ky.gov/law/kar/titles/921/002/016/
- **Effective Date**: 2023 (major update from 1995 levels)

### Secondary Legal Authority
- **Title**: 921 KAR 2:006 - Technical requirements for the Kentucky Transitional Assistance Program (KTAP)
- **Citation**: 921 KAR 2:006
- **URL**: https://apps.legislature.ky.gov/law/kar/titles/921/002/006/
- **Effective Date**: 2023

### Program Website
- **Title**: Kentucky Transitional Assistance Program (KTAP)
- **URL**: https://www.chfs.ky.gov/agencies/dcbs/dfs/fssb/Pages/ktap.aspx

---

## Key Rules and Thresholds

### Payment Standards by Family Size (2023+)
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

### Standard of Need by Family Size (2023+)
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

### Gross Income Limits by Family Size (2023+)
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

### Resource Limits
Per 921 KAR 2:016 Section 3:
- **Liquid Asset Limit**: $10,000
- **Excluded Resources**: IRAs, burial funds, 529 college savings accounts, ABLE accounts, Individual Development Accounts (up to $15,000 when matched)

---

## Income Deductions and Disregards

### Work Expense Standard Deduction
Per 921 KAR 2:016 Section 5(3)(a):
- **Amount**: $175 for full-time AND part-time employment
- **Purpose**: Covers mandatory paycheck deductions, union dues, and tools

### Dependent Care Disregard
Per 921 KAR 2:016 Section 5(3)(b):
- **Full-time employment**: Up to $175/month per individual
- **Part-time employment**: Up to $150/month per individual
- **Child under age 2**: Up to $200/month per individual

### Earned Income Disregard
Per 921 KAR 2:016 Section 5(3)(e):
- **Amount**: First 50% of earned income
- **Duration**: 6 months
- **Availability**: Two-time only disregard per employed adult member of the benefit group
- **Note**: For new employment acquired after approval and reported timely, the disregard covers 6 full calendar months earnings

### Child Support Exclusion
Per 921 KAR 2:016 Section 5(2)(v):
- **Amount**: First $50 of child support payment is excluded

---

## Benefit Calculation Formula

Per 921 KAR 2:016 Section 9(3)-(4):

```
Step 1: Calculate Deficit
  deficit = standard_of_need - countable_income

Step 2: Apply 45% Ratable Reduction
  reduced_deficit = deficit * 0.55  (equivalent to applying 45% reduction)

Step 3: Determine Benefit Amount
  benefit = min(reduced_deficit, payment_maximum)
```

In other words:
- A 45% ratable reduction is applied to the deficit between countable income and standard of need
- The assistance payment equals the LESSER of:
  1. 55% of the deficit between countable income and standard of need, OR
  2. The payment maximum for the family size

---

## Eligibility Requirements

### Demographic Eligibility (921 KAR 2:006)

**Age Requirements for Children:**
- Age 15 or younger, OR
- Ages 16-18 in regular full-time school attendance, OR
- Under 18 and a high school graduate

**Deprivation Requirements:**
Children must be deprived of parental support due to one of:
1. **Death** of a parent
2. **Absence** of a parent (voluntary or involuntary):
   - Divorce, desertion 30+ days, birth out-of-wedlock
   - Incarceration 30+ days, long-term hospitalization, deportation
3. **Incapacity** of a parent (physical/mental disability lasting 30+ days)
4. **Unemployment** of at least one parent (if both parents in home):
   - Working fewer than 100 hours monthly
   - Prior labor market attachment: $1,000 earned in preceding 24 months (note: this requirement was eliminated in 2023 updates)

**Living Arrangements:**
- Child must live with specified relative (blood, adoptive, or by marriage)
- Children absent 30+ consecutive days lose eligibility (exceptions for medical care, school, college, foster care, family visits)

### Citizenship/Immigration Requirements (921 KAR 2:006)
- U.S. citizens are eligible
- Qualified aliens who entered before August 22, 1996 are eligible
- Qualified aliens entering on/after August 22, 1996 face 5-year eligibility bar with exceptions for:
  - Refugees and asylees
  - Trafficking victims
  - Military veterans and active duty members
  - Afghan/Iraqi special immigrants

**Implementation Approach:**
- [x] Use federal immigration eligibility (follows federal rules)

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limits
- **60-Month Lifetime Limit**: KTAP cannot be provided for more than 60 cumulative months to a benefit group that includes an adult (CANNOT ENFORCE - requires history tracking)
- **Hardship Extensions**: Available for domestic violence victims, disabled individuals, grandparents caring for children (CANNOT TRACK - requires case management data)

### Time-Limited Benefits (Applied Always - Cannot Track Duration)
- **Earned Income Disregard**: 50% for first 6 months (APPLIED ALWAYS - cannot track months)
- **Two-Time Only Disregard**: Two lifetime uses per adult (CANNOT TRACK - requires history)

### Work Requirements
- Must register for work and participate in Kentucky Works Program (KWP) (NOT MODELED - program requirement, not eligibility calculation)

### Sanctions
- 25% benefit reduction for failure to cooperate with child support (NOT MODELED - requires case-specific determination)

---

## References for Metadata

### For Parameters (YAML format):
```yaml
# Payment standards, need standards, gross income limits
reference:
  - title: "921 KAR 2:016 - Standards of need and amount for KTAP"
    href: "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"

# Work expense deduction
reference:
  - title: "921 KAR 2:016 Section 5(3)(a)"
    href: "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"

# Dependent care deduction
reference:
  - title: "921 KAR 2:016 Section 5(3)(b)"
    href: "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"

# Earned income disregard
reference:
  - title: "921 KAR 2:016 Section 5(3)(e)"
    href: "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"

# Child support exclusion
reference:
  - title: "921 KAR 2:016 Section 5(2)(v)"
    href: "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"

# Resource limits
reference:
  - title: "921 KAR 2:016 Section 3"
    href: "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"

# Technical requirements (eligibility)
reference:
  - title: "921 KAR 2:006 - Technical requirements for KTAP"
    href: "https://apps.legislature.ky.gov/law/kar/titles/921/002/006/"
```

### For Variables (Python format):
```python
# Use reference URL format
reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
# NOTE: Do NOT use documentation field - use reference URL instead
```

---

## Historical Notes

### Pre-2023 Values (For Reference Only)
Prior to 2023, Kentucky KTAP used values that had not been updated since 1995:
- Payment maximum for family of 1: $186 (vs $372 in 2023)
- Resource limit: $2,000 (vs $10,000 in 2023)
- Work expense deduction: $90 (vs $175 in 2023)
- Earned income disregard: $30 + 1/3 for 4 months, then $30 only for 8 months (vs 50% for 6 months in 2023)

### 2023 Policy Changes Summary
Per Kentucky Youth Advocates and KY Policy:
- Doubled payment amounts to adjust for inflation since 1995
- Raised resource limit from $2,000 to $10,000
- Increased work expense deduction from $90 to $175
- Simplified earned income disregard to 50% for 6 months
- Increased income eligibility levels
- Eliminated prior labor market attachment requirement for unemployment deprivation

---

## Additional Sources Consulted

- Kentucky Cabinet for Health and Family Services KTAP page
- Cornell Law Institute: https://www.law.cornell.edu/regulations/kentucky/921-KAR-2-016
- Cornell Law Institute: https://www.law.cornell.edu/regulations/kentucky/921-KAR-2-006
- Kentucky Youth Advocates: https://kyyouth.org/celebrating-much-needed-ktap-updates/
- Kentucky Policy: https://kypolicy.org/kentuckys-basic-cash-assistance-program-just-got-a-much-needed-update/

---

## PDFs Requiring Extraction

The following PDFs contain additional information but were not fully extractable:

1. **Kentucky TANF State Plan 2023**
   - URL: https://www.chfs.ky.gov/agencies/dcbs/dfs/fssb/Documents/Kentucky%20TANF%20State%20Plan%202023.pdf
   - Purpose: Contains comprehensive state plan details including EBT restrictions and fee information
   - Note: Most critical information (payment standards, income rules) was obtained from the Kentucky Administrative Regulations

2. **Division of Family Support Operation Manual Volume III**
   - URL: https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLIII.pdf
   - Purpose: Detailed procedural guidance for KTAP implementation
   - Note: Could not be fetched due to access restrictions; regulations provide sufficient detail for implementation

3. **KTAP Fact Sheet 2024**
   - URL: https://khbe.ky.gov/About/2024%20Docs/KTAP-Fact-Sheet.pdf
   - Purpose: Current program summary
   - Note: Key values confirmed through regulatory sources

**Documentation Status**: The Kentucky Administrative Regulations (921 KAR 2:016 and 921 KAR 2:006) provide all necessary information for a simplified implementation. PDF extraction is not required for implementation to proceed.
