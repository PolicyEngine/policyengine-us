# Collected Documentation

## Florida TANF Implementation
**Collected**: October 21, 2025
**Implementation Task**: Florida Temporary Assistance for Needy Families (TANF) / Temporary Cash Assistance (TCA) program

### Source Information

**Primary Legal Authority**:
- **Title**: Florida Statute Chapter 414 - Temporary Cash Assistance Program
- **Citation**: Fla. Stat. Ch. 414
- **URL**: http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/0414.html
- **Effective Date**: Current as of 2024

**Primary Regulations**:
- **Title**: Florida Administrative Code Chapter 65A-4 - Temporary Cash Assistance
- **Citation**: Fla. Admin. Code Ch. 65A-4
- **URL**: https://flrules.org/gateway/ChapterHome.asp?Chapter=65A-4
- **Effective Date**: Various rules updated through 2024

**Federal Authority**:
- **Title**: Personal Responsibility and Work Opportunity Reconciliation Act of 1996
- **Citation**: 42 U.S.C. § 601 et seq.
- **URL**: https://www.govinfo.gov/content/pkg/USCODE-2011-title42/html/USCODE-2011-title42-chap7-subchapIV-partA.htm

### Key Rules and Thresholds

#### Eligibility Requirements
- **Categorical**: Families with children under 18 (or under 19 if full-time high school student) or pregnant women
- **Citizenship**: U.S. citizens or qualified noncitizens
- **Residency**: Florida legal resident
- **Income limit**: Gross income < 185% FPL; Net countable income ≤ payment standard
- **Asset limit**: $2,000 countable assets
- **Vehicle limit**: $8,500 combined value for work-eligible individuals
- **Time limit**: 48 months lifetime as adult (child-only cases exempt)

#### 2024 Gross Income Limits (185% FPL)
| Family Size | Annual | Monthly |
|-------------|---------|---------|
| 1 | $27,861 | $2,322 |
| 2 | $37,814 | $3,151 |
| 3 | $47,767 | $3,981 |
| 4 | $57,720 | $4,810 |
| 5 | $67,673 | $5,639 |

#### Payment Standards (Three-Tier System based on shelter obligation)

**Florida Statute § 414.095(10) establishes three tiers**:
- Tier 1: No shelter obligation ($0)
- Tier 2: Shelter obligation $1-$50
- Tier 3: Shelter obligation >$50 OR homeless

| Family Size | Tier 1 | Tier 2 | Tier 3 |
|-------------|--------|--------|--------|
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
| 13+ | $678 | $781 | $919 |

**Note**: Tier 3 payment for family of 3 ($303) unchanged since 1992

### Calculation Formulas

#### Basic Benefit Formula
```
Monthly TANF Benefit = Payment Standard - Net Countable Income
(rounded down to nearest dollar, minimum $10)
```

#### Earned Income Disregards (Florida Statute § 414.095)

**Step 1 - Standard Disregard**: $90 per individual

**Step 2 - Work Incentive Disregard**: First $200 plus one-half of remainder
```
Gross Earned Income
- $90 (standard disregard)
= Subtotal
- $200
= Remainder
× 0.5 (disregard half of remainder)
= Countable Earned Income
```

**Example**:
```
Gross Earned Income: $1,000
Step 1: $1,000 - $90 = $910
Step 2: $910 - $200 = $710
        $710 × 0.5 = $355 (countable portion)
Countable Earned Income: $355
```

#### Income Exclusions (FAC Rule 65A-4.209)

**Earned Income - Fully Excluded**:
- Full-time student (elementary/secondary/equivalent) minor child earnings
- Minor child WIOA (Workforce Innovation and Opportunity Act) income
- Adult WIOA income (except wages paid directly by employer)
- Child under 19 in high school earnings

**Unearned Income - Fully Excluded**:
- Infrequent/irregular income <$60 per quarter (gifts, etc.)

**Partially Excluded**:
- First $50 of child support (remainder counted as unearned income)

### Special Cases and Exceptions

#### Family Cap Policy
**CRITICAL STATE-SPECIFIC RULE**: Florida is one of 6 states with family cap

