# Florida TANF Documentation Summary

**Issue**: #6723
**Date**: October 21, 2025
**Status**: ✅ Documentation Complete

## Documentation Location

All documentation has been saved in: `/docs/agents/sources/fl_tanf/`

### Files Created:
1. **README.md** - Overview and quick reference
2. **eligibility.md** - Complete eligibility requirements
3. **benefit_calculation.md** - Detailed benefit calculation methodology
4. **special_provisions.md** - Florida-specific policies and rules
5. **working_references.md** - Consolidated implementation reference (repository root)

## Key Findings

### Program Overview
- **Program Name**: Temporary Cash Assistance (TCA) - Florida's TANF program
- **Administering Agency**: Florida Department of Children and Families (DCF)
- **Current Recipients**: ~34,000 families, ~44,000 children (November 2023)

### Legal Authority

**Federal**:
- 42 U.S.C. § 601 et seq. (Personal Responsibility and Work Opportunity Reconciliation Act of 1996)

**State Statute**:
- Florida Statute Chapter 414 (Primary: § 414.095)
- http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/0414.html

**State Regulations**:
- Florida Administrative Code Chapter 65A-4
- https://flrules.org/gateway/ChapterHome.asp?Chapter=65A-4
- Key recent updates:
  - 65A-4.201 (3/13/2024) - Hardship extensions
  - 65A-4.209 (4/29/2024) - Income
  - 65A-4.210 (3/13/2024) - Budgeting

### Eligibility Requirements

**Categorical**:
- Families with children under 18 (or under 19 if full-time high school student)
- Pregnant women (3rd trimester if unable to work, or 9th month)

**Financial** (2024):
- Gross income < 185% FPL
- Assets ≤ $2,000
- Vehicle value ≤ $8,500 (combined for work-eligible individuals)

**Other**:
- U.S. citizen or qualified noncitizen
- Florida resident
- Work requirements (unless exempt)
- Drug screening (mandatory)

### 2024 Income Limits (185% FPL)

| Family Size | Monthly Gross | Annual Gross |
|-------------|---------------|--------------|
| 1 | $2,322 | $27,861 |
| 2 | $3,151 | $37,814 |
| 3 | $3,981 | $47,767 |
| 4 | $4,810 | $57,720 |
| 5 | $5,639 | $67,673 |

**Source**: Federal poverty guidelines applied at 185%

### Payment Standards (Three-Tier System)

Florida uses a **unique three-tier structure** based on shelter obligation:
- **Tier 1**: No shelter obligation ($0)
- **Tier 2**: Shelter obligation $1-$50
- **Tier 3**: Shelter obligation >$50 OR homeless

**Most Common Benefits (Tier 3)**:

| Family Size | Maximum Monthly Benefit |
|-------------|-------------------------|
| 1 | $180 |
| 2 | $241 |
| 3 | $303 |
| 4 | $364 |
| 5 | $426 |
| 6 | $487 |
| 7 | $549 |
| 8 | $610 |

**Complete table for all tiers (1-13+ persons) available in benefit_calculation.md**

**Critical Note**: The $303 benefit for family of 3 has **not changed since 1992** - representing only ~17% of current federal poverty level.

### Benefit Calculation Formula

```
Monthly TANF Benefit = Payment Standard - Net Countable Income
(rounded down to nearest dollar, minimum $10)
```

### Earned Income Disregards

**Two-step process** (Florida Statute § 414.095):

1. **Standard Disregard**: $90 per individual
2. **Work Incentive Disregard**: First $200 + 50% of remainder

**Example Calculation**:
```
Gross Earned Income: $1,000
- Step 1: $1,000 - $90 = $910
- Step 2: $910 - $200 = $710
         $710 × 0.5 = $355 (countable portion)
= Countable Earned Income: $355
```

### Income Exclusions

**Fully Excluded**:
- Full-time student (elementary/secondary/equivalent) minor child earnings
- Minor child WIOA (Workforce Innovation and Opportunity Act) income
- Adult WIOA income (except wages paid directly by employer)
- Infrequent/irregular income <$60 per quarter

**Partially Excluded**:
- First $50 of child support (remainder counted)

### Critical State-Specific Policies

#### 1. Family Cap (UNIQUE TO 6 STATES)
Florida is one of only 6 states with a family cap policy:

- **Second child born while receiving TANF**: Benefits reduced by 50%
  - Example: Child receives ~$31/month instead of full $62 increment
- **Third and subsequent children born while receiving TANF**: **NO benefits**

**Exceptions**: Parent incarcerated/institutionalized, or child from rape/incest/sexual exploitation

**Source**: Florida Policy Institute analysis
- https://www.floridapolicy.org/posts/5-reasons-why-florida-lawmakers-should-repeal-the-outdated-family-cap-law

#### 2. Three-Tier Payment Structure (UNIQUE TO FLORIDA)
Most states have single payment standard per family size. Florida adjusts based on shelter costs.

#### 3. Drug Screening Requirement
- Mandatory for all applicants
- Applicant pays cost
- Positive test = 1 year ineligibility

