from policyengine_us.model_api import *


class hud_especially_low_income_factor(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD Especially Low income factor"
    unit = USD
    documentation = "Especially Low income factor for HUD programs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hud.ami_limit
        size = spm_unit("spm_unit_size", period)
        p.family_size_excess = p.per_person_exceeding_4
        size_exceeding_4 = max_(size - 4, 0)
        size_capped_at_4 = min_(size, 4)
        return (
            p.family_size.ESPECIALLY_LOW[size_capped_at_4]
            + p.family_size_excess.ESPECIALLY_LOW * size_exceeding_4
        )
