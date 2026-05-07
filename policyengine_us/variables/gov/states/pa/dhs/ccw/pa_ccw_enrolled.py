from policyengine_us.model_api import *


class pa_ccw_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Pennsylvania CCW"
    defined_for = StateCode.PA
