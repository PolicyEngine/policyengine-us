# Collected Documentation

## Nevada TANF - Implementation Reference
**Collected**: 2025-12-10
**Implementation Task**: Implement Nevada Temporary Assistance for Needy Families (TANF) program

---

## Program Overview

Nevada's TANF program is administered by the Division of Welfare and Supportive Services (DWSS), now known as the Division of Social Services (DSS). The program provides temporary assistance for the care of dependent children in their own homes or the homes of relative caregivers.

### Source Information
- **Agency**: Nevada Division of Social Services (DSS) (formerly DWSS)
- **Website**: https://dss.nv.gov
- **Program Effective Date**: January 1, 1997 (TANF implementation)
- **Statutory Authority**: NRS Chapter 422A - Welfare and Supportive Services

---

## Program Types

Nevada operates five TANF benefit categories:

### 1. TANF-NEON (New Employees of Nevada)
- Cash assistance for families with work-eligible adults
- Subject to work participation requirements
- Subject to state and federal time limits
- Source: https://dss.nv.gov/TANF/Financial_Help/

### 2. TANF Child-Only
- Cash assistance for households lacking work-eligible adults
- NOT subject to time limits
- For children living with relative caregivers
- Source: https://www.fosterkinship.org/kinship-resources/child-only-tanf/

### 3. Self-Sufficiency Grant (SSG)
- One-time lump sum payment
- Recipients ineligible for other TANF for period calculated by dividing benefit amount by maximum family benefit

### 4. Temporary (TEMP) Program
- Monthly payments limited to no more than four months per episode
- For unforeseen circumstances

### 5. TANF Loan
- Monthly payments when adult has anticipated future income
- Benefits must be repaid

---

## Income Eligibility

### Income Tests

Nevada uses multiple income tests for TANF eligibility:

#### 1. Gross Income Test: 130% of Federal Poverty Level
- **Threshold**: Gross income must be less than 130% FPL
- **Example**: For family of 3, gross income limit is approximately $2,693/month (2024)
- **Application**: Initial screening for TANF-NEON
- **Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/

#### 2. 100% Need Standard Test
- **Purpose**: Determines if earned income disregards can be applied
- **Application**: Applied after passing 130% FPL test
- **Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/

#### 3. 75% Need Standard Test (Initial Eligibility)
- **Threshold**: 75% of state Need Standard
- **Example**: ~$1,666/month for family of 3
- **Application**: Initial three months eligibility
- **Note**: This implies 100% Need Standard is ~$2,222 for family of 3
- **Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/

#### 4. Child-Only Income Test: 275% of Federal Poverty Level
- **Threshold**: Household income must be at or below 275% FPL
- **Application**: TANF Child-Only (Non-Needy Relative Caregiver) cases only
- **Note**: Once household qualifies, only child's income/resources are counted
- **Source**: https://www.first5nevada.org/services/parenting-and-family-support/temporary-assistance-for-needy-families-tanf-child-only/

### Need Standard

**Definition**: The Need Standard represents basic needs of TANF families - a figure predetermined by the State of Nevada according to the number of persons in the assistance household group. It includes:
- Food
- Clothing
- Housing/Shelter
- Utilities (heating, cooking, water heating, refrigeration, lights)
- Household supplies
- Medical chest supplies
- Recreation
- Personal incidentals

**Example Values (Family of 3)**:
- 100% Need Standard: ~$2,222/month
- 75% Need Standard: ~$1,666/month

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/

---

## Benefit Calculation

### Payment Standard (Maximum Benefit Amounts)

**Known Values**:
- Family of 3 (no income): Up to $386/month
- Child-Only (1 child): $417/month payment allowance

**Calculation Method**:
- Maximum payment issued when there is no countable income
- Benefit reduction is dollar-for-dollar against countable income
- Payment Standard = Maximum Grant Amount (varies by household size)

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/

**Note**: Nevada has one of the lowest TANF benefit amounts in the country. Benefits have not been increased for over a decade. Nevada ranks 37th among all states.

---

## Earned Income Disregards

### Graduated Disregard Schedule

Nevada applies a time-limited graduated disregard to earned income:

| Period | Disregard Rate |
|--------|---------------|
| Months 1-3 | 100% |
| Months 4-6 | 85% |
| Months 7-9 | 75% |
| Months 10-12 | 65% |

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-1/

