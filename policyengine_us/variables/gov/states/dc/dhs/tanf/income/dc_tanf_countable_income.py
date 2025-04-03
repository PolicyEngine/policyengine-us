from policyengine_us.model_api import *


class dc_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "DC Temporary Assistance for Needy Families (TANF) countable income"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DC

    adds = [
        "dc_tanf_countable_earned_income",
        "dc_tanf_countable_unearned_income",
    ]
