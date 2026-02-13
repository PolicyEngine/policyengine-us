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

## Rhode Island LIHEAP Implementation
**Collected**: 2026-02-03
**Implementation Task**: Rhode Island Low Income Home Energy Assistance Program (LIHEAP) eligibility and benefit calculation

---

## Official Program Name

**Federal Program**: Low Income Home Energy Assistance Program (LIHEAP)
**State's Official Name**: Low Income Home Energy Assistance Program (LIHEAP)
**Abbreviation**: LIHEAP
**Administering Agency**: Rhode Island Department of Human Services (DHS)
**Source**: R.I. Gen. Laws Section 39-1-27.12; DHS Program Page

**Variable Prefix**: `ri_liheap`

---

## Program Overview

Rhode Island's LIHEAP is a federally-funded program administered by the Rhode Island Department of Human Services (DHS) through local Community Action Program (CAP) agencies. The program helps eligible low-income households pay their heating bills through federal grants.

### Program Components

1. **Heating Assistance**: A one-time supplemental grant to assist a household in meeting heating costs. The grant is paid directly to heating fuel vendors or utility companies, or in some cases, directly to the applicant.

2. **Crisis Assistance**: A grant to help resolve a home heating crisis caused by:
   - Heat shut-off due to failure to pay a regulated energy bill
   - Inability to pay for deliverable fuel
   - Failure of a heating system that is not repairable

3. **Weatherization**: Services including home insulation, weather stripping, furnace cleaning/repair/replacement, and chimney inspection/cleaning. Households must first apply for heating assistance.

### Source Information
- **Title**: Low Income Home Energy Assistance Program (LIHEAP)
- **URL**: https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-1
- **Effective Date**: FFY 2026 (October 1, 2025 - September 30, 2026)

---

## Income Eligibility

### Income Limit Standard

Rhode Island households are income-eligible for LIHEAP when the household's gross income is **equal to or less than 60 percent of the State Median Income (SMI)** for their household size.

**Legal Authority**:
- Federal: 42 U.S.C. Section 8624(b)(2)(B)
- Regulation: 45 CFR 96.85
- This became **mandatory** as of October 1, 2024

### 60% SMI Calculation Methodology (per 45 CFR 96.85)

The income limits are calculated by taking 60% of the state's estimated median income for a 4-person family and multiplying by the following household size adjustments:

| Household Size | Adjustment Factor |
|----------------|-------------------|
| 1 person | 52% |
| 2 persons | 68% |
| 3 persons | 84% |
| 4 persons | 100% |
| 5 persons | 116% |
| 6 persons | 132% |
| 7 persons | 135% |
| 8 persons | 138% |
| 9 persons | 141% |
| 10 persons | 144% |
| 11 persons | 147% |
| 12 persons | 150% |
| Each additional | +3% |

### Rhode Island SMI for 4-Person Household (from HHS)

| Federal Fiscal Year | 4-Person SMI | 60% of SMI |
|---------------------|--------------|------------|
| FFY 2025 (Oct 2024) | $125,328 | $75,197 |
| FFY 2026 (Oct 2025) | $135,424 | $81,254 |

**Source**: HHS LIHEAP IM2025-02 State Median Income Tables
- https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf

### FFY 2026 Income Limits by Household Size (60% SMI)

| Household Size | Annual (12-Month) | Quarterly (3-Month) | Monthly (1-Month) |
|----------------|-------------------|---------------------|-------------------|
| 1 | $42,252 | $10,563 | $3,521 |
| 2 | $55,252 | $13,813 | $4,604 |
| 3 | $68,253 | $17,063 | $5,687 |
| 4 | $81,254 | $20,313 | $6,771 |
| 5 | $94,254 | $23,563 | $7,854 |
| 6 | $107,255 | $26,813 | $8,937 |
| 7 | $109,692 | $27,423 | $9,141 |
| 8 | $112,130 | $28,032 | $9,344 |
| 9 | $114,568 | $28,642 | $9,547 |
| 10 | $117,005 | $29,251 | $9,750 |
| 11 | $119,443 | $29,860 | $9,953 |
| 12 | $121,881 | $30,470 | $10,156 |
| 13 | $124,318 | $31,079 | $10,359 |
| 14 | $126,756 | $31,689 | $10,563 |

**Source**: RI DHS FFY 2026 Low Income Guidelines
- https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/ffy-2025-low-income-guidelines

