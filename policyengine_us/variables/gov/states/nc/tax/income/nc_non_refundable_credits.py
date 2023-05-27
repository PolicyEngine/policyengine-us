from policyengine_us.model_api import *


class nc_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
