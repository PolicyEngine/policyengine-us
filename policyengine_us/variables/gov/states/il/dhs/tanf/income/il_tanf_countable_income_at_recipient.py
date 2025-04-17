from policyengine_us.model_api import *


class il_tanf_countable_income_at_recipient(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) countable income at recipient"
    unit = USD
    definition_period = MONTH
    reference = "https://www.dhs.state.il.us/page.aspx?item=15864"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.income.disregard

        countable_gross_earned_income = spm_unit(
            "il_tanf_countable_gross_earned_income", period
        )
        exempted_expense = spm_unit(
            "spm_unit_capped_work_childcare_expenses", period
        )
        adjust_earned_income = max_(
            countable_gross_earned_income - exempted_expense, 0
        )

        earned_income_deduction = min_(
            adjust_earned_income, p.rate * adjust_earned_income
        )
        countable_unearned_income = spm_unit(
            "il_tanf_countable_unearned_income", period
        )

        return (
            adjust_earned_income
            - earned_income_deduction
            + countable_unearned_income
        )
