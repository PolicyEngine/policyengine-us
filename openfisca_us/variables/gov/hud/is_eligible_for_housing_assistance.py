from openfisca_us.model_api import *


class is_eligible_for_housing_assistance(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is eligible for HUD voucher"
    documentation = "HUD housing assistance payment"
    definition_period = YEAR
    reference = "https://www.hud.gov/sites/dfiles/PIH/documents/HCV_Guidebook_Calculating_Rent_and_HAP_Payments.pdf"

    def formula(spm_unit, period, parameters):
        receives_housing_assistance = spm_unit(
            "receives_housing_assistance", period
        )
        income_level = spm_unit("hud_income_level", period)
        income_levels = income_level.possible_values
        is_income_eligible = (
            (income_level == income_levels.ESPECIALLY_LOW)
            | (income_level == income_levels.VERY_LOW)
            | (income_level == income_levels.LOW)
        )
        return receives_housing_assistance | is_income_eligible
