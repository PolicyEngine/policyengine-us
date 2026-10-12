from policyengine_us.model_api import *


class nc_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
    adds = ["nc_scca"]
