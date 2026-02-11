# Collected Documentation

## Michigan 2025 Individual Income Tax - Parameter Updates
**Collected**: 2026-01-06
**Implementation Task**: Update Michigan income tax parameters to 2025 values per issue #7120

---

## Official Program Names

**Program**: Michigan Individual Income Tax
**Administering Agency**: Michigan Department of Treasury
**Key Forms**: MI-1040, MI-1040CR, MI-1040CR-7
**Tax Rate**: 4.25% (flat rate, unchanged for 2025)

---

## 2025 Parameter Values - Summary

| Parameter | 2024 Value | 2025 Value | Source |
|-----------|------------|------------|--------|
| Personal Exemption | $5,600 | $5,800 | 446 Withholding Guide |
| Disabled Exemption | $3,300 | $3,400 | 446 Withholding Guide |
| Disabled Veteran Exemption | $500 | $500 | 446 Withholding Guide |
| Homestead Property Value Limit | $160,700 | $165,400 | MI-1040CR Form |
| Homestead Credit Cap | $1,800 | $1,900 | MI-1040CR Form |
| Homestead Reduction Start | $60,700 | $62,500 | MI-1040CR Form |
| Total Household Resources Limit | $69,700 | $71,500 | MI-1040CR Form |
| Tier One Retirement (Single) | $64,040 | $65,897 | Retirement & Pension Benefits |
| Tier One Retirement (Joint) | $128,080 | $131,794 | Retirement & Pension Benefits |

---

## Detailed Parameter Documentation

### 1. Personal Exemption Amount

**2025 Value**: $5,800
**2024 Value**: $5,600
**Change**: +$200

**Source**: Michigan 2025 Income Tax Withholding Guide (Form 446, Rev. 01-25)
- Quote: "Withholding Rate: 4.25% Personal Exemption Amount: $5,800"
- This exemption applies to the filer, spouse, each dependent, and stillborn children

**Legal Authority**: Michigan Legal Code Section 206.30(2)

**References for Parameter**:
```yaml
reference:
  - title: Michigan 2025 Income Tax Withholding Guide (Form 446)
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/SUW/TY2025/446_Withholding-Guide_2025.pdf
  - title: 2025 MI-1040 Instructions
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf
```

---

### 2. Disabled Exemption Amount (Special Exemption)

**2025 Value**: $3,400
**2024 Value**: $3,300
**Change**: +$100

**Applies to**: Individuals who are deaf, blind, hemiplegic, paraplegic, quadriplegic, or totally and permanently disabled

**Note**: A taxpayer who is age 66 by April 30 of the tax year may not claim a totally and permanently disabled exemption (considered retirement age).

**Source**: Michigan 2025 Income Tax Withholding Guide (Form 446)
- Quote: "The special exemption allowance for deaf, blind, hemiplegic, paraplegic, quadriplegic, or totally and permanently disabled is $3,400"

**Legal Authority**: Michigan Legal Code Section 206.30(3)(a)

**References for Parameter**:
```yaml
reference:
  - title: Michigan 2025 Income Tax Withholding Guide (Form 446)
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/SUW/TY2025/446_Withholding-Guide_2025.pdf
  - title: 2025 MI-1040 Instructions
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf
```

---

### 3. Disabled Veteran Exemption Amount

**2025 Value**: $500
**2024 Value**: $500
**Change**: No change

**Applies to**: Qualified disabled veteran, spouse of qualified disabled veteran, or dependent of taxpayer who is a qualified disabled veteran

**Source**: Michigan 2025 Income Tax Withholding Guide (Form 446)
- Quote: "The exemption allowance for qualified disabled veterans is $500"

**Legal Authority**: Michigan Legal Code Section 206.30

**References for Parameter**:
```yaml
reference:
  - title: Michigan 2025 Income Tax Withholding Guide (Form 446)
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/SUW/TY2025/446_Withholding-Guide_2025.pdf
```

---

### 4. Homestead Property Tax Credit - Property Value Limit

**2025 Value**: $165,400
**2024 Value**: $160,700
**Change**: +$4,700

**Rule**: Homesteads with a taxable value greater than this amount are not eligible for the credit (except vacant farmland classified as agricultural)

**Source**: 2025 MI-1040CR Form
- Quote: "Homesteads with a taxable value greater than $165,400 are not eligible for this credit"

