from policyengine_us.model_api import *


class il_aabd_supplement_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) supplement payment"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/title-89/part-113/subpart-D",
    )

    adds = [
        "il_aabd_utility_allowance",
        #"il_aabd_personal_allowance",
        # laundry, telephone, shelter,
    ]
