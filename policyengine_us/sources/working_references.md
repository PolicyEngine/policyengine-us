# Collected Documentation

## New Hampshire TANF (FANF) Implementation
**Collected**: 2025-12-28
**Implementation Task**: Implement New Hampshire Financial Assistance to Needy Families (FANF) program

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Financial Assistance to Needy Families (FANF)
**Abbreviation**: FANF
**Source**: RSA 167:77 et seq.; He-W 601.04

**Variable Prefix**: `nh_fanf` (e.g., `nh_fanf_eligible`, `nh_fanf_countable_income`)

**Sub-Programs Under FANF**:
- New Hampshire Employment Program (NHEP) - Work participation required
- Family Assistance Program (FAP) - No work requirements
- Interim Disabled Parent (IDP) - For families with disabled parents
- Families With Older Children (FWOC) - For 19-year-olds in high school

All sub-programs have the same cash eligibility requirements and benefit limits.

---

## Regulatory Authority

### New Hampshire Revised Statutes (RSA)
- **RSA Chapter 167**: Public Assistance to Blind, Aged, or Disabled Persons, and to Dependent Children
- **RSA 167:77**: Statement of Purpose - NH Employment Program and Family Assistance Program
- **RSA 167:77-g**: Adjustment of TANF Financial Assistance (60% FPG provision)
- **RSA 167:79**: Employment Program; Eligibility

**Source URLs**:
- https://gc.nh.gov/rsa/html/xii/167/167-77.htm
- https://gc.nh.gov/rsa/html/xii/167/167-77-g.htm
- https://gc.nh.gov/rsa/html/xii/167/167-79.htm

### New Hampshire Administrative Rules
- **He-W 600**: Financial Assistance and Eligibility for Medical Care
- **He-W 601**: Definitions
- **He-W 606**: General Verification Requirements

**Source URL**: https://gc.nh.gov/rules/state_agencies/he-w600.html

### Family Assistance Manual (FAM)
- **FAM 203**: TANF (Temporary Assistance for Needy Families)
- **FAM 403**: Resource Limits
- **FAM 601**: Standards and Budget Tables
- **FAM 603**: Deductions and Disregards

**Source URL**: https://www.dhhs.nh.gov/fam_htm/

---

## Demographic Eligibility

### Age Requirements
- **Minor child age limit**: Under 18 years old
- **Full-time student age limit**: Under 19 years old (if enrolled full-time in high school or equivalency program)
- **FWOC program**: Age 19 up to 20 for full-time high school students

**Source**: RSA 167:79(I); NH DHHS TANF website

**Implementation approach**:
- [x] Use federal demographic eligibility (age 18/19 matches federal definition)

### Deprivation Requirement
The dependent child must be deprived of parental support or care by reason of:
- Death of a parent
- Continued absence from the home
- Physical or mental incapacity of a parent
- Unemployment or underemployment of a parent

**Source**: RSA 167:79(I)

### Household Composition
The following must be included in the assistance group (if living in household or temporarily absent):
- Any dependent child
- All minor blood-related or step-relatives
- Parent or caretaker relative

**Source**: RSA 167:79(II)

---

## Immigration Eligibility

### Citizenship Requirements
- Must be a United States citizen, OR
- Must meet the citizenship requirements established in PRWORA (Personal Responsibility and Work Opportunity Reconciliation Act), as amended

**Source**: RSA 167:79(IV)(c)

**Implementation approach**:
- [x] Use federal immigration eligibility (state follows federal PRWORA rules)

---

## Income Eligibility Tests

### Single Income Test
NH FANF uses a single income test comparing net countable income to the payment standard (60% FPG).

**Formula**: Net Countable Income <= Payment Standard (60% FPG)

**Source**: RSA 167:77-g; FAM 601 Table B

### Payment Standard / Income Limit (60% FPG)
Per RSA 167:77-g, effective July 1, 2017:
> "The maximum monthly cash benefit under this subdivision shall be equal to 60 percent of the federal poverty guidelines, based upon the applicable household size and composition, as determined annually by the United States Department of Health and Human Services."

**Implementation approach**: Store as rate (0.60), not dollar amounts. The payment standard = 60% of monthly FPG for household size.

**2024 Payment Standards (60% FPG - Monthly)**:

| Household Size | 60% FPG (Monthly) |
|----------------|-------------------|
| 1 | $753 |
| 2 | $1,022 |
| 3 | $1,291 |
| 4 | $1,560 |
| 5 | $1,829 |
| 6 | $2,098 |
| 7 | $2,367 |
| 8 | $2,636 |
| Each additional | +$269 |

**Note**: These amounts update annually based on FPG published in the Federal Register.

**Parameter**: Store as `fpg_rate: 0.60` and calculate from federal poverty guidelines.