**Legal Authority**: Michigan Income Tax Act 206.520(1)

**References for Parameter**:
```yaml
reference:
  - title: 2025 MI-1040CR Form
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR.pdf
  - title: Michigan Income Tax Act 206.520(1)
    href: http://legislature.mi.gov/doc.aspx?mcl-206-520
```

---

### 5. Homestead Property Tax Credit - Maximum Credit Cap

**2025 Value**: $1,900
**2024 Value**: $1,800
**Change**: +$100

**Rule**: The maximum homestead property tax credit is capped at this amount

**Source**: 2025 MI-1040CR Form
- The credit is calculated and then capped at the maximum

**Legal Authority**: Michigan Income Tax Act 206.520(15)

**References for Parameter**:
```yaml
reference:
  - title: 2025 MI-1040CR Form
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR.pdf
  - title: Michigan Income Tax Act 206.520(15)
    href: http://legislature.mi.gov/doc.aspx?mcl-206-520
```

---

### 6. Homestead Property Tax Credit - Reduction Start Threshold

**2025 Value**: $62,500
**2024 Value**: $60,700
**Change**: +$1,800

**Rule**: The computed credit is reduced by 10% for every $1,000 (or part of $1,000) that total household resources exceeds this threshold

**Source**: 2025 MI-1040CR Form
- Quote: "The computed credit (line 12) is reduced by 10 percent for every $1,000 (or part of $1,000) that total household resources exceeds $62,500"

**Legal Authority**: Michigan Income Tax Act 206.520(8)

**References for Parameter**:
```yaml
reference:
  - title: 2025 MI-1040CR Form
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR.pdf
  - title: Michigan Income Tax Act 206.520(8)
    href: http://legislature.mi.gov/doc.aspx?mcl-206-520
```

---

### 7. Homestead Property Tax Credit - Total Household Resources Limit

**2025 Value**: $71,500
**2024 Value**: $69,700
**Change**: +$1,800

**Rule**: Taxpayers with total household resources over this amount are not eligible for a credit in any category

**Source**: 2025 MI-1040CR Form
- Quote: "Taxpayers with total household resources over $71,500 are not eligible for a credit in any category"

**Note**: This threshold equals the reduction start ($62,500) plus $9,000, at which point the 10% reduction per $1,000 completely phases out the credit.

**References for Parameter**:
```yaml
reference:
  - title: 2025 MI-1040CR Form
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR.pdf
  - title: Michigan Homestead Property Tax Credit
    href: https://www.michigan.gov/taxes/iit/tax-guidance/credits-exemptions/hptc
```

---

### 8. Tier One Retirement Deduction Amounts

**2025 Values**:
- Single/Married Filing Separately: $65,897
- Married Filing Jointly: $131,794

**2024 Values**:
- Single/Married Filing Separately: $64,040
- Married Filing Jointly: $128,080

**Change**:
- Single: +$1,857
- Joint: +$3,714

**Eligibility**:
- **Born before 1946 (Tier 1)**: May deduct all qualifying public/federal pension and up to the maximum for private pensions
- **Born 1946-1966**: May deduct 75% of maximum for 2025 ($49,422 single / $98,845 joint)
- **Born 1967 or after**: Not eligible for deduction in 2025 tax year

**Note**: Maximum amounts are adjusted annually by the percentage increase in the United States Consumer Price Index.

**Source**: Michigan Department of Treasury - Retirement and Pension Benefits
- Quote: "The maximum deduction for the 2025 tax year is $65,897 for single or married filing separately, and $131,794 for married filing jointly"

**Legal Authority**: Michigan Legal Code Section 206.30(1)(f)

**References for Parameter**:
```yaml
reference:
  - title: Michigan Retirement and Pension Benefits
    href: https://www.michigan.gov/taxes/iit/tax-guidance/tax-situations/retirement-and-pension-benefits
  - title: Michigan Legal Code Section 206.30(1)(f)
    href: http://legislature.mi.gov/doc.aspx?mcl-206-30
  - title: 2025 MI-1040 Instructions
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf
```

---

### 9. Home Heating Credit Standard Allowances

**Status**: The 2025 tax year MI-1040CR-7 form has not yet been released. Current values are for 2024 tax year.

**2024 Values (filed in 2025)**:
| Exemptions | Standard Allowance |
|------------|-------------------|
| 1 | $581 |
| 2 | $788 |
| 3 | $995 |
| 4 | $1,202 |
| 5 | $1,409 |
| 6 | $1,616 |

