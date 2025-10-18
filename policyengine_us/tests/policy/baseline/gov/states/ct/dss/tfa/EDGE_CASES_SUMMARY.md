# Connecticut TFA Edge Case Tests - Summary

## Overview
This document summarizes the comprehensive edge case test suite created for the Connecticut Temporary Family Assistance (TFA) program. These tests are designed to prevent "what about X?" review comments by systematically testing boundary conditions, extreme values, and corner cases.

## Test Files Created

### 1. income_boundaries.yaml
**Purpose**: Tests income eligibility at critical FPL thresholds

**Key Edge Cases Covered**:
- Income exactly at 55% FPL (initial eligibility threshold)
- Income one dollar below/above 55% FPL
- Income exactly at 100% FPL (continuing eligibility threshold)
- Income one dollar below/above 100% FPL
- Income exactly at 171% FPL (extension benefit reduction threshold)
- Income one dollar below/above 171% FPL
- Income exactly at 230% FPL (maximum extension eligibility)
- Income one dollar below/above 230% FPL
- Threshold calculations for various family sizes (2, 3, 4, 5, 8)

**Total Test Cases**: 17 tests

**Why These Matter**:
- <= vs < comparison at thresholds
- Extension period trigger points
- Benefit reduction application
- Eligibility cutoffs

---

### 2. resource_limits.yaml
**Purpose**: Tests asset eligibility at $6,000 limit

**Key Edge Cases Covered**:
- Assets exactly at $6,000 limit
- Assets one dollar below/above $6,000
- Zero assets (minimum)
- Very small assets ($100)
- Mid-range assets ($3,000)
- Assets moderately over limit ($6,500, $7,000)
- Assets well over limit ($10,000)
- Large families at asset limit (tests size independence)
- High income/low assets combination
- Low income/high assets combination

**Total Test Cases**: 15 tests

**Why These Matter**:
- Asset limit is independent of family size
- Tests boundary comparisons (<=)
- Validates independence of income and asset tests

---

### 3. household_size.yaml
**Purpose**: Tests very large families and household size extremes

**Key Edge Cases Covered**:
- Single person household (pregnant woman) - minimum size
- Family of 9 (one beyond standard 8-person tables)
- Family of 10-20 (stress testing)
- Three-generation household
- Size 8 at FPL table boundary
- Size 10+ income eligibility calculations
- Large family at 230% FPL extension limit

**Total Test Cases**: 13 tests

**Why These Matter**:
- FPL calculation beyond 8-person base
- $448 per additional person increment
- Parameter file limits (capped at size 20)
- Ensures formulas work for unusual household sizes

---

### 4. age_boundaries.yaml
**Purpose**: Tests children at age 18 boundary and student status

**Key Edge Cases Covered**:
- Child exactly age 18 (not a student) - ineligible
- Child exactly age 18 (full-time student) - eligible
- Child age 17 (just under 18) - eligible
- Child age 19 (full-time student) - ineligible
- Newborn (age 0)
- Multiple children at boundary with mixed student status
- Young parent age 18 with infant
- Teen parent age 16 with infant
- Children spanning ages 15-19
- Age 18 in vocational school

**Total Test Cases**: 15 tests

**Why These Matter**:
- Documentation: "Children age 18 enrolled full-time in high school or vocational school"
- Student status determines eligibility at age 18
- Age 19+ not eligible even as student
- Tests demographic eligibility rules

---

### 5. family_cap.yaml
**Purpose**: Tests family cap rules for children born within 10 months

**Key Edge Cases Covered**:
- Family cap application (50% reduction on increment)
- Size transitions: 2→3, 3→4, 4→5, 5→6
- First child (no cap)
- Twins born within 10 months (both subject to cap)
- Large family adds child (size 7→8, 8→9)
- Teen parent with multiple children
- Child exactly 10 months old (boundary)
- Child 11 months old (just after cap period)
- Pregnant woman (no children yet)
- Triplets (three children subject to cap)

**Total Test Cases**: 14 tests

**Why These Matter**:
- 50% reduction creates fractional amounts
- Tests increment calculation: payment_standard[n] - payment_standard[n-1]
- Different regions have different increments
- Family cap exceptions (first child to minor parent)

