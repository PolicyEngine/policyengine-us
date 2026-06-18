from policyengine_us.model_api import *


class hi_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    adds = ["hi_ccap"]
