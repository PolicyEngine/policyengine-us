# Arizona LIHEAP Test Scenarios

## Purpose
This document provides test scenarios for validating the implementation of Arizona's LIHEAP program. Each scenario includes input parameters and expected outcomes based on the program rules documented in the source files.

## Test Scenario 1: Basic Eligible Household

### Input
- **Household Size**: 3 (2 adults, 1 child)
- **Monthly Income**: $2,000
- **Monthly Electric Bill**: $150
- **Monthly Gas Bill**: $50
- **Location**: Maricopa County
- **Demographics**: No elderly or disabled members
- **Application Date**: May 1, 2025 (Cooling Season)

### Calculations
- **Income Limit**: $4,758 (household of 3)
- **Income Percentage**: $2,000 / $4,758 = 42%
- **Income Points**: 5 (0-50% range)
- **Energy Burden**: $200 / $2,000 = 10%
- **Energy Burden Points**: 3 (6-10% range)
- **Demographic Points**: 0
- **Total Points**: 8

### Expected Outcome
- **Eligible**: Yes
- **Benefit Amount**: $300-$480 range (based on 8 points)
- **Program Type**: Cooling assistance

## Test Scenario 2: Elderly and Disabled Household

### Input
- **Household Size**: 1
- **Monthly Income**: $758
- **Monthly Electric Bill**: $40
- **Monthly Gas Bill**: $34
- **Age**: 84
- **Disability Status**: Receiving SSDI
- **Location**: Coconino County
- **Application Date**: December 15, 2024 (Heating Season)

### Calculations
- **Income Limit**: $2,944
- **Income Percentage**: $758 / $2,944 = 26%
- **Income Points**: 5 (0-30% range)
- **Energy Burden**: $74 / $758 = 9.8%
- **Energy Burden Points**: 3 (6-10% range)
- **Demographic Points**: 2 (1 elderly + 1 disabled)
- **Total Points**: 10

### Expected Outcome
- **Eligible**: Yes
- **Benefit Amount**: $480-$640 range (based on 10 points)
- **Program Type**: Heating assistance

## Test Scenario 3: Categorically Eligible Household

### Input
- **Household Size**: 4
- **Monthly Income**: $3,500
- **SNAP Recipient**: Yes
- **Monthly Electric Bill**: $250
- **Location**: Pima County
- **Application Date**: July 1, 2025 (Cooling Season)

### Calculations
- **Categorical Eligibility**: Automatic qualification due to SNAP
- **No Income Verification Required**
- **Energy Burden**: $250 / $3,500 = 7.1%
- **Energy Burden Points**: 3
- **Income Points**: 5 (categorical eligibility = lowest income category)
- **Demographic Points**: 0
- **Total Points**: 8

### Expected Outcome
- **Eligible**: Yes (categorical)
- **Benefit Amount**: $300-$480 range
- **Program Type**: Cooling assistance
- **Documentation**: No income docs needed

## Test Scenario 4: High Income Ineligible Household

### Input
- **Household Size**: 2
- **Monthly Income**: $5,000
- **Monthly Electric Bill**: $100
- **Location**: Yavapai County

### Calculations
- **Income Limit**: $3,851
- **Income Percentage**: $5,000 / $3,851 = 130%

### Expected Outcome
- **Eligible**: No (income exceeds 100% of limit)
- **Reason**: Income above maximum threshold

## Test Scenario 5: Crisis Assistance Eligible

### Input
- **Household Size**: 3
- **Monthly Income**: $1,800
- **Regular LIHEAP Received**: Yes ($300 in January 2025)
- **Shut-off Notice**: Yes (dated June 15, 2025)
- **Past Due Amount**: $450
- **Location**: Maricopa County
- **Application Date**: June 20, 2025

### Calculations
- **Income Eligible**: Yes ($1,800 < $4,758)
- **Crisis Type**: Regular Crisis (shut-off notice)
- **Crisis Amount Needed**: $450

### Expected Outcome
- **Crisis Eligible**: Yes
- **Crisis Benefit**: $450 (actual need, under $500 max)
- **Total FY Benefits**: $750 ($300 regular + $450 crisis)

## Test Scenario 6: Life-Threatening Medical Crisis

### Input
- **Household Size**: 2
- **Monthly Income**: $2,200
- **Medical Equipment**: Oxygen concentrator
- **Physician Statement**: Yes
- **Past Due Amount**: $800
- **Application Date**: August 1, 2025

### Calculations
- **Income Eligible**: Yes ($2,200 < $3,851)
- **Crisis Type**: Life-Threatening
- **Medical Documentation**: Verified

