# Indiana TANF - Eligibility Requirements

## Legal Authority

- **Indiana Code**: IC 12-14-1 (Chapter 1: Eligibility and Application)
- **Administrative Code**: 470 IAC 10.3-3 (Nonfinancial Eligibility Requirements)
- **Administrative Code**: 470 IAC 10.3-4 (Fiscal Eligibility Requirements)
- **Policy Manual**: Chapter 2400 (Nonfinancial Eligibility)

## Demographic Eligibility

### Family Composition

**TANF Assistance Group** (IC 12-14-1-0.5):
> "TANF assistance group" means persons whose income, resources, or needs are considered in determining eligibility for assistance under TANF and the amount of TANF assistance for which the persons are eligible.

**Eligible Individuals:**
- Child under age 18 living with parent(s) or relative
- Pregnant woman (if at least 6 months pregnant and meets income requirements)
- Parent or caretaker relative of eligible child

**Specified Relatives:**
- Parent
- Grandparent
- Aunt
- Uncle

**Source**:
- Indiana Code IC 12-14-1-0.5
- FSSA website: https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/

### Age Requirements

**Children:**
- Must be under age 18
- Federal TANF baseline typically uses age 18 (19 for full-time students)
- Indiana appears to follow federal baseline

**Adults:**
- No upper age limit for parents/caretaker relatives
- Subject to 24-month lifetime limit on adult benefits

**Implementation**: Use federal `is_demographic_tanf_eligible` variable.

### Citizenship and Immigration

**Requirements** (470 IAC 10.3-3):
- Must satisfy citizenship/immigration status requirements
- Indiana follows federal TANF rules for immigration eligibility

**Implementation**: Use federal `is_citizen_or_legal_immigrant` variable.

### Residency

**Indiana Residency** (Policy Manual Chapter 2400):
> "Resident means one who is living in Indiana voluntarily with the intention of making a home here and not for a temporary purpose."

**Requirements**:
- Must be living in Indiana
- Must have intention to make home in Indiana
- Not present for temporary purpose only

**Source**:
- 470 IAC 10.3-3-10 (Indiana residency requirements)
- Policy Manual Chapter 2400: https://www.in.gov/fssa/dfr/files/2400.pdf

### Social Security Number

**Requirements** (Policy Manual Chapter 2400):
- Must provide Social Security number for all household members
- Must verify Social Security coverage under individual's own account number
- Part of nonfinancial eligibility requirements

**Source**: Policy Manual Chapter 2400

## Financial Eligibility

### Income Tests

Indiana TANF uses **multiple income tests**:

1. **Gross Income Test**: Family size-specific limits
2. **Net Income Test**: Family size-specific limits
3. **Continuing Eligibility Test**: < 100% Federal Poverty Level

#### Gross Income Limits (2024)

| Family Size | Monthly Gross Income Limit |
|-------------|---------------------------|
| 1 | $457 |
| 2 | $618 |
| 3 | $778 |
| Each additional | Add $161 |

#### Net Income Limits (2024)

| Family Size | Monthly Net Income Limit |
|-------------|-------------------------|
| 1 | $248 |
| 2 | $409 |
| 3 | $513 |
| Each additional | Add $104 |

**Note**: Net income is calculated after applying earned income disregards and deductions.

#### Continuing Eligibility Standard

**Indiana Code IC 12-14-1-1**:
> "Families remain eligible for TANF services when the family's gross income is less than one hundred percent (100%) of the federal income poverty level."

This allows families to continue receiving services even if income exceeds the net income limit, as long as it remains below 100% FPL.

### Future Income Limit Changes (SEA 265)

**Timeline:**
- **Current (pre-July 2025)**: ~16% FPL (~$307/month for family of 3)
- **July 2025 onward**: Phased increases begin
- **By December 31, 2027**: 50% FPL (~$950/month for family of 3)

**Note**: Specific year-by-year percentages not found in accessible sources.

**Source**:
- Senate Enrolled Act 265 (2023): https://iga.in.gov/legislative/2023/bills/senate/265/details
- Signed May 22, 2023

### Resource Limits

**Two-Tier System:**

1. **Application Phase**: Maximum $1,000 in countable resources
2. **Receipt Phase**: Maximum $10,000 in countable resources

**Excluded Resources:**
- Primary residence (usual home)
- Vehicle equity up to $20,000 total (fair market value - amount owed)

**Source**:
- FSSA website: https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/
- IC 12-14-1-1 (Resources while receiving)

## Work Requirements

### IMPACT Program

**Indiana Manpower Placement and Comprehensive Training (IMPACT)**
- Combined approach: employment + education + training
- Designed for career advancement and wage increases
- Mandatory for most applicants and recipients

### Applicant Requirements

