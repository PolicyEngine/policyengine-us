from policyengine_us.model_api import *


class housing_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing assistance"
    unit = USD
    documentation = "Housing assistance"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        hap = spm_unit("hud_hap", period)
        eligible = spm_unit("is_eligible_for_housing_assistance", period)
        return hap * eligible
