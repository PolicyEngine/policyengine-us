from policyengine_us.model_api import *


class il_aabd_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) countable income"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL

    adds = [
        "il_aabd_countable_earned_income",
        "il_aabd_countable_unearned_income",
    ]
