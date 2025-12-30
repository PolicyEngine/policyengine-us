# Collected Documentation

## Rhode Island Works (RIW) - Rhode Island TANF Implementation
**Collected**: 2025-12-29
**Implementation Task**: Implement Rhode Island's TANF cash assistance program (Rhode Island Works)

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Rhode Island Works (RIW)
**Abbreviation**: RIW
**Source**: R.I. Gen. Laws Chapter 40-5.2 et seq. (The Rhode Island Works Program)

**Variable Prefix**: `ri_tanf` (following existing state TANF naming conventions)

---

## Regulatory Authority

### Primary Legal Sources

1. **Rhode Island General Laws Chapter 40-5.2** - The Rhode Island Works Program
   - Establishes the legal framework for cash assistance
   - URL: https://law.justia.com/codes/rhode-island/2023/title-40/chapter-40-5-2/

2. **218-RICR-20-00-2** - Rhode Island Works Program Rules and Regulations
   - Full administrative code implementing the program
   - URL: https://rules.sos.ri.gov/Regulations/part/218-20-00-2

3. **218-RICR-20-00-2.15** - Income (specific regulation section)
   - Details income calculation methodology and disregards
   - URL: https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15

### Administering Agency
Rhode Island Department of Human Services (DHS)
- Program Page: https://dhs.ri.gov/programs-and-services/ri-works-program
- Eligibility Page: https://dhs.ri.gov/programs-and-services/ri-works-program/eligibility-how-apply

---

## Non-Financial Eligibility Requirements

### Age Requirements
**Source**: 218-RICR-20-00-2

- **Dependent child**: Under age 18
- **Full-time student exception**: Age 18-19 if enrolled full-time in secondary school or equivalent
- **Pregnant women**: Eligible from pregnancy verification

### Citizenship/Immigration Requirements
**Source**: 218-RICR-20-00-2

Applicant must be:
- U.S. citizen, OR
- Qualified non-citizen (refugees, asylees, Legal Permanent Residents who entered before 8/22/96, or LPRs in status 5+ years if entered after 8/22/96)

**Implementation approach:**
- [x] Use federal immigration eligibility (state follows federal rules)

### Residency Requirement
- Must maintain continuous physical presence in Rhode Island

### Relationship Requirement
Child must live with:
- Parent(s), OR
- Caretaker relatives (grandparents, aunts, uncles, adult siblings), OR
- Legal guardian

### Teen Parent Requirements
Pregnant/parenting teens under 18 must:
- Reside with parent/relative or in supervised supportive living arrangement
- Participate in secondary education

---

## Resource/Asset Limits

**Source**: 218-RICR-20-00-2

### Resource Limit
- **Maximum**: $5,000 in countable resources

### Resource Exclusions
- Primary residence and appurtenant land
- One vehicle per adult (maximum two vehicles per household)
- Income-producing property necessary for employment
- Household furnishings and personal effects
- One burial plot per family member
- Funeral agreements (up to $1,000 per person)
- EITC refunds (12-month exclusion period)

### Verification Requirements
- Self-attestation accepted for resources under $3,000
- Documentation required for resources between $3,000-$5,000

---

## Income Eligibility Tests

### Net Income Test (Primary Eligibility Test)
**Source**: 218-RICR-20-00-2.15

Rhode Island Works uses a **net income test** - comparing countable income after disregards to the payment standard.

**Formula**: Net Adjusted Income = (Earned Income - Earned Income Disregards) + Unearned Income

**Eligibility**: Net Adjusted Income must be less than the applicable Payment Standard

### Employment Transition Test (6-Month Period)
**Source**: 218-RICR-20-00-2.15

When a parent has earnings, they can continue to receive full RI Works benefits for 6 months as long as:
- Gross income is less than **185% of Federal Poverty Level (FPL)**

**Note**: This is a time-limited provision that cannot be fully simulated (see Non-Simulatable Rules section).

---

## Income Deductions and Disregards

### Earned Income Disregards
**Source**: 218-RICR-20-00-2.15

Applied in this order:

1. **Dependent Child Earnings**: Disregard ALL earned income of dependent children

2. **Standard Earned Income Disregard** (per eligible individual):
   - Disregard **$525.00** from gross earned income, PLUS
   - Disregard **50% (one-half)** of remaining earned income after the $525 disregard

   **Formula**: Countable Earned = (Gross Earned - $525) * 0.5

   (If gross earned is less than $525, countable earned income = $0)

