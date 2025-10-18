# Connecticut TFA - Eligibility Requirements

**Source Documentation for Implementation**

---

## Categorical Eligibility

### Eligible Family Types

**Families with Dependent Children**:
- Children under age 18
- Children who are 18 years old AND enrolled full-time in:
  - High school
  - Vocational school
  - Technical school

**Legal Authority**: Connecticut TFA Fact Sheet, CT TANF State Plan

**Pregnant Women**:
- Pregnant women may qualify for TFA benefits
- No specific documentation of gestational age requirements found

**Legal Authority**: Connecticut TFA Fact Sheet

### Adult-Child Relationship Requirement

The child(ren) must live with:
- A related adult (parent, grandparent, aunt, uncle, sibling, etc.) OR
- An adult who has filed for guardianship

**Legal Authority**: Connecticut TFA Fact Sheet

**Implementation Note**: "Related adult" includes both blood relatives and relatives by marriage.

---

## Income Eligibility

### Initial Eligibility (New Applicants)

**Standard of Need = 55% of Federal Poverty Level**

**Earned Income Test**:
```
Gross Earned Income < (55% FPL for household size)
```

**Initial Application Deduction**:
- $90 deducted from each person's gross earnings at time of application

**Calculation**:
```python
countable_earned_income = sum(person.earnings for person in household) - (90 * number_of_earners)
eligible = countable_earned_income < (0.55 * federal_poverty_level[household_size])
```

**Unearned Income Test**:
```
Unearned Income < Standard of Need (55% FPL)
```

**Legal Authority**:
- Connecticut TANF State Plan 2024-2026
- Public Act 22-118 (2022)

### Continuing Eligibility (Active Recipients)

**Earned Income Limit = 100% Federal Poverty Level**

Once enrolled in TFA:
- Earned income **fully disregarded** (100% exclusion) up to 100% FPL
- Family can earn up to 100% FPL and remain eligible

**Calculation**:
```python
if household_earned_income <= federal_poverty_level[household_size]:
    countable_earned_income = 0
    eligible = True
else:
    # Check extension period rules
    eligible = check_extension_eligibility()
```

**Legal Authority**: Connecticut TANF State Plan 2024-2026, Connecticut TFA Fact Sheet

### Extension Period Eligibility (Effective January 1, 2024)

When earnings exceed 100% FPL, families may continue receiving benefits for up to **6 consecutive months** if:

**Extended Eligibility Limit = 230% Federal Poverty Level**

```python
if 100% FPL < household_earned_income <= 230% FPL:
    # Eligible for extension period (up to 6 months)
    countable_earned_income = 0  # For eligibility determination only
    eligible = True

    # But check if benefit reduction applies
    if 171% FPL < household_earned_income <= 230% FPL:
        benefit_multiplier = 0.80  # 20% benefit reduction
    else:
        benefit_multiplier = 1.0

elif household_earned_income > 230% FPL:
    eligible = False
```

**Legal Authority**: Connecticut TANF State Plan 2024-2026, effective January 1, 2024

### Income Eligibility by Household Size (2024)

| Household Size | Initial Eligibility<br>(55% FPL) | Continuing Eligibility<br>(100% FPL) | Extension Limit<br>(230% FPL) |
|----------------|----------------------------------|--------------------------------------|-------------------------------|
| 1              | $690/month                       | $1,255/month                         | $2,887/month                  |
| 2              | $937/month                       | $1,703/month                         | $3,917/month                  |
| 3              | $1,184/month                     | $2,152/month                         | $4,950/month                  |
| 4              | $1,430/month                     | $2,600/month                         | $5,980/month                  |
| 5              | $1,676/month                     | $3,048/month                         | $7,010/month                  |
| 6              | $1,923/month                     | $3,497/month                         | $8,043/month                  |
| 7              | $2,170/month                     | $3,945/month                         | $9,074/month                  |
| 8              | $2,416/month                     | $4,393/month                         | $10,104/month                 |

**Formula for additional household members**:
- Add $448/month (55% of $815 annual increment)

---

## Asset Eligibility

### Asset Limit

**Total Countable Assets ≤ $6,000**

**Legal Authority**:
- Connecticut TFA Fact Sheet
- Connecticut TANF State Plan 2024-2026

**Historical Note**: Earlier sources cited $3,000 asset limit. Current limit is $6,000.

### Asset Exclusions

**Home Property**:
- Home (primary residence) not counted toward asset limit

**One Vehicle**:
Vehicle excluded from asset calculation if:
- (Fair market value - debt owed) < $9,500 OR
- Vehicle used to transport household member with a disability (no value limit)

**Calculation**:
```python
vehicle_equity = fair_market_value - debt_owed

if vehicle_equity < 9_500:
    countable_vehicle_value = 0
elif vehicle_used_for_disabled_transport:
    countable_vehicle_value = 0
else:
    countable_vehicle_value = vehicle_equity
```

**Guardian Assets**:
- Non-parent guardian's assets not counted when determining child's eligibility

**Legal Authority**: Connecticut TFA Fact Sheet

---

## Time Limit Eligibility

### State Time Limit

**Families with Employable Adult**:
- Maximum **36 months** of TFA benefits in Connecticut
- Effective: April 1, 2024 (increased from prior limit)

**Families without Employable Adult**:
- **No state time limit**

**Extensions Available**:
- Up to two **6-month extensions**
- Must continue to meet income and asset guidelines
- Extensions granted if time limit was for employability reasons

**Legal Authority**:
- Connecticut TANF State Plan 2024-2026 (revised April 15, 2024)
- Connecticut General Statutes § 17b-112

