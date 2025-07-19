from policyengine_us.model_api import *


class va_map_famis_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP FAMIS Plus income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        income = spm_unit("va_map_famis_income", period)
        limit = spm_unit("va_map_famis_income_limit", period)
        return income <= limit