**Note**: For tax year 2025, there will be a major form change to MI-1040CR-7, Home Heating Credit Claim. The 2025 values will need to be verified once the form is released.

**Additional Exemption Amount**:
- Senior/disabled claimants receive an additional exemption
- 2024 additional exemption: $207 (difference between 3 and 2 exemption amounts: $995 - $788)

**Source**: Michigan 2024 MI-1040CR-7 Instructions, Table A

**Legal Authority**: Michigan Section 206.527a, Income Tax Act of 1967

**References for Parameter**:
```yaml
reference:
  - title: Michigan 2024 MI-1040CR-7 Home Heating Instructions, Table A
    href: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2024/BOOK_MI-1040CR-7.pdf#page=11
  - title: Michigan Section 206.527a
    href: http://legislature.mi.gov/doc.aspx?mcl-206-527a
```

---

## Tax Rate Confirmation

**2025 Tax Rate**: 4.25% (unchanged)

**Source**: Michigan Department of Treasury Notice
- Quote: "After applying the statutory formula, it has been determined there is no reduction of the Section 51 rate for the 2025 tax year. The rate in effect under Section 51 for the 2025 tax year is therefore 4.25%"

**References**:
```yaml
reference:
  - title: 2025 Tax Year Income Tax Rate for Individuals and Fiduciaries
    href: https://www.michigan.gov/treasury/reference/taxpayer-notices/2025-tax-year-income-tax-rate-for-individuals-and-fiduciaries
  - title: Calculation of State Individual Income Tax Rate Adjustment for 2025 Tax Year
    href: https://www.michigan.gov/treasury/news/2025/05/01/calculation-of-state-individual-income-tax-rate-adjustment-for-2025-tax-year
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

### 1. **2025 MI-1040 Instructions (Complete)**
   - URL: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf
   - Expected content: Complete individual income tax instructions including exemption calculations, deduction instructions, and credit eligibility
   - Key pages: Page 3 (exemption amounts), Page 13 (line-by-line instructions), Page 20+ (retirement deductions)

### 2. **2025 MI-1040 Form**
   - URL: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040.pdf
   - Expected content: The actual tax return form with line numbers and calculations
   - Key pages: Page 1-2 (main form)

### 3. **2025 MI-1040CR Form (Homestead Property Tax Credit)**
   - URL: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR.pdf
   - Expected content: Homestead property tax credit form with 2025 thresholds
   - Key pages: Page 1 (line 9 - taxable value $165,400), Page 2 (line 38 - max credit $1,900)

### 4. **2025 MI-1040CR-2 Book (Veterans/Blind)**
   - URL: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR-2-Book.pdf
   - Expected content: Instructions for veterans and blind homestead property tax credit with specific thresholds

### 5. **2025 Withholding Guide (Form 446)**
   - URL: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/SUW/TY2025/446_Withholding-Guide_2025.pdf
   - Expected content: Withholding tables, personal exemption amounts, disabled exemption amounts
   - Key pages: Page 1 (exemption amounts: $5,800 personal, $3,400 disabled, $500 veteran)

### 6. **2025 MI-1040CR-7 Home Heating Credit Instructions**
   - URL: Not yet available (2024 form: https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2024/BOOK_MI-1040CR-7.pdf)
   - Expected content: 2025 standard allowance amounts (Table A), income limits
   - Note: Per Michigan Treasury, there will be a major form change for 2025. Values should be verified when released.

---

## Implementation Notes

### Parameters to Update

The following parameter files need 2025-01-01 values added:

1. **Personal Exemption**: `gov/states/mi/tax/income/exemptions/personal.yaml`
   - Add: `2025-01-01: 5_800`

2. **Disabled Exemption**: `gov/states/mi/tax/income/exemptions/disabled/amount/base.yaml`
   - Add: `2025-01-01: 3_400`

3. **Homestead Property Value Limit**: `gov/states/mi/tax/income/credits/homestead_property_tax/property_value_limit.yaml`
   - Add: `2025-01-01: 165_400`

4. **Homestead Credit Cap**: `gov/states/mi/tax/income/credits/homestead_property_tax/cap.yaml`
   - Add: `2025-01-01: 1_900`

5. **Homestead Reduction Start**: `gov/states/mi/tax/income/credits/homestead_property_tax/reduction/start.yaml`
   - Add: `2025-01-01: 62_500`

6. **Tier One Retirement Amount**: `gov/states/mi/tax/income/deductions/retirement_benefits/tier_one/amount.yaml`
   - Add for SINGLE: `2025-01-01: 65_897`
   - Add for JOINT: `2025-01-01: 131_794`
   - Add for SURVIVING_SPOUSE: `2025-01-01: 65_897`
   - Add for HEAD_OF_HOUSEHOLD: `2025-01-01: 65_897`
   - Add for SEPARATE: `2025-01-01: 65_897`

7. **Home Heating Credit Standard Base**: `gov/states/mi/tax/income/credits/home_heating/standard/base.yaml`
   - **Status**: 2025 values not yet available; form release pending with major changes
   - Current 2024 values should remain; 2025 values to be added when MI-1040CR-7 2025 is released

### Note on Uprating

Several of these parameters have automatic uprating configured. However, the actual published values should be used rather than relying on uprating, as Michigan Treasury publishes specific amounts that may differ slightly from mechanical uprating calculations.

---

## Sources Consulted

### Official Michigan Government Sources

1. [Michigan Department of Treasury - Tax Forms](https://www.michigan.gov/taxes/iit-forms/2025-individual-income-tax-forms)
2. [Michigan Homestead Property Tax Credit](https://www.michigan.gov/taxes/iit/tax-guidance/credits-exemptions/hptc)
3. [Michigan Retirement and Pension Benefits](https://www.michigan.gov/taxes/iit/tax-guidance/tax-situations/retirement-and-pension-benefits)
4. [Michigan Withholding Tax Information](https://www.michigan.gov/taxes/business-taxes/withholding/calendar-year-tax-information)
5. [Michigan Home Heating Credit Information](https://www.michigan.gov/taxes/questions/iit/accordion/heating/home-heating-credit-information-1)
6. [2025 Tax Year Income Tax Rate Notice](https://www.michigan.gov/treasury/reference/taxpayer-notices/2025-tax-year-income-tax-rate-for-individuals-and-fiduciaries)

### Legal Authority

1. [Michigan Compiled Laws Section 206.30](http://legislature.mi.gov/doc.aspx?mcl-206-30) - Exemptions and deductions
2. [Michigan Compiled Laws Section 206.520](http://legislature.mi.gov/doc.aspx?mcl-206-520) - Homestead property tax credit
3. [Michigan Compiled Laws Section 206.527a](http://legislature.mi.gov/doc.aspx?mcl-206-527a) - Home heating credit

---

## Validation Checklist

- [x] Personal exemption 2025 value confirmed: $5,800
- [x] Disabled exemption 2025 value confirmed: $3,400
- [x] Disabled veteran exemption 2025 value confirmed: $500
- [x] Homestead property value limit 2025 confirmed: $165,400
- [x] Homestead credit cap 2025 confirmed: $1,900
- [x] Homestead reduction start 2025 confirmed: $62,500
- [x] Total household resources limit 2025 confirmed: $71,500
- [x] Tier one retirement single 2025 confirmed: $65,897
- [x] Tier one retirement joint 2025 confirmed: $131,794
- [ ] Home heating credit 2025 standard allowances: PENDING (form not yet released)
- [x] Tax rate 2025 confirmed: 4.25%

---
---

## Maryland State Income Tax - 2025 Implementation
**Collected**: 2026-02-11
**Implementation Task**: Document 2025 Maryland income tax rules including new brackets, standard deduction changes, itemized deduction phase-out, capital gains surtax, and credits.

---

## Official Program Name

**Federal Program**: State Income Tax
**State's Official Name**: Maryland Income Tax
**Administering Agency**: Comptroller of Maryland
**Source**: Maryland Tax-General Article, Title 10

**Variable Prefix**: `md_income_tax` (existing pattern in codebase)

---

## Key Legislative Change for 2025

**House Bill 352 - Budget Reconciliation and Financing Act of 2025**
- Signed by Governor Wes Moore on May 20, 2025
- Effective: July 1, 2025, for taxable years beginning after December 31, 2024
- Purpose: Address state's $3 billion budget deficit
- Primary reference: [HB 352 Enrolled](https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf)

---

## State Income Tax Rates and Brackets (2025)

### Source Information
- **Title**: Maryland Tax-General Section 10-105 - State Income Tax Rates
- **Citation**: Md. Code, Tax-General SS 10-105
- **URL**: https://govt.westlaw.com/mdc/Document/N5C14CC91D9D311E2A5EFA1428CB399FF
- **Effective Date**: Taxable years beginning after December 31, 2024

### Key Changes for 2025
Maryland expanded from 8 tax brackets to 10, adding two new high-income brackets:
- New 6.25% bracket for high earners
- New 6.50% bracket for top earners (highest rate increased from 5.75%)

### Single Filers / Married Filing Separately

| Taxable Income | Rate |
|----------------|------|
| $0 - $1,000 | 2.00% |
| $1,001 - $2,000 | 3.00% |
| $2,001 - $3,000 | 4.00% |
| $3,001 - $100,000 | 4.75% |
| $100,001 - $125,000 | 5.00% |
| $125,001 - $150,000 | 5.25% |
| $150,001 - $250,000 | 5.50% |
| $250,001 - $500,000 | 5.75% |
| $500,001 - $1,000,000 | **6.25% (NEW)** |
| Over $1,000,000 | **6.50% (NEW)** |

### Married Filing Jointly / Head of Household / Surviving Spouse

| Taxable Income | Rate |
|----------------|------|
| $0 - $1,000 | 2.00% |
| $1,001 - $2,000 | 3.00% |
| $2,001 - $3,000 | 4.00% |
| $3,001 - $150,000 | 4.75% |
| $150,001 - $175,000 | 5.00% |
| $175,001 - $225,000 | 5.25% |
| $225,001 - $300,000 | 5.50% |
| $300,001 - $600,000 | 5.75% |
| $600,001 - $1,200,000 | **6.25% (NEW)** |
| Over $1,200,000 | **6.50% (NEW)** |

### References for Parameters
```yaml
reference:
  - title: "SS 10-105 (a)(1). State income tax rates"
    href: "https://govt.westlaw.com/mdc/Document/N5C14CC91D9D311E2A5EFA1428CB399FF"
  - title: "Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025"
    href: "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=161"
