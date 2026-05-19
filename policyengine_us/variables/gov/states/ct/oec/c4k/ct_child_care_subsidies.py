from policyengine_us.model_api import *


class ct_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    adds = ["ct_c4k"]