---

### 6. zero_negative_values.yaml
**Purpose**: Tests handling of zero and negative income/asset values

**Key Edge Cases Covered**:
- Zero employment income
- Zero assets
- Negative self-employment income (business loss)
- Large negative income exceeding positive income
- Zero income AND zero assets (maximum need)
- Very small income ($1/year)
- Very small assets ($1)
- Mixed income netting to zero (W-2 + self-employment loss)
- Zero earned income with positive unearned income
- All income from SSI (fully disregarded)
- Smallest possible positive values ($0.01)

**Total Test Cases**: 17 tests

**Why These Matter**:
- max_() function prevents negative countable income
- Tests robustness against unusual input
- Validates graceful handling of edge cases
- Self-employment losses common in real data

---

### 7. mixed_demographics.yaml
**Purpose**: Tests pregnant women and complex household structures

**Key Edge Cases Covered**:
- Pregnant woman alone (no children)
- Pregnant woman with existing children
- Elderly caregiver (age 60+) with grandchild
- Three-generation household
- Both parents disabled with children
- Parent with disabled child
- Multiple disabled children
- Teen parent living with grandparent
- Non-parent guardian (relative caregiver)
- Foster parent with foster children
- Single father (male caregiver)
- Two-parent households (one/both working)
- Pregnant teen
- Blended family (step-children)
- Adopted children
- Parent with infant under 1 year
- All household members disabled
- Older pregnant woman (over 40)

**Total Test Cases**: 20 tests

**Why These Matter**:
- Pregnant women qualify per documentation
- Tests work requirement exemptions
- Validates various family structures
- Non-parent guardian assets not counted
- Disability exemptions

---

### 8. rounding_precision.yaml
**Purpose**: Tests fractional benefit amounts and calculation precision

**Key Edge Cases Covered**:
- Income resulting in fractional benefits ($0.50)
- 20% extension reduction (creates $139.60, $558.40)
- 50% family cap reduction (creates $67.50)
- Income exactly at $90 disregard
- Benefit of exactly $0.01 (smallest positive)
- Monthly income with repeating decimals (divide by 12)
- FPL threshold calculation precision
- Very small countable income (pennies/month)
- Benefit amount exactly at $0.99
- Odd income amounts ($1,111.11)
- 171% FPL boundary precision
- Multiple disregards creating fractional amounts
- SSI disregard with fractional amounts
- Child support at exactly $50 pass-through
- Extremely low monthly income ($1/month)
- Asset limit precision ($5,999.99)
- Combined reductions (family cap AND extension)

**Total Test Cases**: 19 tests

**Why These Matter**:
- 20% reduction: $698 * 0.80 = $558.40
- 50% cap: $135 * 0.50 = $67.50
- Floating point comparison precision
- Cumulative precision errors
- Tests whether cents are handled correctly

---

## Test Coverage Summary

| Category | Test Cases | Critical Boundaries |
|----------|-----------|-------------------|
| Income Boundaries | 17 | 55%, 100%, 171%, 230% FPL |
| Resource Limits | 15 | $6,000 asset limit |
| Household Size | 13 | Size 1, 8, 9+, 20 |
| Age Boundaries | 15 | Age 18, student status |
| Family Cap | 14 | 10 months, 50% reduction |
| Zero/Negative Values | 17 | $0, negative amounts |
| Mixed Demographics | 20 | Pregnant, disabled, multi-gen |
| Rounding/Precision | 19 | Fractional amounts, cents |
| **TOTAL** | **130** | **Multiple dimensions** |

## Edge Case Categories Addressed

### 1. Boundary Conditions
- **At threshold**: Income/assets exactly at limit
- **Just below**: One dollar below threshold
- **Just above**: One dollar above threshold
- Tests whether comparisons use < or <=

### 2. Extreme Values
- **Minimum**: Zero income, zero assets, age 0
- **Maximum**: Size 20 household, 230% FPL, $10k+ assets
- **Negative**: Business losses, negative income

