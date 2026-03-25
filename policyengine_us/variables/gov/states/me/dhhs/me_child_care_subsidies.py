from policyengine_us.model_api import *


class me_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    adds = ["me_ccap"]
