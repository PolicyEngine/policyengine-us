from policyengine_us.model_api import *


class il_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Illinois Child Care Assistance Program (CCAP)"
    defined_for = StateCode.IL
