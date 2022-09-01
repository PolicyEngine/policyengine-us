from openfisca_us.model_api import *
from openfisca_us.variables.household.demographic.tax_unit.filing_status import filing_status

class mo_federal_income_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO Federal income tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=8"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        #without any additions or subtractions, mo_agi is the same as adjusted_gross_income, the Federal AGI measure
        mo_agi = tax_unit("adjusted_gross_income", period)
        federal_tax = tax_unit("income_tax", period)
        filing_status = tax_unit("filing_status", period)

        federal_income_tax_deduction_rates = parameters(period).gov.states.mo.tax.income.deductions.federal_income_tax_deduction_rates
        rate = federal_income_tax_deduction_rates.calc(mo_agi)
        federal_income_tax_deduction_amount = federal_tax * rate

        federal_income_tax_deduction_cap = parameters(period).gov.states.mo.tax.income.deductions.mo_federal_income_tax_deduction_caps[filing_status]        
        
        return min_(federal_income_tax_deduction_amount, federal_income_tax_deduction_cap)
