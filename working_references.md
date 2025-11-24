# Collected Documentation

## Missouri TANF (Temporary Assistance for Needy Families) Implementation
**Collected**: 2025-11-23
**Implementation Task**: Implement Missouri TANF eligibility and benefit calculation
**Documentation Status**: COMPLETE - All PDF extractions integrated with HTML research

---

## Program Overview

Missouri's Temporary Assistance (TA) program provides monthly cash benefits to help families care for their children in their own homes. The program emphasizes moving families toward self-sufficiency through work activities and job preparation.

**Key Program Features:**
- Maximum benefit for family of 3: $292/month (unchanged since 1991)
- Lifetime limit: 45 cumulative months
- Work requirements through Missouri Work Assistance (MWA) Program
- Resource limits: $1,000 at application, $5,000 with Individual Employment Plan
- Three-tiered income testing system
- Complex earned income disregard system with time limits

---

## Eligibility Requirements

### Demographic Eligibility

**Age Requirements:**
- **Eligible children**: Under age 18, OR age 18 and in secondary school/equivalent if expected to graduate before age 19
- **Minor parents**: Under age 19 and full-time student - all earned income disregarded
- **Pregnant women**: Eligible during the month before due date

**Implementation approach:**
- [x] Use federal demographic eligibility (age 18/19 thresholds match federal)
- Source: 13 CSR 40-2.300, 13 CSR 40-2.310

### Residency and Citizenship

**Requirements:**
- Must be resident of Missouri
- Must be U.S. citizen or qualified alien
- **Qualified alien restriction**: Those entering after August 22, 1996 face 5-year waiting period

**Social Security Numbers:**
- Required for all parents, caretakers, and children
- Must cooperate with obtaining SSNs

**Implementation approach:**
- [x] Use federal immigration eligibility (follows federal qualified alien rules)

### Resource Limits

**Source**: 13 CSR 40-2.310(3)

**At Application**: $1,000 maximum countable resources

**With Individual Employment Plan (IEP)**: $5,000 maximum countable resources

**Excluded Resources:**
- Primary residence (up to 40 adjoining acres)
- First automobile plus $1,500 equity in second vehicle
- Household furnishings and personal effects
- Tools and equipment for self-employment
- Qualified tuition programs (529 plans)
- Individual Development Accounts

**Countable Resources:**
- Life insurance cash surrender value
- Real property beyond homestead
- Joint bank accounts (unless verified as belonging to non-applicants)

---

## Income Eligibility Tests

**Source**: 13 CSR 40-2.310(10), (11), (12)

Missouri TANF requires passing THREE sequential income tests:

### 1. 185% Gross Income Test (13 CSR 40-2.310(10))

**Formula**: Total income (without earned income disregards except $90 and child care for up to 6 months) must be < 185% of Standard of Need

**Income Counted:**
- All earned and unearned gross income
- Income from sanctioned parents
- Stepparent income (appropriate amount)
- Minor parents' parents deemed income
- Income from excluded parents (fugitive felon/drug conviction)

**Income Deductions Allowed:**
- $90 standard work exemption (first 6 months only)
- Child care costs (first 6 months only)
- Overhead expenses for self-employment

**Income Deductions NOT Allowed:**
- $30+1/3 disregard
- $30 disregard
- Two-thirds disregard
- New spouse disregard
- Other earned income disregards beyond $90

**Example**: Family of 3 with $432/month income
- Standard of Need: $846
- 185% Test: $846 × 1.85 = $1,565.10
- $1,565.10 - $432 = $1,133.10 surplus → PASSES test

### 2. Standard of Need Test (13 CSR 40-2.310(11))

**Formula**: Total income (without earned income disregards except $90, child care, and student exemption) must be < Standard of Need

**Income Deductions Allowed:**
- $90 standard work exemption
- Child care costs
- Student income exemption (full-time students under 19)
- Overhead expenses for self-employment

