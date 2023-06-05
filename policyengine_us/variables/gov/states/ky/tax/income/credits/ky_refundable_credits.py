from policyengine_us.model_api import *


class ky_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