3. **Dependent Care Disregard** (actual expenses, per child/incapacitated adult):
   - Children age 2 and older: up to **$175/month** per child
   - Children under age 2: up to **$200/month** per child
   - Incapacitated adults: up to **$175/month**
   - Only applies when care is provided by non-household members

### Unearned Income Treatment
**Source**: 218-RICR-20-00-2.15

Unearned income is counted **dollar-for-dollar** with limited exceptions.

**Sources of Unearned Income** (counted):
- Retirement, Survivors, and Disability Insurance (RSDI)
- Unemployment Insurance (UI)
- Temporary Disability Insurance (TDI)
- Veterans' Administration benefits (non-disability pension)
- Workers' Compensation
- Interest and dividends
- Regular contributions from non-legally liable relatives
- Child support (amounts exceeding $50/month)

### Child Support Passthrough
**Source**: 218-RICR-20-00-2.15

- **First $50** of monthly child support from each noncustodial parent is **excluded**
- Amounts exceeding $50 are counted as unearned income
- Applies in initial month of eligibility

### Income Exclusions
**Source**: 218-RICR-20-00-2.15

The following income types are EXCLUDED:
- SSI (Supplemental Security Income) benefits
- Food assistance (SNAP, WIC, child nutrition)
- Housing subsidies (federal, state, local)
- EITC refunds and advance payments
- Educational assistance (scholarships, grants, loans for undergraduates)
- VISTA volunteer payments
- Home energy assistance (LIHEAP)
- Native American per capita payments
- Veterans' disability pension benefits
- Small gifts under $30 per recipient per quarter

### Self-Employment Income
**Source**: 218-RICR-20-00-2.15

Net income = Gross receipts - Allowable operating expenses

Non-deductible expenses:
- Depreciation
- Personal business and entertainment expenses
- Personal transportation

### Roomer/Boarder Income
**Source**: 218-RICR-20-00-2.15

- **Roomer**: Subtract $25/month maintenance cost
- **Boarder**: Subtract $124/month maintenance cost

---

## Payment Standards (Benefit Amounts)

### Current Payment Standards (2025)
**Source**: Economic Progress Institute, DHS Press Releases

The payment standard is the maximum benefit amount. Families receive the **difference** between their countable income and the payment standard.

| Family Size | Standard (Non-Subsidized) | Subsidized Housing |
|-------------|---------------------------|-------------------|
| 1           | $510                      | $445              |
| 2           | $701 (or $700)            | $635              |
| 3           | $865                      | $800 *            |
| 4           | $990                      | $925              |
| 5           | $1,115                    | $1,050            |
| 6           | $1,240                    | $1,175            |
| 7           | $1,364                    | $1,299            |
| 8           | $1,489                    | $1,424            |
| 6+          | Add $125 per additional person | Add $125      |

**Subsidized Housing Reduction**: Per 218-RICR-20-00-2, families in subsidized housing receive a **$65.00 reduction** to their standard assistance payment.

\* Note: The Economic Progress Institute lists $791 for subsidized housing family of 3, but per the $65 reduction rule it should be $800. The regulation states a flat $65 reduction.

### Previous Payment Standards (2021, for reference)
**Source**: DHS Press Release (August 2021)

After 30% increase effective July 1, 2021:
| Family Size | Standard | Subsidized Housing |
|-------------|----------|-------------------|
| 1           | $425     | $360              |
| 2           | $584     | $519              |
| 3           | $721     | $656              |
| 4           | $825     | $760              |

### Benefit History
- **2021**: 30% benefit increase (July 1, 2021)
- **2024**: 20% benefit increase (FY 2025 state budget, effective September 2024)

---

## Benefit Calculation

### Formula
**Source**: 218-RICR-20-00-2

```
Benefit = Payment Standard - Net Countable Income
```

Where:
- **Payment Standard** = Amount from table above based on family size and housing status
- **Net Countable Income** = Countable Earned Income + Unearned Income

### Calculation Steps

1. **Calculate Gross Earned Income** (exclude dependent child earnings)
2. **Apply Earned Income Disregard**:
   - Subtract $525 from gross earned
   - Take 50% of remainder
   - Result = Countable Earned Income (cannot be negative)
