# Collected Documentation

## Mississippi TANF Implementation
**Collected**: 2025-12-18
**Implementation Task**: Document Mississippi's Temporary Assistance for Needy Families (TANF) program for PolicyEngine implementation

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Mississippi Temporary Assistance for Needy Families (TANF)
**Abbreviation**: TANF
**Agency**: Mississippi Department of Human Services (MDHS)
**Source**: Mississippi Code Section 43-17-1

**Variable Prefix**: `ms_tanf`

---

## Legal Authority

### Primary Statute
- **Mississippi Code Title 43, Chapter 17**
  - Section 43-17-1: Program establishment
  - Section 43-17-5: Amount of assistance (payment standards)
  - URL: https://law.justia.com/codes/mississippi/title-43/chapter-17/

### Administrative Regulations
- **Mississippi Administrative Code Title 18, Part 19**
  - Division of Economic Assistance TANF State Plan
  - URL: https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19

---

## Income Eligibility

### Definition of "Needy Family"
A needy family is defined as a family with dependent child(ren) and an **average annual income at or below 185 percent of the need standard**.

**Source**: Miss. Code. tit. 18, pt. 19 - https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19

### Gross Income Limits by Household Size
The gross monthly income limits (185% of need standard) are:

| Household Size | Maximum Monthly Gross Income |
|----------------|------------------------------|
| 1 | $627 |
| 2 | $851 |
| 3 | $1,074 |
| 4 | $1,298 |
| 5 | $1,522 |
| 6 | $1,746 |
| 7 | $1,970 |
| 8 | $2,194 |
| 9 | $2,417 |
| 10 | $2,641 |

**Source**: Mississippi Department of Human Services - https://www.mdhs.ms.gov/help/tanf/applying-for-tanf/

### Need Standard (Calculated)
The Need Standard can be derived by dividing the gross income limits by 1.85:

| Household Size | Need Standard (Monthly) |
|----------------|-------------------------|
| 1 | $339 |
| 2 | $460 |
| 3 | $581 |
| 4 | $702 |
| 5 | $823 |
| 6 | $944 |
| 7 | $1,065 |
| 8 | $1,186 |
| 9 | $1,307 |
| 10 | $1,428 |

**Note**: For households larger than 10, add $75 to the requirements for each person above 10 and compute 185 percent of that figure, rounding down to the nearest dollar.

**Source**: Miss. Code. tit. 18, pt. 19 - https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19

### Income Limit Calculation
```
Gross Income Limit = Need Standard x 1.85
```
**Implementation approach:**
- [x] Store the need standard amounts by household size
- [x] Store the 185% multiplier as a rate parameter (1.85)

---

## Payment Standards (Maximum Benefit Amounts)

### Statutory Payment Formula
Per Mississippi Code Section 43-17-5(1):
- **First person**: $200 per month
- **Second person**: $36 per month
- **Each additional person**: $24 per month

**Source**: Mississippi Code 1972 Annotated at 43-17-5(1) - https://law.justia.com/codes/mississippi/title-43/chapter-17/section-43-17-5/

### Maximum Monthly Benefit by Household Size

| Household Size | Calculation | Maximum Monthly Benefit |
|----------------|-------------|-------------------------|
| 1 | $200 | $200 |
| 2 | $200 + $36 | $236 |
| 3 | $200 + $36 + $24 | $260 |
| 4 | $200 + $36 + $24 + $24 | $284 |
| 5 | $200 + $36 + $24 + $24 + $24 | $308 |
| 6 | $200 + $36 + $24 + $24 + $24 + $24 | $332 |
| 7 | $200 + $36 + $24 + $24 + $24 + $24 + $24 | $356 |
| 8 | $200 + $36 + $24 + $24 + $24 + $24 + $24 + $24 | $380 |
| 9 | $200 + $36 + $24 + $24 + $24 + $24 + $24 + $24 + $24 | $404 |
| 10 | $200 + $36 + $24 + $24 + $24 + $24 + $24 + $24 + $24 + $24 | $428 |

**Implementation approach:**
- [x] Store first person amount ($200)
- [x] Store second person amount ($36)
- [x] Store each additional person amount ($24)
- [x] Calculate benefit using formula: first + second + (additional * (size - 2))

---

## Resource Limits

### Resource Limit Amount
**$2,000** for all TANF households

**Effective Date**: July 1, 2019

**Exclusions**:
- Personal home (primary residence)
- Personal vehicle

**Source**: Mississippi Department of Human Services - https://www.mdhs.ms.gov/help/tanf/

