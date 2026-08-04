from policyengine_us.model_api import *


class housing_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing assistance"
    unit = USD
    documentation = "Housing assistance"
    definition_period = YEAR
    defined_for = "is_eligible_for_housing_assistance"

    def formula(spm_unit, period, parameters):
        if parameters(period).gov.hud.abolition:
            return 0

        takes_up = spm_unit("takes_up_housing_assistance_if_eligible", period)
        return spm_unit("hud_hap", period) * takes_up
