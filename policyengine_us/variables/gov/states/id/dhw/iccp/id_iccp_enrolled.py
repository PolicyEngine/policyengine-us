from policyengine_us.model_api import *


class id_iccp_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in the Idaho Child Care Program"
    defined_for = StateCode.ID
