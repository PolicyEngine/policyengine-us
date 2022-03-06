from openfisca_us.model_api import *


class tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF countable income"
    documentation = "Countable income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD

    def formula(spm_unit, period, parameters):
        earned_income = spm_unit("tanf_gross_earned_income", period)
        state = spm_unit.household("state_code_str", period)
        earnings_deductions = parameters(
            period
        ).hhs.tanf.cash.income.deductions.earnings
        flat_earnings_deduction = earnings_deductions.flat[state]
        percent_earnings_deduction = earnings_deductions.percent[state]
        countable_earned_income -= flat_earnings_deduction
        countable_earned_income -= (
            countable_earned_income * percent_earnings_deduction
        )
        # No deduction for unearned income.
        unearned_income = spm_unit("tanf_gross_unearned_income", period)
        return countable_earned_income + unearned_income
