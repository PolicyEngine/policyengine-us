from policyengine_us.model_api import *


class ga_caps_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Georgia CAPS"
    defined_for = StateCode.GA