- **Second child born while receiving TANF**: Benefits reduced by 50%
  - Example: $31/month instead of $62 increment
- **Third+ children born while receiving TANF**: NO benefits
- **Exceptions**: Parent incarcerated/institutionalized, or child from rape/incest/sexual exploitation

#### Work Requirement Exemptions
- Domestic violence victims unable to comply
- Medical incapacity (verified by physician)
- Mental health/substance abuse treatment (up to 5 hours/week)
- Person totally responsible for disabled family member care (no alternative available)
- Single parent with child <6 when childcare unavailable

#### Sanctions for Non-Compliance
- First violation: 10 days minimum termination
- Second violation: 1 month termination
- Third violation: 3 months termination

#### Time Limit Extensions
- Up to 20% of average monthly caseload may receive hardship extensions
- Criteria: Work participation + employment barriers, domestic violence, awaiting SSI/SSDI

#### Pregnant Women
- 3rd trimester if unable to work
- 9th month automatic eligibility

#### Drug Screening
- Mandatory for applicants (applicant pays cost)
- Positive test = 1 year ineligibility

### Implementation Notes for Code

#### Parameters to Define

**Income Limits** (by year and family size):
```yaml
fl_tanf_gross_income_limit:
  2024:
    1: 27_861
    2: 37_814
    3: 47_767
    4: 57_720
    5: 67_673
  reference:
    - title: "Florida Statute § 414.095 - Determining eligibility for temporary cash assistance"
      href: "https://www.flsenate.gov/Laws/Statutes/2024/414.095"
```

**Payment Standards** (three-tier system):
```yaml
fl_tanf_payment_standard:
  tier_1:  # No shelter obligation
    2024:
      1: 95
      2: 158
      3: 198
      # ... etc
  tier_2:  # Shelter $1-$50
    2024:
      1: 153
      2: 205
      3: 258
      # ... etc
  tier_3:  # Shelter >$50 or homeless
    2024:
      1: 180
      2: 241
      3: 303
      4: 364
      5: 426
      6: 487
      7: 549
      8: 610
      9: 671
      10: 733
      11: 795
      12: 857
      13: 919
  reference:
    - title: "Florida Statute § 414.095(10)"
      href: "https://www.flsenate.gov/Laws/Statutes/2024/414.095"
```

**Asset Limits**:
```yaml
fl_tanf_asset_limit:
  2024: 2_000
  reference:
    - title: "Florida Statute § 414.075"
      href: "http://www.leg.state.fl.us/statutes/"

fl_tanf_vehicle_limit:
  2024: 8_500
  reference:
    - title: "Florida Statute § 414.075"
      href: "http://www.leg.state.fl.us/statutes/"
```

**Disregards**:
```yaml
fl_tanf_earned_income_disregard_standard:
  2024: 90
  reference:
    - title: "Florida DCF TCA Documentation"
      href: "https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance"

fl_tanf_earned_income_disregard_base:
  2024: 200
  reference:
    - title: "Florida Statute § 414.095 - Work Incentive Disregard"
      href: "https://www.flsenate.gov/Laws/Statutes/2024/414.095"

fl_tanf_earned_income_disregard_rate:
  2024: 0.5
  reference:
    - title: "Florida Statute § 414.095"
      href: "https://www.flsenate.gov/Laws/Statutes/2024/414.095"

fl_tanf_child_support_disregard:
  2024: 50
  reference:
    - title: "Florida Statute § 414.095"
      href: "https://www.flsenate.gov/Laws/Statutes/2024/414.095"

fl_tanf_irregular_income_exclusion:
  2024: 60  # Per quarter
  reference:
    - title: "FAC Rule 65A-4.209"
      href: "http://flrules.elaws.us/fac/65a-4.209"
```

**Time Limits**:
```yaml
fl_tanf_time_limit_months:
  2024: 48
  reference:
    - title: "Florida Statute § 414.105"
      href: "http://www.leg.state.fl.us/statutes/"
```

#### Variables to Define

