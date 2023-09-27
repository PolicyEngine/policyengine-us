from policyengine_us.model_api import *


class ms_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
