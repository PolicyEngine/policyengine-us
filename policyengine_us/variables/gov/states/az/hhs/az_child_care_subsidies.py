from policyengine_us.model_api import *


class az_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Arizona child care subsidies"
    definition_period = YEAR
    defined_for = StateCode.AZ
    adds = ["az_ccap"]