### Income Definition

- **Gross income** is used (not net income)
- Income documentation must represent gross income earned in the most recent 4 weeks, 3 months, or 12 months
- Self-employment income is verified by IRS tax forms
- Interest income in excess of $500 annually must be included
- Student income exemption: Full-time students ages 18-23 may have income excluded with proper documentation

**Source**: Rhode Island LIHEAP Administration and Procedures Manual
- https://ripuc.ri.gov/sites/g/files/xkgbur841/files/eventsactions/docket/4290-DHS-DR-PUC-3-6-attachment-LIHEAP-Manual-2020---Final.pdf

---

## Categorical Eligibility

### Rhode Island Does NOT Use Categorical Eligibility

Unlike some states, Rhode Island does **NOT** provide automatic/categorical eligibility for LIHEAP based on participation in:
- SNAP (Supplemental Nutrition Assistance Program)
- SSI (Supplemental Security Income)
- TANF (Temporary Assistance for Needy Families)

All Rhode Island households must meet the 60% SMI income eligibility test regardless of participation in other programs.

**Source**: LIHEAP Clearinghouse - Categorical Eligibility Tables
- https://liheapch.acf.gov/delivery/income_categorical.htm

### SNAP Nominal Payment ("Heat and Eat")

Rhode Island provides an annual **nominal LIHEAP payment of $20.01** to certain SNAP households. This allows eligible SNAP households to claim the Standard Utility Allowance (SUA) and receive higher SNAP benefits.

**Eligibility for Nominal Payment**:
- Household has not received LIHEAP at their current residence for the past 12 months
- Household lives in subsidized housing with heat included in rent
- As of November 1, 2025: Limited to households with an elderly (60+) or disabled member

**Source**: RI DHS FFY 2026 State Plan Summary
- https://dhs.ri.gov/media/9371/download?language=en

---

## FFY 2026 Benefit Matrix (from PDF)

**Source**: Rhode Island Department of Human Services - LIHEAP Grant Amounts Federal Fiscal Year 2026
- URL: /Users/ziminghua/Downloads/RI_BenefitMatrix_2026.pdf (local file)
- Online: https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf
- **Effective Date**: October 1, 2025 through September 30, 2026

**Important Note from Document**: "Moderate matrix dependent on funding levels at FFY 2025, to be input 9/30/2025" - This indicates values may be subject to adjustment based on federal funding.

### Grant Amounts by Income Level and Heating Source

Rhode Island uses **Federal Poverty Guidelines (FPG)** percentages to determine benefit tiers (NOT SMI - SMI is used for eligibility only).

| Category | Income Level (% FPG) | Deliverables | Natural Gas | Electric | Other |
|----------|---------------------|--------------|-------------|----------|-------|
| A | Up to 75% | $861 | $232 | $393 | - |
| B | 76-100% | $805 | $211 | $357 | - |
| C | 101-125% | $752 | $192 | $324 | - |
| D | 126-150% | $704 | $175 | $295 | - |
| E | 151%+ | $657 | $159 | $268 | - |
| F | Subsidized Housing w/ Primary Heating Bill | $657 | $159 | $268 | - |
| G | Heat in Rent Direct Pay to Household | $400 | $400 | $400 | $400 |
| H | Heat in Rent Secondary Electric | - | - | - | $80 |
| I | Heat in Rent Subsidized Housing Secondary Electric | - | - | - | $50 |

### Heating Source Definitions

- **Deliverables**: Oil, propane, kerosene, wood, coal, or other delivered fuels
- **Natural Gas**: Utility-provided natural gas
- **Electric**: Electric heat (baseboard, heat pump, etc.)
- **Other**: Used for special categories (Heat in Rent)

### Minimum and Maximum Benefit Amounts (FFY 2026)

| Measure | Amount | Category |
|---------|--------|----------|
| **Maximum Benefit** | $861 | Deliverables, Up to 75% FPG (Category A) |
| **Minimum Regular Benefit** | $159 | Natural Gas, 151%+ FPG (Category E/F) |
| **Heat in Rent Flat Payment** | $400 | Direct Pay to Household (Category G) |
| **Secondary Electric** | $80 | Heat in Rent Secondary Electric (Category H) |
| **Minimum Benefit** | $50 | Subsidized Housing Secondary Electric (Category I) |

### Comparison: FFY 2025 vs FFY 2026

