from policyengine_us.model_api import *


class ga_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
