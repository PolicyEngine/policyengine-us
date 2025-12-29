## Oklahoma 2025 Individual Income Tax Documentation Collection

I have gathered and verified the official documentation for the Oklahoma 2025 individual income tax implementation. Below is a comprehensive summary with page number references.

---

### Primary Sources Collected

| Form | Description | URL |
|------|-------------|-----|
| 511-NR-Pkt | 2025 Nonresident/Part-Year Instructions | [Link](https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf) |
| 511-Pkt | 2025 Resident Instructions | [Link](https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf) |
| 538-H | 2025 Property Tax Credit | [Link](https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf) |
| 538-S | 2025 Sales Tax Relief Credit | [Link](https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf) |
| 511-EIC | 2025 Earned Income Credit | [Link](https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-EIC.pdf) |
| 511-CR | 2025 Other Credits | [Link](https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/tax-credits/511-CR.pdf) |
| HB 2020 | Pension Exemption Increase | [Link](https://www.okhouse.gov/posts/news-20230324_4) |

---

### Tax Rates and Brackets (Page 38)

**Verified - No changes from current implementation for 2025**

**Single/MFS:**
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

---

### Standard Deduction (Page 10)

**Verified - No changes from current implementation**

| Filing Status | Amount |
|---------------|--------|
| Single | $6,350 |
| MFJ | $12,700 |
| MFS | $6,350 |
| HOH | $9,350 |
| Surviving Spouse | $12,700 |

---

### Exemptions (Pages 9-10)

**Verified - No changes from current implementation**

- **Per-person exemption**: $1,000 (Page 10)
- **Special exemption AGI limits** for 65+/blind (Page 9):
  - Single: $15,000
  - MFJ: $25,000
  - MFS: $12,500
  - HOH: $19,000
  - Surviving Spouse: $25,000

---

### AGI Subtractions (Pages 16-17)

**CRITICAL UPDATE REQUIRED - Pension Limit**

Per HB 2020 (passed House 90-0 on March 20, 2023), the retirement income exemption increased from $10,000 to $20,000 effective tax year 2024:

```yaml
# pension_limit.yaml - REQUIRES UPDATE
values:
  2021-01-01: 10_000
  2024-01-01: 20_000  # HB 2020 - NEW VALUE
```

**Military Retirement (Page 17):**
- 100% exclusion (since 2022) - Already correctly implemented

**Other Subtractions (Page 16):**
- US Government Interest
- Social Security Benefits
- Federal Civil Service Retirement (100%)
- Oklahoma Government Retirement (100%)
- Railroad Retirement Benefits
- Capital Gains Deduction

---

### Credits

**EITC (Page 15, Form 511-EIC):**
- Match rate: **5%** of federal EITC - Verified unchanged

**Child/CDCC Credits (Page 11):**
- CTC match: **5%** of federal CTC - Verified unchanged
- CDCC match: **20%** of federal CDCC - Verified unchanged
- AGI limit: **$100,000** - Verified unchanged

**Property Tax Credit (Form 538-H):**
- Age minimum: **65** (or disabled)
- Income limit: **$12,000** gross household income
- Maximum credit: **$200**
- All values verified unchanged

**Sales Tax Relief Credit (Page 15, Form 538-S):**
- Amount: **$40** per exemption
- Income limit (general): **$20,000**
- Income limit (elderly/disabled/dependents): **$50,000**
- All values verified unchanged

---

### Summary of Required Changes

**Value Update Required (1 file):**
- [ ] `pension_limit.yaml`: Add `2024-01-01: 20_000` per HB 2020

**Reference Updates Required (29 files):**
All Oklahoma income tax parameter files need 2025 form references added:

**Tax Rates (5 files):**
- `rates/single.yaml` - Page 38
- `rates/joint.yaml` - Page 38
- `rates/separate.yaml` - Page 38
- `rates/head_of_household.yaml` - Page 38
- `rates/surviving_spouse.yaml` - Page 38

**Deductions (2 files):**
- `deductions/standard/amount.yaml` - Page 10
- `deductions/itemized/limit.yaml` - Page 10

**Exemptions (3 files):**
- `exemptions/amount.yaml` - Page 10
- `exemptions/special_age_minimum.yaml` - Page 9
- `exemptions/special_agi_limit.yaml` - Page 9

**AGI Subtractions (4 files):**
- `agi/subtractions/subtractions.yaml` - Page 16
- `agi/subtractions/pension_limit.yaml` - Page 17 + HB 2020
- `agi/subtractions/military_retirement/rate.yaml` - Page 17
- `agi/subtractions/military_retirement/floor.yaml` - Page 17

**Credits (14 files):**
- `credits/earned_income/eitc_fraction.yaml` - Page 15
- `credits/child/agi_limit.yaml` - Page 11
- `credits/child/cdcc_fraction.yaml` - Page 11
- `credits/child/ctc_fraction.yaml` - Page 11
- `credits/property_tax/*.yaml` (4 files) - Form 538-H
- `credits/sales_tax/*.yaml` (4 files) - Page 15, Form 538-S
- `credits/refundable.yaml`
- `credits/nonrefundable.yaml`
- `credits/gross_income_sources.yaml`

---

### Detailed Documentation

Full documentation with regulatory text and reference blocks has been saved to:
- `docs/agents/sources/ok_income_tax_2025/` (detailed documentation)
- `working_references.md` (implementation summary)

---

### New Reference Block Format

For all 2025 updates, use this reference format:
```yaml
reference:
  - title: 2025 Form 511-NR instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=XX
  - title: 2025 Form 511 instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=XX
```

For pension_limit.yaml specifically:
```yaml
reference:
  - title: 2025 Form 511-NR instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-NR-Pkt.pdf#page=17
  - title: 2025 Form 511 instructions
    href: https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=17
  - title: HB 2020 - Pension Exemption Increase
    href: https://www.okhouse.gov/posts/news-20230324_4
```
