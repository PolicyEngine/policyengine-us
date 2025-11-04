# Pennsylvania TANF Documentation Collection

**Collected**: 2025-11-03
**Implementation Task**: Pennsylvania TANF (Temporary Assistance for Needy Families) - Issue #6759
**State Agency**: Pennsylvania Department of Human Services (DHS)

---

## 1. PROGRAM OVERVIEW

### Official Name
Temporary Assistance for Needy Families (TANF) - Pennsylvania

### Authoritative Sources

#### State Regulations
- **Title**: Pennsylvania Code Title 55 (Human Services)
- **Citation**: 55 Pa. Code Chapters 105, 135, 153, 160, 175, 181, 183
- **URL**: https://www.pacodeandbulletin.gov/Display/pacode?titleNumber=055&file=/secure/pacode/data/055/055toc.html
- **Effective Date**: Various (ongoing updates)

#### Primary Policy Manual
- **Title**: Cash Assistance Handbook
- **Citation**: Office of Income Maintenance (OIM) Policy Manuals
- **URL**: http://services.dpw.state.pa.us/oimpolicymanuals/cash/index.htm
- **Note**: State services website experiences timeouts; alternative access through PA Code recommended

#### State Plan
- **Title**: Pennsylvania TANF State Plan 2024-2027
- **Citation**: Pennsylvania PYs 2024-2027
- **URL**: https://www.pa.gov/en/agencies/dhs/resources/cash-assistance/tanf/tanf-state-plan.html
- **Effective Date**: October 1, 2024

#### Federal Regulations (Context)
- **Title**: Code of Federal Regulations - TANF
- **Citation**: 45 CFR Parts 260-265
- **URL**: https://www.ecfr.gov/current/title-45/subtitle-B/chapter-II
- **Note**: 45 CFR 233 covers legacy AFDC; TANF is 45 CFR 260-265

---

## 2. CATEGORICAL ELIGIBILITY REQUIREMENTS

### Source Information
- **Title**: TANF Categorical Requirements
- **Citation**: 55 Pa. Code Chapter 105, § 105.2; Policy Manual Section 105.2
- **URL**: http://services.dpw.state.pa.us/oimpolicymanuals/cash/105_Category/105_2_TANF_Categorical_Requirements.htm

### Age Requirements

**Minor Child Definition**:
- Under age 18, OR
- Age 18 and a full-time student in secondary school or equivalent vocational/technical training

**Reference**:
```yaml
reference:
  - title: "105.2 TANF Categorical Requirements"
    href: "http://services.dpw.state.pa.us/oimpolicymanuals/cash/105_Category/105_2_TANF_Categorical_Requirements.htm"
```

### Pregnant Women
- Pregnant women with no other dependent children are eligible (Category C)
- Special requirements apply to unmarried pregnant women under age 18

### TANF Minor Parents
- **Definition**: TANF-eligible person under age 18 who has never married and who is pregnant or is the natural parent of a dependent child living with them
- **Living Arrangement Requirement**: Must live in home of minor parent's parent, legal guardian, or other adult relative, or in an adult-supervised supportive living arrangement (unless exempt)

### Budget Group Requirements
- Biological or adoptive parents and dependent full or half siblings of a TANF child must be included in the budget group

---

## 3. FINANCIAL ELIGIBILITY

### Resource Limits

**Source**:
- **Citation**: 55 Pa. Code Chapter 183; Policy Manual
- **URL**: Various sources confirm $1,000 limit

**Resource Limit**: $1,000 in countable resources

**Excluded Resources**:
- Primary residence (home)
- One vehicle per household (regardless of value)

**Reference**:
```yaml
reference:
  - title: "Pennsylvania TANF Resource Limits"
    href: "https://www.pa.gov/agencies/dhs/resources/cash-assistance/tanf"
```

### Income Eligibility Limits

