from policyengine_us.model_api import *


class unused_aca_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unused ACA premium tax credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return max_(0, tax_unit("aca_ptc", period) - tax_unit("used_aca_ptc", period))
