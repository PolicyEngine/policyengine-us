from policyengine_us.model_api import *


class nd_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.nd.gov/dhs/policymanuals/40019/400_19_110_20.htm"
    defined_for = StateCode.ND

    adds = [
        "nd_tanf_countable_earned_income",
        "nd_tanf_countable_unearned_income",
    ]
