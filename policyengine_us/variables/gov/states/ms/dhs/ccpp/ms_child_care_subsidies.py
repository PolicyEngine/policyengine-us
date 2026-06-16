from policyengine_us.model_api import *


class ms_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    adds = ["ms_ccpp"]
