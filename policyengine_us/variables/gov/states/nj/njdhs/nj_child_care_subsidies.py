from policyengine_us.model_api import *


class nj_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    adds = ["nj_ccap"]
