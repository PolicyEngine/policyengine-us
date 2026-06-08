from policyengine_us.model_api import *


class selected_marketplace_plan_actuarial_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "Selected Marketplace plan actuarial value"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/45/156.140#b"

    def formula(tax_unit, period, parameters):
        takes_up_aca_if_eligible = tax_unit("takes_up_aca_if_eligible", period)
        person = tax_unit.members
        pays_marketplace_premium = tax_unit.sum(person("pays_aca_premium", period)) > 0
        category = tax_unit("selected_marketplace_plan_category", period)
        p = parameters(period).gov.aca.metal_actuarial_value
        selected_plan_av = where(
            category == category.possible_values.BRONZE,
            p.bronze,
            p.silver,
        )
        return where(
            takes_up_aca_if_eligible & pays_marketplace_premium,
            selected_plan_av,
            0,
        )
