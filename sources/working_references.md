# Collected Documentation

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Family Investment Program (FIP)
**State**: Iowa (IA)
**Abbreviation**: FIP
**Source**: Iowa Code Section 239B

**Variable Prefix**: `ia_fip`
**Parameter Path**: `gov.states.ia.dhs.tanf`

---

## Iowa TANF (FIP - Family Investment Program) Implementation
**Collected**: 2026-01-15 (Updated)
**Implementation Task**: Implement Iowa FIP cash assistance program with eligibility tests and benefit calculations

### Source Information

#### Primary Legal Sources
- **Title**: Iowa Code Chapter 239B - Family Investment Program
- **Citation**: Iowa Code Section 239B
- **URL**: https://www.legis.iowa.gov/docs/ico/chapter/239B.pdf
- **Effective Date**: Current

- **Title**: Iowa Administrative Code 441-41.27(239B) - Income
- **Citation**: 441 IAC 41.27(239B)
- **URL**: https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27
- **Effective Date**: 7/1/2025

- **Title**: Iowa Administrative Code 441-41.28(239B) - Need Standards
- **Citation**: 441 IAC 41.28(239B)
- **URL**: https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28
- **Effective Date**: 7/1/2025

- **Title**: Iowa Administrative Code 441-41.26(239B) - Resources
- **Citation**: 441 IAC 41.26(239B)
- **URL**: https://www.legis.iowa.gov/docs/iac/rule/441.41.26.pdf
- **Effective Date**: Current

#### Federal TANF Regulations
- **Title**: 45 CFR Part 260 - General TANF Provisions
- **URL**: https://www.ecfr.gov/current/title-45/subtitle-B/chapter-II/part-260
- **Title**: 45 CFR Part 261 - Ensuring That Recipients Work
- **URL**: https://www.ecfr.gov/current/title-45/subtitle-B/chapter-II/part-261

### Key Rules and Thresholds

#### Resource Limits
- Applicant families: $2,000
- Recipient families (member received FIP in prior month): $5,000
- Vehicle equity exclusion: $3,959 per vehicle per adult/working teen (adjusted annually as of July 1)

#### Excluded Resources (Not Counted)
- Homestead property
- Non-homestead property listed for sale at fair market value or producing income
- Household goods and personal effects
- Life insurance with zero cash value
- Burial plots (one per household member) and funeral trusts (up to $1,500 per person)
- Tools and capital assets for self-employment (up to $10,000 equity)
- Inventory and supplies for self-employment
- Individual Development Account (IDA) balances (full balance excluded)
- Educational/training assistance funds
- SSI recipient resources
- Current monthly income
- Loans and inaccessible resources
- Child support payments (up to $50 monthly)
- Medical expense reserves from lump-sum payments

#### Income Eligibility Tests
1. **Test 1**: Gross income <= 185% of Standard of Need
2. **Test 2**: Net income (after 20% earned income deduction) < Standard of Need (applicants only)
3. **Test 3**: Net income (after work incentive) < Payment Standard

#### Income Deductions
- **20% Earned Income Deduction**: Applied to gross nonexempt earned income (covers taxes, transportation, meals, uniforms, other work expenses)
- **58% Work Incentive Disregard**: Applied after 20% deduction to remaining earned income (not time-limited)

#### Time Limits
- 60-month lifetime limit on benefits
- Hardship exemptions available for 6-month extensions
- Hardship criteria: domestic violence, lack of employability, lack of suitable child care, medical/mental health issues, housing situations, substance abuse issues, child requiring parent at home
- Extension request can be filed starting in month 59
- SSI exemption: 60-month limit does not apply if child lives with one parent on SSI or both parents on SSI

### Payment Standards (Effective 7/1/2025)

#### Schedule of Living Costs (100% Standard of Need)

| Family Size | Monthly Amount |
|-------------|----------------|
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
| Each additional | +$173 |

#### 185% of Standard of Need (Gross Income Limit - Test 1)

| Family Size | Monthly Amount |
|-------------|----------------|
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
| Each additional | +$320.05 |

#### Schedule of Basic Needs (Payment Standard)

| Family Size | Monthly Amount |
|-------------|----------------|
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
| Each additional | +$87 |

### Exempt Income (Complete List)

The following income is NOT counted for FIP eligibility:

**Government Benefits**
- SNAP (Food Stamp) benefits
- SSI recipient income (when not in eligible group)
- Earned Income Tax Credit (EITC) - federal and state
- Low-Income Home Energy Assistance (LIHEAP)
- WIC program benefits
- Foster care/kinship caregiver payments
- Rent supplements from governmental agencies
- Disaster and emergency assistance
- Indian tribal judgment funds
- Retroactive SSI benefits and payments
- General assistance from county funds (non-basic need or emergency)

