from policyengine_us.model_api import *


class fl_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "Florida Administrative Code Rule 65A-4.209"
    documentation = "Net countable income after applying all disregards, used to determine benefit amount"

    def formula(spm_unit, period, parameters):
        # Gross income sources
        gross_earned = spm_unit("fl_tanf_gross_earned_income", period)
        gross_unearned = spm_unit("fl_tanf_gross_unearned_income", period)

        # Earned income disregards
        earned_disregard = spm_unit("fl_tanf_earned_income_disregard", period)

        # Calculate countable earned and unearned income
        countable_earned = max_(gross_earned - earned_disregard, 0)
        countable_unearned = gross_unearned

        return countable_earned + countable_unearned
