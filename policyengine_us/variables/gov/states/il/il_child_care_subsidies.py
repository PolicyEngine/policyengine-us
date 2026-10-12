from policyengine_us.model_api import *


class il_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = YEAR
    label = "Illinois child care subsidies"
    defined_for = StateCode.IL
    adds = ["il_ccap"]
