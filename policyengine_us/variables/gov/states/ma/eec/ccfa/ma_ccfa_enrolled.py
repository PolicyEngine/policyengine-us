from policyengine_us.model_api import *


class ma_ccfa_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether the family is currently enrolled in Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
