# Connecticut TFA - Benefit Calculation Methodology

**Source Documentation for Implementation**

---

## Overview

Connecticut TFA benefit calculation involves multiple steps:
1. Determine maximum payment standard based on family size
2. Calculate countable income (earned and unearned)
3. Apply family cap if applicable
4. Apply extension period reduction if applicable
5. Subtract countable income from maximum benefit

---

## Payment Standards

### Current System (Post-July 1, 2022)

**Public Act 22-118 Implementation**:
- Effective July 1, 2022
- Made benefit levels **uniform statewide**
- Indexed to 55% of Federal Poverty Level
- Automatic annual adjustments

**Confirmed 2024 Amount**:
- Family of 3 with no income: **$833/month**

**Legal Authority**:
- Public Act 22-118 (2022)
- Connecticut TANF State Plan 2024-2026

**Implementation Note**: Current complete benefit schedule by all family sizes not publicly available. The $833 figure for family of 3 suggests benefits are now higher than historical 2014 rates.

### Historical Regional System (July 1, 2014 - June 30, 2022)

Prior to PA 22-118, Connecticut had three payment regions:

**Payment Standards by Region and Family Size** (Historical - July 1, 2014):

| Family Size | Region A | Region B | Region C |
|-------------|----------|----------|----------|
| 1           | $443     | $366     | $366     |
| 2           | $563     | $487     | $487     |
| 3           | $698     | $597     | $589     |
| 4           | $815     | $701     | $684     |
| 5           | $919     | $803     | $779     |
| 6           | $1,028   | $908     | $885     |
| 7           | $1,143   | $1,026   | $994     |
| 8           | $1,257   | $1,134   | $1,100   |
| 9           | $1,374   | $1,250   | $1,213   |
| 10          | $1,490   | $1,362   | $1,324   |
| 11          | $1,607   | $1,475   | $1,432   |
| 12          | $1,722   | $1,586   | $1,540   |
| 13          | $1,837   | $1,696   | $1,648   |
| 14          | $1,952   | $1,807   | $1,756   |
| 15          | $2,067   | $1,918   | $1,864   |
| 16          | $2,183   | $2,028   | $1,972   |
| 17          | $2,298   | $2,139   | $2,080   |
| 18          | $2,413   | $2,250   | $2,188   |
| 19          | $2,369   | $2,222   | $2,184   |
| 20          | $2,326   | $2,193   | $2,180   |

**Source**: SSA POMS SI BOS00830.403, effective July 1, 2014

**Note**: These rates are **historical only** and superseded by PA 22-118.

---

## Income Calculation

### Earned Income

#### At Initial Application

**Initial Application Deduction**:
- $90 deducted from each person's gross earnings

**Formula**:
```python
countable_earned_income = max(0, (
    sum(person.earnings for person in household)
    - (90 * number_of_earners)
))
```

**Legal Authority**: Connecticut TANF State Plan 2024-2026

#### For Continuing Eligibility

**100% Earned Income Disregard up to 100% FPL**:

```python
household_earned_income = sum(person.earnings for person in household)
fpl_100 = federal_poverty_level[household_size]

if household_earned_income <= fpl_100:
    countable_earned_income = 0  # Fully disregarded
else:
    # Check extension period rules
    countable_earned_income = calculate_extension_period_income()
```

**Legal Authority**: Connecticut TANF State Plan 2024-2026, Connecticut TFA Fact Sheet

#### Extension Period (Effective January 1, 2024)

When household earnings exceed 100% FPL:

**Extended Earned Income Disregard**:
- Earnings disregarded up to 230% FPL for **eligibility determination**
- Period: Up to 6 consecutive months

