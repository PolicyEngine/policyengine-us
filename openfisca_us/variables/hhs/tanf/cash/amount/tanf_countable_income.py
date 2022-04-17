from openfisca_us.model_api import *


class tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF countable income"
    documentation = "Countable income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD

    def formula(spm_unit, period, parameters):
        gross_earned_income = spm_unit("tanf_gross_earned_income", period)
        state = spm_unit.household("state_code_str", period)
        earnings_deductions = parameters(
            period
        ).hhs.tanf.cash.amount.countable_income.deductions.earnings
        household_earnings_deduction = earnings_deductions.household[state]
        percent_earnings_deduction = earnings_deductions.percent[state]
        total_earnings_deductions = household_earnings_deduction + (gross_earned_income * percent_earnings_deduction)
        countable_earned_income = gross_earned_income - total_earnings_deductions
        # No deduction for unearned income.
        unearned_income = spm_unit("tanf_gross_unearned_income", period)
        return max_(countable_earned_income + unearned_income, 0)