**Eligibility Variables**:
```python
# fl_tanf_eligible
reference = "Florida Statute § 414.095"
documentation = "https://www.flsenate.gov/Laws/Statutes/2024/414.095"

# fl_tanf_meets_categorical_requirements
reference = "Florida Statute § 414.095; FAC Rule 65A-4.208"

# fl_tanf_meets_income_test
reference = "Florida Statute § 414.095; FAC Rule 65A-4.209"

# fl_tanf_meets_asset_test
reference = "Florida Statute § 414.075"
```

**Income Variables**:
```python
# fl_tanf_gross_income
reference = "FAC Rule 65A-4.209"
documentation = "http://flrules.elaws.us/fac/65a-4.209"

# fl_tanf_earned_income_deduction
reference = "Florida Statute § 414.095 - Earned income disregards"

# fl_tanf_countable_income
reference = "FAC Rule 65A-4.209 - Income calculation"
```

**Benefit Variables**:
```python
# fl_tanf_payment_standard
reference = "Florida Statute § 414.095(10)"
documentation = "Three-tier payment structure based on shelter obligation"

# fl_tanf_shelter_tier
reference = "Florida Statute § 414.095(10)"
# Returns: 1 (no shelter), 2 ($1-$50), or 3 (>$50 or homeless)

# fl_tanf
reference = "Florida Statute § 414.095(12)"
documentation = "https://www.flsenate.gov/Laws/Statutes/2024/414.095"
# Formula: payment_standard - countable_income, rounded down, min $10
```

**Special Provision Variables**:
```python
# fl_tanf_family_cap_applies
reference = "Florida Policy Institute analysis"
documentation = "https://www.floridapolicy.org/posts/5-reasons-why-florida-lawmakers-should-repeal-the-outdated-family-cap-law"

# fl_tanf_work_exempt
reference = "Florida Statute § 414.065; § 414.105"

# fl_tanf_months_received
reference = "Florida Statute § 414.105 - Time limits"
```

### Key Implementation Decisions

1. **Three-tier structure**: Need variable to determine shelter obligation tier (likely based on housing costs)
2. **Family cap**: Need to track birth order and timing relative to TANF receipt
3. **Earned income disregard**: Two-step process ($90 standard + $200 + 50% remainder)
4. **Student income**: Full exclusion for qualifying students
5. **WIOA income**: Special exclusion rules
6. **Minimum benefit**: $10 floor (below this, no cash but retain categorical eligibility)
7. **Child-only cases**: Exempt from time limits
8. **Shelter costs**: Needed to determine tier assignment

### Testing Scenarios

1. **Basic family with earned income**: Family of 3, $500/month earnings, Tier 3 shelter
2. **Family cap case**: Family on TANF has additional child
3. **Student income**: Teen with part-time job while in high school
4. **Multiple income sources**: Earned + child support
5. **Boundary cases**: Income exactly at payment standard
6. **Minimum benefit**: Calculation resulting in <$10
7. **Different tiers**: Same income/family size across three shelter tiers

### References for Metadata

```yaml
# For parameters:
reference:
  - title: "Florida Statute Chapter 414 - Temporary Cash Assistance"
    href: "http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/0414.html"
  - title: "Florida Administrative Code Chapter 65A-4"
    href: "https://flrules.org/gateway/ChapterHome.asp?Chapter=65A-4"
```

```python
# For variables:
reference = "Florida Statute § 414.095"
documentation = "https://www.flsenate.gov/Laws/Statutes/2024/414.095"
```

### Additional Resources

**Policy Analysis**:
- NCCP TANF Profile: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Florida.pdf
- Florida Policy Institute Family Cap: https://www.floridapolicy.org/posts/5-reasons-why-florida-lawmakers-should-repeal-the-outdated-family-cap-law

**State Resources**:
- Florida DCF TCA Page: https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance
- ACCESS Florida Application: https://www.myflorida.com/accessflorida/

**Federal Resources**:
- ACF TANF Overview: https://www.acf.hhs.gov/ofa/programs/tanf
- Welfare Rules Databook: https://acf.gov/opre/report/welfare-rules-databook-state-and-territory-tanf-policies-july-2023
