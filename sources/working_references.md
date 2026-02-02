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

# New Jersey Unemployment Insurance - Working References

**Collected**: 2026-01-30

---

## Official Program Name

**Federal Program**: Unemployment Insurance (UI)
**State's Official Name**: New Jersey Unemployment Insurance
**Abbreviation**: UI
**Administering Agency**: New Jersey Department of Labor and Workforce Development
**Division**: Division of Unemployment Insurance

**Variable Prefix**: `nj_unemployment_insurance`

---

## Eligibility Requirements

### Monetary Eligibility

To qualify for New Jersey Unemployment Insurance benefits, applicants must meet one of two alternative monetary requirements:

#### Option 1: Base Week Method
- **2024**: Earn at least $283 per week for 20 or more weeks in covered employment during the base year
- **2025**: Earn at least $303 per week for 20 or more weeks in covered employment during the base year
- **2026**: Earn at least $310 per week for 20 or more weeks in covered employment during the base year

#### Option 2: Total Earnings Method (Alternative)
If the individual has not established 20 base weeks:
- **2024**: Earn at least $14,200 in total covered employment during the base year
- **2025**: Earn at least $15,200 in total covered employment during the base year
- **2026**: Earn at least $15,500 in total covered employment during the base year

**How Base Week Amount is Calculated**: The base week requirement is computed based on the state minimum wage in effect as of October 1 of the previous calendar year. The base week amount equals 20 times the state minimum hourly wage.

