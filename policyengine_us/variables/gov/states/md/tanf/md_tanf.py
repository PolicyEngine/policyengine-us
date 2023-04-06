from policyengine_us.model_api import *


class md_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "md_tanf_eligible"

    def formula(spm_unit, period, parameters):
        maximum_benefit = spm_unit("md_tanf_maximum_benefit", period)
        income_deduction = add(
            spm_unit,
            period,
            [
                "md_tanf_countable_earned_net_income",
                "md_tanf_countable_unearned_net_income",
            ],
        )
        return max(maximum_benefit - net_countable_income, 0)
