from policyengine_us.model_api import *


class taxsim_v11(Variable):
    value_type = float
    entity = TaxUnit
    label = "UI in AGI"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("tax_unit_taxable_unemployment_compensation", period)
