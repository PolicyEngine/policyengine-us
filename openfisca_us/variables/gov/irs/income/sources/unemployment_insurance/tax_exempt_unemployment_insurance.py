from openfisca_us.model_api import *


class tax_exempt_unemployment_insurance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax-exempt unemployment insurance"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        total_ui = tax_unit("unemployment_insurance", period)
        taxable_ui = tax_unit("taxable_unemployment_insurance", period)
        return total_ui - taxable_ui