3. **Apply Dependent Care Deduction** (if applicable)
4. **Calculate Countable Unearned Income** (dollar-for-dollar minus exclusions)
5. **Sum** Countable Earned + Countable Unearned = Net Countable Income
6. **Subtract** Net Countable Income from Payment Standard = Benefit Amount

### Minimum Payment Threshold
**Source**: 218-RICR-20-00-2

"No payment of cash assistance shall be made for any month if the amount of such payment would be less than **ten dollars ($10.00)**."

Families meeting all eligibility criteria but with calculated benefit under $10 remain active cases but receive no cash payment.

### Payment Schedule
- Benefits issued **twice monthly** via Electronic Benefit Transfer (EBT)
- Payments on the **1st and 16th** of each month
- Benefits for first month are prorated based on application date

---

## Time Limits

### Lifetime Limit
**Source**: R.I. Gen. Laws 40-5.2, 218-RICR-20-00-2

- **60 months** lifetime limit on cash assistance for adults
- Months receiving benefits in ANY state count toward the limit
- Months need not be consecutive

### Child Benefits Exception
Children can receive benefits beyond parent's time limit if:
- Living with SSI-receiving parent, OR
- Living with non-payment caretaker relative

### Hardship Extensions
**Source**: 218-RICR-20-00-2

Families reaching 60-month limit may request 6-month extensions if meeting one of:
1. Documented significant disability with pending SSI/SSDI application
2. Caring for significantly disabled family member requiring full-time care
3. Experiencing homelessness
4. Unable to work due to current domestic violence situation
5. Unable to work due to critical circumstances (supervisor-approved)

---

## Non-Simulatable Rules (Architecture Limitation)

### CANNOT be simulated (require historical tracking):

1. **60-Month Lifetime Limit** - Cannot track cumulative months of benefit receipt across periods

2. **185% FPL Gross Income Test for 6 Months** - The employment transition provision allowing full benefits for 6 months while gross income < 185% FPL requires tracking employment start date and duration

3. **Work Requirements** - Must work/participate in work activities 20-35 hours/week depending on circumstances; cannot track participation

4. **Progressive Sanctions** - Benefit reductions for non-compliance escalate over time

5. **First-Month Child Support Exclusion** - The $50 child support exclusion specifically applies "in initial month of eligibility"

### CAN be simulated (current point-in-time):

- Current resource limits ($5,000)
- Current income calculations with disregards
- Current benefit calculations (Payment Standard - Net Income)
- Current household composition
- Subsidized housing reduction ($65)
- Minimum benefit threshold ($10)

---

## Income Deeming Provisions

### Minor Parent Deeming
**Source**: 218-RICR-20-00-2.16

When unwed minor parent (under 18) lives with their parent(s)/stepparent:
1. Disregard first $90 from grandparent's gross earned income
2. Disregard amount equal to cash assistance standard for grandparent's household
3. Disregard amounts paid for dependents not in the home
4. Disregard alimony/child support payments
5. Remainder is deemed as unearned income to minor's assistance unit

**Exception**: Income of SSI-eligible parents/stepparents is NOT subject to deeming.

### Non-Citizen Sponsor Deeming
**Source**: 218-RICR-20-00-2.17

Sponsor and sponsor's spouse income is deemed to sponsored non-citizen (except organization-sponsored cases).

---

## Reporting Requirements

**Source**: 218-RICR-20-00-2

- Changes must be reported within **10 days**
- Child absences exceeding 30 days must be reported within **5 days**
- Mid-certification verification required in **month 5** of 12-month certification period

---

## Implementation Approach Summary

### Use Federal Baseline For:
- [x] Demographic eligibility (age 18/19 matches federal rules)
- [x] Immigration eligibility (follows federal qualified non-citizen rules)

### Create State-Specific Variables For:
- [x] Earned income disregard ($525 + 50% of remainder)
- [x] Dependent care deduction ($175/$200 limits)
- [x] Child support exclusion ($50)
- [x] Payment standards by family size
- [x] Subsidized housing reduction ($65)
- [x] Resource limit ($5,000)
- [x] Benefit calculation

---

## References for Metadata