**Employment and Training**
- PROMISE JOBS payments
- Training allowances (Department of the Blind, JTPA, Vocational Rehabilitation)
- Food Stamp Employment and Training allowances
- Car pool payments
- Job-related reimbursements
- VISTA volunteer payments
- Incentive allowances from Work Force Investment Project
- AmeriCorps educational awards

**Education**
- Educational/training assistance and financial aid
- Earnings of students age 19 or younger in full-time school (high school or equivalent)

**Child Support**
- Up to $50 of current monthly support paid by legally responsible person

**Other**
- Food from home production
- Food coupons value and USDA commodities value
- Income in-kind
- Gifts of $30 or less per person per calendar quarter
- Loans and bona fide loans
- Income tax refunds
- Vendor payments
- Interest or dividend payments
- Third-party reimbursements
- Medical expense settlements
- Individual Development Account (IDA) deposits
- Refunds from rent or utility deposits
- Terminated income of retrospectively budgeted households (when requirements met)
- Veterans benefits under Aid and Attendance program
- Census worker earnings
- Family Support Subsidy payments

### Self-Employment Income Rules

- **Net Profit Calculation**: Either 40% of gross income deducted OR actual documented expenses
- **Irregular Self-Employment**: Averaged over 12-month period
- **Work Hours Calculation for Self-Employed**: Actual gross income less business expenses divided by federal minimum wage

### Lump Sum Income Treatment

- Nonrecurring lump sum amounts create ineligibility period
- Ineligibility period calculated by dividing lump sum by standard of need
- Period can be reduced if:
  - Living costs increase
  - Funds spent on medical services
  - Funds spent on home repairs
  - Funds spent on funeral expenses

### Income Budgeting Rules

- **Weekly Income**: Multiply by 4 regardless of actual payment frequency
- **Biweekly Income**: Multiply by 2 regardless of actual payment frequency
- **Prospective Budgeting**: Projection based on best estimate of future income using income from 30 days before interview
- **Variable Income**: Average all instances received in the period

### Calculation Formulas

#### Income Eligibility

```python
# Test 1: Gross Income Test (185% Standard of Need)
gross_income_limit = standard_of_need * 1.85
passes_test_1 = gross_income <= gross_income_limit

# Test 2: Net Income Test (Standard of Need) - Applicants Only
earned_income_deduction = gross_earned_income * 0.20
net_income_test_2 = gross_income - earned_income_deduction
passes_test_2 = net_income_test_2 < standard_of_need

# Test 3: Payment Standard Test
work_incentive_disregard = (gross_earned_income - earned_income_deduction) * 0.58
countable_net_income = gross_income - earned_income_deduction - work_incentive_disregard
passes_test_3 = countable_net_income < payment_standard
```

#### Benefit Calculation

```python
# FIP Benefit = Payment Standard - Countable Net Income
fip_benefit = max(payment_standard - countable_net_income, 0)
```

#### Complete Benefit Formula

```python
def calculate_fip_benefit(gross_earned_income, gross_unearned_income, family_size):
    # Get parameters
    standard_of_need = get_standard_of_need(family_size)
    payment_standard = get_payment_standard(family_size)
    gross_income_limit = standard_of_need * 1.85

    gross_income = gross_earned_income + gross_unearned_income

    # Test 1: 185% Gross Income Test
    if gross_income > gross_income_limit:
        return 0

    # 20% Earned Income Deduction
    earned_income_deduction = gross_earned_income * 0.20

    # Test 2: Standard of Need Test (for applicants)
    net_income_after_20 = gross_income - earned_income_deduction
    if net_income_after_20 >= standard_of_need:
        return 0  # Applicant ineligible

    # 58% Work Incentive Disregard
    remaining_earned = gross_earned_income - earned_income_deduction
    work_incentive = remaining_earned * 0.58

    # Test 3: Payment Standard Test
    countable_net_income = gross_income - earned_income_deduction - work_incentive
    if countable_net_income >= payment_standard:
        return 0

    # Calculate benefit
    return payment_standard - countable_net_income
```

### Example Calculation

**Family of 3 with one employed parent earning $800/month gross:**

1. **Test 1 (185% Gross Income Test):**
   - Gross Income: $800
   - 185% Standard of Need for 3: $1,570.65
   - $800 < $1,570.65 - PASS

