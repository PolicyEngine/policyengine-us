from policyengine_us.model_api import *


class co_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Colorado TANF income eligible"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "co_tanf_countable_earned_income_need",
                "co_tanf_countable_gross_unearned_income",
            ],
        )
        need_standard = spm_unit("co_tanf_need_standard", period)
        return income < need_standard
