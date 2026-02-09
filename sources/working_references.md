# Collected Documentation

## Iowa Family Investment Program (FIP) / TANF Implementation
**Collected**: 2026-02-09
**Implementation Task**: Implement Iowa's TANF program (Family Investment Program / FIP) including eligibility determination, income tests, deductions, and benefit calculation.

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Family Investment Program (FIP)
**Abbreviation**: FIP
**Administering Agency**: Iowa Department of Health and Human Services (HHS)
**Source**: Iowa Code Chapter 239B; IAC 441-41.21 through 441-41.30

**Variable Prefix**: `ia_tanf`
**Parameter Path**: `parameters/gov/states/ia/hhs/tanf/`

---

## Source Information

### Primary Legal Sources

1. **Iowa Code Chapter 239B** - Family Investment Program
   - Citation: Iowa Code Ch. 239B
   - URL: https://www.legis.iowa.gov/docs/ico/chapter/239B.pdf
   - Type: State statute (PDF)

2. **IAC 441-41.21** - Eligibility factors specific to child
   - Citation: Iowa Admin. Code r. 441-41.21(239B)
   - URL: https://www.legis.iowa.gov/docs/iac/rule/441.41.21.pdf
   - Type: Administrative rule (PDF)

3. **IAC 441-41.22** - Eligibility factors specific to payee
   - Citation: Iowa Admin. Code r. 441-41.22(239B)
   - URL: https://www.legis.iowa.gov/docs/ACO/rule/441.41.22.pdf
   - Type: Administrative rule (PDF)

4. **IAC 441-41.23** - Home, residence, citizenship, and alienage
   - Citation: Iowa Admin. Code r. 441-41.23(239B)
   - URL: https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-23
   - Effective Date: 7/1/2025

5. **IAC 441-41.26** - Resources
   - Citation: Iowa Admin. Code r. 441-41.26(239B)
   - URL: https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-26
   - Effective Date: Current

6. **IAC 441-41.27** - Income
   - Citation: Iowa Admin. Code r. 441-41.27(239B)
   - URL: https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27
   - Effective Date: 7/1/2025

7. **IAC 441-41.28** - Need standards
   - Citation: Iowa Admin. Code r. 441-41.28(239B)
   - URL: https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28
   - Effective Date: 7/1/2025

8. **IAC 441-41.30** - Time limits
   - Citation: Iowa Admin. Code r. 441-41.30(239B)
   - URL: https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-30
   - Effective Date: 7/1/2025

9. **IAC 441-45.27** - Rounding of need standard and payment amount
   - Citation: Iowa Admin. Code r. 441-45.27
   - URL: https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-45-27
   - Effective Date: 7/1/2025

### Secondary Sources

10. **Iowa HHS FIP Overview Page**
    - URL: https://hhs.iowa.gov/assistance-programs/cash-assistance/fip-tanf

11. **WorkWorld FIP Financial Eligibility**
    - URL: https://help.workworldapp.com/wwwebhelp/fip_eligibility_financial_iowa.htm
    - Note: Some information may be outdated (references 50% work incentive; current law is 58%)

---

## Demographic Eligibility

### Age Thresholds
- **Minor child age limit**: Under 18 years (eligible without regard to school attendance)
- **Full-time student age limit**: 18 years old, attending secondary school or equivalent vocational/technical training full-time, and reasonably expected to complete before age 19
- **Source**: IAC 441-41.21(239B)

**Exact statutory language**: "The FIP will be available to a needy child under the age of 18 years without regard to school attendance" and "FIP will also be available to a needy child of 18 years who is a full-time student in a secondary school, or in the equivalent level of vocational or technical training, and who is reasonably expected to complete the program before reaching the age of 19."

### Eligible Group Composition
- All dependent children who are siblings of whole or half blood or adoptive
- Any parent of such children living in the same home
- The needy specified relative who assumes the role of parent
- SSI recipients are excluded from the eligible group
- There must be at least one child in the eligible group (except when only eligible child receives SSI)
- **Source**: IAC 441-41.22(239B), IAC 441-41.28(1)

### Implementation Approach
- [x] Use federal demographic eligibility (age 18/19 matches federal)
- [x] Confirm: Federal age thresholds (18 for non-students, 19 for full-time students) match Iowa

---

## Immigration Eligibility

