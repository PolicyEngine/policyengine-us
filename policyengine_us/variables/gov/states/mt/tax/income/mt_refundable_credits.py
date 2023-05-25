from policyengine_us.model_api import *


class mt_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
