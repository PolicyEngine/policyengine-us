from policyengine_us.model_api import *


class ks_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KS
    adds = ["ks_ccap"]
