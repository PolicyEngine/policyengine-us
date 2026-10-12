from policyengine_us.model_api import *


class nv_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NV
    adds = ["nv_ccdp"]
