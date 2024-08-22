from policyengine_us.model_api import *


class hud_low_income_factor(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD Low income factor"
    unit = USD
    documentation = "Low income factor for HUD programs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        p_hud = parameters(period).gov.hud.ami_limit
        size = spm_unit("spm_unit_size", period)
        size_limit = p_hud.family_size
        size_limit_excess = p_hud.per_person_exceeding_4
        size_exceeding_4 = max_(size - 4, 0)
        size_capped_at_4 = min_(size, 4)
        return (
            size_limit.LOW[size_capped_at_4]
            + size_limit_excess.LOW * size_exceeding_4
        )