### Expected Outcome
- **Crisis Eligible**: Yes (expedited processing)
- **Crisis Benefit**: $500 (maximum)
- **Processing Time**: Immediate
- **Note**: $300 balance remains customer responsibility

## Test Scenario 7: Large Household with Mixed Ages

### Input
- **Household Size**: 7
- **Adults**: 4 (ages 35, 33, 62, 19)
- **Children**: 3 (ages 5, 10, 15)
- **Monthly Income**: $6,000
- **Monthly Electric Bill**: $400
- **Location**: Apache County
- **Application Date**: November 15, 2024

### Calculations
- **Income Limit**: $7,648
- **Income Percentage**: $6,000 / $7,648 = 78%
- **Income Points**: 2 (71-85% range)
- **Energy Burden**: $400 / $6,000 = 6.7%
- **Energy Burden Points**: 3 (6-10% range)
- **Demographic Points**: 2 (1 elderly + 1 child under 6)
- **Total Points**: 7

### Expected Outcome
- **Eligible**: Yes
- **Benefit Amount**: $300-$480 range
- **Program Type**: Heating assistance

## Test Scenario 8: Frequency Limitation

### Input
- **Previous Regular Benefit**: Received $400 on November 1, 2024
- **New Application**: October 15, 2025
- **Household Size**: 2
- **Monthly Income**: $2,000

### Calculations
- **Months Since Last Benefit**: 11 months
- **12-Month Rule**: Not yet satisfied

### Expected Outcome
- **Eligible**: No
- **Reason**: Must wait until November 1, 2025 (12 months)

## Test Scenario 9: Zero Energy Burden

### Input
- **Household Size**: 1
- **Monthly Income**: $1,000
- **Utilities Included in Rent**: Yes
- **Rent**: $600 (includes all utilities)
- **Location**: Phoenix

### Expected Outcome
- **Eligible**: No
- **Reason**: No separate utility costs
- **Exception**: Could qualify if facing eviction with proper notice

## Test Scenario 10: Self-Employment Income

### Input
- **Household Size**: 2
- **Self-Employment Gross**: $4,000/month
- **Business Expenses**: $1,500/month
- **Net Income**: $2,500/month
- **Monthly Electric Bill**: $200

### Calculations
- **Countable Income**: $2,500 (net after expenses)
- **Income Limit**: $3,851
- **Income Percentage**: $2,500 / $3,851 = 65%
- **Income Points**: 3 (51-70% range)
- **Energy Burden**: $200 / $2,500 = 8%
- **Energy Burden Points**: 3 (6-10% range)
- **Total Points**: 6

### Expected Outcome
- **Eligible**: Yes
- **Benefit Amount**: $240-$360 range
- **Documentation Required**: Profit/loss statement

## Test Scenario 11: Non-Citizen Household Member

### Input
- **Household Size**: 3 total
- **Eligible Members**: 2 (US citizens)
- **Ineligible Member**: 1 (undocumented, age 25)
- **Income US Citizens**: $1,500/month
- **Income Non-Citizen**: $1,000/month
- **Total Household Income**: $2,500

### Calculations
- **Household Size for Limit**: 2 (eligible members only)
- **Income Counted**: $2,500 (all adults 18+)
- **Income Limit**: $3,851 (2-person household)
- **Income Percentage**: $2,500 / $3,851 = 65%

### Expected Outcome
- **Eligible**: Yes
- **Note**: Income from all adults counts, but household size based on eligible members only

## Test Scenario 12: Shared Living Arrangement

### Input
- **Total Occupants**: 6 (2 separate families)
- **Applicant Family**: 3 members
- **Applicant Income**: $2,000/month
- **Total Electric Bill**: $300
- **Applicant's Share**: 50% ($150)
- **Separate Food Purchase**: Yes

### Calculations
- **Household Size**: 3 (applicant family only)
- **Energy Cost**: $150 (prorated share)
- **Income Limit**: $4,758
- **Energy Burden**: $150 / $2,000 = 7.5%

### Expected Outcome
- **Eligible**: Yes (separate household)
- **Benefit Calculation**: Based on prorated utility costs

## Validation Notes

These test scenarios should validate:
1. Income eligibility determination
2. Points-based benefit calculation
3. Categorical eligibility bypass
4. Crisis assistance rules
5. Frequency limitations
6. Documentation requirements
7. Household composition rules
8. Regional program dates
9. Special populations (elderly, disabled, young children)
10. Mixed eligibility households