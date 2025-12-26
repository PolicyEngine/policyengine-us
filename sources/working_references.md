# Collected Documentation

## New Mexico Works (NM Works) - TANF Implementation
**Collected**: December 23, 2025
**Implementation Task**: Implement New Mexico's TANF program (NM Works) including eligibility determination and benefit calculation

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: New Mexico Works (NM Works or NMW)
**Abbreviation**: NMW
**Source**: 8.102.100 NMAC - "New Mexico Works (NMW) means the program implemented under NMWA for the purpose of providing cash assistance as a support service to enable and assist parents to participate in employment."

**Variable Prefix**: `nm_tanf`

**Administering Agency**: New Mexico Health Care Authority (HCA)
- Note: Previously administered by Human Services Department (HSD), which was reorganized

---

## Regulatory Authority

### State Regulations
- **Primary Regulation**: 8.102 NMAC - Cash Assistance Programs (New Mexico Works)
  - 8.102.100 NMAC - General Provisions/Definitions
  - 8.102.400 NMAC - Eligibility Determination
  - 8.102.410 NMAC - Recipient Requirements (Citizenship, Work Requirements)
  - 8.102.420 NMAC - Benefit Group Composition
  - 8.102.500 NMAC - Eligibility Policy - General Information
  - 8.102.501 NMAC - Transition Bonus Program (TBP)
  - 8.102.510 NMAC - Resources/Property
  - 8.102.520 NMAC - Income
  - 8.102.620 NMAC - Benefit Determination

### State Statutes
- New Mexico Statutes Annotated 1978, Chapter 27, Articles 1 and 2
- New Mexico Works Act of 1998 (NMWA)

### Federal Authority
- Title IV-A of the Social Security Act
- Personal Responsibility and Work Opportunity Reconciliation Act (PRWORA) of 1996

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limit
- **60-Month Lifetime Limit**: "NMW/TANF cash assistance shall not be provided to or for an adult or a minor head of household for more than 60 months during the individual's lifetime."
- Source: 8.102.410.17 NMAC
- **CANNOT ENFORCE** - requires tracking benefit history across periods

### Hardship Extensions
- Up to 20% of TANF participants may receive extensions beyond 60 months
- Based on: disability, domestic violence, age 60+, pending SSI applications
- **CANNOT TRACK** - requires history of months received

### Transitional Benefit Program (TBP)
- 18-month lifetime limit
- **CANNOT TRACK** - requires history of TBP months

---

## Demographic Eligibility

### Dependent Child Age Thresholds

| Category | Age Threshold | Source |
|----------|---------------|--------|
| Minor child | Under 18 years | 8.102.100.7(R) NMAC |
| High school student (18) | Age 18 and enrolled in high school | 8.102.100.7(R) NMAC |
| Special education | Ages 18-22 with current IEP | 8.102.420.8 NMAC |

**Legal Citation**: 8.102.100.7(R) NMAC defines "dependent child" as:
> "a natural child, adopted child, stepchild or ward that is: (a) 17 years of age or younger; or (b) 18 years of age and is enrolled in high school; or (c) between 18 and 22 years of age and is receiving special education services regulated by the New Mexico Public Education Department with a current valid Individual Education Plan (IEP)."

### Pregnant Women
- Pregnant women are eligible as specified relatives
- Source: 8.102.400 NMAC

### Caretaker Relative Requirements
- Must be within the 5th degree of relationship to the dependent child
- Must be the primary caretaker for the child
- Must reside in the home with the dependent child
- Source: 8.102.400 NMAC

**Implementation Approach:**
- [x] Use federal demographic eligibility baseline for age 18 threshold
- [ ] Create state-specific for age 18-22 special education provision if needed
- [x] Follow federal caretaker relative definition

---

## Immigration Eligibility

### Eligible Categories

**U.S. Citizens**: Natural-born, naturalized, or born in U.S. territories