**Income Deductions NOT Allowed:**
- $30+1/3 disregard
- $30 disregard
- Two-thirds disregard
- New spouse disregard

### 3. Percentage of Need Test (13 CSR 40-2.310(12))

**Formula**: Total income (after all earned income disregards) must be < 34.526% of Standard of Need

**This test determines BOTH eligibility AND benefit amount**

**All Disregards Applied:**
- $90 standard work exemption
- Child care costs ($175/$200)
- Two-thirds disregard OR $30+1/3 disregard OR $30 disregard (see detailed rules below)
- New spouse disregard (if applicable)
- Student income exemption
- Overhead expenses for self-employment

**If Eligible**: Grant = (34.526% × Standard of Need) - Net Countable Income
- Round DOWN to nearest dollar
- If grant < $10, no payment made

---

## Standard of Need Amounts

**Source**: 13 CSR 40-2.120(3)(A)1. - AFDC Consolidated Standard

Also called "Consolidated Standard" in regulations. Unchanged since 1991.

| Family Size | Standard of Need |
|------------|------------------|
| 1 person | $393.00 |
| 2 persons | $678.00 |
| 3 persons | $846.00 |
| 4 persons | $990.00 |
| 5 persons | $1,123.00 |
| 6 persons | $1,247.00 |
| 7 persons | $1,372.00 |
| 8 persons | $1,489.00 |
| 9 persons | $1,606.00 |
| 10 persons | $1,722.00 |
| 11 persons | $1,839.00 |
| 12+ persons | $1,956.00 + $116 per additional person |

---

## Income Sources and Treatment

### Earned Income (13 CSR 40-2.310(4)(A))

**Definition**: Income in cash or kind currently earned as wages, salary, commissions, or profits from business requiring continuing activity

**Included Sources:**
- Wages, bonuses, commissions
- Self-employment and farm income (>$1,000/year)
- On-the-job training positions
- Sheltered workshop earnings
- Subsidized federal employment
- Tips and training allowances
- Green Thumb senior programs
- AmeriCorps NCCC

**Excluded Sources:**
- AmeriCorps (non-NCCC)
- WIA Work Experience
- Title IV-funded Work Study
- YouthBuild payments
- Disaster payments
- Full income of minor parent if full-time student
- All earned income of minor parent up to 100% FPL

**Implementation approach:**
- [x] Use federal baseline for income sources (standard employment and self-employment definitions apply)

### Unearned Income

**Included Sources:**
- Social Security benefits
- Child support and alimony
- Military retirement and deployment compensation
- Veteran's disability benefits
- Unemployment insurance
- Railroad retirement
- Strike benefits and severance pay

**Excluded Sources:**
- SSI and state supplemental payments
- Section 8 housing subsidies
- TANF from other states
- Interest income
- Many educational assistance programs
- HUD vendor payments

### Child Support Treatment

**Source**: 13 CSR 40-2.310(4)(B), Manual Section 0210.015.20.20

**At Application:**
- Only actually received amounts budgeted
- Intercepted by Child Support Enforcement day after case approval

**Active Cases:**
- CSE retains lesser of: (1) assigned arrearages, or (2) unreimbursed assistance
- Excess child support goes to child
- Child support reduces TA dollar-for-dollar
- **NO CHILD SUPPORT PASSTHROUGH/DISREGARD FOR TANF**
- (Note: $50 disregard only applies to Medical Assistance for Families, not TA)

---

## Earned Income Disregards

**Source**: 13 CSR 40-2.120(6), 13 CSR 40-2.310(9)(D), 13 CSR 40-2.310(8)(B)1.D.

Missouri has a complex system of earned income disregards with different rules based on:
- Whether person is actively receiving TA when they become employed
- Length of time receiving TA
- Marital status changes

### Complete List of Disregards (13 CSR 40-2.120(6))

