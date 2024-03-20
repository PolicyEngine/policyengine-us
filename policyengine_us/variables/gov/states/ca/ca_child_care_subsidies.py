from policyengine_us.model_api import *


class ca_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "California child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    adds = ["ca_calworks_child_care"]
