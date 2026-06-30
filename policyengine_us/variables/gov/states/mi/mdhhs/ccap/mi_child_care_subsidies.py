from policyengine_us.model_api import *


class mi_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    adds = ["mi_ccap"]