### State Immigration Rules
- **Citizenship requirement**: Must be a citizen, national, or qualified alien
- **Legal permanent residents**: Subject to 5-year bar from date of entry with qualified alien status
- **Refugees/Asylees**: Exempt from 5-year bar (INA Sections 207, 208)
- **Cuban/Haitian entrants**: Exempt from 5-year bar
- **Qualified alien veterans**: Exempt from 5-year bar (honorable discharge)
- **Active duty military**: Exempt from 5-year bar
- **Amerasians**: Exempt from 5-year bar
- **Human trafficking victims**: Exempt from 5-year bar
- **Iraqi/Afghan refugees**: Exempt from 5-year bar (specified public laws)
- **Battered aliens**: Exempt from 5-year bar
- **Pre-1996 residents**: Qualified aliens residing in U.S. before August 22, 1996 are exempt from 5-year bar
- **Source**: IAC 441-41.23(239B)

### Implementation Approach
- [x] Use federal immigration eligibility (state follows federal rules with standard exceptions)
- [ ] Create state-specific immigration rules

---

## Resource Limits

### Resource Thresholds
- **Applicants**: Countable resources cannot exceed **$2,000**
- **Recipients (continuing)**: Countable resources cannot exceed **$5,000**
- **Exception**: Applicant units with at least one member who was a recipient in Iowa in the month prior to the month of application use the **$5,000** limit
- **Level**: Per assistance unit (GROUP level, not per person)
- **Source**: IAC 441-41.26(239B)

### Exempt Resources
- Homestead (without regard to value)
- Household goods and personal effects (without value limit)
- One motor vehicle (unrestricted value)
- Second vehicle equity up to $4,115 per adult/working teen (adjusted annually by CPI)
- Life insurance with no cash surrender value
- Burial plots (one per person)
- Funeral contracts/burial trusts up to $1,500 per person
- Life estates
- Federal/state EITC (month received + following month)
- Individual Development Accounts (IDA) balance and earned interest
- Self-employment tools of the trade up to $10,000 equity
- Income-producing nonhomestead property when publicly advertised for sale
- SSI recipients' resources (excluded entirely)
- **Source**: IAC 441-41.26(239B)

---

## Income Eligibility Tests

### Overview: Three-Test System

Iowa FIP uses a three-test income eligibility system:
- **Applicants** must pass ALL THREE tests (Tests 1, 2, and 3)
- **Recipients (continuing)** must pass only Tests 1 and 3 (skip Test 2)
- **Source**: IAC 441-41.27(239B)

### Test 1: Gross Income Test (185% Standard of Need)

**Rule**: Countable gross nonexempt unearned and earned income must be no more than 185% of the Standard of Need (Schedule of Living Costs) for the eligible group size.

**CRITICAL**: The 185% is applied to the state's own Standard of Need, NOT to the Federal Poverty Level.

| Persons | 185% of Standard of Need |
|---------|--------------------------|
| 1 | $675.25 |
| 2 | $1,330.15 |
| 3 | $1,570.65 |
| 4 | $1,824.10 |
| 5 | $2,020.20 |
| 6 | $2,249.60 |
| 7 | $2,469.75 |
| 8 | $2,695.45 |
| 9 | $2,915.60 |
| 10 | $3,189.40 |
| Each Additional | $320.05 |

**Source**: IAC 441-41.28(2), IAC 441-41.27(239B)

**Note on implementation**: Although 185% of Standard of Need = 1.85 x SoN (verified: $365 x 1.85 = $675.25; $849 x 1.85 = $1,570.65), the 185% amounts are published as their own fixed schedule in IAC 441-41.28. Implementation can EITHER:
- Store the 185% amounts as fixed values in a parameter, OR
- Compute them as 1.85 x Standard of Need
Both approaches are valid since the published values match the 1.85 multiplier exactly.

### Test 2: Standard of Need Test (Applicants ONLY)

**Rule**: Countable net unearned and earned income must be less than the Standard of Need (Schedule of Living Costs) for the eligible group.

**Net income for Test 2** = Gross nonexempt income MINUS:
- 20% earned income deduction
- Income diversions (for ineligible dependents, court-ordered support)

**IMPORTANT**: The 58% work incentive disregard is NOT applied in Test 2.

