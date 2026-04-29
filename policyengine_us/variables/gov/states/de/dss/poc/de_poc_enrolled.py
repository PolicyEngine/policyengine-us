from policyengine_us.model_api import *


class de_poc_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Delaware Purchase of Care"
    defined_for = StateCode.DE
