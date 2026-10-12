from policyengine_us.model_api import *


class ut_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    adds = ["ut_ccap"]
