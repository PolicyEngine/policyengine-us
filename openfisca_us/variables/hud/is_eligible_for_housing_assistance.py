from openfisca_us.model_api import *


class is_eligible_for_housing_assistance(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is eligible for HUD voucher"
    documentation = "HUD housing assistance payment"
    definition_period = YEAR
    reference = "https://www.hud.gov/sites/dfiles/PIH/documents/HCV_Guidebook_Calculating_Rent_and_HAP_Payments.pdf"

    def formula(spm_unit, period, parameters):
        receives_housing_assistance = spm_unit("receives_housing_assistance", period)
        hud_annual_income = spm_unit("hud_annual_income", period)
        fpl = spm_unit("fpl", period)
        hud_fpl_percent = hud_annual_income / fpl
        limit = parameters(period).hud.housing_assistance.limit
        return receives_housing_assistance | (hud_fpl_percent <= limit)
