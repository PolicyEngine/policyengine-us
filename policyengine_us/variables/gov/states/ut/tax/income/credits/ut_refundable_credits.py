from policyengine_us.model_api import *


class ut_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = ""
