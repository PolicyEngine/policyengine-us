from policyengine_us.model_api import *


class tn_ff_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Get countable earned income (after $250 disregard)
        countable_earned = spm_unit("tn_ff_countable_earned_income", period)

        # Subtract child care deduction from earned income
        child_care_deduction = spm_unit("tn_ff_child_care_deduction", period)
        countable_earned_after_childcare = max_(
            countable_earned - child_care_deduction, 0
        )

        # Add unearned income (no disregard for unearned)
        countable_unearned = add(
            spm_unit, period, ["tanf_gross_unearned_income"]
        )

        return countable_earned_after_childcare + countable_unearned
