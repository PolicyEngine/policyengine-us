# Florida TANF Documentation

This directory contains comprehensive documentation for implementing Florida's Temporary Assistance for Needy Families (TANF) program, known in Florida as Temporary Cash Assistance (TCA).

**Documentation Date**: October 21, 2025
**Effective Period**: 2024-2025
**GitHub Issue**: https://github.com/PolicyEngine/policyengine-us/issues/6723

## Contents

### 1. [eligibility.md](./eligibility.md)
Complete eligibility requirements including:
- Categorical eligibility (families with children, pregnant women)
- Citizenship and residency requirements
- Financial eligibility (income and asset limits)
- 2024 income limits at 185% FPL
- Time limits and work requirements
- Assistance group composition rules
- Child-only cases

### 2. [benefit_calculation.md](./benefit_calculation.md)
Detailed benefit calculation methodology:
- Three-tier payment standard system (based on shelter obligation)
- Complete payment standard table (family sizes 1-13+)
- Income calculation and disregards
- Earned income disregard formula ($90 + $200 + 50% remainder)
- Income exclusions (student income, WIOA, child support)
- Family cap policy implementation
- Step-by-step calculation examples

### 3. [special_provisions.md](./special_provisions.md)
Florida-specific policies and unique features:
- **Family cap**: One of only 6 states (50% reduction for 2nd child, zero for 3rd+)
- **Drug screening**: Mandatory testing requirement
- **Three-tier payment structure**: Based on shelter costs
- **WAGES program**: Work requirements and sanctions
- **Time limit extensions**: Hardship exemptions (20% cap)
- Teen parent requirements
- Immigrant provisions
- Diversion programs
- Pregnancy provisions
- Comparison to federal TANF rules

## Legal Authority

### Federal
- **Personal Responsibility and Work Opportunity Reconciliation Act of 1996**
  - Citation: 42 U.S.C. § 601 et seq.
  - URL: https://www.govinfo.gov/content/pkg/USCODE-2011-title42/html/USCODE-2011-title42-chap7-subchapIV-partA.htm

### State Statute
- **Florida Statute Chapter 414** - Temporary Cash Assistance Program
  - URL: http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/0414.html
  - Key sections:
    - § 414.075: Resource limits
    - § 414.085: Income standards
    - § 414.095: Eligibility determination (PRIMARY)
    - § 414.105: Time limits
    - § 414.065: Work requirements
    - § 414.0652: Drug screening

### State Regulations
- **Florida Administrative Code Chapter 65A-4** - Temporary Cash Assistance
  - URL: https://flrules.org/gateway/ChapterHome.asp?Chapter=65A-4
  - Key rules:
    - 65A-4.201: Hardship extensions (effective 3/13/2024)
    - 65A-4.205: Work requirement penalties
    - 65A-4.207: Age requirements
    - 65A-4.208: Need determination
    - 65A-4.209: Income (effective 4/29/2024)
    - 65A-4.210: Budgeting (effective 3/13/2024)
    - 65A-4.215: Pregnant women eligibility
    - 65A-4.220: Amount and duration of payment

## Quick Reference

### Key Numbers (2024)

**Asset Limits**:
- General assets: $2,000
- Vehicle value: $8,500 (combined for work-eligible individuals)

**Income Limits (185% FPL)**:
| Family Size | Monthly Gross Income |
|-------------|----------------------|
| 1 | $2,322 |
| 2 | $3,151 |
| 3 | $3,981 |
| 4 | $4,810 |
| 5 | $5,639 |

**Payment Standards (Tier 3 - Most Common)**:
| Family Size | Maximum Monthly Benefit |
|-------------|-------------------------|
| 1 | $180 |
| 2 | $241 |
| 3 | $303 |
| 4 | $364 |
| 5 | $426 |

**Earned Income Disregards**:
1. $90 per individual (standard)
2. $200 + 50% of remainder (work incentive)

**Time Limit**: 48 months lifetime (adults)

**Work Sanctions**:
- 1st: 10+ days
- 2nd: 1 month
- 3rd: 3 months

## Implementation Considerations

### Unique Features to Code