### Warning: Non-Simulatable Time-Limited Disregards
These graduated disregards are tracked individually by wage earner and require employment history tracking. PolicyEngine cannot simulate the time-based progression of disregards due to single-period architecture.

**Implementation approach**: Apply a single disregard rate (likely the initial 100% or a conservative estimate like 65%) with documentation noting the limitation.

### Standard Work Expense Deduction

After earned income disregards are exhausted:
- **Deduction**: Greater of $90 OR 20% of gross earnings
- **Application**: Applied to gross earnings
- **Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-1/

### Exception for Low Earnings
If wage earner's income is $90 or less:
- Standard work expense deduction ($90) is allowed
- 100% earned income disregard is NOT applied
- Once earnings exceed $90, the 100% disregard applies if eligible

### Disregard Renewal
- New set of earned income disregards begins when:
  - Individual is off cash benefits for 12 consecutive months
  - Individual meets both income tests
- Disregards do NOT continue where they left off

### Disregard Tracking
- Disregards are applied and tracked separately for each individual wage earner
- Persons who lose a job and obtain another continue with disregards where they left off
- Those who leave assistance for more than one month must pass 130% FPL test upon reapplication

---

## Child Care Deduction

After applying earned income disregards and work expenses:
- **Deduction**: Actual amount of child care expenses paid or anticipated to be paid
- **Application**: Subtracted to arrive at net earned income
- **Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-1/

---

## Stepparent Income Budgeting

When a natural parent applies for TANF while married to a stepparent:

### Deductions from Stepparent Gross Income:
1. **Standard Work Expense**: $90 or 20% of gross earnings (whichever is greater)
2. **Need Standard Deduction**: 100% need standard for stepparent plus any other persons not in TANF household claimed as dependents
3. **Support Payments**: Amounts paid to persons not living in the home claimed as dependents, plus alimony and child support

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-4/

---

## Resource Limits

### Countable Resource Limit
- **Limit**: $10,000 per TANF household
- **Effective Date**: July 1, 2014
- **Consequence**: If resources exceed limit, application denied or case terminated

### Excluded Resources (NOT counted):
- Two vehicles per household
- Home (including contiguous land) - usual residence owned or being purchased
- One burial plot per household member
- One bona fide funeral agreement per TANF assistance unit member
- Household goods and personal items

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-R/S/

---

## Time Limits

### Warning: Non-Simulatable Time Limits
Time limits require tracking benefit history across periods. PolicyEngine cannot enforce time limits due to single-period architecture.

### State Cycle Limit: 24 Months On / 12 Months Off
- Households may receive 24 months of cash assistance
- After exhausting this period: 12 consecutive months ineligibility
- 24-month period need not be consecutive
- 12-month sit-out period MUST be consecutive
- Exception: Qualifying hardship

### Extension Provision
District Office Managers may grant a 6-month extension beyond the 24-month limit if recipient will achieve self-sufficiency with additional time.

### Federal Lifetime Limit: 60 Months
- Adults who received TANF cash assistance from Nevada or any other state for 60 months (cumulative) are prohibited from receiving TANF-NEON and/or Loan benefits
- Exception: Qualifying hardship
- Child-Only TANF: NOT subject to time limits

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-S/T/

---

## Age Requirements

### Children
- **Under 18**: Eligible
- **Age 18 in School**: Eligible through graduation month if:
  - Enrolled full-time in high school, technical/vocational, or GED program
  - Expected to graduate before or in month of 19th birthday
- **Age 18+ NOT in School**: Ineligible

### Post-19th Birthday Rule
A minor who will not complete GED or high school until after turning 19 loses eligibility the month following their 18th birthday.

### Minor Parents
Must be enrolled and attending high school or actively participating in GED program with adequate progress.

### School Attendance Requirements
Head of household must ensure children ages 7-12 attend school as required by state law.

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-A/

---

## Citizenship and Immigration Requirements

### Basic Requirement
Must be a U.S. citizen or lawful permanent resident

### Social Security Number
Each TANF household member must provide or apply for SSN unless religious beliefs prohibit enumeration. Non-qualified non-citizens are not required to provide SSN.

