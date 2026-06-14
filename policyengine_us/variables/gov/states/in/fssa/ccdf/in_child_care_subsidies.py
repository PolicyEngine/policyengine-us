from policyengine_us.model_api import *


class in_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IN
    adds = ["in_ccdf"]
