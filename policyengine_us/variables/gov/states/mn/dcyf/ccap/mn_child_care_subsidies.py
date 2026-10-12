from policyengine_us.model_api import *


class mn_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN
    adds = ["mn_ccap"]
