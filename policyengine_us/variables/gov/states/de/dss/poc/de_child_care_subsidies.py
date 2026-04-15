from policyengine_us.model_api import *


class de_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    adds = ["de_poc"]
