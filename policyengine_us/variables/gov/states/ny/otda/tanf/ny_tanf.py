from policyengine_us.model_api import *


class ny_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "ny_tanf_eligible"

    def formula(spm_unit, period, parameters):
        grant_standard = spm_unit("ny_tanf_grant_standard", period)
        income = add(
            spm_unit,
            period,
            [
                "ny_tanf_countable_earned_income",
                "ny_tanf_countable_gross_unearned_income",
            ],
        )
        return max_(grant_standard - income, 0)
