from policyengine_us.model_api import *


class oh_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    adds = ["oh_ccap"]