| Persons | Standard of Need (Schedule of Living Costs) |
|---------|---------------------------------------------|
| 1 | $365 |
| 2 | $719 |
| 3 | $849 |
| 4 | $986 |
| 5 | $1,092 |
| 6 | $1,216 |
| 7 | $1,335 |
| 8 | $1,457 |
| 9 | $1,576 |
| 10 | $1,724 |
| Each Additional | $173 |

**Source**: IAC 441-41.28(2), IAC 441-41.27(239B)

### Test 3: Payment Standard Test (Determines Benefit Amount)

**Rule**: Countable net unearned and earned income, after applying allowable disregards, must be less than the Payment Standard (Schedule of Basic Needs) for the eligible group.

**Net income for Test 3** = Gross nonexempt income MINUS:
- 20% earned income deduction
- Income diversions
- 58% work incentive disregard (for recipients; NOT for initial applicants)

| Persons | Payment Standard (Schedule of Basic Needs) |
|---------|---------------------------------------------|
| 1 | $183 |
| 2 | $361 |
| 3 | $426 |
| 4 | $495 |
| 5 | $548 |
| 6 | $610 |
| 7 | $670 |
| 8 | $731 |
| 9 | $791 |
| 10 | $865 |
| Each Additional | $87 |

**Source**: IAC 441-41.28(2), IAC 441-41.27(239B)

**Note**: The Payment Standard is approximately 50.18% of the Standard of Need. Verified: $183 / $365 = 0.5014; $426 / $849 = 0.5018. However, the amounts are published as fixed dollar amounts in the IAC, not dynamically calculated. Implementation should use the fixed amounts as published.

---

## Income Deductions & Exemptions

### 20% Earned Income Deduction

- **Amount**: 20% of nonexempt monthly gross earnings
- **Level**: Per PERSON (each person in the assistance unit whose gross nonexempt earned income is considered)
- **Covers**: All work-related expenses OTHER THAN child care (taxes, transportation, meals, uniforms, etc.)
- **Applied**: To all three income tests
- **Source**: IAC 441-41.27(2)"a"

**Exact language**: "Each person in the assistance unit whose gross nonexempt earned income...is entitled to one 20 percent earned income deduction of nonexempt monthly gross earnings."

### 58% Work Incentive Disregard

- **Amount**: 58% of remaining monthly nonexempt earned income (after 20% deduction and diversions)
- **Level**: Per PERSON (applied to each person whose income must be considered)
- **NOT time-limited**: The work incentive disregard is not time-limited
- **NOT applied to initial eligibility**: "Initial eligibility is determined without the application of the work incentive disregard"
- **Applied**: Only to Test 3 (Payment Standard Test) and for continuing eligibility
- **Source**: IAC 441-41.27(2)"c"

**Exact language**: "the department shall disregard 58 percent of the total of the remaining monthly nonexempt earned income, earned as an employee or the net profit from self-employment, of each person whose income must be considered in determining eligibility and the amount of the assistance grant."

**CRITICAL for Implementation**: Use `is_tanf_enrolled` to distinguish between new applicants and existing recipients. The 58% disregard applies ONLY to recipients (continuing eligibility), not to initial applicants.

### Child Care Deduction

- **Status**: Subrule 41.27(2)"b" is **RESERVED** (no separate child care deduction currently in the rule)
- **Note**: The 20% earned income deduction is described as covering "all work-related expenses other than child care," but no separate child care deduction mechanism exists in the current IAC
- **Source**: IAC 441-41.27(2)"b" (Reserved)

### Income Diversions (Subrule 41.27(4))

Income diversions allow parent income to be diverted to meet:
1. Unmet needs of ineligible children meeting age/school attendance requirements
2. Court-ordered child support actually being paid
- Maximum diversion = difference between eligible group needs with and without the ineligible children
- **Source**: IAC 441-41.27(4)
- **Note for implementation**: Income diversions are complex and depend on the presence of ineligible household members. For a simplified implementation, this can be noted but not fully implemented.

### Child Support Treatment

- **Assigned support**: Child support collected and retained by Child Support Recovery is **exempt** as income for determining eligibility
- **$50 voluntary support exemption**: The first $50 received and retained representing a current monthly support obligation or voluntary support payment is exempt
  - **Level**: Per eligible GROUP ($50 per month per eligible group, not per person)
  - **Source**: IAC 441-41.27(239B)