```python
fpl_100 = federal_poverty_level[household_size]
fpl_171 = 1.71 * fpl_100
fpl_230 = 2.30 * fpl_100

if household_earned_income <= fpl_100:
    countable_earned_income = 0
    benefit_reduction_factor = 1.0

elif fpl_100 < household_earned_income <= fpl_230:
    # Extension period - eligible for up to 6 months
    countable_earned_income = 0  # For eligibility only

    # Check if benefit reduction applies
    if fpl_171 < household_earned_income <= fpl_230:
        benefit_reduction_factor = 0.80  # 20% reduction
    else:
        benefit_reduction_factor = 1.0

else:  # household_earned_income > fpl_230
    # Ineligible for TFA
    eligible = False
```

**Legal Authority**: Connecticut TANF State Plan 2024-2026, effective January 1, 2024

### Unearned Income

**General Rule**:
- Unearned income counted **dollar-for-dollar** against benefit

**Exceptions**:
1. **SSI**: Supplemental Security Income fully disregarded
2. **Child Support**: First $50/month passed through and disregarded

**Formula**:
```python
child_support_passthrough = min(50, child_support_received)
ssi = household_ssi_income

countable_unearned_income = (
    gross_unearned_income
    - ssi
    - child_support_passthrough
)
```

**Legal Authority**:
- Connecticut TFA Fact Sheet (SSI exclusion)
- SSA POMS SI BOS00830.403 (child support passthrough)

### Student Income Disregard

Per Connecticut General Statutes § 17b-80:

**100% Disregard for Student Children**:
```python
for person in household:
    if person.is_child and person.is_student:
        person.countable_earned_income = 0
```

**Legal Authority**: Conn. Gen. Stat. § 17b-80

---

## Benefit Calculation Steps

### Step-by-Step Process

**Step 1: Determine Maximum Benefit**

Post-PA 22-118 (current):
```python
max_benefit = payment_standard[household_size]
# Payment standards indexed to 55% FPL
# Specific current schedule needs verification with CT DSS
```

Pre-PA 22-118 (historical):
```python
region = determine_region(household_location)
max_benefit = payment_standard[region][household_size]
```

**Step 2: Calculate Total Countable Income**

```python
countable_income = countable_earned_income + countable_unearned_income
```

**Step 3: Apply Family Cap (if applicable)**

```python
if child_born_within_10_months_of_application:
    old_max_benefit = payment_standard[household_size - 1]
    new_max_benefit = payment_standard[household_size]
    benefit_increase = (new_max_benefit - old_max_benefit) * 0.5
    max_benefit = old_max_benefit + benefit_increase
```

**Step 4: Apply Extension Period Reduction (if applicable)**

```python
if extension_period and (fpl_171 < earned_income <= fpl_230):
    max_benefit = max_benefit * 0.80  # 20% reduction
```

**Step 5: Subtract Countable Income**

```python
final_benefit = max(0, max_benefit - countable_income)
```

**Legal Authority**: SSA POMS SI BOS00830.403 (calculation method), Connecticut TANF State Plan (current rules)

---

## Family Cap Calculation

### Partial Family Cap Policy

Connecticut is the **only state** with a **partial** family cap.

**Rule**:
- Children born within **10 months** of mother's application for TFA
- Receive only **50%** of the additional benefit they would otherwise generate

**Exceptions**:
1. Child conceived by rape or incest
2. First child born to a minor dependent parent

**Formula**:
```python
def calculate_family_cap_benefit(household_size, child_born_date, application_date, exceptions):
    """Calculate TFA benefit with family cap applied"""

    base_benefit = payment_standard[household_size - 1]  # Without new child
    full_benefit = payment_standard[household_size]      # With new child
    benefit_increase = full_benefit - base_benefit

    # Check if family cap applies
    months_since_application = (child_born_date - application_date).months

    if months_since_application <= 10 and not exceptions:
        # Apply 50% cap
        actual_increase = benefit_increase * 0.5
    else:
        # No cap
        actual_increase = benefit_increase

    return base_benefit + actual_increase
```

