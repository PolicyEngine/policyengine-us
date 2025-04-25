from policyengine_us.model_api import *


class il_tanf_countable_income_for_grant_calculation(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) countable income for grant calculation"
    unit = USD
    definition_period = MONTH
    reference = "https://www.dhs.state.il.us/page.aspx?item=15864"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.income.disregard

        countable_gross_earned_income = spm_unit(
            "il_tanf_countable_gross_earned_income", period
        )
        childcare_deduction = spm_unit("il_tanf_childcare_deduction", period)
        adjusted_earned_income = max_(
            countable_gross_earned_income - childcare_deduction, 0
        )
        adjusted_earned_income_fraction = p.rate * adjusted_earned_income
        earned_income_deduction = min_(
            adjusted_earned_income, adjusted_earned_income_fraction
        )
        countable_unearned_income = spm_unit(
            "il_tanf_countable_unearned_income", period
        )

        return (
            adjusted_earned_income
            - earned_income_deduction
            + countable_unearned_income
        )
