from openfisca_us.model_api import *


class ny_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income tax before credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ny_taxable_income", period)
        filing_status = tax_unit("filing_status", period)

        rates = parameters(period).gov.states.ny.tax.income.rates

        return rates.single.calc(taxable_income)



