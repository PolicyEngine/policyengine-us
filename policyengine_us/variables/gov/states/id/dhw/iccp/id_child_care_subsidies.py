from policyengine_us.model_api import *


class id_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = YEAR
    label = "Idaho child care subsidies"
    defined_for = StateCode.ID
    adds = ["id_iccp"]
