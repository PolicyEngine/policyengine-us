from policyengine_us.model_api import *


class al_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AL
