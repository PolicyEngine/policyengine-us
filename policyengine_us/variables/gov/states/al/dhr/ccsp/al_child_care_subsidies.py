from policyengine_us.model_api import *


class al_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alabama child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AL
    adds = ["al_ccsp"]
