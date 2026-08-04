from policyengine_us.model_api import *


class nv_ccdp_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Nevada CCDP"
    defined_for = StateCode.NV