### Hope Act Changes
In 2017, the Mississippi Legislature passed House Bill 1090, "The Medicaid and Human Services Transparency and Fraud Prevention Act" (Hope Act). Under the Hope Act:
- Broad-Based Categorical Eligibility (BBCE) status is no longer permitted for most TANF households
- Effective July 1, 2019, all families applying for TANF are subject to evaluation of all household resources

**Source**: Miss. Code. tit. 18, pt. 19 - https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19

---

## Earned Income Disregards

### Six-Month Total Earned Income Disregard
TANF recipients who find full-time employment may have their earned income **totally disregarded** for up to six (6) months.

**Requirements:**
- Employment of **35 or more hours per week**
- Earnings at or above the **federal minimum wage**
- Must claim within 30 days of new approval or job start date

**Source**: Miss. Code. tit. 18, pt. 19 - https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19

### Three-Month Total Earned Income Disregard
Available when TANF case is subject to closure due to increased earnings.

**Requirements:**
- Employment of **at least 25 hours per week**
- Earnings at or above the **federal minimum wage**
- Cannot be combined with six-month disregard
- Can be claimed again after 12-month consecutive break in assistance

**Source**: Miss. Code. tit. 18, pt. 19 - https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19

### Marriage Disregard
When a TANF recipient marries, the **new spouse's income and resources are disregarded for six months**.

**Purpose**: Allows single parents who marry employed persons to continue receiving TANF benefits without immediately losing assistance.

**Source**: Miss. Code. tit. 18, pt. 19 - https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19

---

## Non-Financial Eligibility Requirements

### Household Composition
- Must have at least one **child under 18 years of age** living in the home
- Child must be deprived of parental support due to:
  - Incapacity of a parent
  - Death of a parent
  - Continued absence of a parent
  - Unemployment of principal wage earner (two-parent families only)

### Two-Parent Families
Two-parent families are eligible only if the principal wage earner:
- Is designated as "unemployed"
- Has not worked full-time for at least 30 days prior to receipt of TANF benefits

### Citizenship/Immigration Status
- Must be a U.S. citizen or legal permanent resident
- Lawful permanent residents are only potentially eligible if they can be credited with 40 quarters of work (approximately 10 years)

### School Attendance and Immunizations
- Children under age 7 must comply with immunization requirements
- Children ages 6 to 17 must attend school with satisfactory attendance
- Children age 18 in the Assistance Unit (full-time students) must have satisfactory school attendance
- **Sanction**: 25% monthly benefit reduction for non-compliance without good cause

**Source**: Mississippi Code 43-17-5 and Miss. Code. tit. 18, pt. 19

---

## Family Benefit Cap

Mississippi imposes a **family benefit cap** to prevent increases in assistance for new children coming into the family after the initial **ten (10) months of benefits**.

**Exceptions apply** as defined in state law.

**Source**: Miss. Code. tit. 18, pt. 19 - https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19

---

## Benefit Calculation

### Formula
```
Benefit = Maximum Payment Standard - Countable Income
```

If countable income exceeds the payment standard, benefit = $0

### Determining Countable Income
**Note**: Mississippi's specific earned income disregard calculation (beyond the 6-month and 3-month total disregards) was not found in available HTML sources. The TANF Manual may contain additional details.

Based on the total disregard structure:
- During disregard periods (6-month or 3-month), earned income is fully excluded
- Outside disregard periods, standard TANF income counting rules apply

---

## Non-Simulatable Rules (Architecture Limitations)

### Cannot Be Simulated - Requires Historical Tracking

**Time Limit**: 60-month lifetime limit on TANF benefits
- The Department of Human Services shall deny TANF benefits to families which include an adult who has received TANF assistance for sixty (60) months, whether consecutive or not
- **CANNOT ENFORCE - requires benefit history tracking**

**Earned Income Disregard Periods**:
- 6-month total disregard requires tracking employment start date and duration
- 3-month total disregard requires tracking when case would close due to earnings
- **CANNOT TRACK - requires employment history**

**Marriage Disregard**:
- 6-month disregard of new spouse's income requires tracking marriage date
- **CANNOT TRACK - requires marital history**

**Family Benefit Cap**:
- Requires tracking which children were born after 10 months of initial benefits
- **CANNOT ENFORCE - requires benefit and birth history**

**Work Requirements**:
- Required after 24 months of assistance or when deemed work-ready
- Progressive sanctions for non-compliance
- **CANNOT ENFORCE - requires participation history**

### Partially Simulatable
- **Earned Income Disregards**: Can implement assuming household qualifies, but cannot track time limits

### Can Be Simulated
- [x] Current gross income eligibility test
- [x] Current resource eligibility test
- [x] Current benefit calculation (payment standard - countable income)
- [x] Current household composition requirements
- [x] Demographic eligibility (age of children)

