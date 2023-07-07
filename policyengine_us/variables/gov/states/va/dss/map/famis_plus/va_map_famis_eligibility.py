from policyengine_us.model_api import *


class va_map_famis_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP FAMIS Plus eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        age_eligible = spm_unit("va_map_famis_age_eligibility", period)
        income_eligible = spm_unit("va_map_famis_income_eligibility", period)
        return age_eligible & income_eligible
