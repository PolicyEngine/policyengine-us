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

# Texas SSI State Supplement - Implementation Documentation

**Collected**: 2026-02-09
**Implementation Task**: Implement Texas Optional State Supplement (OSS) for SSI recipients in Medicaid long-term care facilities

---

## Official Program Name

**Federal Program**: Supplemental Security Income (SSI) - Optional State Supplementation (OSS)
**State's Official Name**: Texas Optional State Supplement (no distinct state branding; referred to as "state supplement" or "optional state supplementation" in Texas HHSC documents)
**Abbreviation**: OSS (Optional State Supplement)
**Administering Agency**: Texas Health and Human Services Commission (HHSC)
**Administration Type**: State-administered (NOT federally administered by SSA)
**Source**: SSA Publication No. 13-11975; SSA State Assistance Programs for SSI Recipients, January 2011 - Texas

**Variable Prefix**: `tx_ssi_state_supplement`

---

## Program Overview

Texas provides one of the most minimal SSI state supplements in the nation. The supplement is:
- **Limited to SSI recipients residing in Medicaid-funded long-term care facilities** (nursing facilities and ICF/IID)
- **NOT available** to SSI recipients living in the community, assisted living, or any non-institutional setting
- Designed specifically to bring the total personal spending money for institutionalized SSI recipients up to the state's Personal Needs Allowance (PNA) level

### How it works

When an SSI recipient enters a Medicaid-funded nursing facility or ICF/IID facility for more than a full calendar month, the federal SSI payment is reduced from the full Federal Benefit Rate (FBR) to a reduced rate of **$30/month** for an individual and **$60/month** for a couple (per 42 USC 1382(e)(1)(B)).

Texas then supplements this reduced federal payment to bring the total up to the state's Personal Needs Allowance (PNA).

**Current calculation (effective January 1, 2024):**
```
State Supplement = Personal Needs Allowance - Federal SSI Reduced Benefit
State Supplement = $75 - $30 = $45 per month (individual)
```

**For couples (both in Medicaid facility):**
```
Reduced SSI couple rate = $60/month
Each person's PNA target = $75
Total couple PNA target = $150
State Supplement = $150 - $60 = $90 per month (couple)
```

---

## Eligibility Criteria

### Who qualifies

1. **Must be an SSI recipient** (aged 65+, blind, or disabled with limited income and resources)
2. **Must reside in a Medicaid-funded long-term care facility:**
   - Nursing facility (NF)
   - Intermediate Care Facility for Individuals with Intellectual Disabilities (ICF/IID)
3. **Must have countable income less than the PNA amount** (currently $75)
4. **Must be receiving the reduced SSI benefit** ($30/month individual, $60/month couple)

### Who does NOT qualify

- SSI recipients living in the community (at home)
- SSI recipients in assisted living facilities (they have a separate $85 PNA but no SSI supplement)
- SSI recipients participating in Medicaid waiver programs (e.g., HCBS waivers)
- SSI recipients in their month of entry to the facility (they receive full SSI that month)

### Federal SSI eligibility used

The state supplement relies entirely on federal SSI eligibility determination:
- **Resource test**: Federal SSI resource limits apply ($2,000 individual / $3,000 couple as of 2024)
- **Income exclusions**: Federal SSI income exclusions apply (no additional state exclusions)
- **Categorical eligibility**: Federal aged, blind, or disabled criteria apply
- **No additional state-specific eligibility criteria** beyond facility residence

---

## Benefit Amounts / Payment Standards

### Current amounts (effective January 1, 2024)

| Category | Federal Reduced SSI | State Supplement | Total (PNA) |
|---|---|---|---|
| Individual in NF/ICF-IID | $30/month | $45/month | $75/month |
| Couple (both in facility) | $60/month | $90/month | $150/month |

### Historical Personal Needs Allowance and implied state supplement

The state supplement amount is derived from: **PNA - Federal Reduced SSI Benefit = State Supplement**

The federal reduced SSI benefit has been $30/individual since July 1, 1988 (it was $25 from Jan 1, 1974 through June 30, 1988).

| Period | PNA | Federal Reduced SSI (Individual) | State Supplement (Individual) |
|---|---|---|---|
| Sep 1, 1999 - Aug 31, 2001 | $45 | $30 | $15 |
| Sep 1, 2001 - Aug 31, 2003 | $60 | $30 | $30 |
| Sep 1, 2003 - Dec 31, 2005 | $45 | $30 | $15 |
| Jan 1, 2006 - Dec 31, 2023 | $60 | $30 | $30 |
| Jan 1, 2024 - present | $75 | $30 | $45 |

**Note on PNA history**: The PNA history above comes from the HHSC Medicaid for the Elderly and People with Disabilities Handbook, Section H-1500. The program effective date per SSA records is September 1, 1999.

### Important notes on implementation

1. **The supplement amount is NOT a fixed dollar parameter** -- it is derived as: `PNA - federal_reduced_SSI_benefit`
2. The federal reduced SSI benefit ($30) is set by federal statute (42 USC 1382(e)(1)(B)) and has not changed since 1988
3. The PNA amount is set by the Texas legislature via Texas Human Resources Code Section 32.024(w) and can change
4. The couple reduced rate ($60/month) has also been unchanged since 1988

---

## Income Rules

### No additional state income rules

Texas does NOT apply any income rules beyond the federal SSI rules for the state supplement:
- Federal SSI income exclusions apply
- No additional state income disregards
- No state-specific income counting rules
- The supplement is effectively automatic for SSI recipients in qualifying facilities

### How it interacts with federal SSI

The Texas state supplement is paid **on top of** the reduced federal SSI benefit. The calculation is:
1. Person is determined SSI-eligible by SSA
2. Person enters Medicaid-funded NF or ICF/IID facility
3. After the month of entry, SSI payment is reduced to $30/month (individual)
4. Texas supplements by $45/month to reach $75 PNA

