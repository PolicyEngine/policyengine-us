# Collected Documentation

## Oklahoma 2025 Individual Income Tax Implementation
**Collected**: 2025-12-29
**Implementation Task**: Update Oklahoma 2025 individual income tax parameters per issue #7060

---

## Source Information

### Primary Forms (2025 Tax Year)

| Form | Title | URL |
|------|-------|-----|
| 511-NR-Pkt | Nonresident/Part-Year Instructions | https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf |
| 511-Pkt | Resident Instructions | https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf |
| 538-H | Property Tax Credit | https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf |
| 538-S | Sales Tax Relief Credit | https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf |
| 511-EIC | Earned Income Credit | https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-EIC.pdf |
| 511-CR | Other Credits | https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/tax-credits/511-CR.pdf |

### Legislative Authority

| Citation | Description | URL |
|----------|-------------|-----|
| HB 2020 (2023) | Pension exemption $10,000 -> $20,000 | https://www.okhouse.gov/posts/news-20230324_4 |
| HB 2764 (2025) | 2026 tax rate reduction | https://www.oklegislature.gov/cf_pdf/2025-26%20ENR/hB/HB2764%20ENR.PDF |
| 68 O.S. Section 2355 | Tax rates/brackets | https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=92565 |
| OAC 710:50-15-49 | Retirement income deduction | https://www.law.cornell.edu/regulations/oklahoma/OAC-710-50-15-49 |
| OAC 710:50-15-96 | Sales tax relief credit | https://www.law.cornell.edu/regulations/oklahoma/OAC-710-50-15-96 |

---

## Key Rules and Thresholds

### Tax Rates (Page 38)

**Single/Married Filing Separately:**
| Threshold | Rate |
|-----------|------|
| $0 | 0.25% |
| $1,000 | 0.75% |
| $2,500 | 1.75% |
| $3,750 | 2.75% |
| $4,900 | 3.75% |
| $7,200 | 4.75% |

**Joint/HOH/Surviving Spouse:**
| Threshold | Rate |
|-----------|------|
| $0 | 0.25% |
| $2,000 | 0.75% |
| $5,000 | 1.75% |
| $7,500 | 2.75% |
| $9,800 | 3.75% |
| $14,400 | 4.75% |

### Standard Deduction (Page 10)
| Filing Status | Amount |
|---------------|--------|
| Single | $6,350 |
| MFJ | $12,700 |
| MFS | $6,350 |
| HOH | $9,350 |
| Surviving Spouse | $12,700 |

### Exemptions (Pages 9-10)
- **Per-person exemption**: $1,000
- **Special exemption AGI limits** (65+/blind):
  - Single: $15,000
  - MFJ: $25,000
  - MFS: $12,500
  - HOH: $19,000
  - Surviving Spouse: $25,000

### AGI Subtractions (Pages 16-17)

**CRITICAL UPDATE - Pension Limit (HB 2020):**
```
2021-01-01: $10,000
2024-01-01: $20,000  <-- NEW VALUE REQUIRED
```

**Military Retirement:**
- 2022+: 100% exclusion (already implemented)

### Credits

**EITC (Form 511-EIC, Page 15):**
- Match rate: 5% of federal EITC

**Child/CDCC Credits (Page 11):**
- CTC match: 5% of federal CTC
- CDCC match: 20% of federal CDCC
- AGI limit: $100,000

**Property Tax Credit (Form 538-H):**
- Age minimum: 65 (or disabled)
- Income limit: $12,000
- Maximum credit: $200

**Sales Tax Relief Credit (Form 538-S, Page 15):**
- Amount: $40 per exemption
- Income limit 1: $20,000 (general)
- Income limit 2: $50,000 (elderly/disabled/dependents)

---

## Parameter Files Requiring 2025 Reference Updates

### Tax Rates (5 files)
```
policyengine_us/parameters/gov/states/ok/tax/income/rates/
  single.yaml        # Page 38
  joint.yaml         # Page 38
  separate.yaml      # Page 38
  head_of_household.yaml  # Page 38
  surviving_spouse.yaml   # Page 38
```

