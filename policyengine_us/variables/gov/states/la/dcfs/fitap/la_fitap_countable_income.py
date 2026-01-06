from policyengine_us.model_api import *


class la_fitap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Louisiana FITAP countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://ldh.la.gov/page/fitap"
    defined_for = StateCode.LA

    adds = [
        "la_fitap_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
