from policyengine_us.model_api import *


class vt_reach_up_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    adds = [
        "vt_reach_up_countable_earned_income",
        "vt_reach_up_countable_unearned_income",
    ]
