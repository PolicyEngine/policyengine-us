from policyengine_us.model_api import *


class pa_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF countable income"
    documentation = "Pennsylvania TANF countable income is the sum of earned income after deductions plus all unearned income, used to determine eligibility and benefit amount."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 183"

    def formula(spm_unit, period, parameters):
        # Get gross income
        gross_earned = spm_unit("pa_tanf_gross_earned_income", period)
        gross_unearned = spm_unit("pa_tanf_gross_unearned_income", period)

        # Get earned income deductions
        earned_deductions = spm_unit(
            "pa_tanf_earned_income_deductions", period
        )

        # Calculate countable earned income
        countable_earned = max_(gross_earned - earned_deductions, 0)

        # All unearned income is countable (no deductions)
        countable_unearned = gross_unearned

        # Total countable income
        return countable_earned + countable_unearned
