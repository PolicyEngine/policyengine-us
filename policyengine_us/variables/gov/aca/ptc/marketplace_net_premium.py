from policyengine_us.model_api import *


class marketplace_net_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Marketplace plan net premium after PTC"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Annual net premium paid by a tax unit for its selected Marketplace "
        "plan, after the advance premium tax credit is applied. Equal to "
        "the plan premium proxy minus the PTC actually used. Zero for "
        "households not taking up Marketplace coverage."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/36B"

    def formula(tax_unit, period, parameters):
        plan_cost = tax_unit("selected_marketplace_plan_premium_proxy", period)
        used_ptc = tax_unit("used_aca_ptc", period)
        return max_(plan_cost - used_ptc, 0)
