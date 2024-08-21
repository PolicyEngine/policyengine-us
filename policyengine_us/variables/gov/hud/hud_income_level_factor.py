from policyengine_us.model_api import *


class hud_income_level_factor(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD income level factor"
    documentation = "Income level factor for HUD programs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        p_hud = parameters(period).gov.hud.ami_limit
        size = spm_unit("spm_unit_size", period)
        size_limit = p_hud.family_size
        size_limit_excess = p_hud.per_person_exceeding_4
        size_exceeding_4 = max_(size - 4, 0)
        size_capped_at_4 = min_(size, 4)
        moderate_factor = (
            size_limit.MODERATE[size_capped_at_4]
            + size_limit_excess.MODERATE * size_exceeding_4
        )
        low_factor = (
            size_limit.LOW[size_capped_at_4]
            + size_limit_excess.LOW * size_exceeding_4
        )
        very_low_factor = (
            size_limit.VERY_LOW[size_capped_at_4]
            + size_limit_excess.VERY_LOW * size_exceeding_4
        )
        especially_low_factor = (
            size_limit.ESPECIALLY_LOW[size_capped_at_4]
            + size_limit_excess.ESPECIALLY_LOW * size_exceeding_4
        )
        income_level = spm_unit("hud_income_level", period)
        income_levels = income_level.possible_values
        return select(
            [
                income_level == income_levels.MODERATE,
                income_level == income_levels.LOW,
                income_level == income_levels.VERY_LOW,
                income_level == income_levels.ESPECIALLY_LOW,
            ],
            [
                moderate_factor,
                low_factor,
                very_low_factor,
                especially_low_factor,
            ],
            default=0,
        )
