from policyengine_us.model_api import *


class ne_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NE
    adds = ["ne_child_care_subsidy"]
