from policyengine_us.model_api import *


class tn_ff_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = "https://publications.tnsosfiles.com/rules/1240/1240-01/1240-01-50.20081124.pdf#page=19"

    def formula(spm_unit, period, parameters):
        earned_after_disregard = spm_unit(
            "tn_ff_earned_income_after_disregard", period
        )
        child_care_deduction = spm_unit("tn_ff_child_care_deduction", period)
        return max_(earned_after_disregard - child_care_deduction, 0)
