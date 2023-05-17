from policyengine_us.model_api import *


class ri_refunable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island refundable credits"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR