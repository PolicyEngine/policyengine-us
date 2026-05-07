from policyengine_us.model_api import *


class wv_works_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia WV Works countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://bfa.wv.gov/media/2766/download?inline#page=589"
    defined_for = StateCode.WV

    # Step 7: Add together the total countable earned and unearned income
    adds = [
        "wv_works_countable_earned_income",
        "wv_works_countable_unearned_income",
    ]
