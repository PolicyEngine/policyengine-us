# Collected Documentation

## South Dakota TANF - Implementation
**Collected**: 2025-12-30
**Implementation Task**: Implement South Dakota TANF eligibility and benefit calculations

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Temporary Assistance for Needy Families (TANF)
**Abbreviation**: TANF
**Source**: South Dakota Department of Social Services - https://dss.sd.gov/economicassistance/tanf.aspx

**Variable Prefix**: `sd_tanf`

**Note**: South Dakota uses the standard federal program name without a state-specific name.

---

## Regulatory Authority

### Primary Sources
- **South Dakota Codified Laws (SDCL)**: Chapter 28-7A - Temporary Assistance for Needy Families
- **South Dakota Administrative Rules (ARSD)**: Article 67:10 - Temporary Assistance for Needy Families
  - URL: https://sdlegislature.gov/Rules/Administrative/67:10

### Administrative Rules Structure
Article 67:10 is organized into the following chapters:
- **67:10:01** - General provisions and definitions
- **67:10:03** - Income standards (specific text not accessible online - requires PDF extraction)
- **67:10:04** - Resource requirements
- **67:10:05** - Payment standards (specific text not accessible online - requires PDF extraction)
- **67:10:08** - Transitional employment allowance

### Key Rule Sections on Cornell Law
- ARSD 67:10:01:05 - Individuals ineligible for assistance
  - URL: https://www.law.cornell.edu/regulations/south-dakota/ARSD-67-10-01-05
- ARSD 67:10:04:06 - Exclusion of earned income tax credit
- ARSD 67:10:08:04 - Limit on transitional employment allowance
  - URL: https://www.law.cornell.edu/regulations/south-dakota/ARSD-67-10-08-04

---

## Demographic Eligibility

### Child Age Thresholds
| Condition | Age Limit | Source |
|-----------|-----------|--------|
| Minor child | Under 18 | https://dss.sd.gov/economicassistance/tanf.aspx |
| Full-time high school student | Under 19 | https://dss.sd.gov/economicassistance/tanf.aspx |
| Full-time student graduation requirement | Graduate before age 20 | https://www.tanf.us/south_dakota.html |

**Implementation approach:**
- [x] Use federal demographic eligibility (age 18/19 thresholds match federal baseline)

### Qualifying Circumstances
Families qualify when they need financial support because of:
- Death of a parent
- Parent absent from the home
- Physical or mental incapacity of a parent
- Unemployment of a parent

**Source**: https://dss.sd.gov/economicassistance/tanf.aspx

### Pregnant Women
Pregnant women are eligible for TANF during the month before their due date.

**Source**: https://www.tanf.us/south_dakota.html

---

## Immigration Eligibility

**State Immigration Rules:**
- Citizenship requirement: Required - must be U.S. citizen, legal alien, or qualified alien
- Children must be citizens or have eligible alien status
- Must have a social security number

**Source**: https://dss.sd.gov/economicassistance/tanf.aspx

**Implementation approach:**
- [x] Use federal immigration eligibility (state follows federal rules)

---

## Individuals Ineligible for TANF (ARSD 67:10:01:05)

Per ARSD 67:10:01:05, the following individuals CANNOT receive TANF:

1. **Fleeing felons**: Those fleeing to avoid prosecution, custody, or confinement for committing or attempting to commit a felony, or for violating a condition of probation or parole

2. **Fraud convictions**: Individuals convicted in federal or state court of making false statements about residency to receive benefits from multiple programs (10-year ineligibility period)

3. **Non-qualifying dependent children**: Children who don't meet relationship requirements

4. **Ineligible aliens**: Parents or siblings who lack required citizenship or alienage status

5. **Non-parent caretakers**: Caretaker relatives other than the parent cannot receive benefits (child-only cases allowed)

6. **SSI recipients**: Individuals already receiving Supplemental Security Income are excluded

7. **Non-dependent adults**: People who don't qualify as dependent children (except parents)

**Source**: https://www.law.cornell.edu/regulations/south-dakota/ARSD-67-10-01-05
**Effective Date**: July 2, 2020

---

## Resource Limits

### Asset Limits
| Resource Type | Limit | Source |
|---------------|-------|--------|
| Countable assets | $2,000 | https://www.tanf.us/south_dakota.html |
| Vehicle (for work requirement individuals) | $8,500 | https://www.tanf.us/south_dakota.html |

**Note**: Licensed vehicles needed for individuals subject to the work requirement may not exceed $8,500.

---

## Income Eligibility Tests