**Source**: [NJ Department of Labor 2026 Benefit Rates Press Release](https://www.nj.gov/labor/lwdhome/press/2025/20251229_newbenefitrates2026.shtml)

### Base Period Definition

The **regular base year** is the first four of the last five completed calendar quarters before the week you first applied for unemployment. This period covers approximately 52 weeks.

**Example Filing Windows**:
| Claim Filed | Base Year Period |
|-------------|------------------|
| Jan - Mar 2025 | Oct 1, 2023 - Sep 30, 2024 |
| Apr - Jun 2025 | Jan 1, 2024 - Dec 31, 2024 |
| Jul - Sep 2025 | Apr 1, 2024 - Mar 31, 2025 |
| Oct - Dec 2025 | Jul 1, 2024 - Jun 30, 2025 |

**Source**: [Division of Unemployment Insurance - Who is eligible for benefits?](https://www.nj.gov/labor/myunemployment/before/about/who/)

### Alternate Base Years

If earnings during the regular base year are insufficient, New Jersey reviews two alternate base year periods:

#### Alternate Base Year 1 (ABY1)
The four most recently completed calendar quarters before the claim date.

**Example for 2025 Claims**:
| Claim Filed | ABY1 Period |
|-------------|-------------|
| Jan - Mar 2025 | Jan 1 - Dec 31, 2024 |
| Apr - Jun 2025 | Apr 1, 2024 - Mar 31, 2025 |
| Jul - Sep 2025 | Jul 1, 2024 - Jun 30, 2025 |
| Oct - Dec 2025 | Oct 1, 2024 - Sep 30, 2025 |

#### Alternate Base Year 2 (ABY2)
The three most recently completed calendar quarters plus weeks and wages in the filing quarter through the last work day. This produces fewer than 52 weeks.

**Important**: You cannot pick and choose which base year period to use for qualification.

**Source**: [Division of Unemployment Insurance - How alternate base years are calculated](https://www.nj.gov/labor/myunemployment/before/about/who/alternatebaseyears.shtml)

### Non-Monetary Eligibility

Claimants must also meet the following non-monetary requirements:

1. **Separation Reason**: Must have lost job through no fault of their own (e.g., lack of work, layoff)
2. **Able and Available**: Must be able to work, available for work, and ready to start immediately
3. **Active Job Search**: Must actively seek employment each week benefits are claimed
4. **Work Authorization**: If claiming based on Temporary Protected Status, must prove wages were earned while authorized to work AND currently possess valid work authorization

**Source**: [Division of Unemployment Insurance - Who is eligible for benefits?](https://www.nj.gov/labor/myunemployment/before/about/who/)

### Work Search Requirements

- **Minimum Contacts**: At least 3 different employer contacts per week is considered reasonable
- **Acceptable Methods**: Telephone, internet, in-person visits, sending resumes
- **Documentation**: Must maintain records; may be asked to furnish work search contacts at any time
- **Must Contact Different Employers**: Cannot contact the same employers each week

**Source**: [Division of Unemployment Insurance - Make sure you are actively seeking work](https://www.nj.gov/labor/myunemployment/before/about/howtoapply/worksearch.shtml)

---

## Benefit Calculation

### Weekly Benefit Rate (WBR)

**Formula**: 60% of the average weekly wage earned during the base year, up to the maximum weekly benefit amount.

The average weekly wage is determined from wage information reported by employers.

**Source**: [Division of Unemployment Insurance - How we calculate benefits](https://www.nj.gov/labor/myunemployment/before/about/calculator/)

### Maximum Weekly Benefit

| Year | Maximum Weekly Benefit | Statewide Avg Weekly Wage (2 years prior) |
|------|------------------------|-------------------------------------------|
| 2024 | $854 | $1,507.76 (2022) |
| 2025 | $875 | $1,545.60 (2023) |
| 2026 | $905 | $1,598.66 (2024) |

The maximum benefit rate is recalculated each year based on the statewide average weekly wage in the second preceding calendar year.

**Sources**:
- [NJ Department of Labor 2025 Benefit Rates](https://www.nj.gov/labor/lwdhome/press/2024/20241217_new_benefit_rates.shtml)
- [NJ Department of Labor 2026 Benefit Rates](https://www.nj.gov/labor/lwdhome/press/2025/20251229_newbenefitrates2026.shtml)

### Minimum Weekly Benefit

New Jersey does not specify a statutory minimum weekly benefit amount. The benefit is calculated as 60% of average weekly wages. The effective minimum would be determined by the minimum earnings required to qualify (which would produce a very low WBR).

### Dependency Allowance

New Jersey provides additional benefits for dependents:

| Dependents | Increase |
|------------|----------|
| 1st dependent | 7% of WBR |
| 2nd dependent | 4% of WBR |
| 3rd dependent | 4% of WBR |
| **Maximum Total** | **15% of WBR** |

**Important Rules**:
- Dependency benefits can only increase your weekly benefit rate up to the maximum weekly benefit rate
- Must apply for dependency benefits within 6 weeks of the date of claim or become ineligible
- Only one spouse can claim dependency benefits if both are unemployed

**Who Qualifies as a Dependent**:
- Unemployed spouse or civil union partner
- Unemployed, unmarried child under age 19 (or 22 if attending school full-time)
- Unemployed, unmarried disabled adult child with blindness or disability that began before age 22

**Restrictions**:
- If your spouse/civil union partner was employed during the week you established your claim, you cannot receive dependency benefits
- Both spouses cannot receive dependency benefits simultaneously

**Documentation Required**:
- Social security numbers
- Proof of dependency (tax returns, birth certificates, marriage certificates, adoption/custody documents)
- For disabled children: Social Security Administration disability determination

**Source**: [Division of Unemployment Insurance - How to claim dependency benefits](https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml)

### Benefit Duration

**Maximum Duration**: 26 weeks

Your maximum benefit amount equals: (weeks worked in base period, up to 26) x (your weekly benefit rate)

**Maximum Total Benefit Amount**:
| Year | Maximum Total (26 weeks x Max WBR) |
|------|-----------------------------------|
| 2024 | $22,204 (26 x $854) |
| 2025 | $22,750 (26 x $875) |
| 2026 | $23,530 (26 x $905) |

**Source**: [Division of Unemployment Insurance - How we calculate benefits](https://www.nj.gov/labor/myunemployment/before/about/calculator/)

### Waiting Week

There is a one-week waiting period before benefits can be received. The first certification for benefits occurs on a Wednesday, 17 days after the date of claim.

---

## Partial Benefits (Working While Claiming)

### Partial Benefit Rate (PBR)
The Partial Benefit Rate is 20% higher than your weekly benefit rate.

**Formula**: PBR = WBR + (20% of WBR) = WBR x 1.20

### Earnings Disregard
- If you earn 20% or less of your WBR, you receive your full weekly benefit
- If you earn more than 20% of your WBR, benefits are reduced dollar-for-dollar

**Calculation**:
Partial Benefit = PBR - Gross Wages Earned

**Example** (WBR = $500):
- PBR = $500 + $100 = $600
- If you earn $200: Benefit = $600 - $200 = $400
- If you earn $50: Would be $550, but capped at WBR of $500

**Hours Limitation**: To be eligible for partial benefits, you cannot work more than 80% of the hours normally worked in the job.

**Reporting**: Wages must be reported for the week in which they are earned, not when paid.

**Source**: [Division of Unemployment Insurance - FAQ: Factors that affect your weekly benefit rate](https://www.nj.gov/labor/myunemployment/help/faqs/reducebenefits.shtml)

---

## Benefit Reductions

### Pension Offset
Pension benefits may reduce unemployment benefits:
- **100% reduction**: Employer contributed entire pension amount
- **50% reduction**: Both employer and employee contributed
- **No reduction**: Employee funded the entire pension

**Note**: Social Security benefits do NOT reduce unemployment insurance benefits.

### Refusing Suitable Work
Refusing suitable work may result in denial of benefits for the week of refusal and the next 3 weeks.

**Source**: [Division of Unemployment Insurance - FAQ: Factors that affect your weekly benefit rate](https://www.nj.gov/labor/myunemployment/help/faqs/reducebenefits.shtml)

---

## Disqualification Rules

### Voluntary Quit

**Rule**: Workers who quit without "good cause connected with the work" are disqualified from benefits.

**Burden of Proof**: On the employee to prove good cause.

**What Constitutes Good Cause**:
- Reason must be directly job-related
- Must be "so compelling that you had no choice but to leave"
- Examples: unsafe, unhealthful, or dangerous working conditions; intentional harassment; vulgar/abusive language; threatened violence

**What Does NOT Constitute Good Cause** (generally):
- Personal reasons like relocating
- Seeking better pay or hours elsewhere

**Exceptions That May Qualify**:
- Unsafe workplace conditions
- Domestic violence
- Military spouse relocation
- Securing comparable/better employment within 7 days

**Job Abandonment**: Missing work for more than 5 consecutive days without contacting employer is considered voluntary quit.

**Removal of Disqualification**: Must return to covered employment for at least 8 weeks, earn 10 times your weekly benefit rate, then become unemployed through no fault of your own.

**Source**: [Division of Unemployment Insurance - What if you quit or were fired?](https://www.nj.gov/labor/myunemployment/before/about/who/quitfired.shtml)

### Misconduct

#### Simple/Regular Misconduct
**Definition**: Conduct that is improper, intentional, connected with work, within the individual's control, not a good faith error, and either:
- Deliberate refusal without good cause to comply with employer's lawful/reasonable rules, OR
- Deliberate disregard of standards of behavior the employer has a reasonable right to expect

**What is NOT Misconduct**:
- Inadvertence or ordinary negligence in isolated instances
- Inefficiency or failure to perform due to inability or incapacity

**Disqualification Period**: 5 weeks (begins the week of firing/suspension)

**Burden of Proof**: On the employer to provide written documentation.

#### Gross Misconduct
**Definition**: Termination resulting from committing a crime of the first, second, third, or fourth degree under New Jersey Criminal Code.

**Disqualification**: Indefinite until:
- Return to covered employment for 8 weeks
- Earn 10 times weekly benefit rate
- Become unemployed through no fault of your own
- Wages from terminating employer cannot be used for future claims

**Domestic Violence Exception**: Separations related to domestic violence may be exempt from disqualification.

**Sources**:
- [Division of Unemployment Insurance - What if you quit or were fired?](https://www.nj.gov/labor/myunemployment/before/about/who/quitfired.shtml)
- [Division of Unemployment Insurance - Reasons for ineligibility](https://www.nj.gov/labor/myunemployment/before/about/who/ineligible.shtml)

### Other Ineligibility Reasons

- **Unable or Unavailable to Work**: Lacking childcare, transportation, or experiencing temporary disability
- **Full-Time Employment**: Currently employed full-time
- **Insufficient Job Search**: Not actively seeking employment
- **Disability**: A disability that prevents work (may qualify for other programs)

**Source**: [Division of Unemployment Insurance - Reasons for ineligibility](https://www.nj.gov/labor/myunemployment/before/about/who/ineligible.shtml)

---

## Taxable Wage Base (Employer Contributions)

| Year | Taxable Wage Base |
|------|-------------------|
| 2024 | $42,300 |
| 2025 | $43,300 |
| 2026 | $44,800 |

**Government Entity Contribution Rate**: 0.6% of taxable wages (for entities choosing contributions over reimbursement)

**Sources**:
- [NJ Department of Labor 2025 Benefit Rates](https://www.nj.gov/labor/lwdhome/press/2024/20241217_new_benefit_rates.shtml)
- [NJ Department of Labor 2026 Benefit Rates](https://www.nj.gov/labor/lwdhome/press/2025/20251229_newbenefitrates2026.shtml)

---

## Sources

### Official NJ Department of Labor Pages

1. [Division of Unemployment Insurance - Who is eligible for benefits?](https://www.nj.gov/labor/myunemployment/before/about/who/)
2. [Division of Unemployment Insurance - How we calculate benefits](https://www.nj.gov/labor/myunemployment/before/about/calculator/)
3. [Division of Unemployment Insurance - How alternate base years are calculated](https://www.nj.gov/labor/myunemployment/before/about/who/alternatebaseyears.shtml)
4. [Division of Unemployment Insurance - How to claim dependency benefits](https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml)
5. [Division of Unemployment Insurance - What if you quit or were fired?](https://www.nj.gov/labor/myunemployment/before/about/who/quitfired.shtml)
6. [Division of Unemployment Insurance - Reasons for ineligibility](https://www.nj.gov/labor/myunemployment/before/about/who/ineligible.shtml)
7. [Division of Unemployment Insurance - Make sure you are actively seeking work](https://www.nj.gov/labor/myunemployment/before/about/howtoapply/worksearch.shtml)
8. [Division of Unemployment Insurance - FAQ: Factors that affect your weekly benefit rate](https://www.nj.gov/labor/myunemployment/help/faqs/reducebenefits.shtml)

### Press Releases

9. [NJ Department of Labor 2025 Benefit Rates (Dec 2024)](https://www.nj.gov/labor/lwdhome/press/2024/20241217_new_benefit_rates.shtml)
10. [NJ Department of Labor 2026 Benefit Rates (Dec 2025)](https://www.nj.gov/labor/lwdhome/press/2025/20251229_newbenefitrates2026.shtml)

### Legal Resources

11. [Legal Services of New Jersey - Unemployment Eligibility](https://www.lsnjlaw.org/legal-topics/jobs-employment/unemployment-insurance/claims/pages/unemployment-eligibility)
12. [Legal Services of New Jersey - Voluntary Quit](https://www.lsnjlaw.org/legal-topics/jobs-employment/unemployment-insurance/voluntary-quit-misconduct/pages/voluntary-quit-aspx)
13. [NJ Statutes 43:21-5 - Disqualification for benefits](https://law.justia.com/codes/new-jersey/title-43/section-43-21-5/)

---

## PDFs for Future Reference

1. **NJ Unemployment Compensation Law (Full Statute)**
   - URL: https://nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf
   - Contains: Complete statutory text of N.J.S.A. 43:21-1 et seq.
   - Note: PDF could not be parsed; contains benefit calculation formulas and legal definitions

2. **Work Search Log Template (BC_514)**
   - URL: https://www.nj.gov/labor/myunemployment/assets/pdfs/BC_514.pdf
   - Contains: Official work search documentation form

3. **NJ Employer Handbook - Unemployment Insurance Section**
   - URL: https://www.nj.gov/labor/ea/help/employer_handbook/ui.shtml
   - Contains: Employer perspective on UI, including contribution rates

---

## Key Formulas Summary

### Weekly Benefit Rate (WBR)
```
WBR = min(0.60 × Average Weekly Wage in Base Period, Maximum Weekly Benefit)
```

### Weekly Benefit Rate with Dependents
```
WBR_with_deps = min(WBR × (1 + dependency_rate), Maximum Weekly Benefit)

where dependency_rate:
  - 1 dependent: 0.07
  - 2 dependents: 0.11
  - 3+ dependents: 0.15
```

### Partial Weekly Benefit
```
Partial_Benefit_Rate = WBR × 1.20
Partial_Benefit = max(0, min(Partial_Benefit_Rate - Gross_Wages, WBR))
```

### Maximum Total Benefits
```
Max_Total_Benefits = min(weeks_worked_in_base_period, 26) × WBR
```

### Monetary Eligibility (2026)
```
Eligible if:
  (base_weeks >= 20 AND weekly_wage_per_base_week >= $310)
  OR
  (total_base_year_earnings >= $15,500)
```

---

## Implementation Notes

### Parameters to Create

The following parameters would need to be created for NJ Unemployment Insurance:

1. **Weekly Benefit Rate Calculation**
   - `nj_unemployment_insurance_wbr_rate`: 0.60 (60% of average weekly wage)

2. **Maximum Weekly Benefit**
   - `nj_unemployment_insurance_max_weekly_benefit`
     - 2024-01-01: 854
     - 2025-01-01: 875
     - 2026-01-01: 905

3. **Eligibility - Base Week Amount**
   - `nj_unemployment_insurance_base_week_amount`
     - 2024-01-01: 283
     - 2025-01-01: 303
     - 2026-01-01: 310

4. **Eligibility - Minimum Total Earnings (Alternative)**
   - `nj_unemployment_insurance_min_total_earnings`
     - 2024-01-01: 14_200
     - 2025-01-01: 15_200
     - 2026-01-01: 15_500

5. **Eligibility - Required Base Weeks**
   - `nj_unemployment_insurance_required_base_weeks`: 20

6. **Dependency Allowance Rates**
   - `nj_unemployment_insurance_dependency_rate_first`: 0.07
   - `nj_unemployment_insurance_dependency_rate_additional`: 0.04
   - `nj_unemployment_insurance_dependency_max_rate`: 0.15
   - `nj_unemployment_insurance_max_dependents`: 3

7. **Maximum Duration**
   - `nj_unemployment_insurance_max_weeks`: 26

8. **Partial Benefit Rate**
   - `nj_unemployment_insurance_partial_benefit_multiplier`: 1.20

9. **Disqualification Periods**
   - `nj_unemployment_insurance_misconduct_disqualification_weeks`: 5
   - `nj_unemployment_insurance_refuse_work_disqualification_weeks`: 4

10. **Work Search Requirements**
    - `nj_unemployment_insurance_min_weekly_job_contacts`: 3

---

## Validation Checklist

- [x] WBR formula confirmed: 60% of average weekly wage
- [x] Maximum weekly benefit 2024 confirmed: $854
- [x] Maximum weekly benefit 2025 confirmed: $875
- [x] Maximum weekly benefit 2026 confirmed: $905
- [x] Base week requirement 2024 confirmed: $283
- [x] Base week requirement 2025 confirmed: $303
- [x] Base week requirement 2026 confirmed: $310
- [x] Alternative total earnings 2024 confirmed: $14,200
- [x] Alternative total earnings 2025 confirmed: $15,200
- [x] Alternative total earnings 2026 confirmed: $15,500
- [x] Required base weeks confirmed: 20
- [x] Maximum duration confirmed: 26 weeks
- [x] Dependency rates confirmed: 7% first, 4% additional, 15% max
- [x] Partial benefit multiplier confirmed: 1.20 (20% higher than WBR)
- [x] Base period definition confirmed: First 4 of last 5 completed quarters
- [x] Alternate base year definitions confirmed
- [x] Misconduct disqualification period confirmed: 5 weeks
- [x] Refuse work disqualification confirmed: 4 weeks
- [x] Work search minimum contacts confirmed: 3 per week