- **Direct payments over $50**: Cash support payments exceeding $50/month received directly are counted as unearned income
- **Source**: IAC 441-41.27(239B)

**Exact language**: "The first $50 received and retained by an applicant or recipient which represents a current monthly support obligation or a voluntary support payment, paid by a legally responsible individual, but in no case shall the total amount exempted exceed $50 per month per eligible group."

### Income Exempt from Counting

**Completely exempt as both income and resources**:
- SNAP benefits
- USDA donated foods
- Child Nutrition Act benefits
- LIHEAP payments
- SSI recipient income (entire income of SSI recipients)
- Ineligible child income
- In-kind income
- Educational funds for students (undergraduate or graduate)
- First $50/month voluntary support (per eligible group)
- Bona fide loans
- **Source**: IAC 441-41.27(239B)

**Exempt as income only**:
- Third-party reimbursements
- Employer job expense reimbursements
- Tax refunds and retroactive SSI benefits
- Medical expense settlements
- Security deposit/utility refunds
- Funeral/burial expense portions
- Foster care/kinship payments
- Nonrecurring gifts up to $30/person/quarter
- Federal/state earned income tax credit
- PROMISE JOBS program payments
- Carpool reimbursements
- Full-time student earnings (under age 20)
- Interest and dividend income
- Census worker earnings
- **Source**: IAC 441-41.27(239B)

### Self-Employment Income

- **Net profit** = Gross self-employment income minus EITHER:
  - 40% flat cost allowance, OR
  - Actual documented expenses directly related to production
- **Allowable actual expenses**: Inventory, supplies, employee wages, shelter costs (rent/interest/taxes/utilities), equipment rental, insurance, repairs, travel, other production-related costs
- **NOT allowable**: Capital equipment purchases, loan principal payments, depreciation
- **Averaging**: Self-employment income not on regular schedule averaged over 12-month period
- **Source**: IAC 441-41.27(239B)

---

## Income Calculation Order

### For Applicants (Initial Eligibility) - All Three Tests

**Test 1 (Gross Income Test)**:
1. Calculate total gross nonexempt earned + unearned income
2. Compare to 185% of Standard of Need for group size
3. If gross income > 185% of SoN: INELIGIBLE (stop)

**Test 2 (Standard of Need Test - Applicants Only)**:
1. Start with gross nonexempt earned income
2. Subtract 20% earned income deduction (per person)
3. Subtract income diversions (if applicable)
4. Add unearned income
5. Compare to Standard of Need (Schedule of Living Costs) for group size
6. If net income >= Standard of Need: INELIGIBLE (stop)

**Test 3 (Payment Standard Test)**:
1. Start with gross nonexempt earned income
2. Subtract 20% earned income deduction (per person)
3. Subtract income diversions (if applicable)
4. **For applicants**: Do NOT apply 58% work incentive disregard
5. **For recipients**: Apply 58% work incentive disregard to remaining earned income
6. Add unearned income
7. Compare to Payment Standard (Schedule of Basic Needs) for group size
8. If net income >= Payment Standard: INELIGIBLE (stop)
9. If net income < Payment Standard: ELIGIBLE; benefit = Payment Standard - net income

### For Recipients (Continuing Eligibility) - Tests 1 and 3

**Test 1**: Same as above
**Test 3**: Same as above, but WITH 58% work incentive disregard applied

---

## Benefit Calculation

### Formula
```
FIP Grant = Payment Standard - Countable Net Income
```

Where:
- Payment Standard = Schedule of Basic Needs for the eligible group size (from IAC 441-41.28)
- Countable Net Income = income after all applicable deductions and disregards

### Calculation Steps (for recipients with earned income)
```
1. Gross earned income
2. Minus 20% earned income deduction (per working person)
3. Minus income diversions (if applicable)
4. Minus 58% work incentive disregard on remaining earned income (recipients only)
5. Equals countable earned income
6. Plus countable unearned income (minus $50 child support exemption if applicable)
7. Equals total countable net income
8. FIP Grant = Payment Standard - total countable net income
9. Round down to whole dollar
```

### Rounding Rules
- **Need standard and payment amount**: Rounded DOWN to next whole dollar when result is not a whole dollar
- **Income computations**: "The third digit to the right of the decimal point in any computation of income and hours of employment shall be dropped" (truncated, not rounded)
- **Source**: IAC 441-45.27, IAC 441-41.27(239B)

