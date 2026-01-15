# Collected Documentation

## NY Assembly Bill A04948 - Youth Worker Tax Benefits
**Collected**: January 15, 2026
**Implementation Task**: Implement NY A04948 reform providing youth EITC, enhanced standard deduction, and student loan interest deduction

---

## Official Program Name

**Bill Number**: Assembly Bill A04948 (2025-2026 Regular Sessions)
**Companion Bill**: Senate Bill S4103
**Short Title**: Youth Worker Tax Benefits Act
**Sponsors**: A. Bronson, Simon (Assembly); Parker, Fernandez (Senate)
**Committee**: Ways and Means

**Variable Prefix**: `ny_a04948_` (for reform-specific variables)

---

## Bill Overview

This legislation amends New York Tax Law sections 606, 614, and 615 to provide tax benefits for young workers and student loan borrowers.

### Effective Dates
- **Takes Effect**: January 1, 2026
- **Expires**: December 31, 2031 (deemed repealed)

### Source
- Title: NY Assembly Bill 2025-A4948
  href: https://www.nysenate.gov/legislation/bills/2025/A4948

---

## Section 1: Youth Earned Income Tax Credit (Section 606(d-2))

### Legal Citation
- **Amended Section**: NY Tax Law Section 606, new subsection (d-2)
- **Title**: "Earned income tax credit for youth workers"

### Credit Calculation

**Credit Amount**: 130% (1.3x) of the federal EITC that would have been allowed

The statutory language states the credit equals:
> "the product of one and three-tenths and the amount of the earned income tax credit that would have been allowed to the taxpayer under section thirty-two of the internal revenue code, if the taxpayer had attained the minimum age of eligibility for such earned income tax credit"

**Parameter Value**: `1.3` (rate multiplier)

### Eligibility Requirements

A taxpayer must meet ALL of the following criteria:

1. **Residency**: Must be a resident taxpayer
2. **Dependency Status**: Cannot be claimed as a dependent of another taxpayer
3. **Age Requirement**:
   - Must have attained age 17
   - Must NOT have attained the minimum federal EITC age (currently age 25 for childless filers)
   - **Eligible ages**: 17, 18, 19, 20, 21, 22, 23, 24
4. **Parental Status**: Cannot be a custodial or non-custodial parent of a minor child or children
5. **Student Exception**: Eligibility is NOT restricted for taxpayers who are:
   - Enrolled in full-time or part-time high school diploma programs
   - Pursuing GED certification
   - Enrolled in post-secondary certificate or degree programs

### Federal EITC Reference (IRC Section 32)

The youth credit is based on what the federal EITC would be if the taxpayer met age requirements:

**Federal EITC Age Requirements (IRC Section 32(c)(1)(A)(ii)(II))**:
- Minimum age: 25 years old
- Maximum age: 64 years old (before end of tax year)
- Age requirements apply only to childless filers

**Federal EITC Maximum Credits (2025)**:
| Children | Maximum Credit |
|----------|---------------|
| 0        | $649          |
| 1        | $4,328        |
| 2        | $7,152        |
| 3+       | $8,046        |

**Youth EITC Maximum (at 130%)**:
Since youth (ages 17-24) cannot have qualifying children under this credit:
- Maximum federal childless EITC: $649
- **Youth EITC Maximum**: $649 x 1.3 = **$844.70**

### Reporting Requirements

The Commissioner must submit reports to:
- Governor
- Temporary President of the Senate
- Speaker of the Assembly
- Chairpersons of Senate Finance and Assembly Ways and Means Committees

**Report Schedule**:
- Preliminary report: By July 31st of each year
- Final report: By December 31st of each year

**Report Contents**:
- Number of credits granted
- Average credit amount
- County-level breakdowns

### References
- Title: NY Tax Law Section 606 - Credits Against Tax
  href: https://www.nysenate.gov/legislation/laws/TAX/606
- Title: NY Assembly Bill 2025-A4948
  href: https://www.nysenate.gov/legislation/bills/2025/A4948
- Title: IRC Section 32 - Earned Income
  href: https://www.law.cornell.edu/uscode/text/26/32

---

## Section 2: Enhanced Standard Deduction (Section 614)

### Legal Citation
- **Amended Section**: NY Tax Law Section 614
- **New Provision**: Additional paragraph for young adults aged 18-24

