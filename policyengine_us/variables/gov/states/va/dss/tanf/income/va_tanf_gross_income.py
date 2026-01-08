from policyengine_us.model_api import *


class va_tanf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF gross income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=50"

    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