### Federal Lifetime Limit

**60-Month Federal Limit**:
- Cannot receive more than **60 months** of TFA/TANF in lifetime
- Counts TANF benefits received in ANY state
- Month counts if family receives assistance for any day of that month

**Exception**:
- Domestic violence victims may receive benefits beyond 60 months

**Legal Authority**:
- Federal TANF statute
- Connecticut General Statutes § 17b-112

### Time Limit Exemptions

Individuals exempt from time limits and work requirements:

1. **Disability**:
   - Physical or mental disability that prevents work

2. **Age-Related**:
   - Individual 60 years of age or older caring for dependent child

3. **Caring for Young Child**:
   - Caring for child under 1 year old

4. **Caring for Disabled**:
   - Caring for household member with a disability

5. **Pregnancy/Postpartum**:
   - Pregnant women unable to work
   - Postpartum women unable to work

6. **Non-Parent Caregiver**:
   - Non-parent relative or guardian who only receives cash for children in their care

**Legal Authority**: Connecticut TFA Fact Sheet, Connecticut TANF State Plan

---

## Residency Requirement

**Connecticut Residency Required**:
- Must live in Connecticut to receive TFA
- No specific duration of residency requirement documented

**Legal Authority**: Connecticut TFA Fact Sheet

---

## Cooperation Requirements

### Child Support Cooperation

**Mandatory Cooperation**:
- Custodial parents must cooperate with child support enforcement
- Must provide information about non-custodial parent

**Good Cause Exception**:
- Exceptions granted for domestic violence cases
- Must demonstrate good cause for non-cooperation

**Legal Authority**: Connecticut TFA program documentation

### Work Program Participation

**Jobs First Employment Services**:
- Adult recipients able to work must participate in Jobs First Employment Services (JFES)
- Activities coordinated by Connecticut Department of Labor

**Exemptions**: Same as time limit exemptions (disability, age 60+, caring for young child, etc.)

**Legal Authority**:
- Connecticut TFA Fact Sheet
- Connecticut General Statutes § 17b-688c

### Employability Assessment

Per Connecticut General Statutes § 17b-689c:
- Assessment required for persons found eligible for time-limited assistance after July 1, 1998
- Assessment covers:
  - Education level
  - Employment and training history
  - Basic educational needs
  - Other social service needs

**Legal Authority**: Conn. Gen. Stat. § 17b-689c

---

## Special Eligibility Rules

### Student Income Disregard

Per Connecticut General Statutes § 17b-80:
- **Any earned income of a child who is a student** is disregarded in determining:
  - Eligibility for TFA
  - Standard of need
  - Amount of assistance

**Implementation**:
```python
if person.is_student and person.is_child:
    countable_earned_income_for_person = 0
```

**Legal Authority**: Conn. Gen. Stat. § 17b-80

### SSI Recipients

**SSI Not Counted**:
- Supplemental Security Income (SSI) not counted as income for TFA eligibility
- SSI recipients may also receive TFA if they meet other requirements

**Legal Authority**: Connecticut TFA documentation, SSA POMS

### Minor Parents

Minor parents may be ineligible under certain circumstances.

**Legal Authority**: Connecticut General Statutes § 17b-688g (specific provisions not fully documented in available sources)

---

## Eligibility Determination Process

### Application Investigation

Per Connecticut General Statutes § 17b-80:

**Initial Investigation**:
- Commissioner must promptly investigate within:
  - **45 days** for standard applications
  - **60 days** if disability determination required

**Ongoing Verification**:
- Commissioner makes periodic investigations to determine continuing eligibility
- May modify, suspend, or discontinue award based on changed circumstances

**Legal Authority**: Conn. Gen. Stat. § 17b-80

### Application Methods

**Online Application**:
- Primary method: www.connect.ct.gov
- Click "Apply Now" button

**Phone**:
- 1-855-626-6632 (1-855-CONNECT)

**In-Person**:
- Local DSS office

**Legal Authority**: Connecticut TFA Fact Sheet

---

## References for Implementation

### For Variable Definitions

```python
# Example eligibility variable structure
class ct_tfa_eligible(Variable):
    value_type = bool
    entity = TaxUnit  # Or appropriate entity
    label = "Eligible for Connecticut Temporary Family Assistance"
    definition_period = MONTH
    reference = [
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf",
        "https://www.cga.ct.gov/current/pub/chap_319s.htm",
    ]

    def formula(tax_unit, period, parameters):
        # Check demographic eligibility
        demographic_eligible = tax_unit("ct_tfa_demographic_eligible", period)

        # Check income eligibility
        income_eligible = tax_unit("ct_tfa_income_eligible", period)

        # Check asset eligibility
        assets_eligible = tax_unit("ct_tfa_assets_eligible", period)

        # Check time limit eligibility
        time_limit_eligible = tax_unit("ct_tfa_time_limit_eligible", period)

        return (
            demographic_eligible
            & income_eligible
            & assets_eligible
            & time_limit_eligible
        )
```

### Parameter Reference Format

```yaml
reference:
  - title: "Connecticut TANF State Plan 2024-2026, Section 4: Eligibility"
    href: "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf"
  - title: "Connecticut General Statutes § 17b-112"
    href: "https://www.cga.ct.gov/current/pub/chap_319s.htm"
  - title: "Connecticut TFA Fact Sheet - Eligibility Requirements"
    href: "https://portal.ct.gov/dss/knowledge-base/articles/fact-sheets-and-brochures-articles/fact-sheets-articles/tfa-fact-sheet"
```

---

**Document Status**: Complete and ready for implementation
**Last Updated**: October 14, 2025
