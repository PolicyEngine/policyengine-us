from openfisca_us.model_api import *


class v11(Variable):
    value_type = float
    entity = TaxUnit
    label = "UI in AGI"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("taxable_ui", period)
