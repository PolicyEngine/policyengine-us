# Arkansas 2025 Income Tax — Working References

Source: [AR1000F/AR1000NR Instructions (2025)](https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf)
Additional: [2025 Tax Tables (separate PDF)](https://www.dfa.arkansas.gov/wp-content/uploads/TaxTables_FI_2025.pdf)

## Page Offset
PDF page = instruction page (no offset). Page 1 is the cover.

## Special Information for 2025 (PDF page 5)

- **Tax Rate Reduction**: Marginal income tax rates for 2025 are **3.9%** (Act 1 of Second Extraordinary Session of 2024)
- **Additional Tax Credit for Qualified Individuals**: Net income up to **$27,600** (Act 1 of Second Extraordinary Session of 2021)
- **Developmentally Disabled Credit**: Eliminated 5-year recertification requirement; form changed from AR1000RC5 to AR1000-DD

## Standard Deduction (PDF page 14, line 26-27 instructions)

| Filing Status | 2025 Amount | 2024 Amount (repo) |
|---------------|-------------|-------------------|
| Single | $2,470 | $2,410 |
| Married Filing Joint | $4,940 | $4,820 |
| Head of Household | $2,470 | $2,410 |
| Married Filing Separately | $2,470 each | $2,410 |
| Surviving Spouse | $2,470 | $2,410 |

## Personal Tax Credits (PDF page 12, line 7A-7C instructions)

- **$29** per credit (same as prior years)
- Additional $29 "65 Special" for taxpayers age 65+ not claiming retirement income exemption on line 18

## Retirement/Disability Benefits Exemption (PDF pages 10-12)

- **$6,000** per taxpayer (same as prior years)
- Combined limit from all plans (employer pension + IRA) cannot exceed $6,000 per taxpayer

## Capital Gains (PDF page 12)

- Loss cap: **$3,000** ($1,500 per taxpayer for filing status 4 or 5)
- Home sale exemption: $250,000 per taxpayer ($500,000 joint)

## Tax Rates & Brackets (PDF pages 25-30 in main booklet, also in TaxTables_FI_2025.pdf)

**2024 rate structure** (from repo rate.yaml):
- Bracket 1: 0% up to threshold (2024: $5,500)
- Bracket 2: 2% (2024: $5,500 - $10,900)
- Bracket 3: 3% (2024: $10,900 - $15,600)
- Bracket 4: 3.4% (2024: $15,600 - $25,700)
- Bracket 5: 3.9% (2024: $25,700+)

**2025**: Top rate confirmed as 3.9%. Thresholds have uprating applied. Agents must derive 2025 thresholds from the regular tax table or from the indexed brackets document at www.dfa.arkansas.gov/incometax

**For $100,001+ net taxable income**: Tax = **$3,809 + 3.9% of excess over $100,000** (PDF page 30)

## Tax Reduction (reduction.yaml)

The reduction parameter is a complex bracket-by-bracket schedule that phases down the effective tax as income increases. In 2024 it has entries from $5,500 to $95,501 with reductions from $109.98 down to $87.40. Agents must derive the 2025 reduction values from the regular tax table.

## Low Income Tax Tables (PDF pages 23-25, also in TaxTables_FI_2025.pdf)

| Filing Status | AGI Limit | Table Location |
|--------------|-----------|---------------|
| Single (FS 1) | $0 - $17,500 | PDF page 23 |
| HoH/Surviving Spouse, 1 or no deps (FS 3/6) | $0 - $25,300 | PDF page 23 |
| HoH/Surviving Spouse, 2+ deps (FS 3/6) | $0 - $29,000 | PDF page 24 |
| Joint, 1 or no deps (FS 2) | $0 - $29,000 | PDF page 24 |
| Joint, 2+ deps (FS 2) | $0 - $36,100 | PDF page 24-25 |

Note: Standard deduction is built into the low income tables. Cannot use if itemizing or using military/pension exemptions.

## Additional Tax Credit for Qualified Individuals (PDF page 20)

| Income Range | Credit |
|-------------|--------|
| $0 - $26,500 | $60 |
| $26,501 - $26,600 | $55 |
| $26,601 - $26,700 | $50 |
| $26,701 - $26,800 | $45 |
| $26,801 - $26,900 | $40 |
| $26,901 - $27,000 | $35 |
| $27,001 - $27,100 | $30 |
| $27,101 - $27,200 | $25 |
| $27,201 - $27,300 | $20 |
| $27,301 - $27,400 | $15 |
| $27,401 - $27,500 | $10 |
| $27,501 - $27,600 | $5 |
| $27,601+ | $0 |

- For Filing Status 2 (Joint): double the credit
- For Filing Status 4 (MFS Same Return): compute for each spouse separately, then add
- Net income = line 28 (net taxable income)

## Credits Summary (PDF pages 14-15)

### Non-Refundable Credits
- Line 34: Personal tax credits ($29 each)
- Line 35: Child/Dependent Care Credit (Form AR2441)
- Line 36: Other credits via AR1000TC:
  - State Political Contribution Credit
  - Other State Tax Credit
  - Credit for Adoption Expenses
  - Phenylketonuria Disorder Credit
  - Stillborn Child Credit
  - Additional Tax Credit for Qualified Individuals
  - Individuals with Developmental Disabilities Credit
  - Business Incentive Credits

### Refundable Credits
- Line 43: Early Childhood Program Credit (Form AR2441 + AR1000EC)

## Mileage Rates (PDF page 19)

- Business: 70 cents/mile
- Charitable: 14 cents/mile
- Medical/Moving: 21 cents/mile

## Section 179 (PDF page 19)

- Deduction limit: $1,250,000
- Cost of qualifying property limit: $3,130,000
- Phase-out: dollar for dollar from $3,130,000 to $4,270,000

## Files Referenced

### Parameters to update
- `policyengine_us/parameters/gov/states/ar/tax/income/rates/main/rate.yaml` (2024 latest)
- `policyengine_us/parameters/gov/states/ar/tax/income/rates/main/reduction.yaml` (2024 latest)
- `policyengine_us/parameters/gov/states/ar/tax/income/deductions/standard.yaml` (2024 latest)
- `policyengine_us/parameters/gov/states/ar/tax/income/rates/low_income_tax_tables/` (7 files, 2021 latest)
- `policyengine_us/parameters/gov/states/ar/tax/income/credits/` (~10 files)
- `policyengine_us/parameters/gov/states/ar/tax/income/exemptions/` (2021 latest)
- `policyengine_us/parameters/gov/states/ar/tax/income/gross_income/` (2021 latest)

### Rendered PDF Pages
- Main booklet: `/tmp/ar-2025-page-{01..38}.png` (300 DPI)
- Tax tables: `/tmp/ar-2025-tax-tables-page-{01..NN}.png` (300 DPI)
- Extracted text: `/tmp/ar-2025-booklet.txt` and `/tmp/ar-2025-tax-tables.txt`
