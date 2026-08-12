from policyengine_us.model_api import *


class dc_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
    adds = ["dc_ccsp"]