```

---

## Standard Deduction (2025)

### Source Information
- **Title**: Maryland Standard Deduction Changes
- **Citation**: HB 352, Page 164
- **URL**: https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=164
- **Effective Date**: Tax year 2025

### Key Changes for 2025
**Major structural change**: Maryland eliminated the income-based phase-in calculation and moved to a **flat standard deduction** for all filers of the same filing status.

Previous system (pre-2025):
- Calculated as 15% of Maryland AGI
- Minimum: $1,500-$1,850 depending on status
- Maximum: $2,250-$5,450 depending on status

New system (2025 onward):
- Flat amount based on filing status
- Subject to cost-of-living (chained CPI) adjustments

### 2025 Standard Deduction Amounts

| Filing Status | Amount |
|---------------|--------|
| Single | $3,350 |
| Married Filing Separately | $3,350 |
| Married Filing Jointly | $6,700 |
| Head of Household | $6,700 |
| Surviving Spouse | $6,700 |

### References for Parameters
```yaml
reference:
  - title: "Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025 (page 164 - chained CPI indexing)"
    href: "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=164"
  - title: "Maryland new tax year update - exemptions and deductions"
    href: "https://www.marylandtaxes.gov/new-tax-year-update.php"
```

---

## Itemized Deduction Phase-Out (NEW for 2025)

### Source Information
- **Title**: Maryland Itemized Deduction Limitation
- **Citation**: HB 352, Page 166-167
- **URL**: https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=166
- **Effective Date**: Tax year 2025

### Key Rules
Beginning in tax year 2025, taxpayers with high federal adjusted gross income must reduce their itemized deductions.

**Phase-out Formula**:
```
Reduction = 7.5% x (FAGI - Threshold)
Allowable Itemized Deductions = Otherwise Allowable - Reduction
```

### Phase-Out Thresholds

| Filing Status | FAGI Threshold |
|---------------|----------------|
| Single | $200,000 |
| Head of Household | $200,000 |
| Married Filing Jointly | $200,000 |
| Married Filing Separately | $100,000 |
| Surviving Spouse | $200,000 |

**Phase-Out Rate**: 7.5%

### References for Parameters
```yaml
reference:
  - title: "Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025"
    href: "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=166"
