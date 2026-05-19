from policyengine_us.model_api import *


class la_fitap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Louisiana FITAP countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/louisiana/La-Admin-Code-tit-67-SS-III-1229"
    defined_for = StateCode.LA

    adds = [
        "la_fitap_earned_income_after_disregard",
        "tanf_gross_unearned_income",
    ]