2. **Test 2 (Standard of Need Test - Applicant Only):**
   - Gross Income: $800
   - 20% Earned Income Deduction: $800 x 0.20 = $160
   - Net Income: $800 - $160 = $640
   - Standard of Need for 3: $849
   - $640 < $849 - PASS (eligible for work incentive)

3. **Test 3 (Payment Standard Test):**
   - Net Income from Test 2: $640
   - 58% Work Incentive: $640 x 0.58 = $371.20
   - Countable Net Income: $640 - $371.20 = $268.80
   - Payment Standard for 3: $426
   - $268.80 < $426 - PASS

4. **Benefit Calculation:**
   - FIP Benefit = $426 - $268.80 = $157.20/month

### Special Cases and Exceptions

#### Eligible Group
- Must include child, eligible siblings, and natural/adoptive parents when living together
- Nonparental relatives optional (at relative's request)
- Incapacitated stepparents may be included
- Exception: Parent-only case when only child receives SSI

#### Two-Parent Families
- No 100-hour rule (eliminated under FIP)
- Both parents must participate in PROMISE JOBS unless one meets exemption criteria

#### Caretaker Relative Rules
- Unmarried specified relative under 19 living with parents: needs included with parent(s)
- Nonparental relative as caretaker: children considered separate eligible group

#### Temporary Absences
- Education/training: remain in group if expected to return upon completion
- Medical institutions: remain in group if expected return within 12 months
- Other reasons: remain in group if expected return within 3 months

#### Work Requirements (PROMISE JOBS)
- Required unless exempt
- Exemptions:
  - SSI/SSDI recipients (due to own disability)
  - Aliens not listed under 8 USC Section 1641
  - Persons determined disabled and unable to participate
  - Children under age 16 who are not parents
  - Students 16-19 (non-parents) attending school full-time
  - Parent/relative of child under 6 months who personally provides care (one exemption per case)
  - Person working 30+ hours/week in unsubsidized employment at initial determination
- Limited Benefit Plan for non-compliance:
  - First LBP: benefits reduced then terminated
  - Subsequent LBPs: 6-month minimum termination
  - Must complete 20 hours of employment/similar activity to restart

#### Federal TANF Work Requirements (45 CFR 261)
- 30 hours/week minimum for overall rate (20 hours from core activities)
- Single parent with child under 6: 20 hours/week minimum
- Community service required if received assistance for 2 months (unless exempt or engaged in work)

### References for Metadata

```yaml
# For parameters:
reference:
  - title: "Iowa Administrative Code 441-41.28(239B) - Need Standards"
    href: "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"
```

```python
# For variables:
reference = "441 IAC 41.27(239B)"
documentation = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"
```

### Implementation Notes

1. **Parameter Files Needed**:
   - `gov/states/ia/hhs/tanf/income/standard_of_need.yaml` - Schedule of Living Costs by family size
   - `gov/states/ia/hhs/tanf/income/gross_income_limit_percent.yaml` - 185% multiplier
   - `gov/states/ia/hhs/tanf/income/earned_income_deduction.yaml` - 20% deduction rate
   - `gov/states/ia/hhs/tanf/income/work_incentive_disregard.yaml` - 58% disregard rate
   - `gov/states/ia/hhs/tanf/benefit/payment_standard.yaml` - Schedule of Basic Needs by family size
   - `gov/states/ia/hhs/tanf/eligibility/resource_limit_applicant.yaml` - $2,000
   - `gov/states/ia/hhs/tanf/eligibility/resource_limit_recipient.yaml` - $5,000

2. **Variable Files Needed**:
   - `ia_fip.py` - Main benefit calculation
   - `ia_fip_eligible.py` - Overall eligibility
   - `ia_fip_gross_income_eligible.py` - Test 1
   - `ia_fip_net_income_eligible.py` - Test 2 (applicants)
   - `ia_fip_payment_standard_eligible.py` - Test 3
   - `ia_fip_countable_earned_income.py` - Earned income after deductions
   - `ia_fip_countable_unearned_income.py` - Unearned income
   - `ia_fip_payment_standard.py` - Payment standard by family size
   - `ia_fip_standard_of_need.py` - Standard of need by family size

3. **Entity**: SPMUnit (consistent with other state TANF implementations)

4. **Definition Period**: YEAR (consistent with other state TANF implementations)

5. **Key Differences from Federal TANF**:
   - Iowa uses 58% work incentive (vs. typical 50%)
   - Iowa has separate applicant ($2,000) and recipient ($5,000) resource limits
   - Iowa eliminated 100-hour rule for two-parent families

---
