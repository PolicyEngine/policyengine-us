from policyengine_us.model_api import *


class me_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine nonrefundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME

    adds = ["me_dependent_exemption", "me_non_refundable_child_care_credit"]
