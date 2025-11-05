from policyengine_us.model_api import *


class ga_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1525/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/1615/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        countable_earned = spm_unit("ga_tanf_countable_earned_income", period)
        countable_unearned = spm_unit(
            "ga_tanf_countable_unearned_income", period
        )
        childcare_deduction = spm_unit("ga_tanf_childcare_deduction", period)
        return max_(
            countable_earned + countable_unearned - childcare_deduction, 0
        )
