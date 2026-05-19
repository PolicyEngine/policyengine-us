from policyengine_us.model_api import *


class nd_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40019/400_19_110_20.htm",
        "https://www.law.cornell.edu/regulations/north-dakota/N-D-A-C-75-02-1.2-51",
    )
    defined_for = StateCode.ND

    adds = ["nd_tanf_countable_earned_income_person"]
