from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.ptc.selected_marketplace_plan_category import (
    MarketplacePlanCategory,
)


class selected_marketplace_plan_actuarial_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "Selected Marketplace plan actuarial value"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/45/156.140#b"

    def formula(tax_unit, period, parameters):
        category = tax_unit("selected_marketplace_plan_category", period)
        p = parameters(period).gov.aca.metal_actuarial_value
        return where(category == MarketplacePlanCategory.BRONZE, p.bronze, p.silver)
