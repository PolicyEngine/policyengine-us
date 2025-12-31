# Collected Documentation

## Delaware TANF Implementation
**Collected**: December 30, 2025
**Implementation Task**: Implement Delaware Temporary Assistance for Needy Families (TANF) program

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Temporary Assistance for Needy Families (TANF) / A Better Chance (ABC) Welfare Reform Program
**Abbreviation**: TANF
**Source**: [Delaware DHSS TANF Page](https://dhss.delaware.gov/dss/tanf/)

**Variable Prefix**: `de_tanf`

---

## Regulatory Authority

### State Statute
- **Title 31 Delaware Code, Chapter 5, Section 512**
  - Authorizes Delaware Health and Social Services (DHSS) / Division of Social Services (DSS) to administer the TANF program

### State Administrative Code
- **16 Del. Admin. Code DSSM 3000** - Defining Delaware's TANF Program
  - [Cornell Law - 16 Del. Admin. Code SS 3000-3000](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-3000-3000)
- **16 Del. Admin. Code DSSM 4000** - Financial Eligibility
  - [Cornell Law - 16 Del. Admin. Code SS 4000-4008](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008)
  - [Cornell Law - 16 Del. Admin. Code SS 4000-4002](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4002)
  - [Cornell Law - 16 Del. Admin. Code SS 4000-4005](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4005)

### Federal Authority
- Personal Responsibility and Work Opportunity Reconciliation Act of 1996 (PRWORA)
- 45 CFR Part 260-265

---

## Demographic Eligibility

### Age Thresholds
- **Minor child age limit**: Under 18
- **Full-time student age limit**: 18 (must graduate before turning 19)
- **Pregnant women**: Eligible in their ninth month of pregnancy

**Source**: [Delaware DHSS TANF](https://dhss.delaware.gov/dss/tanf/)

**Implementation approach:**
- [x] Use federal demographic eligibility (age thresholds align with federal definition)
- [ ] Create state-specific age thresholds

---

## Immigration Eligibility

Delaware follows federal TANF immigration/citizenship rules.

**Implementation approach:**
- [x] Use federal immigration eligibility (state follows federal rules)
- [ ] Create state-specific immigration rules

---

## Income Eligibility Tests

Delaware uses a **two-part income test** for TANF eligibility:

### Test 1: Gross Income Test
- **Threshold**: 185% of the Standard of Need
- **Standard of Need basis**: 75% of Federal Poverty Level (FPL)
- **Applies to**: Both applicants and recipients
- **Source**: [16 Del. Admin. Code SS 4000-4008](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008)

### Test 2: Net Income Test
- **For Applicants**: Net income compared to **Payment Standard**
- **For Recipients**: Net income compared to **Standard of Need**
- **Source**: [16 Del. Admin. Code SS 4000-4008](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008)

**Quote from regulation:**
> "Applicants are defined as families who have not received assistance in at least one of the four months immediately preceding the application. For applicants, the net income is compared to the payment standard. Recipients are defined as families who have received assistance in at least one of the four months preceding the application or are current recipients. For recipients the net income is compared to the standard of need."

### Implementation Note on Applicant vs Recipient
PolicyEngine uses single-period simulation and cannot track benefit receipt history. For implementation:
- Use the **Applicant** standard (Payment Standard) as the default net income test
- This is the more restrictive test and ensures eligibility is correctly determined for new applicants

---

## Income Deductions & Exemptions

### Earned Income Deductions

#### 1. Standard Work Expense Deduction
- **Amount**: $90 per earner per month
- **Level**: Per PERSON (each working individual)
- **Source**: [16 Del. Admin. Code SS 4000-4008](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008)
- **Quote**: "Subtract the standard work deduction ($90.00)... from each earner's monthly earned income"

#### 2. $30 Plus 1/3 Disregard (First 4 Months)
- **Amount**: $30 + 1/3 of remaining earned income after $90 deduction
- **Duration**: 4 consecutive months
- **Source**: [WorkWorld - DE Earned Income Disregards](https://help.workworldapp.com/wwwebhelp/de_earned_income_disregards_tanf_and_ga.htm)

### Non-Simulatable Time-Limited Deductions (Architecture Limitation)
- **$30 Plus 1/3 Disregard**: Only applies for first 4 consecutive months of receipt [CANNOT TRACK - requires history]
- **$30 Disregard**: Applies for 8 months following the 4-month period [CANNOT TRACK - requires history]

**Implementation Note**: Since PolicyEngine cannot track months of benefit receipt, implement the base deductions ($90 work expense) without the time-limited disregards. Document that the $30 plus 1/3 and $30 disregards exist but cannot be enforced.

#### 3. Dependent Care Deduction
- **Amount per child under age 2**: Up to $200 per month
- **Amount per child age 2 and older**: Up to $175 per month
- **Amount per incapacitated adult**: Up to $175 per month
- **Level**: Per PERSON (each dependent)
- **Source**: [16 Del. Admin. Code SS 4000-4008](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008); [WorkWorld - DE Earned Income Disregards](https://help.workworldapp.com/wwwebhelp/de_earned_income_disregards_tanf_and_ga.htm)

### Unearned Income Deductions

#### Child Support Disregard
- **Amount**: First $50 of child support received per month
- **Level**: Per GROUP (per assistance unit)
- **Source**: [Delaware DHSS TANF](https://dhss.delaware.gov/dss/tanf/)
- **Quote**: "subtract... the first $50 of child support received to determine the net income"

### Calculation Order
1. Start with gross earned income
2. Subtract $90 standard work expense deduction (per earner)
3. Subtract dependent care expenses (actual costs up to limits)
4. (If recipient for 4+ months) Apply $30 plus 1/3 disregard OR $30 disregard
5. Result = Net earned income
6. Add net earned income to unearned income
7. Subtract $50 child support disregard from unearned income (if applicable)
8. Result = Total net income

---

## Income Standards by Family Size

### Effective October 1, 2025 - September 30, 2026

| Family Size | 185% of Standard of Need (Gross Limit) | Standard of Need (Recipient Net Limit) | Payment Standard (Applicant Net Limit / Max Benefit) |
|-------------|----------------------------------------|----------------------------------------|------------------------------------------------------|
| 1 | $1,811 | $979 | $201 |
| 2 | $2,446 | $1,322 | $270 |
| 3 | $3,082 | $1,666 | $338 |
| 4 | $3,719 | $2,010 | $407 |
| 5 | $4,355 | $2,354 | $475 |
| 6 | $4,989 | $2,697 | $544 |
| 7 | $5,626 | $3,041 | $612 |
| 8 | $6,262 | $3,385 | $681 |
| 9 | $6,899 | $3,729 | $750 |
| 10 | $7,535 | $4,073 | $819 |

**Source**: [Delaware DHSS TANF](https://dhss.delaware.gov/dss/tanf/)

### How Standards Are Calculated
- **Standard of Need** = 75% of Federal Poverty Level (FPL)
- **Gross Income Limit** = 185% of Standard of Need = 185% * 75% FPL = 138.75% FPL
- **Payment Standard** = Approximately 23.6% of Standard of Need (varies by family size)

**Source**: [16 Del. Admin. Code SS 4000-4008](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008); [NCCP TANF Profile - Delaware](https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Delaware.pdf)

---

## Benefit Calculation

### Grant Calculation Formula

**Source**: [16 Del. Admin. Code SS 4000-4008](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008)

**Quote from regulation:**
> "Subtract the net income from the applicable standard of need; the number calculated is the deficit. Multiply the deficit by 50%; the number calculated is the remainder. The grant is either the remainder or the payment standard whichever is less."

### Step-by-Step Calculation

1. **Calculate Deficit**:
   ```
   Deficit = Standard of Need - Net Income
   ```

2. **Calculate Remainder**:
   ```
   Remainder = Deficit * 50%
   ```

3. **Determine Grant Amount**:
   ```
   Grant = min(Remainder, Payment Standard)
   ```

### Example Calculation (Family of 3)
- Standard of Need: $1,666
- Payment Standard: $338
- Net Income: $500

```
Deficit = $1,666 - $500 = $1,166
Remainder = $1,166 * 0.50 = $583
Grant = min($583, $338) = $338
```

### Minimum/Maximum Benefits
- **Minimum Benefit**: Not specified (benefit rounds to $0 if remainder is less than $1)
- **Maximum Benefit**: Payment Standard (see table above)

### Fill-the-Gap Budgeting
Delaware used fill-the-gap budgeting on July 1, 1975. This methodology creates a "gap" between the need standard and the payment standard, paying a percentage of the deficit.

---

## Resource/Asset Limits

### General Resource Limit
- **Amount**: $10,000
- **Source**: [16 Del. Admin. Code SS 4000-4002](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4002)

### Excluded Resources
- Primary residence
- All automobiles owned by household members
- One burial plot per assistance unit member
- Funeral agreements up to $1,500 per family member
- Federal income tax refunds (including EITC) received within previous 12 months
- Education and Business Investment Accounts (EBIA) up to $5,000
- Cash value of life insurance policies
- Essential household items
- Self-employment tools and equipment
- Federal disaster assistance funds

### Transfer Penalty
- Transferring resources valued over $500 without fair market consideration results in 2-year ineligibility

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limits
- **36-month lifetime limit** on TANF benefits [CANNOT ENFORCE - requires history]
- **12-month hardship extension** available [CANNOT TRACK - requires history]

### Work History Requirements
- **30 hours/week** work or work-related activities required [CANNOT TRACK - requires ongoing monitoring]

### Time-Limited Disregards
- **$30 plus 1/3 disregard**: Only for first 4 consecutive months [CANNOT TRACK months]
- **$30 disregard**: Only for 8 months following the 4-month period [CANNOT TRACK months]

---

## Additional Program Features

### Diversion Assistance Program
- **Maximum**: Up to $1,500 lump sum
- **Purpose**: One-time assistance to prevent need for ongoing TANF
- **Payment**: Made to third-party vendors only
- **Source**: [Delaware DHSS TANF](https://dhss.delaware.gov/dss/tanf/)

**Implementation Note**: Diversion assistance is a separate program from regular TANF benefits and is not modeled in PolicyEngine.

### Child Support Pass-Through
- Recipients receive $50 supplemental payment when current child support is collected
- This is separate from the $50 disregard used in eligibility calculations
- **Source**: [16 Del. Admin. Code SS 4000-4008](https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008)

---

## Summary of Key Parameters Needed

### Income Parameters
| Parameter | Value | Source |
|-----------|-------|--------|
| Gross income test rate | 185% of Standard of Need | DSSM 4008 |
| Standard of Need rate | 75% of FPL | DSSM 4007 |
| Work expense deduction | $90 | DSSM 4008 |
| Child care max (under 2) | $200/month | DSSM 4008 |
| Child care max (2+) | $175/month | DSSM 4008 |
| Child support disregard | $50/month | DSSM 4008 |

### Benefit Parameters
| Parameter | Value | Source |
|-----------|-------|--------|
| Payment standard (family of 1) | $201 | DHSS TANF |
| Payment standard (family of 2) | $270 | DHSS TANF |
| Payment standard (family of 3) | $338 | DHSS TANF |
| Payment standard (family of 4) | $407 | DHSS TANF |
| Payment standard (family of 5) | $475 | DHSS TANF |
| Payment standard (family of 6) | $544 | DHSS TANF |
| Payment standard (family of 7) | $612 | DHSS TANF |
| Payment standard (family of 8) | $681 | DHSS TANF |
| Payment standard (family of 9) | $750 | DHSS TANF |
| Payment standard (family of 10) | $819 | DHSS TANF |
| Deficit rate | 50% | DSSM 4008 |

### Resource Parameters
| Parameter | Value | Source |
|-----------|-------|--------|
| Resource limit | $10,000 | DSSM 4002 |
| EBIA exclusion max | $5,000 | DSSM 4002 |
| Funeral agreement exclusion max | $1,500 per person | DSSM 4002 |
| Transfer penalty threshold | $500 | DSSM 4002 |

---

## References for Metadata

### For Parameters
```yaml
reference:
  - title: "16 Del. Admin. Code SS 4000-4008 - Determining Financial Eligibility and Grant Amounts in TANF"
    href: "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008"
  - title: "Delaware DHSS TANF Program"
    href: "https://dhss.delaware.gov/dss/tanf/"
```

### For Variables
```python
reference = "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008"
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **Delaware TANF State Plan 2017**
   - URL: https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/detanfstateplan2017.pdf
   - Expected content: Complete state plan with detailed program rules, waivers, and historical context

2. **Delaware TANF State Plan 2020-2022**
   - URL: https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/TANFStatePlan2020-2022.pdf
   - Expected content: Updated state plan with current program structure

3. **NCCP TANF Profile - Delaware**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Delaware.pdf
   - Expected content: Summary of Delaware TANF policies including income limits, benefit amounts, and eligibility rules

4. **Delaware October 2022 COLA Notice**
   - URL: https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/OCT2022COLA.pdf
   - Expected content: Historical standard of need and payment standard tables, self-employment deduction rates

5. **ACF Graphical Overview of State TANF Policies (July 2023)**
   - URL: https://acf.gov/sites/default/files/documents/opre/opre-graphical-overview-tanf-policies-dec2024.pdf
   - Expected content: Comparative state policy data including Delaware

---

## Implementation Approach Summary

### What to Implement
1. **Gross income eligibility** - 185% of Standard of Need (derived from 75% FPL)
2. **Net income eligibility** - Compare to Payment Standard (applicant standard)
3. **Earned income deductions** - $90 work expense, dependent care limits
4. **Unearned income deductions** - $50 child support disregard
5. **Benefit calculation** - 50% of deficit, capped at payment standard
6. **Resource eligibility** - $10,000 limit with exclusions

### What NOT to Implement (Cannot Simulate)
1. Time limits (36-month lifetime)
2. Work participation requirements (30 hours/week)
3. $30 plus 1/3 disregard (time-limited)
4. $30 disregard (time-limited)
5. Diversion assistance program
6. Applicant vs. recipient distinction (use applicant standard)
