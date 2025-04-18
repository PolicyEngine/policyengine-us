from policyengine_us.model_api import *


class il_tanf_countable_income_at_application(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) countable income at application"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.il.dhs.tanf.income.initial_employment_deduction

        countable_gross_earned_income = spm_unit(
            "il_tanf_countable_gross_earned_income", period
        )
        exempted_expense = spm_unit(
            "spm_unit_capped_work_childcare_expenses", period
        )
        adjust_earned_income = max_(
            countable_gross_earned_income - exempted_expense, 0
        )

        fpg = spm_unit("spm_unit_fpg", period)
        initial_employment_deduction = p.rate * fpg - spm_unit(
            "il_tanf_payment_level", period
        )
        earned_income_deduction = min_(
            adjust_earned_income, initial_employment_deduction
        )
        countable_unearned_income = spm_unit(
            "il_tanf_countable_unearned_income", period
        )

        return (
            adjust_earned_income
            - earned_income_deduction
            + countable_unearned_income
        )
