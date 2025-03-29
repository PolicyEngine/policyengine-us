from policyengine_us.model_api import *


class tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "TANF countable income"
    documentation = "Countable income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD
    reference = (
        # California:
        "https://ehsd.org/benefits/calworks-cash-aid/calworks-fact-sheet"
    )

    def formula(spm_unit, period, parameters):
        deductions = parameters(
            period
        ).gov.hhs.tanf.cash.amount.countable_income.deductions
        state = spm_unit.household("state_code_str", period)
        household_deduction = deductions.household[state]
        # First subtract household deduction from unearned income.
        unearned_income = spm_unit("tanf_gross_unearned_income", period)
        countable_unearned_income = max_(
            0, unearned_income - household_deduction
        )
        # Then allocate remaining household deduction to earned income.
        remaining_household_deduction = household_deduction - (
            unearned_income - countable_unearned_income
        )
        gross_earned_income = spm_unit("tanf_gross_earned_income", period)
        earnings_after_household_deduction = max_(
            gross_earned_income - remaining_household_deduction, 0
        )
        # Then subtract percent earnings deduction after household deduction.
        percent_earnings_deduction = deductions.earnings.percent[state]
        total_percent_deduction = (
            earnings_after_household_deduction * percent_earnings_deduction
        )
        countable_earned_income = (
            earnings_after_household_deduction - total_percent_deduction
        )
        return countable_earned_income + countable_unearned_income