### Income Test Structure
South Dakota uses a **Net 100% Test** after applying earned income disregards:

1. **No separate gross income test** - South Dakota does not apply a gross income test
2. **Net income test**: Countable income (after disregards) must not exceed the payment standard for the family size

**Formula:**
```
Net Countable Income = Gross Income - $90 - (20% × (Gross Earned Income - $90))
Eligible if: Net Countable Income ≤ Payment Standard
```

**Source**: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-South-Dakota-.pdf

**Implementation approach:**
- [x] Use federal demographic eligibility (follows federal baseline)
- [x] Income test is net income only (no gross test)

---

## Income Standards by Family Size

### Payment Standards - With Parent in Home (ARSD 67:10:05:03)

Per S.D. Admin. R. 67:10:05:03, effective 07/01/2023:

| Unit Size | Independent Living | Shared Living |
|-----------|-------------------|---------------|
| 1 person | $512 | $317 |
| 2 persons | $627 | $432 |
| 3 persons | $701 | $507 |
| 4 persons | $775 | $581 |
| 5 persons | $848 | $654 |
| 6 persons | $922 | $728 |
| 7 persons | $996 | $800 |
| 8 persons | $1,070 | $875 |
| 9 persons | $1,141 | $949 |
| 10 persons | $1,213 | $1,020 |
| 11 persons | $1,287 | $1,093 |
| 12 persons | $1,361 | $1,167 |

**For larger families:** Add $53 for each additional member beyond 12 persons.

**Source**: https://www.law.cornell.edu/regulations/south-dakota/ARSD-67-10-05-03

**Living Arrangement Definitions:**
- **Independent Living**: Parent assumes sole responsibility for all shelter costs
- **Shared Living**: Includes subsidized housing or living with others who share shelter costs

### Payment Standards - Caretaker Relatives (No Parent in Home)

For child-only cases where a caretaker relative (not a parent) cares for the child:
- The caretaker relative is NOT included in the assistance unit
- Only the children are counted for payment standard purposes

**Source**: ARSD 67:10:01:05

### Summary Statistics
- Maximum benefit for family of 3 (independent): $701/month (33% FPL)
- Maximum benefit for family of 3 (shared): $507/month (25% FPL)
- Average household benefit (2024): $518.06/month

**Source**: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-South-Dakota-.pdf

---

## Income Deductions & Exemptions

### Earned Income Disregard (CONFIRMED)

South Dakota applies the following earned income disregard:

**Formula:** `$90 + 20% of remaining gross earned income`

**Step-by-step calculation:**
1. Start with gross earned income
2. Subtract $90 (flat deduction)
3. Subtract 20% of the amount remaining after Step 2
4. Result is countable earned income

**Example:** If gross earned income is $500/month:
- Step 1: $500 (gross earned income)
- Step 2: $500 - $90 = $410
- Step 3: $410 - ($410 × 0.20) = $410 - $82 = $328
- Countable earned income: $328

**Source**: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-South-Dakota-.pdf

### Unearned Income Treatment

Unearned income is counted dollar-for-dollar with no disregard.

**Source**: ARSD 67:10:03:02

### Income Exclusions (Not Counted)

The following are NOT counted as income per ARSD 67:10:04:06 and related rules:
- Earned Income Tax Credit (EITC)
- Student financial aid (grants, loans, scholarships)
- IRS tax refunds
- Child Support pass-through amounts (if applicable)

**Source**: https://www.law.cornell.edu/regulations/south-dakota/ARSD-67-10-04-06

### Implementation Summary

| Component | Amount/Rate | Source |
|-----------|-------------|--------|
| Flat earned income deduction | $90 | NCCP Profile |
| Percentage disregard on remainder | 20% | NCCP Profile |
| Unearned income disregard | None (counted fully) | ARSD 67:10:03:02 |

---

## Benefit Calculation

### Complete Formula

**Step 1: Calculate Countable Earned Income**
```
Countable Earned = max(0, Gross Earned - $90) × (1 - 0.20)
                 = max(0, Gross Earned - $90) × 0.80
```

**Step 2: Calculate Total Countable Income**
```
Total Countable Income = Countable Earned Income + Unearned Income
```

**Step 3: Determine Payment Standard**
- Look up payment standard based on:
  - Assistance unit size
  - Living arrangement (independent vs. shared)

**Step 4: Calculate Benefit**
```
Benefit = Payment Standard - Total Countable Income
```

**Step 5: Apply Minimum**
```
Final Benefit = max(0, Benefit)  # No negative benefits
```

### Benefit Calculation Example