#### 4. Time Limits
- **48 months lifetime** as adult
- **Child-only cases exempt** (no time limit)
- **Hardship extensions**: Up to 20% of caseload (statewide cap)

#### 5. Work Requirements
Administered through Florida WAGES program (Work and Gain Economic Self-Sufficiency)

**Sanctions**:
- 1st violation: 10+ days termination
- 2nd violation: 1 month termination
- 3rd violation: 3 months termination

**Exemptions**:
- Domestic violence victims
- Medical incapacity
- Caring for disabled family member
- Mental health/substance abuse treatment (up to 5 hrs/week)
- Single parent with child <6 when childcare unavailable

### Implementation Challenges

1. **Three-tier structure**: Requires shelter cost data and tier determination logic
2. **Family cap**: Need birth timing and TANF receipt history
3. **Two-step earned income disregard**: More complex than most states
4. **Minimum benefit**: $10 floor (below = no cash but retain categorical status)
5. **WIOA income**: Special exclusion rules
6. **Student income**: Full exclusion for qualifying students

### Sample Calculations

**Example 1: Single Parent + 2 Children, $500 Earned Income, Tier 3**
```
Payment standard: $303
Gross earned: $500

Income calculation:
$500 - $90 = $410
$410 - $200 = $210
$210 × 0.5 = $105 (countable)

Benefit: $303 - $105 = $198/month
```

**Example 2: Single Parent + 1 Child, $800 Earned Income, Tier 3**
```
Payment standard: $241
Gross earned: $800

Income calculation:
$800 - $90 = $710
$710 - $200 = $510
$510 × 0.5 = $255 (countable)

Benefit: $241 - $255 = INELIGIBLE (income exceeds standard)
```

**More examples in benefit_calculation.md**

## Resources Cited

### Primary Legal Sources
- Florida Statute Chapter 414: http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/0414.html
- Florida Administrative Code Chapter 65A-4: https://flrules.org/gateway/ChapterHome.asp?Chapter=65A-4
- 42 U.S.C. § 601: https://www.govinfo.gov/content/pkg/USCODE-2011-title42/html/USCODE-2011-title42-chap7-subchapIV-partA.htm

### Official State Resources
- Florida DCF TCA Page: https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance
- ACCESS Florida Application: https://www.myflorida.com/accessflorida/
- Florida Workforce Development: https://floridajobs.org/

### Policy Analysis Sources
- NCCP Florida TANF Profile (2024): https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Florida.pdf
- Florida Policy Institute - Family Cap: https://www.floridapolicy.org/posts/5-reasons-why-florida-lawmakers-should-repeal-the-outdated-family-cap-law
- Florida Policy Institute - 9 Ways to Fix: https://www.floridapolicy.org/posts/9-ways-to-fix-floridas-tanf-program-to-help-children-who-need-it-most

### Federal Resources
- ACF TANF Overview: https://www.acf.hhs.gov/ofa/programs/tanf
- Welfare Rules Databook 2023: https://acf.gov/opre/report/welfare-rules-databook-state-and-territory-tanf-policies-july-2023

## Documentation Completeness

✅ **Federal and state statutes** - Florida Statute Chapter 414, 42 U.S.C. § 601
✅ **Regulations** - Florida Administrative Code Chapter 65A-4 (all relevant rules)
✅ **Program manuals and policy guides** - DCF documentation and policy institute analyses
✅ **Official examples** - Sample calculations included
✅ **Amendment histories and effective dates** - Recent rule updates documented (2024)
✅ **All aspects covered** - Eligibility, calculations, deductions, limits, special cases
✅ **Current and historical rules** - Including 1992 benefit freeze
✅ **Special cases and exceptions** - Family cap, exemptions, hardship extensions
✅ **Structured markdown with citations** - All files with clear references

## Next Steps for Implementation

1. **test-creator** agent: Create YAML test files based on examples in benefit_calculation.md
2. **rules-engineer** agent: Implement variables and parameters based on working_references.md
3. Both agents should reference `/working_references.md` for consolidated implementation guide

## Notes

- **Benefit freeze**: Maximum benefits unchanged since 1992 - significant historical context
- **Family cap**: Controversial policy under advocacy for repeal
- **Tier system**: More complex than typical state TANF programs
- **Drug testing**: Has faced legal challenges
- **Work requirements**: Administered through workforce boards (WAGES program)

## Questions for Implementation Team

1. **Shelter cost data**: How will we determine tier assignment? Use actual shelter costs or default to Tier 3?
2. **Family cap tracking**: Do we have birth date and TANF receipt timing data?
3. **Time limit tracking**: Should we implement 48-month tracking or assume current eligibility?
4. **Work exemptions**: Implement exemption logic or assume all meet work requirements?
5. **Drug testing**: Include in eligibility or assume all pass?

---

**Documentation Status**: ✅ Complete and ready for implementation
**Files Location**: `/docs/agents/sources/fl_tanf/`
**Working Reference**: `/working_references.md` (repository root)
**Commit**: Ready for git commit to fl-tanf branch
