from policyengine_us.model_api import *


class va_famis_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA FAMIS Plus income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "va_famis_earned_income",
                "va_famis_unearned_income",
            ],
        )
        limit = spm_unit("va_famis_income_limit", period)
        return income <= limit