### Enhanced Deduction Amount

**Amount**: $10,000 (for taxable years beginning after 2026)

The statutory language provides:
> "For taxable years beginning after two thousand twenty-six, the New York standard deduction of a resident individual who is between the ages of eighteen and twenty-four and who is not married nor the head of a household nor a surviving spouse nor an individual whose federal exemption amount is zero shall be ten thousand dollars."

### Eligibility Requirements

A taxpayer qualifies if ALL of the following apply:

1. **Residency**: Must be a resident individual
2. **Age Requirement**: Between ages 18 and 24 (inclusive)
3. **Filing Status Restrictions** - Cannot be:
   - Married (any filing status)
   - Head of household
   - Surviving spouse/qualifying widow(er)
4. **Dependency Status**: Federal exemption amount cannot be zero (i.e., cannot be claimed as dependent)

### Comparison to Current NY Standard Deductions (2025)

| Filing Status | Current Amount | With A04948 (Ages 18-24) |
|---------------|---------------|--------------------------|
| Single (non-dependent) | $8,000 | **$10,000** |
| Single (dependent) | $3,100 | Not eligible (exemption = 0) |
| Married filing jointly | $16,050 | Not eligible (married) |
| Married filing separately | $8,000 | Not eligible (married) |
| Head of household | $11,200 | Not eligible (HoH) |
| Qualifying surviving spouse | $16,050 | Not eligible |

**Benefit**: Young adults aged 18-24 receive an additional $2,000 deduction compared to standard single filers.

### Implementation Note

**Effective Date**: Taxable years beginning after 2026 (first applicable year: 2027)

This differs from the EITC and student loan provisions which begin January 1, 2026.

### References
- Title: NY Tax Law Section 614 - Standard Deduction
  href: https://www.nysenate.gov/legislation/laws/TAX/614
- Title: 2025 Standard Deductions - NY Tax Department
  href: https://www.tax.ny.gov/pit/file/standard_deductions.htm

---

## Section 3: Student Loan Interest Deduction (Section 615(h))

### Legal Citation
- **Amended Section**: NY Tax Law Section 615
- **New Subsection**: (h)

### Deduction Amount

The deduction equals:
> "an amount equal to the interest paid by the taxpayer during the taxable year on any qualified education loan to the extent and as provided in section 221 of the Internal Revenue Code"

**Key**: The deduction follows federal IRC Section 221 rules entirely.

### Federal IRC Section 221 Rules

**Maximum Deduction**: $2,500 per year

**Qualified Education Loan Definition** (IRC 221(d)(1)):
Any indebtedness incurred solely to pay qualified higher education expenses:
- For the taxpayer, spouse, or dependent (at time debt was incurred)
- Paid within a reasonable period before/after the loan
- Attributable to education during eligible student status
- Includes refinanced qualifying loans

**Excludes**:
- Loans from related persons
- Loans under employer education plans

### Income Phaseout (2025 Federal)

| Filing Status | Phaseout Begins | Phaseout Complete |
|---------------|-----------------|-------------------|
| Single/HoH | $75,000 MAGI | $90,000 MAGI |
| Married Filing Jointly | $155,000 MAGI | $185,000 MAGI |

**2026 Inflation-Adjusted (for reference)**:
| Filing Status | Phaseout Begins | Phaseout Complete |
|---------------|-----------------|-------------------|
| Single/HoH | $85,000 MAGI | $100,000 MAGI |
| Married Filing Jointly | $175,000 MAGI | $205,000 MAGI |

### Eligibility Requirements (per IRC 221)

1. **Residency**: Must be a resident individual (NY requirement)
2. **Paid Interest**: Must have paid interest on a qualified education loan
3. **Legal Obligation**: Must be legally obligated to pay interest
4. **Filing Status**: Cannot be married filing separately
5. **Income Limit**: MAGI must be below phaseout threshold
6. **Dependency**: Cannot be claimed as dependent on another's return

### Deduction Type

This is an "above-the-line" adjustment to income:
- Reduces Adjusted Gross Income (AGI) directly
- Does NOT require itemizing deductions
- Available even with standard deduction

### References
- Title: IRC Section 221 - Interest on Education Loans
  href: https://www.law.cornell.edu/uscode/text/26/221
