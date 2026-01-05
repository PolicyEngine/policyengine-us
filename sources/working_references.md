# Collected Documentation

## Florida Temporary Cash Assistance (TCA) Implementation
**Collected**: 2026-01-04
**Implementation Task**: Implement Florida's TANF program (Temporary Cash Assistance)

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Temporary Cash Assistance (TCA)
**Abbreviation**: TCA
**Administering Agency**: Florida Department of Children and Families (DCF)
**Source**: Florida Statutes Chapter 414; Florida Administrative Code Chapter 65A-4

**Variable Prefix**: `fl_tca`

---

## Regulatory Authority

### Primary Legal Sources

1. **Florida Statutes Chapter 414** - Family Self-Sufficiency
   - Section 414.095 - Eligibility for temporary cash assistance
   - URL: https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html

2. **Florida Administrative Code Chapter 65A-4** - Temporary Cash Assistance
   - Rule 65A-4.207 - Age
   - Rule 65A-4.208 - Need
   - Rule 65A-4.209 - Income
   - Rule 65A-4.210 - Budgeting
   - Rule 65A-4.220 - Amount and Duration of Cash Payment
   - URL: https://flrules.org/gateway/ChapterHome.asp?Chapter=65A-4

3. **Florida DCF Official TCA Page**
   - URL: https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance

---

## Income Eligibility Tests

Florida uses a **dual income test** for TCA eligibility:

### Test 1: Gross Income Test (185% of FPL)

**Requirement**: Total average gross monthly income (after the $90 earned income deduction) cannot exceed 185% of the Federal Poverty Level (Consolidated Need Standard).

**Formula**:
```
Adjusted Gross Income = Gross Earned Income - ($90 x number of earners) + Gross Unearned Income
Pass Test: Adjusted Gross Income < 185% of FPL
```

**Key Details**:
- The $90 deduction applies to each individual's gross earned income
- The $200 plus half disregard is NOT applied in this test
- The 185% FPL threshold is based on the Consolidated Need Standard (CNS) = 100% of current federal poverty level

**Source**:
- Florida DCF TCA Page: "Gross income must be less than 185% of the Federal Poverty level"
- FAC 65A-4.220: "adjusted gross income cannot exceed 185 percent of the Consolidated Need Standard (CNS)"

### Test 2: Net Income Test (Payment Standard Test)

**Requirement**: Countable income (after disregards) cannot exceed the payment standard for the family size.

**Formula**:
```
Net Countable Income = Gross Income - $200 - 50% of (Remaining Earned Income) - Other Deductions
Pass Test: Net Countable Income < Payment Standard for family size
```

**Source**:
- Florida Statutes 414.095(11): "The first $200 plus one-half of the remainder of earned income shall be disregarded"
- Florida Statutes 414.095(12): Benefit calculation based on payment standard minus net income

---

## Income Deductions & Exemptions

### 1. $90 Gross Earned Income Deduction (Eligibility Test)

**Amount**: $90 per individual
**Level**: Per PERSON (each working individual)
**Applied In**: Gross income test (185% FPL test)
**NOT Applied In**: Benefit calculation (uses $200 + 50% instead)

**Source**: Florida DCF TCA Page: "Individuals get a $90 deduction from their gross earned income"

### 2. Earned Income Disregard ($200 + 50%)

**Amount**: First $200 of earned income, plus 50% of the remainder
**Level**: Per assistance GROUP
**Applied In**: Net income test and benefit calculation
**Requirements**: Individual must be eligible for earned income to be disregarded per FL Statute 414.095(11)

**Formula**:
```
Earned Income Disregard = $200 + 0.5 x max(Gross Earned Income - $200, 0)
Countable Earned Income = Gross Earned Income - Earned Income Disregard
                        = 0.5 x max(Gross Earned Income - $200, 0)
```

**Source**:
- Florida Statutes 414.095(11): "As an incentive to employment, the first $200 plus one-half of the remainder of earned income shall be disregarded."
- URL: https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html