### Deductions (2 files)
```
policyengine_us/parameters/gov/states/ok/tax/income/deductions/
  standard/amount.yaml       # Page 10
  itemized/limit.yaml        # Page 10
```

### Exemptions (3 files)
```
policyengine_us/parameters/gov/states/ok/tax/income/exemptions/
  amount.yaml              # Page 10
  special_age_minimum.yaml # Page 9
  special_agi_limit.yaml   # Page 9
```

### AGI Subtractions (4 files)
```
policyengine_us/parameters/gov/states/ok/tax/income/agi/subtractions/
  subtractions.yaml              # Page 16
  pension_limit.yaml             # Page 17 ** VALUE CHANGE: $10,000 -> $20,000 **
  military_retirement/rate.yaml  # Page 17
  military_retirement/floor.yaml # Page 17
```

### Credits (14 files)
```
policyengine_us/parameters/gov/states/ok/tax/income/credits/
  earned_income/eitc_fraction.yaml  # Page 15
  child/agi_limit.yaml              # Page 11
  child/cdcc_fraction.yaml          # Page 11
  child/ctc_fraction.yaml           # Page 11
  property_tax/age_minimum.yaml     # Form 538-H
  property_tax/income_fraction.yaml # Form 538-H
  property_tax/income_limit.yaml    # Form 538-H
  property_tax/maximum_credit.yaml  # Form 538-H
  sales_tax/age_minimum.yaml        # Form 538-S
  sales_tax/amount.yaml             # Page 15
  sales_tax/income_limit1.yaml      # Page 15
  sales_tax/income_limit2.yaml      # Page 15
  refundable.yaml                   # Multiple
  nonrefundable.yaml                # Multiple
  gross_income_sources.yaml         # Multiple
```

---

## References for Metadata

### Standard Reference Block (2025)
```yaml
reference:
  - title: 2025 Form 511-NR instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=XX
  - title: 2025 Form 511 instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=XX
```

### Pension Limit (CRITICAL UPDATE)
```yaml
# pension_limit.yaml - REQUIRES VALUE UPDATE
description: Oklahoma limit on taxable pension benefit AGI subtraction per person.
values:
  2021-01-01: 10_000
  2024-01-01: 20_000  # HB 2020

metadata:
  period: year
  unit: currency-USD
  label: Oklahoma limit on taxable pension benefit AGI subtraction per person
  reference:
    - title: 2025 Form 511-NR instructions
      href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=17
    - title: 2025 Form 511 instructions
      href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=17
    - title: HB 2020 - Pension Exemption Increase
      href: https://www.okhouse.gov/posts/news-20230324_4
```

---

## Special Cases and Exceptions

### Pension Subtraction
- Early distributions (box 7 code "1" on 1099-R) do NOT qualify
- Cannot exceed amount included in Federal AGI
- Combined with other retirement exclusions, total cannot exceed per-person limit

### Military Retirement
- 100% exclusion since 2022
- Applies to all branches of U.S. Armed Forces
- Historical: 75% (2007-2021), 50% (2006)

### Sales Tax Relief Credit
- TANF recipients EXCLUDED (benefit already includes sales tax relief)
- Visa holders do NOT qualify
- Must be alive at end of tax year
- No extensions for filing deadline

### Property Tax Credit
- Must be head of household
- Applies to taxes paid on occupied homestead only
- June 30 deadline - no extensions, no amended claims

---

## Detailed Documentation Location

Full regulatory text and comprehensive documentation saved to:
`docs/agents/sources/ok_income_tax_2025/`

Files:
- `overview.md` - Source summary and links
- `tax_rates.md` - Tax brackets by filing status
- `standard_deductions.md` - Deduction amounts
- `exemptions.md` - Personal and special exemptions
- `agi_subtractions.md` - All AGI subtraction rules
- `credits.md` - All tax credits