**Source**:
- **Citation**: 55 Pa. Code Chapter 183, Appendix B, Table 3 (Family Size Allowance)
- **URL**: Referenced but table not directly accessible online
- **Note**: FSA relocated from Chapter 175 to Chapter 183, Appendix B, Table 3 per 20 Pa.B. 554 (February 3, 1990)

**Family Size Allowances (FSA) - Group 2 (Philadelphia County and most recipients)**:
- 1 person: $205/month
- 2 people: $316/month
- 3 people: $403/month
- 4 people: $497/month
- 5 people: $589/month
- 6 people: $670/month

**Geographic Variations**:
- Pennsylvania has four benefit schedules based on county
- Benefit amounts listed above are for Group 2 (includes Philadelphia County)
- Maximum benefit varies by county

**Eligibility Test**:
- Family is "needy" when countable income is less than the FSA plus any special needs allowances
- If countable income equals or exceeds FSA plus special needs, the budget group is ineligible

**Reference**:
```yaml
reference:
  - title: "55 Pa. Code Chapter 183, Appendix B, Table 3 - Family Size Allowances"
    href: "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"
  - title: "Pennsylvania TANF Profile 2024"
    href: "https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Pennsylvania.pdf"
```

---

## 4. INCOME DEFINITIONS AND COUNTING

### Source Information
- **Title**: Income Definitions and Treatment
- **Citation**: 55 Pa. Code §§ 183.2, 183.11, 183.21-183.37
- **URL**: https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html

### Earned Income
- Gross earned income from wages, tips, salary, commissions, and bonuses (§ 183.21)
- Profit from self-employment (§ 183.22)
- EITC excluded from income counting (§ 183.24)
- Lump sum earned income special treatment (§ 183.25)

### Unearned Income
- Benefits, dividends, and interest (§ 183.31)
- Child support (§ 183.32)
- Cash contributions (§ 183.33)
- Child income exemptions (§ 183.34)
- Deemed income from legally responsible relatives and parents of minor parents (§ 183.35)
- Nonrecurring unearned lump sums (§ 183.37)

### Income Exemptions
- **Citation**: 55 Pa. Code § 183.81
- 30 categories of income exemptions for TANF/GA

---

## 5. EARNED INCOME DEDUCTIONS AND DISREGARDS

### Source Information
- **Title**: TANF Earned Income Deductions
- **Citation**: 55 Pa. Code § 183.94; Policy Manual Section 160.2
- **URL**: https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/s183.94.html&d=reduce
- **Last Amendment**: September 13, 2002 (retroactive to March 3, 1997)

### Standard Deduction
**Amount**: $90 per month from gross earned income (first $90)

### Work Expense Deduction
**Amount**: $200 per month for all working TANF families with earned income
**Effective Date**: September 26, 2020 (earlier sources indicate March 28, 2009 for $50; increased to $200 in 2020)

**Reference**:
```yaml
reference:
  - title: "PA Changes in TANF Support Transition from Welfare to Work"
    href: "https://justharvest.org/pa-changes-tanf-support-transition-from-welfare-to-work/"
```

### 50% Earned Income Disregard

**Eligibility for Continuous 50% Disregard**:

1. **Recent Recipients**: Applicants who received TANF within the preceding 4 calendar months automatically qualify
2. **New Applicants**: Those without prior TANF receipt qualify if, after applying deductions ($90 standard + eligible personal care expenses + unearned income deductions), their income falls below the established need standard

**Ineligibility**:
- Individuals who terminated employment or reduced earned income without good cause within 30 days preceding the budget month
- Individuals who refused employment without good cause

**Citation**: 55 Pa. Code § 183.97 - Ineligibility for disregards from earned income

### Personal Care Expenses
For incapacitated adults living in the same home and receiving TANF:
- **Full-time employment**: Up to $175 per incapacitated adult per month
- **Part-time employment**: Up to $150 per incapacitated adult per month

**Condition**: Only if no other sound plan can be made for their care

---

## 6. BENEFIT CALCULATION FORMULA

### Calculation Steps

