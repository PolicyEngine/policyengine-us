# Collected Documentation

## Illinois Senior Citizens Real Estate Tax Deferral Program Implementation
**Collected**: 2026-01-14
**Implementation Task**: Implement the Illinois Senior Citizens Real Estate Tax Deferral Program eligibility and benefit calculation

---

## Official Program Name

**Federal Program**: N/A (State program)
**State's Official Name**: Senior Citizens Real Estate Tax Deferral Program
**Abbreviation**: SCRETD (commonly referred to as "Senior Tax Deferral")
**Source**: 320 ILCS 30/1 (Senior Citizens Real Estate Tax Deferral Act)

**Variable Prefix**: `il_scretd` (e.g., `il_scretd_eligible`, `il_scretd_income_eligible`)

---

## Legal Authority

### Primary Statute
- **Title**: Senior Citizens Real Estate Tax Deferral Act
- **Citation**: 320 ILCS 30/1 et seq.
- **URL**: https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31
- **Effective Date**: Originally enacted 1977; multiple amendments

### Related Statutes
- **320 ILCS 25** - Senior Citizens and Persons with Disabilities Property Tax Relief Act (defines "household income")
- **30 ILCS 105/6p-4** - State Finance Act provisions for the deferral fund

### Recent Amendment
- **SB1821** (Public Act effective 2025) - Expanded income limits
- **URL**: https://www.ilga.gov/legislation/BillStatus?DocNum=1821&GAID=18&DocTypeID=SB&LegId=160970&SessionID=114

---

## Program Overview

The Senior Citizens Real Estate Tax Deferral Program allows qualified senior citizens (age 65+) to defer all or part of their property taxes and special assessments on their principal residence. The deferral functions as a loan from the State of Illinois:

1. The State pays the deferred property taxes to the county collector
2. A lien is placed on the property
3. Interest accrues on deferred amounts
4. The deferred amount plus interest must be repaid upon sale, transfer, or death