**Non-Citizen U.S. Nationals**: Persons from American Samoa, Swains Island, or Northern Mariana Islands

**Qualified Non-Citizens** (8.102.410.10 NMAC):
1. Lawfully admitted permanent residents (LPRs)
2. Asylees under INA Section 208
3. Refugees admitted under INA Section 207
4. Parolees (admitted for at least one year under INA Section 212)
5. Individuals with deportation withheld under INA Sections 241(b)(3) or 243(h)
6. Those granted conditional entry (pre-April 1, 1980)
7. Cuban or Haitian entrants under the Refugee Education Assistance Act of 1980
8. Trafficking victims certified by HHS
9. COFA migrants (Compact of Free Association - Micronesia, Marshall Islands, Palau)

**Additional Eligibility Pathways**:
- Entry before August 22, 1996, with qualified status
- Five-year residence requirement for post-August 22, 1996 entrants
- 40 qualifying quarters under Social Security
- Veterans with honorable discharge or active duty members
- Family members of qualifying veterans
- Domestic violence exception

**State-Funded Aliens**:
- Qualified non-citizens who entered on/after August 22, 1996
- Eligible for state-funded TANF without the 5-year waiting period
- Source: 8.102.410.10(B) NMAC

**Implementation Approach:**
- [x] Use federal immigration eligibility baseline (state follows federal rules with state-funded option)

---

## Income Eligibility Tests

### Test 1: Gross Income Test (85% Test)

**Rule**: The countable gross income of the benefit group cannot exceed 85% of the Federal Poverty Guidelines for the benefit group size.

**Source**: 8.102.520.11 NMAC - "For the benefit group to be eligible, the countable gross income available to the benefit group cannot exceed eighty-five percent of the federal poverty guidelines for the size of the benefit group."

**Gross Income Limits (85% FPL) - October 2024 through September 2025**:

| Benefit Group Size | Monthly Limit |
|--------------------|---------------|
| 1 | $1,067 |
| 2 | $1,448 |
| 3 | $1,829 |
| 4 | $2,210 |
| 5 | $2,592 |
| 6 | $2,972 |
| 7 | $3,353 |
| 8 | $3,735 |
| Each additional | +$382 |

**Note**: These limits are revised annually each October based on Federal Poverty Guidelines.

**Implementation**: Store as 0.85 rate multiplied by FPL, not fixed dollar amounts.

### Test 2: Net Income Test (Standard of Need)

**Rule**: The countable net income (after deductions) must be less than the Standard of Need for the benefit group size.

**Source**: 8.102.520.11 NMAC - "For the benefit group to be eligible, the countable net income must be less than the standard of need applicable to the size of the benefit group."

---

## Income Deductions and Exemptions

### Earned Income Deductions (Work Incentive)

**Source**: 8.102.520.12 NMAC

| Recipient Type | Deduction Formula |
|----------------|-------------------|
| Single-parent benefit group (parent) | $125 + 50% of remainder |
| Two-parent benefit group (each parent) | $225 + 50% of remainder |
| Other benefit group member (not parent) | $125 + 50% of remainder |
| Non-benefit group member (deemed income) | $125 flat deduction |

**Calculation Example (Single Parent with $800 gross earnings)**:
1. Start with gross earnings: $800
2. Subtract $125: $800 - $125 = $675
3. Subtract 50% of remainder: $675 - ($675 * 0.50) = $675 - $337.50 = $337.50
4. Countable earned income: $337.50

### Child Care Deductions

**Source**: 8.102.520.12 NMAC

| Child Age | Maximum Monthly Deduction |
|-----------|---------------------------|
| Under age 2 | $200 |
| Age 2 or older | $175 |

**Note**: Deducted from earnings remaining after work incentive deduction.

### Child Support Disregard and Passthrough

**Source**: 8.102.520.10 NMAC, HCA announcement January 2023

**Disregard**: First $50 of child support received by the benefit group is disregarded (not counted as income).

