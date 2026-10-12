from policyengine_us.model_api import *


class mn_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Currently enrolled in Minnesota CCAP"
    defined_for = StateCode.MN
