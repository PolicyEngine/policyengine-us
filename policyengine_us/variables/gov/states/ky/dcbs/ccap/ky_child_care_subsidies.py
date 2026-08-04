from policyengine_us.model_api import *


class ky_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    adds = ["ky_ccap"]
