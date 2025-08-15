from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value


class nyc_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("nyc_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        rates = parameters(period).gov.local.ny.nyc.tax.income.rates
        return select_filing_status_value(
            filing_status,
            rates,
            taxable_income,
        )
