# PolicyEngine US Program Summary

This provides an overview of the tax and benefit programs modeled in PolicyEngine US, organized by administering agency.

## Federal Programs

### Internal Revenue Service (IRS)

**Core Tax Structure**
- **Individual Income Tax**: Progressive tax brackets, filing status rules
- **Alternative Minimum Tax (AMT)**: Parallel tax system ensuring minimum tax payment
- **Capital Gains Tax**: Preferential rates for long-term gains, ordinary rates for short-term
- **Net Investment Income Tax**: Additional tax on investment income for high earners
- **Additional Medicare Tax**: Surtax on high wage and self-employment income
- **Payroll Taxes**: Social Security and Medicare taxes on wages
- **Self-Employment Tax**: Social Security and Medicare for self-employed

**Income Calculations**
- **Adjusted Gross Income (AGI)**: Base for many tax calculations
- **Modified AGI variations**: Different definitions for various provisions
- **Taxable Income**: AGI less deductions and exemptions

**Deductions**
- **Standard Deduction**: Basic deduction with additional amounts for elderly/blind
- **Itemized Deductions**: 
  - State and Local Tax (SALT) deduction with cap
  - Mortgage interest deduction
  - Charitable contributions
  - Medical expenses above threshold
  - Casualty losses
- **Above-the-Line Deductions**: Student loan interest, self-employed health insurance, retirement contributions
- **Qualified Business Income Deduction (QBID)**: 20% deduction for pass-through entities

**Tax Credits**
- **Earned Income Tax Credit (EITC)**: Refundable credit for working families
- **Child Tax Credit (CTC)**: Partially refundable credit for children
- **Child and Dependent Care Credit (CDCC)**: For work-related care expenses
- **American Opportunity Tax Credit**: Partially refundable education credit
- **Lifetime Learning Credit**: Non-refundable education credit
- **Premium Tax Credit**: Health insurance subsidies
- **Retirement Savings Credit**: For retirement contributions
- **Residential Clean Energy Credit**: Solar, batteries, other renewables
- **Clean Vehicle Credits**: New and used electric vehicles
- **Energy Efficient Home Improvement Credit**: Insulation, HVAC, etc.
- **Elderly and Disabled Credit**: For qualifying taxpayers
- **Foreign Tax Credit**: Prevents double taxation

**Special Provisions**
- **Kiddie Tax**: Unearned income of children taxed at parent's rate
- **Social Security Benefit Taxation**: Partial taxation based on combined income
- **Unemployment Compensation Taxation**: Federal tax treatment
- **Recovery Rebate Credits**: Economic impact payments

### Department of Health and Human Services (HHS)

- **Medicaid**: Health insurance for low-income individuals and families
- **Children's Health Insurance Program (CHIP)**: Health coverage for uninsured children
- **Temporary Assistance for Needy Families (TANF)**: Time-limited cash assistance
- **Child Care and Development Fund (CCDF)**: Child care subsidies (CA, CO, NE modeled)
- **Head Start**: Early childhood education
- **Low Income Home Energy Assistance Program (LIHEAP)**: Utility assistance (DC, MA modeled)
- **Medicare**: Health insurance for elderly and disabled (limited modeling)

### Social Security Administration (SSA)

- **Supplemental Security Income (SSI)**: Cash assistance for aged, blind, disabled
- **Social Security Retirement**: Monthly benefits for retired workers
- **Social Security Disability Insurance (SSDI)**: Benefits for disabled workers
- **Social Security Survivors**: Benefits for surviving family members

### Department of Agriculture (USDA)

- **Supplemental Nutrition Assistance Program (SNAP)**: Food assistance
- **Special Supplemental Nutrition Program for WIC**: Women, infants, children
- **National School Lunch Program**: Free and reduced-price meals
- **School Breakfast Program**: Morning meals
- **Commodity Supplemental Food Program (CSFP)**: Food packages for seniors
- **Food Distribution Program on Indian Reservations (FDPIR)**: Alternative to SNAP

### Department of Housing and Urban Development (HUD)

- **Housing Choice Vouchers (Section 8)**: Rental assistance
- **Public Housing**: Government-owned units
- **Project-Based Section 8**: Property-specific assistance

### Department of Education

- **Pell Grant**: Need-based undergraduate grants
- **Federal Student Aid**: Loans and work-study (limited modeling)

### Federal Communications Commission (FCC)

- **Lifeline**: Phone and internet discounts
- **Affordable Connectivity Program**: Broadband subsidies (ended 2024)
- **Emergency Broadband Benefit**: Pandemic program (ended)

### Department of Energy

- **Weatherization Assistance Program**: Home energy efficiency
- **High Efficiency Electric Home Rebate**: Appliance rebates

### Affordable Care Act Programs

- **Premium Tax Credit**: Health insurance subsidies
- **Cost-Sharing Reductions**: Lower out-of-pocket costs
- **Individual Mandate**: Tax penalty (zeroed out)

## State Programs

### State Tax Systems

**Income Taxes**
- Progressive or flat rate structures
- Standard and itemized deductions
- Personal exemptions (where applicable)
- State-specific credits and modifications

**Sales Taxes**
- State and local rates
- Exemptions for necessities

**Property Taxes**
- Assessment and rate modeling
- Homestead exemptions
- Circuit breaker credits

### State-Administered Federal Programs

- **TANF**: CA, CO, DC, IL, NY, NC, OK have detailed implementations
- **Medicaid**: Expansion status and eligibility rules by state
- **SNAP**: Broad-based categorical eligibility options
- **LIHEAP**: DC and MA have detailed implementations
- **CCDF**: CA, CO, NE have child care subsidy programs
- **SSI State Supplements**: CA, CO, MA provide additional benefits

### Major State-Specific Programs

**California**
- CalEITC and Young Child Tax Credit
- CalWORKs (TANF)
- Renter's Credit
- Climate Action Credit

**New York**
- Empire State Child Credit
- NYC tax system
- STAR property tax relief

**State EITCs**
PolicyEngine US models state EITCs for: CA, CO, CT, DC, DE, HI, IA, IL, IN, KS, LA, MA, MD, ME, MI, MN, MT, NE, NJ, NM, NY, OH, OK, OR, RI, SC, UT, VA, VT, WA, WI

**State CTCs**
Several states including CA, CO, CT, ID, ME, MD, NM, NY, OK, OR, UT

**Other State Programs**
- State property tax credits and circuit breakers
- State disability insurance (CA, NJ, NY, RI)
- Various state-specific assistance programs

## Local Programs

### Major Cities
- New York City income tax
- Local EITCs
- Property tax relief programs

## Program Interactions

PolicyEngine models complex interactions:
- Benefit cliffs and marginal tax rates
- Categorical eligibility between programs
- Income definitions and exclusions
- Asset limits and resource rules
- Work requirements and time limits

## Microdata

For information on the enhanced microdata construction used in PolicyEngine US simulations, see the [policyengine-us-data](https://github.com/PolicyEngine/policyengine-us-data) repository.
