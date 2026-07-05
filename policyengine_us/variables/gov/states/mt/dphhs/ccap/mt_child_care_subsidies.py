from policyengine_us.model_api import *


class mt_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    adds = ["mt_ccap"]
