from policyengine_us.model_api import *


class me_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME

    adds = ["me_refundable_child_care_credit", "me_eitc"]