1. **All earned income of full-time students** (under age 19)
2. **First $90 of gross earned income** (standard work exemption)
3. **$30 + 1/3 of remainder** for 4 consecutive months
4. **$30 disregard only** for 8 months following the 4 consecutive months
5. **Child care costs**: $175/month (age 2+), $200/month (under age 2)
6. **All earned income of parents under 19 who are full-time students**

### Two-Thirds Disregard (13 CSR 40-2.310(9)(D))

**For Active TA Recipients Who Become Employed:**

- **Amount**: 2/3 of gross monthly earned income
- **Duration**: 12 consecutive months
- **Applied BEFORE**: Standard work exemption ($90) and child care costs
- **Eligibility**: Once used, not eligible again until 12 consecutive months off TA
- **Purpose**: Incentivize work for current recipients

**Disregard Sequence for Active Recipients:**
1. Two-thirds disregard (2/3 of gross earned income)
2. Standard work exemption ($90)
3. Child care costs ($175/$200)

### $30+1/3 Disregard

**For Non-Active TA Recipients Who Become Employed:**

- **Amount**: $30 + 1/3 of remaining earned income after $90 exemption
- **Duration**: 4 consecutive months
- **Followed by**: $30 disregard only for next 8 months
- **Purpose**: Transition assistance for those entering TA while employed

**Disregard Sequence for Non-Active Recipients:**
1. Standard work exemption ($90)
2. $30 + 1/3 of remainder (4 months)
3. $30 only (8 months)
4. Child care costs ($175/$200)

### New Spouse Disregard (13 CSR 40-2.310(8)(B)1.D.)

**Special Provision for New Marriages:**

- **Coverage**: New spouse's income and resources disregarded completely
- **Duration**: 6 consecutive months of TA receipt
- **Eligibility**: Once-in-a-lifetime benefit per person
- **Both Parents**: Applied to both parents if both are TA recipients when they marry
- **Purpose**: Encourage family formation without immediate benefit loss

### Child Care Deductions

**Source**: 13 CSR 40-2.120(6)

**Amounts:**
- **$175/month** for children age 2 and over
- **$200/month** for children under age 2

**Applied to**: Costs for child care or care of incapacitated person in household

### CRITICAL Implementation Notes

**For 185% Test:**
- Only $90 exemption and child care allowed (first 6 months only)
- NO other disregards applied to this test

**For Standard of Need Test:**
- Only $90 exemption, child care, and student exemption allowed
- NO two-thirds, $30+1/3, or $30 disregards applied

**For Percentage of Need Test:**
- ALL disregards applied
- This determines final benefit amount

---

## Self-Employment Overhead Expenses

**Verification**: Previous year's tax forms when possible

**Allowed Deductions:**

**Income from boarders:**
- Food expense: Monthly Food Stamp issuance for 1-person household per boarder

**Income from child care self-employment:**
- Meals: $1.00 per child per meal provided (unless already deducted on tax schedules)

**Income from sales:**
- Vehicle operation: Current state reimbursement rate
- Supplies: Actual cost as paid

**Note**: All self-employment expenses entered in eligibility system

---

## Maximum Benefit Amounts

**Source**: 13 CSR 40-2.310(13) - Equal to 34.526% of Standard of Need

Benefit amounts have been frozen since 1991.

| Family Size | Maximum Monthly Benefit |
|------------|-------------------------|
| 1 person | $136 |
| 2 persons | $234 |
| 3 persons | $292 |
| 4 persons | $342 |
| 5 persons | $388 |
| 6 persons | $431 |
| 7 persons | $474 |
| 8 persons | $514 |
| 9 persons | $554 |
| 10 persons | $595 |
| 11 persons | $635 |
| 12+ persons | (continues with ~$40 increments) |

**Calculation**: Each maximum equals Standard of Need × 0.34526

**Verification Examples:**
- 1 person: $393 × 0.34526 = $135.67 → $136 (rounded)
- 3 persons: $846 × 0.34526 = $292.09 → $292
- 5 persons: $1,123 × 0.34526 = $387.72 → $388 (rounded)

