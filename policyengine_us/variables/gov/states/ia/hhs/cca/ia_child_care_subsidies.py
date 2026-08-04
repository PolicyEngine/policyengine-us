from policyengine_us.model_api import *


class ia_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    adds = ["ia_cca"]
