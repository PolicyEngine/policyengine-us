from openfisca_us.model_api import *


class mo_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-1040%20Print%20Only_2021.pdf"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("mo_taxable_income", period)
        rates = parameters(period).gov.states.mo.tax.income.rates
        return rates.calc(taxable_income)
