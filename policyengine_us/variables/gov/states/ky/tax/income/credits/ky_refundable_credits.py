from policyengine_us.model_api import *


class ky_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kenntucky refundable credits"
    unit = USD
    definition_period = YEAR