from policyengine_us.model_api import *


class pa_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA
    adds = ["pa_ccw"]
