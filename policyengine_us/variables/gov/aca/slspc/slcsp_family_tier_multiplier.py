from policyengine_us.model_api import *


class slcsp_family_tier_multiplier(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA family tier multiplier for premium calculation"
    unit = "/1"
    definition_period = MONTH
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        family_category = tax_unit("slcsp_family_tier_category", period)
        p = parameters(period).gov.aca.family_tier_ratings
        state_code = tax_unit.household("state_code", period)
        in_ny = state_code == state_code.possible_values.NY
        return where(in_ny, p.ny[family_category], p.vt[family_category])
