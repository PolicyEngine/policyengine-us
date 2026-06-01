from policyengine_us.model_api import *


class HUDIncomeLevel(Enum):
    ABOVE_MODERATE = "Above moderate"
    MODERATE = "Moderate"
    LOW = "Low"
    VERY_LOW = "Very low"
    ESPECIALLY_LOW = "Especially low"


class hud_income_level(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = HUDIncomeLevel
    default_value = HUDIncomeLevel.ABOVE_MODERATE
    label = "HUD income level"
    documentation = "Income level for HUD programs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        annual_income = spm_unit("hud_annual_income", period)
        ami = spm_unit.household("ami", period)
        extremely_low_limit = spm_unit("hud_extremely_low_income_limit", period)
        very_low_limit = spm_unit("hud_very_low_income_limit", period)
        low_limit = spm_unit("hud_low_income_limit", period)

        extremely_low_factor = spm_unit("hud_especially_low_income_factor", period)
        very_low_factor = spm_unit("hud_very_low_income_factor", period)
        low_factor = spm_unit("hud_low_income_factor", period)
        moderate_factor = spm_unit("hud_moderate_income_factor", period)

        fallback_extremely_low_limit = extremely_low_factor * ami
        fallback_very_low_limit = very_low_factor * ami
        fallback_low_limit = low_factor * ami
        moderate_limit = moderate_factor * ami

        extremely_low_limit = where(
            extremely_low_limit > 0,
            extremely_low_limit,
            fallback_extremely_low_limit,
        )
        very_low_limit = where(
            very_low_limit > 0,
            very_low_limit,
            fallback_very_low_limit,
        )
        low_limit = where(low_limit > 0, low_limit, fallback_low_limit)

        return select(
            [
                (extremely_low_limit > 0) & (annual_income <= extremely_low_limit),
                (very_low_limit > 0) & (annual_income <= very_low_limit),
                (low_limit > 0) & (annual_income <= low_limit),
                (moderate_limit > 0) & (annual_income <= moderate_limit),
            ],
            [
                HUDIncomeLevel.ESPECIALLY_LOW,
                HUDIncomeLevel.VERY_LOW,
                HUDIncomeLevel.LOW,
                HUDIncomeLevel.MODERATE,
            ],
            default=HUDIncomeLevel.ABOVE_MODERATE,
        )
