"""
Connecticut TFA total countable income.
"""

from policyengine_us.model_api import *


class ct_tfa_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA countable income"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Total countable income for Connecticut TFA, including both earned and "
        "unearned income after all applicable disregards and exclusions."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026; "
        "Connecticut DSS Uniform Policy Manual Section 8030"
    )

    def formula(spm_unit, period, parameters):
        countable_earned = spm_unit("ct_tfa_countable_earned_income", period)
        countable_unearned = spm_unit(
            "ct_tfa_countable_unearned_income", period
        )

        return countable_earned + countable_unearned
