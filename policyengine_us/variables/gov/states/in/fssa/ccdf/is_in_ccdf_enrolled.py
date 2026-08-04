from policyengine_us.model_api import *


class is_in_ccdf_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Enrolled in Indiana CCDF"
    defined_for = StateCode.IN
