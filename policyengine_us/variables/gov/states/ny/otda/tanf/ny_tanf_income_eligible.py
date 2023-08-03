from policyengine_us.model_api import *


class ny_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF income eligible"
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "ny_tanf_countable_earned_income",
                "ny_tanf_countable_gross_unearned_income",
            ],
        )
        need_standard = spm_unit("ny_tanf_need_standard", period)
        return income < need_standard
