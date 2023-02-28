from policyengine_us.model_api import *


class co_tanf_gross_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "CO TANF total countable income"
    unit = USD
    definition_period = YEAR
    adds = [
        "co_tanf_countable_gross_earned_income",
        "co_tanf_countable_gross_unearned_income",
    ]