```

---

## Personal Exemptions

### Source Information
- **Title**: Maryland Personal Exemptions
- **Citation**: Md. Code, Tax-General SS 10-211
- **URL**: https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-iii-exemptions/section-10-211-individuals-other-than-fiduciaries
- **Effective Date**: Ongoing (no changes in 2025)

### Exemption Amount
The personal exemption is **$3,200 per exemption** but phases out based on federal AGI.

### Phase-Out Schedule (Single/Married Filing Separately)

| FAGI | Exemption Amount |
|------|------------------|
| Up to $100,000 | $3,200 |
| $100,001 - $125,000 | $1,600 |
| $125,001 - $150,000 | $800 |
| Over $150,000 | $0 |

### Phase-Out Schedule (Joint Filers/Head of Household/Surviving Spouse)

| FAGI | Exemption Amount |
|------|------------------|
| Up to $150,000 | $3,200 |
| $150,001 - $175,000 | $1,600 |
| $175,001 - $200,000 | $800 |
| Over $200,000 | $0 |

### Additional Exemptions
- **Aged exemption**: $1,000 for taxpayers age 65 or older
- **Blind exemption**: $1,000 for blind taxpayers
- **Aged dependent exemption**: Additional amount for aged dependents

### References for Parameters
```yaml
reference:
  - title: "Part III - Exemptions Section 10-211 Individuals Other Than Fiduciaries"
    href: "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-iii-exemptions/section-10-211-individuals-other-than-fiduciaries"
  - title: "Maryland 2024 State & Local Tax Forms & Instructions - Exemption Amount Chart"
    href: "https://www.marylandtaxes.gov/forms/24-forms/Resident-Booklet.pdf#page=12"