**Pre-Eligibility Job Search**:
- Attend Applicant Job Search Orientation
- Complete minimum 6 employer contacts
- Submit 3 job applications
- Complete at least 20 days of job search activities

**Consequence of Non-Compliance**:
- Application denial (without good cause)

### Recipient Requirements

**Ongoing Participation**:
- Participate in job search activities through IMPACT
- Attend assigned job interviews
- Cannot voluntarily terminate employment without prior approval
- Must maintain required employment documentation

**Good Cause Exemptions**:
- Details not specified in HTML sources
- Likely documented in Policy Manual Chapter 2400 PDF

**Source**:
- 470 IAC 10.3-10-1 (IMPACT responsibilities)
- FSSA website: https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/

## Time Limits

### Lifetime Limits

**Children:**
- 60 months (5 years) lifetime limit
- Months do not need to be consecutive
- Months from another state's TANF program count toward limit
- Does not apply to children under age 18 as recipients

**Adults:**
- 24 months lifetime limit for adults receiving TANF
- More restrictive than federal 60-month requirement
- Does not apply to children under age 18

**Source**:
- FSSA website: https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/
- SingleMotherGuide: https://singlemotherguide.com/state/indiana/TANF

### Federal vs. Indiana Limits

| Limit Type | Federal | Indiana |
|------------|---------|---------|
| Adults | 60 months | **24 months** |
| Children | 60 months | 60 months |

Indiana's 24-month adult limit is significantly more restrictive than federal requirements.

## Child Support Requirements

### Assignment of Rights

**Requirement**:
- Must assign child support rights to state as condition of eligibility
- Assignment amount = lesser of:
  - TANF benefits received that month, OR
  - Amount of child support due that month

### Cooperation Requirements

**Must Cooperate In**:
- Establishing paternity for children born out of wedlock
- Establishing child support orders
- Enforcing child support obligations

**Good Faith Effort Required**:
- Presumption of good faith effort applies
- Other considerations may apply (not detailed in HTML sources)

**Source**:
- DCS Child Support: https://www.in.gov/dcs/child-support/custodial-party-information/tanf-benefits-and-child-support/
- Policy Manual Chapter 2400: https://www.in.gov/fssa/dfr/files/2400.pdf

## Application and Determination Timeline

### Processing Time

**Standard Timeline**:
- Eligibility decision made within 60 days of application
- Denials issued by day 61 if not approved

**Source**: FSSA website

## Reporting Requirements

### Recipient Obligations

**Must Report**:
- Changes in circumstances within 10 days
- Changes in income
- Changes in household composition
- Changes in resources

**Must Provide**:
- Accurate information
- Required employment documentation
- Cooperation with child support enforcement

**Source**: FSSA website

## Special Eligibility Provisions

### Pregnant Women (SEA 265)

**New Provision (effective with SEA 265)**:
- Pregnant woman eligible if at least 6 months pregnant
- Must meet income requirements
- Expands eligibility beyond just families with minor children

**Source**: Senate Enrolled Act 265 (2023)

## Documentation Requirements

### Required Documentation

**Application Phase**:
- Social Security numbers for all household members
- Proof of Indiana residency
- Proof of citizenship/immigration status
- Income verification
- Resource verification

**Details**: Policy Manual Chapter 2400 PDF (requires extraction)

## Exemptions and Special Cases

**Good Cause Exemptions**:
- Available for work requirements
- Available for child support cooperation
- Specific criteria not detailed in HTML sources
- **Requires**: Policy Manual Chapter 2400 PDF extraction

## Implementation Checklist

### Use Federal Baseline:
- [ ] Age thresholds (18/19 matches federal)
- [ ] Immigration eligibility (follows federal rules)

### Create State-Specific Rules:
- [x] Gross income limits (family size-based)
- [x] Net income limits (family size-based)
- [x] Continuing eligibility test (100% FPL)
- [x] Resource limits (two-tier: $1k/$10k)
- [x] Vehicle equity exclusion ($20k)
- [x] Adult time limit (24 months)
- [x] Work requirements (IMPACT program)
- [x] Pregnant women eligibility (6+ months)

### Outstanding Items:
- [ ] Good cause exemptions (need PDF extraction)
- [ ] SEA 265 year-by-year implementation schedule
- [ ] Detailed work requirement exemptions

## References

```yaml
# For eligibility parameters:
reference:
  - title: "Indiana Code 12-14-1 - TANF Eligibility"
    href: "https://iga.in.gov/laws/2023/ic/titles/12"
  - title: "470 IAC 10.3-3 - Nonfinancial Eligibility Requirements"
    href: "https://iar.iga.in.gov/latestArticle/470/10.3"
```

```python
# For eligibility variables:
reference = "470 IAC 10.3-3"
documentation = "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/"
```
