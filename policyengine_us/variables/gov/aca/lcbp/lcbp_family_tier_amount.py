from policyengine_us.model_api import *


class lcbp_family_tier_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA bronze family tier premium amount"
    unit = USD
    definition_period = MONTH
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        base_cost = tax_unit.household("lcbp_age_0", period)
        family_tier_multiplier = tax_unit("lcbp_family_tier_multiplier", period)
        return base_cost * family_tier_multiplier
