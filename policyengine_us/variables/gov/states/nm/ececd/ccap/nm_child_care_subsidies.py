from policyengine_us.model_api import *


class nm_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
    adds = ["nm_ccap"]
