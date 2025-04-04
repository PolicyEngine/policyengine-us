# DC Child Care Subsidy Program

## Overview

The DC Child Care Subsidy Program helps eligible families with the cost of child care. The program provides subsidies for children from birth to age 12 (or up to 19 for children with disabilities).

## Eligibility Requirements

### Basic Eligibility
- Child must be US citizen or qualified immigrant
- Parents' immigration status is irrelevant
- Default requirement: Parents/guardians working, in job training/education, or seeking employment
- Maximum income: 300% FPL (initial eligibility) or 85% SMI (redetermination)
- Assets under $1,000,000 (self-declaration acceptable)

### Special Categories with Waived Requirements
1. **Full waiver** (activity, income, co-payment):
   - Children under protective services
   - Children of adults with disabilities
   - Children experiencing homelessness
   - Children of teen parents
   - Children in Head Start/Early Head Start/QIN
   - Children in families experiencing domestic violence

2. **Partial waiver** (activity and co-payment only):
   - Children with disabilities
   - Children of elder caregivers
   - Children with parent(s) in addiction recovery

3. **Automatic eligibility** (waived verification requirements):
   - TANF recipients (co-payments waived)
   - SNAP E&T participants (co-payments waived)
   - Families below 150% FPL (co-payments waived)

### Income Rules
- 3-month grace period if income exceeds 85% SMI
- Countable income includes: wages, self-employment, rental income, certain education grants, pensions, retirement distributions, alimony
- Exempt income includes: public benefits (TANF, SNAP, WIC, etc.), Social Security/SSI, unemployment, child support, tax refunds, EITC, foster care payments, non-recurring income

## Implementation Notes

The implementation follows these core principles:
1. **Entity Structure**: Eligibility is determined at the SPM Unit level
2. **Modular Design**: Eligibility logic is broken into separate components
3. **Vectorized Operations**: Uses vectorized numpy operations for efficiency
4. **Parameter-Driven Logic**: All thresholds and limits are defined as parameters

## References

- [DC Child Care Subsidy Program Manual](https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf)