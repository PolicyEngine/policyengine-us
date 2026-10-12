from policyengine_us.model_api import *


class tn_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.TN
    adds = ["tn_ccap"]
