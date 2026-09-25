from policyengine_us.model_api import *


class housing_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing assistance"
    unit = USD
    documentation = """
    Housing assistance the model computes for this unit: HUD's housing
    assistance payment where the unit is eligible and takes up.

    Eligibility is `receives_housing_assistance | (is_renter &
    is_income_eligible)` and take-up defaults to true, so this is a modelled
    amount rather than a report of receipt.
    """
    definition_period = YEAR
    defined_for = "is_eligible_for_housing_assistance"

    def formula(spm_unit, period, parameters):
        if parameters(period).gov.hud.abolition:
            return 0

        takes_up = spm_unit("takes_up_housing_assistance_if_eligible", period)
        return spm_unit("hud_hap", period) * takes_up
