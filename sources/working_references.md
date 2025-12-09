# Collected Documentation

## Oregon TANF - Simplified Implementation
**Collected**: 2025-12-08
**Implementation Task**: Implement Oregon Temporary Assistance for Needy Families (TANF) program

---

## Source Information

### Primary Legal Authority
- **Title**: Oregon Administrative Rules Chapter 461 - Self-Sufficiency Programs
- **Citation**: OAR 461-155-0030, OAR 461-160-0100, OAR 461-160-0160, OAR 461-135-0070
- **URL**: https://secure.sos.state.or.us/oard/displayChapterRules.action?selectedChapter=90
- **Effective Date**: Various, most recent July 6, 2020 and later amendments

### Oregon Department of Human Services
- **Title**: TANF Cash Benefits Program Page
- **URL**: https://www.oregon.gov/odhs/cash/pages/tanf.aspx
- **Purpose**: Official program information and application portal

---

## Key Rules and Thresholds

### Payment Standards (OAR 461-155-0030)
Payment standards for benefit groups **containing an adult**:

| Need Group Size | Payment Standard |
|-----------------|------------------|
| 1 | $339 |
| 2 | $432 |
| 3 | $506 |
| 4 | $621 |
| 5 | $721 |
| 6 | $833 |
| 7 | $923 |
| 8 | $1,030 |
| 9 | $1,093 |
| 10 | $1,204 |
| Each additional | +$110 |

**Note**: Payment standards have been at these levels since July 1, 2011.

### Countable Income Limits (OAR 461-155-0030)
For need groups **not** eligible for Exit Limit Increase (ELI):

| Need Group Size | Countable Income Limit |
|-----------------|------------------------|
| 1 | $345 |
| 2 | $499 |
| 3 | $616 |
| 4 | $795 |
| 5 | $932 |
| 6 | $1,060 |
| 7 | $1,206 |
| 8 | $1,346 |
| 9 | $1,450 |
| 10 | $1,622 |
| Each additional | +$172 |

### Adjusted Income Limits (OAR 461-155-0030)
For need groups **not** eligible for ELI:

| Need Group Size | Adjusted Income Limit |
|-----------------|----------------------|
| 1 | $326 |
| 2 | $416 |
| 3 | $485 |
| 4 | $595 |
| 5 | $695 |
| 6 | $796 |
| 7 | $886 |
| 8 | $976 |
| 9 | $1,039 |
| 10 | $1,150 |
| Each additional | +$110 |

### Exit Limit Increase (ELI) Standards (OAR 461-155-0030)
Higher income limits for families with earned income (approximately 2x payment standard):

| Need Group Size | ELI Standard |
|-----------------|--------------|
| 1 | $678 |
| 2 | $864 |
| 3 | $1,012 |
| 4 | $1,242 |
| 5 | $1,442 |
| 6 | $1,666 |
| 7 | $1,846 |
| 8 | $2,060 |
| 9 | $2,186 |
| 10 | $2,408 |
| Each additional | +$220 |

### Resource Limits (OAR 461-160-0015)
- **Standard limit**: $10,000 for most need groups
- **Lower limit**: $2,500 for need groups where every caretaker relative is serving an intentional program violation/JOBS disqualification
- **Non-needy caretaker relative**: Income limit is 185% of Federal Poverty Level

### Minimum Benefit (OAR 461-165-0060)
- Benefits are not issued if monthly benefit is less than **$10**
- Exception: Special payments, one-time needs, emergency assistance are not subject to this minimum

---

## Calculation Formulas

### Eligibility Determination (OAR 461-160-0100)

**Step 1: Countable Income Test**
```
IF countable_income >= countable_income_limit THEN
    NOT ELIGIBLE
```

**Step 2: Adjusted Income Test** (if passed Step 1)
```
IF adjusted_income >= adjusted_income_limit THEN
    NOT ELIGIBLE
```

**Step 3: Benefit Calculation** (if passed Steps 1 and 2)
```
benefit = payment_standard - adjusted_income
benefit = max(benefit, 0)
IF benefit < 10 THEN benefit = 0
```

### Adjusted Income Calculation (OAR 461-001-0000)
```
adjusted_income = countable_income - earned_income_deduction
```

### Earned Income Deduction (OAR 461-160-0160)
```
earned_income_deduction = 0.50 * gross_earned_income
```
- The deduction is **50%** of gross earned income including self-employment income

### ELI Eligibility Alternative (OAR 461-160-0100)
For families with earned income:
```
IF countable_income < ELI_standard THEN
    benefit = payment_standard - adjusted_income
```

---

## Demographic Eligibility

### Dependent Child Definition (OAR 461-120-0510)
A dependent child must be:
- Under 18 years of age, OR
- Under 19 years of age AND regularly attending school full-time

**"Regularly attending school" includes:**
- School in grade 12 or below (including approved home schooling)
- GED classes in lieu of high school
- Vocational or technical training (including Job Corps) in lieu of high school
- Oregon School for the Deaf

