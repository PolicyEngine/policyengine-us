from policyengine_us.model_api import *


class nm_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in New Mexico CCAP"
    defined_for = StateCode.NM
