from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.ptc.selected_marketplace_plan_category import (
    MarketplacePlanCategory,
)


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
        selected_plan_category = tax_unit(
            "selected_marketplace_plan_category", period
        )
        silver_premium = tax_unit("slcsp", period) * tax_unit(
            "selected_marketplace_plan_benchmark_ratio", period
        )
        selected_plan_premium = where(
            selected_plan_category == MarketplacePlanCategory.BRONZE,
            tax_unit("lcbp", period),
            silver_premium,
        )
        return where(
            takes_up_aca_if_eligible & pays_marketplace_premium,
            selected_plan_premium,
            0,
        )
