from openfisca_us.model_api import *


class is_state_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Exempt from state income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        limit = tax_unit("state_income_tax_exempt_limit", period)
        agi = tax_unit("adjusted_gross_income", period)
        return agi <= limit