### Federal Immigration Framework
- Qualified immigrants include: LPRs, refugees, asylees, persons granted withholding of deportation, Cuban/Haitian entrants, battered spouses/children with pending immigration petitions
- Subject to federal 5-year bar provisions
- Sponsor deeming rules may apply

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-F/I/

---

## Residency Requirements

Applicants must be:
- Living in Nevada with intention of making it their home permanently or for indefinite period
- OR entering Nevada with a job commitment or seeking employment

**Source**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-R/S/

---

## Work Requirements

### TANF-NEON Work Participation

**Single-Parent Households**:
- Minimum 30 hours/week
- Reduced to 20 hours/week if youngest child under age 6

**Two-Parent Households**:
- Minimum 55 hours/week combined
- Reduced to 35 hours/week combined if youngest child under age 6

### Exemptions
- Single parents with children under 1 year: May be exempt for up to 3 months per child (max 12 months lifetime)
- Parents caring for ill/incapacitated family members may qualify for exemptions
- Exempt parents can voluntarily participate

**Note**: Work requirements are NOT simulated in PolicyEngine - only eligibility and benefit calculation.

**Source**: https://nevadalawhelp.org/resource/temporary-assistance-for-needy-families-tanf

---

## Child Support Enforcement

### Cooperation Requirement
Cooperation with Child Support Enforcement is mandatory for all TANF cases, including:
- Surrendering support payments to the state
- Providing information to locate absent parent

### Income Treatment
- Current child support obligations: Counted as unearned income
- Child support arrearages: Counted as unearned income
- Penalties and interest on child support: Excluded

### Child Support Passthrough
**Note**: Detailed information about child support passthrough amount (portion passed to family vs. retained by state) was not found in web sources. This may be in the State Plan PDF.

---

## Unearned Income

### Sources Counted as Unearned Income:
- Social Security benefits
- Unemployment benefits
- Child support payments received
- Spousal support (only when current support being paid)
- Pensions
- Disabled veterans payments
- Survivors of deceased disabled veterans payments
- Third-party payments for household expenses (when legally obligated)

### Exempt/Excluded Unearned Income:
- AmeriCorps State and National monthly living stipends
- VISTA payments (if receiving TANF/SNAP when joined program)
- Certain educational grants or loans used for tuition/fees

**Source**: https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Home/Features/Chapter%20A_700%2012-15-15.pdf

---

## Income Calculation Process

### Benefit Computation Steps:
1. Determine gross earned income
2. Subtract allowable earned income disregards (if eligible)
3. Subtract standard work expense ($90 or 20%)
4. Subtract actual child care expenses
5. Result = Net earned income
6. Add unearned income
7. Result = Total countable income
8. Compare to payment standard for household size
9. Benefit = Payment Standard - Total Countable Income (if positive)

---

## Non-Simulatable Rules (Architecture Limitation)

The following rules CANNOT be fully simulated in PolicyEngine due to single-period architecture:

### Time Limits
- **24-month state limit**: CANNOT ENFORCE - requires benefit history tracking
- **12-month sit-out period**: CANNOT ENFORCE - requires tracking
- **60-month federal lifetime limit**: CANNOT ENFORCE - requires cumulative tracking

### Graduated Earned Income Disregards
- **100%/85%/75%/65% progression**: CANNOT TRACK - requires employment history
- **Implementation**: Apply a conservative single rate (recommend 65% after work expense OR implement initial 100%)

### Disregard Renewal
- **12-month off-benefits requirement**: CANNOT TRACK - requires benefit history

### Work Participation History
- **Work requirements**: CANNOT TRACK - not part of eligibility simulation

---

## Partially Simulatable (Time-Limited Benefits)

### Earned Income Disregards
- **Rule**: 100% for first 3 months, decreasing to 65% over 12 months
- **Implementation**: Apply a single rate with documentation noting time limitation
- **Recommendation**: Use 65% rate (post-disregard period) for conservative estimates, OR 100% for maximum benefit estimates

### Standard Work Expense
- **Rule**: $90 or 20% of gross earnings (whichever is greater) after disregards exhausted
- **Implementation**: CAN simulate this as point-in-time calculation

---

## Implementation Approach

### Recommended Variables:

1. **nv_tanf_eligible** - Main eligibility determination
2. **nv_tanf_income_eligible** - Income eligibility (130% FPL + Need Standard tests)
3. **nv_tanf_resource_eligible** - Resource eligibility ($10,000 limit)
4. **nv_tanf_countable_earned_income** - Earned income after disregards
5. **nv_tanf_countable_unearned_income** - Unearned income (use federal baseline)
6. **nv_tanf** - Final benefit calculation