**Rounding Rules:**
- Always round DOWN to nearest dollar
- If determined need results in grant < $10, no cash payment made

**Prorated Payments:**
- Application month: Prorated from date of application through end of month
- Formula: (Monthly amount) × (days from application to end of month) ÷ 30

---

## Assistance Unit Composition

### Members Included (if eligible):

1. **Eligible children**: Under age 18, OR age 18 in secondary school if graduating before age 19
2. **Natural or adoptive parents** of one or more eligible children
3. **Needy non-parent caretaker relative** or related/unrelated guardian
   - Has option to be excluded from assistance group
4. **Biological or adoptive siblings** of eligible child if meeting conditions and living in home

### Eligible Relative Caretakers:

- Biological/adoptive parents
- Grandparents (but not their parents)
- Siblings
- Aunts and uncles
- Cousins
- Legal guardians

### Deprivation Requirements:

Children must be deprived of parental support due to:
- Parent death
- Absence from/never living in home
- Physical/mental incapacity (30+ days)
- Divorce/separation
- Desertion
- Institutional confinement
- Vocational rehabilitation participation
- Insufficient parental income

### Special Rules:

**SSI Recipients:**
- Cannot receive TA for themselves
- Their income, expenses, and resources excluded from household calculations

**Minor Parents' Parents (Income Deeming):**
- Income of minor parent's parents living in home included same as stepparent income

---

## Work Requirements and Exemptions

**Source**: Missouri TANF State Plan 2024-2027

### Work Participation Hours

**Single Parents:**
- 30 hours/week required
- 20 hours/week if child under age 6

**Two-Parent Families:**
- 35 hours/week required
- 55 hours/week if receiving federally-funded child care assistance

### Exemptions from Work Requirements

**Permanent Exemptions:**
- Permanently disabled individuals
- Children under 18 (or 18-19 if in secondary school)
- Caretakers age 60 or older
- Single parents with child under 12 weeks old
- Caring for disabled family member

**Temporary Exclusions:**
- Temporarily disabled (30 days to 6 months)
- Domestic violence victim
- Active Children's Division case
- Unable to find child care or transportation

### New Applicant Requirements

**Effective August 28, 2015:**
- Must complete standardized orientation
- Must sign Personal Responsibility Plan
- Must complete online job registration before receiving payment (effective January 1, 2016)

**Sanctioned Cases:**
- If closed due to work sanction: must perform 30 hours/week work activities for 1 month before reapplying

**Active Recipients:**
- Must engage in work activities once work-ready OR after 24 months of TA receipt

**Implementation Note**: TANF implementations only model eligibility and benefit calculation, not work participation requirements

---

## Special Programs and Benefits

**Source**: Missouri TANF State Plan 2024-2027

### Transitional Employment Benefit

- **Amount**: $50/month
- **Duration**: Up to 6 months
- **Eligibility**: Individuals leaving TA due to increased earnings
- **Purpose**: Support during transition to employment

### Cash Diversion Program

- **Amount**: Lump sum payment equal to 2-3 months of benefits
- **Purpose**: Emergency needs that would prevent employment
- **Lifetime Limit**: Maximum 5 diversion payments in lifetime as parent/guardian/caretaker relative
- **Effect**: May delay regular TA eligibility

### Hardship Extensions

- **Purpose**: Extensions to 45-month lifetime limit
- **Criteria**: Documented hardship circumstances
- **Decision**: Case-by-case basis

---

## Time Limits

**Lifetime Limit**: 45 cumulative months (effective January 1, 2016)

**Diversion Program**: Maximum 5 diversion payments in lifetime as parent/guardian/caretaker relative

**Hardship Extensions**: Available on case-by-case basis

---

## References for Metadata

### Legal Code - Missouri Code of State Regulations (13 CSR)