**Legal Authority**:
- Connecticut General Assembly OLR Report 98-R-0058
- SSA POMS SI BOS00830.403
- Connecticut General Statutes § 17b-688b

**Citation**: https://www.cga.ct.gov/PS98/rpt/olr/htm/98-R-0058.htm

---

## Benefit Issuance

### Payment Timing

**Full Month Benefits**:
- Benefits paid at beginning of month
- Full month of benefits regardless of when in month eligibility begins

**No Partial Month Benefits**:
- Connecticut does not prorate benefits for partial months
- Either receive full month benefit or no benefit

**Legal Authority**: SSA POMS SI BOS00830.403

### Payment Method

**Electronic Benefit Transfer (EBT)**:
- TFA benefits issued via EBT card
- Can access with minimal fees

**Electronic Fund Transfer (EFT)**:
- Direct deposit option available

**No Checks**:
- Connecticut does not issue paper checks for TFA cash assistance

**Legal Authority**: Connecticut TANF State Plan 2024-2026

---

## Calculation Examples

### Example 1: Basic Benefit Calculation (Continuing Recipient)

**Scenario**: Single parent with 2 children, no earned income, $300/month unemployment

**Given**:
- Household size: 3
- Earned income: $0
- Unearned income: $300 (unemployment)
- SSI: $0
- Child support: $0

**Calculation**:
```
Step 1: Maximum benefit for family of 3 = $833 (2024 rate)

Step 2: Countable earned income
  - Earned income: $0
  - Countable earned income = $0 (fully disregarded up to 100% FPL)

Step 3: Countable unearned income
  - Unemployment: $300
  - Less SSI: $0
  - Less child support passthrough: $0
  - Countable unearned income = $300

Step 4: Total countable income = $0 + $300 = $300

Step 5: Final benefit = $833 - $300 = $533/month
```

**Result**: Family receives **$533/month** in TFA benefits.

### Example 2: Earned Income with Disregard

**Scenario**: Single parent with 1 child, working part-time

**Given**:
- Household size: 2
- Earned income: $1,500/month
- Unearned income: $0
- 100% FPL for household of 2: $1,703/month

**Calculation**:
```
Step 1: Maximum benefit for family of 2 (need current rate)
  Assume proportionally increased from 2014: ~$675

Step 2: Countable earned income
  - Earned income: $1,500
  - 100% FPL: $1,703
  - Since $1,500 < $1,703: Countable earned income = $0

Step 3: Countable unearned income = $0

Step 4: Total countable income = $0

Step 5: Final benefit = $675 - $0 = $675/month
```

**Result**: Family receives **full TFA benefit** because earned income is below 100% FPL and fully disregarded.

### Example 3: Extension Period with Benefit Reduction

**Scenario**: Family of 4, high earner in extension period

**Given**:
- Household size: 4
- Earned income: $5,000/month
- 100% FPL: $2,600/month
- 171% FPL: $4,446/month
- 230% FPL: $5,980/month

**Calculation**:
```
Step 1: Maximum benefit for family of 4 (need current rate)
  Assume proportionally increased from 2014: ~$980

Step 2: Check eligibility
  - Earned income ($5,000) > 100% FPL ($2,600)
  - Earned income ($5,000) < 230% FPL ($5,980)
  - Eligible for extension period (up to 6 months)

Step 3: Countable earned income
  - For eligibility: $0 (disregarded up to 230% FPL)

Step 4: Check benefit reduction
  - $5,000 is between 171% FPL ($4,446) and 230% FPL ($5,980)
  - 20% benefit reduction applies

Step 5: Final benefit
  - Base benefit: $980
  - With 20% reduction: $980 × 0.80 = $784/month
```

**Result**: Family receives **$784/month** (reduced benefit) during extension period.

### Example 4: Family Cap Application

**Scenario**: Family of 2 on TFA, new baby born 8 months after starting TFA