### 3. Calculation Precision
- **Fractional amounts**: 20% reduction, 50% cap
- **Rounding**: Division by 12, repeating decimals
- **Cumulative errors**: Multiple reductions compound

### 4. Special Rules
- **Family cap**: 50% reduction on increment
- **Extension period**: 20% benefit reduction
- **Disregards**: $90 earned, SSI, child support
- **Student income**: Full disregard

### 5. Demographic Edge Cases
- **Age**: Exactly 18, student status
- **Pregnancy**: Alone, with children, teen
- **Disability**: Parent, child, all members
- **Guardianship**: Non-parent, foster, relative

### 6. Household Structure
- **Size extremes**: 1 to 20 members
- **Generations**: Single, two, three generations
- **Relationships**: Step-children, adopted, foster

## Known Limitations

### Tests That Cannot Be Fully Validated Yet

1. **TFA Application Date Tracking**
   - Family cap requires knowing when TFA was applied
   - Current implementation may not track application dates
   - Tests assume family cap applies to newborns (age 0)

2. **Vehicle Exclusion ($9,500)**
   - Requires detailed vehicle asset tracking
   - May not be fully implemented in current variables
   - Tests focus on general $6,000 asset limit

3. **Extension Period Status**
   - Requires tracking when household entered extension period
   - Tests assume extension eligibility based on income only
   - Actual 6-month time limit may need additional tracking

4. **Regional Payment Differences**
   - Historical regions (A, B, C) still in parameters
   - Post-July 2022: statewide uniform rates at 55% FPL
   - Tests use historical regional rates from 2014

## Validation Approach

### How to Use These Tests

1. **Run all edge case tests**:
   ```bash
   policyengine-core test policyengine_us/tests/policy/baseline/gov/states/ct/dss/tfa/ -c policyengine_us -v
   ```

2. **Run specific edge case file**:
   ```bash
   policyengine-core test policyengine_us/tests/policy/baseline/gov/states/ct/dss/tfa/income_boundaries.yaml -c policyengine_us -v
   ```

3. **Review failures carefully**:
   - Check if expected values are correct
   - Verify formulas match documentation
   - Ensure parameters are accurate

### Expected Failures

Some tests may initially fail due to:
- Parameter values needing updates (2024 rates vs 2014 rates)
- Variables not fully implemented (family cap tracking)
- Implementation differences from documentation

These failures are **valuable** - they highlight areas needing attention.

## Review Checklist

When reviewing this implementation, use these tests to verify:

- [ ] All income thresholds calculate correctly (55%, 100%, 171%, 230% FPL)
- [ ] Asset limit enforced at exactly $6,000
- [ ] Age 18 eligibility depends on student status
- [ ] Family cap reduces increment by 50%
- [ ] Extension period reduces benefit by 20%
- [ ] Zero income households receive maximum benefit
- [ ] Negative self-employment income handled gracefully
- [ ] Large families (9+) use $448 per additional person
- [ ] Fractional amounts handled with appropriate precision
- [ ] All demographic categories eligible (pregnant, disabled, elderly)

## Preventing Future Issues

This edge case test suite helps prevent:

1. **Off-by-one errors**: Tests at, above, and below every threshold
2. **Sign errors**: Tests negative values explicitly
3. **Rounding errors**: Tests fractional amounts and precision
4. **Boundary errors**: Tests <= vs < comparisons
5. **Size limit errors**: Tests beyond standard tables (size 8+)
6. **Missing validations**: Tests zero and extreme values

## References

- **Connecticut TANF State Plan 2024-2026**: https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf
- **Connecticut General Statutes § 17b-112**: https://www.cga.ct.gov/current/pub/chap_319s.htm
- **CT TFA Fact Sheet**: https://portal.ct.gov/dss/knowledge-base/articles/fact-sheets-and-brochures-articles/fact-sheets-articles/tfa-fact-sheet
- **Working References**: /Users/ziminghua/vscode/policyengine-us/working_references.md

---

**Generated**: October 14, 2025
**Branch**: ct-tfa-implementation
**Test Suite Version**: 1.0
**Total Edge Cases**: 130 tests across 8 categories
