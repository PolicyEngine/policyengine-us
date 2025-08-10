from policyengine_us.model_api import *


class dc_ccsp_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in DC Child Care Subsidy Program (CCSP)"
    defined_for = StateCode.DC
