from policyengine_us.model_api import *


class selected_marketplace_plan_premium_proxy(Variable):
    value_type = float
    entity = TaxUnit
    label = "Selected marketplace plan premium proxy"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        takes_up_aca_if_eligible = tax_unit("takes_up_aca_if_eligible", period)
        person = tax_unit.members
        pays_marketplace_premium = tax_unit.sum(person("pays_aca_premium", period)) > 0
        return where(
            takes_up_aca_if_eligible & pays_marketplace_premium,
            tax_unit("slcsp", period)
            * tax_unit("selected_marketplace_plan_benchmark_ratio", period),
            0,
        )
