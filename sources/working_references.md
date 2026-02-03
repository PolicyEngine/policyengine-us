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
