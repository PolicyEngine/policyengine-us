# Collected Documentation

## Louisiana FITAP (Family Independence Temporary Assistance Program) Implementation
**Collected**: 2026-01-04
**Implementation Task**: Implement Louisiana TANF program (FITAP)

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Family Independence Temporary Assistance Program
**Abbreviation**: FITAP
**Source**: LA RS 46:231.2 - "There is hereby created the Family Independence Temporary Assistance Program"

**Variable Prefix**: `la_tanf`

---

## Regulatory Authority

### Primary Sources

1. **Louisiana Revised Statutes Title 46**
   - RS 46:231 - Aid to needy families; definitions
   - RS 46:231.2 - Family Independence Temporary Assistance Program
   - RS 46:231.3 - FITAP benefits; prohibited uses
   - URL: https://www.legis.la.gov/legis/Law.aspx?d=100599

2. **Louisiana Administrative Code Title 67, Part III**
   - Subpart 5: Family Independence Temporary Assistance Program
   - Chapter 5: Eligibility Requirements
   - URL: https://www.doa.la.gov/media/tp3lmkyg/67.pdf

3. **Louisiana Department of Health FITAP Page**
   - URL: https://ldh.la.gov/page/fitap

4. **Louisiana DCFS FITAP Page**
   - URL: https://www.dcfs.louisiana.gov/page/fitap

5. **DCFS Benefit Increase Announcement (January 2022)**
   - URL: https://www.dcfs.louisiana.gov/news/louisiana-to-increase-tanf-cash-assistance-benefits-beginning-january-2022

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limits (CANNOT ENFORCE - requires history)
- **24-of-60 Month Limit**: Cannot receive benefits for more than 24 months within any 60-month period
- **60-Month Lifetime Limit**: Lifetime limit of 60 months if the assistance unit includes a parent/caretaker relative
- There are exceptions to both limits

### Time-Limited Deductions (APPLIED ALWAYS - cannot track months)
- **$900 Employment Deduction**: Time-limited deduction of $900 for six months for each employed member
- **Note**: This will be applied assuming the household qualifies since PolicyEngine cannot track employment duration

---

## Income Eligibility Test

### Single Income Test
Louisiana FITAP uses a unique income eligibility structure where **the income limit equals the flat grant amount** for the household size.

**Rule**: Monthly countable income, both earned and unearned, cannot exceed the flat grant amount for the number of persons in the assistance unit.

**Source**: Louisiana Department of Health FITAP page - "Monthly countable income, both earned and unearned, cannot exceed the flat grant amount for the number of persons in the assistance unit."

### Benefit Calculation
**Formula**: Benefit = Flat Grant Amount - Total Countable Income

**Source**: "Total countable income is subtracted from the flat grant amount to determine the client's grant amount."

---

## Income Deductions & Disregards

### Earned Income Deductions

| Deduction Type | Amount | Level | Notes |
|---------------|--------|-------|-------|
| Standard Earned Income Deduction | $120 | Per employed member | Always available |
| Time-Limited Employment Deduction | $900 | Per employed member | For 6 months (cannot track) |
| Dependent Care Deduction | Varies | Per employed member | Certain requirements must be met |

**Source**: Louisiana Department of Health FITAP page - "The allowable earned income deductions are: Standard earned income deduction of $120 for each employed member."

**Implementation approach:**
- [x] $120 standard deduction per employed member (will implement)
- [x] $900 time-limited deduction (will implement as always available with comment noting limitation)
- [ ] Dependent care deduction (specific amounts not found in documentation)

### Unearned Income
- Counted dollar-for-dollar (no disregards)
- Examples include: Child Support, alimony, unemployment benefits, Social Security benefits, SSI benefits, VA benefits, worker's compensation, pensions, contributions from friends/family

### Child Support Policy
**No pass-through or disregard**: Louisiana does NOT pass through child support to TANF families or disregard it when calculating benefits.

**Source**: NCSL Child Support Pass-Through and Disregard Policies - Louisiana shows "No" for both pass-through and disregard.

**Requirement**: Client must assign any child support and medical support rights to the state and must cooperate with the agency's Child Support Enforcement Services.

