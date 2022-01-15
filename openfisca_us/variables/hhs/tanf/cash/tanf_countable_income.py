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
        earned_income_deduction = parameters(
            period
        ).hhs.tanf.cash.earned_income_deduction[state]
        countable_earned_income = earned_income * (1 - earned_income_deduction)
        # No deduction for unearned income.
        unearned_income = spm_unit("tanf_gross_unearned_income", period)
        return countable_earned_income + unearned_income
