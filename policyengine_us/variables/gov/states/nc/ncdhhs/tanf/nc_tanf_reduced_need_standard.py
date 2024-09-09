from policyengine_us.model_api import *


class nc_tanf_reduced_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF reduced need standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "nc_tanf_countable_earned_income",
                "nc_tanf_countable_gross_unearned_income",
            ],
        )
        need_standard = spm_unit("nc_tanf_need_standard", period)
        reduced_need_standard = max_(need_standard - income, 0)

        return reduced_need_standard
