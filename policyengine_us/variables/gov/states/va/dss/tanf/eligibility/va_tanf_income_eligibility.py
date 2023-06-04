from policyengine_us.model_api import *


class va_tanf_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA TANF income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "va_tanf_countable_earned_income",
                "va_tanf_countable_unearned_income",
            ],
        )
        need_standard = spm_unit("va_tanf_need_standard", period)
        return income <= need_standard
