# Wisconsin TANF (Wisconsin Works - W-2) Program Overview

**State**: Wisconsin
**Program**: Wisconsin Works (W-2)
**Agency**: Department of Children and Families (DCF)
**Documentation Collected**: 2025-11-23

---

## Program Description

Wisconsin Works (W-2) is Wisconsin's TANF program, implemented in 1997 to replace Aid to Families with Dependent Children (AFDC). The program is unique among TANF programs in several ways:

1. **Fixed Monthly Payments**: Unlike most TANF programs, Wisconsin provides fixed monthly payments that do NOT vary by family size - only by placement type
2. **Employment-Based Structure**: Benefits are based on work capacity and placement type, not family composition
3. **Work-First Philosophy**: Strong emphasis on employment preparation and work participation

**Key Statistic**: Wisconsin is one of only two states that provides the same amount of TANF benefits to all families with no countable income, regardless of family size.

---

## Legal Authorities

### Wisconsin Statutes
- **§§ 49.141 - 49.161**: Wisconsin Works statutory provisions
  - § 49.141: General provisions
  - § 49.145: Eligibility for employment positions
  - § 49.148: Wages and benefits
  - § 49.149: Education and training
  - § 49.151: Sanctions
  - § 49.155: Wisconsin Shares child care subsidy

**Citation Format**: Wis. Stat. § 49.148
**Online Access**: https://docs.legis.wisconsin.gov/statutes/statutes/49

### Wisconsin Administrative Code
- **DCF Chapter 101**: Wisconsin Works program rules
- **DCF Chapter 102**: Child support cooperation requirements
- **DCF Chapter 103**: W-2 worker training requirements

**Citation Format**: Wis. Admin. Code § DCF 101.09
**Online Access**: https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101

### Policy Manual
- **Wisconsin Works (W-2) Manual**: Comprehensive policy guidance
- **Publisher**: Wisconsin Department of Children and Families
- **Updates**: Regular manual releases (latest: Release 25-01, February 4, 2025)
- **Online Access**: https://dcf.wisconsin.gov/manuals/w-2-manual/Production/default.htm

### State Plan
- **2024 WIOA Combined Plan - TANF Section**: Official state plan submitted to federal government
- **Status**: Available as PDF (requires extraction)
- **URL**: https://dcf.wisconsin.gov/files/w2/tanf-state-plans/2024-wioa-combined-plan-tanf-section-for-comment.pdf

---

## Program Structure

### W-2 Placement Types

Wisconsin W-2 operates through employment placements rather than traditional cash assistance:

1. **Trial Employment Match Program (TEMP)**: Wage subsidy for employment-ready individuals
2. **Community Service Jobs (CSJ)**: Work experience for those not ready for unsubsidized employment
3. **W-2 Transition (W-2 T)**: For individuals with incapacities or caregiving responsibilities
4. **Custodial Parent of an Infant (CMC)**: 8-week placement for parents with newborns
5. **At Risk Pregnancy (ARP)**: For unmarried women in third trimester with medical complications

### W-2 Group Composition

The "W-2 Group" determines financial eligibility and includes:
- Custodial parents
- Dependent children
- Spouses/non-marital co-parents (if residing in same household)

---

## Implementation Considerations

### What CAN Be Simulated

1. **Income eligibility test** (115% FPL)
2. **Asset eligibility test** ($2,500 limit)
3. **Fixed payment amounts** by placement type
4. **Income disregards** and exclusions
5. **Basic demographic eligibility** (age, custodial parent status)

### What CANNOT Be Simulated (Architecture Limitations)

1. **Time Limits**: 48-month state limit and 60-month federal limit require historical tracking
2. **Work Requirements**: Tracking participation hours and activities requires time-series data
3. **Placement Assignment**: Determining which placement type a participant should receive requires assessment data
4. **Sanctions**: Progressive sanctions require tracking compliance history
5. **Case Management**: Ongoing reviews and compliance monitoring

### Simplified Implementation Strategy

For PolicyEngine, recommend implementing:

1. **Single placement type assumption** (e.g., CSJ at $653/month as the standard benefit)
2. **Income eligibility** using 115% FPL test
3. **Asset eligibility** using $2,500 test with vehicle/homestead exclusions
4. **Income disregards** for child support, tax credits, and other excluded sources
5. **Basic demographic eligibility** using federal baseline (age 18, custodial parent)

**Rationale**: This provides a reasonable benefit estimate for eligible families while acknowledging the limitation that actual benefits depend on placement assignment, which requires case worker assessment.

---

## Key Policy Features

### Unique Characteristics

1. **No Benefit Reduction Rate**: Payments are fixed amounts, not calculated based on income level
2. **Extensive Income Disregards**: All child support, tax credits, and many other income sources are fully disregarded
3. **Employment Focus**: All placements except CMC and ARP require work participation
4. **Fixed Payments**: Same payment for all eligible families in a placement type, regardless of family size

### Comparison to Traditional TANF

Traditional TANF programs typically:
- Vary benefits by family size
- Use benefit reduction rates (e.g., 50% or 100% of earned income)
- Calculate benefits as: Max Benefit - (Countable Income × Reduction Rate)

Wisconsin W-2 instead:
- Provides fixed payments by placement type
- Uses income only for eligibility determination (115% FPL test)
- Does not reduce benefits based on income level (pass/fail eligibility)

---

## Documentation Sources

### Primary Sources (Authoritative)
- [Wisconsin Works Manual](https://dcf.wisconsin.gov/manuals/w-2-manual/Production/default.htm)
- [Wisconsin Administrative Code DCF 101-103](https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199)
- [Wisconsin Statutes §§ 49.141-49.161](https://docs.legis.wisconsin.gov/statutes/statutes/49)

### State Plan (Requires PDF Extraction)
- [2024 WIOA Combined Plan TANF Section](https://dcf.wisconsin.gov/files/w2/tanf-state-plans/2024-wioa-combined-plan-tanf-section-for-comment.pdf)

### Related Resources
- [W-2 Overview for Parents](https://dcf.wisconsin.gov/w2/parents/w2)
- [W-2 for Researchers](https://dcf.wisconsin.gov/w2/researchers/programs)
- [W-2 State Plans Archive](https://dcf.wisconsin.gov/w2/researchers/state-plans)

---

## Effective Dates

**Current Policy**: 2024-2025
**Income Limits**: Updated annually each February based on federal poverty guidelines
**Payment Standards**: As of 2024 (verify for updates)
**Last Major Revision**: Various manual releases throughout 2024-2025

---

## Next Steps for Implementation

1. **Extract State Plan PDF** to verify payment standards and policy details
2. **Review existing TANF implementations** in PolicyEngine for structural patterns
3. **Determine placement type assumption** for simplified implementation
4. **Create parameter files** for income limits, asset limits, and payment standards
5. **Implement eligibility variables** for income test, asset test, and demographic requirements
6. **Create benefit calculation variable** returning fixed payment amount
7. **Write comprehensive tests** covering various household configurations

---

## Contact Information

**Wisconsin Department of Children and Families**
Bureau of Working Families
Email: bwf_co@wisconsin.gov
Website: https://dcf.wisconsin.gov/w2

---

**Documentation Status**: Complete (HTML sources); PDF extraction pending for State Plan