### Minimum/Maximum Amounts
- **Maximum benefit**: Payment Standard for the group size (no income = full payment standard)
- **Minimum benefit**: No specific minimum grant amount found in the regulations. The benefit is the calculated difference between payment standard and countable net income. If the difference is positive, the family receives that amount.

---

## Non-Simulatable Rules (Architecture Limitation)

### Cannot be enforced (requires history)
- **60-Month Time Limit**: Lifetime limit of 60 calendar months of FIP benefits (IAC 441-41.30). CANNOT ENFORCE in PolicyEngine's single-period architecture -- requires tracking cumulative months of assistance.
- **Hardship Exemptions**: Extensions beyond 60 months for domestic violence, lack of employability, medical conditions, etc. CANNOT TRACK -- requires history of prior months.
- **Work Requirements / PROMISE JOBS**: Mandatory participation in PROMISE JOBS program. CANNOT TRACK -- requires ongoing compliance monitoring.
- **Lump Sum Ineligibility Period**: Nonrecurring lump sum income exceeding group needs causes ineligibility for calculated number of months. CANNOT TRACK -- requires historical income data.
- **Limited Benefit Plan (LBP)**: Period of reduced or no assistance for non-compliance. CANNOT TRACK -- requires sanction history.
- **Progressive Sanctions**: Escalating penalties for non-cooperation. CANNOT TRACK -- requires violation history.

### Partially Simulatable (Time-Limited Benefits)
- **58% Work Incentive Disregard**: Applied only to recipients (continuing eligibility), not initial applicants. PARTIALLY SIMULATABLE using `is_tanf_enrolled` to differentiate.

### CAN be simulated (current point-in-time)
- Current income limits (all three tests)
- Current resource limits ($2,000 applicant / $5,000 recipient)
- Current benefit calculations (Payment Standard - Net Income)
- Current household composition / eligible group size
- Current earned income deductions (20% + 58%)
- Current child support exemption ($50/month)

---

## Implementation Approach: Federal vs State-Specific

### Use Federal Baseline
- [x] **Demographic eligibility**: Age thresholds match federal (18 for non-students, 19 for full-time students)
- [x] **Immigration eligibility**: State follows federal rules with standard exceptions
- [x] **Income sources**: Standard earned/unearned income definitions apply

### State-Specific Implementation Required
- [x] **Income eligibility tests**: Three-test system (185% SoN, SoN, Payment Standard) is state-specific
- [x] **Need standards**: State's own Schedule of Living Costs and Schedule of Basic Needs (NOT based on FPL)
- [x] **Earned income deductions**: 20% + 58% (state-specific percentages)
- [x] **Resource limits**: $2,000 applicant / $5,000 recipient (with prior-recipient exception)
- [x] **Child support exemption**: $50/month per eligible group
- [x] **Benefit calculation**: Payment Standard minus countable net income
- [x] **Rounding**: Round down to whole dollar (IAC 441-45.27)

---

## Suggested Parameter Structure

```
parameters/gov/states/ia/hhs/tanf/
  income/
    earned_income_deduction/
      rate.yaml                    # 0.20 (20%)
    work_incentive_disregard/
      rate.yaml                    # 0.58 (58%)
    child_support_exemption/
      amount.yaml                  # $50/month per group
    gross_income_limit/
      amount.yaml                  # 185% of SoN by group size (scale parameter)
  need_standard/
    amount.yaml                    # Standard of Need (Schedule of Living Costs) by group size
    additional_person.yaml         # $173 for each additional person beyond 10
  payment_standard/
    amount.yaml                    # Payment Standard (Schedule of Basic Needs) by group size
    additional_person.yaml         # $87 for each additional person beyond 10
  resources/
    applicant_limit.yaml           # $2,000
    recipient_limit.yaml           # $5,000
  self_employment/
    flat_cost_rate.yaml            # 0.40 (40% flat cost allowance)
```

---

## Income Standards Summary Table