```

---

## Capital Gains Surtax (NEW for 2025)

### Source Information
- **Title**: Maryland Capital Gains Surtax
- **Citation**: HB 352, Page 163-164
- **URL**: https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=163
- **Effective Date**: Taxable years beginning after December 31, 2024

### Key Rules
A new **2% surtax** applies to net capital gains for high-income taxpayers.

**Threshold**: Federal Adjusted Gross Income exceeding $350,000

**Rate**: 2% of net capital gains

**Exclusions**:
- Primary residence sales under $1,500,000
- Certain gains tied to Section 179 property

### References for Parameters
```yaml
reference:
  - title: "Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025"
    href: "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=163"
```

---

## Local/County Income Tax

### Source Information
- **Title**: Maryland County Income Tax Rates
- **URL**: https://help.nfc.usda.gov/bulletins/2025/1737141865.htm
- **Effective Date**: 2025

### Key Change for 2025
**Maximum local tax rate increased from 3.20% to 3.30%**

### 2025 County Tax Rates

| County | Rate | Notes |
|--------|------|-------|
| Allegany | 3.03% | Flat |
| Anne Arundel | 2.70% - 3.20% | Graduated |
| Baltimore County | 3.20% | Flat |
| Baltimore City | 3.20% | Flat |
| Calvert | 3.20% | Flat (updated 2025) |
| Caroline | 3.20% | Flat |
| Carroll | 3.03% | Flat |
| Cecil | 2.74% | Flat (updated 2025) |
| Charles | 3.03% | Flat |
| Dorchester | 3.30% | Flat (increased from 3.20% in 2025) |
| Frederick | 2.25% - 3.20% | Graduated |
| Garrett | 2.65% | Flat |
| Harford | 3.06% | Flat |
| Howard | 3.20% | Flat |
| Kent | 3.20% | Flat |
| Montgomery | 3.20% | Flat |
| Prince George's | 3.20% | Flat |
| Queen Anne's | 3.20% | Flat |
| St. Mary's | 3.20% | Flat (updated 2025) |
| Somerset | 3.20% | Flat |
| Talbot | 2.40% | Flat |
| Washington | 2.95% | Flat |
| Wicomico | 3.20% | Flat |
| Worcester | 2.25% | Flat |

### Graduated Local Tax Tables

**Anne Arundel County** (2025):
| Taxable Income | Rate |
|----------------|------|
| $1 - $50,000 | 2.70% |
| Over $50,000 | 2.94% |
(For Single, Married Filing Separately, or Dependent)

| Taxable Income | Rate |
|----------------|------|
| $1 - $25,000 | 2.25% |
| $25,001 - $100,000 | 2.75% |
| $100,001 - $250,000 | 2.96% |
| Over $250,000 | 3.20% |
(For Married Filing Jointly, Head of Household, Qualifying Surviving Spouse)

**Frederick County** (2025):
Similar graduated structure based on filing status.

### References for Parameters
```yaml
reference:
  - title: "Maryland State and Counties Income Tax Withholding"
    href: "https://help.nfc.usda.gov/bulletins/2025/1737141865.htm"
  - title: "2025 Maryland State and Local Withholding Information"
    href: "https://www.marylandcomptroller.gov/content/dam/mdcomp/md/state-payroll/memos/2025/2025-Maryland-State-and-Local-Withholding-Information.pdf"
