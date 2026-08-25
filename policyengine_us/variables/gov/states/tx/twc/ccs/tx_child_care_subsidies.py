from policyengine_us.model_api import *


class tx_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.TX
    adds = ["tx_ccs"]
