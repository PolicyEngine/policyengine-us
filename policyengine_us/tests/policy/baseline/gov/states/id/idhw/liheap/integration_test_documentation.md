# Idaho LIHEAP Integration Test Documentation

## Overview

This document explains the derivation and methodology behind all test values in the Idaho Low Income Home Energy Assistance Program (LIHEAP) integration tests. All tests are based solely on official documentation from the Idaho Department of Health and Welfare and federal LIHEAP regulations (45 CFR Part 96, Subpart H).

## Source Documentation

- **Primary Authority**: Idaho Department of Health and Welfare LIHEAP State Plan
- **Federal Authority**: 45 CFR Part 96, Subpart H - Low-income Home Energy Assistance Program
- **Federal Statute**: Section 2605 of Public Law 97-35 (42 U.S.C. 8624)
- **Program Year**: Federal Fiscal Year 2025 (October 1, 2024 - September 30, 2025)
- **Retrieved Date**: August 26, 2025

## Income Eligibility Test Derivation

### Income Standard: 60% State Median Income

Idaho uses 60% of State Median Income (SMI) for LIHEAP eligibility, except weatherization which uses 200% Federal Poverty Level.

**Monthly Gross Income Limits for FY 2025** (from documentation):
- 1 Person: $2,530 → Annual: $30,360
- 2 People: $3,309 → Annual: $39,708  
- 3 People: $4,087 → Annual: $49,044
- 4 People: $4,866 → Annual: $58,392
- 5 People: $5,644 → Annual: $67,728
- 6 People: $6,423 → Annual: $77,076

**Calculation Method** (per 45 CFR 96.85):
60% of Idaho's estimated median income for a 4-person family is multiplied by these percentages:
- 1 person: 52%
- 2 persons: 68%
- 3 persons: 84%
- 4 persons: 100%
- 5 persons: 116%
- 6 persons: 132%

### Test Case Income Selection

1. **At Threshold Tests**: Used exact annual amounts from monthly limits
   - Example: 1 person at $30,360 (exactly $2,530/month × 12)

2. **Below Threshold Tests**: Used amounts 10-20% below limits
   - Example: 2 people at $35,000 (below $39,708 limit)

3. **Above Threshold Tests**: Used amounts $1-$100 above limits
   - Example: 1 person at $30,500 (above $30,360 limit)

4. **Boundary Tests**: Tested exactly $1 above and below thresholds
   - Example: 1 person at $30,361 (above) vs $30,359 (below)

## Categorical Eligibility

### Automatic Qualification Programs
Per documentation: "Households are automatically qualified if they participate in:"
- SNAP (Food Stamps)
- TANF (Temporary Assistance for Needy Families)  
- SSI (Supplemental Security Income)

**Test Income Levels**: Used incomes well above regular LIHEAP limits (e.g., $50,000-$80,000) to verify categorical eligibility overrides income limits.

**Benefit Amounts**: Used realistic monthly amounts:
- SNAP: $150-$400/month for different household sizes
- TANF: $300-$500/month for families with children
- SSI: $800-$900/month for individuals

## Priority Groups

### Definition
Priority given to households with:
- Children under age 6
- Elderly members (age 60 or 65+)
- Disabled members
- Emergency heating situations

### Age Boundaries Tested
- **Child Priority**: Tested ages 5 (priority) vs 6 (no priority)
- **Elderly Priority**: Tested age 60 as threshold (documentation indicates "typically age 60 or 65+")
- **Disabled Priority**: Used `is_disabled: true` flag

## Benefit Amount Derivation

### Seasonal Heating Assistance
**From Documentation**:
- **Minimum Benefit**: $75
- **Maximum Benefit**: $1,242
- **Season**: October 1 - March 31
- **Frequency**: One payment per program year

**Test Benefit Calculations**:
- **Minimum ($75)**: Used for low heating costs or minimal need scenarios
- **Maximum ($1,242)**: Used for large families with high heating costs and priority members
- **Moderate Amounts ($300-$650)**: Estimated based on household size, heating costs, and priority status

### Crisis Heating Assistance
**From Documentation**:
- **Maximum Benefit**: $1,500
- **Availability**: Year-round
- **Frequency**: Once per 12 months
- **Response Time**: 48 hours goal

**Test Crisis Scenarios**:
- **Utility Shutoff**: Used `utility_shut_off_notice: true`
- **Past Due Balance**: Used specific dollar amounts ($400-$2,000)
- **Bulk Fuel Crisis**: Used `bulk_fuel_supply_low: true` (less than 48 hours supply)

**Benefit Calculations**:
- Benefits set to match crisis need amount up to $1,500 maximum
- Used realistic past due amounts: $400-$950 for individual/small families, $1,500+ for large families (capped at max)

## Seasonal Restrictions

### Heating Season
**From Documentation**: October 1 through March 31