| Measure | FFY 2025 | FFY 2026 | Change |
|---------|----------|----------|--------|
| Maximum Benefit | $1,285 | $861 | -$424 (-33%) |
| Minimum Benefit | $75 | $50 | -$25 (-33%) |

**Significant reduction in benefits for FFY 2026** - This is consistent with the RI DHS FFY 2026 State Plan Summary which noted that "grant amounts are expected to be smaller than in prior years" due to anticipated changes in federal funding.

### FFY 2026 Income Eligibility Thresholds by FPG (for Benefit Tier Assignment)

The PDF also provides FPG-based income thresholds used to assign households to benefit tiers:

| Household Size | 75% FPG (Annual) | 100% FPG (Annual) | 125% FPG (Annual) | 150% FPG (Annual) |
|----------------|------------------|-------------------|-------------------|-------------------|
| 1 | $11,738 | $15,650 | $19,563 | $23,475 |
| 2 | $15,863 | $21,150 | $31,725 | $31,725 |
| 3 | $19,988 | $26,650 | $33,313 | $39,975 |
| 4 | $24,113 | $32,150 | $40,188 | $48,225 |
| 5 | $28,238 | $37,650 | $47,063 | $56,475 |
| 6 | $32,363 | $43,150 | $53,938 | $64,725 |
| 7 | $36,488 | $48,650 | $60,813 | $72,975 |
| 8 | $40,613 | $54,150 | $67,688 | $81,225 |
| 9 | $44,738 | $59,650 | $74,563 | $89,475 |
| 10 | $48,863 | $65,150 | $81,438 | $97,725 |
| 11 | $52,988 | $70,650 | $88,313 | $105,975 |
| 12 | $57,113 | $76,150 | $95,188 | $114,225 |
| 13 | $61,238 | $81,650 | $102,063 | $122,475 |
| 14 | $65,363 | $87,150 | $108,938 | $130,725 |

**Note**: The 100% FPG column shows monthly values as well ($1,304 for 1 person, etc.) which are used for income verification.

### Benefit Calculation Logic

1. **Determine Eligibility**: Household income must be at or below 60% SMI
2. **Determine Benefit Tier**: Compare household income to FPG thresholds
   - Up to 75% FPG -> Category A (highest benefit)
   - 76-100% FPG -> Category B
   - 101-125% FPG -> Category C
   - 126-150% FPG -> Category D
   - 151%+ FPG (up to 60% SMI) -> Category E (lowest regular benefit)
3. **Determine Heating Source**: Deliverables, Natural Gas, or Electric
4. **Special Categories**:
   - Subsidized housing with primary heating bill -> Category F
   - Heat included in rent -> Category G (flat $400)
   - Heat in rent with separate electric -> Category H ($80)
   - Subsidized housing with heat in rent, secondary electric -> Category I ($50)

### Parameters Needed for Implementation

Based on the FFY 2026 Benefit Matrix, the following parameters are needed:

```yaml
# Benefit amounts by income tier and fuel type
ri_liheap_benefit_deliverables:
  2025-10-01:
    tier_a: 861  # Up to 75% FPG
    tier_b: 805  # 76-100% FPG
    tier_c: 752  # 101-125% FPG
    tier_d: 704  # 126-150% FPG
    tier_e: 657  # 151%+ FPG

ri_liheap_benefit_natural_gas:
  2025-10-01:
    tier_a: 232
    tier_b: 211
    tier_c: 192
    tier_d: 175
    tier_e: 159

ri_liheap_benefit_electric:
  2025-10-01:
    tier_a: 393
    tier_b: 357
    tier_c: 324
    tier_d: 295
    tier_e: 268

# Special categories
ri_liheap_heat_in_rent_payment:
  2025-10-01: 400

ri_liheap_secondary_electric:
  2025-10-01: 80

ri_liheap_subsidized_secondary_electric:
  2025-10-01: 50
```

### References for Parameters

```yaml
reference:
  - title: "Rhode Island LIHEAP Grant Amounts FFY 2026"
    href: "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf"
  - title: "RI DHS LIHEAP Program"
    href: "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-1"
```

---

## Benefit Calculation

### Benefit Determination Factors

LIHEAP Primary Grant amounts are based on:
1. **Household income level**
2. **Household (family) size**
3. **Fuel type** (electric, gas, oil, propane)
4. **Minimum delivery requirements**

### FFY 2025 Benefit Amounts (Previous Year - For Reference)

