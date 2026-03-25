from policyengine_us.model_api import *


class ri_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.RI
    adds = ["ri_ccap"]