**Passthrough** (Effective January 1, 2023):
- 1 child: $100
- 2 or more children: $200

**Implementation**: Both disregard ($50) and passthrough amounts reduce countable income.

### Income Exclusions (Not Counted)

**Source**: 8.102.520.10 NMAC

The following income sources are excluded from countable income:
- Medicaid and SNAP benefits
- Supplemental Security Income (SSI)
- Government-subsidized housing or housing payments
- Educational payments made directly to institutions
- Subsidized child care
- Earned income of children 17 and younger (not heads of household)
- Emergency one-time payments
- Job-related expense reimbursements
- Utility assistance programs (LIHEAP)
- Guaranteed basic income (private-funded or mixed-funded)
- Universal basic income (private-funded or mixed-funded)

### Self-Employment Income

**Source**: 8.102.520.9 NMAC

- Gross profit requiring "substantial effort on a continuous basis"
- Averaged over the period it's intended to cover (typically 12 months)
- If business operated less than one year, averaged over actual operation period

**Allowable Business Expenses**:
- Materials and supplies
- Business travel (capped at $0.25/mile unless actual costs higher)
- Business taxes
- Equipment/tool rentals
- Business location rent
- Principal payments on income-producing assets
- Interest on income-producing property purchases

**Non-Allowable Expenses**:
- Depreciation
- Personal entertainment
- Personal commuting

---

## Resource/Asset Limits

**Source**: 8.102.510 NMAC

| Resource Type | Limit |
|---------------|-------|
| Liquid Resources | $1,500 |
| Non-Liquid Resources | $2,000 |

### Liquid Resources Definition
Cash or financial instruments easily convertible to cash:
- Savings accounts
- Checking accounts
- Stocks, bonds, mutual funds
- Promissory notes, mortgages
- Life insurance cash values

### Non-Liquid Resources Definition
Assets not readily convertible to cash:
- Real property (land, buildings)
- Personal property (equipment, vehicles)

### Key Exempt Resources
- Primary residence and reasonable surrounding land
- Vehicles used for transportation to work or daily living
- Specially equipped vehicles for disabled individuals
- Burial plots (one per person)
- Funeral agreements (unlimited)
- Work-related equipment (up to $1,000 per individual)
- Individual Development Accounts (IDAs)
- Livestock
- Grazing permits currently in use

---

## Income Standards (Standard of Need / Payment Standard)

**Source**: 8.102.500.8 NMAC

The Standard of Need is based on the number of participants in the benefit group and allows for a financial standard and basic needs (food, clothing, shelter, utilities, personal items, household supplies).

### Payment Standard by Benefit Group Size (Effective August 2023 - 23% increase)

| Benefit Group Size | Monthly Payment Standard |
|--------------------|--------------------------|
| 1 | $327 |
| 2 | $439 |
| 3 | $549 |
| 4 | $663 |
| 5 | $775 |
| 6 | $887 |
| 7 | $999 |
| 8 | $1,134 |
| Each additional | +$111 (approximately) |

**Source for 23% increase**: HCA announcement September 1, 2023 - "State announces a 23 percent increase in cash assistance for low-income New Mexico families" - effective August 2023, first increase since 2011.

**Historical Note**: Prior to August 2023, family of 4 received $539; after increase, $663.

---

## Benefit Calculation

**Source**: 8.102.620 NMAC

### Formula

```
Benefit = Payment Standard - Net Countable Income
```

### Calculation Steps

1. **Calculate Gross Income**
   - Add all earned income
   - Add all unearned income
   - Apply income exclusions

2. **Apply Gross Income Test**
   - Compare gross income to 85% FPL limit for benefit group size
   - If gross income >= limit, ineligible

3. **Calculate Net Countable Earned Income**
   - Start with gross earned income
   - Subtract work incentive deduction ($125/$225 + 50% of remainder)
   - Subtract child care costs (up to $200 under 2, $175 age 2+)

