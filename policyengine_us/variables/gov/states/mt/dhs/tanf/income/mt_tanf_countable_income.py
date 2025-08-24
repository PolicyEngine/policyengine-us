from policyengine_us.model_api import *


class mt_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        income_sources = add(
            spm_unit,
            period,
            [
                "mt_tanf_countable_earned_income",
                "mt_tanf_countable_unearned_income",
            ],
        )

        childcare_deduction = spm_unit("mt_tanf_childcare_deduction", period)
        return max_(income_sources - childcare_deduction, 0)