```

---

## Tax Credits

### Earned Income Tax Credit (EITC)

**Source**: Md. Code, Tax-General SS 10-704

**Match Rates**:
- **Refundable EITC**: 45% of federal EITC (for filers with children or married)
- **Non-refundable EITC**: Additional percentage for married or with child
- **Unmarried Childless**: Different match rate applies

**Eligibility**: Must qualify for and claim federal EITC

### References
```yaml
reference:
  - title: "Md. Code, Tax-Gen. SS 10-704(c)(2)(ii)"
    href: "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"
  - title: "Maryland 2024 State & Local Tax Forms & Instructions - Line 22 - Earned Income Credit"
    href: "https://www.marylandtaxes.gov/forms/24-forms/Resident-Booklet.pdf#page=14"
```

---

### Child Tax Credit (CTC)

**Source**: Md. Code, Tax-General SS 10-751

**Credit Amount**: $500 per eligible child

**Eligibility**:
- Federal AGI of $15,000 or less
- Child must be under age 6 OR disabled child under age 17

**Note**: Maryland will offer fully refundable Child Tax Credits starting in 2026.

### References
```yaml
reference:
  - title: "Md. Code, Tax-Gen. SS 10-751 (a)(2)(ii.)"
    href: "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
  - title: "Maryland 2024 Resident Tax Forms and Instructions"
    href: "https://www.marylandtaxes.gov/forms/24-forms/Resident-Booklet.pdf#page=27"
```

---

### Child and Dependent Care Credit (CDCC)

**Source**: Md. Code, Tax-General SS 10-716

**Match Rate**: 32% of federal CDCC

**Refundable portion**: Available for lower-income filers (AGI cap applies)

### References
```yaml
reference:
  - title: "Md. Code, Tax-Gen. SS 10-716 (c)(1)"
    href: "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care"
  - title: "Maryland 2024 Form 502 CR Instructions"
    href: "https://marylandtaxes.gov/forms/24-forms/502CR.pdf#page=7"
```

---

### Poverty Line Credit

**Source**: Md. Code, Tax-General SS 10-709

**Credit Amount**: Up to 5% of earned income

**Eligibility**:
- Earned income and Federal AGI plus additions below poverty level for household size
- Nonrefundable credit

### References
```yaml
reference:
  - title: "MD. Tax - General Code Ann. SS 10-709"
    href: "https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-709/"
  - title: "Maryland 2024 State & Local Tax Forms & Instructions - Line 23 - Poverty Level Credit"
    href: "https://www.marylandtaxes.gov/forms/24-forms/Resident-Booklet.pdf#page=14"
```

---

### Senior Tax Credit

**Source**: Technical Bulletin No. 51

**Credit Amount**: Up to $1,000 (nonrefundable)

**Eligibility**:
- Age 65 or older on last day of tax year
- Income thresholds vary by filing status:
  - Single: FAGI up to $100,000
  - Joint/HoH/Surviving Spouse: FAGI up to $150,000

### References
```yaml
reference:
  - title: "Technical Bulletin No. 51 - Senior Citizens and Maryland Income Tax"
    href: "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/technical-bulletins/tb-51.pdf"
