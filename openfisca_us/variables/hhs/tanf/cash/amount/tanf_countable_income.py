from openfisca_us.model_api import *


class tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF countable income"
    documentation = "Countable income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD
    reference = (
        # California:
        "https://ehsd.org/benefits/calworks-cash-aid/calworks-fact-sheet"
    )

    def formula(spm_unit, period, parameters):
        gross_earned_income = spm_unit("tanf_gross_earned_income", period)
        state = spm_unit.household("state_code_str", period)
        earnings_deductions = parameters(
            period
        ).hhs.tanf.cash.amount.countable_income.deductions.earnings
        household_earnings_deduction = earnings_deductions.household[state]
        percent_earnings_deduction = earnings_deductions.percent[state]
        # Percent earnings deduction applies after deducting the household deduction.
        earnings_after_household_deduction = gross_earned_income - household_earnings_deduction
        total_percent_deduction = earnings_after_household_deduction * percent_earnings_deduction
        total_earnings_deductions = household_earnings_deduction + total_percent_deduction
        countable_earned_income = gross_earned_income - total_earnings_deductions
        # No deduction for unearned income.
        unearned_income = spm_unit("tanf_gross_unearned_income", period)
        return max_(countable_earned_income + unearned_income, 0)