**Source**:
- **Citation**: 55 Pa. Code §§ 183.94, 183.101-183.108; Policy Manual Section 160.2
- **URL**: Multiple sections of Chapter 183

### Step-by-Step Calculation:

1. **Determine Gross Earned Income**
   - Include all wages, tips, salary, commissions, bonuses
   - Include self-employment profit

2. **Apply Standard Deduction**
   - Subtract $90 from gross earned income

3. **Apply Personal Care Expense Deduction (if applicable)**
   - Subtract up to $175/month per incapacitated adult (full-time work)
   - Or $150/month per incapacitated adult (part-time work)

4. **Apply 50% Earned Income Disregard**
   - Divide remaining earned income by 2
   - Only count 50% of earned income (if eligible for continuous disregard)

5. **Apply Work Expense Deduction**
   - Subtract $200 (for all working TANF families as of September 2020)

6. **Calculate Countable Earned Income**
   - Result after all deductions and disregards

7. **Add Countable Unearned Income**
   - Include unearned income after applicable deductions per § 183.98

8. **Total Countable Income**
   - Countable earned income + countable unearned income

9. **Compare to Family Size Allowance**
   - If total countable income ≥ FSA + special needs allowances → Ineligible
   - If total countable income < FSA + special needs allowances → Eligible

10. **Calculate Benefit Amount**
    - Benefit = FSA + special needs allowances - total countable income
    - Payment issued in two increments per month

### Example (from advocacy source):
**Family of 3, earned income $580/month (20 hours/week at minimum wage)**

Before September 2020 policy:
- Gross: $580
- Less $90 standard deduction: $490
- Apply 50% disregard: $490 ÷ 2 = $245 countable
- FSA for family of 3: $403
- Benefit: $403 - $245 = $158 (but source says $113, suggesting additional factors)

After September 2020 policy:
- Gross: $580
- Less $90 standard deduction: $490
- Apply 50% disregard: $490 ÷ 2 = $245
- Less $200 work expense: $245 - $200 = $45 countable
- FSA for family of 3: $403
- Benefit: $403 - $45 = $358 (but source says $313, suggesting additional factors)

**Note**: Exact calculation may include additional factors not shown in simplified example

### Budgeting Methods
- **Citation**: 55 Pa. Code §§ 183.101, 183.61-183.65
- **Prospective Budgeting**: Eligibility based on estimates of future income
- **Retrospective Budgeting**: Assistance based on actual income from previous "budget month"
- Income averaging procedures for irregular income (§ 183.64)

---

## 7. SPECIAL PROVISIONS AND DEDUCTIONS

### Child Support Treatment

**Source**:
- **Title**: Child Support Pass-Through and Disregard
- **Citation**: 55 Pa. Code § 183.32; Historical references to Act 1996-35
- **URL**: https://www.ncsl.org/human-services/child-support-pass-through-and-disregard-policies-for-public-assistance-recipients

**Historical**: First $50 per budget month of court-ordered or voluntary current support payments was disregarded

**Current**: Pennsylvania has elected DRA (Deficit Reduction Act) distribution and participates in pass-through and disregard policies, though specific current dollar amounts not clearly documented in available sources

### Child Care Allowances

**Source**:
- **Citation**: Policy Manual Section 183.2 (Child Care Eligibility Requirements)
- **URL**: http://services.dpw.state.pa.us/oimpolicymanuals/cash/183_Child_Care/183_2_Eligibility_Requirements.htm

**Eligibility**:
- TANF budget group must include individual participating in approved work-related activity
- Must include TANF dependent child or child who would qualify except for SSI or Foster Care receipt
- Employed TANF recipients eligible beginning first day of employment
- Must pay required co-payment determined by Early Learning Resource Center (ELRC)

### Diversion Program

**Source**:
- **Title**: Diversion Program
- **URL**: https://www.pa.gov/agencies/dhs/resources/cash-assistance/diversion-program

**Payment Amount**: Equal to 1, 2, or maximum of 3 months of FSA, depending on family's need

**Purpose**: One-time lump sum payment as alternative to ongoing TANF assistance