```

---

## Subtractions from Income

### Social Security Subtraction
- Fully subtracted from Maryland AGI for qualifying taxpayers
- Part of the Maryland Retirement Tax Reduction Act of 2022

### Pension Subtraction
- Maximum amount varies by age and income
- Minimum age: 65

### Two-Income Subtraction
- For married couples filing jointly where both spouses have earned income
- Maximum subtraction applies

### Dependent Care Subtraction
- For child care expenses
- Year offset applies

---

## Summary of 2025 Changes

| Component | Pre-2025 | 2025 Change |
|-----------|----------|-------------|
| Top State Tax Rate | 5.75% | 6.50% |
| Number of Brackets | 8 | 10 |
| Standard Deduction | Income-based (15% of AGI) | Flat ($3,350 single / $6,700 joint) |
| Itemized Deduction Limit | None | 7.5% phase-out above $200,000 FAGI |
| Capital Gains Surtax | None | 2% for FAGI > $350,000 |
| Max Local Tax Rate | 3.20% | 3.30% |

---

## PDFs for Future Reference (Maryland)

The following PDFs contain additional information but could not be extracted directly:

1. **2025 Resident Booklet - Maryland Tax Forms and Instructions**
   - URL: https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf
   - Expected content: Complete 2025 tax forms, instructions, tax tables, worksheets, and filing guidance
   - Key pages: Tax computation worksheets, exemption charts, credit instructions

2. **Tax Alert - Changes to Standard and Itemized Deductions and State/Local Income Tax Rates from 2025 Legislative Session**
   - URL: https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/alerts/tax-alert-changes-to-standard-and-itemized-deductions-and-to-state-and-local-income-tax-rates-from-the-2025-legislative-session.pdf
   - Expected content: Official tax alert detailing all 2025 changes

3. **Maryland Withholding Tax Facts January 2025**
   - URL: https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/facts/Withholding-Tax-Facts-2025.pdf
   - Expected content: Withholding tables, exemption allowances, calculation methods

4. **2025 Maryland State and Local Withholding Information**
   - URL: https://www.marylandcomptroller.gov/content/dam/mdcomp/md/state-payroll/memos/2025/2025-Maryland-State-and-Local-Withholding-Information.pdf
   - Expected content: Complete county tax rate tables, graduated rate schedules

5. **House Bill 352 - Budget Reconciliation and Financing Act of 2025 (Enrolled)**
   - URL: https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf
   - Expected content: Full legislative text of all 2025 tax changes
   - Key pages:
     - Page 161: Income tax rate changes
     - Page 163-164: Capital gains surtax
     - Page 164: Standard deduction changes
     - Page 166-167: Itemized deduction phase-out

6. **2025 Tax Updates Webinar Presentation**
   - URL: https://www.marylandcomptroller.gov/content/dam/mdcomp/md/legal-publications/2025-tax-updates-webinar-presentation.pdf
   - Expected content: Summary presentation of all 2025 tax changes

---

## Existing Implementation Status

The codebase already has Maryland income tax implemented at:
`policyengine_us/parameters/gov/states/md/tax/income/`

**Parameters already updated for 2025:**
- Tax rate brackets (all filing statuses) - includes new 6.25% and 6.50% brackets
- Standard deduction flat amounts
- Itemized deduction phase-out (threshold and rate)
- Capital gains surtax (rate and threshold)

**Variables in place:**
- `md_income_tax` - Final state income tax
- `md_taxable_income` - Taxable income calculation
- `md_standard_deduction` - Standard deduction
- `md_itemized_deductions` - Itemized deductions with phase-out
- `md_exemptions` - Personal exemptions
- `md_eitc` - Earned Income Tax Credit
- `md_ctc` - Child Tax Credit
- `md_cdcc` - Child and Dependent Care Credit
- `md_poverty_line_credit` - Poverty Line Credit
- `md_capital_gains_surtax` - Capital gains surtax
- `md_local_income_tax_before_credits` - Local/county income tax

---

## Sources (Maryland)

### Official Government Sources
- [Maryland Comptroller's Office](https://www.marylandcomptroller.gov/)
- [Maryland Tax Guidance](https://www.marylandtaxes.gov/)
- [Maryland General Assembly - HB 352](https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/hb0352)
- [Maryland Code - Tax General](https://govt.westlaw.com/mdc/)

### Secondary Sources
- [RSM - Maryland Budget Tax Changes](https://rsmus.com/insights/tax-alerts/2025/maryland-budget-adds-new-taxes-increases-rates.html)
- [Gordon Feinblatt - Maryland Tax Alert 2025](https://www.gfrlaw.com/what-we-do/insights/maryland-tax-alert-2025)
- [PBMares - Major Maryland Tax Updates for 2025](https://www.pbmares.com/major-maryland-tax-updates-for-2025/)
- [USDA NFC - Maryland State Income Tax](https://help.nfc.usda.gov/bulletins/2025/1756838508.htm)
