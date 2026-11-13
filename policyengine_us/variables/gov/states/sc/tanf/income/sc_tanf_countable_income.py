from policyengine_us.model_api import *


class sc_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        # PDF pages 121, 131, 134
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=121",
        "https://www.scstatehouse.gov/coderegs/Chapter%20114.pdf#page=212",
    )

    def formula(spm_unit, period, parameters):
        sources = [
            "sc_tanf_countable_earned_income_person",
            "sc_tanf_gross_unearned_income",
        ]
        income = add(spm_unit, period, sources)
        # Section 8.16 H tests and budgets income net of child support paid.
        # Section 8.1 says "Do not round at any step of the TANF calculation",
        # so countable income keeps its cents.
        deduction = spm_unit("sc_tanf_child_support_deduction", period)
        # Each payer's deduction stops at that payer's own income
        # (114-1140(L)), so the total never falls below the sum of the
        # members' negative incomes, which only a self-employment or farm
        # loss produces. That floor absorbs float32 rounding in the deduction.
        member_income = add(spm_unit.members, period, sources)
        floor = spm_unit.sum(min_(member_income, 0))
        return max_(income - deduction, floor)