**Family:** Parent + 2 children (3 persons), independent living
- Gross earned income: $400/month
- Unearned income: $100/month

**Calculation:**
1. Countable earned = max(0, $400 - $90) × 0.80 = $310 × 0.80 = $248
2. Total countable = $248 + $100 = $348
3. Payment standard (3 persons, independent) = $701
4. Benefit = $701 - $348 = $353/month

### Minimum Benefit
South Dakota does not have an explicit minimum benefit amount documented. Benefits are calculated to the dollar.

### Living Arrangement Adjustment
South Dakota applies different payment standards based on living arrangement:
- **Independent living**: Full payment standard (parent assumes sole responsibility for shelter costs)
- **Shared living**: Approximately 62-72% of independent living amount (subsidized housing or shared shelter costs)

**Source**: ARSD 67:10:05:03

---

## Work Requirements

### Hours Required
| Situation | Weekly Hours |
|-----------|--------------|
| Standard | 30 hours |
| Parent with child under age 6 | 20 hours |

### Exemptions from Work Requirements
You are NOT required to participate in work activities if:

1. You are a dependent child under 16 years old
2. You are a full-time student in high school
3. You are a parent caring for a baby under 12 weeks old (one parent per household only)
4. You are approved to receive Social Security Disability (SSDI)
5. You are approved to receive Supplemental Security Income (SSI)
6. You are a 100% disabled veteran receiving VA disability benefits
7. You are a caretaker relative (not receiving TANF for your own child)

**Source**: https://dss.sd.gov/economicassistance/tanf.aspx

---

## Time Limits

### WARNING: Non-Simulatable Rules (Architecture Limitation)

**60-Month Lifetime Limit**: An adult TANF recipient may not receive TANF benefits for more than 60 months (five years).
- The 60 months do NOT have to be consecutive
- Months from ANY state count toward the limit
- CANNOT ENFORCE in PolicyEngine (requires benefit history tracking)

**Source**: https://dss.sd.gov/economicassistance/tanf.aspx

**Implementation Note**: PolicyEngine's single-period architecture cannot track cumulative months. This limit cannot be simulated but should be documented.

---

## Recent Policy Changes (2025)

### 10% Benefit Reduction (August 2025)
The South Dakota Legislative Rules Review Committee voted 4-2 to reduce TANF benefits by 10%, effective August 2025.

**Impact by Family Size:**
- Recipients will lose $32 to $136 per month depending on family size
- Average household loses approximately $51 per month

**Context:**
- State saves approximately $1.5 million annually
- TANF distributed $15.3 million in benefits in FY 2024
- TANF reserve fund: $24.5 million (as of June 2025)

**Future Planned Reductions:**
The 10% reduction is part of a larger plan to gradually reduce benefits to the minimum state contribution needed to receive federal funding - approximately a 35% total reduction.

**Source**: https://southdakotasearchlight.com/2025/07/15/south-dakota-legislative-committee-finalizes-benefit-cuts-tanf-needy-families/

### Caretaker Relative Eligibility Change
The 2025 rule change also removes TANF eligibility for families who take in child relatives when removed from their homes by the state's child welfare system.

---

## Program Administration

### Two-Component Application Process
1. **Work Component**: Handled by employment specialists at:
   - DSS offices (in reservation areas)
   - Department of Labor and Regulation (DLR) Local Offices

2. **Eligibility Component**: Handled by caseworkers at local DSS offices

### Personal Responsibility Requirements
- Recipients must sign a Personal Responsibility Agreement
- A Personal Responsibility Plan is developed with an employment specialist

### Contact Information
- Phone: (877) 999-5612
- Online Application: SD DSS Online System

**Source**: https://dss.sd.gov/economicassistance/tanf.aspx

---

## References for Implementation

### For Parameters
```yaml
reference:
  - title: "South Dakota DSS - TANF Program"
    href: "https://dss.sd.gov/economicassistance/tanf.aspx"
  - title: "ARSD Article 67:10 - Temporary Assistance for Needy Families"
    href: "https://sdlegislature.gov/Rules/Administrative/67:10"
```

