from policyengine_us.model_api import *


class ak_atap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.470"
    defined_for = StateCode.AK

    adds = [
        "ak_atap_countable_earned_income",
        "ak_atap_countable_unearned_income",
    ]