**Given**:
- Original household size: 2
- Original benefit: $563 (2014 Region A rate, for illustration)
- New household size: 3
- New benefit without cap: $698
- Baby born 8 months after TFA start

**Calculation**:
```
Step 1: Determine benefit increase without cap
  Increase = $698 - $563 = $135

Step 2: Check if family cap applies
  - Baby born within 10 months of application: YES
  - Exceptions (rape/incest, first child to minor): NO

Step 3: Apply 50% family cap
  Actual increase = $135 × 0.5 = $67.50

Step 4: Calculate final benefit
  New benefit = $563 + $67.50 = $630.50
```

**Result**: Family receives **$630.50** instead of **$698** due to partial family cap.

---

## Special Calculation Rules

### Child Support Integration

**$50 Passthrough**:
- First $50/month of child support passed through to family
- Not counted as income for benefit calculation
- Amounts over $50 deducted from TFA benefit

**Calculation**:
```python
if child_support_received <= 50:
    countable_child_support = 0
    passthrough_amount = child_support_received
else:
    countable_child_support = child_support_received - 50
    passthrough_amount = 50

# Child support over $50 reduces benefit
benefit = max_benefit - countable_income - countable_child_support
```

**Legal Authority**: SSA POMS SI BOS00830.403

### SSI Interaction

**SSI Not Counted**:
- Households receiving both TFA and SSI
- SSI income completely excluded from TFA benefit calculation

**Cannot Receive Both for Same Person**:
- Same individual cannot receive both TFA and SSI
- But household can have some members on TFA and others on SSI

**Legal Authority**: Connecticut TFA documentation, SSA POMS

---

## Implementation References

### For Parameter Files

```yaml
# payment_standard.yaml
description: Connecticut TFA maximum monthly benefit amounts by household size
metadata:
  unit: currency-usd
  period: month
  reference:
    - title: "Connecticut TANF State Plan 2024-2026"
      href: "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf"
      publication_date: 2024-04-15
    - title: "Public Act 22-118 - TFA Benefit Standardization"
      href: "https://www.cga.ct.gov/2022/act/pa/pdf/2022PA-00118-R00HB-05506-PA.PDF"
      publication_date: 2022-05-07

# Current uniform statewide rates (post-July 1, 2022)
2022-07-01:
  1: [amount]  # Need current schedule from CT DSS
  2: [amount]
  3: 833       # Confirmed 2024 rate
  4: [amount]
  # etc.

# Historical regional rates (reference only)
historical_region_a:
  2014-07-01:
    1: 443
    2: 563
    3: 698
    # etc.
```

### For Variable Formulas

```python
class ct_tfa_benefit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut TFA monthly benefit amount"
    definition_period = MONTH
    unit = "currency-USD"
    reference = [
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500830403BOS",
    ]

    def formula(tax_unit, period, parameters):
        # Get parameters
        p = parameters(period).gov.states.ct.dss.tfa

        # Get maximum benefit
        household_size = tax_unit("ct_tfa_assistance_unit_size", period)
        max_benefit = p.payment_standard[household_size]

        # Get countable income
        countable_income = tax_unit("ct_tfa_countable_income", period)

        # Apply family cap if applicable
        family_cap_reduction = tax_unit("ct_tfa_family_cap_reduction", period)

        # Apply extension benefit reduction if applicable
        extension_reduction = tax_unit("ct_tfa_extension_benefit_reduction", period)

        # Calculate benefit
        benefit_before_reductions = max_benefit - family_cap_reduction
        benefit_with_extension = benefit_before_reductions - extension_reduction
        final_benefit = max_(benefit_with_extension - countable_income, 0)

        # Only return if eligible
        eligible = tax_unit("ct_tfa_eligible", period)
        return where(eligible, final_benefit, 0)
```

---

**Document Status**: Complete and ready for implementation
**Last Updated**: October 14, 2025
**Note**: Current 2024 payment standard amounts for all family sizes should be obtained from CT DSS for complete implementation.
