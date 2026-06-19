from policyengine_us.model_api import *


class md_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    adds = ["md_ccs"]
