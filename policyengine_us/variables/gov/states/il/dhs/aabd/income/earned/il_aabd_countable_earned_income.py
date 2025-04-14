from policyengine_us.model_api import *


class il_aabd_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/title-89/part-113/subpart-C",
    )

    adds = ["il_aabd_earned_income_after_exemption_person"]
    # don't really need this when we change everything one person level 
