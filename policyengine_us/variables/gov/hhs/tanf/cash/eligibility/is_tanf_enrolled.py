from policyengine_us.model_api import *


class is_tanf_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Enrolled in TANF"
    documentation = "Whether the familiy is currently enrolled in the Temporary Assistance for Needy Families program."
