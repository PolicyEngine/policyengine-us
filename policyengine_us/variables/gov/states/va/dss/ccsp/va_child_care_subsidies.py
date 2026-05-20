from policyengine_us.model_api import *


class va_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Virginia child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    adds = ["va_ccsp"]