**Source**: [Illinois Department of Revenue PIO-64](https://tax.illinois.gov/research/publications/pio-64.html)

---

## Eligibility Requirements

### Age Requirement (320 ILCS 30/2)

**Primary Applicant:**
- Must be **65 years of age or older by June 1** of the year the application is filed

**Surviving Spouse:**
- May continue deferrals if **55 years of age or older within six months** of the taxpayer's death
- Must enter into a new tax deferral and recovery agreement

**Source**: [320 ILCS 30/2](https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31), [IDOR Q&A](https://tax.illinois.gov/questionsandanswers/answer.388.html)

### Income Limit (320 ILCS 30/2)

Household income must not exceed the following thresholds:

| Tax Year | Income Limit |
|----------|-------------|
| Through 2005 | $40,000 |
| 2006-2011 | $50,000 |
| 2012-2021 | $55,000 |
| 2022-2024 | $65,000 |
| 2025 | $75,000 |
| 2026 | $77,000 |
| 2027 and thereafter | $79,000 |

**Source**: [320 ILCS 30/2](https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31), [IDOR News Release](https://tax.illinois.gov/research/news/seniors-eligible-for-property-tax-relief.html)

### Household Income Definition (320 ILCS 25/3.07)

"Household income" is defined in 320 ILCS 25/3.07 as the combined income of all household members. "Income" means:

**Federal adjusted gross income (AGI) PLUS the following add-backs:**
- Amounts received as annuities under annuity, endowment, or life insurance contracts
- Benefits paid under the Federal Social Security Act
- Benefits paid under the Railroad Retirement Act
- Public assistance payments from governmental agencies (excluding benefits under this Act)
- Workers' compensation and occupational disease benefits
- Net operating loss or capital loss carryovers
- Interest and dividends

**Examples of income to include** (from PIO-64):
- Alimony received
- Annuity benefits
- Black Lung benefits
- Business income
- Capital gains
- Cash assistance from Human Services
- Cash winnings (raffles, lotteries)
- Civil Service benefits
- Dividends
- Farm income
- Interest
- Pension and IRA benefits (federally taxable portion)
- Railroad Retirement benefits
- Rental income
- Social Security benefits
- Miscellaneous income

**Source**: [320 ILCS 25/3.07](https://ilga.gov/legislation/ilcs/documents/032000250K3.07.htm), [PIO-64](https://tax.illinois.gov/research/publications/pio-64.html)

### Property Requirements (320 ILCS 30/2, 30/3)

1. **Principal Residence**: Property must be the taxpayer's principal residence ("homestead")
2. **Ownership Duration**: Must have owned and occupied the property (or other qualifying Illinois residence) for **at least the last three years**
3. **Ownership Type**: Must own the property, share joint ownership with spouse, or be sole beneficiary (or co-beneficiary with spouse) of an Illinois land trust
4. **Non-Income Producing**: Property cannot be used to generate income
5. **No Delinquent Taxes**: No unpaid property taxes or special assessments on the property
6. **Insurance**: Must maintain adequate fire or casualty insurance coverage

**Homestead Definition** (320 ILCS 30/2):
> "Homestead" means the land and buildings thereon, including a condominium or a dwelling unit in a multidwelling building that is owned and operated as a cooperative, occupied by the taxpayer as his residence or which are temporarily unoccupied by the taxpayer because such taxpayer is temporarily residing, for not more than 1 year, in a licensed facility as defined in Section 1-113 of the Nursing Home Care Act.

**Source**: [320 ILCS 30/2](https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31), [PIO-64](https://tax.illinois.gov/research/publications/pio-64.html)

---

## Benefit Calculation

### Maximum Annual Deferral

**Amount**: $7,500 per tax year (includes both 1st and 2nd installments)

This limit includes:
- Deferred property taxes
- Interest charges
- Lien fees

**Source**: [PIO-64](https://tax.illinois.gov/research/publications/pio-64.html)

### Cumulative Deferral Limit - 80% Equity Rule

The maximum **cumulative** amount that can be deferred (including interest and lien fees) is **80 percent of the taxpayer's equity interest** in the property.

**Equity Calculation** (320 ILCS 30/2):
> "Equity interest" means the current assessed valuation of the qualified property times the fraction necessary to convert that figure to full market value minus any outstanding debts or liens on that property.

**Formula:**
```
Equity Interest = (Assessed Value x Equalization Factor) - Outstanding Debts/Liens

Maximum Cumulative Deferral = Equity Interest x 0.80
```

**Notes:**
- For property without separate assessed valuation, use appraised value from qualified real estate appraiser
- Previous senior deferrals are NOT included when calculating outstanding debts
- Forms IL-1017 and IL-1018 include worksheets for calculating equity

**Source**: [320 ILCS 30/2](https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31), [Lake County IL](https://www.lakecountyil.gov/511/Senior-Citizen-Tax-Deferral-Program)

### Interest Rate (320 ILCS 30/3)

Interest accrues as **simple interest** (not compound) on deferred amounts:

| Tax Year | Annual Interest Rate |
|----------|---------------------|
| 2022 and prior | 6% |
| 2023 and thereafter | 3% |

**Example** (from PIO-64):
- $2,000 deferred generates $60 first-year interest at 3% rate

**Source**: [320 ILCS 30/3](https://ilga.gov/Documents/legislation/ilcs/documents/032000300K3.htm), [PIO-64](https://tax.illinois.gov/research/publications/pio-64.html)

---

## Repayment Requirements (320 ILCS 30/3)

### Triggering Events

Deferred amounts plus accrued interest must be repaid:

1. **Upon Sale or Transfer**: Before closing and recording
   - No sale or transfer may be legally closed until all deferred amounts are paid
   - Collector may certify arrangement for prompt payment

2. **Upon Taxpayer Death**: Within **one year** of death
   - Exception: Surviving spouse 55+ may continue deferral (see below)
   - Heirs cannot take priority until amounts are paid

3. **Property No Longer Qualifies**: Within **90 days**
   - If property ceases to be qualifying property
   - If taxpayer fails to reapply annually

**Surviving Spouse Continuation**:
A surviving spouse who is at least 55 years old within six months of the taxpayer's death may continue the tax-deferred status by:
1. Being the heir-at-law, assignee, or legatee
2. Entering into a new tax deferral and recovery agreement before deferred taxes become due

**Early Repayment**: Permitted at any time with no penalty

**Failure to Pay**: May result in foreclosure proceedings under the Property Tax Code

**Source**: [320 ILCS 30/3](https://ilga.gov/Documents/legislation/ilcs/documents/032000300K3.htm), [IDOR Q&A](https://tax.illinois.gov/questionsandanswers/answer.388.html)

---

## Application Process

### Filing Period
- **Opens**: January 1
- **Deadline**: March 1 of each year

### Where to Apply
- County Collector's Office (not the State)

### Required Forms
- **IL-1017**: Application for Deferral of Real Estate/Special Assessment Taxes
- **IL-1018**: Real Estate/Special Assessment Tax Deferral and Recovery Agreement
  - Requires notarized signature
  - If property is in trust, both trustee (bank/trust company) and homeowner must sign

### Worksheets on Forms
- **Worksheet A**: Calculate total household income
- **Step 1**: Fair market value (assessed value x equalization factor, or township valuation x 3)
- **Step 3**: Calculate current equity interest

**Source**: [PIO-64](https://tax.illinois.gov/research/publications/pio-64.html), [DuPage County](https://www.dupagecounty.gov/elected_officials/treasurer/senior_serve/senior_citizens__real_estate_tax_deferral_program.php)

---

## Non-Simulatable Rules (Architecture Limitation)

### Cannot be fully simulated (requires historical tracking):
- **3-Year Ownership Requirement**: Cannot verify ownership duration
- **80% Equity Cumulative Limit**: Cannot track cumulative deferrals across years
- **Interest Accumulation**: Cannot track multi-year interest accrual
- **Annual Reapplication**: Cannot enforce annual renewal requirement

### Can be simulated (point-in-time):
- Age eligibility (65+ by June 1)
- Income eligibility (household income vs. threshold)
- Annual deferral limit ($7,500)
- Current year interest rate
- Surviving spouse age eligibility (55+)

---

## Summary of Key Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Primary Age Threshold | 65 years (by June 1) | 320 ILCS 30/2 |
| Surviving Spouse Age | 55 years (within 6 months of death) | 320 ILCS 30/3 |
| Income Limit (2025) | $75,000 | SB1821 |
| Income Limit (2026) | $77,000 | SB1821 |
| Income Limit (2027+) | $79,000 | SB1821 |
| Maximum Annual Deferral | $7,500 | 320 ILCS 30/3 |
| Maximum Cumulative (% Equity) | 80% | 320 ILCS 30/3 |
| Interest Rate (2023+) | 3% simple | 320 ILCS 30/3 |
| Interest Rate (2022 and prior) | 6% simple | 320 ILCS 30/3 |
| Ownership Duration Required | 3 years | 320 ILCS 30/3 |
| Repayment After Death | 1 year | 320 ILCS 30/3 |
| Repayment After Disqualification | 90 days | 320 ILCS 30/3 |

---

## References for Metadata

### For Parameters
```yaml
reference:
  - title: 320 ILCS 30/2 - Definitions
    href: https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31
  - title: Illinois Department of Revenue PIO-64
    href: https://tax.illinois.gov/research/publications/pio-64.html
```

### For Variables
```python
reference = "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31"
# or for income definition:
reference = "https://ilga.gov/legislation/ilcs/documents/032000250K3.07.htm"
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **IDOR News Release (December 2025)**
   - URL: https://www.illinois.gov/content/dam/soi/en/web/illinois/iisnewsattachments/32009-121625-idor-encourages-seniors-to-apply-for-expanded-senior-tax-deferral-program-12-16-25.pdf.pdf
   - Expected content: Details on the 2025 income limit expansion under SB1821

2. **Whiteside County IL Deferral Program Document**
   - URL: https://www.whitesidecountyil.gov/DocumentCenter/View/210/Senior-Citizen-Deferral-Program-PDF
   - Expected content: County-specific application instructions and worksheets

3. **Lake County Senior Deferral Sample Application**
   - URL: https://www.lakecountyil.gov/DocumentCenter/View/38172/Senior-Deferral-Sample-Application
   - Expected content: Sample IL-1017 and IL-1018 forms with instructions

4. **Lake County Senior Citizens Real Estate Tax Deferral Supplement**
   - URL: https://www.lakecountyil.gov/DocumentCenter/View/81066/Senior-Citizens-Real-Estate-Tax-Deferral-Supplement
   - Expected content: Detailed household income calculation worksheet and equity calculation instructions

---

## Implementation Notes

### Variable Structure Recommendation

```
il_scretd/
  eligibility/
    il_scretd_age_eligible.py           # Age 65+ check
    il_scretd_income_eligible.py        # Income vs. threshold
    il_scretd_eligible.py               # Combined eligibility
  il_scretd_household_income.py         # Household income per 320 ILCS 25
  il_scretd_maximum_deferral.py         # $7,500 annual limit
  il_scretd_interest_rate.py            # 3% or 6% depending on year
```

### Entity Level
- **Tax Unit** or **Household** level (property-owner based program)

### Key Considerations
1. The program is household-based but tied to property ownership
2. Income definition references a separate statute (320 ILCS 25)
3. Some eligibility criteria cannot be verified in simulation (ownership duration, insurance)
4. The 80% equity limit is cumulative and cannot be fully modeled

---

## Sources

- [Illinois Department of Revenue PIO-64](https://tax.illinois.gov/research/publications/pio-64.html)
- [320 ILCS 30 - Senior Citizens Real Estate Tax Deferral Act](https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1454&ChapterID=31)
- [320 ILCS 25/3.07 - Income Definition](https://ilga.gov/legislation/ilcs/documents/032000250K3.07.htm)
- [IDOR Q&A - What is the Program?](https://tax.illinois.gov/questionsandanswers/answer.385.html)
- [IDOR Q&A - Repayment Requirements](https://tax.illinois.gov/questionsandanswers/answer.388.html)
- [IDOR News - Expanded Eligibility](https://tax.illinois.gov/research/news/seniors-eligible-for-property-tax-relief.html)
- [Lake County Senior Tax Deferral](https://www.lakecountyil.gov/511/Senior-Citizen-Tax-Deferral-Program)
- [DuPage County Senior Tax Deferral](https://www.dupagecounty.gov/elected_officials/treasurer/senior_serve/senior_citizens__real_estate_tax_deferral_program.php)
- [Cook County Treasurer - Tax Deferral](https://www.cookcountytreasurer.com/theseniorcitizenrealestatetaxdeferralprogram.aspx)
- [ATG - Senior Citizens Real Estate Tax Deferral Act](https://www.atgf.com/tools-publications/pubs/senior-citizens-real-estate-tax-deferral-act)