| Persons | 185% Standard of Need (Test 1 Gross) | Standard of Need (Test 2 Net) | Payment Standard (Test 3 Net / Max Benefit) |
|---------|--------------------------------------|-------------------------------|----------------------------------------------|
| 1 | $675.25 | $365 | $183 |
| 2 | $1,330.15 | $719 | $361 |
| 3 | $1,570.65 | $849 | $426 |
| 4 | $1,824.10 | $986 | $495 |
| 5 | $2,020.20 | $1,092 | $548 |
| 6 | $2,249.60 | $1,216 | $610 |
| 7 | $2,469.75 | $1,335 | $670 |
| 8 | $2,695.45 | $1,457 | $731 |
| 9 | $2,915.60 | $1,576 | $791 |
| 10 | $3,189.40 | $1,724 | $865 |
| Each Addl | $320.05 | $173 | $87 |

**Effective Date**: July 1, 2025 (IAC adopted by IAB May 14, 2025, Volume XLVII, Number 23)
**Source**: IAC 441-41.28(2)

**Note**: These same amounts ($426 for family of 3, etc.) have been reported consistently in 2024 and prior years. The July 2025 effective date reflects the most recent codification, but the dollar amounts appear unchanged from at least 2024.

---

## Calculation Examples

### Example 1: Family of 3, No Income (Applicant)
- Test 1: $0 gross income <= $1,570.65 (185% SoN) -- PASS
- Test 2: $0 net income < $849 (SoN) -- PASS
- Test 3: $0 net income < $426 (Payment Standard) -- PASS
- **FIP Grant = $426 - $0 = $426/month**

### Example 2: Family of 3, Recipient with $800/month Earnings
(Based on Form 470-2471 example pattern)
- Gross earned income: $800
- 20% earned income deduction: $800 x 0.20 = $160
- After 20%: $800 - $160 = $640
- 58% work incentive disregard (recipient): $640 x 0.58 = $371.20
- Countable earned income: $640 - $371.20 = $268.80
- No unearned income
- Test 1: $800 gross <= $1,570.65 -- PASS
- Test 3: $268.80 < $426 -- PASS
- **FIP Grant = $426 - $268.80 = $157.20, rounded down to $157/month**

### Example 3: Family of 3, Applicant with $800/month Earnings
- Gross earned income: $800
- 20% earned income deduction: $800 x 0.20 = $160
- After 20%: $800 - $160 = $640
- Test 1: $800 gross <= $1,570.65 -- PASS
- Test 2: $640 net < $849 (SoN) -- PASS
- Test 3 (no 58% disregard for applicants): $640 net income
- $640 >= $426 (Payment Standard) -- FAIL
- **INELIGIBLE** (net income exceeds payment standard without work incentive disregard)

### Example 4: Family of 4, Recipient with $500/month Earnings + $200/month Unearned Income
- Gross earned income: $500
- Gross unearned income: $200
- 20% earned income deduction: $500 x 0.20 = $100
- After 20%: $500 - $100 = $400
- 58% work incentive disregard (recipient): $400 x 0.58 = $232
- Countable earned income: $400 - $232 = $168
- Countable unearned income: $200
- Total countable net income: $168 + $200 = $368
- Test 1: $500 + $200 = $700 gross <= $1,824.10 -- PASS
- Test 3: $368 < $495 -- PASS
- **FIP Grant = $495 - $368 = $127/month**

### Example 5: Family of 3, Recipient with $200/month Child Support
- Gross unearned income (child support received directly): $200
- $50 child support exemption (per eligible group): $200 - $50 = $150 countable
- No earned income
- Test 1: $200 gross <= $1,570.65 -- PASS
- Test 3: $150 < $426 -- PASS
- **FIP Grant = $426 - $150 = $276/month**

---

## References for Metadata

### For Parameters
```yaml
reference:
  - title: "IAC 441-41.28(2)"
    href: "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"
  - title: "IAC 441-41.27(2)"
    href: "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"
```

