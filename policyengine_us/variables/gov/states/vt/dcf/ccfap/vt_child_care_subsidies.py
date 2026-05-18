from policyengine_us.model_api import *


class vt_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    adds = ["vt_ccfap"]
