from policyengine_us.model_api import *


class co_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "co_tanf_eligible"

    def formula(spm_unit, period, parameters):
        grant_standard = spm_unit("co_tanf_grant_standard", period)
        income = add(
            spm_unit,
            period,
            [
                "co_tanf_countable_earned_income_grant_standard",
                "co_tanf_countable_gross_unearned_income",
            ],
        )
        return max_(grant_standard - income, 0)