**Source**:
- RSA 167:77-g
- SR 24-07 Dated 03/24
- https://law.justia.com/codes/new-hampshire/2022/title-xii/title-167/section-167-77-g/

---

## Income Deductions & Exemptions

### For Applicants: 20% Employment Expense Disregard
A 20% disregard of gross earned income is applied as an employment expense disregard.

**Formula**: Countable Earned Income = Gross Earned Income * (1 - 0.20)

**Level**: Per PERSON (applies to each employed individual)

**Source**: SR 97-03 Dated 02/97; FAM 603

### For Recipients: 50% Earned Income Disregard
Financial assistance recipients receive a continuing 50% earned income disregard (replaces the old $30 and 1/3 rule).

**Formula**: Countable Earned Income = Gross Earned Income * (1 - 0.50)

**Level**: Per PERSON (applies to each employed individual)

**Who qualifies**:
- Current financial assistance recipients
- Applicants who have received TANF financial assistance in at least one of the last six months

**Source**: SR 97-03 Dated 02/97; FAM 603

### WARNING: Time-Limited Disregard (Partially Simulatable)
The 50% earned income disregard for recipients vs 20% for applicants represents a time-based distinction that PolicyEngine cannot fully track.

**Implementation Note**: Since PolicyEngine cannot track whether someone is a new applicant vs continuing recipient, we should implement the **50% disregard** as the standard (more favorable to recipients) and document the limitation.

### Child Support Treatment
**CRITICAL**: The $50 child support disregard has been ELIMINATED.

The full amount of direct child support is counted as unearned income in determining eligibility and benefit amounts. New Hampshire does not allow any child support funds to pass through to FANF recipients.

**Source**: SR 97-03 Dated 02/97

### SSI Exclusion
SSI (Supplemental Security Income) is NOT counted as income for FANF eligibility purposes.

**Source**: NH DHHS policy

---

## Unearned Income
Unearned income is generally counted in full (no disregard) with the following exception:
- SSI is excluded entirely

**Source**: FAM 603; SR 97-03

---

## Benefit Calculation

### Formula
```
Benefit = Payment Standard - Net Countable Income
```

Where:
- **Payment Standard** = 60% of FPG for household size (monthly)
- **Net Countable Income** = Countable Earned Income + Countable Unearned Income

### Calculation Steps
1. Calculate gross earned income
2. Apply earned income disregard (50% for recipients, 20% for applicants)
3. Result = Countable Earned Income
4. Add Countable Unearned Income (full amount, excluding SSI)
5. Result = Net Countable Income
6. Get Payment Standard for household size (60% FPG)
7. If Net Countable Income <= Payment Standard: Eligible
8. Benefit = Payment Standard - Net Countable Income

**Source**: SR 97-03 Dated 02/97; FAM 603

### Payment Method
FANF cash assistance is issued twice per month via:
- Electronic Funds Transfer (EFT) - direct deposit
- Electronic Benefit Transfer (EBT) - debit-style card

---

## Resource / Asset Limits

### Resource Limit
**Amount**: $1,000 countable resources

**Source**: FAM 403; CLASP reports confirm NH has $1,000 TANF asset limit

### Vehicle Exclusion
**Rule**: One vehicle per adult assistance group member is excluded, regardless of value or ownership.

If the assistance group has more than one vehicle per adult member, they choose which vehicle(s) to exclude.

**Source**: SR 97-03 Dated 02/97; SR 01-12 Dated 07/01

### Other Resource Exclusions
- Home (primary residence)
- Household furniture
- Life insurance equity value (excluded)

**Source**: SR 97-03 Dated 02/97

---

## Non-Simulatable Rules (Architecture Limitation)

### 60-Month Lifetime Limit
**Rule**: FANF recipients can receive cash assistance for a maximum of 60 months (consecutive or nonconsecutive).

**CANNOT ENFORCE** - requires tracking benefit history across multiple periods. PolicyEngine uses single-period simulation.

**Exception**: FAP cases (Family Assistance Program) are exempt from this lifetime limit.

**Source**: RSA 167:82; NH DHHS TANF website

### Work Requirements (NHEP)
**Rule**: NHEP participants must work, seek employment, or attend job readiness programs.

**CANNOT TRACK** - requires tracking work participation over time.

**Source**: RSA 167:82

### Applicant vs Recipient Status
**Rule**: Different earned income disregard rates apply:
- 20% for applicants
- 50% for recipients (or those who received TANF in past 6 months)

**PARTIALLY SIMULATABLE** - Cannot track prior receipt. Implementation uses 50% disregard (recipient rate) as default.

---

## Implementation Approach Summary

### Use Federal Baseline Variables For:
- [x] Demographic eligibility (age 18/19 matches federal)
- [x] Immigration eligibility (follows federal PRWORA rules)
- [x] Gross earned income sources
- [x] Gross unearned income sources