| Component | Minimum | Maximum |
|-----------|---------|---------|
| Heating Assistance | $75 | $1,285 |
| Winter Crisis | N/A | $1,500 |

**Alternative Source (LIHEAP Clearinghouse)**:
| Component | Minimum | Maximum |
|-----------|---------|---------|
| Heating Assistance | $64 | $1,148 |
| Winter Crisis | N/A | $1,500 |

**Note**: Benefit amounts vary by source due to timing of updates and funding levels.

### FFY 2026 Benefit Amounts (Current Year)

| Component | Minimum | Maximum |
|-----------|---------|---------|
| Heating Assistance | $50 | $861 |
| Winter Crisis | N/A | TBD (likely $1,500) |

Grant amounts for FFY 2026 are **dependent on funding levels** and are **smaller than in prior years** due to anticipated changes in federal funding and guidance.

**Source**: RI DHS FFY 2026 State Plan Summary
- https://dhs.ri.gov/media/9371/download?language=en

### Crisis Assistance Eligibility

Crisis assistance may be issued if:
- Client has the utility shut off, OR
- Client has 1/4 tank or less of heating fuel

**Additional Requirement**: Clients must have $300 or less remaining of their primary heating benefit before applying for crisis assistance.

**Life-Threatening Crisis Definition**: A life-threatening crisis occurs when the client is unable to maintain heat in the home and the overnight temperature is **below 20 degrees Fahrenheit**.

**Source**: RI DHS LIHEAP Program Information

---

## Priority Groups (Vulnerable Populations)

### Statutory Requirement

Per 42 U.S.C. Section 8624, states must ensure "the highest level of assistance will be furnished to those households which have the lowest incomes and the highest energy costs or needs in relation to income, taking into account family size."

### Rhode Island Priority Implementation

Rhode Island gives priority to households with:
- **Elderly member** (age 60+)
- **Disabled member**
- **Young child**

**How Priority is Applied**:
1. **Crisis Grants**: First round of crisis grants available to priority households for several weeks before opening to all eligible households
2. **Weatherization**: Work orders are prioritized in the software system by household composition
3. **Application Processing**: Grant renewal forms mailed in September to give vulnerable populations extra time

**Source**: RI DHS FFY 2026 State Plan Summary; 42 U.S.C. Section 8624
- https://www.law.cornell.edu/uscode/text/42/8624

---

## Program Dates and Seasons

### FFY 2026 Program Dates

| Component | Start Date | End Date |
|-----------|------------|----------|
| Heating Assistance | October 1, 2025 | April 15, 2026 |
| Winter Crisis | October 1, 2025 | May 1, 2026 |
| Weatherization | Year-round | Year-round |

### Application Period

- **New Applications**: Taken from September through May each year
- **Renewal Applications**: Mailed to prior year recipients in September
- **Vendor Notification**: December 1, 2025 (previously November 1)

### Cooling Assistance

Rhode Island DHS is **NOT planning to offer a cooling component** in FFY 2026.

**Source**: RI DHS FFY 2026 State Plan Summary
- https://dhs.ri.gov/media/9371/download?language=en

---

## Citizenship and Immigration Requirements

### Eligible Applicants

- U.S. Citizens
- Permanent legal residents
- Qualified aliens

### Mixed Status Households

"Mixed status households" (e.g., parent is undocumented and children are citizens/lawful immigrants) **may be eligible**. Family income is measured against the household size of the **eligible members only**.

**Source**: RI DHS LIHEAP Eligibility Information
- https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program

---

## LIHEAP Enhancement Plan (State Supplement)

### Legal Authority

R.I. Gen. Laws Section 39-1-27.12 established the Low-Income Home Energy Assistance Program Enhancement Plan to supplement federal LIHEAP funding.

### Funding Mechanism

A surcharge is applied to all electric and gas customer bills:
- **Electric customers**: Up to $10.00 per year
- **Natural gas customers**: Up to $10.00 per year

### Total Revenue Cap

- **Maximum**: $7,500,000 annually
- **Minimum**: $6,500,000 annually

### Use of Enhancement Funds

- Credits applied to accounts of customers receiving federal LIHEAP assistance
- Minimum 5% allocated for customers seeking LIHEAP certification for arrearage plans between April 15 and September 30
- A portion set aside for homeless families/individuals transitioning from shelters into housing (for summer months)

