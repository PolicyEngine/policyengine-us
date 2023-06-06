from policyengine_us.model_api import *


class nj_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
