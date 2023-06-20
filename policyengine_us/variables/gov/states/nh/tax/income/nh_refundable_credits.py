from policyengine_us.model_api import *


class nh_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH
