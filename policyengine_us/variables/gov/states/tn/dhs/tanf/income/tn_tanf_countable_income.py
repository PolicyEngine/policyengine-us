from policyengine_us.model_api import *


class tn_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50",
        "Tennessee Administrative Code § 1240-01-50 - Financial Eligibility Requirements",
        "Tennessee TANF State Plan 2024-2027",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Get countable earned income (after $250 disregard)
        countable_earned = spm_unit("tn_tanf_countable_earned_income", period)

        # Subtract child care deduction from earned income
        # Per TN regulations, childcare deduction applies to earned income only
        child_care_deduction = spm_unit("tn_tanf_child_care_deduction", period)
        countable_earned_after_childcare = max_(
            countable_earned - child_care_deduction, 0
        )

        # Add unearned income (no disregard for unearned)
        countable_unearned = spm_unit(
            "tn_tanf_countable_unearned_income", period
        )

        return countable_earned_after_childcare + countable_unearned