### 3. Student Earned Income Exclusion

**Exclusion**: 100% of earned income excluded
**Eligibility**: Child who is a family member, attends high school or equivalent, and is 19 years of age or younger

**Source**:
- FAC 65A-4.209: "The earned monthly income of a minor child who is a full-time student in an elementary or secondary school or an equivalent level of career training does not count"
- Florida Statutes 414.095(11)(b): "A child's earned income shall be disregarded if the child is a family member, attends high school or the equivalent, and is 19 years of age or younger"

### 4. WIOA Income Exclusion

**Exclusion**: All income received under Workforce Innovation and Opportunity Act (WIOA)
**For Minor Children**: Full exclusion
**For Adults**: Only wages paid directly by employer are counted; other WIOA income excluded

**Source**: FAC 65A-4.209

### 5. Infrequent/Irregular Unearned Income Exclusion

**Amount**: Up to $60 per calendar quarter
**Examples**: Gifts for Christmas, birthdays, graduation

**Source**: FAC 65A-4.209: "Infrequent or irregular unearned income not exceeding $60 per calendar quarter such as gifts for Christmas, birthdays or graduation does not count"

### 6. Child Care Deduction

**Amount**: $0 (NO deduction allowed)

**Source**: Florida Statutes 414.095(12): "A deduction may not be allowed for child care payments"

### 7. Self-Employment Deductions

**Per FAC 65A-4.210**:
- Operating costs (excluding depreciation and capital expenditures)
- $58 monthly standard deduction per boarder for room and board providers
- $1 per day per child for home-based child care
- 25% of gross rental receipts from improved property
- 15% of gross rental receipts from unimproved property
- Taxes and mortgage interest on non-homestead property

**Source**: FAC 65A-4.210

---

## Resource/Asset Limits

### Countable Asset Limit

**Amount**: $2,000
**Level**: Per assistance GROUP (family)

**Source**:
- Florida DCF TCA Page: "A family's countable assets must be equal to or less than $2,000"
- URL: https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance

### Vehicle Limit

**Amount**: $8,500 combined value maximum
**Applies To**: Licensed vehicles needed for individuals subject to work requirement

**Source**: Florida DCF TCA Page: "Licensed vehicles needed for individuals subject to the work requirement may not exceed a combined value of $8,500"

---

## Income Standards (Payment Standards by Family Size)

Florida uses a **three-tier shelter payment system** based on monthly shelter obligations:

- **Tier I (>$50 Shelter)**: Highest payment - for groups with shelter obligation exceeding $50 or experiencing homelessness
- **Tier II ($1-$50 Shelter)**: Middle payment - for groups with shelter obligation between $1 and $50
- **Tier III ($0 Shelter)**: Lowest payment - for groups with zero shelter obligation or teen parents living with relatives

### Payment Standard Table (Per FL Statute 414.095(10))

| Family Size | Zero Shelter ($0) | $1-$50 Shelter | >$50 Shelter |
|-------------|-------------------|----------------|--------------|
| 1 | $95 | $153 | $180 |
| 2 | $158 | $205 | $241 |
| 3 | $198 | $258 | $303 |
| 4 | $254 | $309 | $364 |
| 5 | $289 | $362 | $426 |
| 6 | $346 | $414 | $487 |
| 7 | $392 | $467 | $549 |
| 8 | $438 | $519 | $610 |
| 9 | $485 | $570 | $671 |
| 10 | $534 | $623 | $733 |
| 11 | $582 | $676 | $795 |
| 12 | $630 | $728 | $857 |
| 13 | $678 | $781 | $919 |

**Note**: These payment standards have remained unchanged since 1992.

**Source**:
- Florida Statutes 414.095(10)
- URL: https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html

---

## Benefit Calculation

### Formula

```
TCA Benefit = Payment Standard - Net Countable Income
```

