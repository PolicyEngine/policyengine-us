# Internal Revenue Service (IRS) Programs

The IRS administers the federal income tax system, including all tax credits, deductions, and collection mechanisms. PolicyEngine US models the complete individual income tax code.

## Tax Credits

### Child Tax Credit (CTC)

**Overview**: Provides tax relief to families with qualifying children under age 17.

**Time Period**: 1998-present (with major expansions in 2021)

**Eligibility**:
- Child must be under 17 at year end
- Must be a qualifying child (relationship, residency, support tests)
- Must have valid SSN (with exceptions for adoption)
- Subject to income phase-outs

**Benefit Calculation**:
- Base credit: $2,000 per child (2018-2025)
- ARPA expansion: $3,000/$3,600 for 2021
- Refundability: Up to $1,400-$1,600 per child (varies by year)
- Phase-out begins at $200,000 (single)/$400,000 (married)

**Key Variables**:
- `ctc_qualifying_child`: Boolean for each person
- `ctc_child_individual_maximum`: Maximum credit per child
- `ctc`: Total Child Tax Credit amount

**Legislative Sources**:
- IRC Section 24
- Tax Cuts and Jobs Act (2017)
- American Rescue Plan Act (2021)

### Earned Income Tax Credit (EITC)

**Overview**: Refundable credit for low-to-moderate income workers.

**Time Period**: 1975-present

**Eligibility**:
- Earned income requirements
- Investment income limit ($10,000+ for 2023)
- Valid SSN required
- Age requirements (25-64 for childless, exceptions apply)

**Benefit Calculation**:
- Credit rates: 7.65% (0 children) to 45% (3+ children)
- Maximum credits: $560-$6,935 (2023)
- Complex phase-in and phase-out schedule
- Marriage penalty mitigation adjustments

**Key Variables**:
- `eitc_eligible`: Eligibility determination
- `eitc_phase_in_rate`: Applicable phase-in rate
- `eitc_maximum`: Maximum credit amount
- `eitc`: Final EITC amount

**Legislative Sources**:
- IRC Section 32
- Annual inflation adjustments per IRC

### Child and Dependent Care Credit (CDCC)

**Overview**: Credit for employment-related child care expenses.

**Time Period**: 1976-present

**Eligibility**:
- Care must be for qualifying persons (children under 13, disabled dependents)
- Expenses must be work-related
- Provider cannot be a relative under 19

**Benefit Calculation**:
- Expense limits: $3,000 (1 qualifying person), $6,000 (2+)
- Credit rate: 20-35% based on AGI
- ARPA expansion for 2021: Up to 50% rate, refundable

**Key Variables**:
- `childcare_expenses`: Annual qualifying expenses
- `cdcc_relevant_expenses`: Capped expenses
- `cdcc_rate`: Applicable credit percentage
- `cdcc`: Credit amount

**Legislative Sources**:
- IRC Section 21
- American Rescue Plan Act (2021) temporary changes

### Education Credits

#### American Opportunity Tax Credit (AOTC)

**Overview**: Credit for first four years of post-secondary education.

**Benefit Calculation**:
- 100% of first $2,000 + 25% of next $2,000 in expenses
- Maximum $2,500 per eligible student
- 40% refundable
- Phase-out: $80,000-$90,000 (single), $160,000-$180,000 (married)

**Key Variables**:
- `american_opportunity_credit_eligible`: Student eligibility
- `qualified_tuition_expenses`: Qualifying education expenses
- `american_opportunity_credit`: Credit amount

#### Lifetime Learning Credit

**Overview**: Credit for all post-secondary education and job skills courses.

**Benefit Calculation**:
- 20% of first $10,000 in expenses
- Maximum $2,000 per return
- Non-refundable
- Phase-out at lower income levels than AOTC

### Premium Tax Credit (PTC)

**Overview**: Subsidizes health insurance premiums for marketplace coverage.

**Time Period**: 2014-present (ACA implementation)

**Eligibility**:
- Income between 100-400% FPL (with temporary expansions)
- Not eligible for affordable employer coverage
- Not eligible for government programs (Medicare, Medicaid)

**Benefit Calculation**:
- Based on second-lowest cost Silver plan (SLCSP)
- Applicable percentage of income varies by FPL level
- Premium cap ranges from 2-9.5% of income
- Advance payments reconciled on tax return

**Key Variables**:
- `is_aca_ptc_eligible`: Eligibility determination
- `aca_slcsp`: Benchmark plan premium
- `aca_ptc`: Premium tax credit amount

**Legislative Sources**:
- IRC Section 36B
- American Rescue Plan Act temporary enhancements

