from policyengine_us.model_api import *


class va_map_pregnant_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP Pregnant Women income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "va_pregnant_women_earned_income",
                "va_pregnant_women_unearned_income",
            ],
        )
        limit = spm_unit("va_pregnant_women_income_limit", period)
        return income <= limit
