from policyengine_us.model_api import *


class tx_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1350-calculating-household-income",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        countable_earned = spm_unit("tx_tanf_countable_earned_income", period)
        countable_unearned = spm_unit(
            "tx_tanf_countable_unearned_income", period
        )

        # Total countable income after all deductions
        total_income = countable_earned + countable_unearned

        return total_income