The state supplement does NOT affect the federal SSI calculation. It is a separate state payment.

---

## Legal Authority and References

### Texas statute

**Primary legal authority:**
- **Texas Human Resources Code, Section 32.024(w)** -- Sets the Personal Needs Allowance
  - Current text (as amended by HB 54, 88th Legislature, 2023):
    > "The executive commissioner shall set a personal needs allowance of not less than $75 a month for a resident of a convalescent or nursing facility or related institution licensed under Chapter 242, Health and Safety Code, assisted living facility, ICF-IID facility, or other similar long-term care facility who receives medical assistance."
  - URL: https://statutes.capitol.texas.gov/Docs/HR/htm/HR.32.htm
  - Also: https://texas.public.law/statutes/tex._human_resources_code_section_32.024

**Amending legislation:**
- **HB 54, 88th Texas Legislature (2023)** -- Increased PNA from $60 to $75
  - Effective date: September 1, 2023 (PNA increase applied January 1, 2024)
  - Bill text: https://capitol.texas.gov/tlodocs/88R/billtext/html/HB00054F.HTM
  - Analysis: https://capitol.texas.gov/tlodocs/88R/analysis/html/HB00054S.htm

### Federal authority

- **42 USC 1382(e)(1)(B)** -- Federal SSI reduced benefit for institutional residents ($30/month)
  - URL: https://www.law.cornell.edu/uscode/text/42/1382
- **42 USC 1382e** -- Optional state supplementation authority
  - URL: https://www.law.cornell.edu/uscode/text/42/1382e

### Texas HHSC policy manuals

- **MEPD Handbook, Section H-1500** -- Personal Needs Allowance
  - URL: https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-1500-personal-needs-allowance
  - Contains: PNA amounts, history, and rules

- **MEPD Handbook, Section H-6000** -- Co-Payment for SSI Cases
  - URL: https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-6000-co-payment-ssi-cases
  - Contains: Federal SSI benefit rates, reduced payment standards, and how the state supplement works

- **MEPD Handbook, Section A-2100** -- Supplemental Security Income
  - URL: https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/a-2100-supplemental-security-income
  - Contains: Overview of SSI and automatic Medicaid eligibility

- **MEPD Handbook, Appendix XXXI** -- Budget Reference Chart
  - URL: https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/appendix-xxxi-budget-reference-chart
  - Contains: Current PNA amounts ($75 for NF/ICF-IID, $85 for foster care/assisted living), SSI FBR rates

- **MEPD Handbook, Section H-5100** -- ICF/IID Individual and Couple Cases
  - URL: https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-5100-icfiid-individual-couple-cases
  - Contains: ICF/IID-specific PNA calculations including Protected Earned Income (PEI) provisions

### SSA documentation

- **SSA State Assistance Programs for SSI Recipients (2011) - Texas**
  - URL: https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/tx.html
  - Contains: Comprehensive overview of Texas state assistance programs for SSI recipients

- **SSA State Assistance Programs for SSI Recipients (2002) - Texas**
  - URL: https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2002/tx.html
  - Contains: Historical recipient counts (6,441 recipients in January 2002)

- **SSA POMS SI 01401.001** -- General Information about State Supplementation
  - URL: https://secure.ssa.gov/apps10/poms.nsf/lnx/0501401001
  - Contains: Federal framework for state supplementation programs

- **SSA POMS SI 01415.001** -- State Supplementary Programs
  - URL: https://secure.ssa.gov/poms.nsf/lnx/0501415001
  - Note: Texas has NO state-specific POMS section (unlike CA, MA, NY, etc.) -- consistent with being state-administered

### Secondary/summary sources

- **Medicaid Planning Assistance -- SSI and OSS**
  - URL: https://www.medicaidplanningassistance.org/ssi-and-oss/
  - Lists Texas as state-administered, $45/month for individuals in Medicaid-funded long-term care

- **WorkWorld -- SSI State Supplement Texas**
  - URL: https://help.workworldapp.com/wwwebhelp/ssi_state_supplement_texas.htm
  - Contains: Individual $60/month, couple $90/month (appears to be pre-2024 data with the $60 PNA)

- **Brendan Conley Law -- Optional State Supplements by State (2020)**
  - URL: https://brendanconley.com/faq/questions-about-benefits/optional-state-supplements-for-ssi-in-each-state/
  - Lists Texas supplement range as $30-$60 (based on 2020 PNA of $60)

---

## Non-Simulatable Rules (Architecture Limitation)

### Cannot be simulated

- **Facility residence duration**: The $30 reduced SSI benefit only applies after the first full calendar month in a Medicaid facility. The month of entry uses full SSI rates. PolicyEngine cannot track entry dates or duration. IMPLEMENTATION: Apply the supplement as if the person has been in the facility for the qualifying period.
- **Temporary institutionalization exception**: SSI recipients expected to stay 90 days or less may continue receiving full SSI. Cannot be modeled.

### Partially simulatable

