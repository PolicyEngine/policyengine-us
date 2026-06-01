from policyengine_us.model_api import *


class wv_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    adds = ["wv_ccap"]
