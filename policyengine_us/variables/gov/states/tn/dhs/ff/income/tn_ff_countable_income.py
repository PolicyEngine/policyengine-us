from policyengine_us.model_api import *


class tn_ff_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = "https://publications.tnsosfiles.com/rules/1240/1240-01/1240-01-50.20081124.pdf#page=19"
    adds = [
        "tn_ff_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