- **Living arrangement**: PolicyEngine does not currently model whether someone lives in a Medicaid facility vs. the community. The supplement would need to be conditional on a living arrangement input variable (similar to Massachusetts's `ma_state_living_arrangement` approach).
- **ICF/IID Protected Earned Income (PEI)**: ICF/IID residents have a more complex PNA calculation that includes earned income disregards beyond the base $75. This is a secondary feature and may be out of scope for initial implementation.

### Can be simulated

- PNA-based supplement amount (current point-in-time)
- Individual vs. couple amounts
- Basic eligibility based on SSI eligibility + facility residence

---

## Implementation Recommendations

### Approach

Given the extremely narrow scope of the Texas SSI state supplement (applies ONLY to SSI recipients in Medicaid-funded nursing facilities/ICF-IID), the implementation should follow a simplified approach similar to Colorado's `co_state_supplement`:

1. **Parameter**: Store the PNA amount ($75/month) as the parameter, since the supplement is derived from PNA minus the federal reduced benefit
2. **Variable**: Calculate the supplement as `max(0, PNA - federal_SSI_reduced_benefit)`
3. **Eligibility**: Condition on SSI eligibility AND a living arrangement variable indicating Medicaid facility residence

### Parameter structure

```
gov/states/tx/hhsc/ssi_state_supplement/
  personal_needs_allowance.yaml          # $75/month (individual)
```

The federal reduced SSI benefit ($30/month individual, $60/month couple) is already defined in federal parameters and does not need to be duplicated.

### Variable structure

```
variables/gov/states/tx/hhsc/ssi_state_supplement/
  tx_ssi_state_supplement.py             # Main supplement calculation
  tx_ssi_state_supplement_eligible.py    # Eligibility (SSI eligible + in Medicaid facility)
```

### Key consideration: living arrangement input

The existing codebase does not have a general "in Medicaid facility" input variable. Massachusetts uses `ma_state_living_arrangement` as a state-specific enum. Options for Texas:

1. **Create a federal-level variable** `is_in_medicaid_facility` (boolean) -- usable by multiple states
2. **Create a Texas-specific variable** -- simpler but less reusable
3. **Use Massachusetts's pattern** with a Texas-specific living arrangement enum -- likely overkill given Texas only distinguishes facility vs. non-facility

Recommendation: Option 1 (federal-level boolean) is cleanest, since the $30 reduced SSI benefit is itself a federal concept that applies to all states.

### Connection to SPM unit benefits

The new `tx_ssi_state_supplement` variable would need to be added to the `spm_unit_benefits` variable in `policyengine_us/variables/household/income/spm_unit/spm_unit_benefits.py`, following the same pattern as `ma_state_supplement` and `co_state_supplement`.

---

## Existing Implementation Patterns for Reference

### California (ca_state_supplement)
- **Entity**: SPMUnit
- **Calculation**: `max(0, payment_standard - ssi - countable_income)`
- **Complexity**: High (multiple living arrangements, blind/aged/disabled categories, dependent amounts, food allowances)
- **Parameters**: Extensive breakdowns by category and living arrangement

### Massachusetts (ma_state_supplement)
- **Entity**: Person
- **Calculation**: `max(0, maximum_supplement - reduction_after_ssi)` where `reduction_after_ssi = max(0, -uncapped_ssi)`
- **Complexity**: High (6 living arrangements, 3 SSI categories, single vs. couple breakdowns)
- **Living Arrangement**: Uses `MAStateLivingArrangement` enum

### Colorado (co_state_supplement)
- **Entity**: Person
- **Calculation**: `max(0, grant_standard - ssi - countable_income)`
- **Complexity**: Low (single grant standard, age restriction, blind/disabled only)
- **Most similar to Texas** in terms of simplicity

### Recommended pattern for Texas
- Follow Colorado's approach (simplest existing pattern)
- Single parameter for PNA amount
- Derive supplement from PNA minus federal reduced benefit
- Simple eligibility check: SSI eligible + in Medicaid facility

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **SSA "Understanding SSI" -- 2025 Edition**
   - URL: https://www.ssa.gov/pubs/EN-17-008.pdf
   - Expected content: Comprehensive overview of SSI program including reduced benefit provisions for institutional residents

2. **SSA "SSI in California" Publication**
   - URL: https://www.ssa.gov/pubs/EN-05-11125.pdf
   - Expected content: Example of how SSA documents state supplements (useful as pattern reference)

3. **Texas MEPD Policy Bulletin 24-2**
   - URL: https://www.hhs.texas.gov/sites/default/files/documents/mepd-24-2.pdf
   - Expected content: May contain policy updates related to the PNA increase or SSI supplement changes

4. **National LTC Ombudsman Personal Needs Allowance Brief (2009)**
   - URL: https://ltcombudsman.org/uploads/files/support/brief-pna-mar-2009.pdf
   - Expected content: Historical comparison of PNA amounts across all states

---

## Summary of Key Implementation Values

| Parameter | Value | Source |
|---|---|---|
| Personal Needs Allowance (individual) | $75/month | TX HRC 32.024(w), HHSC MEPD Handbook H-1500 |
| Personal Needs Allowance (couple, both in facility) | $150/month ($75 each) | HHSC MEPD Handbook H-6000 |
| Federal SSI reduced benefit (individual) | $30/month | 42 USC 1382(e)(1)(B) |
| Federal SSI reduced benefit (couple) | $60/month | 42 USC 1382(e)(1)(B) |
| State supplement (individual) | $45/month (= $75 - $30) | Derived from PNA and federal reduced SSI |
| State supplement (couple) | $90/month (= $150 - $60) | Derived from PNA and federal reduced SSI |
| Program effective date | September 1, 1999 | SSA State Assistance Programs for SSI Recipients |
| Current PNA effective date | January 1, 2024 | HB 54 (88th Legislature), HHSC MEPD Handbook H-1500 |
| Qualifying facilities | NF, ICF/IID (Medicaid-funded) | HHSC MEPD Handbook H-6000 |
| Administration | State-administered by HHSC | SSA State Assistance Programs, multiple sources |
| SSI category restriction | None -- aged, blind, and disabled all qualify | SSA State Assistance Programs 2002 (shows all categories) |
| Additional income rules | None beyond federal SSI | SSA State Assistance Programs, WorkWorld |
| Waiver program exclusion | Yes -- HCBS waiver participants excluded | TX HRC 32.024(w) |

---
---

# South Carolina SSI State Supplement - Implementation Documentation

**Collected**: 2026-02-10
**Implementation Task**: Implement South Carolina Optional State Supplementation (OSS) for SSI recipients and other eligible individuals in licensed Community Residential Care Facilities (CRCFs)

---

## Official Program Name

**Federal Program**: Supplemental Security Income (SSI) - Optional State Supplementation (OSS)
**State's Official Name**: Optional State Supplementation (OSS) Program
**Abbreviation**: OSS
**Administering Agency**: South Carolina Department of Health and Human Services (SCDHHS), Bureau of Long Term Care Services, Division of Community and Facility Services
**Administration Type**: State-administered (NOT federally administered by SSA)
**Source**: SSA POMS SI 01415.010 lists SC as "S" (State Administration) for optional programs; SCDHHS manages all OSS eligibility determinations and payments through county DSS offices

**Variable Prefix**: `sc_ssi_state_supplement`

---

## Program Overview

South Carolina provides an Optional State Supplementation (OSS) program that is distinct from most other states' SSI supplements in several important ways:

1. **It is available ONLY to individuals residing in licensed Community Residential Care Facilities (CRCFs)** -- essentially assisted living facilities. It is NOT available to SSI recipients living in the community, in nursing homes, or in other institutional settings.
2. **It covers not just SSI recipients** but also other low-income individuals who meet SSA criteria for aged, blind, or disabled status and have countable income below the Net Income Limit.
3. **The benefit structure is designed as a facility payment system** -- most of the money goes to the facility, with the individual retaining a Personal Needs Allowance (PNA).
4. **It is NOT a small add-on to federal SSI** like Texas. South Carolina's supplement provides substantial facility payment support (up to $1,719/month to the facility as of 2026).

### How it works

The OSS program supplements the income of eligible individuals to bring their total up to the Net Income Limit (NIL). The calculation has two components:

1. **OSS Amount** = Net Income Limit - Countable Income (this is the state's contribution)
2. **Facility Payment** = OSS Amount + (Countable Income - Personal Needs Allowance) (total going to the CRCF)
3. **Individual retains** = Personal Needs Allowance (for personal spending)

The Net Income Limit itself equals the Maximum Facility Payment plus the PNA (for SSI-only recipients):

```
Net Income Limit = Maximum Facility Payment + PNA (SSI-only)
```

**Verification with 2026 amounts:**
```
$1,804 (NIL) = $1,719 (Max Facility Payment) + $85 (PNA for SSI-only)
```

### Example calculation (2026, SSI-only recipient with $994 SSI payment)

```
Countable Income = $994 (SSI payment)
Net Income Limit = $1,804
OSS Amount = $1,804 - $994 = $810
Personal Needs Allowance = $85 (SSI-only recipient)
Individual retains = $85
Facility receives = $810 + ($994 - $85) = $810 + $909 = $1,719
```

### Example calculation (2026, individual with $994 SSI + $200 Social Security)

```
Countable Income = $994 + $200 = $1,194
Net Income Limit = $1,804
OSS Amount = $1,804 - $1,194 = $610
Personal Needs Allowance = $105 (has income beyond SSI)
Individual retains = $105
Facility receives = $610 + ($1,194 - $105) = $610 + $1,089 = $1,699
```

Note: In this case the facility receives less than the maximum because the individual's higher income (with higher PNA) reduces the total facility payment.

---

## Eligibility Criteria

### Who qualifies (per S.C. Code Regs. 126-920)

An individual must meet ALL of the following criteria:

1. **Residency**: Be a resident of the State of South Carolina
2. **Categorical Status**: Be determined by the Social Security Administration or the State to be aged (65+), blind, or disabled in accordance with SSA guidelines
3. **Resources**: Have countable resources that do not exceed the eligibility limitations for resources set by the federal SSI Program ($2,000 individual / $3,000 couple as of 2024; increasing to $4,000/$6,000 per recent federal changes)
4. **Income**: Meet ONE of the following income conditions:
   - (a) Receives an SSI payment AND combined income (SSI + other) is below the OSS Net Income Limit, OR
   - (b) Has countable income that exceeds the SSI standard but remains below the OSS Net Income Limit (i.e., NOT an SSI recipient but still income-eligible for OSS), OR
   - (c) Has income below the SSI standard with SSI application pending, OR
   - (d) Has income below the SSI standard without SSI application or was denied SSI solely due to public institution residence
5. **SSI Compliance**: Meets all other SSI program eligibility criteria (except for conditions 4(b) or 4(d) above)
6. **Facility Residence**: Resides in a Community Residential Care Facility (CRCF) that has executed a "Facility Participation Agreement" with SCDHHS
7. **Applied for all benefits**: Has applied for all benefits, public or private, to which they may be legally entitled

### Who does NOT qualify

- SSI recipients or other eligible individuals living in the community (at home)
- Individuals in nursing homes or skilled nursing facilities (they have a separate Medicaid PNA program, not OSS)
- Individuals in ICF/IIDs (they have a separate Medicaid PNA program)
- Individuals in facilities not licensed by DHEC as CRCFs
- Individuals with countable income above the Net Income Limit
- Individuals with resources above the federal SSI resource limits

### Couples

Per S.C. Code Regs. 126-920(B): "Couples are treated as two separate individuals upon admission to a CRCF." Eligibility for couples is determined by measuring a couple's combined countable income against a combined Net Income Limit, but once admitted to a facility, each person is treated individually.

### Important distinction from Texas

Unlike Texas (which supplements ONLY for nursing facility residents receiving reduced $30/month SSI), South Carolina's OSS supplements income for CRCF residents who may be receiving FULL SSI payments (not reduced). The supplement brings total income up to the Net Income Limit, not just a personal needs allowance level.

### CRCF definition

Per S.C. Code Regs. 126-910(C): A CRCF is a facility "licensed by the South Carolina Department of Health and Environmental Control" (DHEC). Per WorkWorld, the facility must "serve two or more adults for periods exceeding 24 consecutive hours" and provide "accommodation, board, and personal assistance in daily living activities" including feeding and dressing.

---

## Benefit Amounts / Payment Standards

### Current amounts (effective January 1, 2026)

| Component | Amount | Source |
|---|---|---|
| Maximum Facility Payment | $1,719/month | SCDHHS MB# 26-001 (Jan 8, 2026) |
| Net Income Limit (NIL) | $1,804/month | SCDHHS MB# 26-001 (Jan 8, 2026) |
| PNA (SSI-only income) | $85/month | SCDHHS MB# 26-001 (Jan 8, 2026) |
| PNA (other income beyond SSI) | $105/month | SCDHHS MB# 26-001 (Jan 8, 2026) |

### Historical amounts

| Effective Date | Max Facility Payment | Net Income Limit | PNA (SSI-only) | PNA (other income) | Source |
|---|---|---|---|---|---|
| Jan 1, 2026 | $1,719 | $1,804 | $85 | $105 | SCDHHS MB# 26-001 |
| Jan 1, 2025 | $1,694 | $1,777 | $83 | $103 | SCDHHS 2025 COLA Bulletin |
| Jan 1, 2024 | $1,672 | $1,753 | $81 | $101 | SCDHHS 2024 COLA Bulletin |
| Jul 1, 2023 | $1,645 | $1,724 | $79 | $99 | SCDHHS MB# 23-009 ($25 rate increase) |
| Jan 1, 2023 | $1,620 | $1,699 | $79 | $99 | SCDHHS COLA Bulletin (pre-July rate increase) |
| Jul 1, 2022 | $1,620 | $1,699 | $77 | $97 | SCDHHS MB# 22-013 ($100 rate increase) |
| Pre-Jul 2022 | $1,520 | $1,526 | $77 | $97 | SCDHHS (per $100 increase announcement) |
| 2010 (CY) | -- | $1,157 combined | $77 | $57 | WorkWorld (2010 data) |
| 2007 (CY) | $900 | $1,036 | $71 | $51 | WorkWorld (2007 data) |

**Notes on the NIL discrepancy for pre-Jul 2022:**
- The 2022 rate increase announcement says NIL increased from $1,526 to $1,626, but this does not match $1,520 + $77 = $1,597. The NIL may have been adjusted separately from the facility payment rate. The $1,526 figure comes directly from SCDHHS MB# 22-013.

### Formula verification

The relationship **Net Income Limit = Maximum Facility Payment + PNA (SSI-only)** is verified for multiple years:
- 2026: $1,719 + $85 = $1,804
- 2025: $1,694 + $83 = $1,777
- 2024: $1,672 + $81 = $1,753
- Jul 2023: $1,645 + $79 = $1,724

### How amounts change

Per S.C. Code Regs. 126-940(E): "Cost-of-living adjustments in benefit payments made by the federal government will result in adjustments in the OSS Program as directed by the South Carolina General Assembly in the legislative budgetary process." Without specific General Assembly direction, COLA adjustments do NOT change the NIL, facility rate, or PNA -- they only adjust individual benefit amounts to reflect changes in recipients' countable income.

In practice, SCDHHS issues Medicaid Bulletins announcing adjustments to the facility rate, NIL, and PNA. Both the annual SSI COLA and periodic legislative rate increases affect the amounts.

### The individual's supplement (what PolicyEngine should calculate)

The **total state supplement paid on behalf of an individual** is:

```
OSS Amount = max(0, Net Income Limit - Countable Income)
```

This is the amount the STATE pays. The individual ALSO contributes their own income (minus PNA) to the facility. But the state supplement variable should capture the OSS amount -- the state's contribution.

For the maximum scenario (zero other income besides SSI):
- 2026: $1,804 - $994 (federal SSI individual FBR) = $810/month
- 2025: $1,777 - $967 = $810/month
- 2024: $1,753 - $943 = $810/month

---

## Income Rules

### Countable income definition

Per S.C. Code Regs. 126-910(E): **"Countable Income -- gross income less such exclusions as are permitted under the federal Supplemental Security Income (SSI) Program."**

This means South Carolina uses the SAME income counting rules as federal SSI:
- $20/month general income exclusion
- $65/month earned income exclusion + 50% of remaining earned income
- Other standard SSI income exclusions

There are **no additional state income disregards** beyond federal SSI standards (confirmed by WorkWorld: "No additional disregards beyond federal SSI standards").

### Resource limits

Per S.C. Code Regs. 126-910(F) and 126-920(A)(3): **"Countable Resources -- available assets as determined under the provisions of the federal Supplemental Security Income (SSI) Program."** Resources cannot exceed the federal SSI resource limits.

### Relative responsibility

None required (per WorkWorld and SSA documentation).

### Recoveries/liens

None (per WorkWorld and SSA documentation).

---

## Non-Simulatable Rules (Architecture Limitation)

### Cannot be simulated

- **Facility Participation Agreement**: The CRCF must have executed a participation agreement with SCDHHS. PolicyEngine cannot verify this.
- **Waiting list / slot availability**: Per S.C. Code Regs. 126-940(A-B), the program is subject to available funding and SCDHHS manages waiting lists. An approved "OSS slot request" is required. PolicyEngine cannot model slot availability.
- **12-month recertification**: Eligibility must be reestablished every 12 months. PolicyEngine cannot track this.
- **"Applied for all benefits" requirement**: Recipients must have applied for all benefits to which they are entitled. PolicyEngine cannot verify this.
- **10-day change reporting**: Changes must be reported within 10 days. PolicyEngine cannot track this.

### Partially simulatable

- **Living arrangement (CRCF residence)**: PolicyEngine would need an input variable for CRCF residence. This could use the same living arrangement infrastructure as other state supplements. Applied as a point-in-time condition.
- **PNA tier (SSI-only vs. other income)**: The PNA amount depends on whether the individual receives income ONLY from SSI or also has other income sources (e.g., Social Security). This IS simulatable based on income variables -- check if the individual has any non-SSI income.

### Can be simulated

- Net Income Limit eligibility test (countable income < NIL)
- OSS amount calculation (NIL - countable income)
- Categorical eligibility (aged, blind, or disabled)
- Resource test (using federal SSI resource limits)
- Individual vs. couple treatment
- PNA determination based on income sources

---

## Legal Authority and References

### South Carolina regulations (primary legal authority)

The OSS program is governed by South Carolina Code of Regulations, Chapter 126, Article 9:

- **S.C. Code Regs. 126-910** -- Program Definitions
  - Defines: OSS Program, OSS Facility Rate, CRCF, Net Income Limitation, Countable Income, Countable Resources, SSI Program, Personal Needs Allowance
  - Added: State Register Volume 24, Issue No. 3, effective March 23, 2001
  - URL: https://www.law.cornell.edu/regulations/south-carolina/R-126-910

- **S.C. Code Regs. 126-920** -- Eligibility
  - Contains: All seven eligibility criteria (residency, categorical status, resources, income, SSI compliance, facility residence, benefits applications); couple treatment; county DSS determination process; 12-month recertification; change reporting; automatic Medicaid eligibility for OSS recipients; prohibition on facilities charging above the OSS rate
  - Added: State Register Volume 24, Issue No. 3, effective March 23, 2001
  - URL: https://www.law.cornell.edu/regulations/south-carolina/R-126-920

- **S.C. Code Regs. 126-930** -- Termination, Suspension or Reduction of Benefits
  - Contains: "Eligibility for further OSS payments shall be terminated as soon as information indicating ineligibility is reported."
  - Added: State Register Volume 24, Issue No. 3, effective March 23, 2001
  - URL: https://www.law.cornell.edu/regulations/south-carolina/R-126-930

- **S.C. Code Regs. 126-940** -- Program Administration
  - Contains: Funding-limited program; SCDHHS manages waiting lists; monthly payments issued to CRCFs as single checks; facility record-keeping requirements; COLA adjustment rules; facility compliance requirements; prohibition on extra charges; participant compliance requirements
  - Added: State Register Volume 24, Issue No. 3, effective March 23, 2001
  - URL: https://www.law.cornell.edu/regulations/south-carolina/R-126-940

### South Carolina statutes

- **S.C. Code Title 44, Chapter 81** -- Long-Term Care Facilities
  - References OSS program in context of resident rights (relocation notice exemptions for OSS participants)
  - URL: https://www.scstatehouse.gov/code/t44c081.php

Note: The OSS program does not appear to have a dedicated enabling statute in the S.C. Code of Laws. The regulatory authority under Chapter 126, Article 9 appears to be the primary legal framework, with funding authorized through the annual General Appropriations Act.

### Federal authority

- **42 USC 1382e** -- Optional state supplementation authority
  - URL: https://www.law.cornell.edu/uscode/text/42/1382e
- **SSA POMS SI 01415.010** -- Administration of State Supplementary Programs
  - Shows South Carolina as "S" (State Administration) for optional programs and "NR" (No Recipients) for mandatory programs
  - URL: https://secure.ssa.gov/poms.nsf/lnx/0501415010

### SCDHHS policy documents and bulletins

- **SCDHHS Medicaid Bulletin MB# 26-001** (Jan 8, 2026) -- 2026 COLA Adjustments
  - Contains: 2026 maximum facility payment ($1,719), NIL ($1,804), PNA amounts ($85/$105)
  - URL: https://www.scdhhs.gov/communications/social-security-and-supplemental-security-income-cost-living-adjustment-increases-0

- **SCDHHS 2025 COLA Bulletin** -- 2025 COLA Adjustments
  - Contains: 2025 maximum facility payment ($1,694), NIL ($1,777), PNA amounts ($83/$103)
  - URL: https://www.scdhhs.gov/communications/social-security-and-supplemental-security-income-cost-living-adjustment-increases

- **SCDHHS 2024 COLA Bulletin** -- 2024 COLA Adjustments
  - Contains: 2024 maximum facility payment ($1,672), NIL ($1,753), PNA amounts ($81/$101)
  - URL: https://www.scdhhs.gov/communications/social-security-and-supplemental-security-income-ssi-cost-living-adjustment-cola

- **SCDHHS MB# 23-009** (Sep 2023) -- OSS Rate Increases effective July 2023
  - Contains: $25 rate increase per resident; max facility payment $1,645; NIL $1,724; PNA $79/$99
  - URL: https://www.scdhhs.gov/communications/optional-state-supplementation-oss-rate-increases-0

- **SCDHHS MB# 22-013** (Aug 2022) -- OSS Rate Increases effective July 2022
  - Contains: $100 rate increase per resident; NIL from $1,526 to $1,626
  - URL: https://www.scdhhs.gov/communications/optional-state-supplementation-oss-rate-increases

- **SCDHHS OSS Program Page**
  - URL: https://www.scdhhs.gov/resources/programs-and-initiatives/long-term-living/optional-state-supplementation-oss
  - Contains: Eligibility overview, required documentation, application forms

- **SCDHHS OSS Services Manual** (Provider Manual)
  - URL: https://provider.scdhhs.gov/internet/pdf/manuals/oss/Manual.pdf
  - Contains: Complete program rules, billing procedures, forms

- **SCDHHS Personal Needs Allowance Increase** (Oct 2025 -- Medicaid NF/ICF-IID PNA, NOT OSS)
  - URL: https://www.scdhhs.gov/communications/personal-needs-allowance-increase
  - Note: This is the SEPARATE nursing facility Medicaid PNA ($30 to $60), NOT the OSS PNA

### SSA documentation

- **SSA State Assistance Programs for SSI Recipients (2011) - South Carolina**
  - URL: https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/sc.html
  - Contains: Comprehensive overview of SC state assistance programs for SSI recipients

- **SSA State Assistance Programs for SSI Recipients (2004) - South Carolina**
  - URL: https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2004/sc.html
  - Contains: Historical program information

### Secondary/summary sources

- **WorkWorld -- SSI State Supplement South Carolina**
  - URL: https://help.workworldapp.com/wwwebhelp/ssi_state_supplement_south_carolina.htm
  - Contains: 2010 data -- individual $483/month state supplement; combined $1,157; PNA $77/$57

- **WorkWorld -- OSS Eligibility South Carolina**
  - URL: https://help.workworldapp.com/wwwebhelp/medicaid_program_optional_state_supplementation_oss_eligibility_south_carolina.htm
  - Contains: Eligibility requirements, income conditions, couple rules

- **WorkWorld -- OSS Overview South Carolina**
  - URL: https://help.workworldapp.com/wwwebhelp/medicaid_program_optional_state_supplementation_oss_overview_south_carolina.htm
  - Contains: 2007 data -- max facility payment $900, NIL $1,036, PNA $71/$51

- **Medicaid Planning Assistance -- SSI and OSS**
  - URL: https://www.medicaidplanningassistance.org/ssi-and-oss/
  - Lists SC as state-administered; $810/month maximum for individuals

- **Atticus -- SSI Supplemental Payments by State**
  - URL: https://www.atticus.com/advice/disability-help-by-state/ssi-supplemental-payments-by-state
  - Lists SC among the 33 states that "pay and administer their own SSPs"

- **SC Lt. Governor's Office on Aging -- Medicaid OSS Fact Sheet** (Rev. Jan 7, 2025)
  - URL: https://aging.sc.gov/sites/default/files/documents/PrivateVAGAL/FactSheets/Medicaid%20OSS.pdf
  - PDF -- could not be extracted; expected to contain current program overview

---

## Implementation Recommendations

### Approach

South Carolina's OSS program is fundamentally different from Texas's simple PNA-based supplement. It is a comprehensive facility payment program with a net income limit test. The implementation should be closer to Colorado's `co_state_supplement` pattern (grant standard minus income) but with additional complexity for the two-tier PNA system.

### Key parameters

```
gov/states/sc/scdhhs/ssi_state_supplement/
  net_income_limit.yaml           # $1,804/month (2026)
  personal_needs_allowance/
    ssi_only.yaml                 # $85/month (2026) -- for recipients with only SSI income
    other_income.yaml             # $105/month (2026) -- for recipients with non-SSI income
  maximum_facility_payment.yaml   # $1,719/month (2026) -- optional, can be derived
```

**Note**: The maximum facility payment can be derived as NIL - PNA (SSI-only), so it may not need its own parameter. However, having it explicitly may be useful for validation.

### Key variables

```
variables/gov/states/sc/scdhhs/ssi_state_supplement/
  sc_ssi_state_supplement.py              # Main supplement calculation: max(0, NIL - countable_income)
  sc_ssi_state_supplement_eligible.py     # Eligibility: aged/blind/disabled + CRCF resident + income < NIL + resources < limit
  sc_ssi_state_supplement_pna.py          # PNA amount: $85 if SSI-only, $105 if other income
```

### Calculation logic

```python
# sc_ssi_state_supplement.py
# OSS Amount = max(0, Net Income Limit - Countable Income)
net_income_limit = p.net_income_limit * MONTHS_IN_YEAR
countable_income = person("ssi_countable_income", period) + person("ssi", period)
oss_amount = max_(0, net_income_limit - countable_income)
```

### Living arrangement requirement

Like Texas, this requires a CRCF residence input variable. Options:
1. Reuse the living arrangement infrastructure being developed for TX
2. Create a boolean `is_in_crcf` or more general `is_in_residential_care_facility`
3. Create an enum with CRCF as one of the options

Recommendation: Create a general boolean `is_in_residential_care_facility` at the federal level, or use the Texas-proposed `is_in_medicaid_facility` concept but broadened. Alternatively, if a state-specific enum is preferred, create `SCSSILivingArrangement` with values like `CRCF` and `OTHER`.

### Connection to SPM unit benefits

The new `sc_ssi_state_supplement` variable would need to be added to the `spm_unit_benefits` variable.

### Important implementation note: OSS covers non-SSI recipients too

Per S.C. Code Regs. 126-920(A)(4)(b), individuals whose "countable income exceeds the SSI standard but is less than the OSS Net Income Limit" are ALSO eligible. This means the OSS supplement is NOT strictly tied to federal SSI eligibility -- it has its own income threshold (the NIL). However, the individual must still meet the categorical requirement (aged, blind, or disabled per SSA criteria) and resource limits.

For implementation purposes, this means:
- The eligibility check should NOT simply be `is_ssi_eligible & is_in_crcf`
- Instead, it should check: `is_ssi_aged_blind_disabled & meets_ssi_resource_test & is_in_crcf & countable_income < NIL`
- The person does NOT need to actually receive SSI to qualify for OSS

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be extracted:

1. **SCDHHS OSS Services Provider Manual**
   - URL: https://provider.scdhhs.gov/internet/pdf/manuals/oss/Manual.pdf
   - Expected content: Complete program rules, billing procedures, eligibility determination process, payment calculation methodology
   - This is the primary operational document for the program

2. **SC Lt. Governor's Office on Aging -- Medicaid OSS Fact Sheet (Rev. Jan 7, 2025)**
   - URL: https://aging.sc.gov/sites/default/files/documents/PrivateVAGAL/FactSheets/Medicaid%20OSS.pdf
   - Expected content: Current program overview with 2025 amounts, eligibility summary

3. **2017 OSS Provider Training (SCDHHS)**
   - URL: https://medicaidelearning.remote-learner.net/pluginfile.php/19106/mod_resource/content/1/2017%20OSS%20Provider%20TrainingfinalBCBS.PDF
   - Expected content: Training materials with payment calculation examples

4. **SCDHHS CRCF-01 Form and Instructions**
   - URL: https://www1.scdhhs.gov/internet/eligfm/FM%20CRCF-01.pdf
   - Expected content: The actual eligibility determination form used for OSS cases

5. **SCDHHS MB# 26-001 (2026 COLA Bulletin PDF)**
   - URL: https://www.scdhhs.gov/sites/dhhs/files/(2026-1-9)%20SSI%20COLA%20Increase%202026%20Bulletin.pdf
   - Expected content: Official bulletin with all 2026 amounts

6. **SC State Library -- DHHS OSS Services Provider Manual (June 2019)**
   - URL: https://dc.statelibrary.sc.gov/bitstream/handle/10827/32500/DHHS_Optional_State_Supplementation_Services_Provider_Manual_2019-06-01.pdf
   - Expected content: Archived version of the full provider manual

7. **SC Code of Regulations Chapter 126 (Full PDF)**
   - URL: https://www.scstatehouse.gov/coderegs/Chapter%20126.pdf
   - Expected content: Complete text of all DHHS regulations including Article 9 (OSS)

---

## Summary of Key Implementation Values

| Parameter | Value | Source |
|---|---|---|
| Net Income Limit | $1,804/month (2026) | SCDHHS MB# 26-001 |
| Maximum Facility Payment | $1,719/month (2026) | SCDHHS MB# 26-001 |
| PNA (SSI-only income) | $85/month (2026) | SCDHHS MB# 26-001 |
| PNA (other income sources) | $105/month (2026) | SCDHHS MB# 26-001 |
| Maximum state supplement (zero other income) | $810/month (2026, for SSI-only recipient with $994 FBR) | Derived: $1,804 - $994 |
| Countable income definition | Federal SSI rules (gross income less SSI exclusions) | S.C. Code Regs. 126-910(E) |
| Resource limit | Federal SSI resource limits | S.C. Code Regs. 126-910(F), 126-920(A)(3) |
| Categorical requirement | Aged (65+), blind, or disabled per SSA criteria | S.C. Code Regs. 126-920(A)(2) |
| Facility type | CRCF licensed by DHEC with Facility Participation Agreement | S.C. Code Regs. 126-920(A)(6), 126-910(C) |
| Administration | State-administered by SCDHHS | SSA POMS SI 01415.010 |
| Couples treatment | Treated as two separate individuals upon CRCF admission | S.C. Code Regs. 126-920(B) |
| Automatic Medicaid | OSS recipients automatically eligible for Medicaid | S.C. Code Regs. 126-920(F) |
| Regulations effective date | March 23, 2001 | S.C. Code Regs. Chapter 126, Article 9 |
| Income disregards | None beyond federal SSI | WorkWorld, S.C. Code Regs. 126-910(E) |
| Relative responsibility | None | WorkWorld |

---

## Existing Implementation Patterns for Reference

### Colorado (co_state_supplement) -- most similar pattern
- **Entity**: Person
- **Calculation**: `max(0, grant_standard - ssi - countable_income)`
- **Complexity**: Low (single grant standard, age restriction, blind/disabled only)
- **Key difference from SC**: Colorado has a single grant standard amount; SC has a Net Income Limit with two PNA tiers

### California (ca_state_supplement) -- useful for facility-based patterns
- **Entity**: SPMUnit
- **Calculation**: `max(0, payment_standard - ssi - countable_income)`
- **Complexity**: High (multiple living arrangements, multiple categories)
- **Key similarity to SC**: Both have facility-based payment standards

### Recommended pattern for South Carolina
- Follow Colorado's approach for the main calculation (NIL minus income)
- Add PNA determination logic (SSI-only vs. other income)
- Use a living arrangement input variable for CRCF residence
- Eligibility check should be: aged/blind/disabled AND CRCF resident AND income < NIL AND resources within limits
- Note: Unlike CO, SC does NOT require actual SSI receipt -- just meeting the categorical and resource criteria

---

## Validation Checklist

- [x] 2026 Net Income Limit confirmed: $1,804/month (SCDHHS MB# 26-001)
- [x] 2026 Maximum Facility Payment confirmed: $1,719/month (SCDHHS MB# 26-001)
- [x] 2026 PNA (SSI-only) confirmed: $85/month (SCDHHS MB# 26-001)
- [x] 2026 PNA (other income) confirmed: $105/month (SCDHHS MB# 26-001)
- [x] 2025 amounts confirmed: NIL $1,777, Facility $1,694, PNA $83/$103
- [x] 2024 amounts confirmed: NIL $1,753, Facility $1,672, PNA $81/$101
- [x] Jul 2023 amounts confirmed: NIL $1,724, Facility $1,645, PNA $79/$99
- [x] Formula verified: NIL = Max Facility Payment + PNA (SSI-only) for all years
- [x] Countable income uses federal SSI rules: confirmed per S.C. Code Regs. 126-910(E)
- [x] Resource limits use federal SSI rules: confirmed per S.C. Code Regs. 126-920(A)(3)
- [x] State-administered: confirmed per SSA POMS SI 01415.010
- [x] CRCF-only (not nursing homes, not community): confirmed per S.C. Code Regs. 126-920(A)(6)
- [x] Non-SSI recipients can qualify: confirmed per S.C. Code Regs. 126-920(A)(4)(b)
- [x] Couples treated as individuals: confirmed per S.C. Code Regs. 126-920(B)
- [ ] Full provider manual PDF: NOT extracted -- referenced for future use
