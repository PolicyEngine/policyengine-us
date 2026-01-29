# Collected Documentation

## New York State 2025 Individual Income Tax Implementation
**Collected**: 2026-01-08
**Implementation Task**: Update NY income tax model for tax year 2025 (Issue #7142)

---

## Official Program Name

**Program**: New York State Individual Income Tax
**Form**: IT-201 (Full-Year Resident Income Tax Return)
**Tax Year**: 2025

---

## Source Information

### Primary Sources
- **Title**: 2025 Form IT-201-I Instructions (HTML)
- **URL**: https://www.tax.ny.gov/forms/html-instructions/2025/it/it201i-2025.htm
- **Effective Date**: Tax Year 2025

### 📄 PDFs for Future Reference

The following PDFs contain additional information:

1. **2025 Form IT-201 Instructions (PDF)**
   - URL: https://www.tax.ny.gov/pdf/current_forms/it/it201i.pdf
   - Expected content: Complete IT-201 instructions with tax tables, household credit tables, supplemental tax computation
   - Key pages: Pages 33-37 (tax rate tables), Page 11 (standard deduction), Pages 25-27 (credits)

2. **Form IT-216 Instructions (CDCC)**
   - URL: https://www.tax.ny.gov/pdf/current_forms/it/it216i.pdf
   - Expected content: NYS Child and Dependent Care Credit percentage tables by income

3. **Form IT-214 Instructions (Real Property Tax Credit)**
   - URL: https://www.tax.ny.gov/pdf/current_forms/it/it214i.pdf
   - Expected content: Detailed calculation methodology for real property tax credit

4. **Form IT-272 Instructions (College Tuition)**
   - URL: https://www.tax.ny.gov/pdf/current_forms/it/it272i.pdf
   - Expected content: College tuition credit and deduction calculation details

5. **Form IT-196 Instructions (Itemized Deductions)**
   - URL: https://www.tax.ny.gov/pdf/current_forms/it/it196i.pdf
   - Expected content: Itemized deduction reduction rules and thresholds

---

## NYS Income Tax Rates (2025)

### Single & Married Filing Separately (Filing Status 1 & 3)

| Taxable Income | Rate |
|----------------|------|
| $0 - $8,500 | 4.00% |
| $8,500 - $11,700 | 4.50% |
| $11,700 - $13,900 | 5.25% |
| $13,900 - $80,650 | 5.50% |
| $80,650 - $215,400 | 6.00% |
| $215,400 - $1,077,550 | 6.85% |
| $1,077,550 - $5,000,000 | 9.65% |
| $5,000,000 - $25,000,000 | 10.30% |
| Over $25,000,000 | 10.90% |

**Source**: 2025 Form IT-201-I Instructions, Pages 33-34
**Legal Citation**: Tax Law Section 601

### Married Filing Jointly & Qualifying Surviving Spouse (Filing Status 2 & 5)

| Taxable Income | Rate |
|----------------|------|
| $0 - $17,150 | 4.00% |
| $17,150 - $23,600 | 4.50% |
| $23,600 - $27,900 | 5.25% |
| $27,900 - $161,550 | 5.50% |
| $161,550 - $323,200 | 6.00% |
| $323,200 - $2,155,350 | 6.85% |
| $2,155,350 - $5,000,000 | 9.65% |
| $5,000,000 - $25,000,000 | 10.30% |
| Over $25,000,000 | 10.90% |

**Source**: 2025 Form IT-201-I Instructions, Pages 33-34

### Head of Household (Filing Status 4)

| Taxable Income | Rate |
|----------------|------|
| $0 - $12,800 | 4.00% |
| $12,800 - $17,650 | 4.50% |
| $17,650 - $20,900 | 5.25% |
| $20,900 - $107,650 | 5.50% |
| $107,650 - $269,300 | 6.00% |
| $269,300 - $1,616,450 | 6.85% |
| $1,616,450 - $5,000,000 | 9.65% |
| $5,000,000 - $25,000,000 | 10.30% |
| Over $25,000,000 | 10.90% |

**Source**: 2025 Form IT-201-I Instructions, Pages 33-34

### Implementation Note
**No change from 2024** - The 2025 tax brackets and rates remain unchanged from 2024. The existing parameters are current.

---

## NYS Supplemental Tax

### Minimum AGI Threshold
- **All filing statuses**: $107,650
- Taxpayers with NY AGI over $107,650 cannot use the standard tax tables and must compute tax using the supplemental tax calculation

**Source**: 2025 Form IT-201-I Instructions
**Legal Citation**: Tax Law Section 601(d-2), (d-3), (d-4)

### Implementation Note
**No change from 2024** - The supplemental tax threshold remains at $107,650.

---

## NYS Standard Deductions (2025)

| Filing Status | Amount |
|---------------|--------|
| Single (can be claimed as dependent) | $3,100 |
| Single (cannot be claimed as dependent) | $8,000 |
| Married Filing Jointly | $16,050 |
| Married Filing Separately | $8,000 |
| Head of Household | $11,200 |
| Qualifying Surviving Spouse | $16,050 |

**Source**: 2025 Form IT-201-I Instructions, Page 11

### Implementation Note
**No change from 2024** - Standard deduction amounts remain unchanged.

---

## NYS Dependent Exemption (2025)

- **Amount**: $1,000 per dependent

**Source**: 2025 Form IT-201-I Instructions, Page 11

### Implementation Note
**No change from 2024** - Dependent exemption remains at $1,000.

---

## NYS Earned Income Tax Credit (EITC)

### Match Percentage
- **Rate**: 30% of federal EITC
- **Reduced by**: Any household credit claimed

**Source**: https://www.tax.ny.gov/pit/credits/earned_income_credit.htm
**Legal Citation**: Tax Law Section 606(d)

### Implementation Note
**No change from 2024** - EITC match rate remains at 30%.

---

## Empire State Child Tax Credit (2025-2027 Enhanced)

### Credit Amounts by Age (Tax Year 2025)

| Child Age | Maximum Credit |
|-----------|----------------|
| Under 4 years old | $1,000 |
| 4 through 16 years old | $330 |
| 17 and older | $0 |

### Credit Amounts by Age (Tax Year 2026-2027)

| Child Age | Maximum Credit |
|-----------|----------------|
| Under 4 years old | $1,000 |
| 4 through 16 years old | $500 |
| 17 and older | $0 |

### Phase-Out Thresholds (2025-2027)

| Filing Status | Phase-Out Begins |
|---------------|-----------------|
| Married Filing Jointly | $110,000 |
| Single | $75,000 |
| Head of Household | $75,000 |
| Married Filing Separately | $55,000 |
| Qualifying Surviving Spouse | $110,000 |

### Phase-Out Rate
- **Reduction**: $16.50 per $1,000 of income above threshold
- **Increment**: $1,000

### Eligibility Requirements
- Full-year New York State resident
- Qualifying child under age 17 on December 31
- Valid SSN or ITIN required

### Important Notes
- **Refundable credit** - benefit available regardless of tax liability
- **No phase-in** - lowest income families receive full benefit (changed from previous law)
- **Sunset**: Enhanced amounts expire after 2027

**Source**: https://www.tax.ny.gov/pit/credits/empire_state_child_credit.htm
**Legal Citation**: Tax Law Section 606(c-1), Senate Bill S.3009-C Part C Section 2

### Implementation Note
**Already implemented for 2025** - Parameters in `gov/states/ny/tax/income/credits/ctc/post_2024/` contain correct 2025 values. The age 4+ amount for 2025 shows $330 (not $500 which applies starting 2026).

---

## NYS Child and Dependent Care Credit (CDCC)

### Calculation Method
The NYS CDCC is calculated as a **percentage of the federal CDCC**, based on NYS adjusted gross income.

### Key Facts
- **Refundable**: Yes (for full-year residents)
- **Basis**: Federal CDCC amount (up to $3,000 for one dependent, $6,000 for two or more)
- **NYS percentage**: Varies by income (percentage table in IT-216 instructions)

**Source**: https://www.tax.ny.gov/pit/credits/child_and_dependent_care_credit.htm

### Implementation Note
**No structural changes for 2025** - The CDCC percentage calculation methodology has not changed. Specific percentage tables should be verified in IT-216 instructions PDF.

---

## NYS Real Property Tax Credit

### Income Threshold
- **Maximum federal AGI**: $18,000 or less

### Property Value Limit
- **Maximum current market value**: $85,000 or less

### Maximum Credit Amounts

| Household Composition | Maximum Credit |
|-----------------------|----------------|
| All members under age 65 | $75 |
| At least one member age 65+ | $375 |

### Additional Requirements
- Must be NYS resident entire year
- Occupied same NY residence for 6+ months
- Cannot be claimed as dependent
- Residence not completely tax-exempt

**Source**: https://www.tax.ny.gov/pit/credits/real_property_tax_credit.htm

### Implementation Note
**No change from 2024** - Real property tax credit thresholds remain unchanged.

---

## NYS College Tuition Credit/Deduction

### Credit
- **Maximum credit**: $400 per eligible student
- **Rate**: 4% of qualified tuition expenses
- **Minimum**: $200 if tuition is under $5,000

### Itemized Deduction
- **Maximum deduction**: $10,000 per eligible student

### High-Income Phase-Out (Deduction Only)
- **AGI $525,000 - $1,000,000**: 50% of deduction allowed
- **AGI over $1,000,000**: No deduction allowed

### Eligibility
- Undergraduate tuition only
- NYS residents only for credit (deduction available to part-year/nonresidents)

**Source**: https://www.tax.ny.gov/pit/credits/college_tuition_credit.htm

### Implementation Note
**No change from 2024** - College tuition credit and deduction parameters remain unchanged.

---

## NYS Household Credit

### Income Limits

| Filing Status | Maximum AGI |
|---------------|-------------|
| Single | $28,000 |
| Married Filing Jointly | $32,000 |
| Married Filing Separately | $32,000 |
| Head of Household | $32,000 |
| Qualifying Surviving Spouse | $32,000 |

### Credit Amount Structure
- **Single filers**: Up to $75
- **MFJ/HOH/QSS**: $20-$90 base, plus $5-$15 per dependent

### Tables
- **Table 1**: Single filers
- **Table 2**: MFJ, HOH, QSS
- **Table 3**: Married Filing Separately

**Source**: https://www.tax.ny.gov/pit/credits/household_credit.htm

### Implementation Note
**Verify detailed tables** - The exact credit amounts by income level should be extracted from the IT-201 instructions PDF. Current parameters appear to have bracket-based implementation.

---

## NYS Pension & Annuity Exclusion

### Parameters
- **Maximum exclusion**: $20,000
- **Minimum age**: 59.5 years old

**Source**: 2025 Form IT-201-I Instructions, Page 10

### Implementation Note
**No change from 2024** - Pension exclusion parameters remain unchanged.

---

## NYS Itemized Deduction Reduction

### Key Rules
1. **SALT Deduction**: NYS does not limit state and local tax deductions (unlike federal $40,000/$20,000 cap)
2. **High-Income Limitation**: For AGI over $10 million, charitable contribution deduction limited to 25% (through 2029)

### Phase-Out Structure
The reduction applies based on income thresholds with incremental calculations. Specific thresholds are in IT-196 instructions.

**Source**: https://www.tax.ny.gov/pit/file/itemized-deductions-2025.htm

### Implementation Note
**Verify phase-out thresholds** - The existing parameter files at `gov/states/ny/tax/income/deductions/itemized/reduction/` should be reviewed against IT-196 instructions.

---

## NYS Inflation Refund Credit (2025 Only)

### Payment Amounts by Filing Status and Income

| Filing Status | Income Threshold | Refund Amount |
|---------------|------------------|---------------|
| Single | $75,000 or less | $200 |
| Single | $75,001 - $150,000 | $150 |
| Married Filing Jointly | $150,000 or less | $400 |
| Married Filing Jointly | $150,001 - $300,000 | $300 |
| Head of Household | $75,000 or less | $200 |
| Head of Household | $75,001 - $150,000 | $150 |
| Married Filing Separately | $75,000 or less | $200 |
| Married Filing Separately | $75,001 - $150,000 | $150 |
| Qualifying Surviving Spouse | $150,000 or less | $400 |
| Qualifying Surviving Spouse | $150,001 - $300,000 | $300 |

### Eligibility
- Based on **2023 tax year** filing
- Must have filed Form IT-201 (full-year resident)
- Cannot be claimed as dependent

### Important Notes
- **One-time payment** - Not recurring
- **Automatic** - No application required
- **Distributed**: September-November 2025

**Source**: https://www.tax.ny.gov/pit/inflation-refund-checks.htm

### Implementation Note
**Already implemented** - Parameters exist at `gov/states/ny/tax/income/credits/inflation_refund/`. These are based on 2023 tax year income, not 2025.

---

## NYS Solar Energy System Equipment Credit

### Parameters
- **Credit rate**: 25% of qualified expenditures
- **Maximum credit**: $5,000
- **Carryforward**: Up to 5 years
- **Refundable**: No

### Eligibility
- System must be at principal NYS residence
- Purchased or leased solar equipment

**Source**: https://www.tax.ny.gov/pit/credits/solar_energy_system_equipment_credit.htm

### Implementation Note
**No change from 2024** - Solar credit parameters remain unchanged.

---

## NYS Geothermal Energy System Credit

### Credit Rate
- **Rate**: 25% of qualified expenditures

### Maximum Credit (Date-Dependent)

| System Placed in Service | Maximum Credit |
|--------------------------|----------------|
| On or before June 30, 2025 | $5,000 |
| On or after July 1, 2025 | $10,000 |

### Carryforward
- Up to 5 years

### Refundable
- No (currently nonrefundable)
- Starting 2026: May become refundable for lower-income homeowners

**Source**: https://www.tax.ny.gov/pit/credits/geothermal-energy-system-credit.htm

### Implementation Note
**NEEDS UPDATE** - Current parameter at `gov/states/ny/tax/income/credits/geothermal_energy_system/cap.yaml` only has $5,000 value. Need to add:
- `2025-07-01: 10_000` for the new cap

---

## NYC Income Tax Rates (2025)

### Single & Married Filing Separately

| NYC Taxable Income | Rate |
|--------------------|------|
| $0 - $12,000 | 3.078% |
| $12,000 - $25,000 | 3.762% |
| $25,000 - $50,000 | 3.819% |
| Over $50,000 | 3.876% |

### Married Filing Jointly & Qualifying Surviving Spouse

| NYC Taxable Income | Rate |
|--------------------|------|
| $0 - $21,600 | 3.078% |
| $21,600 - $45,000 | 3.762% |
| $45,000 - $90,000 | 3.819% |
| Over $90,000 | 3.876% |

### Head of Household

| NYC Taxable Income | Rate |
|--------------------|------|
| $0 - $14,400 | 3.078% |
| $14,400 - $30,000 | 3.762% |
| $30,000 - $60,000 | 3.819% |
| Over $60,000 | 3.876% |

**Source**: 2025 Form IT-201-I Instructions, Pages 40-41
**Legal Citation**: NYC Administrative Code Section 11-1701

### Implementation Note
**No change from 2024** - NYC tax rates remain unchanged.

---

## NYC Earned Income Credit

### Percentage Structure by Income

| NYC Taxable Income | EITC Match Rate |
|--------------------|-----------------|
| $0 - $7,500 | 30% |
| $7,500 - $17,500 | 25% |
| $17,500 - $22,500 | 20% |
| $22,500 - $42,500 | 15% |
| Over $42,500 | 10% |

**Source**: NYC EITC Worksheet, Form IT-215 Instructions
**Legal Citation**: NYC Administrative Code Section 11-1706(b)

### Implementation Note
**No change from 2024** - NYC EITC percentage brackets remain unchanged.

---

## NYC School Tax Credit

### Fixed Amount Credit

| Filing Status | Amount |
|---------------|--------|
| Single | $63 |
| Married Filing Separately | $63 |
| Head of Household | $63 |
| Married Filing Jointly | $125 |
| Qualifying Surviving Spouse | $125 |

### Income Limit
- **Maximum NYC taxable income**: $250,000

### Rate Reduction Amount
- Calculated as percentage of NYC taxable income
- **Income limit**: $500,000 or less

**Source**: 2025 Form IT-201-I Instructions, Pages 20, 26

### Implementation Note
**No change from 2024** - NYC School Tax Credit amounts remain unchanged.

---

## NYC Household Credit

### Income Limits

| Filing Status | Maximum Income |
|---------------|----------------|
| Single | $12,500 |
| MFJ/HOH/QSS | $22,500 |

### Credit Structure
- **Single filers**: Up to $15
- **Other filers**: Based on dependents

**Source**: https://www.tax.ny.gov/pit/credits/new_york_city_credits.htm

### Implementation Note
**No change from 2024** - NYC Household Credit parameters remain unchanged.

---

## NYC Child and Dependent Care Credit

### Match Rate
- **Maximum**: 75% of NYS CDCC

### Eligibility Requirements
- Must qualify for NYS CDCC
- **Child age requirement**: Under age 4 on December 31
- **Federal AGI limit**: $30,000 or less

**Source**: https://www.tax.ny.gov/pit/credits/new_york_city_credits.htm

### Implementation Note
**No change from 2024** - NYC CDCC parameters remain unchanged.

---

## NEW: Central Business District Toll Credit (2025)

### Overview
New refundable credit for NYC residents who pay congestion pricing tolls.

### Eligibility Requirements
1. **Residence**: Primary residence in NYC's Central Business District (Congestion Relief Zone)
2. **Income**: NYS adjusted gross income under $60,000
3. **Tolls**: Paid CBD tolls during the tax year that were NOT business expenses

### Credit Amount
- **100% of CBD tolls paid** during the tax year
- **No maximum stated** - appears to be full reimbursement
- **Refundable**: Yes

### Income Limit
- **Maximum NYS AGI**: $60,000
- **No phase-out**: Full eligibility below threshold, no credit at or above

### How to Claim
- File Form IT-268, Central Business District Toll Credit
- Submit with income tax return
- Retain toll statements/receipts as documentation

### Effective Date
- Credit available starting 2025 tax year
- Last updated: November 19, 2025

**Source**: https://www.tax.ny.gov/pit/credits/central-business-district-toll-credit.htm

### Implementation Requirements
New parameters needed:
```yaml
# gov/states/ny/tax/income/credits/cbd_toll/max_agi.yaml
values:
  2025-01-01: 60_000
```

New variable needed:
- `ny_cbd_toll_credit` - Calculate credit equal to CBD tolls paid
- Input variable: `cbd_tolls_paid` - Amount of tolls paid
- Eligibility variable: `eligible_for_cbd_toll_credit` - Residence + income check

---

## Summary of Required Updates for 2025

### Parameters Needing Updates

1. **Geothermal Credit Cap** (`gov/states/ny/tax/income/credits/geothermal_energy_system/cap.yaml`)
   - Add: `2025-07-01: 10_000`

2. **2025 References** - All parameters should have 2025 references added

### New Parameters Needed

1. **CBD Toll Credit**
   - Income threshold: $60,000
   - Credit rate: 100% of tolls paid

### Parameters Unchanged from 2024

- NYS tax brackets (all filing statuses)
- Standard deductions (all filing statuses)
- Dependent exemption ($1,000)
- EITC match (30%)
- Empire State Child Credit (2025 values already implemented)
- Supplemental tax threshold ($107,650)
- Real property tax credit thresholds
- College tuition credit/deduction
- Household credit amounts
- Pension exclusion ($20,000, age 59.5)
- Solar credit ($5,000, 25%)
- NYC tax brackets
- NYC EITC percentages
- NYC School Tax Credit ($63/$125)
- NYC Household Credit
- NYC CDCC (75% max, $30,000 income limit)

---

## References for Parameter Metadata

```yaml
# For 2025 NY parameters:
reference:
  - title: "2025 Form IT-201-I Instructions"
    href: "https://www.tax.ny.gov/forms/html-instructions/2025/it/it201i-2025.htm"
  - title: "2025 Form IT-201-I Instructions (PDF)"
    href: "https://www.tax.ny.gov/pdf/current_forms/it/it201i.pdf#page=XX"

# For variables:
reference = "https://www.tax.ny.gov/forms/html-instructions/2025/it/it201i-2025.htm"
```

---

## Legal Citations

- **NYS Tax Law Section 601**: Imposition of tax (rates, supplemental tax)
- **NYS Tax Law Section 606**: Credits against tax (EITC, CTC, CDCC, household credit, etc.)
- **NYC Administrative Code Section 11-1701**: NYC tax imposition
- **NYC Administrative Code Section 11-1706(b)**: NYC EITC
