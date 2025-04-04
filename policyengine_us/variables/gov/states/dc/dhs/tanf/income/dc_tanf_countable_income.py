from policyengine_us.model_api import *


class dc_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "DC Temporary Assistance for Needy Families (TANF) countable income"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        income_sources = add(
            spm_unit,
            period,
            [
                "dc_tanf_countable_earned_income",
                "dc_tanf_countable_unearned_income",
            ],
        )
        childcare_deduction = spm_unit("dc_tanf_childcare_deduction", period)
        return max_(income_sources - childcare_deduction, 0)
