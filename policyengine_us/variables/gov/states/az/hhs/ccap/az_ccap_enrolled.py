from policyengine_us.model_api import *


class az_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Enrolled in Arizona Child Care Assistance Program"
    definition_period = MONTH
    defined_for = StateCode.AZ
