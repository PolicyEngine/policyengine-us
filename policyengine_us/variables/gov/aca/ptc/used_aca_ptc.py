from policyengine_us.model_api import *


class used_aca_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Used ACA premium tax credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return min_(
            tax_unit("aca_ptc", period),
            tax_unit("selected_marketplace_plan_premium_proxy", period),
        )
