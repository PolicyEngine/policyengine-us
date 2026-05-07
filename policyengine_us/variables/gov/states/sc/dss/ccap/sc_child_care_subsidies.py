from policyengine_us.model_api import *


class sc_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    adds = ["sc_ccap"]