Where:
- **Payment Standard** = Amount from table above based on family size and shelter obligation
- **Net Countable Income** = Gross Income - Earned Income Disregard ($200 + 50%) - Other Allowable Deductions

### Rounding

Benefit is rounded to the nearest dollar (per FAC 65A-4.220: "rounding down to the nearest dollar").

### Minimum Grant

**Amount**: $10

If the calculated benefit is less than $10, no TCA is paid, but the family retains recipient status for Medicaid and food assistance purposes.

**Source**: FAC 65A-4.220: "The minimum grant is $10; those eligible for less than $10 don't receive TCA but retain recipient status for Medicaid and food assistance"

### Calculation Steps

1. Calculate Gross Income = Earned Income + Unearned Income
2. Apply Gross Income Test: Gross Income - ($90 x earners) < 185% FPL
3. Calculate Earned Income Disregard = $200 + 0.5 x (Earned Income - $200)
4. Calculate Countable Earned Income = Earned Income - Disregard
5. Calculate Net Countable Income = Countable Earned + Unearned
6. Determine Payment Standard based on family size and shelter tier
7. TCA Benefit = max(Payment Standard - Net Countable Income, $10 or $0)

**Source**:
- Florida Statutes 414.095(12)
- FAC 65A-4.210
- FAC 65A-4.220

---

## Budgeting Methodology

### Prospective Budgeting

Florida uses a **prospective budgeting system** where eligibility and benefit amount for a payment month are based on the Department's estimate of the assistance group's projected income and circumstances for that month.

### Income Conversion Factors

| Income Frequency | Conversion Factor |
|------------------|-------------------|
| Weekly | Multiply by 4.3 |
| Biweekly | Multiply by 2.15 |
| Semi-monthly | Multiply by 2 |

### Income Averaging

For determining future earnings, all income from the most recent four weeks shall be used if representative of future earnings. A longer period may be used if necessary to provide a more accurate indication of anticipated fluctuations.

**Source**: FAC 65A-4.210

---

## Demographic Eligibility

### Age Requirements

**Minor Child**: Under age 18
**Exception**: Under age 19 if full-time secondary (high school) student

**Source**:
- Florida DCF TCA Page
- FAC 65A-4.207

### Pregnant Women

Eligible in specific circumstances:
- Third trimester if unable to work, OR
- Ninth month of pregnancy

**Source**:
- Florida DCF TCA Page
- Florida Statutes 414.095

### Implementation Approach

- [ ] Use federal demographic eligibility (age 18/19 matches federal)
- [x] Age thresholds match federal definition

---

## Immigration Eligibility

### Citizenship Requirement

Must be U.S. citizen or qualified non-citizen as defined in 8 U.S.C. Section 1641(b)

**Source**: FAC 65A-1.205

### Implementation Approach

- [x] Use federal immigration eligibility (state follows federal rules)

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limit

**48-month lifetime limit** for adults receiving TCA. This cannot be enforced in PolicyEngine's single-period simulation architecture.

**Exception**: Child-only cases have no time limit.

**Source**: Florida DCF TCA Page

### Work Participation Requirements

Adults must work or participate in job training (with possible exemptions). Cannot track work history across periods.

**Source**: Florida Statutes 414.095

---

## Relative Caregiver Program (Child-Only Cases)

### Payment Standards by Age

| Child Age | Monthly Payment |
|-----------|-----------------|
| 0-5 years | $242 |
| 6-12 years | $249 |
| 13-17 years | $298 |

### Eligibility

- Child must be court-ordered dependent by a Florida court
- Placed in relative caregiver's home by DCF Child Welfare/Community Based Care
- Child's countable assets must be $2,000 or less
- Child's net countable income cannot exceed payment standard for child's age
- Relative caregiver must be within specified degree of relationship

**Source**:
- Florida DCF TCA Page
- FAC 65C-28.008 (Relative Caregiver Program Requirements)
- URL: https://www.law.cornell.edu/regulations/florida/Fla-Admin-Code-Ann-R-65C-28-008

