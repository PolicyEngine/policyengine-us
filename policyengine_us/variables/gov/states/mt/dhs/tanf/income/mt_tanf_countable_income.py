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
                "mt_tanf_gross_unearned_income",
            ],
        )

        dependent_care_deduction = spm_unit(
            "mt_tanf_dependent_care_deduction", period
        )
        return max_(income_sources - dependent_care_deduction, 0)
