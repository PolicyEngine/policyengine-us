from policyengine_us.model_api import *


class il_pass_through_withholding(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL Pass-Through Withholding"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