```yaml
# Definitions
- title: "13 CSR 40-2.300 - Definitions for TANF Block Grant Programs"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-300"

# Eligibility Requirements
- title: "13 CSR 40-2.310 - Requirements as to Eligibility for Temporary Assistance"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310"

# Subsections for specific parameters:
- title: "13 CSR 40-2.310(3) - Resource Limits"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310"

- title: "13 CSR 40-2.310(10) - 185% Gross Income Test"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310"

- title: "13 CSR 40-2.310(11) - Standard of Need Test"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310"

- title: "13 CSR 40-2.310(12) - Percentage of Need Test"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310"

- title: "13 CSR 40-2.310(13) - Maximum Benefit Amounts"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310"

- title: "13 CSR 40-2.310(9)(D) - Two-Thirds Disregard"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310"

- title: "13 CSR 40-2.310(8)(B)1.D. - New Spouse Disregard"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310"

# Payment Determination
- title: "13 CSR 40-2.120 - Methods Used to Determine the Amount of Cash Payments"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120"

- title: "13 CSR 40-2.120(3)(A)1. - Standard of Need Amounts"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120"

- title: "13 CSR 40-2.120(6) - Earned Income Disregards"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120"

# Work Requirements
- title: "13 CSR 40-2.315 - Work Activity and Work Requirements"
  href: "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-315"
```

### Policy Manual - Missouri DSS Manuals

```yaml
# Program Overview
- title: "0200.000.00 - Overview of the Temporary Assistance Program"
  href: "https://dssmanuals.mo.gov/temporary-assistance-case-management/0200-000-00/"

# 185% Test
- title: "0210.010.05 - 185 Percent Income Eligibility Limit"
  href: "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-05-185/"

# Percentage of Need
- title: "0210.010.15 - Percentage of Need"
  href: "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-15/"

# Income Sources
- title: "0210.015.05 - Sources of Earned, Unearned, and Educational Income"
  href: "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-05/"

# Earned Income Disregards
- title: "0210.015.30 - Earned Income Disregards"
  href: "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/"

# Child Support Treatment
- title: "0210.015.20.20 - Treatment of Child Support Income"
  href: "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-20-20/"
```

### Federal Regulations

```yaml
# Federal TANF Regulations
- title: "45 CFR Part 260 - General TANF Provisions"
  href: "https://www.ecfr.gov/current/title-45/subtitle-B/chapter-II/part-260"

- title: "45 CFR Part 261 - Ensuring That Recipients Work"
  href: "https://www.ecfr.gov/current/title-45/subtitle-B/chapter-II/part-261"
```

### State Plans and Analysis

```yaml
# Current State Plan
- title: "Missouri TANF State Plan 2024-2027"
  href: "https://dss.mo.gov/fsd/pdf/tanf-wioa-2024-2027.pdf"

# Previous State Plan
- title: "Missouri TANF State Plan 2021-2023"
  href: "https://dss.mo.gov/fsd/pdf/mo-tanf-plan-ffy2021-2023.pdf"
```

---

## Implementation Notes

### Program Structure

Missouri TANF uses a **needs-based test** with three sequential income tests:

1. **185% Gross Income Test** - First eligibility gate (gross income only, minimal deductions)
2. **Standard of Need Test** - Income cannot meet full need standard
3. **Percentage of Need Test (34.526%)** - Final eligibility test AND benefit calculation

### Key Implementation Details

**Income Tests:**
- All three tests must be passed for eligibility
- Different deductions apply to different tests
- 185% test uses GROSS income (only overhead expenses, $90, and child care for first 6 months)
- Standard of Need test adds student exemption
- Percentage of Need test uses NET income (after ALL disregards)

**Earned Income Disregards - Complex System:**
- **Two different sequences** depending on whether person is actively receiving TA when employed
- **Active recipients**: Get two-thirds disregard for 12 months (better benefit)
- **Non-active recipients**: Get $30+1/3 for 4 months, then $30 only for 8 months
- **New spouse**: Complete disregard for 6 months (once in lifetime)
- **Time limits** on various disregards must be tracked
- **NOT applied** to 185% test calculation (except $90 and child care for first 6 months)

