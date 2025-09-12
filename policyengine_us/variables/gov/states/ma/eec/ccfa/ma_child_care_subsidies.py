from policyengine_us.model_api import *


class ma_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    adds = ["ma_ccfa"]
