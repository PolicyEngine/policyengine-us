from policyengine_us.model_api import *


class va_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=50"

    adds = [
        "va_tanf_countable_earned_income",
        "va_tanf_countable_unearned_income",
    ]