### For Parameters:
```yaml
reference:
  - title: 218-RICR-20-00-2.15 Income
    href: https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15
  - title: Rhode Island Works Program Eligibility
    href: https://dhs.ri.gov/programs-and-services/ri-works-program/eligibility-how-apply
```

### For Variables:
```python
reference = (
    "https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15",
    "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
)
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **Rhode Island Works Program Participant Guide**
   - URL: https://dhs.ri.gov/media/7966/download?language=en
   - Expected content: Detailed program rules, benefit tables, eligibility requirements

2. **218-RICR-20-00-2 Full Regulations PDF**
   - URL: https://dhs.ri.gov/media/6351/download?language=en
   - Expected content: Complete regulatory text with all sections

3. **Rhode Island TANF State Plan PDF**
   - URL: https://risos-apa-production-public.s3.amazonaws.com/DHS/218-RICR-20-00-2_Rhode%20Island%20Works%20Rules%20and%20and%20Regulations.pdf
   - Expected content: State plan submitted to ACF with income calculation methodology details

4. **NCCP Rhode Island TANF Profile**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Rhode-Island.pdf
   - Expected content: Summary of eligibility, benefits, and policy details

5. **ACF TANF and MOE Spending - Rhode Island**
   - URL: https://www.acf.hhs.gov/sites/default/files/documents/ofa/fy2021_tanf_moe_state_piechart_rhodeisland.pdf
   - Expected content: TANF spending breakdown

---

## Key Parameters Summary

| Parameter | Value | Source |
|-----------|-------|--------|
| Resource limit | $5,000 | 218-RICR-20-00-2 |
| Earned income disregard (flat) | $525 | 218-RICR-20-00-2.15 |
| Earned income disregard (rate) | 50% (0.5) | 218-RICR-20-00-2.15 |
| Dependent care (age 2+) | $175/month | 218-RICR-20-00-2.15 |
| Dependent care (under 2) | $200/month | 218-RICR-20-00-2.15 |
| Child support exclusion | $50/month | 218-RICR-20-00-2.15 |
| Subsidized housing reduction | $65 | 218-RICR-20-00-2 |
| Minimum benefit | $10 | 218-RICR-20-00-2 |
| Lifetime limit | 60 months | R.I. Gen. Laws 40-5.2 |
| Payment standard (size 1) | $510 | DHS/Economic Progress Institute |
| Payment standard (size 2) | $701 | DHS/Economic Progress Institute |
| Payment standard (size 3) | $865 | DHS/Economic Progress Institute |
| Payment standard (size 4) | $990 | DHS/Economic Progress Institute |
| Payment standard (size 5) | $1,115 | DHS/Economic Progress Institute |
| Payment standard (size 6) | $1,240 | DHS/Economic Progress Institute |
| Payment standard increment | $125/person | DHS/Economic Progress Institute |
| Minor child age threshold | 18 | 218-RICR-20-00-2 |
| Student age threshold | 19 | 218-RICR-20-00-2 |
| Minor parent deeming disregard | $90 | 218-RICR-20-00-2.16 |
| Roomer maintenance deduction | $25/month | 218-RICR-20-00-2.15 |
| Boarder maintenance deduction | $124/month | 218-RICR-20-00-2.15 |

---

## Sources

### Primary Sources (Official Government)
1. [Rhode Island Works Program - DHS](https://dhs.ri.gov/programs-and-services/ri-works-program)
2. [Rhode Island Works Eligibility - DHS](https://dhs.ri.gov/programs-and-services/ri-works-program/eligibility-how-apply)
3. [218-RICR-20-00-2 Income Regulations - Cornell LII](https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15)
4. [218-RICR-20-00-2 Full Regulations - RI Secretary of State](https://rules.sos.ri.gov/Regulations/part/218-20-00-2)
5. [RI Works Benefit Increase FY 2025 - DHS](https://dhs.ri.gov/press-releases/rhode-island-works-families-see-increase-benefits-fy-2025-state-budget)
6. [RI Works 30% Benefit Increase 2021 - DHS](https://dhs.ri.gov/press-releases/ri-works-benefit-increase-almost-here)
7. [SSA POMS - Rhode Island TANF](https://secure.ssa.gov/poms.nsf/lnx/0500830407BOS)

### Secondary Sources (Policy Analysis)
1. [Economic Progress Institute - Rhode Island Works](https://economicprogressri.org/resources/rhode-island-works-program-ri-works)
