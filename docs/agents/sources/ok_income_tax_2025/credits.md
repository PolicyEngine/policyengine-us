# Oklahoma 2025 Tax Credits

## Earned Income Tax Credit (EITC)

**Source**: Form 511-EIC
**URL**: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-EIC.pdf

### Credit Calculation
**Match Rate**: 5% of federal EITC

The Oklahoma EITC equals 5% of the federal earned income credit calculated using the same requirements in effect for the 2020 federal income tax year.

### Eligibility
- Must be Oklahoma resident or part-year resident
- Nonresidents do not qualify
- Must qualify for federal EITC

### Calculation (Schedule 511-G)
1. Enter federal earned income credit from Form 511-EIC
2. Multiply by 5% (0.05)
3. For part-year residents: multiply by ratio of Oklahoma AGI to Federal AGI

### Reference for Metadata
```yaml
reference:
  - title: 2025 Form 511-EIC
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-EIC.pdf
  - title: 2025 Form 511-NR instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=15
  - title: 2025 Form 511 instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=15
```

---

## Child Tax/Child Care Tax Credit

**Source**: Form 511-NR-Pkt, Page 11
**URL**: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=11

### Credit Options
Taxpayers may claim the GREATER of:
1. **5%** of the federal Child Tax Credit (CTC), OR
2. **20%** of the federal Child and Dependent Care Credit (CDCC)

### Income Limit
**Federal AGI Limit**: $100,000 (married filing jointly)

### Credit Type
- Nonrefundable credit
- Reduces tax liability but cannot generate refund

### Reference for Metadata
```yaml
# For ctc_fraction.yaml:
reference:
  - title: 2025 Form 511-NR instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=11
  - title: 2025 Form 511 instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=11

# For cdcc_fraction.yaml:
reference:
  - title: 2025 Form 511-NR instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=11
  - title: 2025 Form 511 instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=11

# For agi_limit.yaml:
reference:
  - title: 2025 Form 511-NR instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=11
  - title: 2025 Form 511 instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=11
```

---

## Property Tax Credit (Form 538-H)

**Source**: Form 538-H
**URL**: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf

### Eligibility Requirements
1. **Age**: 65 or older OR totally disabled
2. **Residency**: Head of household and Oklahoma resident during prior year
3. **Income**: Gross household income not exceeding $12,000

### Credit Amount
- Maximum credit: $200
- Based on property taxes actually paid on homestead
- Calculated as: Property taxes paid (capped at $200)

### Gross Household Income Definition
Includes income of ALL persons living in the same household:
- Wages and salaries
- Pensions and annuities
- Social Security benefits
- Unemployment payments
- Veterans benefits
- All other income (taxable or not), EXCEPT gifts

### Filing Deadline
- June 30 for property taxes paid in prior year
- No extensions allowed for this credit
- Cannot amend return to claim after deadline

### Reference for Metadata
```yaml
# For property_tax/income_limit.yaml:
reference:
  - title: 2025 Form 538-H
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf

# For property_tax/maximum_credit.yaml:
reference:
  - title: 2025 Form 538-H
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf

# For property_tax/age_minimum.yaml:
reference:
  - title: 2025 Form 538-H
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf
```

---

## Sales Tax Relief Credit (Form 538-S)

**Source**: Form 538-S; OAC 710:50-15-96
**URL**: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf

### Credit Amount
**$40 per exemption** (each household member)

### Income Limits

| Eligibility Category | Maximum Gross Income |
|---------------------|---------------------|
| Elderly (65+), Disabled, or Has Dependents | $50,000 |
| All Other Filers | $20,000 |

### Eligibility Requirements
1. Oklahoma resident for entire tax year
2. Not received TANF benefits during the year (TANF includes sales tax relief)
3. Not living in Oklahoma under a visa
4. Neither taxpayer nor spouse died during tax year

### Credit Type
- **Refundable credit** - can be claimed even with no tax liability

### Filing Deadlines
- **As credit against tax**: April 15 (part of regular return)
- **As standalone refund**: June 30
- Extensions do NOT extend the filing deadline for this credit

### Historical Note
- Enacted in 1990 (HB 1017)
- $40 amount has remained unchanged since inception
- Originally intended to offset sales tax on groceries for low-income households

### Reference for Metadata
```yaml
# For sales_tax/amount.yaml:
reference:
  - title: 2025 Form 538-S
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf
  - title: 2025 Form 511-NR instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=15
  - title: 2025 Form 511 instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=15

# For sales_tax/income_limit1.yaml ($20,000 limit):
reference:
  - title: 2025 Form 538-S
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf
  - title: OAC 710:50-15-96
    href: https://www.law.cornell.edu/regulations/oklahoma/OAC-710-50-15-96

# For sales_tax/income_limit2.yaml ($50,000 limit):
reference:
  - title: 2025 Form 538-S
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf
  - title: OAC 710:50-15-96
    href: https://www.law.cornell.edu/regulations/oklahoma/OAC-710-50-15-96

# For sales_tax/age_minimum.yaml:
reference:
  - title: 2025 Form 538-S
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf
```

---

## Other Credits (Form 511-CR)

**Source**: Form 511-CR
**URL**: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/tax-credits/511-CR.pdf

### New Programs Identified (Potential Future Implementation)

1. **Scholarship-Granting Organization Credit**
   - 50-75% of contribution
   - Maximum: $1,000-$2,000

2. **Parental Choice Tax Credit (Homeschool)**
   - Expense-based credit
   - Maximum: $1,000 per student per year

3. **Electric Vehicle Credit**
   - $5,500-$9,000 per vehicle

4. **Zero-Emission Facility Credit**
   - Based on electricity production/sales

### Reference for Metadata
```yaml
reference:
  - title: 2025 Form 511-CR
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/tax-credits/511-CR.pdf
```
