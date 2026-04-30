from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.ptc.selected_marketplace_plan_category import (
    MarketplacePlanCategory,
)


class marketplace_csr_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tax unit is eligible for ordinary Marketplace cost-sharing reductions"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/45/155.305#g_1"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        receives_aca = tax_unit.sum(person("person_receives_aca", period)) > 0
        category = tax_unit("selected_marketplace_plan_category", period)
        silver_selected = category == MarketplacePlanCategory.SILVER
        magi_fraction = tax_unit("aca_magi_fraction", period)
        p = parameters(period).gov.aca.csr.income_threshold
        income_eligible = (magi_fraction >= p.minimum) & (magi_fraction <= p.maximum)
        return receives_aca & silver_selected & income_eligible