**Test Dates**:
- **Within Season**: 2025-01 (January), 2025-02 (February), 2025-03-31 (last day)
- **Outside Season**: 2025-04-01 (first day out), 2025-07 (July), 2025-09 (September)
- **Boundary Tests**: 2024-10-01 (first day), 2024-09-30 (last day out)

## Weatherization Program

### Income Standard: 200% Federal Poverty Level
**From Documentation**: Weatherization uses 200% FPL instead of 60% SMI

**Estimated 2025 200% FPL Thresholds** (approximate):
- 1 person: ~$31,200
- 2 people: ~$42,400  
- 3 people: ~$53,600
- 4 people: ~$64,800
- 5 people: ~$76,000

**Additional Requirements**:
- `is_homeowner: true`
- `home_energy_efficiency_need: true`
- Year-round availability

## Multi-Household Scenarios

### Household Definition
**From Documentation**: "Household includes everyone on the same utility bill"

### Complex Family Types Tested
1. **Multi-generational**: Grandparents + parents + children
2. **Single Parent**: Various configurations with different child ages
3. **Blended Families**: Stepchildren and biological children
4. **Foster Families**: Foster children count toward household size
5. **Adult Children**: Young adults living with parents
6. **Mixed Immigration Status**: At least one US citizen required

### Income Calculations
- Combined all household member incomes
- Used realistic employment income ranges: $8,000-$40,000 per working adult
- Added benefit income where applicable: Social Security ($10,000-$18,000), SSI ($9,600), disability ($14,400-$16,000)

## Edge Cases and Boundary Conditions

### Zero Income
- Tested $0 income scenarios (eligible - below all thresholds)

### Mixed Income Types
- Combined employment, Social Security, disability, self-employment
- Ensured totals fell appropriately above/below thresholds

### Geographic Restrictions
- Used `state_code: ID` for eligible households
- Used other state codes (WA, CA) for ineligible scenarios

### Crisis Restrictions
- **12-Month Rule**: Tested scenarios with previous assistance dates
- **Crisis Conditions**: Required specific crisis triggers (shutoff notice, fuel shortage)

## Assumptions Made

### Where Documentation Was Silent
1. **Specific Benefit Amounts**: Documentation provided min/max but not calculation methodology
   - Assumed benefits vary based on household size, income, heating costs, and priority status
   - Used reasonable estimates within documented ranges

2. **Priority Age Thresholds**: Documentation said "typically age 60 or 65+"
   - Used age 60 as threshold for tests
   - Could be adjusted if actual threshold is 65

3. **200% FPL Values**: Exact 2025 FPL not available
   - Used estimated values based on 2024 FPL with typical annual adjustments
   - Actual values may differ slightly

4. **Crisis Benefit Calculation**: Documentation provides maximum but not calculation method
   - Assumed benefits match crisis need up to maximum
   - Based amounts on realistic utility bills and fuel costs

## Test File Organization

### Files Created
1. **integration.yaml**: Comprehensive tests covering all major scenarios
2. **edge_cases.yaml**: Boundary conditions and special circumstances  
3. **multi_household.yaml**: Complex family compositions and real-world scenarios
4. **eligibility/id_liheap_eligible.yaml**: Main eligibility variable tests
5. **eligibility/id_liheap_income_eligible.yaml**: Income eligibility tests
6. **payment/id_liheap_seasonal_payment.yaml**: Seasonal heating benefit amounts
7. **payment/id_liheap_crisis_payment.yaml**: Crisis heating benefit amounts

### Coverage Achieved
- ✅ All documented household sizes (1-6+ people)
- ✅ All income eligibility paths (income + categorical)
- ✅ All benefit types (seasonal, crisis, weatherization)
- ✅ All priority groups (children <6, elderly, disabled)
- ✅ All seasonal restrictions (Oct-Mar heating season)
- ✅ All crisis conditions (shutoff, fuel shortage)
- ✅ Edge cases and boundary conditions
- ✅ Complex household compositions
- ✅ Geographic and citizenship requirements

## Validation Notes

### Expected Implementation Behavior
1. **Income Eligibility**: Should use exact thresholds from documentation
2. **Categorical Eligibility**: Should override income limits for SNAP/TANF/SSI participants
3. **Seasonal Restrictions**: Should only allow heating assistance October-March
4. **Crisis Availability**: Should be available year-round with higher maximums
5. **Priority Processing**: Should identify households with elderly/disabled/young children
6. **Benefit Calculation**: Should respect minimum ($75) and maximum ($1,242 seasonal, $1,500 crisis) limits

### Test Success Criteria
- All income eligible households below thresholds should pass
- All categorically eligible households should pass regardless of income  
- All households above income limits without categorical eligibility should fail
- Seasonal benefits should only be available October-March
- Crisis benefits should be available year-round
- Priority groups should be properly identified
- Benefit amounts should fall within documented ranges

This test suite provides comprehensive coverage of Idaho LIHEAP based solely on the official documentation provided.