### Create State-Specific Variables For:
- [ ] `nh_fanf_countable_earned_income` - Apply 50% disregard
- [ ] `nh_fanf_countable_income` - Earned + Unearned (excluding SSI)
- [ ] `nh_fanf_payment_standard` - 60% FPG by household size
- [ ] `nh_fanf_income_eligible` - Compare income to payment standard
- [ ] `nh_fanf_resources_eligible` - $1,000 resource limit
- [ ] `nh_fanf_eligible` - Combine all eligibility tests
- [ ] `nh_fanf` - Final benefit calculation

### Parameters Needed:
- `income/earned_income_disregard_rate` - 0.50 (50%)
- `payment_standard/fpg_rate` - 0.60 (60% of FPG)
- `resources/limit` - $1,000

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **New Hampshire's Cash Assistance (TANF) policy - NCCP**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-New-Hampshire.pdf
   - Expected content: Detailed TANF policy profile including income disregards, benefit amounts

2. **Bureau of Family Assistance Fact Sheet**
   - URL: https://www.dhhs.nh.gov/sites/g/files/ehbemt476/files/documents2/bfa-progam-fact-sheet.pdf
   - Expected content: Current eligibility requirements, income limits, resource limits by program

3. **BFA Program Net Monthly Income Limits**
   - URL: https://www.dhhs.nh.gov/sites/g/files/ehbemt476/files/documents2/bfa-program-net-monthly-income-limits.pdf
   - Expected content: Current income limit tables by household size for all BFA programs

4. **New Hampshire TANF State Plan**
   - URL: https://www.dhhs.nh.gov/sites/g/files/ehbemt476/files/documents2/tanf-state-plan.pdf
   - Expected content: Official state plan submitted to ACF with program details

5. **ACF Welfare Rules Databook (July 2023)**
   - URL: https://acf.gov/sites/default/files/documents/opre/opre-graphical-overview-tanf-policies-dec2024.pdf
   - Expected content: Comprehensive state-by-state TANF policy comparison

6. **NH Bureau of Family Assistance Fact Sheet (2022)**
   - URL: https://nhfv.org/wp-content/uploads/2022/06/fam-asst-fact-sheet-3-22.pdf
   - Expected content: Older fact sheet with eligibility and benefit information

---

## Key Online References

### Official NH DHHS Sources
- NH DHHS TANF Main Page: https://www.dhhs.nh.gov/temporary-assistance-needy-families-tanf
- FAM Manual: https://www.dhhs.nh.gov/fam_htm/
- Administrative Rules He-W 600: https://gc.nh.gov/rules/state_agencies/he-w600.html

### Legal Sources
- RSA Chapter 167: https://www.gencourt.state.nh.us/rsa/html/nhtoc/nhtoc-xii-167.htm
- RSA 167:77-g (60% FPG): https://law.justia.com/codes/new-hampshire/2022/title-xii/title-167/section-167-77-g/

### Policy Updates (SR Documents)
- SR 25-09 (March 2025 updates): https://www.dhhs.nh.gov/sr_htm/html/sr_25-09_dated_03_25.htm
- SR 24-07 (March 2024 updates): https://www.dhhs.nh.gov/sr_htm/html/sr_24-07_dated_03_24.htm
- SR 97-03 (Original TANF implementation): https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm

### Third-Party Analysis
- NH Fiscal Policy Institute analysis: https://nhfpi.org/blog/under-enrollment-in-key-aid-program-and-increased-available-funds-provide-opportunities-for-enhanced-outreach-and-assistance/

---

## References for Metadata

### For Parameters:
```yaml
reference:
  - title: RSA 167:77-g - Adjustment of TANF Financial Assistance
    href: https://gc.nh.gov/rsa/html/xii/167/167-77-g.htm
  - title: SR 24-07 Dated 03/24 - FPG Updates
    href: https://www.dhhs.nh.gov/sr_htm/html/sr_24-07_dated_03_24.htm
```

### For Variables:
```python
reference = "https://gc.nh.gov/rsa/html/xii/167/167-77-g.htm"
# Or for multiple:
reference = (
    "https://gc.nh.gov/rsa/html/xii/167/167-77-g.htm",
    "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
)
```

---

## Validation Checklist

- [x] URLs load and show actual values
- [x] Legal code references included (RSA 167:77-g, RSA 167:79)
- [x] Values match sources exactly
- [x] Effective dates documented (60% FPG effective July 1, 2017)
- [x] Identified all eligibility tests
- [x] Documented BOTH earned AND unearned income treatment
- [x] Flagged non-simulatable rules (60-month limit, work requirements)
- [x] Documented deduction levels (per PERSON)
- [x] Confirmed no child support disregard/passthrough
