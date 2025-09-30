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

    adds = [
        "tx_tanf_countable_earned_income",
        "tx_tanf_countable_unearned_income",
    ]
