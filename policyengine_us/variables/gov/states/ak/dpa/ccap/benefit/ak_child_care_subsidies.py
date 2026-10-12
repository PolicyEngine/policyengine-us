from policyengine_us.model_api import *


class ak_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AK
    adds = ["ak_ccap"]
