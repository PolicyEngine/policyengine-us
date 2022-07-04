from openfisca_us.model_api import *


class mo_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-1040%20Print%20Only_2021.pdf"

    def formula(tax_unit, period, parameters):
        agi = tax_unit("agi", period)
        rates = parameters(period).gov.states.mo.tax.income.rates
        tax_due = rates.calc(agi, right=True)
        return tax_due