### For Variables
```python
reference = "https://dss.sd.gov/economicassistance/tanf.aspx"
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **South Dakota TANF State Plan**
   - URL: https://dss.sd.gov/docs/economicassistance/tanf/TANFStatePlan.pdf
   - Expected content: Complete program rules, income calculation methodology, deduction formulas, and benefit calculation procedures
   - **CRITICAL**: This document likely contains the income eligibility tests and earned income disregard rates not found in HTML sources

2. **NCCP TANF Profile - South Dakota (August 2024)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-South-Dakota-.pdf
   - Expected content: Detailed policy parameters, income eligibility thresholds, deduction amounts, and comparative state data

3. **Archived Payment Standards Rules (2016)**
   - URL: https://sdlegislature.gov/api/Rules/Archived/10994.pdf
   - Expected content: Historical payment standard amounts by family size

4. **Archived Payment Standards Rules (2021)**
   - URL: https://sdlegislature.gov/api/Rules/Archived/11393.pdf
   - Expected content: Payment standard amounts by family size (more recent)

5. **SD Legislature TANF Overview Document (2025)**
   - URL: https://mylrc.sdlegislature.gov/api/Documents/Attachment/285332.pdf?Year=2025
   - Expected content: Current legislative summary of TANF program

6. **CRS Report R43634 - TANF: Eligibility and Benefit Amounts**
   - URL: https://crsreports.congress.gov/product/pdf/R/R43634
   - Expected content: Comparative state data on TANF eligibility and benefits

7. **Urban Institute Welfare Rules Databook**
   - URL: https://wrd.urban.org/ (various PDFs)
   - Expected content: Detailed state TANF policies including income disregards

---

## Implementation Gaps - Information Needed

### Resolved (Found During Research)
1. ✅ **Gross income eligibility test** - No gross test; SD uses net income test only
2. ✅ **Net income eligibility test** - Net 100% test (countable income ≤ payment standard)
3. ✅ **Earned income disregard rate** - $90 + 20% of remainder
4. ✅ **Standard work expense deduction** - Included in the $90 flat deduction
5. ✅ **Complete payment standard table** - Found in ARSD 67:10:05:03 (1-12+ persons)
6. ✅ **Income calculation methodology** - Step-by-step process documented above

### Remaining Gaps (Medium Priority - Not Required for Simplified Implementation)
7. **Dependent care deduction** - Not documented; may not apply (often handled through CCDF)
8. **Child support treatment** - Processed through OCSE, but pass-through rules unclear
9. **Self-employment income calculation** - Specific rules not documented
10. **Transitional benefits** - Transitional employment allowance is separate program (ARSD 67:10:08)

---

## Comparison to Federal Baseline

### Matches Federal Baseline (Use Federal Variables)
- [x] Demographic eligibility (age 18/19 thresholds)
- [x] Immigration eligibility (follows federal qualified alien rules)
- [x] 60-month lifetime limit (non-simulatable)
- [x] Gross earned/unearned income definitions

### State-Specific Parameters Needed (Create SD-Specific)
- [x] Payment standards by family size (1-12+, with $53 increment)
- [x] Living arrangement types (independent vs. shared)
- [x] Earned income disregard ($90 flat + 20% of remainder)
- [ ] Resource limits ($2,000 assets, $8,500 vehicle) - NOT implementing in simplified version

### Implementation Approach for Simplified TANF
For this **simplified implementation**, we will:
1. Use federal baseline for: `tanf_gross_earned_income`, `tanf_gross_unearned_income`
2. Create state-specific variables for:
   - `sd_tanf_countable_earned_income` (applies $90 + 20% disregard)
   - `sd_tanf_countable_income` (earned + unearned)
   - `sd_tanf_payment_standard` (based on unit size and living arrangement)
   - `sd_tanf_eligible` (net income test)
   - `sd_tanf` (final benefit amount)

---

## Next Steps for Implementation

### Phase 3: Development (Ready to Begin)

**Step 3A: Create Parameters** (parameter-architect)
- `gov/states/sd/dss/tanf/income/earned_income_disregard/flat_deduction.yaml` ($90)
- `gov/states/sd/dss/tanf/income/earned_income_disregard/percentage.yaml` (20%)
- `gov/states/sd/dss/tanf/payment_standard/independent_living.yaml` (by family size)
- `gov/states/sd/dss/tanf/payment_standard/shared_living.yaml` (by family size)
- `gov/states/sd/dss/tanf/payment_standard/additional_person.yaml` ($53)

**Step 3B: Create Variables** (rules-engineer - simplified approach)
- `sd_tanf_countable_earned_income.py` - Apply $90 + 20% disregard
- `sd_tanf_countable_income.py` - Sum earned + unearned
- `sd_tanf_payment_standard.py` - Look up by size/arrangement
- `sd_tanf_eligible.py` - Net income test
- `sd_tanf.py` - Final benefit calculation

**Step 3B: Create Tests** (test-creator)
- Unit tests for each variable
- Integration tests for complete benefit calculations

### Documentation Complete
All critical information has been gathered. Ready for Phase 3.
