from policyengine_us.model_api import *


class va_map_mb_slmb_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP MB SLMB eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("va_map_mb_slmb_income_eligibility", period)
        resources_eligible = spm_unit(
            "va_map_mb_resources_eligibility", period
        )
        return income_eligible & resources_eligible