---

## Flat Grant Amounts (Payment Standards)

### Current Amounts (Effective January 2022)

| Household Size | Monthly Grant |
|----------------|---------------|
| 1 | $244 |
| 2 | $376 |
| 3 | $484 |
| 4 | $568 |
| 5 | $654 |
| 6 | $732 |
| 7 | $804 |
| 8 | $882 |
| 9 | $954 |

**Source**: Louisiana Department of Health FITAP page (https://ldh.la.gov/page/fitap) and DCFS Benefit Increase Announcement (January 2022)

**Note**: Benefits were doubled in January 2022 for the first time in over 20 years. The previous amounts were:
- 1: $122, 2: $188, 3: $240, 4: $284, 5: $327, 6: $366, 7: $402, 8: $441, 9: $477, 10: $512

### Minimum Payment
**LAC 67:III.1211** covers "Minimum Payments" - specific amount not confirmed in available sources but typically $10.

---

## Resource Limits

**All resources are EXCLUDED** when determining FITAP eligibility.

**Source**: Law Library of Louisiana FITAP Guide - "Resources are assets or possessions that a household can convert to cash to meet needs. All resources are excluded when determining eligibility."

**Implementation approach:**
- [x] No resource eligibility test needed for Louisiana FITAP

---

## Eligibility Criteria

### Age Requirements
- **Minor Child**: Under 18 years of age
- **Student Exception**: 18 years of age AND enrolled full-time in a secondary school or equivalent vocational/technical training, expected to complete before age 19
- **Unborn Children**: Not eligible for FITAP benefits
- **Pregnant Women**: May be certified if in the sixth month of pregnancy or beyond (with medical verification)

**Source**: LA RS 46:231 - "Dependent child" is defined as a needy child under the age of 18, or under age 19 if a full-time student in secondary school or equivalent vocational/technical training who may reasonably be expected to complete the program before age 19.

**Implementation approach:**
- [x] Use federal demographic eligibility (age thresholds match federal: 18/19)

### Citizenship/Immigration Eligibility
- Must be a U.S. citizen, non-citizen national, or qualified alien

**Source**: Louisiana Department of Health FITAP page

**Implementation approach:**
- [x] Use federal immigration eligibility (state follows federal rules)

### Residency
- Must be living in Louisiana
- Must intend to make a home in Louisiana (not temporary)

### Relationship Requirements
- Must be a qualified relative (related by blood, marriage, or adoption)
- Child must reside in the same home with the qualified relative
- Within fifth degree of relationship

### Minor Parent Requirements
- Unmarried parents under 18 and their children must reside with parent, legal guardian, or in adult-supervised setting

### Work Requirements (STEP Program)
- Work-eligible applicants and recipients are required to participate in the Strategies to Empower People (STEP) Program
- **Note**: Work requirements are not modeled in PolicyEngine - only eligibility and benefit calculation

### Child Support Cooperation
- Client must assign child support and medical support rights to the state
- Must cooperate with Child Support Enforcement Services

### Drug Screening
- Adults 18+ must cooperate with drug screening and testing if required

### Immunization
- Children under 18 must show sufficient evidence of immunity or immunization against vaccine-preventable diseases

---

## Benefit Calculation Formula

### Step-by-Step Calculation

1. **Determine Household Size** (assistance unit)
2. **Look up Flat Grant Amount** from payment standard table
3. **Calculate Gross Earned Income** for all employed members
4. **Apply Earned Income Deductions**:
   - Subtract $120 per employed member (standard deduction)
   - Subtract $900 per employed member (time-limited, if applicable)
   - Subtract allowable dependent care expenses
5. **Calculate Countable Earned Income** = Gross Earned - Deductions (minimum of $0)
6. **Calculate Total Countable Income** = Countable Earned + Unearned Income
7. **Determine Eligibility**: If Total Countable Income > Flat Grant Amount, NOT eligible
8. **Calculate Benefit**: Benefit = Flat Grant Amount - Total Countable Income

**Note**: Minimum benefit payment is typically $10 (LAC 67:III.1211)

---

## Implementation Notes

### Variables to Create

1. **Eligibility Variables**:
   - `la_tanf_eligible` - Overall TANF eligibility
   - `la_tanf_income_eligible` - Income eligibility check

2. **Income Variables**:
   - `la_tanf_countable_earned_income` - Earned income after deductions
   - `la_tanf_countable_income` - Total countable income
   - `la_tanf_earned_income_deduction` - Standard and time-limited deductions

3. **Benefit Variables**:
   - `la_tanf_flat_grant` - Flat grant amount by household size
   - `la_tanf` - Final benefit amount

### Parameters to Create

1. **Flat Grant Amounts**: `/parameters/gov/states/la/dcfs/tanf/flat_grant/amount.yaml`
   - Bracket-style by household size (1-9+)
   - Effective date: 2022-01-01 for current values
   - Historical values from 2000-07-01

2. **Earned Income Deductions**:
   - `/parameters/gov/states/la/dcfs/tanf/income/deductions/standard/amount.yaml` - $120
   - `/parameters/gov/states/la/dcfs/tanf/income/deductions/time_limited/amount.yaml` - $900

3. **Age Thresholds** (if not using federal):
   - Minor child: 18
   - Full-time student: 19

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Louisiana Administrative Code Title 67 (Full Text)**
   - URL: https://www.doa.la.gov/media/tp3lmkyg/67.pdf
   - Expected content: Complete regulatory text for FITAP including LAC 67:III.1211 (Minimum Payments), income determination rules, and detailed eligibility requirements

2. **Louisiana TANF State Plan**
   - URL: https://www.dcfs.louisiana.gov/assets/docs/searchable/EconomicStability/TANF/TANF%20State%20Plan%20Renewal%20for%20Louisiana2012.pdf
   - Expected content: State plan details, income calculation methodology, dependent care deduction specifics

3. **TANF Combined WIOA Plan**
   - URL: https://www.dcfs.louisiana.gov/assets/docs/searchable/EconomicStability/TANF/TANF_portion_combined_WIOAplan.pdf
   - Expected content: Updated state plan information

4. **2021 FITAP Brochure**
   - URL: https://www.dcfs.louisiana.gov/assets/docs/searchable/Publication_Library/Family_Support/2021_FITAP_Brochure.pdf
   - Expected content: Program overview and eligibility summary (pre-2022 benefit amounts)

5. **NCCP TANF Profile - Louisiana**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Louisiana.pdf
   - Expected content: Income limits, asset limits, benefit amounts, earned income disregards

---

## References for Metadata

### For Parameters:
```yaml
reference:
  - title: Louisiana Department of Health FITAP Page
    href: https://ldh.la.gov/page/fitap
  - title: Louisiana DCFS TANF Benefits Increase Announcement
    href: https://www.dcfs.louisiana.gov/news/louisiana-to-increase-tanf-cash-assistance-benefits-beginning-january-2022
```

### For Variables:
```python
reference = (
    "https://ldh.la.gov/page/fitap",
    "https://www.legis.la.gov/legis/Law.aspx?d=100599",
)
```

---

## Verification Checklist

- [x] Official program name discovered (FITAP)
- [x] Current benefit amounts by family size documented
- [x] Income eligibility test documented (income <= flat grant)
- [x] Earned income deductions documented ($120 + $900 time-limited)
- [x] Resource limit documented (all resources excluded)
- [x] Age requirements documented (under 18, or 18 if student completing before 19)
- [x] Child support passthrough policy documented (none)
- [x] Time limits documented (non-simulatable)
- [ ] Dependent care deduction amounts not fully specified in available sources
- [ ] LAC 67:III.1211 minimum payment amount not confirmed

---

## Key Differences from Other State TANF Programs

1. **No Resource Test**: Unlike many states, Louisiana excludes all resources from eligibility determination
2. **Income Limit = Benefit Amount**: The flat grant amount serves as both the income limit and the maximum benefit
3. **No Child Support Passthrough**: Louisiana does not pass through or disregard child support for FITAP families
4. **Time-Limited Deduction**: $900 for 6 months is unique to Louisiana
5. **2022 Benefit Doubling**: Benefits were doubled in January 2022 after 20+ years without increase