4. **Calculate Net Countable Unearned Income**
   - Start with gross unearned income
   - Subtract child support disregard ($50)
   - Apply child support passthrough ($100 for 1 child, $200 for 2+ children)

5. **Calculate Total Net Countable Income**
   - Add net countable earned income + net countable unearned income

6. **Apply Net Income Test**
   - Compare net countable income to Standard of Need
   - If net income >= Standard of Need, ineligible

7. **Calculate Benefit**
   - Benefit = Standard of Need - Net Countable Income
   - Round down (remove cents)

### Minimum Benefit
- No explicit minimum benefit specified
- If calculation results in $0 or negative, no benefit is issued

### Sanctions
Benefits may be reduced for:
- First-level sanction: 25% of standard of need
- Second-level sanction: 50% of standard of need (after 3 months non-compliance)
- Third-level sanction: Case closure for minimum 6 months

---

## Additional Benefits

### School Clothing Allowance

**Source**: 8.102.620 NMAC

| Month | Amount per School-Age Child |
|-------|----------------------------|
| August | $100 |
| January | $50 |

### Diversion Payment

**Source**: 8.102.100 NMAC

A one-time payment in lieu of ongoing cash assistance:

| Household Size | Diversion Payment Amount |
|----------------|--------------------------|
| 1-3 persons | $1,500 |
| 4+ persons | $2,500 |

**Limitations**: Limited to two times in an applicant's 60-month lifetime limit.

---

## Transitional Benefit Program (TBP)

**Source**: 8.102.501 NMAC

### Purpose
Provides limited-duration cash assistance to encourage NMW families to maintain employment after leaving cash assistance.

### Benefit Amount
$200/month (fixed, non-prorated)

### Eligibility Requirements
- Left NMW cash assistance program
- Engaged in paid employment minimum 30 hours/week
- Gross income below 150% FPL
- Received NMW for at least 3 months (including 1 of last 3 months)
- Not reached 60-month TANF limit
- Not reached 18-month TBP limit

### Duration
Maximum 18 months lifetime

**Note**: Cannot be fully simulated due to lifetime tracking requirement.

---

## Support Services Only Eligibility

**Source**: 8.102.500.8 NMAC

Benefit groups not receiving cash assistance but with gross income less than 100% FPL may be eligible to receive support services.

**100% FPL Limits** (for support services only):

| Benefit Group Size | Monthly Limit |
|--------------------|---------------|
| 1 | $1,255 |
| 2 | $1,703 |
| 3 | $2,152 |
| 4 | $2,600 |
| 5 | $3,049 |
| 6 | $3,497 |
| 7 | $3,946 |
| 8 | $4,394 |

---

## Key References for Implementation

### Parameters (metadata reference format)

```yaml
reference:
  - title: 8.102.520.12 NMAC - Earned Income Deductions
    href: https://www.srca.nm.gov/parts/title08/08.102.0520.html
  - title: 8.102.500.8 NMAC - Eligibility Policy
    href: https://www.srca.nm.gov/parts/title08/08.102.0500.html
```

### Variables (reference format)

```python
reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
```

---

## Summary of Implementation Parameters Needed

### Income Parameters
- `income/gross_limit/rate.yaml` - 0.85 (85% of FPL)
- `income/deductions/work_incentive/single_parent/amount.yaml` - $125
- `income/deductions/work_incentive/two_parent/amount.yaml` - $225 per parent
- `income/deductions/work_incentive/disregard_rate.yaml` - 0.50 (50%)
- `income/deductions/child_care/under_2/max.yaml` - $200
- `income/deductions/child_care/age_2_plus/max.yaml` - $175
- `income/child_support/disregard/amount.yaml` - $50
- `income/child_support/passthrough/one_child.yaml` - $100
- `income/child_support/passthrough/multiple_children.yaml` - $200

### Resource Parameters
- `resources/limit/liquid.yaml` - $1,500
- `resources/limit/non_liquid.yaml` - $2,000