### Check if State Matches Federal Baseline:

- **Age thresholds**: Federal is age 18 (age 19 for students) - Nevada MATCHES federal
- **Immigration eligibility**: Nevada follows federal rules - MATCHES federal
- **Income sources**: Standard employment and self-employment - Use federal baseline with Nevada-specific disregards

---

## References for Metadata

### Legal/Regulatory Sources:
```yaml
reference:
  - title: "NRS 422A - Welfare and Supportive Services"
    href: "https://www.leg.state.nv.us/nrs/NRS-422A.html"
  - title: "Nevada DSS TANF FAQ - Income Considerations"
    href: "https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/"
```

### Variable References:
```python
reference = "https://dss.nv.gov/TANF/TANF_FAQ/"
```

---

## PDFs Requiring Extraction

The following PDFs contain critical information that needs extraction:

### 1. Nevada TANF State Plan
- **URL**: https://dss.nv.gov/uploadedFiles/dwssnvgov/content/TANF/TANF_State_Plan_FINAL%20_Effective_12.31.20.pdf
- **Purpose**: Contains official benefit calculation formulas, need standard/payment standard methodology, child support passthrough amounts
- **Key pages**: Unknown - full document review needed
- **Priority**: HIGH - contains authoritative calculation methodology

### 2. Chapter C-140 - TANF Needs Standards
- **URL**: https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Home/Features/Eligibility_and_Payments/Chapter%20C_140.pdf
- **Purpose**: Contains complete needs standard and payment standard tables by household size
- **Key pages**: Contains tables for all household sizes (1-10+)
- **Priority**: HIGH - essential for benefit calculation parameters

### 3. Chapter A-700 - Income
- **URL**: https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Home/Features/Chapter%20A_700%2012-15-15.pdf
- **Purpose**: Detailed income counting rules, earned/unearned income definitions
- **Key pages**: Income sources, exclusions, deductions
- **Priority**: MEDIUM - clarifies income treatment details

### 4. TANF Budget Form (2183-EE-A)
- **URL**: https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Home/Features/Forms/2183-EE-A_TANF%20Budget.pdf
- **Purpose**: Shows budget worksheet structure with payment allowance amounts
- **Key pages**: Budget calculation example
- **Priority**: MEDIUM - helpful for verification

### 5. NCCP Nevada TANF Profile
- **URL**: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Nevada.pdf
- **Purpose**: Consolidated policy summary with benefit amounts
- **Key pages**: All - summary document
- **Priority**: MEDIUM - secondary source for verification

### 6. Nevada Legal Services TANF Fact Sheet
- **URL**: https://nevadalegalservices.org/wp-content/uploads/2022/01/TANF-fact-sheet_2020-Update.pdf
- **Purpose**: Summary of eligibility and benefits
- **Key pages**: All - overview document
- **Priority**: LOW - tertiary source

---

## Key Web Sources Used

1. **Nevada DSS TANF Main Page**: https://dss.nv.gov/TANF/Financial_Help/
2. **TANF FAQ - Eligibility**: https://dss.nv.gov/TANF/TANF_FAQ/
3. **Income Considerations**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/
4. **Earned Income Disregards**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-1/
5. **Resource Limits**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-R/S/
6. **Time Limits**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-S/T/
7. **Age Requirements**: https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-A/
8. **Child-Only TANF**: https://www.fosterkinship.org/kinship-resources/child-only-tanf/
9. **TANF NEON**: https://www.first5nevada.org/services/parenting-and-family-support/temporary-assistance-for-needy-families-tanf-new-employees-of-nevada-neon/
10. **NRS 422A**: https://www.leg.state.nv.us/nrs/NRS-422A.html

---

## Documentation Gaps

The following information was NOT found in web sources and may require PDF extraction or direct agency contact:

1. **Complete Need Standard table** by household size (1-10+)
2. **Complete Payment Standard table** by household size
3. **Child support passthrough amount** (portion passed to families)
4. **Specific calculation formulas** for benefits
5. **Historical effective dates** for parameter changes

---

## PDF extraction required - documentation incomplete without PDFs listed above