## Income Tax Computation

### Tax Rate Structure

**Ordinary Income Tax Brackets** (2024):
- 10%: $0-$11,000 (single), $0-$22,000 (married)
- 12%: $11,000-$44,725 (single)
- 22%: $44,725-$95,375 (single)
- 24%: $95,375-$182,050 (single)
- 32%: $182,050-$231,250 (single)
- 35%: $231,250-$578,125 (single)
- 37%: Above $578,125 (single)

**Capital Gains Tax Rates**:
- 0%: Below ~$44,625 (single)
- 15%: Middle income ranges
- 20%: Above ~$492,300 (single)
- Additional 3.8% Net Investment Income Tax at high incomes

### Standard Deduction

**2024 Amounts**:
- Single: $14,600
- Married Filing Jointly: $29,200
- Head of Household: $21,900
- Additional amounts for elderly/blind

### Alternative Minimum Tax (AMT)

**Overview**: Parallel tax system to ensure minimum tax payment.

**Key Features**:
- Exemption: $85,700 (single), $133,300 (married) for 2024
- Tax rates: 26% and 28%
- Disallows certain deductions (SALT, misc. itemized)
- Phase-out of exemption at high incomes

**Key Variables**:
- `alternative_minimum_tax_income`: AMTI calculation
- `amt_exemption`: Applicable exemption amount
- `alternative_minimum_tax`: AMT liability

## Payroll Taxes

### Social Security Tax

**Rates**:
- Employee: 6.2% of wages
- Employer: 6.2% of wages
- Self-employed: 12.4% of net earnings

**Wage Base**: $160,200 (2023), indexed annually

**Key Variables**:
- `social_security_taxable_wages`: Wages subject to tax
- `employee_social_security_tax`: Employee portion
- `employer_social_security_tax`: Employer portion

### Medicare Tax

**Rates**:
- Employee: 1.45% of all wages
- Employer: 1.45% of all wages
- Additional Medicare Tax: 0.9% on high earners
- Self-employed: 2.9% + 0.9% additional

**Additional Medicare Tax Thresholds**:
- Single: $200,000
- Married Filing Jointly: $250,000

## Business Income

### Qualified Business Income Deduction (Section 199A)

**Overview**: 20% deduction for pass-through business income.

**Time Period**: 2018-2025 (TCJA provision)

**Calculation**:
- 20% of qualified business income
- Subject to W-2 wage and property limitations
- Specified service trades or businesses (SSTB) phase-out
- Overall taxable income limitations

**Key Variables**:
- `qualified_business_income`: QBI from all sources
- `qbi_deduction`: Section 199A deduction amount

## Filing Status and Exemptions

### Filing Status Determination

**Categories**:
- Single
- Married Filing Jointly
- Married Filing Separately
- Head of Household
- Qualifying Widow(er)

**Key Variables**:
- `filing_status`: Enum of filing status options
- `tax_unit_married`: Boolean for married couples
- `head_of_household_eligible`: HOH qualification

### Dependent Exemptions

**Note**: Personal and dependent exemptions suspended 2018-2025 under TCJA.

**Other Dependent Credit**: $500 for dependents not qualifying for CTC.

## Withholding and Payments

### Income Tax Withholding

**Calculation**: Based on W-4 elections and withholding tables.

**Key Variables**:
- `income_tax_withholding`: Federal tax withheld from wages
- `eitc_advance`: Advance EITC payments (discontinued)

### Estimated Tax Payments

**Requirements**: Required if tax owed exceeds $1,000 after withholding.

### Refunds and Balances

**Calculation**: Total payments minus total tax liability.

**Key Variables**:
- `income_tax_refund`: Amount to be refunded
- `income_tax_owed`: Balance due

## Recent Legislative Changes

### Tax Cuts and Jobs Act (2017)
- Doubled standard deduction
- Suspended personal exemptions
- Expanded CTC
- Created QBI deduction
- Limited SALT deduction to $10,000

### American Rescue Plan Act (2021)
- Expanded CTC to $3,000/$3,600
- Made CTC fully refundable
- Expanded EITC for childless workers
- Made CDCC refundable with higher rates
- Enhanced PTC subsidies

### Inflation Reduction Act (2022)
- Extended enhanced PTC through 2025
- Created/expanded clean energy credits

## Implementation Notes

All IRS programs in PolicyEngine US:
- Follow current law baselines with legislative sunsets
- Include automatic inflation adjustments where applicable
- Model interactions between provisions (e.g., AMT and credits)
- Account for filing status differences
- Include state tax deduction interactions