**Source**: R.I. Gen. Laws Section 39-1-27.12
- http://webserver.rilin.state.ri.us/Statutes/title39/39-1/39-1-27.12.HTM
- https://law.justia.com/codes/rhode-island/2012/title-39/chapter-39-1/chapter-39-1-27.12/

---

## Additional Benefits for LIHEAP Recipients

### Reduced Electric Rate

Eligible LIHEAP clients also qualify for a **25% discount** on their electric and/or gas bill through Rhode Island Energy.

**Source**: RI Energy Assistance Programs
- https://www.rienergy.com/site/ways-to-save/assistance-programs/grant-programs

---

## Resource Test

**Resources are NOT counted** for LIHEAP eligibility in Rhode Island. Only income is considered.

**Source**: Economic Progress Institute - Low Income Home Energy & Water Assistance
- https://economicprogressri.org/resources/low-income-home-energy-water-assistance

---

## Appeals Process

Households determined ineligible are notified in writing by the agency regarding the reason for the denial along with documentation explaining the appeal process.

**Appeal Deadline**: **15 business days** from receipt of the denial notice to request a hearing.

**Source**: RI DHS LIHEAP Eligibility Information
- https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program

---

## Non-Simulatable Rules (Architecture Limitation)

The following rules CANNOT be fully simulated in PolicyEngine's single-period architecture:

### Time-Based Requirements
- **12-Month Rule for Nominal Payment**: Household must not have received LIHEAP at current residence for past 12 months [CANNOT TRACK - requires history]
- **Crisis Assistance Waiting Period**: Must have $300 or less remaining of primary heating benefit [CANNOT TRACK - requires prior benefit tracking]

### Historical Tracking Requirements
- **Prior Year Renewal Status**: Renewal applicants are those who received heating assistance the prior year [CANNOT TRACK]

### What CAN Be Simulated

- Current income eligibility (60% SMI test)
- Household size determination
- Priority group identification (elderly, disabled, young child)
- Citizenship/immigration eligibility
- **Benefit amount calculation** (based on income tier and fuel type)

---

## References for Metadata

### For Parameters

```yaml
reference:
  - title: "RI DHS FFY 2026 Low Income Guidelines"
    href: "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/ffy-2025-low-income-guidelines"
  - title: "42 U.S.C. Section 8624 - Applications and requirements"
    href: "https://www.law.cornell.edu/uscode/text/42/8624"
  - title: "45 CFR 96.85 - Income Eligibility"
    href: "https://www.ecfr.gov/current/title-45/section-96.85"
  - title: "HHS LIHEAP IM2025-02 State Median Income Tables"
    href: "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf"
  - title: "Rhode Island LIHEAP Grant Amounts FFY 2026"
    href: "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf"
```

### For Variables