---

## Family Cap Policy

Florida has a **family cap policy** but provides a reduced increment for additional children born after initial TANF eligibility is determined.

**Note**: Unlike some states that provide $0 for family cap children, Florida does increase benefits but at less than the normal increment.

**Source**: ACF Welfare Rules Databook

---

## Implementation Notes

### Parameter Structure

Suggested parameter organization for `gov/states/fl/dcf/tanf/`:
```
tanf/
  income/
    gross_test/
      fpl_multiplier.yaml          # 1.85 (185% FPL)
      earned_income_deduction.yaml # $90 per person
    disregard/
      first_amount.yaml            # $200
      rate.yaml                    # 0.5 (50%)
    exclusions/
      infrequent_unearned.yaml     # $60/quarter
  payment_standard/
    tier_1.yaml                    # >$50 shelter
    tier_2.yaml                    # $1-$50 shelter
    tier_3.yaml                    # $0 shelter
  resources/
    limit.yaml                     # $2,000
    vehicle_limit.yaml             # $8,500
  minimum_grant.yaml               # $10
  relative_caregiver/
    payment_by_age.yaml            # $242/$249/$298
```

### Key Implementation Decisions

1. **Two-Step Income Test**: Must implement both 185% FPL gross test AND payment standard net test
2. **Shelter-Based Payment**: Payment standard varies by shelter cost tier (0, 1-50, >50)
3. **$90 vs $200+50%**: Different deductions for different tests
4. **No Child Care Deduction**: Explicitly prohibited by statute
5. **Student Income Exclusion**: Full exclusion for students 19 and under

### References for Implementation

```yaml
# For parameters:
reference:
  - title: "Florida Statutes 414.095(10) - Payment Standards"
    href: "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html"
  - title: "FAC 65A-4.209 - Income"
    href: "https://flrules.org/gateway/RuleNo.asp?id=65A-4.209"
```

```python
# For variables:
reference = (
    "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
    "https://flrules.org/gateway/RuleNo.asp?id=65A-4.209",
)
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Florida TANF State Plan 2023-2026**
   - URL: https://www.floridajobs.org/docs/default-source/office-of-the-inspector-general/florida-tanf-state-plan-2023-2026.pdf
   - Expected content: Detailed state plan with income calculation methodology, federal reporting requirements

2. **Florida DCF Calculation of Benefits Manual (Chapter 2600)**
   - URL: https://www.myflfamilies.com/sites/default/files/2023-02/2600.pdf
   - Expected content: Step-by-step benefit calculation procedures, eligibility determination process
   - Key pages: Contains detailed calculation methodology for income tests

3. **NCCP Florida TANF Profile (November 2024)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Florida.pdf
   - Expected content: Current policy summary, benefit levels as percentage of FPL

4. **Florida Legislature Bill Analysis (HB 409, 2024)**
   - URL: https://www.flsenate.gov/Session/Bill/2024/409/Analyses/h0409.CFS.PDF
   - Expected content: Legislative analysis with current TCA eligibility requirements and proposed changes

---

## Sources Consulted

1. Florida Statutes Chapter 414, Section 414.095
   - https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html

2. Florida Administrative Code Chapter 65A-4
   - https://flrules.org/gateway/ChapterHome.asp?Chapter=65A-4

3. Florida DCF Temporary Cash Assistance Official Page
   - https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance

4. Florida Law Help - Cash Assistance Benefits
   - https://www.floridalawhelp.org/health-public-benefits/food-cash-benefits/cash-assistance-benefits

5. Florida Policy Institute - P-TANF FAQ
   - https://www.floridapolicy.org/posts/floridas-p-tanf-program-answers-to-frequently-asked-questions

6. ACF Welfare Rules Databook (July 2023)
   - https://acf.gov/opre/report/welfare-rules-databook-state-and-territory-tanf-policies-july-2023