1. **Three-tier payment structure**: Requires shelter cost input and tier determination logic
2. **Family cap**: Track birth order and TANF receipt timing
3. **Two-step earned income disregard**: $90 standard + $200 + 50% formula
4. **Minimum benefit rule**: $10 floor (below maintains categorical eligibility without cash)
5. **Student income exclusion**: Full disregard for qualifying students
6. **WIOA income**: Special exclusion (except direct employer wages for adults)
7. **Child-only cases**: Exempt from time limits
8. **Hardship extensions**: 20% statewide cap

### Data Requirements

- Household composition (ages, relationships)
- Income sources (earned, unearned, WIOA, child support)
- Student status and school attendance
- Housing costs (for tier determination)
- Birth dates and TANF receipt history (for family cap)
- Work requirement status
- Months of TANF received (for time limits)

### Critical Edge Cases

1. **Income exactly at payment standard**: Eligible with $0 benefit
2. **Benefit calculation < $10**: No cash but retain status
3. **Family cap application**: Child born 1 day after TANF receipt
4. **Student vs. non-student sibling**: Different income treatment
5. **Tier changes**: Housing cost fluctuations
6. **Child-only to adult case**: Time limit begins accruing

## Testing Scenarios

See [benefit_calculation.md](./benefit_calculation.md) for detailed examples:
1. Single parent + 1 child, earned income, Tier 3
2. Single parent + 2 children, earned income, Tier 3
3. No earned income, child support, Tier 2
4. Family cap application
5. Student income exclusion
6. Minimum benefit (<$10)
7. Income at exactly payment standard

## Additional Resources

### Florida State Resources
- **Florida DCF TCA Page**: https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance
- **ACCESS Florida Application**: https://www.myflorida.com/accessflorida/
- **Florida Workforce Development**: https://floridajobs.org/

### Policy Analysis
- **NCCP Florida TANF Profile**: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Florida.pdf
- **Florida Policy Institute - Family Cap**: https://www.floridapolicy.org/posts/5-reasons-why-florida-lawmakers-should-repeal-the-outdated-family-cap-law
- **Florida Policy Institute - 9 Ways to Fix FL TANF**: https://www.floridapolicy.org/posts/9-ways-to-fix-floridas-tanf-program-to-help-children-who-need-it-most

### Federal Resources
- **ACF TANF Overview**: https://www.acf.hhs.gov/ofa/programs/tanf
- **Welfare Rules Databook 2023**: https://acf.gov/opre/report/welfare-rules-databook-state-and-territory-tanf-policies-july-2023

## Notes for Implementers

### Historical Context
- Maximum benefit for family of 3 ($303) **unchanged since 1992**
- Represents only ~17% of federal poverty level
- No cost-of-living adjustments in 32+ years
- Florida is one of only 6 states retaining family cap policy

### Known Issues and Controversies
1. **Family cap**: Under ongoing advocacy for repeal
2. **Drug testing**: Has faced constitutional challenges
3. **Benefit adequacy**: Combined TANF + SNAP still below 50% poverty
4. **Time limits**: Hardship extension cap more restrictive than some states

### Implementation Priority
1. **Core eligibility**: Income/asset tests
2. **Basic benefit calculation**: Tier 3 (most common)
3. **Earned income disregards**: Two-step formula
4. **Income exclusions**: Student, WIOA, child support
5. **Family cap**: If data available
6. **Tier 1 & 2**: Additional shelter-based tiers
7. **Time limits**: If tracking historical receipt
8. **Work requirements**: If simulating sanctions

## Contact and Updates

For questions or updates to this documentation:
- **GitHub Issue**: https://github.com/PolicyEngine/policyengine-us/issues/6723
- **Florida DCF**: https://www.myflfamilies.com/contact-us
- **Policy Questions**: Contact Florida DCF Economic Self-Sufficiency Program

## Version History

- **v1.0** (October 21, 2025): Initial comprehensive documentation
  - All eligibility requirements
  - Complete benefit calculation methodology
  - Three-tier payment standards
  - Special provisions including family cap
  - Regulatory citations and references

---

**Documentation compiled by**: Document Collector Agent
**For**: PolicyEngine US Florida TANF Implementation
**Branch**: fl-tanf
