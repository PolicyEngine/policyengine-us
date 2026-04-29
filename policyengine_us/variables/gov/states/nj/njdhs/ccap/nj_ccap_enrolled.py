from policyengine_us.model_api import *


class nj_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in New Jersey CCAP"
    defined_for = StateCode.NJ