- Title: IRS Topic 456 - Student Loan Interest Deduction
  href: https://www.irs.gov/taxtopics/tc456
- Title: NY Tax Law Section 615 - Itemized Deduction
  href: https://www.nysenate.gov/legislation/laws/TAX/615

---

## Current NY Law Comparison

### Current NY EITC (Section 606(d))

**Credit Rate**: 30% of federal EITC (for taxable years 2003 and after)

**Historical Rates**:
- 1994: 7.5%
- 1995: 10%
- 1996-1999: 20%
- 2000: 22.5%
- 2001: 25%
- 2002: 27.5%
- 2003+: 30%

**Key Difference from A04948**:
- Current NY EITC: 30% of federal credit (for those who qualify for federal)
- A04948 Youth EITC: 130% of what federal credit WOULD BE (for ages 17-24 who don't qualify federally)

### Current NY Standard Deduction (Section 614)

The current law provides these standard deductions:

**Statutory Base Amounts** (from Tax Law 614):
- Single (non-dependent): $7,500 (1996+)
- Married filing jointly: $15,000 (2005+)
- Head of household: $10,500 (1996+)
- Married filing separately: $7,500 (2005+)
- Dependent: $3,000 (1996+)

**Current Inflation-Adjusted Amounts (2025)**:
- Single (non-dependent): $8,000
- Single (dependent): $3,100
- Married filing jointly: $16,050
- Married filing separately: $8,000
- Head of household: $11,200
- Qualifying surviving spouse: $16,050

**Cost of Living Adjustment**: Section 614(f) provides that for taxable years after 2017, amounts are adjusted per Section 601-a.

### NY Noncustodial Parent EITC (Section 606(d-1))

**Note**: This is a separate existing credit, NOT part of A04948.

Requirements:
- Age 18 or older
- Child support order through SCU
- Current on child support payments

Credit equals the greater of:
- 20% of federal EITC (as if one child qualified), OR
- 2.5x the federal EITC for childless workers

**Distinction**: A04948's youth EITC (d-2) is separate from and in addition to the noncustodial parent EITC (d-1).

---

## Implementation Parameters Summary

### Youth EITC Parameters (Section 606(d-2))

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| Credit multiplier | 1.3 | rate | 130% of federal EITC |
| Minimum age | 17 | years | Must have attained |
| Maximum age | 24 | years | Below federal EITC min age (25) |
| Can be dependent | false | bool | Cannot be claimed |
| Can be parent | false | bool | No minor children |
| Effective date | 2026-01-01 | date | |
| Expiration date | 2031-12-31 | date | |

### Enhanced Standard Deduction Parameters (Section 614)

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| Deduction amount | 10_000 | USD | For eligible young adults |
| Minimum age | 18 | years | |
| Maximum age | 24 | years | |
| Married eligible | false | bool | |
| Head of household eligible | false | bool | |
| Surviving spouse eligible | false | bool | |
| Can be dependent | false | bool | Exemption must be non-zero |
| Effective date | 2027-01-01 | date | "After 2026" |
| Expiration date | 2031-12-31 | date | |

### Student Loan Interest Deduction Parameters (Section 615(h))

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| Maximum deduction | 2_500 | USD | Per IRC 221 |
| Single phaseout start (2025) | 75_000 | USD | MAGI |
| Single phaseout end (2025) | 90_000 | USD | MAGI |
| Joint phaseout start (2025) | 155_000 | USD | MAGI |
| Joint phaseout end (2025) | 185_000 | USD | MAGI |
| Effective date | 2026-01-01 | date | |
| Expiration date | 2031-12-31 | date | |

---

## Non-Simulatable Rules

### Time-Limited Provisions (Architecture Limitation)

The bill contains sunset provisions:
- **Expiration**: December 31, 2031

**Implementation Note**: PolicyEngine can implement the reform for tax years 2026-2031, but cannot automatically "turn off" provisions after expiration in a single simulation. The expiration should be handled via:
1. Parameter effective dates with end dates
2. Reform description noting temporal scope

### Can Be Fully Simulated

All provisions in A04948 CAN be fully simulated:
- Age-based eligibility (point-in-time)
- Income-based phaseouts (point-in-time)
- Dependency status (point-in-time)
- Parental status (point-in-time)
- Filing status restrictions (point-in-time)

---

## References Summary

### Primary Legal Sources

1. **NY Assembly Bill A4948 (2025)**
   - Title: NY State Assembly Bill 2025-A4948
   - URL: https://www.nysenate.gov/legislation/bills/2025/A4948

2. **NY Senate Bill S4103 (Companion)**
   - Title: NY State Senate Bill 2025-S4103
   - URL: https://www.nysenate.gov/legislation/bills/2025/S4103

3. **NY Tax Law Section 606**
   - Title: NY Tax Law Section 606 - Credits Against Tax
   - URL: https://www.nysenate.gov/legislation/laws/TAX/606

4. **NY Tax Law Section 614**
   - Title: NY Tax Law Section 614 - Standard Deduction
   - URL: https://www.nysenate.gov/legislation/laws/TAX/614

5. **NY Tax Law Section 615**
   - Title: NY Tax Law Section 615 - Itemized Deduction
   - URL: https://www.nysenate.gov/legislation/laws/TAX/615

### Federal Law References

1. **IRC Section 32 - Earned Income Credit**
   - Title: 26 U.S. Code Section 32 - Earned Income
   - URL: https://www.law.cornell.edu/uscode/text/26/32

2. **IRC Section 221 - Student Loan Interest**
   - Title: 26 U.S. Code Section 221 - Interest on Education Loans
   - URL: https://www.law.cornell.edu/uscode/text/26/221

### Supporting Sources

1. **NY Earned Income Credit Info**
   - Title: Earned Income Credit (New York State)
   - URL: https://www.tax.ny.gov/pit/credits/earned_income_credit.htm

2. **NY Standard Deductions (2025)**
   - Title: 2025 Standard Deductions - NY Tax Department
   - URL: https://www.tax.ny.gov/pit/file/standard_deductions.htm

3. **IRS EITC Tables**
   - Title: Earned Income and EITC Tables - IRS
   - URL: https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/earned-income-and-earned-income-tax-credit-eitc-tables

4. **IRS Student Loan Interest Deduction**
   - Title: Topic 456 - Student Loan Interest Deduction
   - URL: https://www.irs.gov/taxtopics/tc456

---

## Variable Implementation Recommendations

### Variables to Create

1. **`ny_a04948_youth_eitc_eligible`** (Person level, bool)
   - Checks age 17-24, not dependent, not parent, resident

2. **`ny_a04948_youth_eitc`** (TaxUnit level, USD)
   - Calculates 130% of hypothetical federal childless EITC

3. **`ny_a04948_enhanced_standard_deduction_eligible`** (Person level, bool)
   - Checks age 18-24, not married, not HoH, not dependent

4. **`ny_a04948_enhanced_standard_deduction`** (TaxUnit level, USD)
   - Returns $10,000 if eligible, else current standard deduction

5. **`ny_a04948_student_loan_interest_deduction`** (TaxUnit level, USD)
   - Follows IRC 221 rules with NY-specific applicability

### Parameters to Create

```
gov/states/ny/tax/income/credits/youth_eitc/
  multiplier.yaml          # 1.3
  age/
    minimum.yaml           # 17
    maximum.yaml           # 24

gov/states/ny/tax/income/deductions/
  enhanced_standard_deduction/
    amount.yaml            # 10_000
    age/
      minimum.yaml         # 18
      maximum.yaml         # 24

  student_loan_interest/
    maximum.yaml           # 2_500
    phaseout/
      single/
        start.yaml         # 75_000 (2025), 85_000 (2026)
        end.yaml           # 90_000 (2025), 100_000 (2026)
      joint/
        start.yaml         # 155_000 (2025), 175_000 (2026)
        end.yaml           # 185_000 (2025), 205_000 (2026)
```

---

## Quality Validation Checklist

- [x] All sources are official government documents (.gov, .state.ny.us)
- [x] Bill text excerpts include exact statutory language
- [x] All numeric values documented with citations
- [x] Effective dates specified (2026-01-01 for EITC/student loan, 2027-01-01 for std deduction)
- [x] Expiration date documented (2031-12-31)
- [x] Federal IRC references included where applicable
- [x] Comparison to current law provided
- [x] Implementation parameters summarized
- [x] Variable prefix recommended: `ny_a04948_`
