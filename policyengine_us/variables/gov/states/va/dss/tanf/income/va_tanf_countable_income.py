from policyengine_us.model_api import *


class va_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/tanfx2fview/tanf/Chapter-300---Need-and-Amount-of-Assistance.pdf#page=54"

    adds = [
        "va_tanf_countable_earned_income",
        "va_tanf_countable_unearned_income",
    ]
