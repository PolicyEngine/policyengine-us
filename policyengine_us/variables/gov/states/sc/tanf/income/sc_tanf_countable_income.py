from policyengine_us.model_api import *


class sc_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        # PDF pages 131, 134
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=131",
    )

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "sc_tanf_countable_earned_income_person",
                "sc_tanf_gross_unearned_income",
            ],
        )
        # Section 8.16 H tests and budgets income net of child support paid.
        # Countable income keeps its cents; nothing says to round it.
        deduction = spm_unit("sc_tanf_child_support_deduction", period)
        # The deduction never takes income below zero (Section 8.11(2)); the
        # floor only absorbs rounding when it equals the group's income. A
        # group with no deduction keeps its income unchanged.
        return where(deduction > 0, max_(income - deduction, 0), income)
