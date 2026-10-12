from policyengine_us.model_api import *


class mo_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO
    adds = ["mo_ccs"]