```python
reference = "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program"
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **Rhode Island LIHEAP FFY 2026 State Plan (Full Document)**
   - URL: https://liheapch.acf.gov/docs/2026/state-plans/RI_Plan_2026.pdf
   - Expected content: Complete state plan with detailed program rules, benefit calculation methodology, outreach procedures, and administrative requirements

2. **Rhode Island LIHEAP FFY 2026 Benefit Matrix** (NOW EXTRACTED - see above)
   - URL: https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf
   - Content: Specific benefit amounts by household size, income level, and fuel type combinations

3. **Rhode Island LIHEAP FFY 2026 State Plan Summary**
   - URL: https://dhs.ri.gov/media/9371/download?language=en
   - Expected content: Summary of FFY 2026 state plan including benefit amounts, eligibility criteria, and program dates

4. **Rhode Island LIHEAP FFY 2025 State Plan Summary**
   - URL: https://dhs.ri.gov/media/7571/download?language=en
   - Expected content: Prior year state plan for comparison

5. **Rhode Island Low-Income Home Energy Assistance Program 2025-2026 Application**
   - URL: https://dhs.ri.gov/media/9656/download?language=en
   - Expected content: Application instructions, required documentation, and eligibility information

6. **Rhode Island LIHEAP Administration and Procedures Manual (2020)**
   - URL: https://ripuc.ri.gov/sites/g/files/xkgbur841/files/eventsactions/docket/4290-DHS-DR-PUC-3-6-attachment-LIHEAP-Manual-2020---Final.pdf
   - Expected content: Detailed administrative procedures, income calculation methodology, and eligibility verification requirements

7. **Rhode Island LIHEAP FFY 2025 Income Eligibility Chart**
   - URL: https://www.ebcap.org/wp-content/uploads/2024/08/FFY2025-Eligibility-Chart-LIHEAP.pdf
   - Expected content: Prior year income limits by household size

8. **HHS LIHEAP IM2025-02 State Median Income Table (Attachment 4)**
   - URL: https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf
   - Expected content: Official SMI figures for all states for FFY 2026, including Rhode Island

9. **Rhode Island Public Utilities Commission - Low-Income Ratepayers' Discount Overview**
   - URL: https://ripuc.ri.gov/sites/g/files/xkgbur841/files/2025-08/Low-Income%20Ratepayers'%20Discount%20and%20Funding%20Sources%20-%20Regulatory%20Topic%20Overview%20(08-2025).pdf
   - Expected content: Details on LIHEAP Enhancement Plan funding, rate discounts, and regulatory framework

---

## Implementation Notes

### Existing Federal Parameters

PolicyEngine already has federal-level LIHEAP parameters that can be reused:

1. **HHS State Median Income**: `parameters/gov/hhs/smi/amount.yaml`
   - Contains Rhode Island SMI for 4-person household by year
   - FFY 2026 (2025-10-01): $135,424

2. **SMI Household Size Adjustments**: `parameters/gov/hhs/smi/household_size_adjustment.yaml`
   - First person: 0.52
   - Second to sixth person: +0.16 each
   - Additional person: +0.03 each

3. **LIHEAP SMI Limit**: `parameters/gov/hhs/liheap/smi_limit.yaml`
   - Value: 0.6 (60% of SMI)

### Variable to Calculate SMI Threshold

The existing variable `hhs_smi` calculates the state median income for any SPM unit based on state and household size. The Massachusetts implementation shows how to use this:

```python
# From ma_liheap_state_median_income_threshold.py
def formula(spm_unit, period, parameters):
    p = parameters(period).gov.hhs.liheap
    state_median_income = spm_unit("hhs_smi", period)
    return state_median_income * p.smi_limit  # 0.6 = 60% SMI
```

### State-Specific Parameters Needed

Rhode Island LIHEAP implementation needs:

1. **Benefit amounts by income level and fuel type** (from Benefit Matrix PDF - NOW DOCUMENTED)
2. **Crisis assistance maximum** ($1,500)
3. **Nominal SNAP payment amount** ($20.01)
4. **Program season dates** (if used in eligibility)
5. **Priority group definitions** (elderly age threshold: 60)

---

## Key Contacts and Application Information

- **Administering Agency**: RI Department of Human Services (DHS)
- **Application Phone**: 1-855-MY-RIDHS (1-855-697-4347)
- **TTY**: 7-1-1
- **Mailing Address**: RI DHS, P.O. Box 8709, Cranston, RI 02920-8787
- **Local CAP Agency Finder**: 401-921-4968
- **Online Application**: Available through DHS portal

### Community Action Program (CAP) Agencies

Applications are taken at these local agencies:
- East Bay Community Action Program (EBCAP)
- Community Action Partnership of Providence (CAPP)
- Tri-County Community Action Agency
- Westbay Community Action
- Blackstone Valley Community Action Program (BVCAP)
- Community Care Alliance
- Comprehensive Community Action Program

---

## Summary of Key Values for Implementation

| Parameter | Value | Source |
|-----------|-------|--------|
| Income Limit | 60% of SMI | 42 U.S.C. 8624(b)(2)(B) |
| RI 4-Person SMI (FFY 2026) | $135,424 | HHS IM2025-02 |
| 60% SMI for 4-person (FFY 2026) | $81,254 | Calculated |
| Heating Benefit Min (FFY 2026) | $50 | RI Benefit Matrix |
| Heating Benefit Max (FFY 2026) | $861 | RI Benefit Matrix |
| Heating Benefit Min (FFY 2025) | $75 | RI DHS |
| Heating Benefit Max (FFY 2025) | $1,285 | RI DHS |
| Crisis Assistance Max (FFY 2025) | $1,500 | RI DHS |
| SNAP Nominal Payment | $20.01 | RI DHS State Plan |
| Elderly Age Threshold | 60 years | 42 U.S.C. 8624 |
| Heating Season Start | October 1 | RI DHS |
| Heating Season End | April 15 | RI DHS |
| Crisis Season End | May 1 | RI DHS |