---

## 8. WORK REQUIREMENTS AND TIME LIMITS

### Time Limits

**Source**:
- **Citation**: Policy Manual Section 105.2
- **URL**: http://services.dpw.state.pa.us/oimpolicymanuals/cash/105_Category/105_2_TANF_Categorical_Requirements.htm

**Lifetime Limit**: 60 months (5 years) total

**Who It Counts For**:
- Adult head-of-household or spouse of head-of-household (age 18+)
- Pregnant minor head-of-household
- Minor parent head-of-household
- Minor married to head-of-household

**Does Not Count**: Assistance received as a minor (under 18) when not head-of-household or spouse

### Work Requirements

**Source**:
- **Title**: Employment and Training Requirements
- **Citation**: Policy Manual Sections 135.2, 135.8
- **URL**: http://services.dpw.state.pa.us/oimpolicymanuals/cash/135_Employment_and_Training_Requirements/

**First 24 Months**: No specific hour requirement for work activities

**After 24 Months**: Must participate in work activity at least 20 hours/week

**General Requirement**: 30 hours/week in combined work and work-related activities (with good cause exemptions)

### Extended TANF
For recipients who reach 60-month limit:
- Adults employed 20-29 hours/week must enroll in Employment & Training (E&T) program
- Combined work and work-related activities must average at least 30 hours/week

### Work Activity Limits
- Maximum 12 weeks in rolling 12-month period for job search/job readiness and rehabilitative services to count as core activity

### Exemptions from Work Requirements
**Source**: https://justharvest.org/get-help/welfare-client-resources/exemptions-from-work-requirements/

Good cause provisions may exempt individuals from work participation requirements

---

## 9. INCOME DETERMINATION METHODOLOGY

### Source Information
- **Citation**: 55 Pa. Code §§ 183.61-183.65, 183.101-183.108

### Methods for Determining Monthly Income

**Actual Income Method** (§ 183.61):
- Income actually received in budget month

**Anticipated Income Method** (§ 183.62):
- Income expected to be received

**Contractual Income Method** (§ 183.63):
- Income amount specified in contract or agreement

**Income Averaging** (§ 183.64):
- For irregular income, average over appropriate period

**Self-Employment Profit** (§ 183.65):
- Special determination for business income

### Budget Group Changes
- **Citation**: §§ 183.103-183.108
- Additions to budget group (§ 183.103)
- Payment calculations when composition changes

---

## 10. PAYMENT ISSUANCE

### Payment Schedule
**Frequency**: Monthly, issued in two increments
- Example: Family of 3 receiving $403/month receives two payments of $201.50

**Reference**:
```yaml
reference:
  - title: "Pennsylvania TANF Profile"
    href: "https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Pennsylvania.pdf"
```

---

## 11. REFERENCES FOR PARAMETER METADATA

### For Pennsylvania TANF Maximum Benefit (Family Size Allowance)
```yaml
reference:
  - title: "55 Pa. Code Chapter 183, Appendix B, Table 3"
    href: "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"
  - title: "Pennsylvania TANF Information"
    href: "https://www.pa.gov/agencies/dhs/resources/cash-assistance/tanf"
```

### For Earned Income Deductions
```yaml
reference:
  - title: "55 Pa. Code § 183.94 - Eligibility for TANF earned income deductions"
    href: "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/s183.94.html&d=reduce"
  - title: "160.2 TANF Earned Income Deductions (Policy Manual)"
    href: "http://services.dpw.state.pa.us/oimpolicymanuals/cash/160_Income_Deductions/160_2_TANF_Earned_Income_Deductions.htm"
```

### For Work Expense Deduction ($200)
```yaml
reference:
  - title: "PA Changes in TANF Support Transition from Welfare to Work (September 2020)"
    href: "https://justharvest.org/pa-changes-tanf-support-transition-from-welfare-to-work/"
```