### Payment Standard Parameters
- `payment_standard/amount.yaml` - Bracketed by household size (1-8+)

### Eligibility Parameters
- `eligibility/age_threshold/minor_child.yaml` - 18
- `eligibility/age_threshold/special_education_max.yaml` - 22

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **TANF State Plan 2024-2026**
   - URL: https://www.hca.nm.gov/wp-content/uploads/TANF-Final-State-Plan-2024-to-2026.pdf
   - Expected content: Complete state plan including benefit calculation methodology, program goals, policy changes
   - Key sections: Benefit schedules, income calculations, program statistics

2. **Income Eligibility Guidelines for SNAP and Financial Assistance (October 2024-September 2025)**
   - URL: https://www.hca.nm.gov/wp-content/uploads/Income-Eligibility-Guidelines-for-SNAP-and-Financial-Assistance-October-12024-September-30-2025.pdf
   - Expected content: Complete income limit tables, payment standards by household size
   - Key sections: TANF income limits, payment standard tables

3. **TANF Profile - New Mexico (NCCP August 2024)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-New-Mexico.pdf
   - Expected content: Summary of program rules, benefit levels, eligibility criteria
   - Key sections: Benefit amount tables, comparison to FPL

4. **5 Critical Reforms for New Mexico's TANF Program**
   - URL: https://www.nmlegis.gov/handouts/LHHS%20112822%20Item%2016%20TANF%20Policy.pdf
   - Expected content: Policy analysis, historical benefit levels, reform recommendations

---

## Sources

### Primary Regulatory Sources (NMAC)
- [8.102.100 NMAC - General Provisions](https://srca.nm.gov/parts/title08/08.102.0100.html)
- [8.102.400 NMAC - Eligibility Determination](https://www.srca.nm.gov/parts/title08/08.102.0400.html)
- [8.102.410 NMAC - Recipient Requirements](https://www.srca.nm.gov/parts/title08/08.102.0410.html)
- [8.102.420 NMAC - Benefit Group Composition](https://www.srca.nm.gov/parts/title08/08.102.0420.html)
- [8.102.500 NMAC - Eligibility Policy](https://www.srca.nm.gov/parts/title08/08.102.0500.html)
- [8.102.501 NMAC - Transitional Benefit Program](https://www.srca.nm.gov/parts/title08/08.102.0501.html)
- [8.102.510 NMAC - Resources/Property](https://www.srca.nm.gov/parts/title08/08.102.0510.html)
- [8.102.520 NMAC - Income](https://www.srca.nm.gov/parts/title08/08.102.0520.html)
- [8.102.620 NMAC - Benefit Determination](https://www.srca.nm.gov/parts/title08/08.102.0620.html)

### State Agency Sources
- [New Mexico Health Care Authority - TANF Program](https://www.hca.nm.gov/lookingforassistance/temporary_assistance_for_needy_families/)
- [HCA - Income Eligibility Guidelines](https://www.hca.nm.gov/lookingforinformation/income-eligibility-federal-poverty-level-guidelines/)
- [HCA - 23% Cash Assistance Increase Announcement (Sept 2023)](https://www.hca.nm.gov/2023/09/01/state-announces-a-23-percent-increase-in-cash-assistance-for-low-income-new-mexico-families/)
- [HCA - Child Support Passthrough Increase (Jan 2023)](https://www.hca.nm.gov/2023/01/10/human-services-department-to-pass-through-more-money-to-low-income-families/)
- [HCA - Transition Bonus Program Reinstatement (June 2023)](https://www.hca.nm.gov/2023/06/01/human-services-department-announces-the-cash-assistance-transition-bonus-program-is-back/)

### Federal Sources
- [45 CFR Part 260 - TANF General Provisions](https://www.ecfr.gov/current/title-45/part-260)
- [42 USC 601-619 - TANF Block Grant](https://www.law.cornell.edu/uscode/text/42/chapter-7/subchapter-IV/part-A)