---

## Implementation Notes

### Variables to Create
1. `ms_tanf` - Main benefit calculation variable
2. `ms_tanf_eligible` - Overall eligibility determination
3. `ms_tanf_income_eligible` - Gross income test (185% of need standard)
4. `ms_tanf_resources_eligible` - Resource limit test ($2,000)
5. `ms_tanf_maximum_benefit` - Payment standard by household size
6. `ms_tanf_countable_income` - Countable income for benefit calculation

### Parameters to Create
1. `need_standard/amount.yaml` - Need standard by household size
2. `income/gross_income_limit_rate.yaml` - 185% multiplier
3. `payment_standard/first_person.yaml` - $200
4. `payment_standard/second_person.yaml` - $36
5. `payment_standard/additional_person.yaml` - $24
6. `resources/limit.yaml` - $2,000 resource limit

### Demographic Eligibility
**Implementation approach:**
- [x] Use federal demographic eligibility (minor child under 18)
- [ ] May need state-specific rules for two-parent unemployment definition

### Immigration Eligibility
**Implementation approach:**
- [ ] Use federal immigration eligibility baseline
- [ ] Note: 40 quarters work requirement for LPRs (cannot track)

---

## References for Metadata

### For Parameters
```yaml
reference:
  - title: "Mississippi Code Section 43-17-5(1)"
    href: "https://law.justia.com/codes/mississippi/title-43/chapter-17/section-43-17-5/"
  - title: "Miss. Code. tit. 18, pt. 19 - TANF State Plan"
    href: "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19"
```

### For Variables
```python
reference = (
    "https://law.justia.com/codes/mississippi/title-43/chapter-17/section-43-17-5/",
    "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19",
)
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Mississippi TANF Policy Manual (Volume III)**
   - URL: https://www.mdhs.ms.gov/wp-content/uploads/2019/07/TANF-Manual-Revised_7.19.pdf
   - Expected content: Detailed eligibility procedures, income calculation methodology, deduction amounts
   - Key sections: Chapter 2 (Definitions), Section 4105 (Earned Income Disregards)

2. **NCCP TANF Profile - Mississippi**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Mississippi-.pdf
   - Expected content: Summary of Mississippi TANF policies, comparison data

3. **Mississippi TANF Eligibility Flyer**
   - URL: https://www.mdhs.ms.gov/wp-content/uploads/2018/02/MDHS_TANF-Eligibility-Flyer.pdf
   - Expected content: Quick reference for eligibility requirements

4. **SPLC Mississippi TANF Recommendations**
   - URL: https://www.splcenter.org/wp-content/uploads/files/policy-mississippi-tanf-recommendations.pdf
   - Expected content: Policy analysis and recommendations

5. **CBPP Mississippi TANF Spending Report**
   - URL: https://www.cbpp.org/sites/default/files/atoms/files/tanf_spending_ms.pdf
   - Expected content: TANF spending data and analysis

6. **ACF Graphical Overview of State TANF Policies (July 2023)**
   - URL: https://acf.gov/sites/default/files/documents/opre/opre-graphical-overview-tanf-policies-dec2024.pdf
   - Expected content: Comparative state TANF policy data

---

## Sources

### Primary Sources
- [Mississippi Department of Human Services - TANF](https://www.mdhs.ms.gov/help/tanf/)
- [Mississippi Department of Human Services - Applying for TANF](https://www.mdhs.ms.gov/help/tanf/applying-for-tanf/)
- [Mississippi Administrative Code Title 18, Part 19](https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19)
- [Mississippi Administrative Code Title 18, Part 19 (Effective 4/14/2025)](https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19_v2)
- [Mississippi Code Section 43-17-1](https://law.justia.com/codes/mississippi/title-43/chapter-17/section-43-17-1/)
- [Mississippi Code Section 43-17-5](https://law.justia.com/codes/mississippi/title-43/chapter-17/section-43-17-5/)

### Legislative Bills (for context on proposed changes)
- [HB 582 (2024) - TANF Program Changes](https://billstatus.ls.state.ms.us/documents/2024/html/HB/0500-0599/HB0582IN.htm)
- [HB 715 (2024)](https://billstatus.ls.state.ms.us/documents/2024/html/HB/0700-0799/HB0715IN.htm)
- [SB 2723 (2025)](https://billstatus.ls.state.ms.us/documents/2025/html/SB/2700-2799/SB2723IN.htm)

### Comparative Resources
- [Urban Institute Welfare Rules Database](https://wrd.urban.org/policy-tables)
- [ACF TANF Resources](https://acf.gov/ofa/programs/temporary-assistance-needy-families-tanf)