### Categorical Eligibility (OAR 461-135-0070)
Eligible categories include:
- Dependent children (with exceptions for foster care)
- Caretaker relatives of eligible dependent children
- Parents of unborn children (in calendar month before due date)

### Immigration Status
- Must be a U.S. citizen or qualified immigrant
- Qualified immigrants include: lawful permanent residents, asylees, refugees, VAWA recipients, T-visa holders

---

## Income Treatment

### Earned Income (OAR 461-145-0130)
**Counted as earned income:**
- Wages and salaries
- Self-employment income (gross receipts, no cost deductions for TANF per OAR 461-145-0920)
- Tips and commissions

**Excluded from earned income:**
- Dependent children under 19 who are full-time students in grade 12 or below
- Dependent children under 18 attending school part-time and not employed full-time
- Dependent children too young for school
- First $260/month of Welfare-to-Work experience income
- Earned in-kind income

### Unearned Income (OAR 461-145 series)
**Counted as unearned income:**
- Child support (with partial disregard - see below)
- Spousal support/alimony
- Social Security benefits
- SSI (Supplemental Security Income)
- Unemployment benefits
- Workers' compensation
- Veterans benefits
- Annuity payments
- Dividends, interest, royalties

### Child Support Disregard (OAR 461-145-0080)
- Disregard up to $50 per dependent child per month
- Maximum disregard: $200 per financial group per month
- Applies to current child support only

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limit
- **60-month lifetime limit** on TANF benefits [CANNOT ENFORCE - requires history]

### Work Requirements
- Recipients must participate in JOBS employment program
- Minimum 30 hours/week of work-related activities [NOT IMPLEMENTED - work requirements outside scope]

### 120-Day Disqualification
- Families face 120-day ineligibility if parent voluntarily quit or reduced hours at 100+ hour/month job [CANNOT TRACK - requires history]

### ELI Time-Sensitivity
- ELI standards apply during certification periods and within 30 days after closure due to earned income [SIMPLIFIED - apply ELI when earned income present]

---

## Implementation Approach

### For simplified implementation:
- [x] Use federal demographic eligibility baseline (age 18/19 matches federal pattern)
- [x] Use federal immigration eligibility baseline (follows federal qualified immigrant rules)
- [ ] Create Oregon-specific payment standards (fixed amounts, not FPL-based)
- [ ] Create Oregon-specific income limits (countable, adjusted, ELI)
- [ ] Implement 50% earned income disregard
- [ ] Implement child support disregard ($50/child, max $200/household)

### Key Oregon-Specific Features:
1. **Two-tier eligibility test**: Both countable and adjusted income must be below limits
2. **ELI standards**: Higher income limits for families with earned income (2x payment standard)
3. **50% earned income disregard**: Applied to calculate adjusted income
4. **Child support disregard**: $50/child/month, max $200/household
5. **No self-employment cost deductions**: Gross receipts used for TANF

---

## References for Metadata

### For parameters:
```yaml
reference:
  - title: "OAR 461-155-0030 - Income and Payment Standards; REF, TANF"
    href: "https://oregon.public.law/rules/oar_461-155-0030"
  - title: "Oregon TANF Cash Benefits"
    href: "https://www.oregon.gov/odhs/cash/pages/tanf.aspx"
```

### For variables:
```python
# Eligibility
reference = "https://oregon.public.law/rules/oar_461-160-0100"

# Payment standards
reference = "https://oregon.public.law/rules/oar_461-155-0030"

# Earned income deduction
reference = "https://oregon.public.law/rules/oar_461-160-0160"

# Resource limits
reference = "https://oregon.public.law/rules/oar_461-160-0015"

# Dependent child definition
reference = "https://oregon.public.law/rules/oar_461-120-0510"

# Specific TANF requirements
reference = "https://oregon.public.law/rules/oar_461-135-0070"

# Minimum benefit
reference = "https://oregon.public.law/rules/oar_461-165-0060"
```

---

## PDFs Requiring Extraction

The following PDFs contain potentially useful supplementary information:

1. **NCCP TANF Profile - Oregon**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Oregon.pdf
   - Purpose: Summary of Oregon TANF policy parameters
   - Priority: SUPPLEMENTARY (key values already extracted from HTML sources)

2. **Oregon DHS Combined Standards (Form 5530)**
   - URL: https://sharedsystems.dhsoha.state.or.us/DHSForms/Served/de5530.pdf
   - Purpose: Complete standards tables for all DHS programs
   - Priority: SUPPLEMENTARY (values confirmed from other sources)

3. **Oregon Legislature TANF Committee Document**
   - URL: https://olis.oregonlegislature.gov/liz/2025R1/Downloads/CommitteeMeetingDocument/293797
   - Purpose: Legislative overview of TANF program
   - Priority: SUPPLEMENTARY

**Note**: All critical implementation values have been extracted from authoritative HTML sources (Oregon Administrative Rules via oregon.public.law and Oregon Secretary of State). PDF extraction is NOT required to proceed with implementation.