**Payment Calculation:**
- Grant = (34.526% × Standard of Need) - Net Countable Income
- Always round DOWN to nearest dollar
- No payment if < $10

**Resource Handling:**
- Limit increases from $1,000 to $5,000 after signing Individual Employment Plan
- Significant exclusions (home, vehicle, retirement accounts)

**Child Support:**
- No passthrough/exclusion for TANF (unlike many states)
- Counts dollar-for-dollar against eligibility and benefits
- Intercepted by CSE upon case approval

**Constants Since 1991:**
- Standard of Need amounts frozen
- Maximum benefit amounts frozen
- 34.526% percentage frozen
- This means real value has declined significantly with inflation

### Comparison to Federal Baseline

**Missouri DIFFERS from federal baseline:**
- Uses 185% of State standard (not FPL) for income eligibility
- Has three-tiered income testing system (not common)
- No child support passthrough ($50 disregard)
- Resource limit increases with Individual Employment Plan
- Complex earned income disregard system with multiple time-limited options
- Two-thirds disregard for active recipients (12 months)
- New spouse disregard (6 months, once in lifetime)

**Missouri MATCHES federal baseline:**
- [x] Age thresholds (18/19 for students) - use federal demographic eligibility
- [x] Immigration eligibility (follows federal qualified alien rules) - use federal immigration eligibility
- [x] SSI exclusion rules
- [x] Basic income source definitions - use federal baseline

### Special Implementation Challenges

**Disregard Tracking:**
- Need to track which disregard sequence applies to each person
- Need to track months remaining on time-limited disregards
- Need to track whether two-thirds disregard has been used (lifetime limit)
- Need to track new spouse disregard usage (once in lifetime)

**Income Test Sequence:**
- Must apply different disregards to different tests
- 185% test: minimal disregards
- Standard of Need test: intermediate disregards
- Percentage of Need test: all disregards

**Simplified Implementation Option:**
- For initial implementation, could assume all recipients are in "steady state" (past initial months)
- This would mean: no two-thirds disregard, no $30+1/3 disregard, no new spouse disregard
- Only apply: $90 standard exemption + child care costs
- Document this simplification clearly

### Data Requirements

**For Full Implementation:**
- Months receiving TA (for 45-month lifetime limit)
- Employment status at application (for disregard sequence)
- Months on each disregard type (for time limits)
- New spouse flag and months (for new spouse disregard)
- Individual Employment Plan status (for resource limit)

**For Simplified Implementation:**
- Just basic household composition and income
- Assume steady-state disregards

---

## Verification and Cross-References

### Standard of Need = Consolidated Standard

These terms are used interchangeably in Missouri regulations:
- 13 CSR 40-2.120(3)(A)1. calls it "AFDC Consolidated Standard"
- 13 CSR 40-2.310 calls it "Standard of Need"
- Both refer to same amounts ($393 for 1 person, $846 for 3 persons, etc.)

### 34.526% Percentage Verification

Maximum benefit amounts are exactly 34.526% of Standard of Need:
- This percentage appears in 13 CSR 40-2.310(12) and (13)
- Also called "Percentage of Need" in regulations
- Frozen since 1991 along with Standard of Need amounts

### Payment Standards Table Verification

All maximum benefit amounts verified as Standard of Need × 0.34526:
- 1: $393 × 0.34526 = $135.67 → $136
- 2: $678 × 0.34526 = $234.08 → $234
- 3: $846 × 0.34526 = $292.09 → $292
- 4: $990 × 0.34526 = $341.81 → $342
- 5: $1,123 × 0.34526 = $387.73 → $388
- 6: $1,247 × 0.34526 = $431.14 → $431

Small rounding differences due to truncation.

---

**Documentation Complete**: All critical PDFs extracted and integrated with HTML research. Ready for test-creator and rules-engineer implementation.
