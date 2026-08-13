from policyengine_us.model_api import *


class or_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Oregon child care subsidies"
    defined_for = StateCode.OR
    adds = ["or_erdc"]