### For Categorical Eligibility
```yaml
reference:
  - title: "105.2 TANF Categorical Requirements"
    href: "http://services.dpw.state.pa.us/oimpolicymanuals/cash/105_Category/105_2_TANF_Categorical_Requirements.htm"
```

---

## 12. IMPLEMENTATION NOTES

### Known Gaps in Documentation

1. **Complete FSA Table**: 55 Pa. Code Chapter 183, Appendix B, Table 3 is referenced but not directly accessible online. Family sizes beyond 6 people need verification.

2. **County Benefit Schedule Groups**: Four benefit schedules exist, but only Group 2 amounts are well-documented. Need to identify:
   - Which counties belong to each group
   - Benefit amounts for Groups 1, 3, and 4

3. **Current Child Support Pass-Through Amount**: Historical $50 disregard is documented, but current policy under DRA distribution needs verification

4. **Specific Work Activity Definitions**: General requirements documented, but detailed list of qualifying work activities needs extraction

5. **Special Needs Allowances**: References exist to special needs allowances added to FSA, but specific amounts and qualifying circumstances need documentation

### PDFs Requiring Manual Extraction

1. **Pennsylvania TANF Profile (NCCP)**: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Pennsylvania.pdf
   - PDF appears corrupted in web fetch
   - May contain updated 2024 benefit amounts and policy details

2. **CLS Philadelphia TANF Fact Sheet**: https://clsphila.org/wp-content/uploads/2019/04/YJP-factsheet-TANF_1.pdf
   - PDF not readable via web fetch
   - Likely contains detailed examples and calculations

3. **50-State TANF Comparison**: https://www.nccp.org/wp-content/uploads/2024/11/TANF-Benefit-Amounts-2024-FINAL.pdf
   - Should contain Pennsylvania benefit amounts in comparison table
   - Not successfully extracted

### Alternative Access Methods

Since `services.dpw.state.pa.us` experiences frequent timeouts:
- Use Pennsylvania Code and Bulletin website (pacodeandbulletin.gov) as primary source
- Reference policy manual sections by section number for documentation
- Contact Pennsylvania DHS directly for current benefit tables

### Federal Context

TANF replaced AFDC (Aid to Families with Dependent Children) in 1996 under Personal Responsibility and Work Opportunity Reconciliation Act (PRWORA). Federal regulations are in 45 CFR Parts 260-265, not 45 CFR 233 (which covers legacy AFDC).

---

## 13. SUMMARY OF KEY IMPLEMENTATION VALUES

### For Immediate Use in Code

| Parameter | Value | Source |
|-----------|-------|--------|
| Resource Limit | $1,000 | PA Code, DHS website |
| Vehicle Exemption | 1 vehicle (unlimited value) | PA Policy |
| FSA - 1 person | $205/month | Group 2 schedule |
| FSA - 2 people | $316/month | Group 2 schedule |
| FSA - 3 people | $403/month | Group 2 schedule |
| FSA - 4 people | $497/month | Group 2 schedule |
| FSA - 5 people | $589/month | Group 2 schedule |
| FSA - 6 people | $670/month | Group 2 schedule |
| Standard Deduction | $90/month | 55 Pa. Code § 183.94 |
| Work Expense Deduction | $200/month | Policy change Sept 2020 |
| Earned Income Disregard | 50% | 55 Pa. Code § 183.94 |
| Dependent Care (Full-time) | $175/month max per person | 55 Pa. Code § 183.94 |
| Dependent Care (Part-time) | $150/month max per person | 55 Pa. Code § 183.94 |
| Minor Child Age Limit | Under 18, or 18 if full-time student | 55 Pa. Code § 105.2 |
| Lifetime Time Limit | 60 months | Policy Manual 105.2 |
| Work Hours (after 24 mo) | 20 hours/week minimum | Policy Manual 135.8 |

---

**Document Collection Complete**: 2025-11-03
**Next Steps**:
1. Manually extract PDFs listed above
2. Verify county benefit schedule assignments
3. Confirm current child support pass-through amount
4. Extract complete FSA table for all family sizes
