from policyengine_us.model_api import *


class co_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO


# Colorado non refundable credits currently not modeled in PolicyEngine