### For Variables
```python
reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"
# or
reference = (
    "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27",
    "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28",
)
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **Iowa Code Chapter 239B - Family Investment Program (Statute)**
   - URL: https://www.legis.iowa.gov/docs/ico/chapter/239B.pdf
   - Expected content: Complete statutory authority for FIP, definitions of "dependent child," "specified relative," "eligible group," and other key terms

2. **Iowa TANF State Plan**
   - URL: https://hhs.iowa.gov/media/17445/download?inline=
   - Expected content: Federal TANF state plan submission, may contain child support passthrough formula, benefit calculation methodology, and state option elections

3. **Iowa TANF State Plan: Attachments**
   - URL: https://hhs.iowa.gov/media/17446/download?inline=
   - Expected content: Supporting documentation for state plan

4. **Iowa HHS Employees' Manual Title 4, Chapter E - FIP Income**
   - URL: https://hhs.iowa.gov/media/3970/download
   - Expected content: Detailed income calculation procedures, worked examples, verification requirements, step-by-step budgeting worksheets. Revised December 5, 2025.

5. **Iowa HHS Employees' Manual Title 4, Chapter F - FIP Budgeting**
   - URL: https://hhs.iowa.gov/media/3971/download
   - Expected content: Detailed budgeting procedures for initial and continuing eligibility, calculation worksheets

6. **Iowa HHS Employees' Manual Title 4, Chapter C - Nonfinancial Eligibility**
   - URL: https://hhs.iowa.gov/media/3968/download
   - Expected content: Detailed nonfinancial eligibility criteria including age, relationship, residency requirements

7. **Iowa HHS Employees' Manual Title 4, Chapter D - Resources**
   - URL: https://hhs.iowa.gov/media/3969/download
   - Expected content: Detailed resource/asset counting rules, exemptions, vehicle rules

8. **Iowa HHS Employees' Manual Title 4, Chapter H - Payments and Adjustments**
   - URL: https://hhs.iowa.gov/media/3973/download
   - Expected content: Payment calculation details, adjustments, minimum grant rules if any

9. **Comm. 108 - The Family Investment Program (FIP) Informational Brochure**
   - URL: https://hhs.iowa.gov/media/6454/download
   - Expected content: Summary of FIP eligibility requirements and benefits (Rev. 06/25)

10. **Form 470-2471 - How Earnings May Change Your FIP**
    - URL: https://hhs.iowa.gov/media/4774/download
    - Expected content: Worked example showing how earnings affect FIP benefit calculation (includes child care cost example of $175)

11. **IAC 441-41.21 - Eligibility factors specific to child (PDF)**
    - URL: https://www.legis.iowa.gov/docs/iac/rule/441.41.21.pdf
    - Expected content: Complete age requirements, dependent child definition, school attendance rules

12. **IAC 441-41.22 - Eligibility factors specific to payee (PDF)**
    - URL: https://www.legis.iowa.gov/docs/ACO/rule/441.41.22.pdf
    - Expected content: Complete eligible group composition rules, specified relative definition, payee requirements

13. **IAC 441-41.28 - Need Standards (May 2025 version PDF)**
    - URL: https://www.legis.iowa.gov/docs/iac/rule/05-14-2025.441.41.28.pdf
    - Expected content: Complete need standards tables with all dollar amounts (same data as Cornell LII but in original format)

14. **Iowa Fiscal Topics - FIP**
    - URL: https://www.legis.iowa.gov/docs/publications/FTNO/1544195.pdf
    - Expected content: Legislative fiscal analysis of FIP program, may contain historical payment standard data

---

## Open Questions / Gaps

1. **Child Care Deduction Status**: IAC 441-41.27(2)"b" is RESERVED. The 20% deduction excludes child care, but no separate child care deduction mechanism exists in the current rule. The Form 470-2471 example shows child care costs being deducted, but this may be from an older version of the rules or child care may be handled through the separate Child Care Assistance (CCA) program. The Employees' Manual (PDF) may clarify this.

2. **Minimum Grant Amount**: No specific minimum grant amount was found in the regulations. The benefit is calculated as Payment Standard minus net income. If the difference is $1 or more (after rounding down), it appears the family would receive that amount. The Employees' Manual Chapter H (Payments) PDF may contain minimum grant rules.

3. **Historical Effective Dates for Current Amounts**: The current amounts (e.g., $426 for family of 3) appear to have been in effect since at least 2024, possibly much longer. The July 1, 2025 effective date on Cornell LII reflects the most recent codification. The previous version amounts may be identical. For parameter `values` entries, using `2025-07-01` as the effective date is safe based on the confirmed IAC adoption date.

4. **Third Decimal Truncation**: IAC 441-41.27 states "The third digit to the right of the decimal point in any computation of income and hours of employment shall be dropped." This means income calculations should truncate (not round) at two decimal places. Implementation should use floor/truncation to two decimal places for income calculations.

5. **Income Diversions Complexity**: Income diversions (subrule 41.27(4)) involve calculating the difference between eligible group needs with and without ineligible children. This is complex and depends on household composition details that may be simplified in the initial implementation.
