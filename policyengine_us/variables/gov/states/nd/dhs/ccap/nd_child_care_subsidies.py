from policyengine_us.model_api import *


class nd_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ND
    adds = ["nd_ccap"]
