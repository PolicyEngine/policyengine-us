from policyengine_us.model_api import *


class nm_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
